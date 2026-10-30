"""The detailed specification mode must retain its executable structural check."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import catalog
from portable import assemble, runtime_closure


class SpecModePortabilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.package = self.base / 'feature-spec'
        item = catalog.entries(ROOT)['feature-spec']
        assemble(ROOT, item['source'], self.package,
                 catalog.dependencies(ROOT, item, runtime_closure))
        catalog.apply_entrypoint(self.package, 'feature-spec', item)
        self.mode = self.package / '_runtime/spec-writer'

    def run_check(self):
        return subprocess.run([sys.executable, str(self.mode / 'scripts/spec_writer_selftest.py')],
                              cwd=self.mode, capture_output=True, text=True)

    def test_structural_check_runs_in_isolated_embedded_mode(self):
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_workflow_cannot_be_hidden_by_selectable_skill_file(self):
        workflow = self.mode / 'WORKFLOW.md'
        (self.mode / 'SKILL.md').write_bytes(workflow.read_bytes())
        workflow.unlink()
        self.assertNotEqual(self.run_check().returncode, 0)

    def test_missing_acceptance_method_fails(self):
        workflow = self.mode / 'WORKFLOW.md'
        text = workflow.read_text()
        start = text.index('## Make acceptance executable')
        end = text.index('## Deliver in the requested form', start)
        workflow.write_text(text[:start] + text[end:])
        result = self.run_check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('requires observable acceptance', result.stdout)


if __name__ == '__main__':
    unittest.main()
