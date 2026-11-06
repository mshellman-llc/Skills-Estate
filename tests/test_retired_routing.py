"""Retirement removes selection while preserving executable diagnostics."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import catalog
import plugins
from portable import assemble, runtime_closure


class RetiredRoutingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for directory in ('config', 'agents'):
            shutil.copytree(ROOT / directory, self.root / directory)
        # Selection validation only needs source entrypoint identities.
        for source in (ROOT / 'skills').glob('*/SKILL.md'):
            target = self.root / 'skills' / source.parent.name / 'SKILL.md'
            target.parent.mkdir(parents=True)
            target.write_bytes(source.read_bytes())

    def write_catalog(self, change):
        file = self.root / 'config/skill-catalog.json'
        record = json.loads(file.read_text())
        change(record)
        file.write_text(json.dumps(record))

    def test_retired_maintenance_modes_route_through_their_installed_owner(self):
        item = catalog.entries(ROOT)['maintain-skills-estate']
        self.assertEqual(set(item['modes'].values()),
                         {'author-estate-skill', 'release-skill-package'})
        settings = plugins.config(ROOT)
        self.assertEqual(plugins.router_modules(ROOT, settings['bundles']['estate-governance']),
                         ['maintain-skills-estate', 'load-project-context', 'capture-knowledge', 'check-knowledge-hub',
                          'reconcile-knowledge'])
        for old in item['modes'].values():
            self.assertNotIn(old, catalog.entries(ROOT))

    def test_public_alias_or_mode_cannot_revive_retired_editor(self):
        original = (self.root / 'config/skill-catalog.json').read_bytes()
        for alias in ('writing-diagnostics', 'new-editor'):
            (self.root / 'config/skill-catalog.json').write_bytes(original)
            self.write_catalog(lambda r: r['entries'].update({alias: {'source': 'writing-diagnostics'}}))
            with self.assertRaisesRegex(ValueError, 'Retired workflow'):
                catalog.entries(self.root)
        (self.root / 'config/skill-catalog.json').write_bytes(original)
        self.write_catalog(lambda r: r['entries']['review-writing'].update({'modes': {'old editor': 'writing-diagnostics'}}))
        with self.assertRaisesRegex(ValueError, 'Retired workflow'):
            catalog.entries(self.root)

    def test_router_and_additional_routes_cannot_revive_retired_editor(self):
        router = self.root / 'agents/writing-router.md'
        router.write_text(router.read_text().replace('- `review-writing`', '- `writing-diagnostics`'))
        with self.assertRaisesRegex(ValueError, 'Router selects retired'):
            catalog.entries(self.root)
        router.write_bytes((ROOT / 'agents/writing-router.md').read_bytes())
        file = self.root / 'config/plugin-bundles.json'
        data = json.loads(file.read_text())
        data['bundles']['estate-quality']['additional_routes'] = ['writing-diagnostics']
        file.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'Router selects retired'):
            plugins.config(self.root)

    def test_successor_runtime_and_catalog_are_required(self):
        self.write_catalog(lambda r: r['entries'].pop('review-writing'))
        with self.assertRaisesRegex(ValueError, 'preserve its successor'):
            catalog.entries(self.root)
        (self.root / 'config/skill-catalog.json').unlink()
        with self.assertRaisesRegex(ValueError, 'explicit skill catalog'):
            catalog.entries(self.root)

    def test_legacy_bundler_cannot_export_retired_source_or_bypass_catalog(self):
        script = ROOT / 'skills/maintain-skills-estate/scripts/build_bundles.py'
        output = self.root / 'legacy-output'
        refused = subprocess.run([sys.executable, str(script), '--source', str(ROOT / 'skills'),
                                  '--out', str(output), '--skill', 'writing-diagnostics', '--no-gate'],
                                 capture_output=True, text=True)
        self.assertEqual(refused.returncode, 2, refused.stdout + refused.stderr)
        self.assertIn('task catalog', refused.stderr)
        self.assertFalse(output.exists())
        isolated = self.root / 'non-estate/legacy-skills/writing-diagnostics'
        shutil.copytree(ROOT / 'skills/writing-diagnostics', isolated)
        skipped = subprocess.run([sys.executable, str(script), '--source', str(isolated.parent),
                                  '--out', str(output), '--skill', 'writing-diagnostics', '--no-gate'],
                                 capture_output=True, text=True)
        self.assertEqual(skipped.returncode, 0, skipped.stdout + skipped.stderr)
        self.assertIn('status internal', skipped.stdout)
        self.assertFalse(output.exists())

    def test_successor_contains_unchanged_diagnostic_capabilities_without_old_entrypoint(self):
        self.assertNotIn('writing-diagnostics', catalog.entries(ROOT))
        package = self.root / 'isolated/review-writing'
        assemble(ROOT, 'review-writing', package, runtime_closure(ROOT, 'review-writing'))
        self.assertEqual([p.relative_to(package).as_posix() for p in package.rglob('SKILL.md')], ['SKILL.md'])
        runtime = package / '_runtime/writing-diagnostics'
        self.assertTrue((runtime / 'WORKFLOW.md').is_file())
        for name in ('writing_check.py', 'prose_check.py', 'rewrite_scan.py', 'prose_receipt.py'):
            self.assertEqual((runtime / 'scripts' / name).read_bytes(),
                             (ROOT / 'skills/writing-diagnostics/scripts' / name).read_bytes())
        draft = self.root / 'draft.md'
        draft.write_text('The import failed because row 12 has no account ID.\n')
        check = subprocess.run([sys.executable, str(runtime / 'scripts/writing_check.py'), str(draft)],
                               cwd=self.root, capture_output=True, text=True)
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
        before = self.root / 'before.md'
        before.write_text('The contract covers 12 accounts.\n')
        draft.write_text('The contract covers 15 accounts.\n')
        figures = subprocess.run([sys.executable, str(runtime / 'scripts/rewrite_scan.py'), '--tie-out', str(before), str(draft)],
                                 cwd=self.root, capture_output=True, text=True)
        self.assertNotEqual(figures.returncode, 0, 'A changed commercial figure must be detected')


if __name__ == '__main__':
    unittest.main()
