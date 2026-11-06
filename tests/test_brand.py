import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('brand', ROOT / 'tools/brand.py')
brand = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(brand)


class BrandTests(unittest.TestCase):
    def test_neutral_has_no_logo_and_css_reads_profile(self):
        p = brand.load_profile(ROOT / 'policies/brand.md')
        self.assertIsNone(p['logo'])
        p['colors']['accent'] = '#123456'
        self.assertIn('--brand-accent: #123456;', brand.css(p))

    def test_draft_and_css_injection_are_rejected(self):
        p = brand.load_profile(ROOT / 'policies/brand.md')
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / 'brand.md'
            p['status'] = 'draft'
            file.write_text('```json\n' + json.dumps(p) + '\n```')
            with self.assertRaisesRegex(ValueError, 'confirmed'):
                brand.load_profile(file)
            p['status'] = 'confirmed'; p['type']['body'] = 'Arial; background: url(https://example.com)'
            file.write_text('```json\n' + json.dumps(p) + '\n```')
            with self.assertRaisesRegex(ValueError, 'font'):
                brand.load_profile(file)


if __name__ == '__main__':
    unittest.main()
