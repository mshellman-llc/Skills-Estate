"""Verify plugin boundaries, routing resources and release refusal."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import estate
import plugins


class PluginTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ('.local', 'config', 'policies', 'agents'):
            (self.root / name).mkdir()
        for name in ('primary', 'detail', 'control'):
            directory = self.root / 'skills' / name
            directory.mkdir(parents=True)
            (directory / 'SKILL.md').write_text(f'---\nname: {name}\ndescription: Exercise {name}.\n---\nRead the {name} workflow.\n')
        (self.root / 'skills/detail/resource.txt').write_text('Preserved detail implementation\n')
        self.write('config/skill-catalog.json', {'format': 1, 'entries': {
            'task': {'source': 'primary', 'pack': 'core', 'modes': {'detail mode': 'detail'}}}, 'internal': ['control']})
        settings = {'format': 1, 'version': '0.1.0', 'marketplace': 'private-fixture', 'bundles': {},
                    'release': {'shared': {'status': 'pending'},
                    'modules': {n: {'status': 'pending'} for n in ('primary', 'detail', 'control')}, 'routers': {}}}
        for bundle in sorted(plugins.BUNDLES):
            domain = bundle.removeprefix('estate-')
            row = {'description': 'Synthetic plugin fixture.', 'entries': ['task'] if domain == 'solutioning' else [],
                   'internal': ['control'] if domain == 'quality' else [], 'opt_in': domain == 'additional-skills'}
            if domain != 'additional-skills':
                name = domain + '-router'
                (self.root / f'agents/{name}.md').write_text(
                    f'---\nname: {name}\ndescription: Route a synthetic request.\n---\n\n'
                    '# Router\n\nRead the requested source before selecting a method.\n\n## Available skills\n\n- `primary`\n- `detail`\n')
                row.update(router_source=f'agents/{name}.md', controls=['control'], additional_routes=[])
                settings['release']['routers'][name] = {'status': 'pending'}
            settings['bundles'][bundle] = row
        self.settings = settings
        self.write('config/plugin-bundles.json', settings)

    def write(self, name, value):
        (self.root / name).write_text(json.dumps(value, indent=2) + '\n')

    def test_pilot_has_host_routes_and_complete_hidden_controls(self):
        result = plugins.build_plugins(self.root, ['estate-solutioning', 'estate-quality'], candidate=True)
        self.assertEqual('candidate-unreviewed', result['status'])
        for host in ('claude', 'codex'):
            base = self.root / 'dist/plugins' / host / 'plugins/estate-solutioning'
            self.assertTrue((base / 'skills/task/_runtime/detail/resource.txt').is_file())
            self.assertTrue((base / 'runtime/control/WORKFLOW.md').is_file())
            self.assertFalse((base / 'runtime/control/SKILL.md').exists())
            self.assertEqual({'task'} | ({'solutioning-router'} if host == 'codex' else set()),
                             {p.parent.name for p in (base / 'skills').glob('*/SKILL.md')})
            router = base / ('agents/solutioning-router.md' if host == 'claude' else 'skills/solutioning-router/SKILL.md')
            text = router.read_text()
            self.assertIn('Read the requested source before selecting a method.', text)
            self.assertIn('_runtime/detail/WORKFLOW.md', text)
            self.assertIn('runtime/control/WORKFLOW.md', text)
            for name in ('plugin.json', '.claude-plugin/plugin.json', '.codex-plugin/plugin.json'):
                self.assertEqual('estate-solutioning', json.loads((base / name).read_text())['name'])
            with zipfile.ZipFile(base.parents[1] / 'estate-solutioning.zip') as archive:
                self.assertIn('plugin.json', archive.namelist())
                self.assertFalse(any(name.startswith(('.local/', '.git/')) for name in archive.namelist()))
        # Quality routes cross-bundle primary/mode workflows as hidden resources.
        base = self.root / 'dist/plugins/codex/plugins/estate-quality'
        self.assertTrue((base / 'runtime/primary/WORKFLOW.md').is_file())
        self.assertTrue((base / 'runtime/detail/resource.txt').is_file())

    def test_default_release_refuses_pending_reviews(self):
        with self.assertRaisesRegex(ValueError, 'Release blocked'):
            plugins.build_plugins(self.root, ['estate-solutioning'])
        self.assertFalse((self.root / 'dist/plugins').exists())

    def test_acceptance_is_bound_to_source_bytes(self):
        manifest = estate.build(self.root)
        settings = self.settings
        settings['release']['shared'] = {'status': 'accepted', 'reviewed_sha256': plugins.shared_hash(self.root, settings), 'evidence': 'synthetic-review'}
        for module in settings['release']['modules']:
            settings['release']['modules'][module] = {'status': 'accepted', 'reviewed_sha256': estate.tree_hash(self.root / 'skills' / module), 'evidence': 'synthetic-review'}
        for router in settings['release']['routers']:
            settings['release']['routers'][router] = {'status': 'accepted', 'reviewed_sha256': estate.sha((self.root / f'agents/{router}.md').read_bytes()), 'evidence': 'synthetic-review'}
        self.write('config/plugin-bundles.json', settings)
        self.assertEqual('reviewed', plugins.build_plugins(self.root, ['estate-solutioning'])['status'])
        (self.root / 'skills/detail/resource.txt').write_text('Unreviewed revision\n')
        with self.assertRaisesRegex(ValueError, 'Release blocked: detail'):
            plugins.build_plugins(self.root, ['estate-solutioning'])

    def test_missing_or_duplicate_classification_fails(self):
        self.settings['bundles']['estate-quality']['entries'] = ['task']
        self.write('config/plugin-bundles.json', self.settings)
        with self.assertRaisesRegex(ValueError, 'Duplicate bundle owner'):
            plugins.config(self.root)
        self.settings['bundles']['estate-quality']['entries'] = []
        self.settings['bundles']['estate-solutioning']['entries'] = []
        self.write('config/plugin-bundles.json', self.settings)
        with self.assertRaisesRegex(ValueError, 'Missing bundle classification'):
            plugins.config(self.root)

    def test_router_cannot_select_absent_workflow(self):
        self.settings['bundles']['estate-solutioning']['additional_routes'] = ['absent']
        self.write('config/plugin-bundles.json', self.settings)
        with self.assertRaisesRegex(ValueError, 'absent workflow'):
            plugins.config(self.root)

    def test_unresolved_runtime_dependency_fails(self):
        self.write('config/runtime-dependencies.json', {'control': ['absent']})
        with self.assertRaisesRegex(ValueError, 'absent|Missing|missing'):
            plugins.build_plugins(self.root, ['estate-solutioning'], candidate=True)

    def test_candidate_build_is_reproducible(self):
        first = plugins.build_plugins(self.root, ['estate-solutioning'], candidate=True)
        second = plugins.build_plugins(self.root, ['estate-solutioning'], candidate=True)
        self.assertEqual(first['packages'], second['packages'])

    def test_duplicate_json_keys_are_not_silently_replaced(self):
        (self.root / 'config/plugin-bundles.json').write_text('{"format":1,"format":1}')
        with self.assertRaisesRegex(ValueError, 'Duplicate configuration key'):
            plugins.config(self.root)


if __name__ == '__main__':
    unittest.main()
