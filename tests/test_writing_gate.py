"""Hold changed Markdown to the writing check, with receipts only for protected text."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import writing_gate  # noqa: E402

CLEAN = '# Demo\n\nThe tool reads each changed file and reports what it finds. Owners fix the text and run it again.\n'
FLAWED = '# Demo\n\nThe tool reads each changed file and reports what it finds. It makes delivery seamless for owners.\n'
TEACHING = ('# Demo\n\nThe tool reads each changed file and reports what it finds.\n\n'
            '> It makes delivery seamless for owners.\n\nOwners fix the text and run it again.\n')
QUOTED = '> It makes delivery seamless for owners.'


class WritingGateTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
        self.env = {**env, 'GIT_AUTHOR_NAME': 'Test', 'GIT_AUTHOR_EMAIL': 'test@example.invalid',
                    'GIT_COMMITTER_NAME': 'Test', 'GIT_COMMITTER_EMAIL': 'test@example.invalid'}
        self.git('init', '-q', '-b', 'main')
        self.write('skills/demo/SKILL.md', CLEAN)
        self.write('skills/demo/references/legacy.md', FLAWED.replace('# Demo', '# Legacy `OLD_NAME`'))
        self.write('skills/demo/LICENSE-UPSTREAM.md', FLAWED)
        self.commit('baseline')

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.root), *args], check=True,
                              capture_output=True, text=True, env=self.env)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def commit(self, message):
        self.git('add', '-A')
        self.git('commit', '-q', '-m', message)

    def staged(self):
        self.git('add', '-A')
        return {row['path']: row for row in writing_gate.run(self.root, 'staged')}

    def test_clean_change_passes(self):
        self.write('skills/demo/SKILL.md', CLEAN + '\nThe owner reviews the report before release.\n')
        self.assertTrue(self.staged()['skills/demo/SKILL.md']['passed'])

    def test_new_finding_fails(self):
        self.write('skills/demo/SKILL.md', FLAWED)
        row = self.staged()['skills/demo/SKILL.md']
        self.assertFalse(row['passed'])
        self.assertIn('house-banned-term', row['note'])

    def test_identifier_change_keeps_older_findings(self):
        self.write('skills/demo/references/legacy.md', FLAWED.replace('# Demo', '# Legacy `NEW_NAME`'))
        row = self.staged()['skills/demo/references/legacy.md']
        self.assertTrue(row['passed'], row['note'])
        self.assertIn('clean-up list', row['note'])

    def test_prose_edit_needs_a_full_pass(self):
        edited = FLAWED.replace('# Demo', '# Legacy `OLD_NAME`').replace('reports', 'lists')
        self.write('skills/demo/references/legacy.md', edited)
        row = self.staged()['skills/demo/references/legacy.md']
        self.assertFalse(row['passed'])
        self.assertIn('full pass', row['note'])

    def test_prose_edit_that_fixes_the_file_passes(self):
        self.write('skills/demo/references/legacy.md', CLEAN)
        self.assertTrue(self.staged()['skills/demo/references/legacy.md']['passed'])

    def test_receipt_covers_only_protected_text(self):
        self.write('skills/demo/SKILL.md', TEACHING)
        receipt = {'format': 1, 'artifact': 'skills/demo/SKILL.md',
                   'protected': [{'kind': 'example', 'reason': 'Shows the banned term the section teaches.',
                                  'text': QUOTED}]}
        self.write('.writing-receipts/skills/demo/SKILL.md.json', json.dumps(receipt))
        self.assertTrue(self.staged()['skills/demo/SKILL.md']['passed'])
        self.write('skills/demo/SKILL.md', TEACHING + '\nThe report is seamless.\n')
        row = self.staged()['skills/demo/SKILL.md']
        self.assertFalse(row['passed'])
        self.assertIn('outside protected text', row['note'])

    def test_receipt_text_must_match_the_file(self):
        self.write('skills/demo/SKILL.md', FLAWED)
        receipt = {'format': 1, 'artifact': 'skills/demo/SKILL.md',
                   'protected': [{'kind': 'example', 'reason': 'Not present.', 'text': 'missing sentence'}]}
        self.write('.writing-receipts/skills/demo/SKILL.md.json', json.dumps(receipt))
        row = self.staged()['skills/demo/SKILL.md']
        self.assertFalse(row['passed'])
        self.assertIn('not in the file', row['note'])

    def test_receipt_rejects_unknown_kinds_and_waivers(self):
        self.write('skills/demo/SKILL.md', FLAWED)
        receipt = {'format': 1, 'artifact': 'skills/demo/SKILL.md', 'protected': [],
                   'candidates': [{'rule': 'house-banned-term', 'reason': 'Waive it.', 'source': 'none'}]}
        self.write('.writing-receipts/skills/demo/SKILL.md.json', json.dumps(receipt))
        self.assertFalse(self.staged()['skills/demo/SKILL.md']['passed'])

    def test_changed_receipt_puts_its_file_under_the_gate(self):
        self.write('.writing-receipts/skills/demo/references/legacy.md.json',
                   json.dumps({'format': 1, 'artifact': 'skills/demo/references/legacy.md', 'protected': []}))
        self.assertIn('skills/demo/references/legacy.md', self.staged())

    def test_upstream_license_text_is_not_checked(self):
        self.write('skills/demo/LICENSE-UPSTREAM.md', FLAWED + '\nMore seamless text.\n')
        self.assertNotIn('skills/demo/LICENSE-UPSTREAM.md', self.staged())

    def test_rename_keeps_the_earlier_findings(self):
        self.git('mv', 'skills/demo/references/legacy.md', 'skills/demo/references/moved.md')
        row = self.staged()['skills/demo/references/moved.md']
        self.assertTrue(row['passed'], row['note'])

    def test_base_mode_reads_changes_since_the_merge_base(self):
        self.git('checkout', '-q', '-b', 'topic')
        self.write('skills/demo/SKILL.md', FLAWED)
        self.commit('flawed edit')
        rows = {row['path']: row for row in writing_gate.run(self.root, 'base', 'main')}
        self.assertFalse(rows['skills/demo/SKILL.md']['passed'])

    def test_command_line_exit_codes(self):
        self.write('skills/demo/SKILL.md', FLAWED)
        self.git('add', '-A')
        done = subprocess.run([sys.executable, str(ROOT / 'tools/writing_gate.py'), '--root', str(self.root),
                               '--staged'], capture_output=True, text=True, env=self.env)
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)


class RepositoryHookTests(unittest.TestCase):
    def test_pre_commit_hook_runs_both_checks_and_is_executable(self):
        text = (ROOT / '.githooks/pre-commit').read_text()
        self.assertIn('python3 tools/writing_gate.py --staged', text)
        self.assertIn('python3 tools/private_terms.py --staged', text)
        listed = subprocess.run(['git', '-C', str(ROOT), 'ls-files', '-s', '.githooks'],
                                capture_output=True, text=True)
        modes = {line.split('\t')[1]: line.split()[0] for line in listed.stdout.splitlines()}
        if not modes:
            self.skipTest('No Git index to read in this copy')
        self.assertIn('.githooks/pre-commit', modes)
        for name, mode in modes.items():
            self.assertEqual(mode, '100755', name + ' needs its executable bit, or Git skips it')

    def test_no_pre_push_hook_duplicates_ci(self):
        # The verify workflow runs the full suite on every pull request; a local
        # pre-push copy only slowed pushes and failed without CI's Node settings.
        self.assertFalse((ROOT / '.githooks/pre-push').exists())


class RepositoryGateTests(unittest.TestCase):
    """CI fetches origin/main before the tests, so this holds each pull request to the gate."""

    def test_markdown_changed_since_origin_main_passes_the_gate(self):
        base = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', '--verify', '--quiet',
                               'refs/remotes/origin/main'], capture_output=True, text=True).stdout.strip()
        if not base:
            self.skipTest('No origin/main to compare with')
        failed = [row['path'] + ': ' + row['note'] for row in writing_gate.run(ROOT, 'base', base)
                  if not row['passed']]
        self.assertEqual(failed, [], 'Run python3 tools/writing_gate.py --base origin/main for details.')


if __name__ == '__main__':
    unittest.main()
