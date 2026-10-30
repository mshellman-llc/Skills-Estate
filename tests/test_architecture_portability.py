"""Architecture selftests must work in isolated packages and detect lost resources."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import catalog
from portable import assemble, runtime_closure


class ArchitecturePortabilityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.package = self.base / 'system-design'
        item = catalog.entries(ROOT)['system-design']
        assemble(ROOT, item['source'], self.package,
                 catalog.dependencies(ROOT, item, runtime_closure))
        catalog.apply_entrypoint(self.package, 'system-design', item)
        self.formal = self.package / '_runtime/architecture-doc'

    def run_check(self, relative):
        return subprocess.run([sys.executable, str(self.package / relative)],
                              cwd=self.base, capture_output=True, text=True)

    def test_both_checks_run_without_source_siblings(self):
        for relative in ('scripts/system_design_selftest.py',
                         '_runtime/architecture-doc/scripts/architecture_doc_selftest.py'):
            with self.subTest(relative=relative):
                result = self.run_check(relative)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_embedded_mode_cannot_use_unrelated_sibling(self):
        workflow = self.formal / 'WORKFLOW.md'
        sibling = self.base / 'architecture-doc'
        sibling.mkdir()
        (sibling / 'SKILL.md').write_bytes(workflow.read_bytes())
        workflow.unlink()
        result = self.run_check('scripts/system_design_selftest.py')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('required formal architecture workflow is missing', result.stdout)

    def test_missing_template_is_a_failure(self):
        (self.formal / 'references/architecture-templates.md').unlink()
        result = self.run_check('_runtime/architecture-doc/scripts/architecture_doc_selftest.py')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('architecture-templates.md is missing', result.stdout)

    def test_missing_diagnostics_are_not_skipped(self):
        shutil.rmtree(self.package / '_runtime/prose-pass')
        result = self.run_check('_runtime/architecture-doc/scripts/architecture_doc_selftest.py')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('required diagnostic runtime missing: prose-pass', result.stdout)


if __name__ == '__main__':
    unittest.main()
