import hashlib
import importlib.util
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / 'artifacts' / 'skills-map'
spec = importlib.util.spec_from_file_location('map_builder', MAP / 'build.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

class SkillsMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((MAP / 'index.json').read_text())

    def test_all_canonical_skills_appear_once(self):
        expected = {p.parent.name for p in ROOT.glob('skills/*/SKILL.md')}
        actual = [s['id'] for s in self.data['skills']]
        self.assertEqual(set(actual), expected)
        self.assertEqual(len(actual), len(set(actual)))
        self.assertEqual(self.data['counts']['total'], len(expected))

    def test_exact_sources_and_resource_bytes_survive(self):
        for s in self.data['skills']:
            with self.subTest(skill=s['id']):
                folder = ROOT / 'skills' / s['id']
                raw = (folder / 'SKILL.md').read_bytes()
                self.assertEqual(s['markdown'].encode(), raw)
                self.assertEqual(s['sourceSha256'], hashlib.sha256(raw).hexdigest())
                self.assertEqual(s['resources'], builder.inventory(folder))
                self.assertIn(s['status'], {'github', 'local-revision', 'local-addition'})
                if s['status'] == 'github':
                    self.assertFalse(s['entrypointChanged'])
                if s['githubUrl'] is None:
                    self.assertEqual(s['status'], 'local-addition')

    def test_embedded_html_data_matches_json(self):
        text = (MAP/'index.html').read_text()
        embedded = re.search(r'<script type="application/json" id="estate-data">(.*?)</script>', text, re.S)[1]
        self.assertEqual(json.loads(embedded), self.data)
        self.assertNotIn('<', embedded)

    def test_connections_have_source_evidence(self):
        names={s['id'] for s in self.data['skills']}
        for s in self.data['skills']:
            for mention in s['mentions']:
                self.assertIn(mention['name'], names)
                self.assertIn(mention['name'], mention['context'])
                self.assertIn(mention['context'], s['markdown'])

    def test_markdown_cannot_execute_source_html_or_script_urls(self):
        rendered=builder.markdown('<script>alert(1)</script>\n\n[bad](javascript:alert)\n\n[good](https://example.com)')
        self.assertNotIn('<script>', rendered)
        self.assertNotIn('href="javascript:', rendered)
        self.assertIn('href="https://example.com"', rendered)

    def test_markdown_keeps_tables_and_code(self):
        rendered=builder.markdown('| Name | State |\n| --- | --- |\n| Scope | Draft |\n\n```sh\necho "safe"\n```')
        self.assertIn('<table>', rendered)
        self.assertIn('<td>Draft</td>', rendered)
        self.assertIn('echo &quot;safe&quot;', rendered)

if __name__ == '__main__':
    unittest.main()
