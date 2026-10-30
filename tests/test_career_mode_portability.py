"""The embedded resume workflow must invoke its bundled readiness checker."""
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


class CareerModePortabilityTests(unittest.TestCase):
    def test_checker_link_resolves_and_runs_from_embedded_directory(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td).resolve()
            package = base / 'career-application'
            item = catalog.entries(ROOT)['career-application']
            assemble(ROOT, item['source'], package,
                     catalog.dependencies(ROOT, item, runtime_closure))
            catalog.apply_entrypoint(package, 'career-application', item)
            workflow = package / '_runtime/resume-numbers-and-keywords/WORKFLOW.md'
            link = re.search(r'\[packaged readiness checker\]\(([^)]+)\)', workflow.read_text())
            self.assertIsNotNone(link)
            checker = (workflow.parent / link.group(1)).resolve()
            self.assertEqual(checker, package / 'scripts/check_role_resume_readiness.py')
            self.assertTrue(checker.is_file())
            record = base / 'fictional-career/Role_Work_Record.md'
            result = subprocess.run([sys.executable, str(checker), str(record)],
                                    cwd=workflow.parent, capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn('FAIL: role record missing:', result.stdout)
            self.assertIn(str(record), result.stdout)
            self.assertNotIn('Traceback', result.stderr)


if __name__ == '__main__':
    unittest.main()
