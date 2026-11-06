import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import catalog
import plugin_version


class ReleaseConsistencyTests(unittest.TestCase):
    def fixture(self, root):
        (root/'config').mkdir()
        (root/'skills/example').mkdir(parents=True)
        (root/'skills/example/SKILL.md').write_text('A synthetic workflow.')
        settings = {'version': '0.2.0', 'version_policy': 1, 'release': {}}
        (root/'config/plugin-bundles.json').write_text(json.dumps(settings))
        return settings

    def test_record_is_repeatable_and_changed_content_requires_higher_version(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); settings = self.fixture(root)
            first = plugin_version.record(root, 'Synthetic initial release')
            self.assertEqual(first, plugin_version.record(root, 'Repeat preparation'))
            plugin_version.check(root, settings)
            (root/'skills/example/SKILL.md').write_text('A changed synthetic behavior.')
            with self.assertRaisesRegex(ValueError, 'content changed'):
                plugin_version.check(root, settings)
            with self.assertRaisesRegex(ValueError, 'different content'):
                plugin_version.record(root, 'Cannot reuse the old version')
            settings['version'] = '0.2.1'
            (root/'config/plugin-bundles.json').write_text(json.dumps(settings))
            plugin_version.record(root, 'Changed behavior')
            plugin_version.check(root, settings)
            self.assertEqual(2, len(json.loads((root/plugin_version.HISTORY).read_text())['versions']))

    def test_review_receipt_changes_do_not_change_functional_version(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); settings = self.fixture(root)
            plugin_version.record(root, 'Synthetic release')
            settings['release'] = {'evidence': 'New review of the same bytes'}
            (root/'config/plugin-bundles.json').write_text(json.dumps(settings))
            plugin_version.check(root, settings)
            (root/'config/runtime-dependencies.json').write_text('{"example":["helper"]}')
            with self.assertRaises(ValueError): plugin_version.check(root, settings)

    def test_retired_names_and_aliases_refuse_while_successors_remain(self):
        policy = catalog.retired_entries(ROOT)
        self.assertEqual(16, len(policy))
        self.assertNotIn('build-interactive-explorer', catalog.excluded_sources(ROOT))
        current = json.loads((ROOT/'config/skill-catalog.json').read_text())
        catalog.check_retirements(ROOT, current)
        for name, rule in policy.items():
            with self.subTest(name=name):
                with self.assertRaises(ValueError): catalog.check_public_names(ROOT, [name])
                tampered = json.loads(json.dumps(current))
                tampered['entries'][name] = {'source': rule['retained_runtime'], 'modes': {}}
                with self.assertRaises(ValueError): catalog.check_retirements(ROOT, tampered)
                self.assertIn(rule['successor'], current['entries'])

    def test_private_career_exports_recognize_repository_boundary(self):
        script = ROOT/'skills/prepare-job-application/scripts/build_portable_bundle.py'
        spec = importlib.util.spec_from_file_location('private_export', script)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root/'config').mkdir(); (root/'config/skill-catalog.json').write_text('{}')
            skill = root/'skills/example'; skill.mkdir(parents=True)
            self.assertIn(root.resolve(), module.distribution_roots(skill))
            with patch.object(module, 'SKILL_ROOT', skill):
                with self.assertRaisesRegex(ValueError, 'outside every enclosing'):
                    module.build(root/'unused-manifest.json', root/'dist/private-export')
            self.assertFalse((root/'dist').exists())

if __name__ == '__main__': unittest.main()
