"""Keep the catalog's not-for-sale marks in step with the upstream licenses."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LicenseMarkTests(unittest.TestCase):
    def test_commons_clause_material_is_marked_not_for_sale(self):
        entries = json.loads((ROOT / 'config/skill-catalog.json').read_text())['entries']
        restricted = {path.parent.name for path in (ROOT / 'skills').glob('*/LICENSE*')
                      if 'commons clause' in path.read_text(errors='replace').lower()}
        marked = {entry['source'] for entry in entries.values() if entry.get('commercial_use') == 'not-for-sale'}
        self.assertEqual(marked, restricted)
        for name, entry in entries.items():
            if entry['source'] in restricted:
                with self.subTest(skill=name):
                    self.assertIn('Commons Clause', entry.get('license', ''))
                    self.assertTrue((ROOT / 'skills' / entry['source'] / 'UPSTREAM.md').is_file())


if __name__ == '__main__':
    unittest.main()
