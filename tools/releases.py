"""Content-addressed local installations, separate from mutable build output.

Snapshots are read-only and verified on every activation. This is accidental
write protection, not a security boundary against the filesystem owner.
"""
from contextlib import contextmanager
from pathlib import Path
import datetime as dt
import fcntl
import hashlib
import json
import os
import re
import shutil
import tempfile
import uuid


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def store(home):
    return Path(home) / '.local/share/skills-estate/releases'


def state(home):
    return Path(home) / '.local/state/skills-estate'


def safe_parents(path):
    for p in [path, *path.parents]:
        if p.is_symlink():
            raise ValueError(f'Refusing symlinked managed directory: {p}')


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.tmp-' + uuid.uuid4().hex)
    try:
        temp.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


@contextmanager
def home_lock(home):
    directory = state(home)
    safe_parents(directory)
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / 'install.lock').open('a') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('Another installation is running for this home')
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def load(home, release_id, tree_hash):
    if not re.fullmatch('[a-f0-9]{64}', release_id):
        raise ValueError('Invalid release ID')
    folder = store(home) / release_id
    safe_parents(folder)
    metadata = folder / 'release.json'
    if metadata.is_symlink():
        raise ValueError('Linked release metadata')
    record = json.loads(metadata.read_text())
    if digest(record) != release_id:
        raise ValueError('Release metadata differs from its ID')
    if set(p.name for p in (folder / 'skills').iterdir()) != set(record['packages']):
        raise ValueError('Release inventory changed')
    for name, entry in record['packages'].items():
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name):
            raise ValueError('Invalid package name')
        package = folder / 'skills' / name
        if package.is_symlink() or not package.is_dir() or tree_hash(package) != entry['sha256']:
            raise ValueError(f'Installed release modified: {name}')
    return folder, record


def snapshot(root, home, packages, source_hash, kind, tree_hash):
    record = {'format': 1, 'kind': kind, 'repository': str(Path(root).resolve()),
              'source_sha256': source_hash, 'packages': {}}
    for name, folder in sorted(packages.items()):
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) or folder.is_symlink():
            raise ValueError('Invalid package source')
        record['packages'][name] = {'sha256': tree_hash(folder)}
    release_id = digest(record)
    base = store(home)
    safe_parents(base)
    base.mkdir(parents=True, exist_ok=True)
    target = base / release_id
    if target.exists():
        load(home, release_id, tree_hash)
        return release_id
    temp = Path(tempfile.mkdtemp(prefix='.stage-', dir=base))
    try:
        (temp / 'skills').mkdir()
        for name, source in packages.items():
            destination = temp / 'skills' / name
            shutil.copytree(source, destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store", ".git", ".local", ".venv", "node_modules"))
            if tree_hash(destination) != record['packages'][name]['sha256'] or tree_hash(source) != record['packages'][name]['sha256']:
                raise ValueError('Package changed during snapshot')
        (temp / 'release.json').write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
        for p in temp.rglob('*'):
            if p.is_file():
                p.chmod(p.stat().st_mode & 0o555)
        # Keep directories writable for explicit restoration/retention tools;
        # package files are read-only and integrity is checked before use.
        temp.rename(target)
        try:
            load(home, release_id, tree_hash)
        except BaseException:
            shutil.rmtree(target)
            raise
        return release_id
    finally:
        if temp.exists():
            shutil.rmtree(temp)


def managed_link(path, home, root, tree_hash, verified=None):
    if not path.is_symlink():
        return False
    resolved = path.resolve()
    legacy = Path(root).resolve() / 'build/skills' / path.name
    if resolved.parent == legacy.parent:
        return True
    try:
        relative = resolved.relative_to(store(home))
    except ValueError:
        return False
    if len(relative.parts) != 3 or relative.parts[1] != 'skills':
        return False
    verified = {} if verified is None else verified
    if relative.parts[0] not in verified:
        verified[relative.parts[0]] = load(home, relative.parts[0], tree_hash)[1]
    record = verified[relative.parts[0]]
    return record['repository'] == str(Path(root).resolve())


def linked_inventory(home, repository, links, tree_hash):
    """Verify every immutable version referenced by an activation's exact links."""
    home, root = Path(home).absolute(), Path(repository).resolve()
    pointer = home / '.config/skills-estate/repository'
    allowed = {home / name for name in ['.claude/skills', '.agents/skills', '.codex/skills']}
    versions, packages = {}, {}
    for destination, target in links.items():
        dest, source = Path(destination), Path(target)
        if dest == pointer:
            if source != root:
                raise ValueError('Repository pointer differs from activation')
            continue
        if dest.parent not in allowed or dest.name in ('', '.', '..'):
            raise ValueError('Destination outside managed skill directories')
        relative = source.relative_to(store(home))
        if len(relative.parts) != 3 or relative.parts[1] != 'skills':
            raise ValueError('Activation target is outside an immutable package')
        version, _, name = relative.parts
        if version not in versions:
            versions[version] = load(home, version, tree_hash)[1]
        record = versions[version]
        if record['repository'] != str(root) or name not in record['packages']:
            raise ValueError('Activation target belongs to another repository or package')
        entry = record['packages'][name]
        if name in packages and packages[name] != entry:
            raise ValueError('Managed hosts disagree on package version: ' + name)
        packages[name] = entry
    return versions, packages


def activate(root, home, release_id, tree_hash, adopt=False, destinations=None, preserve_existing=False, links=None,
             account_provided=()):
    root, home = Path(root).resolve(), Path(home).absolute()
    folder, record = load(home, release_id, tree_hash)
    if record['repository'] != str(root):
        raise ValueError('Release belongs to another repository')
    active_file = state(home) / 'active.json'
    previous = json.loads(active_file.read_text()) if active_file.exists() else None
    if previous and previous['repository'] != str(root):
        raise ValueError('This home already has another managed repository')
    if preserve_existing and previous and not inspect(home, tree_hash)['ok']:
        raise ValueError('Current installation drift must be resolved before targeted promotion')
    desired = dict(previous['links']) if preserve_existing and previous else {}
    if links is not None:
        desired = dict(links)
    elif destinations is None:
        for name in record['packages']:
            for parent in ['.claude/skills', '.agents/skills']:
                desired[str(home / parent / name)] = str(folder / 'skills' / name)
            legacy = home / '.codex/skills' / name
            if os.path.lexists(legacy):
                desired[str(legacy)] = str(folder / 'skills' / name)
    else:
        for dest, name in destinations.items():
            if name not in record['packages']:
                raise ValueError('Destination package absent from release')
            desired[str(dest)] = str(folder / 'skills' / name)
    if preserve_existing:
        # Keep owned aliases for selected packages aligned with their native-host entries.
        for destination, target in (previous or {}).get('links', {}).items():
            if Path(target).name in record['packages']:
                desired[destination] = str(folder / 'skills' / Path(target).name)
    # Claude Code already reads these from the Claude account; a local link would list them twice.
    for name in account_provided:
        desired.pop(str(home / '.claude/skills' / name), None)
    pointer = home / '.config/skills-estate/repository'
    desired[str(pointer)] = str(root)
    versions, _ = linked_inventory(home, root, desired, tree_hash)
    operations = []
    verified_releases = {}
    for name, target in desired.items():
        dest = Path(name)
        if dest.parent not in [home / '.claude/skills', home / '.agents/skills', home / '.codex/skills', pointer.parent]:
            raise ValueError('Destination outside managed skill directories')
        safe_parents(dest.parent)
        if dest.is_symlink() and dest.resolve() == Path(target).resolve():
            continue
        if os.path.lexists(dest) and not adopt:
            if dest == pointer or not managed_link(dest, home, root, tree_hash, verified_releases):
                raise ValueError(f'Existing skills preserved. Review before adopt: {dest}')
        operations.append((dest, target))
    for name, target in (previous or {}).get('links', {}).items():
        if name in desired:
            continue
        dest = Path(name)
        if not os.path.lexists(dest):
            continue
        if not dest.is_symlink() or dest.resolve() != Path(target).resolve():
            raise ValueError(f'Changed retired destination: {dest}')
        operations.append((dest, None))
    if not operations and previous and previous['release_id'] == release_id and previous['links'] == desired:
        return {'release_id': release_id, 'links_changed': 0, 'backup': None}
    backup = state(home) / ('backup-' + dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8])
    journal = []
    active_written = False
    plan = [{'destination': str(dest), 'source': target,
             'backup': str(backup / dest.relative_to(home)) if os.path.lexists(dest) else None}
            for dest, target in operations]
    write_json(backup / 'pending.json', {'home': str(home), 'operations': plan, 'previous_active': previous})
    try:
        for dest, target in operations:
            dest.parent.mkdir(parents=True, exist_ok=True)
            saved = None
            if os.path.lexists(dest):
                saved = backup / dest.relative_to(home)
                saved.parent.mkdir(parents=True, exist_ok=True)
                dest.rename(saved)
            journal.append({'destination': str(dest), 'backup': str(saved) if saved else None, 'source': target})
            if target:
                dest.symlink_to(target, target_is_directory=True)
        current = {'format': 2 if len(versions) > 1 else 1, 'release_id': release_id, 'repository': str(root), 'links': desired}
        receipt = {'format': 2, 'phase': 'committed', 'home': str(home), 'operations': journal, 'previous_active': previous, 'active': current}
        write_json(active_file, current)
        active_written = True
        write_json(backup / 'receipt.json', receipt)
        (backup / 'pending.json').unlink()
        return {'release_id': release_id, 'links_changed': len(journal), 'backup': str(backup)}
    except BaseException:
        for op in reversed(journal):
            dest = Path(op['destination'])
            if dest.is_symlink() and op['source'] and dest.resolve() == Path(op['source']).resolve():
                dest.unlink()
            if op['backup'] and os.path.lexists(op['backup']):
                Path(op['backup']).rename(dest)
        if active_written:
            if previous:
                write_json(active_file, previous)
            else:
                active_file.unlink(missing_ok=True)
        if (backup / 'receipt.json').exists():
            (backup / 'receipt.json').rename(backup / 'failed-receipt.json')
        (backup / 'pending.json').rename(backup / 'failed-plan.json')
        raise


def inspect(home, tree_hash):
    active_file = state(home) / 'active.json'
    if not active_file.exists():
        return {'state': 'legacy-or-unmanaged', 'ok': False}
    try:
        active = json.loads(active_file.read_text())
        _, record = load(home, active['release_id'], tree_hash)
        if record['repository'] != active['repository']:
            raise ValueError('Active release belongs to another repository')
        versions, packages = linked_inventory(home, active['repository'], active['links'], tree_hash)
        changed = [name for name, target in active['links'].items()
                   if not Path(name).is_symlink() or Path(name).resolve() != Path(target).resolve()]
        return {'state': 'modified-links' if changed else 'pinned', 'ok': not changed,
                'release_id': active['release_id'], 'source_sha256': record['source_sha256'] if len(versions) <= 1 else None,
                'kind': record['kind'] if len(versions) <= 1 else 'mixed-pinned',
                'release_ids': sorted(versions), 'changed_links': changed, 'packages': packages}
    except (OSError, ValueError, KeyError) as exc:
        return {'state': 'damaged', 'ok': False, 'error': str(exc)}
