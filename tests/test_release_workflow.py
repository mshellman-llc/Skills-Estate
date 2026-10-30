"""Exercise audience preparation against isolated, complete synthetic packages."""
import json
from pathlib import Path
import shutil
import sys
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tests'))
import test_plugins as fixtures
import estate
import catalog
import plugins
import release_workflow as workflow
import releases


class ReleaseWorkflowTests(unittest.TestCase):
    setUp = fixtures.PluginTests.setUp
    write = fixtures.PluginTests.write

    def profiles(self):
        value = {'format': 1, 'profiles': {}}
        for name in ('personal', 'telix'):
            value['profiles'][name] = {'version': '0.1.0', 'marketplace': 'fixture-' + name,
                'plugin': 'fixture-' + name, 'description': 'Synthetic workflow.', 'entries': ['task'],
                'audience': 'personal' if name == 'personal' else 'workplace',
                'blocked_reason': None, 'privacy_review': None}
        self.write(workflow.PROFILE_FILE, value)
        self.write(workflow.HISTORY_FILE, {'format': 1, 'changes': [], 'prepared': []})
        return value

    def build(self):
        return estate.build(self.root)['source_sha256']

    def test_prepare_exact_contents_and_repeat_without_install(self):
        self.profiles()
        source = self.build()
        result = workflow.prepare(self.root, 'personal', source)
        self.assertFalse(result['installed'])
        self.assertFalse(result['published'])
        self.assertFalse(result['ready_for_distribution'])
        self.assertTrue(result['review_gaps'])
        self.assertEqual(source, estate.current_build(self.root)['source_sha256'])
        for host in ('claude', 'codex'):
            base = self.root / 'dist/profiles/personal' / host
            with zipfile.ZipFile(base / 'fixture-personal.zip') as archive:
                self.assertEqual(archive.read('skills/task/_runtime/detail/resource.txt'), b'Preserved detail implementation\n')
                self.assertIn('.claude-plugin/plugin.json', archive.namelist())
                self.assertFalse(any(p.startswith(('.git/', '.local/', 'config/')) for p in archive.namelist()))
            self.assertEqual(['task'], sorted(p.parent.name for p in (base / 'plugins/fixture-personal/skills').glob('*/SKILL.md')))
        receipt = Path(result['receipt'])
        self.assertTrue((receipt.parent / 'artifacts/claude/fixture-personal.zip').is_file())
        repeated = workflow.prepare(self.root, 'personal', source)
        self.assertEqual(result, repeated)
        self.assertEqual(1, len(workflow.history(self.root)['prepared']))

    def test_stale_wrong_hash_and_changed_same_version_refuse(self):
        self.profiles()
        source = self.build()
        with self.assertRaisesRegex(ValueError, 'expected-source'):
            workflow.prepare(self.root, 'personal', 'wrong')
        workflow.prepare(self.root, 'personal', source)
        (self.root / 'skills/detail/resource.txt').write_text('New behavior\n')
        with self.assertRaisesRegex(ValueError, 'stale'):
            workflow.prepare(self.root, 'personal', source)
        changed = self.build()
        with self.assertRaisesRegex(ValueError, 'version bump'):
            workflow.prepare(self.root, 'personal', changed)
        result = workflow.bump(self.root, 'personal', 'patch', 'Preserve new detail behavior.')
        self.assertEqual('0.1.1', result['version'])
        self.assertTrue((Path(result['backup']) / 'distribution-profiles.json').is_file())
        with self.assertRaisesRegex(ValueError, 'stale'):
            workflow.prepare(self.root, 'personal', changed)
        result = workflow.prepare(self.root, 'personal', self.build())
        self.assertEqual('0.1.0', result['previous_prepared']['version'])
        self.assertEqual(2, len(workflow.history(self.root)['prepared']))

    def test_blocked_workplace_has_no_output(self):
        profiles = self.profiles()
        profiles['profiles']['telix']['blocked_reason'] = 'Private dependency requires review.'
        self.write(workflow.PROFILE_FILE, profiles)
        with self.assertRaisesRegex(ValueError, 'Profile blocked'):
            workflow.prepare(self.root, 'telix', self.build())
        self.assertFalse((self.root / 'dist/profiles/telix').exists())

    def test_workplace_review_covers_added_private_dependency_file(self):
        profiles = self.profiles()
        # Produce synthetic bytes for independent review in a private fixture.
        profiles['profiles']['telix']['audience'] = 'personal'
        self.write(workflow.PROFILE_FILE, profiles)
        plugins.build_plugins(self.root, candidate=True, profile_name='telix')
        package = self.root / 'dist/profiles/telix/claude/plugins/fixture-telix'
        for path in ('plugin.json', '.claude-plugin/plugin.json'):
            value = json.loads((package / path).read_text())
            value.pop('repository')
            (package / path).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
        value = json.loads((package / 'estate-release.json').read_text())
        value = {k: value[k] for k in ('status', 'host_adapter', 'source_sha256', 'entries', 'required_modules')}
        (package / 'estate-release.json').write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
        profiles['profiles']['telix']['audience'] = 'workplace'
        profiles['profiles']['telix']['privacy_review'] = {'evidence': 'Synthetic fixture reviewed.', 'payload_sha256': workflow.payload_hash(package)}
        self.write(workflow.PROFILE_FILE, profiles)
        workflow.prepare(self.root, 'telix', self.build())
        (self.root / 'skills/detail/private-record.txt').write_text('Synthetic private client record\n')
        with self.assertRaisesRegex(ValueError, 'privacy review'):
            plugins.build_plugins(self.root, candidate=True, profile_name='telix')

    def test_modified_zip_and_missing_dependency_are_rejected(self):
        self.profiles()
        workflow.prepare(self.root, 'personal', self.build())
        archive = self.root / 'dist/profiles/personal/claude/fixture-personal.zip'
        with zipfile.ZipFile(archive, 'a') as output:
            output.writestr('unexpected-private.txt', 'synthetic confidential value')
        with self.assertRaisesRegex(ValueError, 'ZIP changed'):
            workflow.verify(self.root, 'personal')
        shutil.rmtree(self.root / 'skills/detail')
        with self.assertRaisesRegex(ValueError, 'mode workflow|dependency'):
            self.build()

    def test_retired_aliases_and_cancelled_closure_rejected(self):
        self.profiles()
        self.write('config/retired-entrypoints.json', {'format': 1, 'entries': {'detail': {
            'successor': 'task', 'retained_runtime': 'detail', 'allowed_as_mode': True}}, 'excluded_sources': []})
        self.assertIn('task', catalog.entries(self.root))
        original = json.loads((self.root / 'config/skill-catalog.json').read_text())
        changed = dict(original, entries={**original['entries'], 'old-alias': {'source': 'detail'}})
        self.write('config/skill-catalog.json', changed)
        with self.assertRaisesRegex(ValueError, 'Retired workflow'):
            catalog.entries(self.root)
        self.write('config/skill-catalog.json', original)
        self.write('config/retired-entrypoints.json', {'format': 1, 'entries': {}, 'excluded_sources': ['detail']})
        with self.assertRaisesRegex(ValueError, 'Excluded source'):
            self.build()

    def test_activation_cannot_restore_a_retired_destination_alias(self):
        self.profiles()
        manifest = estate.build(self.root)
        home = self.root.resolve() / 'test-home'
        release_id = releases.snapshot(self.root, home, {'task': self.root / 'build/skills/task'},
            manifest['source_sha256'], 'isolated-candidate', estate.tree_hash)
        self.write('config/retired-entrypoints.json', {'format': 1, 'entries': {'old-name': {
            'successor': 'task', 'retained_runtime': 'detail', 'allowed_as_mode': True}}})
        destination = home / '.claude/skills/old-name'
        with self.assertRaisesRegex(ValueError, 'Retired or excluded'):
            releases.activate(self.root, home, release_id, estate.tree_hash, destinations={destination: 'task'})
        self.assertFalse(destination.exists())

    def test_marketplace_redirection_is_rejected(self):
        self.profiles()
        workflow.prepare(self.root, 'personal', self.build())
        path = self.root / 'dist/profiles/personal/claude/.claude-plugin/marketplace.json'
        value = json.loads(path.read_text())
        value['plugins'][0]['source'] = '../private-tree'
        path.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, 'Marketplace differs'):
            workflow.verify(self.root, 'personal')

    def test_interrupted_history_write_recovers_and_cannot_reuse_version(self):
        self.profiles()
        source = self.build()
        write_json = estate.write_json
        def interrupted(path, value):
            if path == self.root / workflow.HISTORY_FILE:
                raise OSError('Synthetic interrupted history write')
            return write_json(path, value)
        with patch.object(estate, 'write_json', side_effect=interrupted):
            with self.assertRaisesRegex(OSError, 'interrupted'):
                workflow.prepare(self.root, 'personal', source)
        self.assertEqual([], workflow.history(self.root)['prepared'])
        workflow.prepare(self.root, 'personal', source)
        self.assertEqual(1, len(workflow.history(self.root)['prepared']))
        self.write(workflow.HISTORY_FILE, {'format': 1, 'changes': [], 'prepared': []})
        (self.root / 'skills/detail/resource.txt').write_text('Changed after interrupted preparation\n')
        with self.assertRaisesRegex(ValueError, 'version bump'):
            workflow.prepare(self.root, 'personal', self.build())

    def test_legacy_plugin_internal_closure_respects_exclusions(self):
        self.profiles()
        self.write('config/retired-entrypoints.json', {'format': 1, 'entries': {}, 'excluded_sources': ['control']})
        with self.assertRaisesRegex(ValueError, 'Excluded source'):
            plugins.build_plugins(self.root, ['estate-quality'], candidate=True)

    def test_excluded_source_can_remain_on_disk_without_reactivation(self):
        self.profiles()
        self.write('config/retired-entrypoints.json', {'format': 1, 'entries': {}, 'excluded_sources': ['cancelled-source']})
        folder = self.root / 'skills/cancelled-source'
        folder.mkdir()
        file = folder / 'SKILL.md'
        file.write_text('Unaccepted canceled source; preserve these original bytes.\n')
        before = file.read_bytes()
        digest = self.build()
        workflow.prepare(self.root, 'personal', digest)
        self.assertEqual(before, file.read_bytes())
        self.assertNotIn('cancelled-source', estate.names(self.root))
        file.write_text('A separate writer changed the excluded source.\n')
        self.assertEqual(digest, estate.source_hash(self.root))
        self.write('config/retired-entrypoints.json', {'format': 1, 'entries': {}, 'excluded_sources': ['cancelled-source', 'another-cancelled-source']})
        self.assertNotEqual(digest, estate.source_hash(self.root))
        self.write('config/runtime-dependencies.json', {'primary': ['cancelled-source']})
        with self.assertRaisesRegex(ValueError, 'Excluded source'):
            self.build()

    def test_private_review_fixture_is_not_distribution_or_approval(self):
        profiles = self.profiles()
        profiles['profiles']['telix']['blocked_reason'] = 'Await full content review.'
        self.write(workflow.PROFILE_FILE, profiles)
        result = workflow.review_fixture(self.root, 'telix')
        self.assertTrue(result['privacy_review_only'])
        self.assertFalse(result['ready_for_distribution'])
        self.assertFalse((self.root / 'dist/profiles/telix').exists())
        self.assertEqual([], workflow.history(self.root)['prepared'])
        self.assertEqual(result['payload_sha256']['claude'], result['payload_sha256']['codex'])
        self.assertIsNone(workflow.load_profile(self.root, 'telix', True)['privacy_review'])
        with self.assertRaisesRegex(ValueError, 'Profile blocked'):
            workflow.prepare(self.root, 'telix', self.build())
        with self.assertRaisesRegex(ValueError, 'workplace profile'):
            workflow.review_fixture(self.root, 'personal')

    def test_workplace_adaptations_preserve_personal_and_reject_drift(self):
        profiles = self.profiles()
        source = self.root / 'skills/detail/references/example.md'
        source.parent.mkdir()
        source.write_text('Owner-specific example. Preserve this condition.\n')
        before = source.read_bytes()
        adaptations = {'format': 1, 'references': [{'source': 'skills/detail/references/example.md',
            'source_sha256': estate.sha(before), 'edits': [{'before': 'Owner-specific example.',
            'after': 'Synthetic example.', 'count': 1}]}]}
        self.write('config/workplace-adaptations.json', adaptations)
        profiles['profiles']['telix']['reference_adaptations'] = 'config/workplace-adaptations.json'
        self.write(workflow.PROFILE_FILE, profiles)
        result = workflow.review_fixture(self.root, 'telix')
        target = Path(result['directory']) / 'claude/plugins/fixture-telix/skills/task/_runtime/detail/references/example.md'
        self.assertEqual('Synthetic example. Preserve this condition.\n', target.read_text())
        self.assertEqual(before, source.read_bytes())
        workflow.prepare(self.root, 'personal', self.build())
        personal = self.root / 'dist/profiles/personal/claude/plugins/fixture-personal/skills/task/_runtime/detail/references/example.md'
        self.assertEqual(before, personal.read_bytes())
        source.write_text('Changed personal source.\n')
        with self.assertRaisesRegex(ValueError, 'adaptation source changed'):
            workflow.review_fixture(self.root, 'telix')
        source.write_bytes(before)
        adaptations['references'][0]['edits'][0]['before'] = 'Missing text.'
        self.write('config/workplace-adaptations.json', adaptations)
        with self.assertRaisesRegex(ValueError, 'exact text'):
            workflow.review_fixture(self.root, 'telix')
        adaptations['references'][0]['source'] = 'skills/detail/scripts/arbitrary.py'
        self.write('config/workplace-adaptations.json', adaptations)
        with self.assertRaisesRegex(ValueError, 'allowed workplace resource'):
            workflow.review_fixture(self.root, 'telix')

    def test_workplace_learning_refuses_implicit_personal_store(self):
        import os
        import subprocess
        import tempfile
        spec = workflow.read(ROOT / 'config/workplace-reference-adaptations.json')
        adaptation = next(row for row in spec['references'] if row['source'] == 'skills/writing-integrity/scripts/learning.py')
        source = ROOT / adaptation['source']
        self.assertEqual(adaptation['source_sha256'], estate.sha(source.read_bytes()))
        text = source.read_text()
        for edit in adaptation['edits']:
            self.assertEqual(edit['count'], text.count(edit['before']))
            text = text.replace(edit['before'], edit['after'])
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            script = root / 'learning.py'
            script.write_text(text)
            personal = root / 'personal'
            base = [sys.executable, str(source), '--store', str(personal)]
            subprocess.run(base + ['init', '--owner', 'Synthetic Private Owner', '--profile-id', 'private',
                '--host', 'codex', '--durability', 'persistent'], check=True, capture_output=True)
            before = {p.name: p.read_bytes() for p in personal.iterdir()}
            env = dict(os.environ, WRITING_INTEGRITY_HOME=str(personal))
            missing = subprocess.run([sys.executable, str(script), 'context', '--markdown'], env=env,
                text=True, capture_output=True)
            self.assertNotEqual(0, missing.returncode)
            self.assertIn('explicit --store', missing.stderr)
            self.assertNotIn('Synthetic Private Owner', missing.stdout)
            self.assertEqual(before, {p.name: p.read_bytes() for p in personal.iterdir()})
            workplace = root / 'workplace'
            base = [sys.executable, str(script), '--store', str(workplace)]
            subprocess.run(base + ['init', '--owner', 'Synthetic Workplace Owner', '--profile-id', 'work',
                '--host', 'claude-code', '--durability', 'persistent'], check=True, capture_output=True)
            result = subprocess.run(base + ['context', '--markdown'], check=True, text=True, capture_output=True)
            self.assertIn('Synthetic Workplace Owner', result.stdout)
            self.assertNotIn('Synthetic Private Owner', result.stdout)
            self.assertEqual(before, {p.name: p.read_bytes() for p in personal.iterdir()})

    def test_real_workplace_resources_keep_diagnostics_and_personal_sources(self):
        import os
        import subprocess
        import tempfile
        from portable import assemble, runtime_closure
        profile = workflow.load_profile(ROOT, 'telix', allow_blocked=True)
        adaptations = workflow.read(ROOT / profile['reference_adaptations'])
        original = {row['source']: (ROOT / row['source']).read_bytes() for row in adaptations['references']}
        with tempfile.TemporaryDirectory() as folder:
            package = Path(folder)
            target = package / 'skills/code-simplify'
            dependencies = runtime_closure(ROOT, 'code-simplify')
            assemble(ROOT, 'code-simplify', target, dependencies)
            manifest = {'packages': {'code-simplify': {'source_module': 'code-simplify', 'runtime_dependencies': dependencies}}}
            workflow.adapt_workplace_resources(ROOT, profile, package, manifest)
            adapted = target / '_runtime'
            for module, name in [('prose-pass', 'prose_check_selftest.py'),
                                 ('prose-pass', 'prose_receipt_selftest.py'),
                                 ('writing-integrity', 'learning_selftest.py')]:
                script = adapted / module / 'scripts' / name
                result = subprocess.run([sys.executable, str(script)], cwd=script.parent,
                    env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'), capture_output=True, text=True)
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            for file in estate.files(target):
                text = file.read_text()
                for excluded in ('Gene Marsh', 'megan-writing-style', '--profile megan', '550+ automations',
                                 'two real documents, anonymized'):
                    self.assertNotIn(excluded, text, str(file))
            for name, content in original.items():
                self.assertEqual(content, (ROOT / name).read_bytes())

    def test_real_policy_preserves_all_fifteen_modes(self):
        rules = catalog.retired_entries(ROOT)
        modes = {name: rule for name, rule in rules.items() if rule.get('allowed_as_mode')}
        self.assertEqual(15, len(modes))
        public = catalog.entries(ROOT)
        for name, rule in modes.items():
            self.assertNotIn(name, public)
            self.assertIn(name, public[rule['successor']]['modes'].values())
        self.assertEqual({'build-interactive-explorer'}, catalog.excluded_sources(ROOT))


if __name__ == '__main__':
    unittest.main()
