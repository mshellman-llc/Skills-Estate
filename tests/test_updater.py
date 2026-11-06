"""Updater regression tests with real local Git remotes and isolated host homes."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import estate
import releases
import updater


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.DEVNULL).decode().strip()


def commit(root, message='fixture'):
    git(root, 'add', '.')
    git(root, '-c', 'user.name=Test', '-c', 'user.email=test@example.com', '-c', 'core.hooksPath=/dev/null',
        'commit', '-qm', message)
    return git(root, 'rev-parse', 'HEAD')


class UpdaterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.remote = self.base / 'remote'; self.remote.mkdir()
        self.home = self.base / 'home'; self.home.mkdir()
        git(self.remote, 'init', '-q', '-b', 'main')
        shutil.copytree(ROOT / 'tools', self.remote / 'tools', ignore=shutil.ignore_patterns('__pycache__'))
        (self.remote / 'policies').mkdir()
        (self.remote / 'policies/brand.md').write_text('Committed policy\n')
        (self.remote / 'skills/demo').mkdir(parents=True)
        (self.remote / 'skills/demo/SKILL.md').write_text('---\nname: demo\ndescription: Example task\n---\nCommitted skill.\n')
        (self.remote / '.gitignore').write_text('build/\ndist/\n.local/\n__pycache__/\n')
        # This synthetic runner represents the fetched revision's local checks.
        # Failure switches exercise the actual subprocess boundary, not mocked success.
        (self.remote / 'tools/verify.py').write_text('''import json, pathlib, sys
r=pathlib.Path(__file__).resolve().parents[1]
if (r/'fail-tests').exists(): raise SystemExit(1)
(r/'.local').mkdir(exist_ok=True)
(r/'.local/verify-tests.json').write_text(json.dumps({'status':'passed','executed':1,'passed':1,'failures':0,'errors':0,'deferred':[]}))
''')
        self.revision = commit(self.remote)
        self.repo = self.base / 'authoring'
        subprocess.run(['git', 'clone', '-q', str(self.remote), str(self.repo)], check=True)
        self.patch_remote = patch.object(updater, 'REMOTE', str(self.remote)); self.patch_remote.start(); self.addCleanup(self.patch_remote.stop)
        self.runs = patch.object(updater, 'workflow_runs', side_effect=self.successful_runs); self.runs.start(); self.addCleanup(self.runs.stop)

    def successful_runs(self, revision):
        return [{'head_sha':revision,'head_branch':'main','path':'.github/workflows/verify.yml',
                 'id':123,'run_attempt':1,'status':'completed','conclusion':'success'}]

    def state(self):
        return updater.installation_state(self.home)

    def update(self):
        return updater.update(self.repo, self.home)

    def test_ahead_diverged_dirty_and_untracked_authoring_never_enter_update(self):
        (self.repo / 'skills/demo/SKILL.md').write_text('Local committed work')
        commit(self.repo)
        (self.remote / 'policies/brand.md').write_text('New remote policy')
        revision = commit(self.remote)
        (self.repo / 'policies/brand.md').write_text('Uncommitted tracked work')
        (self.repo / 'skills/demo/staged.txt').write_text('Staged unfinished work')
        git(self.repo, 'add', 'skills/demo/staged.txt')
        (self.repo / 'skills/private').mkdir()
        (self.repo / 'skills/private/SKILL.md').write_text('Private untracked work')
        before = (git(self.repo,'rev-parse','HEAD'),git(self.repo,'status','--porcelain'),git(self.repo,'diff','HEAD'))
        result = self.update()
        self.assertEqual(result['source_commit'], revision)
        self.assertEqual((git(self.repo,'rev-parse','HEAD'),git(self.repo,'status','--porcelain'),git(self.repo,'diff','HEAD')),before)
        installed = self.home / '.agents/skills/demo'
        self.assertIn('Committed skill', (installed/'SKILL.md').read_text())
        self.assertFalse((installed/'staged.txt').exists())
        self.assertFalse((self.home/'.claude/skills/demo').exists())
        self.assertEqual((self.home/'.config/skills-estate/repository').resolve(),self.repo)
        _,record=releases.load(self.home,result['release_id'],estate.tree_hash)
        self.assertEqual(record['repository'],str(self.repo))
        self.assertEqual(record['provenance']['source_commit'],revision)
        self.assertEqual(record['provenance']['verification']['verified_run'],123)
        self.assertTrue(releases.inspect(self.home,estate.tree_hash)['ok'])

    def test_fetch_failure_preserves_installed_release_and_claude_copy(self):
        self.update()
        duplicate=self.home/'.claude/skills/demo';duplicate.mkdir(parents=True);(duplicate/'work').write_text('keep')
        before=self.state()
        with patch.object(updater,'REMOTE',str(self.base/'absent')):
            with self.assertRaises(ValueError):self.update()
        self.assertEqual(self.state(),before)
        self.assertEqual((duplicate/'work').read_text(),'keep')

    def test_pending_failed_or_absent_remote_verification_preserves_install(self):
        self.update();before=self.state()
        for change in [{'status':'in_progress','conclusion':None},{'conclusion':'failure'},None]:
            with self.subTest(change=change):
                runs=[] if change is None else [{**self.successful_runs(self.revision)[0],**change}]
                with patch.object(updater,'workflow_runs',return_value=runs):
                    with self.assertRaises(ValueError):self.update()
                self.assertEqual(self.state(),before)

    def test_local_test_and_build_failures_preserve_install(self):
        self.update();before=self.state()
        (self.remote/'fail-tests').touch();commit(self.remote)
        with self.assertRaises(ValueError):self.update()
        self.assertEqual(self.state(),before)
        (self.remote/'fail-tests').unlink()
        (self.remote/'skills/demo/SKILL.md').write_text('Invalid committed source');commit(self.remote)
        with self.assertRaises(ValueError):self.update()
        self.assertEqual(self.state(),before)

    def test_generated_publication_reuses_only_successful_immediate_source_parent(self):
        (self.remote/'plugins').mkdir();(self.remote/'plugins/generated').write_text('Generated payload')
        published=commit(self.remote)
        with patch.object(updater,'workflow_runs',side_effect=lambda rev: [] if rev==published else self.successful_runs(rev)):
            result=self.update()
        _,record=releases.load(self.home,result['release_id'],estate.tree_hash)
        self.assertEqual(record['provenance']['verification']['verified_source_commit'],self.revision)
        self.assertEqual(record['provenance']['source_commit'],published)
        with patch.object(updater,'workflow_runs',return_value=[]):
            with self.assertRaises(ValueError):self.update()

    def test_activation_failure_restores_claude_duplicates_and_codex_links(self):
        self.update()
        duplicate=self.home/'.claude/skills/demo';duplicate.mkdir(parents=True);(duplicate/'work').write_text('keep')
        before=self.state()
        (self.remote/'policies/brand.md').write_text('Next policy');commit(self.remote)
        original=Path.symlink_to
        def fail(path,*args,**kwargs):
            if path==self.home/'.agents/skills/demo':raise OSError('Injected activation failure')
            return original(path,*args,**kwargs)
        with patch.object(Path,'symlink_to',fail):
            with self.assertRaises(OSError):self.update()
        self.assertEqual(self.state(),before)
        self.assertEqual((duplicate/'work').read_text(),'keep')

    def test_concurrent_install_change_during_preparation_is_preserved(self):
        self.update()
        original=updater.test_candidate
        def changed(*args):
            result=original(*args)
            dest=self.home/'.agents/skills/demo';dest.unlink();dest.symlink_to(self.base/'user-change')
            return result
        with patch.object(updater,'test_candidate',side_effect=changed):
            with self.assertRaisesRegex(ValueError,'changed while preparing'):self.update()
        self.assertEqual(os.readlink(self.home/'.agents/skills/demo'),str(self.base/'user-change'))

    def test_success_retains_previous_version_for_rollback(self):
        first=self.update()
        old=(self.home/'.agents/skills/demo').resolve()
        (self.remote/'policies/brand.md').write_text('Next version');commit(self.remote)
        second=self.update()
        self.assertNotEqual(first['release_id'],second['release_id'])
        self.assertTrue(old.exists())
        estate.rollback(self.repo,self.home,first['release_id'])
        self.assertEqual((self.home/'.agents/skills/demo').resolve(),old)
        self.assertTrue(releases.inspect(self.home,estate.tree_hash)['ok'])


if __name__=='__main__':unittest.main()
