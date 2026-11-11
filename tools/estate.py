#!/usr/bin/env python3
"""Build portable skills and reconcile explicitly managed local installations."""
import argparse
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from portable import assemble, runtime_closure
from catalog import entries as catalog_entries, dependencies as catalog_dependencies, apply_entrypoint

IGNORED = {'.DS_Store', '__pycache__', '.git', '.local', '.venv', 'node_modules'}


def files(folder):
    result = []
    for parent, dirs, names in os.walk(folder, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in IGNORED)
        for d in dirs:
            if (Path(parent) / d).is_symlink():
                raise ValueError(f'Symlink inside source package: {Path(parent) / d}')
        for name in sorted(names):
            p = Path(parent) / name
            if name in IGNORED or name.endswith('.pyc'):
                continue
            if p.is_symlink():
                raise ValueError(f'Symlink inside source package: {p}')
            result.append(p)
    return sorted(result)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def tree_hash(folder):
    return sha(json.dumps([(str(p.relative_to(folder)), sha(p.read_bytes()), p.stat().st_mode & 0o111)
                          for p in files(folder)], separators=(',', ':')).encode())


def names(root=ROOT):
    return sorted(p.name for p in (root / 'skills').iterdir() if p.is_dir() and (p / 'SKILL.md').is_file())


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.tmp-' + uuid.uuid4().hex)
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    os.replace(tmp, path)


def source_hash(root=ROOT):
    records = []
    for directory in ('skills', 'policies', 'tools', 'agents', 'tests', 'examples', 'config'):
        records += [(str(p.relative_to(root)), sha(p.read_bytes()), p.stat().st_mode & 0o111)
                    for p in files(root / directory)]
    return sha(json.dumps(records, separators=(',', ':')).encode())


def runtime_dependencies(name, root=ROOT):
    return runtime_closure(root, name)


def validate(root=ROOT):
    errors = []
    skill_names = names(root)
    public = catalog_entries(root)
    if not skill_names:
        errors.append('No skills found')
    for name in skill_names:
        runtime_dependencies(name, root)
        folder = root / 'skills' / name
        text = (folder / 'SKILL.md').read_text()
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) or len(name) > 64:
            errors.append(f'{name}: invalid directory name')
        match = re.match(r'\A---\n(.*?)\n---(?:\n|$)', text, re.S)
        if not match:
            errors.append(f'{name}: missing frontmatter')
            continue
        front = match.group(1)
        declared = re.search(r'^name:\s*[\'\"]?([^\n\'\"]+)', front, re.M)
        if not declared or declared.group(1).strip() != name:
            errors.append(f'{name}: frontmatter name differs from directory')
        if not re.search(r'^description:\s*\S', front, re.M):
            errors.append(f'{name}: missing description')
        for p in files(folder):
            if p.suffix in {'.md', '.py', '.json', '.yaml', '.yml', '.sh', '.txt'}:
                body = p.read_text()
                if re.search(r'(?i)(?:gh[pousr]_[A-Za-z0-9]{24,}|github_pat_[A-Za-z0-9_]{30,}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----)', body):
                    errors.append(f'{p.relative_to(root)}: possible credential')
            if p.suffix == '.md':
                for target in re.findall(r'\]\(([^\s)]+)(?:\s+[^)]*)?\)', p.read_text()):
                    if target.startswith(('https:', 'http:', '/', '#', 'mailto:', 'app:', 'codex:')):
                        continue
                    target = target.split('#')[0]
                    if target and (p.parent / target).resolve().parent == (folder / 'references/estate').resolve():
                        if not (root / 'policies' / Path(target).name).is_file():
                            errors.append(f'{name}: missing policy {target}')
                    elif target and not (p.parent / target).exists():
                        errors.append(f'{p.relative_to(root)}: missing reference {target}')
    for p in files(root / 'policies'):
        if p.suffix != '.md':
            errors.append(f'Unexpected policy type: {p.name}')
    if errors:
        raise ValueError('\n'.join(errors))
    return {'skills': len(public), 'source_modules': len(skill_names), 'source_sha256': source_hash(root)}


@contextlib.contextmanager
def lock(root=ROOT):
    local = root / '.local'
    local.mkdir(exist_ok=True)
    with (local / 'estate.lock').open('w') as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('Another estate operation is running')
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def build(root=ROOT):
    result = validate(root)
    # Keep unchanged packages in place, especially on mounted volumes. Verify
    # their bytes before accepting the existing build; repair damaged builds.
    try:
        return current_build(root)
    except ValueError:
        pass
    stage = Path(tempfile.mkdtemp(prefix='.estate-build-', dir=root / '.local'))
    package_dir = stage / 'skills'
    package_dir.mkdir()
    entries = {}
    try:
        for name, item in catalog_entries(root).items():
            target = package_dir / name
            source = item['source']
            dependencies = catalog_dependencies(root, item, runtime_closure)
            mapping = assemble(root, source, target, dependencies)
            apply_entrypoint(target, name, item)
            entries[name] = {'sha256': tree_hash(target), 'runtime_dependencies': dependencies,
                             'source_files': len(mapping), 'source_module': source,
                             'pack': item['pack'], 'modes': item.get('modes', {})}
        if source_hash(root) != result['source_sha256']:
            raise ValueError('Sources changed during the build; rerun from a stable source tree')
        manifest = {**result, 'packages': entries, 'format': 2}
        write_json(stage / 'manifest.json', manifest)
        destination = root / 'build'
        previous = root / '.local' / ('previous-build-' + uuid.uuid4().hex)
        if destination.exists():
            destination.rename(previous)
        try:
            stage.rename(destination)
        except BaseException:
            if previous.exists():
                previous.rename(destination)
            raise
        if previous.exists():
            shutil.rmtree(previous)
        return manifest
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def current_build(root=ROOT):
    path = root / 'build' / 'manifest.json'
    if not path.exists():
        raise ValueError('No build. Run build first.')
    manifest = json.loads(path.read_text())
    if manifest['source_sha256'] != source_hash(root):
        raise ValueError('Build is stale. Run build before installing or packaging.')
    for name, entry in manifest['packages'].items():
        folder = root / 'build' / 'skills' / name
        if not folder.is_dir() or tree_hash(folder) != entry['sha256']:
            raise ValueError(f'Generated package modified or missing: {name}; rebuild from source')
    return manifest


def local_targets(home):
    return {'claude-code': home / '.claude' / 'skills', 'codex': home / '.agents' / 'skills'}


def install(root=ROOT, home=None, adopt=False):
    home = (home or Path.home()).expanduser().absolute()
    manifest = current_build(root)
    operations = []
    conflicts = []
    targets = [(target, list(manifest['packages'])) for target in local_targets(home).values()]
    legacy = home / '.codex' / 'skills'
    targets.append((legacy, [name for name in manifest['packages'] if os.path.lexists(legacy / name)]))
    for target, selected in targets:
        if target.is_symlink():
            raise ValueError(f'Refusing a symlinked install root: {target}')
        for name in selected:
            dest = target / name
            source = root / 'build' / 'skills' / name
            if dest.is_symlink() and dest.resolve() == source.resolve():
                continue
            if os.path.lexists(dest) and not adopt:
                conflicts.append(str(dest))
            else:
                operations.append((dest, source))
    pointer = home / '.config' / 'skills-estate' / 'repository'
    if not (pointer.is_symlink() and pointer.resolve() == root.resolve()):
        if os.path.lexists(pointer) and not adopt:
            conflicts.append(str(pointer))
        else:
            operations.append((pointer, root))
    if conflicts:
        raise ValueError('Existing skills preserved. Review before adopt:\n' + '\n'.join(conflicts))
    backup = home / '.local' / 'state' / 'skills-estate' / ('backup-' + dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8])
    journal = []
    try:
        for dest, source in operations:
            dest.parent.mkdir(parents=True, exist_ok=True)
            saved = None
            if os.path.lexists(dest):
                saved = backup / dest.relative_to(home)
                saved.parent.mkdir(parents=True, exist_ok=True)
                dest.rename(saved)
            # Journal before linking so a link failure can restore the original.
            journal.append({'destination': str(dest), 'backup': str(saved) if saved else None, 'source': str(source)})
            dest.symlink_to(source, target_is_directory=True)
        receipt = {'source_sha256': manifest['source_sha256'], 'home': str(home), 'operations': journal}
        if journal:
            write_json(backup / 'receipt.json', receipt)
        write_json(root / '.local' / 'install-receipt.json', receipt)
        return {'links_changed': len(journal), 'backup': str(backup) if journal else None}
    except BaseException:
        for op in reversed(journal):
            dest = Path(op['destination'])
            if dest.is_symlink() and dest.resolve() == Path(op['source']).resolve():
                dest.unlink()
            if op['backup'] and os.path.lexists(op['backup']):
                Path(op['backup']).rename(dest)
        raise


def restore(receipt_path):
    receipt = json.loads(receipt_path.read_text())
    operations = receipt['operations']
    for op in operations:
        dest = Path(op['destination'])
        if not dest.is_symlink() or dest.resolve() != Path(op['source']).resolve():
            raise ValueError(f'Changed since installation; refusing restore: {dest}')
        if op['backup'] and not os.path.lexists(op['backup']):
            raise ValueError(f'Missing backup: {op["backup"]}')
    for op in reversed(operations):
        dest = Path(op['destination'])
        dest.unlink()
        if op['backup']:
            Path(op['backup']).rename(dest)
    return {'restored': len(operations)}


def bundle(root=ROOT):
    manifest = current_build(root)
    stage = Path(tempfile.mkdtemp(prefix='.estate-dist-', dir=root / '.local'))
    entries = {}
    try:
        for name, entry in manifest['packages'].items():
            package = root / 'build' / 'skills' / name
            path = stage / (name + '.zip')
            with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
                for p in files(package):
                    info = zipfile.ZipInfo(str(Path(name) / p.relative_to(package)), date_time=(2020, 1, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = ((0o100755 if p.stat().st_mode & 0o111 else 0o100644) << 16)
                    z.writestr(info, p.read_bytes())
            entries[name] = {'file': path.name, 'sha256': sha(path.read_bytes()), 'content_sha256': entry['sha256']}
        release = {'format': 1, 'source_sha256': manifest['source_sha256'], 'packages': entries}
        write_json(stage / 'release.json', release)
        destination = root / 'dist'
        previous = root / '.local' / ('previous-dist-' + uuid.uuid4().hex)
        if destination.exists():
            destination.rename(previous)
        try:
            stage.rename(destination)
        except BaseException:
            if previous.exists():
                previous.rename(destination)
            raise
        if previous.exists():
            shutil.rmtree(previous)
        return release
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def status(root=ROOT, home=None):
    home = (home or Path.home()).expanduser().absolute()
    try:
        manifest = current_build(root)
        build_state = 'current'
    except ValueError as e:
        return {'build': str(e), 'ok': False}
    surfaces = {}
    inspection_errors = {}
    ok = True
    for surface, target in local_targets(home).items():
        rows = {}
        for name, entry in manifest['packages'].items():
            dest = target / name
            if not dest.is_dir():
                state = 'broken-link' if dest.is_symlink() else 'missing'
            else:
                try:
                    same = tree_hash(dest.resolve()) == entry['sha256']
                except (ValueError, OSError) as exc:
                    inspection_errors[str(dest)] = str(exc)
                    same = False
                linked = dest.is_symlink() and dest.resolve() == (root / 'build' / 'skills' / name).resolve()
                state = 'linked-current' if same and linked else ('copy-current' if same else 'drift')
            rows[name] = state
            ok &= state == 'linked-current'
        surfaces[surface] = rows
    # Account downloads and vendor plugins have a separate lifecycle. Inventory
    # duplicate entrypoint names without mutating those roots.
    external = []
    for base in [home / '.codex' / 'skills', home / '.agents' / 'skills' / 'synced', home / '.claude' / 'skills' / 'synced']:
        if not base.exists():
            continue
        for parent, dirs, fs in os.walk(base, followlinks=False):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            if 'SKILL.md' in fs:
                external.append({'path': str(Path(parent)), 'name': Path(parent).name})
        for p in base.iterdir():
            if p.is_symlink() and (p / 'SKILL.md').exists():
                external.append({'path': str(p), 'name': p.name})
    ledger_path = root / '.local' / 'cloud-publications.json'
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {}
    release_path = root / 'dist' / 'release.json'
    release = json.loads(release_path.read_text()) if release_path.exists() else None
    cloud = {}
    for surface in ['claude-account', 'codex-account']:
        rows = {}
        for name in manifest['packages']:
            recorded = ledger.get(surface, {}).get(name)
            desired = release['packages'].get(name, {}).get('sha256') if release else None
            fresh = release and release['source_sha256'] == manifest['source_sha256']
            rows[name] = 'reported-current' if fresh and recorded and recorded['sha256'] == desired else 'pending'
        cloud[surface] = {'packages': rows, 'verified_live': False}
    legacy_rows = {}
    for name, entry in manifest['packages'].items():
        dest = home / '.codex' / 'skills' / name
        if os.path.lexists(dest):
            try:
                same = dest.is_dir() and tree_hash(dest.resolve()) == entry['sha256']
            except (ValueError, OSError) as exc:
                inspection_errors[str(dest)] = str(exc)
                same = False
            legacy_rows[name] = 'current' if same else 'drift'
            ok &= same
    return {'build': build_state, 'source_sha256': manifest['source_sha256'], 'local': surfaces, 'legacy_codex_aliases': legacy_rows, 'external_skill_locations': external, 'inspection_errors': inspection_errors, 'cloud': cloud, 'ok': ok}


def record_publication(root, surface, skill, reference):
    current_build(root)
    release = json.loads((root / 'dist' / 'release.json').read_text())
    if release['source_sha256'] != source_hash(root):
        raise ValueError('Bundles are stale; rebuild and upload the new version')
    if skill not in release['packages']:
        raise ValueError(f'Unknown package: {skill}')
    package = release['packages'][skill]
    if sha((root / 'dist' / package['file']).read_bytes()) != package['sha256']:
        raise ValueError('Bundle changed since release manifest')
    path = root / '.local' / 'cloud-publications.json'
    ledger = json.loads(path.read_text()) if path.exists() else {}
    ledger.setdefault(surface, {})[skill] = {'sha256': package['sha256'], 'reference': reference, 'reported_at': dt.datetime.now(dt.timezone.utc).isoformat(), 'verified_live': False}
    write_json(path, ledger)
    return {'surface': surface, 'skill': skill, 'state': 'reported', 'verified_live': False}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--home', type=Path, default=Path.home(), help='Local install root; use a temporary home for tests')
    sub = ap.add_subparsers(dest='command', required=True)
    for command in ['validate', 'build', 'bundle', 'install', 'adopt', 'sync', 'status']:
        sub.add_parser(command)
    rp = sub.add_parser('restore')
    rp.add_argument('receipt', type=Path)
    pub = sub.add_parser('record-publication')
    pub.add_argument('--surface', choices=['claude-account', 'codex-account'], required=True)
    pub.add_argument('--skill', required=True)
    pub.add_argument('--reference', required=True, help='Account and upload record; a report, not independent verification')
    args = ap.parse_args()
    try:
        with lock():
            if args.command == 'validate': result = validate()
            elif args.command == 'build': result = build()
            elif args.command == 'bundle': result = bundle()
            elif args.command in {'install', 'adopt'}: result = install(home=args.home, adopt=args.command == 'adopt')
            elif args.command == 'restore': result = restore(args.receipt)
            elif args.command == 'status': result = status(home=args.home)
            elif args.command == 'record-publication': result = record_publication(ROOT, args.surface, args.skill, args.reference)
            elif args.command == 'sync':
                build(); bundle(); install(home=args.home)
                result = status(home=args.home)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1 if args.command in {'status', 'sync'} and not result['ok'] else 0
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as e:
        print(str(e), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
