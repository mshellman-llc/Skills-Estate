"""Exercise quality-record refusals through the packaged command."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from portable import assemble


class QualityRecordTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.package = self.base / 'quality-gate'
        assemble(ROOT, 'quality-gate', self.package, [])
        self.record = {
            'artifact': {'id': 'synthetic-memo', 'type': 'memo'},
            'controls_selected': ['source-check'],
            'checks': [{'control': 'source-check', 'verdict': 'pass',
                        'citation': 'Synthetic source, line 1'}],
            'release': {'released': True},
            'hub_update': {'status': 'not_applicable'},
        }

    def invoke(self, record):
        path = self.base / 'record.json'
        path.write_text(json.dumps(record), encoding='utf-8')
        result = subprocess.run(
            [sys.executable, str(self.package / 'scripts/quality_gate.py'), str(path), '--json'],
            cwd=self.base, capture_output=True, text=True)
        self.assertNotIn('Traceback', result.stderr)
        return result, json.loads(result.stdout)

    def test_boolean_release_and_honest_blocked_record(self):
        result, verdict = self.invoke(self.record)
        self.assertEqual(result.returncode, 0)
        self.assertTrue(verdict['released'])
        self.record['release']['released'] = False
        self.record['checks'][0]['verdict'] = 'blocked'
        result, verdict = self.invoke(self.record)
        self.assertEqual(result.returncode, 0)
        self.assertTrue(verdict['valid'])
        self.assertFalse(verdict['released'])
        self.assertTrue(verdict['blockers'])

    def test_release_is_never_inferred_from_truthiness(self):
        for value in ['false', 'true', 0, 1, [], {}, None]:
            with self.subTest(value=value):
                record = copy.deepcopy(self.record)
                record['release']['released'] = value
                result, verdict = self.invoke(record)
                self.assertEqual(result.returncode, 1)
                self.assertFalse(verdict['released'])
                self.assertFalse(verdict['valid'])

    def test_malformed_nested_values_return_structured_refusals(self):
        changes = [
            ('release', {}), ('release', 'approved'),
            ('controls_selected', 'source-check'), ('controls_selected', [[]]),
            ('controls_selected', []), ('controls_selected', ['source-check', 'source-check']),
            ('controls_selected', ['unperformed-check']),
            ('assertions', {'kind': 'financial_figure'}), ('assertions', 'financial_figure'),
            ('assertions', [None]), ('assertions', [{'kind': []}]),
            ('checks', [None]), ('checks', [{'control': [], 'verdict': 'pass'}]),
            ('checks', [{'control': 'source-check', 'verdict': {}}]),
            ('hub_update', {'status': []}), ('hub_update', {'status': ' '}),
            ('artifact', {'client_prose': 'false'}),
            ('artifact', {'brand_render': 0}), ('artifact', {'narrative_final': []}),
        ]
        for key, value in changes:
            with self.subTest(key=key, value=value):
                record = copy.deepcopy(self.record)
                record[key] = value
                result, verdict = self.invoke(record)
                self.assertEqual(result.returncode, 1)
                self.assertFalse(verdict['valid'])
                self.assertFalse(verdict['released'])
                self.assertTrue(verdict['findings'])

    def test_unsupported_financial_claim_and_uncited_pass_still_refuse(self):
        record = copy.deepcopy(self.record)
        record['assertions'] = [{'kind': 'financial_figure', 'supported_by': 'missing'}]
        result, verdict = self.invoke(record)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(verdict['released'])
        self.assertIn('fail-closed', {f['code'] for f in verdict['findings']})
        record = copy.deepcopy(self.record)
        record['checks'][0]['citation'] = ''
        result, verdict = self.invoke(record)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(verdict['released'])
        self.assertIn('uncited-pass', {f['code'] for f in verdict['findings']})


if __name__ == '__main__':
    unittest.main()
