#!/usr/bin/env python3
"""Export an explicitly selected private evidence bundle; never discover personal files."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import shutil
import tempfile
from zipfile import ZIP_DEFLATED, ZipFile

SKILL_ROOT = Path(__file__).resolve().parents[1]
CORE = ('SKILL.md', 'scripts/content-review.ts', 'scripts/content-review-cli.ts',
        'scripts/check_role_resume_readiness.py')


def file_hash(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def selected_sources(manifest_path):
    manifest = json.loads(Path(manifest_path).read_text())
    if manifest.get('format') != 1 or not isinstance(manifest.get('files'), list) or not manifest['files']:
        raise ValueError('Supply format 1 with an explicit nonempty files list.')
    if not isinstance(manifest.get('owner'), str) or not manifest['owner'].strip():
        raise ValueError('Identify the owner whose evidence was authorized for this export.')
    rows, names = [], set(CORE) | {'PRIVATE_BUNDLE_NOTICE.md', 'bundle-manifest.json', 'MANIFEST.sha256'}
    for row in manifest['files']:
        source = Path(row['source']).expanduser()
        destination = PurePosixPath(row['destination'])
        if not source.is_absolute() or source.is_symlink() or not source.is_file():
            raise ValueError('Every source must be an explicit absolute regular file.')
        if destination.is_absolute() or '..' in destination.parts or '\\' in str(destination) or not destination.parts:
            raise ValueError('Every destination must remain inside the private bundle.')
        name = str(destination)
        if name in names or any(name.startswith(n + '/') or n.startswith(name + '/') for n in names):
            raise ValueError('Duplicate or conflicting destination: ' + name)
        names.add(name)
        actual = file_hash(source)
        if row.get('sha256') != actual:
            raise ValueError('Explicit source hash missing or stale: ' + str(source))
        rows.append((source, Path(name), actual))
    required = manifest.get('required', [])
    if not isinstance(required, list) or any(name not in names for name in required):
        raise ValueError('A required evidence destination is absent from the explicit files list.')
    return manifest, rows


def verify_bundle(path):
    with ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError('Private bundle failed its integrity check.')
        prefix = 'career-application/'
        contents = {name: archive.read(name) for name in archive.namelist()}
        if len(contents) != len(archive.namelist()):
            raise ValueError('Duplicate archive members.')
        manifest = json.loads(contents[prefix + 'bundle-manifest.json'])
        for row in manifest['files']:
            if sha256(contents[prefix + row['bundle_path']]).hexdigest() != row['sha256']:
                raise ValueError('Private bundle content hash mismatch.')
        for name in CORE:
            if prefix + name not in contents:
                raise ValueError('Missing workflow resource: ' + name)


def distribution_roots(skill_root):
    """Find enclosing source and plugin boundaries without a personal-path default."""
    roots = {skill_root.resolve()}
    for ancestor in skill_root.resolve().parents:
        if ancestor.name == 'skills':
            roots.add(ancestor)
        if ((ancestor / '.claude-plugin').is_dir()
                or ((ancestor / 'config/skill-catalog.json').is_file() and (ancestor / 'skills').is_dir())):
            roots.add(ancestor)
    return roots


def build(manifest_path, destination):
    """Keep evidence separate from the reusable plugin and preserve existing exports."""
    destination = Path(destination).expanduser()
    if not destination.is_absolute() or destination.exists():
        raise ValueError('Choose a new absolute output directory; existing files are preserved.')
    if any(destination.resolve().is_relative_to(root) for root in distribution_roots(SKILL_ROOT)):
        raise ValueError('Private evidence must remain outside every enclosing source skills tree or plugin package.')
    manifest, sources = selected_sources(manifest_path)
    with tempfile.TemporaryDirectory(prefix='career-evidence-') as tmp:
        stage = Path(tmp) / 'career-application'
        stage.mkdir()
        records = []
        for name in CORE:
            source = SKILL_ROOT / name
            target = stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            records.append({'bundle_path': name, 'sha256': file_hash(source), 'kind': 'workflow'})
        for source, relative, expected in sources:
            if file_hash(source) != expected:
                raise ValueError('Evidence changed while preparing export.')
            target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            records.append({'bundle_path': str(relative), 'sha256': expected, 'kind': 'private-evidence'})
        (stage / 'PRIVATE_BUNDLE_NOTICE.md').write_text(
            '# Private evidence bundle\n\nThis explicitly selected snapshot contains private career evidence. '
            'This is a private evidence snapshot, not an independently installable skill. Its workflow copies '
            'require the separately installed career workflow and its declared dependencies. Do not publish or upload '
            'this snapshot to another account without explicit authorization for that destination.\n')
        receipt = {'format': 1, 'owner': manifest['owner'], 'built_at': datetime.now(timezone.utc).isoformat(),
                   'privacy': 'private-personal-career-material', 'files': records}
        (stage / 'bundle-manifest.json').write_text(json.dumps(receipt, indent=2) + '\n')
        (stage / 'MANIFEST.sha256').write_text('\n'.join(
            file_hash(p) + '  ' + str(p.relative_to(stage)) for p in sorted(stage.rglob('*')) if p.is_file()) + '\n')
        bundle = Path(tmp) / 'career-evidence.zip'
        with ZipFile(bundle, 'w', ZIP_DEFLATED) as archive:
            for file in sorted(stage.rglob('*')):
                if file.is_file():
                    archive.write(file, Path('career-application') / file.relative_to(stage))
        verify_bundle(bundle)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.mkdir()
        try:
            shutil.copytree(stage, destination / 'expanded')
            shutil.copy2(bundle, destination / bundle.name)
            verify_bundle(destination / bundle.name)
            digest = file_hash(destination / bundle.name)
            (destination / (bundle.name + '.sha256')).write_text(digest + '  ' + bundle.name + '\n')
        except BaseException:
            # This directory was newly created by this operation; preserve failed bytes for diagnosis.
            (destination / 'INCOMPLETE').write_text('Export failed validation. Do not use this output.\n')
            raise
    return {'directory': str(destination), 'archive_sha256': digest, 'uploaded': False, 'installed': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-map', type=Path, required=True, help='Explicit owner/files/source hashes/required destinations JSON.')
    parser.add_argument('--output', type=Path, required=True, help='New private directory outside the skill.')
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.source_map, args.output), indent=2))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(2, str(exc) + '\n')


if __name__ == '__main__':
    main()
