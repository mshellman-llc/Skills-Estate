import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'artifacts/skills-map'))
from share import render

class SharingEditionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT/'artifacts/skills-map/index.json').read_text())
        cls.page = render(cls.data)

    def test_every_skill_and_workflow_appears(self):
        for skill in self.data['skills']:
            self.assertIn(f'id="skill-{skill["id"]}"', self.page)
        for workflow in self.data['workflows']:
            self.assertIn(f'id="workflow-{workflow["id"]}"', self.page)

    def test_task_skills_name_their_plugin_command(self):
        for skill in self.data['skills']:
            own = [i for i in skill['install'] if i.get('task')]
            if own:
                self.assertIn(f'/{own[0]["plugin"]}:{own[0]["task"]}', self.page)

    def test_edition_stays_small_and_self_contained(self):
        self.assertLess(len(self.page.encode()), 150_000)
        self.assertNotIn('<script src', self.page)
        self.assertNotIn('<link', self.page)
        self.assertNotIn('"markdown"', self.page)

if __name__ == '__main__':
    unittest.main()
