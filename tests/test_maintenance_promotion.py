"""Verify scoped promotion and reversible retirement in synthetic homes."""
import json
from pathlib import Path
import shutil
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_estate
import promote_maintenance as promotion
import releases

estate = test_estate.estate


class MaintenancePromotionTests(unittest.TestCase):
    def setUp(self):
        fixture = test_estate.EstateTests()
        fixture.setUp()
        self.addCleanup(fixture.tearDown)
        self.root, self.home = fixture.root, fixture.home
        for name in (promotion.PACKAGE, *promotion.MODES):
            folder = self.root / 'skills' / name
            folder.mkdir()
            (folder / 'SKILL.md').write_text(f'---\nname: {name}\ndescription: Test this workflow.\n---\nPreserve the supplied input.\n')
        estate.build(self.root)
        estate.install(self.root, self.home)
        self.candidate = fixture.base / 'candidate'
        shutil.copytree(self.root, self.candidate)
        config = self.candidate / 'config'
        config.mkdir()
        (config / 'skill-catalog.json').write_text(json.dumps({'format': 1, 'entries': {
            'demo': {'source': 'demo', 'pack': 'core'}, promotion.PACKAGE: {'source': promotion.PACKAGE, 'pack': 'maintainer',
            'modes': {name: name for name in promotion.MODES}}}, 'internal': []}))
        self.manifest = estate.build(self.candidate)
        self.source = self.manifest['source_sha256']
        self.config = patch.object(promotion.plugins, 'config', return_value={'bundles': {}})
        self.gaps = patch.object(promotion.plugins, 'release_gaps', return_value=[])
        self.config.start(); self.gaps_mock = self.gaps.start()
        self.addCleanup(self.config.stop); self.addCleanup(self.gaps.stop)

    def active(self):
        return json.loads((releases.state(self.home) / 'active.json').read_text())

    def promote(self):
        return promotion.promote(self.candidate, self.root, self.home, self.source)

    def retirement_inputs(self):
        active = self.active()
        plan = {'active_sha256': releases.digest(active), 'remove': {
            str(self.home / host / mode): active['links'][str(self.home / host / mode)]
            for host in ('.agents/skills', '.claude/skills') for mode in promotion.MODES}}
        output = self.candidate.parent / 'native-fixture.txt'; output.write_text('Synthetic fixture only')
        native = {'package_sha256': self.manifest['packages'][promotion.PACKAGE]['sha256'],
                  'hosts': {host: {'verified': True, 'output': str(output),
                                  'output_sha256': estate.sha(output.read_bytes()),
                                  'modes': list(promotion.MODES)} for host in ('codex', 'claude')}}
        lock = self.candidate.parent / 'cleanup.lock'; lock.mkdir()
        (lock / 'owner.json').write_text(json.dumps({'chat_id': 'test-owner', 'state': 'active'}))
        return plan, native, lock, 'test-owner'

    def test_promotion_retirement_and_restore_preserve_unselected_links(self):
        before = self.active()
        promoted = self.promote()
        self.assertEqual(promoted['links_changed'], 2)
        active = self.active()
        for path, target in before['links'].items():
            if Path(path).name != promotion.PACKAGE:
                self.assertEqual(active['links'][path], target)
        _, release = releases.load(self.home, promoted['release_id'], estate.tree_hash)
        self.assertEqual(release['repository'], str(self.root))
        self.assertEqual(release['provenance']['source_checkout'], str(self.candidate))
        retired = promotion.retire(self.candidate, self.root, self.home, self.source, *self.retirement_inputs())
        self.assertEqual(retired['links_changed'], 4)
        for host in ('.agents/skills', '.claude/skills'):
            for mode in promotion.MODES:
                self.assertFalse((self.home / host / mode).exists())
        self.assertTrue(releases.inspect(self.home, estate.tree_hash)['ok'])
        estate.restore(Path(retired['backup']) / 'receipt.json')
        self.assertEqual(self.active(), active)
        estate.restore(Path(promoted['backup']) / 'receipt.json')
        self.assertEqual(self.active(), before)

    def test_wrong_source_and_stale_build_refuse_without_activation(self):
        before = self.active()
        with self.assertRaisesRegex(ValueError, 'reviewed source'):
            promotion.promote(self.candidate, self.root, self.home, 'wrong')
        (self.candidate / 'skills/demo/SKILL.md').write_text('Changed after build')
        with self.assertRaisesRegex(ValueError, 'stale'):
            self.promote()
        self.assertEqual(self.active(), before)

    def test_identity_and_drift_refuse(self):
        before = self.active()
        with self.assertRaisesRegex(ValueError, 'identity'):
            promotion.promote(self.candidate, self.candidate, self.home, self.source)
        path = self.home / '.agents/skills/demo'; path.unlink(); path.mkdir()
        with self.assertRaisesRegex(ValueError, 'drift'):
            self.promote()
        self.assertEqual(self.active(), before)

    def test_review_gaps_refuse_even_for_temporary_home(self):
        before = self.active()
        self.gaps_mock.return_value = [{'subject': 'shared assembly'}]
        with self.assertRaisesRegex(ValueError, 'review pending'):
            self.promote()
        self.assertEqual(self.active(), before)

    def test_source_change_during_snapshot_refuses_activation(self):
        before = self.active(); original = releases.snapshot
        def changed(*args, **kwargs):
            result = original(*args, **kwargs)
            (self.candidate / 'skills/demo/SKILL.md').write_text('Concurrent source edit')
            return result
        with patch.object(releases, 'snapshot', side_effect=changed):
            with self.assertRaisesRegex(ValueError, 'source changed'):
                self.promote()
        self.assertEqual(self.active(), before)

    def test_retirement_requires_owned_lock_and_exact_plan(self):
        self.promote(); before = self.active()
        plan, native, lock, owner = self.retirement_inputs()
        with self.assertRaisesRegex(ValueError, 'not owned'):
            promotion.retire(self.candidate, self.root, self.home, self.source, plan, native, lock, 'other')
        plan['remove'].pop(next(iter(plan['remove'])))
        with self.assertRaisesRegex(ValueError, 'four predecessor'):
            promotion.retire(self.candidate, self.root, self.home, self.source, plan, native, lock, owner)
        self.assertEqual(self.active(), before)

    def test_retirement_refuses_wrong_native_package_and_changed_inventory(self):
        self.promote(); before = self.active()
        plan, native, lock, owner = self.retirement_inputs()
        native['package_sha256'] = 'wrong'
        with self.assertRaisesRegex(ValueError, 'another package'):
            promotion.retire(self.candidate, self.root, self.home, self.source, plan, native, lock, owner)
        native['package_sha256'] = self.manifest['packages'][promotion.PACKAGE]['sha256']
        plan['active_sha256'] = 'changed'
        with self.assertRaisesRegex(ValueError, 'changed after'):
            promotion.retire(self.candidate, self.root, self.home, self.source, plan, native, lock, owner)
        self.assertEqual(self.active(), before)

    def test_retirement_refuses_missing_mode_or_changed_native_output(self):
        self.promote(); before = self.active()
        plan, native, lock, owner = self.retirement_inputs()
        native['hosts']['codex']['modes'] = [promotion.MODES[0]]
        with self.assertRaisesRegex(ValueError, 'both maintenance modes'):
            promotion.retire(self.candidate, self.root, self.home, self.source, plan, native, lock, owner)
        native['hosts']['codex']['modes'] = list(promotion.MODES)
        Path(native['hosts']['codex']['output']).write_text('Changed after review')
        with self.assertRaisesRegex(ValueError, 'output is missing or changed'):
            promotion.retire(self.candidate, self.root, self.home, self.source, plan, native, lock, owner)
        self.assertEqual(self.active(), before)
