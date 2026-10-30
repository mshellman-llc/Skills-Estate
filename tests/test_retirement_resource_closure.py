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
        for name in ('project-scoping', 'statement-of-work', 'discovery'):
            item = catalog.entries(ROOT)[name]
            package = cls.base / name
            assemble(ROOT, item['source'], package,
                     catalog.dependencies(ROOT, item, runtime_closure))
            catalog.apply_entrypoint(package, name, item)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_estimate_readmes_keep_promised_local_resources(self):
        package = self.base / 'project-scoping'
        self.check_links(package, ['README.md', '_runtime/rom/README.md'])

    def test_contract_readme_keeps_promised_local_resources(self):
        package = self.base / 'statement-of-work'
        self.check_links(package, ['_runtime/sow-quality/README.md'])

    def test_discovery_readmes_keep_promised_local_resources(self):
        self.check_links(self.base / 'discovery', ['README.md', '_runtime/discovery-brief/README.md'])

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
        script = self.base / 'project-scoping/_runtime/evidence-core/scripts/evidence_core_selftest.py'
        result = subprocess.run([sys.executable, str(script)], cwd=self.base,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('stale-rom-ledger.json', result.stdout)
        self.assertIn('Insufficient/readiness_gap_memo', result.stdout)

    def test_contract_hub_boundaries_run_in_package(self):
        script = self.base / 'statement-of-work/_runtime/knowledge-hub/scripts/hub_runtime_selftest.py'
        result = subprocess.run([sys.executable, str(script)], cwd=self.base,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn('FAIL', result.stdout)


if __name__ == '__main__':
    unittest.main()
