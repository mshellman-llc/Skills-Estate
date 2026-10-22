import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

SPEC = importlib.util.spec_from_file_location('estate', Path(__file__).resolve().parents[1] / 'tools/estate.py')
estate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(estate)


class EstateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.root = self.base / 'repo'
        self.home = self.base / 'home'
        self.root.mkdir(); self.home.mkdir()
        (self.root / '.local').mkdir()
        (self.root / 'policies').mkdir()
        (self.root / 'policies/brand.md').write_text('Shared brand revision one\n')
        (self.root / 'skills/demo/references').mkdir(parents=True)
        (self.root / 'skills/demo/SKILL.md').write_text('---\nname: demo\ndescription: Test a package\n---\nRead [brand](references/estate/brand.md) and [detail](references/detail.md).\n')
        (self.root / 'skills/demo/references/detail.md').write_text('Meaningful detail\n')

    def tearDown(self):
        self.tmp.cleanup()

    def test_shared_policy_is_vendored_and_changed_policy_makes_build_stale(self):
        first = estate.build(self.root)
        self.assertEqual((self.root / 'build/skills/demo/references/estate/brand.md').read_text(), 'Shared brand revision one\n')
        (self.root / 'policies/brand.md').write_text('Revision two\n')
        with self.assertRaisesRegex(ValueError, 'stale'):
            estate.current_build(self.root)
        second = estate.build(self.root)
        self.assertNotEqual(first['packages']['demo']['sha256'], second['packages']['demo']['sha256'])

    def test_status_reports_unmanaged_symlink_content_without_aborting_other_skills(self):
        estate.build(self.root)
        dest = self.home / '.claude/skills/demo'
        dest.mkdir(parents=True)
        (dest / 'runtime-link').symlink_to('/usr/bin/python3')
        result = estate.status(self.root, self.home)
        self.assertFalse(result['ok'])
        self.assertEqual('drift', result['local']['claude-code']['demo'])
        self.assertIn(str(dest), result['inspection_errors'])
        self.assertEqual('missing', result['local']['codex']['demo'])

    def test_install_links_both_hosts_and_is_idempotent(self):
        estate.build(self.root)
        self.assertEqual(estate.install(self.root, self.home)['links_changed'], 3)
        self.assertEqual(estate.install(self.root, self.home)['links_changed'], 0)
        self.assertTrue(estate.status(self.root, self.home)['ok'])

    def test_conflict_is_detected_before_any_install(self):
        estate.build(self.root)
        dest = self.home / '.agents/skills/demo'
        dest.mkdir(parents=True); (dest / 'mine.txt').write_text('Keep this')
        with self.assertRaisesRegex(ValueError, 'preserved'):
            estate.install(self.root, self.home)
        self.assertFalse((self.home / '.claude/skills/demo').exists())
        self.assertEqual((dest / 'mine.txt').read_text(), 'Keep this')

    def test_adoption_restores_original_directory_and_symlink(self):
        estate.build(self.root)
        original = self.home / '.agents/skills/demo'
        original.mkdir(parents=True); (original / 'mine.txt').write_text('Keep this')
        claude = self.home / '.claude/skills/demo'
        claude.parent.mkdir(parents=True); claude.symlink_to(original)
        result = estate.install(self.root, self.home, adopt=True)
        self.assertTrue(estate.status(self.root, self.home)['ok'])
        estate.restore(Path(result['backup']) / 'receipt.json')
        self.assertFalse(original.is_symlink())
        self.assertTrue(claude.is_symlink())
        self.assertEqual((claude / 'mine.txt').read_text(), 'Keep this')

    def test_restore_refuses_user_changed_destination(self):
        estate.build(self.root)
        result = estate.install(self.root, self.home)
        dest = self.home / '.claude/skills/demo'
        dest.unlink(); dest.mkdir()
        with self.assertRaisesRegex(ValueError, 'Changed'):
            estate.restore(Path(result['backup']) / 'receipt.json')
        self.assertTrue(dest.is_dir())

    def test_install_failure_rolls_back_moved_originals(self):
        estate.build(self.root)
        dest = self.home / '.claude/skills/demo'
        dest.mkdir(parents=True); (dest / 'mine.txt').write_text('Original')
        with patch.object(Path, 'symlink_to', side_effect=OSError('simulated failure')):
            with self.assertRaises(OSError):
                estate.install(self.root, self.home, adopt=True)
        self.assertEqual((dest / 'mine.txt').read_text(), 'Original')

    def test_generated_edits_are_not_silently_installed(self):
        estate.build(self.root)
        (self.root / 'build/skills/demo/SKILL.md').write_text('edited')
        with self.assertRaisesRegex(ValueError, 'modified'):
            estate.install(self.root, self.home)

    def test_concurrent_source_edit_does_not_publish_a_mixed_build(self):
        original = estate.assemble
        def changed(*args, **kwargs):
            result = original(*args, **kwargs)
            (self.root / 'policies/brand.md').write_text('Concurrent change')
            return result
        with patch.object(estate, 'assemble', side_effect=changed):
            with self.assertRaisesRegex(ValueError, 'changed during'):
                estate.build(self.root)
        self.assertFalse((self.root / 'build').exists())

    def test_builder_changes_invalidate_cached_packages(self):
        (self.root / 'tools').mkdir()
        code = self.root / 'tools/builder.py'
        code.write_text('print("first")\n')
        estate.build(self.root)
        code.write_text('print("second")\n')
        with self.assertRaisesRegex(ValueError, 'stale'):
            estate.current_build(self.root)

    def test_runtime_is_vendored_once_and_entrypoint_links_are_rewritten(self):
        dep = self.root / 'skills/helper'
        dep.mkdir()
        (dep / 'SKILL.md').write_text('---\nname: helper\ndescription: Helper workflow\n---\nSpecific helper instructions.\n')
        (dep / 'run.py').write_text('print("helper executed")\n')
        (self.root / 'skills/demo/SKILL.md').write_text(
            '---\nname: demo\ndescription: Test dependency\n---\nUse [helper](../helper/SKILL.md).\n')
        (self.root / 'config').mkdir()
        (self.root / 'config/runtime-dependencies.json').write_text('{"demo":["helper"]}\n')
        estate.build(self.root)
        package = self.root / 'build/skills/demo'
        self.assertEqual(1, len(list(package.rglob('SKILL.md'))))
        self.assertIn('_runtime/helper/WORKFLOW.md', (package / 'SKILL.md').read_text())
        self.assertIn('Specific helper instructions', (package / '_runtime/helper/WORKFLOW.md').read_text())
        self.assertTrue((package / '_runtime/helper/run.py').exists())

    def test_executable_permissions_survive_packaging_and_affect_drift(self):
        script = self.root / 'skills/demo/run.sh'
        script.write_text('#!/bin/sh\nexit 0\n')
        script.chmod(0o755)
        estate.build(self.root)
        estate.bundle(self.root)
        with zipfile.ZipFile(self.root / 'dist/demo.zip') as archive:
            self.assertEqual(0o755, (archive.getinfo('demo/run.sh').external_attr >> 16) & 0o777)
        (self.root / 'build/skills/demo/run.sh').chmod(0o644)
        with self.assertRaisesRegex(ValueError, 'modified'):
            estate.current_build(self.root)

    def test_bundle_is_deterministic_and_self_contained(self):
        estate.build(self.root)
        a = estate.bundle(self.root)
        b = estate.bundle(self.root)
        self.assertEqual(a, b)
        with zipfile.ZipFile(self.root / 'dist/demo.zip') as z:
            self.assertIn('demo/SKILL.md', z.namelist())
            self.assertIn('demo/references/estate/brand.md', z.namelist())
            self.assertFalse(any('..' in Path(n).parts or n.startswith('/') for n in z.namelist()))

    def test_missing_reference_fails(self):
        (self.root / 'skills/demo/references/detail.md').unlink()
        with self.assertRaisesRegex(ValueError, 'missing reference'):
            estate.validate(self.root)

    def test_source_symlink_is_rejected(self):
        (self.root / 'skills/demo/leak').symlink_to(self.base)
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            estate.validate(self.root)

    def test_empty_estate_fails(self):
        (self.root / 'skills/demo/SKILL.md').unlink()
        with self.assertRaisesRegex(ValueError, 'No skills'):
            estate.validate(self.root)

    def test_account_upload_is_reported_not_verified_and_invalidates_on_change(self):
        estate.build(self.root); estate.bundle(self.root); estate.install(self.root, self.home)
        estate.record_publication(self.root, 'claude-account', 'demo', 'test-account upload record')
        status = estate.status(self.root, self.home)
        self.assertEqual(status['cloud']['claude-account']['packages']['demo'], 'reported-current')
        self.assertFalse(status['cloud']['claude-account']['verified_live'])
        (self.root / 'policies/brand.md').write_text('Changed')
        estate.build(self.root); estate.bundle(self.root)
        status = estate.status(self.root, self.home)
        self.assertEqual(status['cloud']['claude-account']['packages']['demo'], 'pending')

    def test_unmanaged_and_account_downloads_are_untouched(self):
        external = self.home / '.claude/skills/synced/account/other'
        external.mkdir(parents=True); (external / 'SKILL.md').write_text('Account content')
        estate.build(self.root); estate.install(self.root, self.home)
        self.assertEqual((external / 'SKILL.md').read_text(), 'Account content')
        self.assertTrue(estate.status(self.root, self.home)['external_skill_locations'])

    def test_selftest_fixture_paths_are_preserved_without_becoming_dependencies(self):
        (self.root / 'skills/_shared').mkdir()
        scripts = self.root / 'skills/demo/scripts'
        scripts.mkdir()
        fixture = scripts / 'demo_selftest.py'
        fixture.write_text("fixture = '_shared/does-not-exist.md'\n")
        estate.build(self.root)
        self.assertEqual((self.root / 'build/skills/demo/scripts/demo_selftest.py').read_bytes(),
                         fixture.read_bytes())
        (scripts / 'runtime.py').write_text("required = '_shared/does-not-exist.md'\n")
        with self.assertRaisesRegex(ValueError, 'Missing shared reference'):
            estate.build(self.root)


if __name__ == '__main__':
    unittest.main()
