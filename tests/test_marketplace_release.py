"""Exercise the actual release shell using synthetic ZIPs and an isolated gh stub."""
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def workflow_scripts():
    scripts = []
    current = None
    for line in (ROOT / '.github/workflows/marketplace.yml').read_text().splitlines():
        if line == '        run: |':
            current = []
            scripts.append(current)
        elif current is not None:
            if line.startswith('          '):
                current.append(line[10:])
            elif line.strip():
                current = None
    return ['\n'.join(lines) + '\n' for lines in scripts]


GH_STUB = r'''
import json, os, pathlib, shutil, sys
args = sys.argv[1:]
root = pathlib.Path(os.environ['STUB_ROOT'])
with (root / 'calls.jsonl').open('a') as out:
    out.write(json.dumps(args) + '\n')
config = json.loads((root / 'config.json').read_text())
action = args[1] if len(args) > 1 and args[0] == 'release' else None
if action == 'view':
    if config.get('target') is None or config.get('view_failure'):
        raise SystemExit(1)
    print(config['target'])
elif action == 'download':
    if config.get('download_failure'):
        raise SystemExit(1)
    target = pathlib.Path(args[args.index('--dir') + 1])
    target.mkdir(parents=True, exist_ok=True)
    for file in (root / 'remote').glob('*.zip'):
        shutil.copyfile(file, target / file.name)
elif action in ('upload', 'delete', 'create'):
    if action == 'create' and config.get('release_exists'):
        raise SystemExit(23)
    if config.get('fail_action') == action:
        raise SystemExit(23)
else:
    print('Unexpected gh operation: ' + repr(args), file=sys.stderr)
    raise SystemExit(99)
'''


class MarketplaceReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        gh = self.bin / 'gh'
        gh.write_text('#!' + sys.executable + '\n' + textwrap.dedent(GH_STUB))
        gh.chmod(0o755)
        self.remote = self.root / 'remote'
        self.remote.mkdir()
        self.local = self.root / 'dist/plugins/claude'
        self.local.mkdir(parents=True)
        for name in ('documents', 'solutioning'):
            self.make_zip(self.local / (name + '.zip'), name)
        self.commit = 'a' * 40
        self.script = next(script for script in workflow_scripts() if 'gh release create' in script)

    @staticmethod
    def make_zip(file, content):
        with zipfile.ZipFile(file, 'w') as archive:
            archive.writestr(zipfile.ZipInfo('plugin.txt', (2020, 1, 1, 0, 0, 0)), content)

    def copy_remote(self):
        for file in self.local.glob('*.zip'):
            (self.remote / file.name).write_bytes(file.read_bytes())

    def run_release(self, **config):
        (self.root / 'config.json').write_text(json.dumps({'target': self.commit, **config}))
        env = {'PATH': str(self.bin) + os.pathsep + '/usr/bin:/bin',
               'HOME': str(self.root), 'STUB_ROOT': str(self.root),
               'PUBLICATION_COMMIT': self.commit, 'GITHUB_SHA': 'b' * 40,
               'PYTHONDONTWRITEBYTECODE': '1'}
        result = subprocess.run(['/bin/bash', '--noprofile', '--norc', '-e', '-o', 'pipefail', '-c', self.script],
                                cwd=self.root, env=env, capture_output=True, text=True)
        calls = [json.loads(line) for line in (self.root / 'calls.jsonl').read_text().splitlines()]
        return result, calls

    def assert_uploaded_current_zips(self, calls):
        uploads = [call for call in calls if call[:2] == ['release', 'upload']]
        self.assertEqual(1, len(uploads), calls)
        self.assertEqual(['release', 'upload', 'plugins-latest',
                          'dist/plugins/claude/documents.zip', 'dist/plugins/claude/solutioning.zip',
                          '--clobber'], uploads[0])
        self.assertFalse(any(call[1] in ('delete', 'create') for call in calls))

    def test_all_workflow_shell_blocks_parse(self):
        self.assertGreaterEqual(len(workflow_scripts()), 4)
        for script in workflow_scripts():
            result = subprocess.run(['/bin/bash', '-n'], input=script, capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stderr)

    def test_identical_target_and_contents_perform_no_write(self):
        self.copy_remote()
        result, calls = self.run_release()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(['view', 'download'], [call[1] for call in calls])
        self.assertIn('already match', result.stdout)

    def test_missing_remote_assets_are_repaired(self):
        result, calls = self.run_release(download_failure=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assert_uploaded_current_zips(calls)

    def test_partial_remote_assets_are_repaired(self):
        self.copy_remote()
        (self.remote / 'solutioning.zip').unlink()
        result, calls = self.run_release()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assert_uploaded_current_zips(calls)

    def test_different_remote_assets_are_repaired(self):
        self.copy_remote()
        self.make_zip(self.remote / 'documents.zip', 'old')
        result, calls = self.run_release()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assert_uploaded_current_zips(calls)

    def test_changed_target_creates_release_pinned_to_publication_commit(self):
        result, calls = self.run_release(target='c' * 40)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(['view', 'delete', 'create'], [call[1] for call in calls])
        create = calls[-1]
        self.assertEqual(self.commit, create[create.index('--target') + 1])
        self.assertIn('dist/plugins/claude/documents.zip', create)
        self.assertIn('dist/plugins/claude/solutioning.zip', create)

    def test_absent_release_is_created_without_deletion(self):
        result, calls = self.run_release(target=None)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(['view', 'create'], [call[1] for call in calls])

    def test_failed_lookup_does_not_delete_an_existing_release(self):
        result, calls = self.run_release(view_failure=True, release_exists=True)
        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(['view', 'create'], [call[1] for call in calls])

    def test_extra_remote_zip_requires_review_without_writes(self):
        self.copy_remote()
        self.make_zip(self.remote / 'obsolete.zip', 'old bundle')
        result, calls = self.run_release()
        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(['view', 'download'], [call[1] for call in calls])
        self.assertNotIn('already match', result.stdout)
        self.assertIn('review', (result.stdout + result.stderr).lower())

    def test_upload_error_is_not_reported_as_success(self):
        result, calls = self.run_release(download_failure=True, fail_action='upload')
        self.assertEqual(23, result.returncode, result.stdout + result.stderr)
        self.assert_uploaded_current_zips(calls)

    def test_create_error_is_not_reported_as_success(self):
        result, calls = self.run_release(target='c' * 40, fail_action='create')
        self.assertEqual(23, result.returncode, result.stdout + result.stderr)
        self.assertEqual('create', calls[-1][1])


if __name__ == '__main__':
    unittest.main()
