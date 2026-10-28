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
            cwd=self.package, capture_output=True, text=True)
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

    def final_narrative(self):
        artifact = self.base / 'memo.md'
        artifact.write_text('Support Operations owns the routing queue.\n', encoding='utf-8')
        receipt = self.base / 'receipt.json'
        tool = self.package / '_runtime/prose-pass/scripts/prose_receipt.py'
        result = subprocess.run([sys.executable, str(tool), 'emit', str(artifact), '--out', str(receipt),
                                 '--no-change-justification', 'Read the memo against its supplied source; no edit was needed.'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        record = copy.deepcopy(self.record)
        record['artifact'].update(path='memo.md', client_prose=True, narrative_final=True)
        record['controls_selected'] = ['prose-pass']
        record['checks'] = [{'control': 'prose-pass', 'verdict': 'pass',
                             'citation': 'Synthetic memo', 'receipt': 'receipt.json'}]
        return record, artifact, receipt

    def test_final_receipt_is_validated_and_bound_to_current_artifact(self):
        record, artifact, receipt = self.final_narrative()
        result, verdict = self.invoke(record)
        self.assertEqual(result.returncode, 0)
        self.assertTrue(verdict['released'])
        for label, payload in [('malformed', b'{'), ('array', b'[]'), ('empty', b'{}')]:
            with self.subTest(label=label):
                record, artifact, receipt = self.final_narrative()
                receipt.write_bytes(payload)
                result, verdict = self.invoke(record)
                self.assertEqual(result.returncode, 1)
                self.assertFalse(verdict['released'])
                self.assertIn('prose-receipt-invalid', {f['code'] for f in verdict['findings']})
        for label in ['stale', 'different', 'missing', 'relative-receipt-artifact', 'missing-artifact-path', 'deleted-artifact']:
            with self.subTest(label=label):
                record, artifact, receipt = self.final_narrative()
                if label == 'stale':
                    artifact.write_text('Support Operations owns the assignment queue.\n', encoding='utf-8')
                    expected = 'hash-mismatch'
                elif label == 'different':
                    other = self.base / 'other-memo.md'
                    other.write_text('Another document.\n', encoding='utf-8')
                    record['artifact']['path'] = 'other-memo.md'
                    expected = 'different artifact'
                elif label == 'missing':
                    receipt.unlink()
                    expected = 'receipt.json'
                elif label == 'relative-receipt-artifact':
                    data = json.loads(receipt.read_text())
                    data['artifact'] = 'memo.md'
                    receipt.write_text(json.dumps(data))
                    expected = 'relative'
                elif label == 'missing-artifact-path':
                    del record['artifact']['path']
                    expected = 'artifact.path'
                else:
                    artifact.unlink()
                    expected = 'memo.md'
                result, verdict = self.invoke(record)
                self.assertEqual(result.returncode, 1)
                self.assertFalse(verdict['released'])
                errors = [f for f in verdict['findings'] if f['code'] == ('prose-artifact-missing' if label == 'missing-artifact-path' else 'prose-receipt-invalid')]
                self.assertTrue(errors)
                self.assertIn(expected, errors[0]['message'])

    def test_final_receipt_cannot_be_waived_or_run_without_its_validator(self):
        record, artifact, receipt = self.final_narrative()
        record['checks'][0]['verdict'] = 'not_applicable'
        record['artifact']['client_prose'] = False
        result, verdict = self.invoke(record)
        self.assertFalse(verdict['released'])
        record['checks'][0]['verdict'] = 'blocked'
        record['checks'][0].pop('receipt')
        record['release']['released'] = False
        result, verdict = self.invoke(record)
        self.assertEqual(result.returncode, 0)
        self.assertTrue(verdict['valid'])
        self.assertFalse(verdict['released'])
        record['checks'][0].update(verdict='pass', receipt='receipt.json')
        record['release']['released'] = True
        (self.package / '_runtime/prose-pass/scripts/prose_receipt.py').unlink()
        sibling = self.base / 'prose-pass/scripts/prose_receipt.py'
        sibling.parent.mkdir(parents=True)
        sibling.write_text('raise SystemExit(0)\n')
        result, verdict = self.invoke(record)
        self.assertFalse(verdict['released'])
        self.assertIn('prose-receipt-invalid', {f['code'] for f in verdict['findings']})

    def test_relative_emission_and_malformed_receipt_fields(self):
        record, artifact, receipt = self.final_narrative()
        tool = self.package / '_runtime/prose-pass/scripts/prose_receipt.py'
        emitted = subprocess.run([sys.executable, str(tool), 'emit', 'memo.md', '--out', 'receipt.json',
                                  '--no-change-justification', 'Read the memo against its source; the sentence needs no edit.'],
                                 cwd=self.base, capture_output=True, text=True)
        self.assertEqual(emitted.returncode, 0, emitted.stdout + emitted.stderr)
        original = json.loads(receipt.read_text())
        self.assertTrue(Path(original['artifact']).is_absolute())
        self.assertTrue(Path(original['artifact']).samefile(artifact))
        result, verdict = self.invoke(record)
        self.assertTrue(verdict['released'])
        for field, value in [('artifact', []), ('figure_check', []),
                             ('figure_check', {'ran': 'false'}), ('figures_added', [None]),
                             ('no_change_justification', {}), ('changes_made', 'reviewed')]:
            with self.subTest(field=field, value=value):
                malformed = copy.deepcopy(original)
                malformed[field] = value
                receipt.write_text(json.dumps(malformed))
                result, verdict = self.invoke(record)
                self.assertEqual(result.returncode, 1)
                self.assertFalse(verdict['released'])
                validation = subprocess.run([sys.executable, str(tool), 'validate', str(receipt)],
                                            capture_output=True, text=True)
                self.assertEqual(validation.returncode, 1)
                self.assertNotIn('Traceback', validation.stderr)

    def test_unreadable_standalone_receipt_returns_input_error(self):
        record, artifact, receipt = self.final_narrative()
        tool = self.package / '_runtime/prose-pass/scripts/prose_receipt.py'
        for payload in [b'\xff\xfe', b'[' * 2000 + b']' * 2000]:
            with self.subTest(payload_size=len(payload)):
                receipt.write_bytes(payload)
                result = subprocess.run([sys.executable, str(tool), 'validate', str(receipt)],
                                        capture_output=True, text=True)
                # Runtime recursion limits differ. A parsed array is an invalid
                # receipt (1); a decoder refusal is unusable input (2).
                self.assertIn(result.returncode, (1, 2) if len(payload) > 2 else (2,))
                self.assertNotIn('Traceback', result.stderr)


    def test_nested_quality_runtime_uses_only_the_containing_package(self):
        self.package = self.base / 'journey-mapping'
        assemble(ROOT, 'journey-mapping', self.package, [])
        record, artifact, receipt = self.final_narrative()
        gate = self.package / '_runtime/quality-gate/scripts/quality_gate.py'
        record_path = self.base / 'nested-record.json'
        record_path.write_text(json.dumps(record))
        def invoke_nested():
            result = subprocess.run([sys.executable,str(gate),str(record_path),'--json'],
                                    capture_output=True,text=True,cwd=self.base)
            self.assertNotIn('Traceback',result.stderr)
            return result,json.loads(result.stdout)
        result,verdict=invoke_nested()
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertTrue(verdict['released'])
        validator=self.package/'_runtime/prose-pass/scripts/prose_receipt.py'
        validator.unlink()
        external=self.base/'prose-pass/scripts/prose_receipt.py'
        external.parent.mkdir(parents=True)
        marker=self.base/'external-was-run'
        external.write_text('from pathlib import Path\nPath('+repr(str(marker))+').touch()\nraise SystemExit(0)\n')
        result,verdict=invoke_nested()
        self.assertEqual(result.returncode,1)
        self.assertFalse(verdict['released'])
        self.assertIn('bundled prose receipt validator is missing',str(verdict))
        self.assertFalse(marker.exists())
        validator.symlink_to(external)
        result,verdict=invoke_nested()
        self.assertEqual(result.returncode,1)
        self.assertFalse(verdict['released'])
        self.assertFalse(marker.exists())
        (self.package/'references/estate/writing.md').unlink()
        (self.package/'_runtime/quality-gate/references/estate/writing.md').unlink()
        result,verdict=invoke_nested()
        self.assertEqual(result.returncode,1)
        self.assertFalse(verdict['released'])
        self.assertFalse(marker.exists())


if __name__ == '__main__':
    unittest.main()
