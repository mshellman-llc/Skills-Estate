from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from marketplace_guard import verified_run, verify_publication, generated_only_parent


class MarketplaceGuardTests(unittest.TestCase):
    def setUp(self):
        self.sha = 'a' * 40
        self.run = {'id': 20, 'run_attempt': 1, 'head_sha': self.sha, 'head_branch': 'main',
                    'path': '.github/workflows/verify.yml', 'status': 'completed', 'conclusion': 'success'}

    def test_exact_success_is_accepted(self):
        self.assertEqual(20, verified_run(self.sha, {'workflow_runs': [self.run]}))

    def test_stale_unrelated_missing_pending_or_failed_verification_is_refused(self):
        for change in ({'head_sha': 'b' * 40}, {'head_branch': 'feature'},
                       {'path': '.github/workflows/other.yml'}, {'status': 'in_progress'},
                       {'conclusion': 'failure'}, {'conclusion': 'cancelled'}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                verified_run(self.sha, {'workflow_runs': [{**self.run, **change}]})
        with self.assertRaises(ValueError):
            verified_run(self.sha, {'workflow_runs': []})

    def test_prior_success_cannot_hide_a_newer_failed_or_pending_run(self):
        for status, conclusion in [('completed', 'failure'), ('in_progress', None)]:
            newer = {**self.run, 'id': 21, 'status': status, 'conclusion': conclusion}
            with self.subTest(status=status), self.assertRaises(ValueError):
                verified_run(self.sha, {'workflow_runs': [self.run, newer]})

    def test_short_revision_is_refused(self):
        with self.assertRaises(ValueError):
            verified_run(self.sha[:7], {'workflow_runs': [self.run]})

    def test_workflow_has_no_rebase_and_pins_release_to_publication_commit(self):
        source = (Path(__file__).resolve().parents[1] / '.github/workflows/marketplace.yml').read_text()
        self.assertIn('tools/marketplace_guard.py "$GITHUB_SHA"', source)
        self.assertNotIn('--rebase', source)
        self.assertIn('"$remote_main" = "$GITHUB_SHA"', source)
        self.assertIn('--target "$PUBLICATION_COMMIT"', source)

    def test_generated_parent_requires_unchanged_source_and_regular_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            def git(*args):
                return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.DEVNULL).decode().strip()
            git('init', '-q')
            git('config', 'user.name', 'Synthetic Test')
            git('config', 'user.email', 'test@example.invalid')
            (root / 'source.md').write_text('source')
            git('add', '.')
            git('commit', '-qm', 'source')
            parent = git('rev-parse', 'HEAD')
            (root / 'plugins').mkdir()
            (root / 'plugins/output.txt').write_text('generated')
            git('add', '.')
            git('commit', '-qm', 'generated')
            current = git('rev-parse', 'HEAD')
            self.assertEqual(parent, generated_only_parent(root, current))
            payload = {'workflow_runs': [{**self.run, 'head_sha': parent}]}
            self.assertEqual(parent, verify_publication(root, current, payload)['verified_source_commit'])
            payload['workflow_runs'].append({**self.run, 'head_sha': current, 'conclusion': 'failure'})
            with self.assertRaises(ValueError):
                verify_publication(root, current, payload)
            (root / 'source.md').write_text('changed')
            git('add', '.')
            git('commit', '-qm', 'source change')
            with self.assertRaises(ValueError):
                generated_only_parent(root, git('rev-parse', 'HEAD'))
            (root / 'plugins/linked').symlink_to('../source.md')
            git('add', '.')
            git('commit', '-qm', 'linked output')
            with self.assertRaises(ValueError):
                generated_only_parent(root, git('rev-parse', 'HEAD'))


if __name__ == '__main__':
    unittest.main()
