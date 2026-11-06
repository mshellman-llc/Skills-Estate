"""Verify that commercial checks use supplied policy rather than house defaults."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CommercialPolicyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.manifest = {'code': 'EXAMPLE', 'name': 'Fictional offering',
            'shape': 'Assess', 'spec_version': '1.1',
            'options': [{'name': 'Review', 'quote_number': 'Q-EXAMPLE',
                         'timeline_snapshot_id': 'example-revision', 'margin_pct': 40}]}

    def plan(self, policy=None):
        data = copy.deepcopy(self.manifest)
        if policy is not None:
            data['commercial_policy'] = policy
        source = self.folder / 'manifest.json'
        source.write_text(json.dumps(data))
        result = subprocess.run([sys.executable,
            str(ROOT / 'skills/plan-offering-artifacts/scripts/plan.py'), str(source)],
            cwd=self.folder, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(result.stdout)
        number = len(list(self.folder.glob('plan-*.json')))
        (self.folder / ('plan-' + str(number) + '.json')).write_text(result.stdout)
        return record

    def test_no_policy_does_not_assume_an_employer_floor(self):
        record = self.plan()
        self.assertTrue(any('unresolved' in x for x in record['findings']))
        self.assertFalse(any('48' in x or 'below' in x for x in record['findings']))

    def test_different_confirmed_floors_change_the_actual_comparison(self):
        policy = {'source': 'Fictional project policy', 'verified_at': '2026-10-22',
                  'margin_floor_pct': 30}
        low = self.plan(policy)
        policy['margin_floor_pct'] = 50
        high = self.plan(policy)
        self.assertFalse(any('below' in x for x in low['findings']))
        self.assertTrue(any('below the configured floor 50' in x for x in high['findings']))

    def test_unsourced_and_nonfinite_floors_are_not_applied(self):
        for policy in [{'margin_floor_pct': 30},
                {'source': 'Example', 'verified_at': '2026-10-22', 'margin_floor_pct': float('nan')}]:
            record = self.plan(policy)
            self.assertTrue(any('unresolved' in x for x in record['findings']))

    def test_documented_figures_example_actually_reconciles(self):
        result = subprocess.run([sys.executable,
            str(ROOT / 'skills/review-deal-economics/scripts/deal_desk_gate.py'),
            str(ROOT / 'skills/review-deal-economics/references/margin-approval-routing.md')],
            cwd=self.folder, capture_output=True, text=True)
        (self.folder / 'figures-result.txt').write_text(result.stdout + result.stderr)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
