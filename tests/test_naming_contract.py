"""Keep public identifiers portable and catch configured private terms in identifiers."""
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from skill_guide import scan, private_pattern


class NamingContractTests(unittest.TestCase):
    def test_public_names_match_source_and_frontmatter(self):
        entries = json.loads((ROOT / 'config/skill-catalog.json').read_text())['entries']
        for name, entry in entries.items():
            with self.subTest(name=name):
                self.assertLessEqual(len(name), 64)
                self.assertRegex(name, r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
                self.assertEqual(entry['source'], name)
                text = (ROOT / 'skills' / name / 'SKILL.md').read_text()
                self.assertEqual(re.search(r'^name: (.+)$', text, re.M)[1], name)

    def test_private_scan_includes_identifiers_and_escapes_terms(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            skill = root / 'skills' / 'example'; skill.mkdir(parents=True)
            (skill / 'SKILL.md').write_text('name: Example.Co-task\nExampleXCo\n/Users/sample/work\n')
            terms = root / 'terms.json'; terms.write_text(json.dumps(['Example.Co']))
            with patch.dict(os.environ, {'ESTATE_PRIVATE_TERMS_FILE': str(terms)}):
                findings, _ = scan(root, skill)
            self.assertEqual([hit['line'] for hit in findings], [1, 3])

    def test_invalid_private_terms_fail_explicitly(self):
        with tempfile.TemporaryDirectory() as folder:
            terms = Path(folder) / 'terms.json'; terms.write_text('{"name": "example"}')
            with patch.dict(os.environ, {'ESTATE_PRIVATE_TERMS_FILE': str(terms)}):
                with self.assertRaises(ValueError):
                    private_pattern()
