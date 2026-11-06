"""Promised estimate/contract resources must work without neighboring packages."""
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import catalog
from portable import assemble, runtime_closure


class RetirementResourceClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.base = Path(cls.temp.name).resolve()
        for name in ('scope-project', 'write-statement-of-work', 'synthesize-discovery', 'write-business-case'):
            item = catalog.entries(ROOT)[name]
            package = cls.base / name
            assemble(ROOT, item['source'], package,
                     catalog.dependencies(ROOT, item, runtime_closure))
            catalog.apply_entrypoint(package, name, item)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_estimate_readmes_keep_promised_local_resources(self):
        package = self.base / 'scope-project'
        self.check_links(package, ['README.md', '_runtime/estimate-project/README.md'])

    def test_contract_readme_keeps_promised_local_resources(self):
        package = self.base / 'write-statement-of-work'
        self.check_links(package, ['_runtime/review-contract-scope/README.md'])

    def test_discovery_readmes_keep_promised_local_resources(self):
        self.check_links(self.base / 'synthesize-discovery', ['README.md', '_runtime/maintain-discovery-record/README.md'])

    def check_links(self, package, names):
        for name in names:
            file = package / name
            for href in re.findall(r'\]\(([^()\s]+)\)', file.read_text()):
                if href.startswith(('http:', 'https:', '#')):
                    continue
                target = (file.parent / href.split('#', 1)[0]).resolve()
                self.assertTrue(target.is_relative_to(package), f'{file}: escapes package: {href}')
                self.assertTrue(target.is_file(), f'{file}: missing {href}')

    def test_estimate_evidence_failure_cases_run_in_package(self):
        script = self.base / 'scope-project/_runtime/evidence-core/scripts/evidence_core_selftest.py'
        result = subprocess.run([sys.executable, str(script)], cwd=self.base,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('stale-rom-ledger.json', result.stdout)
        self.assertIn('Insufficient/readiness_gap_memo', result.stdout)

    def test_contract_hub_boundaries_run_in_package(self):
        script = self.base / 'write-statement-of-work/_runtime/manage-consulting-knowledge/scripts/hub_runtime_selftest.py'
        result = subprocess.run([sys.executable, str(script)], cwd=self.base,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn('FAIL', result.stdout)

    def test_business_case_documented_evidence_command_runs_in_isolation(self):
        package = self.base / 'write-business-case'
        instruction = (package / 'SKILL.md').read_text()
        self.assertNotIn('estate-evidence-core', instruction)
        command = re.search(r'python3 ([^\s]+evidence_core\.py) ledger\.json business_case', instruction)
        self.assertIsNotNone(command)
        checker = (package / command[1]).resolve()
        self.assertTrue(checker.is_relative_to(package))
        self.assertTrue(checker.is_file())
        result = subprocess.run([sys.executable, str(checker), '--help'], cwd=self.base,
                                capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)

    def test_every_public_package_keeps_its_readme_resources_local(self):
        for name, item in catalog.entries(ROOT).items():
            package = self.base / name
            if not package.exists():
                assemble(ROOT, item['source'], package,
                         catalog.dependencies(ROOT, item, runtime_closure))
                catalog.apply_entrypoint(package, name, item)
            readmes = [str(file.relative_to(package)) for file in package.rglob('README.md')]
            with self.subTest(entrypoint=name):
                self.check_links(package, readmes)


if __name__ == '__main__':
    unittest.main()
