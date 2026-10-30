"""Preserve useful offering checks without inventing a specification authority."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/playbook-suite/scripts'


class PlaybookSpecificationContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = self.root / 'manifest.json'
        self.manifest.write_text(json.dumps({'code': 'SYN', 'name': 'Synthetic',
            'shape': 'Assess', 'spec_version': '1.1', 'options': [], 'artifacts': []}))

    def run_script(self, script, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                              capture_output=True, text=True)

    def assert_unverified(self, result):
        self.assertEqual('unverified', result['spec_authority']['status'])
        self.assertFalse(result['spec_authority']['release_ready'])
        self.assertEqual('1.1', result['spec_authority']['checked_rules_version'])
        self.assertIn('stage_gate_workbook', result['spec_authority']['required_inputs'])

    def test_plan_preserves_work_and_discloses_unverified_authority(self):
        result = self.run_script('plan.py', self.manifest)
        self.assertEqual(0, result.returncode, result.stderr)
        plan = json.loads(result.stdout)
        self.assert_unverified(plan)
        self.assertGreater(plan['totals']['outstanding'], 0)
        self.assertTrue(plan['steps'])
        self.assertTrue(plan['next_step'])

    def test_complete_model_does_not_claim_current_specification_acceptance(self):
        manifest = json.loads(self.manifest.read_text())
        manifest['artifacts'] = [
            {'number': number, 'status': 'present',
             'gates': {'parity': 'pass', 'visual': 'pass', 'prose': 'pass'}}
            for number in range(1, 11)]
        self.manifest.write_text(json.dumps(manifest))
        result = self.run_script('plan.py', self.manifest)
        self.assertEqual(0, result.returncode, result.stderr)
        plan = json.loads(result.stdout)
        self.assertEqual(0, plan['totals']['outstanding'])
        self.assert_unverified(plan)

    def test_audit_keeps_missing_artifact_findings_and_discloses_authority(self):
        result = self.run_script('conformance_audit.py', self.root, '--json')
        self.assertEqual(1, result.returncode, result.stderr)
        audit = json.loads(result.stdout)
        self.assert_unverified(audit)
        self.assertGreater(audit['blocking_findings'], 0)

    def test_changing_version_label_cannot_claim_an_unimplemented_model(self):
        result = self.run_script('plan.py', self.manifest, '--spec-version', '99.0')
        self.assertEqual(2, result.returncode)
        self.assertIn('invalid choice', result.stderr)

    def test_text_outputs_disclose_the_same_limit(self):
        for script, args in [('plan.py', [self.manifest, '--format', 'text']),
                             ('conformance_audit.py', [self.root])]:
            with self.subTest(script=script):
                result = self.run_script(script, *args)
                self.assertIn('Specification authority unverified', result.stdout)

    def test_router_reports_minimum_checks_separately_from_schema_validation(self):
        qualifiers = self.root / 'qualifiers'
        qualifiers.mkdir()
        (qualifiers / 'synthetic.json').write_text(json.dumps(
            {'playbook_code': 'SYN', 'gates': [], 'tiers': [], 'tags': []}))
        signals = self.root / 'signals.json'
        signals.write_text(json.dumps({'signals': [], 'gate_answers': {}}))
        result = subprocess.run([sys.executable,
            str(ROOT / 'skills/playbook-fit-router/scripts/route.py'),
            '--qualifiers', str(qualifiers), '--signals', str(signals), '--format', 'json'],
            capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual('not_performed', report['schema_validation']['status'])
        self.assertEqual('minimum_required_fields', report['schema_validation']['checks'])
        self.assertIn('schema', ' '.join(report['notes']).lower())
        self.assertEqual(1, report['coverage']['scored'])


if __name__ == '__main__':
    unittest.main()
