"""Real Git fixtures prove packages use HEAD, independently of checkout state."""
from pathlib import Path
import subprocess
import shutil
import sys
import unittest
from unittest.mock import patch
import zipfile

import test_estate
import test_plugins

estate = test_estate.estate
plugins = test_plugins.plugins


def git(root, *args):
    return subprocess.run(['git', '-C', str(root), *args], check=True, capture_output=True).stdout.decode().strip()


def commit(root):
    git(root, 'add', 'skills', 'policies')
    git(root, '-c', 'user.name=Test', '-c', 'user.email=test@example.com',
        '-c', 'core.hooksPath=/dev/null', 'commit', '-qm', 'fixture')
    return git(root, 'rev-parse', 'HEAD')


class CommittedSourceTests(unittest.TestCase):
    def setUp(self):
        test_estate.EstateTests.setUp(self)
        self.addCleanup(self.tmp.cleanup)
        git(self.root, 'init', '-q')
        self.revision = commit(self.root)

    def test_dirty_staged_ignored_and_untracked_files_never_enter_build_or_install(self):
        baseline = estate.build(self.root)
        first_zip = estate.bundle(self.root)
        original = (self.root / 'skills/demo/SKILL.md').read_bytes()
        (self.root / 'skills/demo/SKILL.md').write_text('Uncommitted tracked edit')
        (self.root / 'skills/demo/references/detail.md').unlink()
        (self.root / 'skills/draft').mkdir()
        (self.root / 'skills/draft/SKILL.md').write_text('Untracked skill')
        (self.root / 'skills/demo/staged.txt').write_text('Staged but uncommitted')
        git(self.root, 'add', 'skills/demo/staged.txt')
        (self.root / '.gitignore').write_text('private.txt\n')
        (self.root / 'skills/demo/private.txt').write_text('Ignored private data')
        (self.root / 'package.json').write_text('Uncommitted dependency input')
        before = git(self.root, 'diff', 'HEAD', '--', 'skills', 'policies')
        # Force assembly again; a cache hit alone would not test source selection.
        (self.root / 'build/skills/demo/SKILL.md').write_text('Damaged generated file')
        self.assertEqual(estate.build(self.root), baseline)
        self.assertEqual(estate.bundle(self.root), first_zip)
        self.assertEqual(estate.current_build(self.root)['source_commit'], self.revision)
        with zipfile.ZipFile(self.root / 'dist/demo.zip') as archive:
            self.assertEqual(archive.read('demo/SKILL.md'), original)
            self.assertFalse(any('private' in n or 'staged' in n for n in archive.namelist()))
        estate.install(self.root, self.home)
        self.assertEqual((self.home / '.agents/skills/demo/SKILL.md').read_bytes(), original)
        self.assertTrue(estate.status(self.root, self.home)['ok'])
        self.assertEqual(git(self.root, 'diff', 'HEAD', '--', 'skills', 'policies'), before)
        self.assertEqual((self.root / 'skills/demo/SKILL.md').read_text(), 'Uncommitted tracked edit')
        self.assertEqual((self.root / 'skills/demo/private.txt').read_text(), 'Ignored private data')

    def test_new_commit_invalidates_build_and_is_required_before_install(self):
        estate.build(self.root)
        (self.root / 'policies/brand.md').write_text('Committed next version')
        revision = commit(self.root)
        with self.assertRaisesRegex(ValueError, 'stale'):
            estate.install(self.root, self.home)
        result = estate.build(self.root)
        self.assertEqual(result['source_commit'], revision)
        self.assertEqual((self.root / 'build/skills/demo/references/estate/brand.md').read_text(), 'Committed next version')

    def test_commit_modes_and_bytes_ignore_checkout_modes_and_export_attributes(self):
        script = self.root / 'skills/demo/run.sh'
        script.write_text('#!/bin/sh\necho "$Format:%H$"\n')
        script.chmod(0o755)
        (self.root / '.gitattributes').write_text('skills/demo/run.sh export-ignore export-subst\n')
        git(self.root, 'add', '.gitattributes')
        commit(self.root)
        script.chmod(0o644)
        estate.build(self.root)
        built = self.root / 'build/skills/demo/run.sh'
        self.assertEqual(built.read_bytes(), script.read_bytes())
        self.assertEqual(built.stat().st_mode & 0o777, 0o755)

    def test_head_change_during_assembly_leaves_previous_output_intact(self):
        estate.build(self.root)
        before = estate.output_inventory(self.root / 'build')
        (self.root / 'policies/brand.md').write_text('Commit two')
        commit(self.root)
        assemble = estate.assemble
        def changing(*args, **kwargs):
            result = assemble(*args, **kwargs)
            (self.root / 'policies/brand.md').write_text('Commit three')
            commit(self.root)
            return result
        with patch.object(estate, 'assemble', side_effect=changing):
            with self.assertRaisesRegex(ValueError, 'changed during'):
                estate.build(self.root)
        self.assertEqual(estate.output_inventory(self.root / 'build'), before)

    def test_committed_symlinks_are_rejected_but_untracked_links_are_ignored(self):
        link = self.root / 'skills/demo/link'
        link.symlink_to(self.home)
        estate.build(self.root)
        commit(self.root)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            estate.build(self.root)

    def test_broken_git_and_unborn_head_do_not_fall_back_to_disk(self):
        (self.root / '.git/HEAD').write_text('ref: refs/heads/missing\n')
        with self.assertRaisesRegex(ValueError, 'Cannot read committed'):
            estate.build(self.root)
        (self.root / '.git/HEAD').write_text('invalid head\n')
        with self.assertRaisesRegex(ValueError, 'Cannot read committed'):
            estate.build(self.root)

    def copy_toolchain(self):
        shutil.copytree(Path(estate.__file__).parent, self.root / 'tools',
                        ignore=shutil.ignore_patterns('__pycache__'))
        git(self.root, 'add', 'tools')
        commit(self.root)

    def test_cli_rejects_dirty_builder_before_writing_output(self):
        self.copy_toolchain()
        tool = self.root / 'tools/portable.py'
        tool.write_text(tool.read_text() + '\n# uncommitted packaging logic\n')
        result = subprocess.run([sys.executable, str(self.root / 'tools/estate.py'), 'build'],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Packaging code differs from HEAD', result.stderr)
        self.assertFalse((self.root / 'build').exists())

    def test_bundle_cli_rechecks_builder_after_build(self):
        self.copy_toolchain()
        command = [sys.executable, str(self.root / 'tools/estate.py')]
        subprocess.run([*command, 'build'], check=True, capture_output=True)
        tool = self.root / 'tools/portable.py'
        tool.write_text(tool.read_text() + '\n# local edit after build\n')
        result = subprocess.run([*command, 'bundle'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Packaging code differs from HEAD', result.stderr)
        self.assertFalse((self.root / 'dist').exists())

    def test_plugin_cli_requires_git_repository(self):
        self.copy_toolchain()
        (self.root / '.git').rename(self.root / 'saved-git')
        result = subprocess.run([sys.executable, str(self.root / 'tools/plugins.py'), '--candidate'],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Packaging requires a Git checkout', result.stderr)
        self.assertFalse((self.root / 'dist').exists())

    def test_worktree_git_file_is_supported(self):
        linked = self.base / 'linked'
        git(self.root, 'worktree', 'add', '--detach', str(linked), 'HEAD')
        (linked / '.local').mkdir()
        result = estate.build(linked)
        self.assertEqual(result['source_commit'], self.revision)


class CommittedPluginTests(unittest.TestCase):
    def setUp(self):
        test_plugins.PluginTests.setUp(self)
        git(self.root, 'init', '-q')
        git(self.root, 'add', 'agents', 'config')
        self.revision = commit(self.root)

    write = test_plugins.PluginTests.write

    def test_plugins_use_committed_config_routers_runtimes_and_dependencies(self):
        result = plugins.build_plugins(self.root, ['estate-solutioning'], candidate=True)
        (self.root / 'config/plugin-bundles.json').write_text('Invalid local config')
        (self.root / 'agents/solutioning-router.md').write_text('Local router edit')
        (self.root / 'skills/control/private.txt').write_text('Untracked secret')
        (self.root / 'skills/control/SKILL.md').write_text('Local runtime edit')
        (self.root / 'package.json').write_text('Uncommitted dependency')
        second = plugins.build_plugins(self.root, ['estate-solutioning'], candidate=True)
        self.assertEqual(second, result)
        self.assertEqual(second['source_commit'], self.revision)
        for host in ('claude', 'codex'):
            base = self.root / 'dist/plugins' / host / 'plugins/estate-solutioning'
            self.assertFalse((base / 'runtime/control/private.txt').exists())
            self.assertFalse((base / 'package.json').exists())
            self.assertIn('Read the control workflow.', (base / 'runtime/control/WORKFLOW.md').read_text())


if __name__ == '__main__':
    unittest.main()
