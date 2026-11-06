"""Updater activation preserves duplicate copies and detects competing writers."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import test_estate

estate = test_estate.estate
releases = estate.releases


class UpdateTransactionTests(unittest.TestCase):
    def setUp(self):
        self.fixture = test_estate.EstateTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.tearDown)
        self.root, self.home = self.fixture.root, self.fixture.home
        self.claude = self.home / '.claude/skills/demo'
        self.codex = self.home / '.agents/skills/demo'
        self.pointer = self.home / '.config/skills-estate/repository'
        self.active = releases.state(self.home) / 'active.json'
        self.manifest = estate.build(self.root)
        self.release_id = releases.snapshot(self.root, self.home,
            {'demo': self.root / 'build/skills/demo'}, self.manifest['source_sha256'],
            'owner', estate.tree_hash)

    def duplicate(self):
        self.claude.mkdir(parents=True)
        (self.claude / 'notes.txt').write_text('Keep this local copy')

    def activate(self, **kwargs):
        with releases.home_lock(self.home):
            return releases.activate(self.root, self.home, self.release_id, estate.tree_hash,
                account_provided=['demo'], remove_paths=[self.claude], **kwargs)

    def test_duplicate_backup_and_codex_link_share_one_restore_receipt(self):
        self.duplicate()
        before = releases.path_state(self.claude)
        result = self.activate()
        self.assertFalse(self.claude.exists())
        self.assertTrue(self.codex.is_symlink())
        self.assertEqual(self.pointer.resolve(), self.root)
        receipt = json.loads((Path(result['backup']) / 'receipt.json').read_text())
        operation = next(op for op in receipt['operations'] if op['destination'] == str(self.claude))
        self.assertIsNone(operation['source'])
        self.assertEqual(operation['backup_state'], before)
        self.assertEqual(releases.path_state(operation['backup']), before)
        estate.restore(Path(result['backup']) / 'receipt.json')
        self.assertEqual(releases.path_state(self.claude), before)
        self.assertFalse(self.codex.exists())
        self.assertFalse(self.active.exists())

    def test_restore_refuses_changed_backup_before_changing_active_installation(self):
        self.duplicate()
        result = self.activate()
        receipt_path = Path(result['backup']) / 'receipt.json'
        receipt = json.loads(receipt_path.read_text())
        operation = next(op for op in receipt['operations'] if op['destination'] == str(self.claude))
        saved = Path(operation['backup']) / 'notes.txt'
        saved.write_text('Later backup edit')
        active_before = self.active.read_bytes()
        codex_before = releases.path_state(self.codex)
        with self.assertRaisesRegex(ValueError, 'changed during transaction'):
            estate.restore(receipt_path)
        self.assertEqual(self.active.read_bytes(), active_before)
        self.assertEqual(releases.path_state(self.codex), codex_before)
        self.assertEqual(saved.read_text(), 'Later backup edit')
        self.assertFalse(self.claude.exists())

    def test_activation_failure_after_removal_restores_duplicate_and_all_links(self):
        self.duplicate()
        before = releases.path_state(self.claude)
        write = releases.write_json
        def fail_active(path, value):
            if path == self.active:
                self.assertFalse(self.claude.exists())
                raise OSError('Injected active write failure')
            return write(path, value)
        with patch.object(releases, 'write_json', fail_active):
            with self.assertRaisesRegex(OSError, 'Injected'):
                self.activate()
        self.assertEqual(releases.path_state(self.claude), before)
        self.assertFalse(self.codex.exists())
        self.assertFalse(self.pointer.exists())
        self.assertFalse(list(releases.state(self.home).glob('backup-*/pending.json')))

    def test_only_public_claude_skills_in_new_release_can_be_removed(self):
        self.duplicate()
        for path in (self.codex, self.home / '.claude/skills/unrelated',
                     self.home / '.claude/skills/synced/demo', self.home / 'elsewhere/demo'):
            with self.subTest(path=path):
                with releases.home_lock(self.home):
                    with self.assertRaisesRegex(ValueError, 'Removal must name'):
                        releases.activate(self.root, self.home, self.release_id, estate.tree_hash,
                                          remove_paths=[path])
                self.assertTrue(self.claude.is_dir())
                self.assertFalse(self.codex.exists())
        (self.root / 'config').mkdir()
        (self.root / 'config/skill-catalog.json').write_text(json.dumps({
            'format': 1, 'entries': {}, 'internal': ['demo']}))
        with self.assertRaisesRegex(ValueError, 'Removal must name'):
            self.activate()

    def test_candidate_policy_is_separate_from_durable_repository_identity(self):
        self.duplicate()
        with tempfile.TemporaryDirectory() as directory:
            policy = Path(directory)
            (policy / 'skills/demo').mkdir(parents=True)
            (policy / 'skills/demo/SKILL.md').write_text('policy fixture')
            (self.root / 'config').mkdir()
            (self.root / 'config/retired-entrypoints.json').write_text(json.dumps({
                'format': 1, 'entries': {'demo': {}}, 'excluded_sources': []}))
            result = self.activate(policy_root=policy)
        self.assertEqual(self.pointer.resolve(), self.root)
        self.assertEqual(releases.load(self.home, result['release_id'], estate.tree_hash)[1]['repository'], str(self.root))
        self.assertTrue(releases.inspect(self.home, estate.tree_hash)['ok'])

    def test_unfinished_transaction_blocks_activation_without_mutation(self):
        self.duplicate()
        pending = releases.state(self.home) / 'backup-interrupted/pending.json'
        releases.write_json(pending, {'phase': 'prepared'})
        with self.assertRaisesRegex(ValueError, 'Unfinished installation'):
            self.activate()
        self.assertTrue(self.claude.is_dir())
        self.assertFalse(self.codex.exists())
        self.assertTrue(pending.exists())

    def test_destination_change_after_plan_is_preserved(self):
        self.duplicate()
        write = releases.write_json
        def alter_after_plan(path, value):
            result = write(path, value)
            if path.name == 'pending.json':
                self.codex.parent.mkdir(parents=True, exist_ok=True)
                self.codex.write_text('Later user edit')
            return result
        with patch.object(releases, 'write_json', alter_after_plan):
            with self.assertRaisesRegex(ValueError, 'changed during transaction'):
                self.activate()
        self.assertEqual(self.codex.read_text(), 'Later user edit')
        self.assertTrue(self.claude.is_dir())

    def test_rollback_preserves_later_destination_edit_and_blocks_next_run(self):
        self.duplicate()
        link = Path.symlink_to
        def race(path, target, **kwargs):
            if path == self.pointer:
                self.codex.unlink()
                self.codex.write_text('User changed this after it was linked')
                raise OSError('Injected failure after concurrent edit')
            return link(path, target, **kwargs)
        with patch.object(Path, 'symlink_to', race):
            with self.assertRaisesRegex(ValueError, 'recovery incomplete'):
                self.activate()
        self.assertEqual(self.codex.read_text(), 'User changed this after it was linked')
        pending = next(releases.state(self.home).glob('backup-*/pending.json'))
        self.assertEqual(json.loads(pending.read_text())['phase'], 'recovery-required')
        with self.assertRaisesRegex(ValueError, 'Unfinished installation'):
            self.activate()

    def test_active_record_change_after_plan_is_preserved(self):
        self.duplicate()
        write = releases.write_json
        def race(path, value):
            result = write(path, value)
            if path.name == 'pending.json':
                write(self.active, {'another': 'installation'})
            return result
        with patch.object(releases, 'write_json', race):
            with self.assertRaisesRegex(ValueError, 'recovery incomplete'):
                self.activate()
        self.assertEqual(json.loads(self.active.read_text()), {'another': 'installation'})
        self.assertTrue(self.claude.is_dir())
        self.assertFalse(self.codex.exists())
        self.assertTrue(list(releases.state(self.home).glob('backup-*/pending.json')))

    def test_later_active_record_change_during_receipt_failure_is_preserved(self):
        self.duplicate()
        write = releases.write_json
        def race(path, value):
            if path.name == 'receipt.json':
                write(self.active, {'another': 'activation'})
                raise OSError('Receipt unavailable')
            return write(path, value)
        with patch.object(releases, 'write_json', race):
            with self.assertRaisesRegex(ValueError, 'recovery incomplete'):
                self.activate()
        self.assertEqual(json.loads(self.active.read_text()), {'another': 'activation'})
        self.assertTrue(self.codex.is_symlink())
        self.assertTrue(list(releases.state(self.home).glob('backup-*/pending.json')))

    def test_altered_backup_is_retained_when_activation_fails(self):
        self.duplicate()
        write = releases.write_json
        def race(path, value):
            if path == self.active:
                saved = next(releases.state(self.home).glob('backup-*/.claude/skills/demo/notes.txt'))
                saved.write_text('Backup edited by another writer')
                raise OSError('Active write failed')
            return write(path, value)
        with patch.object(releases, 'write_json', race):
            with self.assertRaisesRegex(ValueError, 'recovery incomplete'):
                self.activate()
        saved = next(releases.state(self.home).glob('backup-*/.claude/skills/demo/notes.txt'))
        self.assertEqual(saved.read_text(), 'Backup edited by another writer')
        self.assertFalse(self.claude.exists())
        self.assertTrue(list(releases.state(self.home).glob('backup-*/pending.json')))

    def test_path_state_sees_hidden_files_modes_and_links_without_following(self):
        self.duplicate()
        before = releases.path_state(self.claude)
        hidden = self.claude / '.local-data'
        hidden.write_text('Private work')
        self.assertNotEqual(releases.path_state(self.claude), before)
        link = self.claude / 'outside'
        link.symlink_to(self.root)
        state = releases.path_state(self.claude)
        (self.root / 'unrelated.txt').write_text('External changes do not change a link')
        self.assertEqual(releases.path_state(self.claude), state)
        hidden.chmod(0o600)
        self.assertNotEqual(releases.path_state(self.claude), state)


if __name__ == '__main__':
    unittest.main()
