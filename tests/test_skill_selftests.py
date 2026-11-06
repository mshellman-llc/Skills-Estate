"""Run every skill selftest, so a new or changed skill is covered without a hand-written test.

Each `skills/<name>/scripts/*_selftest.py` becomes one test. A selftest that
needs a tool outside the standard library is listed in TOOLCHAIN and runs
only with the `skill-toolchain` integration, which CI enables.
"""
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from test_capabilities import integration

# Selftest -> what it needs beyond Python's standard library.
TOOLCHAIN = {
    'brand-renderer/scripts/extract_pptx_selftest.py': 'python-pptx',
    'configure-salesforce-project/scripts/hooks_selftest.py': 'jq',
}
TIMEOUT_SECONDS = 300


def selftests():
    return sorted((ROOT / 'skills').glob('*/scripts/*_selftest.py'))


def relative(path):
    return path.relative_to(ROOT / 'skills').as_posix()


def run_selftest(case, path):
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    result = subprocess.run([sys.executable, str(path)], cwd=path.parent.parent, capture_output=True,
                            text=True, timeout=TIMEOUT_SECONDS, env=environment)
    output = (result.stdout + result.stderr)[-4000:]
    case.assertEqual(result.returncode, 0, f'{relative(path)} failed:\n{output}')


def make_test(path):
    def test(self):
        run_selftest(self, path)
    if relative(path) in TOOLCHAIN:
        test = integration('skill-toolchain')(test)
    test.__doc__ = 'Selftest ' + relative(path)
    return test


class SkillSelftests(unittest.TestCase):
    def test_toolchain_list_names_existing_selftests(self):
        present = {relative(path) for path in selftests()}
        self.assertEqual(sorted(set(TOOLCHAIN) - present), [])

    def test_selftests_are_discovered(self):
        self.assertGreater(len(selftests()), 0)


for _path in selftests():
    _name = 'test_' + relative(_path).replace('/scripts/', '__').replace('-', '_').replace('.py', '')
    setattr(SkillSelftests, _name, make_test(_path))


if __name__ == '__main__':
    unittest.main()
