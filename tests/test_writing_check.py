"""Hold check.py to the interface other tools call: flags, exit codes and JSON keys."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills' / 'writing'
CHECK = SKILL / 'scripts' / 'check.py'
FIXTURES = ROOT / 'tests' / 'fixtures' / 'writing-check'


class WritingCheckInterface(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='writing-check-')
        self.addCleanup(self.temp.cleanup)

    def run_check(self, name, *extra):
        done = subprocess.run([sys.executable, str(CHECK), '--file', str(FIXTURES / name), '--json',
                               '--rules-dir', str(FIXTURES / 'rules'), '--receipt-dir', self.temp.name, *extra],
                              capture_output=True, text=True, timeout=60)
        return done.returncode, json.loads(done.stdout)

    def test_pass_exits_0_with_full_coverage(self):
        code, result = self.run_check('pass.md')
        self.assertEqual(code, 0)
        self.assertEqual(result['status'], 'pass')
        self.assertEqual(result['coverage']['lines_total'], result['coverage']['lines_reviewed'])
        self.assertEqual(result['coverage']['lines_total'], 2)
        self.assertEqual(result['findings'], [])
        self.assertTrue(Path(result['receipt']).is_file())

    def test_fail_exits_1_and_each_finding_has_line_rule_text_fix(self):
        code, result = self.run_check('fail.html')
        self.assertEqual((code, result['status']), (1, 'fail'))
        self.assertEqual(len(result['findings']), 1)
        finding = result['findings'][0]
        self.assertEqual({key: finding[key] for key in ('line', 'rule', 'text', 'fix')},
                         {'line': 3, 'rule': 'residue', 'text': 'I hope this helps', 'fix': 'Delete it.'})

    def test_register_selects_rules_scoped_to_it(self):
        code, result = self.run_check('fail.html', '--register', 'status-update')
        self.assertEqual(code, 1)
        self.assertEqual([f['rule'] for f in result['findings']], ['residue', 'channel-only'])

    def test_unknown_register_exits_2_and_lists_the_valid_names(self):
        code, result = self.run_check('pass.md', '--register', 'weekly-update')
        self.assertEqual((code, result['status']), (2, 'incomplete'))
        self.assertIn('Valid names: commit, status-update', result['reason'])

    def test_unparsed_file_exits_2_and_is_never_a_pass(self):
        code, result = self.run_check('open-fence.md')
        self.assertEqual((code, result['status']), (2, 'incomplete'))
        self.assertIn('never closes', result['reason'])
        self.assertEqual(result['coverage']['lines_reviewed'], 0)

    def test_missing_file_exits_2(self):
        code, result = self.run_check('absent.md')
        self.assertEqual((code, result['status']), (2, 'incomplete'))

    def test_result_keys_are_stable(self):
        _, result = self.run_check('pass.md')
        for key in ('status', 'coverage', 'findings', 'receipt'):
            self.assertIn(key, result)
        receipt = json.loads(Path(result['receipt']).read_text())
        steps = {s['step']: s['status'] for s in receipt['steps']}
        self.assertEqual(steps, {'rules': 'ok', 'extract': 'ok', 'scan': 'ok', 'line pass': 'not_run', 'claims check': 'not_run',
                                 'document pass': 'not_run', 'spot audit': 'not_run'})

    def test_skill_carries_no_copy_of_the_rules(self):
        names = {p.name for p in SKILL.rglob('*') if p.is_file()}
        self.assertFalse(names & {'rules.md', 'patterns.json', 'voice-profile.md', 'registers.md', 'corrections.md'})


if __name__ == '__main__':
    unittest.main()
