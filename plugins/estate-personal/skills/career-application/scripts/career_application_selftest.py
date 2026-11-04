#!/usr/bin/env python3
"""Exercise career workflow resources and explicit private export with synthetic evidence."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile
import build_portable_bundle as bundle

ROOT = Path(__file__).resolve().parents[1]


class CareerPortabilityTests(unittest.TestCase):
    def test_workflow_keeps_evidence_and_submission_boundaries(self):
        text = (ROOT / 'SKILL.md').read_text()
        for required in ('filled and awaiting submission', 'explicitly authorizes',
                         'A clipped read is incomplete', 'inventory relevant prior role-specific resumes',
                         'check_role_resume_readiness.py', 'confirmed career root'):
            self.assertIn(required, text)
        self.assertTrue((ROOT / 'scripts/content-review.ts').is_file())

    def test_only_explicit_pinned_evidence_is_exported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            evidence = root / 'evidence.md'
            evidence.write_text('Synthetic candidate completed a sample project.\n')
            unrelated = root / 'not-selected.txt'
            unrelated.write_text('Private sentinel not selected for export.')
            manifest = root / 'sources.json'
            row = {'source': str(evidence), 'destination': 'references/evidence.md',
                   'sha256': hashlib.sha256(evidence.read_bytes()).hexdigest()}
            manifest.write_text(json.dumps({'format': 1, 'owner': 'Synthetic candidate', 'files': [row],
                                            'required': ['references/evidence.md']}))
            result = bundle.build(manifest, root / 'export')
            self.assertFalse(result['uploaded'])
            self.assertFalse(result['installed'])
            with ZipFile(root / 'export/career-evidence.zip') as z:
                self.assertEqual(evidence.read_bytes(), z.read('career-application/references/evidence.md'))
                self.assertFalse(any('not-selected' in name for name in z.namelist()))
            with self.assertRaisesRegex(ValueError, 'existing files'):
                bundle.build(manifest, root / 'export')
            evidence.write_text('Changed synthetic evidence.')
            with self.assertRaisesRegex(ValueError, 'stale'):
                bundle.build(manifest, root / 'new-export')
            row['destination'] = '../escape.md'
            manifest.write_text(json.dumps({'format': 1, 'owner': 'Synthetic candidate', 'files': [row]}))
            with self.assertRaisesRegex(ValueError, 'inside'):
                bundle.build(manifest, root / 'escape-export')

    def test_private_output_cannot_enter_distribution_tree(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / 'plugin'
            (plugin / '.claude-plugin').mkdir(parents=True)
            module = plugin / 'skills/career-application'
            module.mkdir(parents=True)
            alias = root / 'alias'
            alias.symlink_to(plugin, target_is_directory=True)
            with patch.object(bundle, 'SKILL_ROOT', module):
                for output in (plugin / 'skills/another-module/private', plugin / 'private', alias / 'private'):
                    with self.subTest(output=output):
                        with self.assertRaisesRegex(ValueError, 'outside every enclosing'):
                            bundle.build(root / 'unused.json', output)
                        self.assertFalse(output.exists())

    def test_missing_sources_do_not_trigger_discovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / 'sources.json'
            manifest.write_text(json.dumps({'format': 1, 'owner': 'Synthetic candidate', 'files': []}))
            with self.assertRaisesRegex(ValueError, 'explicit nonempty'):
                bundle.build(manifest, root / 'export')
            self.assertFalse((root / 'export').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
