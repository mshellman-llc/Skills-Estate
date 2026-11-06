"""Exercise installation isolation and recovery through actual filesystem changes."""
import json
from pathlib import Path
import shutil
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_estate as estate_tests
estate = estate_tests.estate
import releases


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.fixture = estate_tests.EstateTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.tearDown)
        self.root, self.home = self.fixture.root, self.fixture.home
        estate.build(self.root)
        estate.bundle(self.root)

    def test_snapshot_preserves_partial_executable_modes(self):
        script = self.root / 'skills/demo/scripts/run.py'
        script.parent.mkdir(); script.write_text('print(1)\n'); script.chmod(0o744)
        estate.build(self.root)
        before = estate.tree_hash(self.root / 'build/skills/demo')
        estate.install(self.root, self.home)
        target = self.home / '.claude/skills/demo'
        self.assertEqual(estate.tree_hash(target.resolve()), before)
        self.assertEqual((target / 'scripts/run.py').stat().st_mode & 0o111, 0o100)

    def test_dangling_legacy_link_does_not_block_build(self):
        dest = self.home / '.claude/skills/retired'
        dest.parent.mkdir(parents=True); dest.symlink_to(self.root / 'build/skills/retired')
        estate.build(self.root, home=self.home)
        self.assertTrue(dest.is_symlink())

    def test_renamed_legacy_alias_is_pinned_before_rebuild(self):
        dest = self.home / '.claude/skills/my-alias'
        dest.parent.mkdir(parents=True); dest.symlink_to(self.root / 'build/skills/demo')
        with self.assertRaisesRegex(ValueError, 'pin-installed'):
            estate.build(self.root, home=self.home)
        before = estate.tree_hash(dest.resolve())
        estate.pin_installed(self.root, self.home)
        (self.root / 'policies/brand.md').write_text('Changed')
        estate.build(self.root, home=self.home)
        self.assertEqual(estate.tree_hash(dest.resolve()), before)

    def test_deleted_legacy_alias_does_not_block_next_install(self):
        alias = self.home / '.codex/skills/demo'
        alias.parent.mkdir(parents=True); alias.symlink_to(self.root / 'build/skills/demo')
        estate.install(self.root, self.home)
        alias.unlink()
        estate.install(self.root, self.home)
        self.assertFalse(alias.exists())
        self.assertTrue(releases.inspect(self.home, estate.tree_hash)['ok'])

    def test_failed_active_write_never_becomes_rollback_target(self):
        first = estate.install(self.root, self.home)
        (self.root / 'policies/brand.md').write_text('Changed')
        estate.build(self.root)
        original = releases.write_json
        def fail_active(path, data):
            if path.name == 'active.json':
                raise OSError('active record unavailable')
            return original(path, data)
        with patch.object(releases, 'write_json', fail_active):
            with self.assertRaisesRegex(OSError, 'unavailable'):
                estate.install(self.root, self.home)
        self.assertEqual(releases.inspect(self.home, estate.tree_hash)['release_id'], first['release_id'])
        receipts = list(releases.state(self.home).glob('backup-*/receipt.json'))
        self.assertEqual(len(receipts), 1)
        self.assertEqual(len(list(releases.state(self.home).glob('backup-*/failed-plan.json'))), 1)

    def test_install_refuses_build_changed_after_manifest_check(self):
        original = releases.snapshot
        def change_build(*args, **kwargs):
            (self.root / 'build/skills/demo/SKILL.md').write_text('Changed after validation')
            return original(*args, **kwargs)
        with patch.object(releases, 'snapshot', change_build):
            with self.assertRaisesRegex(ValueError, 'Build changed after'):
                estate.install(self.root, self.home)
        self.assertFalse((self.home / '.claude/skills/demo').exists())

    def test_status_reports_broken_metadata_and_orphan_zip(self):
        (self.root / 'build/manifest.json').write_text('{')
        report = estate.status(self.root, self.home)
        self.assertIn('build', report['inspection_errors'])
        self.assertIn('demo', report['dist'])
        (self.root / 'dist/release.json').write_text('{')
        report = estate.status(self.root, self.home)
        self.assertIn('dist', report['inspection_errors'])
        self.assertFalse(report['ok'])

    def test_status_reports_retired_zip_without_catalog_or_build_entry(self):
        path = self.root / 'dist/release.json'
        record = json.loads(path.read_text())
        record['packages']['retired'] = record['packages']['demo']
        path.write_text(json.dumps(record))
        report = estate.status(self.root, self.home)
        self.assertIn('retired', report['dist'])
        self.assertFalse(report['ok'])

    def test_build_checks_explicit_home_and_git_hooks_do_not_sync(self):
        dest = self.home / '.claude/skills/demo'
        dest.parent.mkdir(parents=True); dest.symlink_to(self.root / 'build/skills/demo')
        with self.assertRaisesRegex(ValueError, 'pin-installed'):
            estate.build(self.root, home=self.home)
        repo = Path(__file__).resolve().parents[1]
        for name in ['post-commit', 'post-merge', 'post-checkout']:
            executable = [line for line in (repo / '.githooks' / name).read_text().splitlines()
                          if line.strip() and not line.startswith('#')]
            self.assertEqual(executable, ['exit 0'])

    def test_rollback_uses_latest_activation_inventory(self):
        first = estate.install(self.root, self.home)
        alias = self.home / '.codex/skills/demo'
        alias.parent.mkdir(parents=True); alias.symlink_to(self.root / 'build/skills/demo')
        second = estate.install(self.root, self.home)
        self.assertEqual(first['release_id'], second['release_id'])
        (self.root / 'policies/brand.md').write_text('Changed')
        estate.build(self.root); estate.install(self.root, self.home)
        estate.rollback(self.root, self.home, first['release_id'])
        self.assertTrue(alias.is_symlink())
        self.assertEqual(alias.resolve(), (self.home / '.claude/skills/demo').resolve())

    def test_build_and_bundle_never_change_pinned_hosts(self):
        first = estate.install(self.root, self.home)
        host = self.home / '.claude/skills/demo'
        before = estate.tree_hash(host.resolve())
        self.assertFalse((host / 'SKILL.md').stat().st_mode & 0o222)
        (self.root / 'policies/brand.md').write_text('Next policy revision\n')
        estate.build(self.root); estate.bundle(self.root)
        self.assertEqual(before, estate.tree_hash(host.resolve()))
        report = estate.status(self.root, self.home)
        self.assertEqual(report['dist']['demo'], 'current')
        self.assertEqual(report['local']['codex']['demo'], 'pinned-other-source')
        self.assertTrue(report['installed_release']['ok'])
        second = estate.install(self.root, self.home)
        self.assertNotEqual(first['release_id'], second['release_id'])
        self.assertEqual(estate.tree_hash(host.resolve()), estate.tree_hash((self.home / '.agents/skills/demo').resolve()))
        estate.rollback(self.root, self.home, first['release_id'])
        self.assertEqual(before, estate.tree_hash(host.resolve()))

    def test_stale_build_does_not_hide_stale_zip_or_account_gaps(self):
        (self.root / 'skills/demo/SKILL.md').write_text((self.root / 'skills/demo/SKILL.md').read_text() + '\nNew requirement.\n')
        report = estate.status(self.root, self.home)
        self.assertFalse(report['ok'])
        self.assertEqual(report['dist']['demo'], 'stale-source')
        self.assertIn('stale', report['build'])
        self.assertEqual(report['cloud']['chatgpt-personal']['packages']['demo'], 'pending')
        self.assertFalse(report['cloud']['cowork']['verified_live'])

    def test_pin_existing_preserves_exact_inventory_and_bytes(self):
        original = self.root / 'build/skills/demo'
        for folder in ['.claude/skills', '.codex/skills']:
            dest = self.home / folder / 'demo'
            dest.parent.mkdir(parents=True); dest.symlink_to(original)
        vendor = self.home / '.agents/skills/synced/vendor'
        vendor.mkdir(parents=True); (vendor / 'SKILL.md').write_text('Vendor content')
        before = estate.tree_hash(original)
        result = estate.pin_installed(self.root, self.home)
        self.assertEqual(result['links_changed'], 3)  # two existing skills and repository pointer
        self.assertFalse((self.home / '.agents/skills/demo').exists())
        self.assertEqual(estate.tree_hash((self.home / '.claude/skills/demo').resolve()), before)
        self.assertEqual((vendor / 'SKILL.md').read_text(), 'Vendor content')
        self.assertEqual(estate.pin_installed(self.root, self.home)['links_changed'], 0)
        estate.restore(Path(result['backup']) / 'receipt.json')
        self.assertEqual((self.home / '.claude/skills/demo').resolve(), original.resolve())

    def test_restore_does_not_relink_to_a_changed_legacy_build(self):
        dest = self.home / '.claude/skills/demo'
        dest.parent.mkdir(parents=True); dest.symlink_to(self.root / 'build/skills/demo')
        pinned = estate.pin_installed(self.root, self.home)
        (self.root / 'policies/brand.md').write_text('Changed')
        estate.build(self.root)
        with self.assertRaisesRegex(ValueError, 'Legacy build changed'):
            estate.restore(Path(pinned['backup']) / 'receipt.json')
        self.assertTrue(releases.inspect(self.home, estate.tree_hash)['ok'])

    def test_rebuild_refuses_legacy_installed_build_directory(self):
        dest = self.home / '.claude/skills/demo'
        dest.parent.mkdir(parents=True); dest.symlink_to(self.root / 'build/skills/demo')
        with patch.object(Path, 'home', return_value=self.home):
            with self.assertRaisesRegex(ValueError, 'pin-installed'):
                estate.build(self.root)
            estate.pin_installed(self.root, self.home)
            estate.build(self.root)

    def test_everyday_promotion_requires_reviewed_hash(self):
        with patch.object(Path, 'home', return_value=self.home):
            with self.assertRaisesRegex(ValueError, 'expected-source'):
                estate.install(self.root)
        self.assertFalse((self.home / '.claude/skills').exists())

    def test_tampered_snapshot_is_reported_and_not_reused(self):
        installed = estate.install(self.root, self.home)
        target = (self.home / '.claude/skills/demo/SKILL.md').resolve()
        target.chmod(0o644); target.write_text('Changed after installation')
        self.assertEqual(estate.status(self.root, self.home)['installed_release']['state'], 'damaged')
        with self.assertRaisesRegex(ValueError, 'modified'):
            estate.install(self.root, self.home)
        with self.assertRaisesRegex(ValueError, 'drift'):
            estate.rollback(self.root, self.home, installed['release_id'])

    def test_failed_second_host_update_restores_first_host_and_active_record(self):
        estate.install(self.root, self.home)
        active = (releases.state(self.home) / 'active.json').read_bytes()
        before = (self.home / '.claude/skills/demo').resolve()
        (self.root / 'policies/brand.md').write_text('New generation')
        estate.build(self.root)
        original = Path.symlink_to
        calls = []
        def fail_second(path, *args, **kwargs):
            calls.append(path)
            if len(calls) == 2:
                raise OSError('second host unavailable')
            return original(path, *args, **kwargs)
        with patch.object(Path, 'symlink_to', fail_second):
            with self.assertRaisesRegex(OSError, 'unavailable'):
                estate.install(self.root, self.home)
        self.assertEqual((self.home / '.claude/skills/demo').resolve(), before)
        self.assertEqual((self.home / '.agents/skills/demo').resolve(), before)
        self.assertEqual((releases.state(self.home) / 'active.json').read_bytes(), active)

    def test_changed_managed_link_is_preserved_on_promotion(self):
        estate.install(self.root, self.home)
        dest = self.home / '.claude/skills/demo'
        dest.unlink(); dest.mkdir(); (dest / 'user.txt').write_text('Keep')
        (self.root / 'policies/brand.md').write_text('Next version')
        estate.build(self.root)
        with self.assertRaisesRegex(ValueError, 'preserved'):
            estate.install(self.root, self.home)
        self.assertEqual((dest / 'user.txt').read_text(), 'Keep')

    def test_home_lock_covers_workers_from_different_checkouts(self):
        with releases.home_lock(self.home):
            with self.assertRaisesRegex(ValueError, 'Another installation'):
                with releases.home_lock(self.home):
                    self.fail('The second writer acquired the same home')

    def test_rollback_rejects_unactivated_snapshot(self):
        estate.install(self.root, self.home)
        (self.root / 'policies/brand.md').write_text('Unapproved generation')
        manifest = estate.build(self.root)
        staged = releases.snapshot(self.root, self.home, {'demo': self.root / 'build/skills/demo'}, manifest['source_sha256'], 'isolated-candidate', estate.tree_hash)
        with self.assertRaisesRegex(ValueError, 'never activated'):
            estate.rollback(self.root, self.home, staged)

    def test_symlinked_state_root_is_refused(self):
        target = self.home / '.local/state/skills-estate'
        target.parent.mkdir(parents=True); target.symlink_to(self.root)
        with self.assertRaisesRegex(ValueError, 'symlinked'):
            estate.install(self.root, self.home)

    def test_retired_managed_entry_is_removed_and_restored_by_rollback(self):
        demo = self.root / 'skills/demo'
        other = self.root / 'skills/other'
        shutil.copytree(demo, other)
        p = other / 'SKILL.md';p.write_text(p.read_text().replace('name: demo','name: other'))
        estate.build(self.root)
        first = estate.install(self.root, self.home)
        shutil.rmtree(other);estate.build(self.root);estate.install(self.root, self.home)
        self.assertFalse((self.home / '.claude/skills/other').exists())
        estate.rollback(self.root, self.home, first['release_id'])
        self.assertTrue((self.home / '.claude/skills/other/SKILL.md').exists())


class TargetedReleaseTests(unittest.TestCase):
    setUp = ReleaseTests.setUp
    def add_other(self):
        other = self.root / 'skills/other'
        shutil.copytree(self.root / 'skills/demo', other)
        p = other / 'SKILL.md'
        p.write_text(p.read_text().replace('name: demo', 'name: other'))
        estate.build(self.root)

    def test_targeted_promotion_keeps_unselected_paths_and_rollback_inventory(self):
        self.add_other()
        first = estate.install(self.root, self.home)
        other = self.home / '.claude/skills/other'
        original_other = other.readlink()
        original_other_bytes = (other / 'SKILL.md').read_bytes()
        (self.root / 'skills/demo/references/detail.md').write_text('Selected update')
        estate.build(self.root)
        selected = estate.install(self.root, self.home, skills=['demo'])
        self.assertEqual(other.readlink(), original_other)
        self.assertEqual((other / 'SKILL.md').read_bytes(), original_other_bytes)
        self.assertEqual(selected['links_changed'], 2)
        report = releases.inspect(self.home, estate.tree_hash)
        self.assertTrue(report['ok']); self.assertEqual(report['kind'], 'mixed-pinned')
        self.assertIsNone(report['source_sha256'])
        self.assertEqual(set(report['packages']), {'demo', 'other'})
        self.assertEqual(estate.install(self.root, self.home, skills=['demo'])['links_changed'], 0)
        (self.root / 'skills/other/references/detail.md').write_text('Second selected update')
        estate.build(self.root)
        estate.install(self.root, self.home, skills=['other'])
        estate.rollback(self.root, self.home, selected['release_id'])
        self.assertEqual(other.readlink(), original_other)
        self.assertEqual((self.home / '.agents/skills/demo/references/detail.md').read_text(), 'Selected update')
        estate.rollback(self.root, self.home, first['release_id'])
        self.assertEqual((self.home / '.agents/skills/demo/references/detail.md').read_text(), 'Meaningful detail\n')

    def test_damaged_retained_version_blocks_targeted_promotion(self):
        self.add_other(); estate.install(self.root, self.home)
        old = self.home / '.agents/skills/other/SKILL.md'
        old.chmod(0o644); old.write_text('Modified installed content')
        (self.root / 'skills/demo/references/detail.md').write_text('Update')
        estate.build(self.root)
        before = (releases.state(self.home) / 'active.json').read_bytes()
        with self.assertRaisesRegex(ValueError, 'drift'):
            estate.install(self.root, self.home, skills=['demo'])
        self.assertEqual((releases.state(self.home) / 'active.json').read_bytes(), before)

    def test_targeted_adoption_restores_legacy_link_and_retains_other_skills(self):
        self.add_other(); estate.install(self.root, self.home, skills=['other'])
        legacy = self.home / 'legacy-writing'; legacy.mkdir(); (legacy / 'SKILL.md').write_text('Previous local text')
        dest = self.home / '.agents/skills/demo'; dest.symlink_to(legacy)
        retained = (self.home / '.agents/skills/other').readlink()
        with self.assertRaisesRegex(ValueError, 'preserved'):
            estate.install(self.root, self.home, skills=['demo'])
        result = estate.install(self.root, self.home, adopt=True, skills=['demo'])
        self.assertEqual((self.home / '.agents/skills/other').readlink(), retained)
        estate.restore(Path(result['backup']) / 'receipt.json')
        self.assertEqual(dest.resolve(), legacy)
        self.assertEqual((dest / 'SKILL.md').read_text(), 'Previous local text')
        self.assertEqual((self.home / '.agents/skills/other').readlink(), retained)

    def test_targeted_failure_restores_mixed_activation(self):
        self.add_other(); estate.install(self.root, self.home)
        (self.root / 'skills/demo/references/detail.md').write_text('Selected update'); estate.build(self.root)
        estate.install(self.root, self.home, skills=['demo'])
        before = (releases.state(self.home) / 'active.json').read_bytes()
        old = (self.home / '.agents/skills/other').readlink()
        (self.root / 'skills/other/references/detail.md').write_text('Second update'); estate.build(self.root)
        original = Path.symlink_to; calls = []
        def fail_second(path, *args, **kwargs):
            calls.append(path)
            if len(calls) == 2: raise OSError('Second host failed')
            return original(path, *args, **kwargs)
        with patch.object(Path, 'symlink_to', fail_second), self.assertRaises(OSError):
            estate.install(self.root, self.home, skills=['other'])
        self.assertEqual((releases.state(self.home) / 'active.json').read_bytes(), before)
        self.assertEqual((self.home / '.agents/skills/other').readlink(), old)
        self.assertTrue(releases.inspect(self.home, estate.tree_hash)['ok'])

    def test_targeted_promotion_checks_shared_and_selected_review_gates(self):
        import plugins
        self.add_other(); manifest = estate.current_build(self.root)
        settings = {'bundles': {'all': {'entries': ['demo', 'other'], 'internal': []}},
                    'release': {'shared': {}, 'modules': {'demo': {}, 'other': {'status': 'pending'}}, 'routers': {}}}
        settings['release']['shared'] = {'status': 'accepted', 'evidence': 'synthetic independent review', 'reviewed_sha256': plugins.shared_hash(self.root, settings)}
        settings['release']['modules']['demo'] = {'status': 'accepted', 'evidence': 'synthetic task review', 'reviewed_sha256': estate.tree_hash(self.root / 'skills/demo')}
        with patch.object(Path, 'home', return_value=self.home), patch.object(plugins, 'config', return_value=settings):
            with self.assertRaisesRegex(ValueError, 'expected-source'):
                estate.install(self.root, skills=['demo'])
            estate.install(self.root, expected_source=manifest['source_sha256'], skills=['demo'])
            self.assertFalse((self.home / '.agents/skills/other').exists())
            with self.assertRaisesRegex(ValueError, 'other'):
                estate.install(self.root, expected_source=manifest['source_sha256'], skills=['other'])
            settings['release']['shared']['status'] = 'pending'
            with self.assertRaisesRegex(ValueError, 'shared assembly'):
                estate.install(self.root, expected_source=manifest['source_sha256'], skills=['demo'])

    def test_unknown_or_empty_selection_never_installs(self):
        for selection in [[], ['missing']]:
            with self.assertRaises(ValueError): estate.install(self.root, self.home, skills=selection)
        self.assertFalse((self.home / '.agents/skills').exists())


    def test_owned_alias_moves_with_selected_package(self):
        alias = self.home / '.codex/skills/my-alias'
        alias.parent.mkdir(parents=True); alias.symlink_to(self.root / 'build/skills/demo')
        estate.pin_installed(self.root, self.home)
        (self.root / 'skills/demo/references/detail.md').write_text('Alias update')
        estate.build(self.root)
        estate.install(self.root, self.home, skills=['demo'])
        self.assertEqual(alias.resolve(), (self.home / '.agents/skills/demo').resolve())
        self.assertEqual((alias / 'references/detail.md').read_text(), 'Alias update')

    def test_selected_dependency_still_needs_its_own_review(self):
        import plugins
        self.add_other(); (self.root / 'config').mkdir()
        (self.root / 'config/runtime-dependencies.json').write_text(json.dumps({'demo':['other']}))
        manifest = estate.build(self.root)
        settings = {'bundles': {}, 'release': {'shared': {}, 'modules': {'demo': {}, 'other': {'status':'pending'}}, 'routers': {}}}
        settings['release']['shared'] = {'status':'accepted','evidence':'synthetic review','reviewed_sha256':plugins.shared_hash(self.root,settings)}
        settings['release']['modules']['demo'] = {'status':'accepted','evidence':'synthetic review','reviewed_sha256':estate.tree_hash(self.root/'skills/demo')}
        gaps=plugins.release_gaps(self.root,settings,[],manifest,entrypoints=['demo'])
        self.assertEqual([g['subject'] for g in gaps],['other'])


    def test_repeated_release_id_rolls_back_to_its_latest_inventory(self):
        self.add_other(); estate.install(self.root, self.home)
        (self.root / 'skills/demo/references/detail.md').write_text('Selected update')
        (self.root / 'skills/other/references/detail.md').write_text('Neighbour update')
        estate.build(self.root)
        first = estate.install(self.root, self.home, skills=['demo'])
        old_other = (self.home / '.agents/skills/other').readlink()
        estate.install(self.root, self.home, skills=['other'])
        new_other = (self.home / '.agents/skills/other').readlink()
        again = estate.install(self.root, self.home, skills=['demo'])
        self.assertEqual(first['release_id'], again['release_id'])
        self.assertNotEqual(old_other, new_other)
        expected = json.loads((releases.state(self.home) / 'active.json').read_text())['links']
        (self.root / 'skills/demo/references/detail.md').write_text('Later update')
        estate.build(self.root); estate.install(self.root, self.home, skills=['demo'])
        estate.rollback(self.root, self.home, first['release_id'])
        self.assertEqual(json.loads((releases.state(self.home) / 'active.json').read_text())['links'], expected)
