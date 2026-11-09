"""Catch configured private names anywhere in the tracked tree without printing them."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import private_terms  # noqa: E402


class PrivateTermsTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        env = {k: v for k, v in os.environ.items() if not k.startswith(('GIT_', 'ESTATE_PRIVATE'))}
        self.env = {**env, 'GIT_AUTHOR_NAME': 'Test', 'GIT_AUTHOR_EMAIL': 'test@example.invalid',
                    'GIT_COMMITTER_NAME': 'Test', 'GIT_COMMITTER_EMAIL': 'test@example.invalid'}
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True, env=self.env)
        for name, text in {'docs/guide.md': 'Ask Example.Co for the export.\n',
                           'config/notes.json': '{"owner": "someone"}\n',
                           'plugins/estate-demo/copy.md': 'Generated copy for Example.Co.\n',
                           'skills/examplexco-task/SKILL.md': 'A clean task.\n'}.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        subprocess.run(['git', '-C', str(self.root), 'add', '-A'], check=True, env=self.env)

    def test_scan_covers_all_text_paths_and_skips_generated_plugins(self):
        hits = private_terms.scan(self.root, ['Example.Co', 'ExampleXCo'])
        self.assertEqual(sorted(hits), [('docs/guide.md', 1, 1), ('skills/examplexco-task/SKILL.md', 0, 2)])

    def test_terms_are_escaped_and_case_insensitive(self):
        self.assertEqual(private_terms.scan(self.root, ['EXAMPLE.CO'])[0][0], 'docs/guide.md')
        self.assertEqual(private_terms.scan(self.root, ['Example?Co']), [])

    def test_reports_never_print_the_term(self):
        terms = self.root.parent / (self.root.name + '-terms.json')
        terms.write_text(json.dumps(['Example.Co']))
        self.addCleanup(terms.unlink)
        done = subprocess.run([sys.executable, str(ROOT / 'tools/private_terms.py'), '--root', str(self.root)],
                              capture_output=True, text=True, env={**self.env, 'ESTATE_PRIVATE_TERMS_FILE': str(terms)})
        self.assertEqual(done.returncode, 1)
        self.assertIn('docs/guide.md:1: private term #1', done.stdout)
        self.assertNotIn('Example.Co', done.stdout)

    def test_missing_terms_skip_and_invalid_terms_fail(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(private_terms.load_terms())
        with patch.dict(os.environ, {'ESTATE_PRIVATE_TERMS': '{"name": "example"}'}, clear=True):
            with self.assertRaises(ValueError):
                private_terms.load_terms()

    def test_staged_mode_reads_the_index(self):
        (self.root / 'docs/guide.md').write_text('A clean guide.\n')
        self.assertEqual(private_terms.scan(self.root, ['Example.Co'], staged=True)[0][0], 'docs/guide.md')


class RepositoryPrivateTermsTests(unittest.TestCase):
    def test_tracked_files_carry_no_configured_private_term(self):
        terms = private_terms.load_terms()
        if terms is None:
            self.skipTest('No private terms configured')
        hits = [f'{path}:{line}: private term #{number}' for path, line, number in private_terms.scan(ROOT, terms)]
        self.assertEqual(hits, [], 'Remove the matches, or rebuild a generated file that still quotes one.')


if __name__ == '__main__':
    unittest.main()
