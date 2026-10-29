"""Exercise local scoping without a CRM, including incomplete pricing and bad inputs."""
import copy
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from catalog import entries, dependencies, apply_entrypoint
from portable import assemble, runtime_closure


class PortableScopingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.package = self.root / 'project-scoping'
        item = entries(ROOT)['project-scoping']
        assemble(ROOT, item['source'], self.package, dependencies(ROOT, item, runtime_closure))
        apply_entrypoint(self.package, 'project-scoping', item)
        self.model = json.loads((self.package / 'fixtures/estimate.example.json').read_text())
        self.count = 0

    def calculate(self, model=None, existing=None):
        self.count += 1
        attempt = self.root / ('attempt-' + str(self.count))
        attempt.mkdir()
        source = attempt / 'scope.json'
        source.write_text(json.dumps(self.model if model is None else model))
        original = source.read_bytes()
        output = attempt / 'estimate.json'
        if existing:
            output.with_suffix(existing).write_text('preserve this file')
        result = subprocess.run([sys.executable, str(self.package / 'scripts/estimate.py'),
            str(source), '--output', str(output)], cwd=self.root, capture_output=True, text=True)
        (attempt / 'command.json').write_text(json.dumps({'exit': result.returncode,
            'stdout': result.stdout, 'stderr': result.stderr}, indent=2))
        self.assertEqual(source.read_bytes(), original)
        return result, output, original

    def test_isolated_package_calculates_supplied_scope_and_capacity(self):
        result, output, raw = self.calculate()
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(output.read_text())
        for scenario, hours, fee in [('low', 34, 3700), ('expected', 52, 5700), ('high', 76, 8400)]:
            self.assertEqual(Decimal(data['totals'][scenario]['hours']), hours)
            self.assertEqual(Decimal(data['totals'][scenario]['fee']), fee)
        self.assertEqual(Decimal(data['capacity_lower_bound_weeks']['expected']), Decimal('2.8'))
        self.assertEqual(data['input_sha256'], hashlib.sha256(raw).hexdigest())
        text = output.with_suffix('.md').read_text()
        self.assertIn('Batch import', text)
        self.assertIn('ledger accepted a posting before retrying', text)
        self.assertIn('Production deployment.', text)
        self.assertEqual(len(list(self.package.rglob('SKILL.md'))), 1)

    def test_effort_only_works_without_a_rate_card(self):
        model = copy.deepcopy(self.model)
        model.pop('rates')
        model.pop('currency')
        result, output, _ = self.calculate(model)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(output.read_text())
        self.assertEqual(data['totals']['expected']['hours'], '52')
        self.assertIsNone(data['totals']['expected']['fee'])
        self.assertNotIn('Fee (', output.with_suffix('.md').read_text())

    def test_missing_partial_rate_or_effort_basis_refuses_a_complete_price(self):
        missing_rate = copy.deepcopy(self.model)
        missing_rate['rates'].pop()
        missing_basis = copy.deepcopy(self.model)
        missing_basis['items'][0].pop('basis')
        for model in [missing_rate, missing_basis]:
            result, output, _ = self.calculate(model)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertFalse(output.exists())
            self.assertFalse(output.with_suffix('.md').exists())

    def test_invalid_values_and_unsupported_financial_fields_are_rejected(self):
        mutations = []
        for value in [-1, float('nan'), True]:
            model = copy.deepcopy(self.model)
            model['items'][0]['allocations'][0]['hours']['low'] = value
            mutations.append(model)
        model = copy.deepcopy(self.model)
        model['items'][0]['allocations'][0]['hours']['low'] = 999
        mutations.append(model)
        model = copy.deepcopy(self.model)
        model['discount'] = 100
        mutations.append(model)
        model = copy.deepcopy(self.model)
        model['capacity'][0]['availability'] = 0
        mutations.append(model)
        mutations += [[], {'source': 'invalid'}, {'source': {}, 'rates': 'invalid'}]
        for model in mutations:
            result, output, _ = self.calculate(model)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertFalse(output.exists())

    def test_existing_json_and_document_are_preserved(self):
        for suffix in ['.json', '.md']:
            result, output, _ = self.calculate(existing=suffix)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(output.with_suffix(suffix).read_text(), 'preserve this file')

    def test_decimal_fees_are_not_silently_rounded_per_line(self):
        model = copy.deepcopy(self.model)
        model['rates'] = [{'role': 'Developer', 'rate': '0.1', 'source': 'Fictional decimal test'}]
        model.pop('capacity')
        for item in model['items']:
            item['allocations'] = [{'role': 'Developer', 'hours': {
                'low': '0.25', 'expected': '0.25', 'high': '0.25'}}]
        result, output, _ = self.calculate(model)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(output.read_text())
        self.assertEqual(Decimal(data['totals']['expected']['fee']), Decimal('0.05'))
        self.assertEqual(sum(Decimal(item['scenarios']['expected']['fee']) for item in data['items']),
                         Decimal(data['totals']['expected']['fee']))

    def unestimated_item(self):
        return {'id': 'migration', 'name': 'Data migration',
                'description': 'Move the agreed historical records.',
                'source': 'Fictional brief, migration question',
                'status': 'unestimated',
                'discovery_needed': 'Confirm record volume and required transformations.'}

    def test_unestimated_scope_remains_visible_and_withholds_project_totals(self):
        model = copy.deepcopy(self.model)
        model['items'].append(self.unestimated_item())
        result, output, _ = self.calculate(model)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(output.read_text())
        self.assertEqual(data['format'], 2)
        self.assertEqual(data['status'], 'incomplete-estimate')
        self.assertFalse(data['totals_complete'])
        self.assertIsNone(data['totals'])
        self.assertEqual(data['estimated_subtotal']['expected'], {'hours': '52', 'fee': '5700'})
        unknown = data['items'][-1]
        self.assertEqual(unknown['source'], model['items'][-1]['source'])
        self.assertEqual(unknown['discovery_needed'], model['items'][-1]['discovery_needed'])
        self.assertIsNone(unknown['scenarios'])
        document = output.with_suffix('.md').read_text()
        for phrase in ['Estimated work subtotal', 'Full-project hours and price are withheld.',
                       'Data migration', 'Status: unestimated', unknown['discovery_needed'],
                       'estimated items only']:
            self.assertIn(phrase, document)
        self.assertNotIn('## Scenario totals', document)

    def test_all_unestimated_scope_cannot_look_like_a_zero_price_project(self):
        model = copy.deepcopy(self.model)
        model['items'] = [self.unestimated_item()]
        model.pop('capacity')
        for priced in [True, False]:
            if not priced:
                model.pop('rates')
                model.pop('currency')
            result, output, _ = self.calculate(model)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(output.read_text())
            self.assertIsNone(data['totals'])
            self.assertIsNone(data['estimated_subtotal'])
            self.assertIsNone(data['capacity_lower_bound_weeks'])
            document = output.with_suffix('.md').read_text()
            self.assertIn('No work has an effort estimate yet.', document)
            self.assertNotIn('| Expected | 0 |', document)

    def test_unestimated_contract_rejects_ambiguous_or_contradictory_inputs(self):
        mutations = []
        for status in ['unknown', '', False, None, []]:
            item = self.unestimated_item()
            item['status'] = status
            mutations.append(item)
        item = self.unestimated_item()
        item.pop('discovery_needed')
        mutations.append(item)
        for allocations in [self.model['items'][0]['allocations'], {}, None]:
            item = self.unestimated_item()
            item['allocations'] = allocations
            mutations.append(item)
        for item in mutations:
            model = copy.deepcopy(self.model)
            model['items'].append(item)
            result, output, _ = self.calculate(model)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertFalse(output.exists())
            self.assertFalse(output.with_suffix('.md').exists())

    def test_document_exposes_calculations_and_escapes_table_text(self):
        model = copy.deepcopy(self.model)
        model['rates'][0]['source'] = 'Fictional card | revision 1\nSecond line'
        result, output, _ = self.calculate(model)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(output.read_text())
        self.assertTrue(data['totals_complete'])
        self.assertEqual(data['totals'], data['estimated_subtotal'])
        document = output.with_suffix('.md').read_text()
        for item in data['items']:
            section = document.split('### ' + item['name'] + '\n', 1)[1].split('\n##', 1)[0]
            for key in ['low', 'expected', 'high']:
                values = item['scenarios'][key]
                self.assertIn('| ' + key.capitalize() + ' | ' + values['hours'] + ' | ' + values['fee'] + ' |', section)
        self.assertIn('| Developer | 28 | 42 | 60 |', document)
        self.assertIn('| Architect | 6 | 10 | 16 |', document)
        self.assertIn('Fictional card \\| revision 1 Second line', document)
        for key, weeks in data['capacity_lower_bound_weeks'].items():
            self.assertIn('| ' + key.capitalize() + ' | ' + weeks + ' |', document)


if __name__ == '__main__':
    unittest.main()
