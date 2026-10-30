import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/build-interactive-explorer'
GENERATOR = SKILL / 'scripts/create_explorer.py'
PLAN = ROOT / 'skills/roadmap-artifacts/examples/01-now-next-later.json'


class ExplorerTests(unittest.TestCase):
    def content(self):
        return json.loads((SKILL / 'assets/site/content.example.json').read_text())

    def roadmap(self):
        return {'id': 'plan', 'title': 'Delivery roadmap', 'plan': json.loads(PLAN.read_text())}

    def generate(self, data):
        folder = Path(tempfile.mkdtemp())
        source = folder / 'content.json'
        source.write_text(json.dumps(data))
        result = subprocess.run([sys.executable, str(GENERATOR), '--content', str(source), '--output', str(folder / 'site')],
                                capture_output=True, text=True)
        return result, folder / 'site/dist'

    def test_explorer_without_roadmap_has_no_kit(self):
        result, dist = self.generate(self.content())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((dist / 'roadmap-kit.js').exists())
        page = (dist / 'index.html').read_text()
        self.assertNotIn('roadmap-kit', page)
        self.assertNotIn('ROADMAP-KIT', page)

    def test_roadmap_is_embedded_without_network_resources(self):
        data = self.content()
        data['roadmaps'] = [self.roadmap()]
        result, dist = self.generate(data)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('roadmap-kit.js', (dist / 'index.html').read_text())
        for name in ('styles.css', 'roadmap-kit.css'):
            text = (dist / name).read_text()
            self.assertNotIn('@import', text)
            self.assertNotIn('http', text)

    def test_invalid_plan_is_rejected(self):
        data = self.content()
        item = self.roadmap()
        del item['plan']['id']
        data['roadmaps'] = [item]
        result, _ = self.generate(data)
        self.assertEqual(result.returncode, 1)
        self.assertIn('"id" is required', result.stderr)

    def test_live_bindings_are_rejected(self):
        data = self.content()
        item = self.roadmap()
        item['plan']['live'] = [{'block': 0}]
        data['roadmaps'] = [item]
        result, _ = self.generate(data)
        self.assertEqual(result.returncode, 1)
        self.assertIn('live bindings', result.stderr)

    def test_accent_cannot_repeat_in_headline(self):
        data = self.content()
        data['meta']['headline'] = 'Ship both ways'
        data['meta']['accent'] = 'both ways'
        result, _ = self.generate(data)
        self.assertEqual(result.returncode, 1)
        self.assertIn('meta.accent', result.stderr)


if __name__ == '__main__':
    unittest.main()
