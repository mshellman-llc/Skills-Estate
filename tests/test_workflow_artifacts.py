"""Keep workflow artifacts from filling the account's Actions storage."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = sorted((ROOT / '.github/workflows').glob('*.yml'))
# Artifact -> (longest retention in days, condition the upload must carry).
EXPECTED = {
    'skills-estate-render-evidence': (7, 'failure()'),
    'skill-collections': (14, "github.ref == 'refs/heads/main'"),
    'skills-estate-map': (30, "github.ref == 'refs/heads/main'"),
}


def uploads(text):
    steps = re.split(r'\n(?=      - )', text)
    return [step for step in steps if 'actions/upload-artifact@' in step]


class WorkflowArtifactTests(unittest.TestCase):
    def test_every_upload_is_known_bounded_and_conditional(self):
        seen = set()
        for workflow in WORKFLOWS:
            for step in uploads(workflow.read_text()):
                name = re.search(r'^\s+name:\s*(\S+)', step, re.M).group(1)
                with self.subTest(workflow=workflow.name, artifact=name):
                    self.assertIn(name, EXPECTED, 'add new artifacts to EXPECTED with a retention and condition')
                    limit, condition = EXPECTED[name]
                    days = re.search(r'^\s+retention-days:\s*(\d+)', step, re.M)
                    self.assertIsNotNone(days, 'set retention-days; the repository default keeps artifacts 90 days')
                    self.assertLessEqual(int(days.group(1)), limit)
                    self.assertRegex(step, re.compile(r"^\s+if:\s*" + re.escape(condition) + r"\s*$", re.M))
                    seen.add(name)
        self.assertEqual(sorted(seen), sorted(EXPECTED))

    def test_map_viewer_retention_covers_its_download(self):
        viewer = (ROOT / 'artifacts/skills-map/viewer.py').read_text()
        self.assertIn("a.get('name')=='skills-estate-map' and not a.get('expired')", viewer,
                      'the viewer must keep handling an expired map artifact')


if __name__ == '__main__':
    unittest.main()
