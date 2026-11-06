"""Materialize source blobs from one Git commit, without checkout filters or attributes."""
from contextlib import contextmanager
from pathlib import Path
import io
import os
import subprocess
import tempfile

SOURCE_PATHS = ('skills', 'policies', 'tools', 'agents', 'tests', 'examples', 'config',
                'browse', 'package.json', 'pnpm-lock.yaml', 'requirements-test.txt')


def git(root, *args, input=None):
    try:
        return subprocess.run(['git', '-C', str(root), *args], input=input,
                              capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError('Cannot read committed source from Git: ' + str(root)) from exc


def head(root):
    return git(root, 'rev-parse', '--verify', 'HEAD^{commit}').decode().strip()


@contextmanager
def snapshot(root):
    root = Path(root).resolve()
    # Non-Git directories remain supported for explicit library fixtures/exports.
    # A broken repository must never fall back to reading working files.
    if not os.path.lexists(root / '.git'):
        yield root, None
        return
    commit = head(root)
    records = []
    for row in git(root, 'ls-tree', '-rz', commit, '--', *SOURCE_PATHS).split(b'\0'):
        if not row:
            continue
        meta, raw_path = row.split(b'\t', 1)
        mode, kind, oid = meta.split()
        path = Path(os.fsdecode(raw_path))
        if path.is_absolute() or '..' in path.parts or mode not in (b'100644', b'100755') or kind != b'blob':
            raise ValueError('Unsupported committed source (symlink or submodule): ' + str(path))
        records.append((path, mode, oid))
    blobs = io.BytesIO(git(root, 'cat-file', '--batch', input=b''.join(oid + b'\n' for _, _, oid in records)))
    with tempfile.TemporaryDirectory(prefix='estate-source-') as directory:
        source = Path(directory)
        for path, mode, oid in records:
            actual, kind, size = blobs.readline().split()
            if actual != oid or kind != b'blob':
                raise ValueError('Unexpected Git object while exporting source')
            data = blobs.read(int(size))
            if len(data) != int(size) or blobs.read(1) != b'\n':
                raise ValueError('Incomplete Git blob while exporting source')
            target = source / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            target.chmod(0o755 if mode == b'100755' else 0o644)
        yield source, commit


def assert_head(root, commit):
    if commit is not None and head(root) != commit:
        raise ValueError('Committed source changed during operation; rerun from a stable HEAD')


def check_builder(source):
    """Do not attest committed tooling while executing different local assembly code."""
    if not (source / 'tools/estate.py').exists():
        return  # Synthetic library fixtures do not supply an executable toolchain.
    running = Path(__file__).resolve().parent
    for name in ('committed_source', 'estate', 'portable', 'catalog', 'releases', 'plugins', 'plugin_version', 'browse', 'promote_maintenance'):
        expected = source / 'tools' / (name + '.py')
        actual = running / (name + '.py')
        if not expected.is_file() or not actual.is_file() or actual.read_bytes() != expected.read_bytes():
            raise ValueError('Packaging code differs from HEAD; commit or restore tools/' + name + '.py before building')
