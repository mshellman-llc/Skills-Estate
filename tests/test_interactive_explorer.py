import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/build-interactive-explorer'
EMBED = ROOT / 'skills/build-roadmap/scripts/rk_embed.py'
PLAN = ROOT / 'skills/build-roadmap/examples/01-now-next-later.json'


class ExplorerTests(unittest.TestCase):
    def render_roadmap(self, data):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'plan.json'
            output = Path(folder) / 'roadmap.html'
            source.write_text(json.dumps(data))
            result = subprocess.run(
                [sys.executable, str(EMBED), 'page', str(source), '--output', str(output)],
                capture_output=True, text=True)
            return result, output.read_text() if output.exists() else ''

    def test_template_and_generator_are_removed(self):
        self.assertFalse((SKILL / 'assets/site').exists())
        self.assertFalse((SKILL / 'scripts/create_explorer.py').exists())
        self.assertTrue((SKILL / 'SKILL.md').is_file())

    def test_roadmap_dependency_and_routing_remain(self):
        dependencies = json.loads((ROOT / 'config/runtime-dependencies.json').read_text())
        self.assertIn('build-roadmap', dependencies['build-interactive-explorer'])
        guidance = (SKILL / 'SKILL.md').read_text()
        self.assertIn('build-review-site', guidance)
        self.assertIn('Use paths and ordered stages only when', guidance)
        self.assertNotIn('assets/site/content.example.json', guidance)

    def test_roadmap_snapshot_is_self_contained(self):
        result, page = self.render_roadmap(json.loads(PLAN.read_text()))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('RoadmapKit.mount', page)
        self.assertNotIn('@import', page)
        self.assertNotRegex(page, r'<(?:script|link)[^>]+(?:src|href)=["\']https?://')

    def test_invalid_plan_is_rejected(self):
        data = json.loads(PLAN.read_text())
        del data['id']
        result, page = self.render_roadmap(data)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('id', result.stderr)
        self.assertEqual(page, '')

    def test_live_bindings_are_rejected(self):
        data = json.loads((PLAN.parent / '06-sheets-live.json').read_text())
        result, page = self.render_roadmap(data)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('live bindings', result.stderr)
        self.assertEqual(page, '')


if __name__ == '__main__':
    unittest.main()
