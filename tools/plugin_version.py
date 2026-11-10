"""Bind the existing functional plugin version to its release inputs."""
import argparse
import hashlib
import json
from pathlib import Path

HISTORY = 'config/plugin-version-history.json'


def fingerprint(root):
    root = Path(root)
    records = []
    for folder in ('skills', 'policies', 'agents', 'tools', 'config'):
        for path in sorted((root / folder).rglob('*')):
            if not path.is_file() or any(p in {'__pycache__', '.local', 'node_modules'} for p in path.relative_to(root).parts):
                continue
            relative = path.relative_to(root).as_posix()
            if relative in {HISTORY, 'config/skills-publication.json'} or path.name in {'.DS_Store'} or path.name.startswith('.smbdelete'):
                continue
            if path.is_symlink():
                raise ValueError('Release input cannot be a symlink: ' + relative)
            data = path.read_bytes()
            if relative == 'config/plugin-bundles.json':
                settings = json.loads(data)
                data = json.dumps({k: v for k, v in settings.items() if k not in {'version', 'release'}}, sort_keys=True).encode()
            records.append((relative, hashlib.sha256(data).hexdigest(), bool(path.stat().st_mode & 0o111)))
    for name in ('package.json', 'pnpm-lock.yaml', 'requirements-test.txt'):
        path = root / name
        if path.exists():
            records.append((name, hashlib.sha256(path.read_bytes()).hexdigest(), False))
    return hashlib.sha256(json.dumps(records, sort_keys=True).encode()).hexdigest()


def check(root, settings):
    if not settings.get('version_policy'):
        return  # Historical/synthetic fixtures predate version binding.
    path = Path(root) / HISTORY
    if not path.exists():
        raise ValueError('Plugin version has no content record; record a new version before packaging.')
    records = json.loads(path.read_text())['versions']
    row = records.get(settings['version'])
    if not row or row['content_sha256'] != fingerprint(root):
        raise ValueError('Plugin content changed without a matching version record; bump and record the version.')


def record(root, note):
    root = Path(root)
    settings = json.loads((root / 'config/plugin-bundles.json').read_text())
    version = settings['version']
    parts = version.split('.')
    if len(parts) != 3 or any(not p.isdigit() for p in parts):
        raise ValueError('Version must be major.minor.patch')
    if not note.strip():
        raise ValueError('A release change note is required')
    digest = fingerprint(root)
    path = root / HISTORY
    history = json.loads(path.read_text()) if path.exists() else {'format': 1, 'versions': {}}
    prior = history['versions']
    if version in prior:
        if prior[version]['content_sha256'] != digest:
            raise ValueError('This version already identifies different content; choose a higher version.')
        return prior[version]
    if prior and tuple(map(int, parts)) <= max(tuple(map(int, v.split('.'))) for v in prior):
        raise ValueError('New plugin versions must increase')
    prior[version] = {'content_sha256': digest, 'note': note.strip()}
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(history, indent=2) + '\n')
    temporary.replace(path)
    return prior[version]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--record', metavar='CHANGE_NOTE')
    args = parser.parse_args()
    if args.record:
        print(json.dumps(record(args.root, args.record), indent=2))
    else:
        check(args.root, json.loads((args.root / 'config/plugin-bundles.json').read_text()))
        print('Plugin version matches its release inputs.')
