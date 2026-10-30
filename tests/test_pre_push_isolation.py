"""Run the actual hook with inherited Git routing and a synthetic test command."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PrePushIsolationTests(unittest.TestCase):
    def test_hook_clears_repository_routing_without_skipping_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            outer, fixture, binaries = [base / name for name in ('outer', 'fixture', 'bin')]
            for path in (outer, fixture, binaries):
                path.mkdir()
            clean_env = dict(os.environ)
            keys = subprocess.check_output(['git', 'rev-parse', '--local-env-vars'], text=True).split()
            for key in keys:
                clean_env.pop(key, None)
            clean_env.update(GIT_AUTHOR_NAME='Synthetic Test', GIT_AUTHOR_EMAIL='test@example.invalid',
                             GIT_COMMITTER_NAME='Synthetic Test', GIT_COMMITTER_EMAIL='test@example.invalid')
            subprocess.run(['git', 'init', '-q', str(outer)], check=True, env=clean_env)
            (outer / 'sentinel').write_text('Keep this source and index intact.\n')
            subprocess.run(['git', '-C', str(outer), 'add', 'sentinel'], check=True, env=clean_env)
            subprocess.run(['git', '-C', str(outer), 'commit', '-qm', 'Original'], check=True, env=clean_env)
            config_before = (outer / '.git/config').read_bytes()
            index_before = (outer / '.git/index').read_bytes()
            head_before = subprocess.check_output(['git', '-C', str(outer), 'rev-parse', 'HEAD'], env=clean_env)
            hook = outer / 'pre-push'
            shutil.copy2(ROOT / '.githooks/pre-push', hook)
            # Replace only Python execution, keeping the real hook's directory
            # selection, environment cleanup, command order and fail-fast behavior.
            python = binaries / 'python3'
            python.write_text('#!/bin/sh\nset -eu\nprintf "%s\\n" "$*" >> "$CALL_LOG"\n'
                              'test -z "${GIT_DIR+x}"\ntest -z "${GIT_WORK_TREE+x}"\n'
                              'test -z "${GIT_INDEX_FILE+x}"\ntest -z "${GIT_COMMON_DIR+x}"\n'
                              'git -C "$FIXTURE" init -q\n'
                              'git -C "$FIXTURE" config user.name "Fixture Test"\n'
                              'git -C "$FIXTURE" commit --allow-empty -qm "Fixture commit"\n'
                              'if [ "$1" = tools/run_tests.py ]; then exit "${TEST_RESULT:-0}"; fi\n')
            python.chmod(0o755)
            log = base / 'calls'
            env = {**clean_env, 'PATH': str(binaries) + os.pathsep + os.environ['PATH'],
                   'GIT_DIR': str(outer / '.git'), 'GIT_WORK_TREE': str(outer),
                   'GIT_COMMON_DIR': str(outer / '.git'),
                   'GIT_INDEX_FILE': str(outer / '.git/index'),
                   'FIXTURE': str(fixture), 'CALL_LOG': str(log)}
            for result in ('0', '7'):
                log.write_text('')
                process = subprocess.run(['sh', str(hook)], cwd=outer,
                                         env={**env, 'TEST_RESULT': result}, capture_output=True, text=True)
                self.assertEqual(int(result), process.returncode, process.stderr)
                self.assertEqual(['tools/estate.py validate',
                                  'tools/run_tests.py --report .local/pre-push-tests.json'],
                                 log.read_text().splitlines())
                self.assertTrue((fixture / '.git').is_dir())
                self.assertEqual(config_before, (outer / '.git/config').read_bytes())
                self.assertEqual(index_before, (outer / '.git/index').read_bytes())
                self.assertEqual(head_before, subprocess.check_output(
                    ['git', '-C', str(outer), 'rev-parse', 'HEAD'], env=clean_env))
