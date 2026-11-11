"""Check packaged routing against gate transitions and incomplete state."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from portable import assemble


class DeliveryRoutingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.package = self.root / 'delivery-kickoff'
        assemble(ROOT, 'delivery-kickoff', self.package, [])
        self.planner = self.package / '_runtime/delivery-suite/scripts/plan.py'

    def plan(self, gates, declared=None):
        file = self.root / 'DELIVERY-STATE.md'
        text = '# Delivery state\n\n'
        if declared:
            text += '## Stage\ncurrent: ' + declared + '\n\n'
        text += '## Gates\n' + ''.join('- ' + key + ': ' + status + '\n' for key, status in gates.items())
        file.write_text(text)
        result = subprocess.run([sys.executable, str(self.planner), str(file), '--json'],
            cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        (self.root / ('plan-' + str(len(list(self.root.glob('plan-*.json')))) + '.json')).write_text(result.stdout)
        return data

    def test_accepted_handoff_routes_to_the_actual_kickoff_skill(self):
        result = self.plan({'brief_accepted': 'accepted'})
        self.assertEqual(result['current_stage']['owner'], 'delivery-kickoff')
        self.assertFalse(result['complete'])
        self.assertEqual(len(list(self.package.rglob('SKILL.md'))), 1)

    def test_build_complete_routes_to_acceptance_testing(self):
        gates = {key: 'met' for key in ['brief_accepted', 'charter_signed',
            'requirements_cosigned', 'sdd_cosigned', 'build_complete']}
        result = self.plan(gates)
        self.assertEqual(result['current_stage']['owner'], 'acceptance-testing')
        self.assertEqual(result['current_stage']['id'], '05')

    def test_later_pass_and_declared_stage_cannot_hide_an_open_gate(self):
        result = self.plan({'brief_accepted': 'accepted', 'go_no_go': 'met'}, '06')
        self.assertEqual(result['current_stage']['id'], '01')
        self.assertGreaterEqual(len(result['findings']), 2)
        self.assertFalse(result['complete'])


if __name__ == '__main__':
    unittest.main()
