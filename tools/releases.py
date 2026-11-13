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
import stat
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


def snapshot(root, home, packages, source_hash, kind, tree_hash, provenance=None):
    record = {'format': 1, 'kind': kind, 'repository': str(Path(root).resolve()),
              'source_sha256': source_hash, 'packages': {}}
    if provenance is not None:
        record['provenance'] = provenance
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


def path_state(path):
    """Fingerprint one destination without following links or omitting user files."""
    path = Path(path)
    if not os.path.lexists(path):
        return None
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode):
        return {'kind': 'symlink', 'target': os.readlink(path)}
    if stat.S_ISREG(info.st_mode):
        value = {'kind': 'file', 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                 'mode': stat.S_IMODE(info.st_mode)}
    elif stat.S_ISDIR(info.st_mode):
        value = {'kind': 'directory', 'sha256': digest([
            (child.name, path_state(child)) for child in sorted(path.iterdir())]),
                 'mode': stat.S_IMODE(info.st_mode)}
    else:
        raise ValueError('Unsupported installation destination: ' + str(path))
    after = path.lstat()
    if (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_mode) != (
            after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_mode):
        raise ValueError('Destination changed while inspecting: ' + str(path))
    return value


def require_state(path, expected):
    safe_parents(Path(path).parent)
    if path_state(path) != expected:
        raise ValueError('Installation path changed during transaction: ' + str(path))


def require_no_pending(home):
    pending = sorted(state(home).glob('backup-*/pending.json'))
    if pending:
        raise ValueError('Unfinished installation transaction requires recovery: ' + str(pending[0]))


def activate(root, home, release_id, tree_hash, adopt=False, destinations=None, preserve_existing=False, links=None,
             account_provided=(), policy_root=None, remove_paths=(), relocate_from=None):
    """Activate under the caller's home lock; retain a journal if recovery is uncertain."""
    root, home = Path(root).resolve(), Path(home).absolute()
    policy_root = Path(policy_root or root).resolve()
    require_no_pending(home)
    folder, record = load(home, release_id, tree_hash)
    if record['repository'] != str(root):
        raise ValueError('Release belongs to another repository')
    active_file = state(home) / 'active.json'
    active_before = path_state(active_file)
    if active_before and active_before['kind'] != 'file':
        raise ValueError('Active installation record must be a regular file')
    previous = json.loads(active_file.read_text()) if active_before else None
    require_state(active_file, active_before)
    if previous and previous['repository'] != str(root) and previous['repository'] != relocate_from:
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
        for destination, target in (previous or {}).get('links', {}).items():
            if Path(target).name in record['packages']:
                desired[destination] = str(folder / 'skills' / Path(target).name)
    for name in account_provided:
        desired.pop(str(home / '.claude/skills' / name), None)
    from catalog import check_public_names, entries as catalog_entries
    removals = {Path(path) for path in remove_paths}
    public = catalog_entries(policy_root) if removals else {}
    for dest in removals:
        if (dest.parent != home / '.claude/skills' or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', dest.name)
                or dest.name not in record['packages'] or dest.name not in public):
            raise ValueError('Removal must name a public Claude skill in this release: ' + str(dest))
        safe_parents(dest.parent)
        desired.pop(str(dest), None)
    pointer = home / '.config/skills-estate/repository'
    desired[str(pointer)] = str(root)
    check_public_names(policy_root, [Path(dest).name for dest in desired if Path(dest) != pointer])
    check_public_names(policy_root, [Path(target).name for dest, target in desired.items() if Path(dest) != pointer])
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
            moved = relocate_from is not None and (
                (dest == pointer and dest.is_symlink() and os.readlink(dest) in (relocate_from, str(root)))
                or (dest != pointer and managed_link(dest, home, relocate_from, tree_hash, verified_releases)))
            if not moved and (dest == pointer or not managed_link(dest, home, root, tree_hash, verified_releases)):
                raise ValueError(f'Existing skills preserved. Review before adopt: {dest}')
        operations.append((dest, target))
    for name, target in (previous or {}).get('links', {}).items():
        if name in desired:
            continue
        dest = Path(name)
        safe_parents(dest.parent)
        if not os.path.lexists(dest):
            continue
        if dest not in removals and (not dest.is_symlink() or dest.resolve() != Path(target).resolve()):
            raise ValueError(f'Changed retired destination: {dest}')
        operations.append((dest, None))
    planned = {dest for dest, _ in operations}
    for dest in sorted(removals - planned):
        if os.path.lexists(dest):
            operations.append((dest, None))
    require_state(active_file, active_before)
    if not operations and previous and previous['release_id'] == release_id and previous['links'] == desired:
        return {'release_id': release_id, 'links_changed': 0, 'backup': None}
    backup = state(home) / ('backup-' + dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8])
    plan = []
    for dest, target in operations:
        before = path_state(dest)
        plan.append({'destination': str(dest), 'source': target,
                     'backup': str(backup / dest.relative_to(home)) if before is not None else None,
                     'before': before, 'backup_state': before,
                     'after': {'kind': 'symlink', 'target': target} if target else None})
    pending = backup / 'pending.json'
    current = {'format': 2 if len(versions) > 1 else 1, 'release_id': release_id, 'repository': str(root), 'links': desired}
    pending_record = {'home': str(home), 'operations': plan, 'previous_active': previous,
                      'active_before': active_before, 'active': current, 'phase': 'prepared'}
    write_json(pending, pending_record)
    journal = []
    active_written = False
    active_after = None
    try:
        require_state(active_file, active_before)
        for op in plan:
            dest = Path(op['destination'])
            require_state(dest, op['before'])
            dest.parent.mkdir(parents=True, exist_ok=True)
            journal.append(op)
            if op['backup']:
                saved = Path(op['backup'])
                saved.parent.mkdir(parents=True, exist_ok=True)
                require_state(saved, None)
                require_state(dest, op['before'])
                dest.rename(saved)
                require_state(saved, op['backup_state'])
            require_state(dest, None)
            if op['source']:
                dest.symlink_to(op['source'], target_is_directory=True)
            require_state(dest, op['after'])
        # Check the complete result, including retained links and backed-up originals.
        for destination, target in desired.items():
            dest = Path(destination)
            if not dest.is_symlink() or dest.resolve() != Path(target).resolve():
                raise ValueError('Installation changed before commit: ' + destination)
        for op in plan:
            require_state(Path(op['destination']), op['after'])
            if op['backup']:
                require_state(Path(op['backup']), op['backup_state'])
        linked_inventory(home, root, desired, tree_hash)
        require_state(active_file, active_before)
        receipt = {'format': 2, 'phase': 'committed', 'home': str(home), 'operations': journal,
                   'previous_active': previous, 'active': current}
        write_json(active_file, current)
        active_written = True
        active_after = path_state(active_file)
        if json.loads(active_file.read_text()) != current:
            raise ValueError('Active installation changed before receipt')
        write_json(backup / 'receipt.json', receipt)
        require_state(active_file, active_after)
        pending.unlink()
        return {'release_id': release_id, 'links_changed': len(journal), 'backup': str(backup)}
    except BaseException as original:
        # Never overwrite another writer's destination or active record during recovery.
        uncertain = []
        if active_written:
            try:
                if active_after is None or json.loads(active_file.read_text()) != current:
                    raise ValueError('Active record changed after transaction write')
                require_state(active_file, active_after)
            except (OSError, ValueError) as exc:
                uncertain.append(str(exc))
        else:
            try:
                require_state(active_file, active_before)
            except (OSError, ValueError) as exc:
                uncertain.append(str(exc))
        if not uncertain:
            for op in reversed(journal):
                dest = Path(op['destination'])
                try:
                    observed = path_state(dest)
                    saved = Path(op['backup']) if op['backup'] else None
                    if saved and not os.path.lexists(saved):
                        # The original rename failed before it changed the destination.
                        require_state(dest, op['before'])
                        continue
                    if saved:
                        require_state(saved, op['backup_state'])
                    if observed not in (None, op['after']):
                        raise ValueError('Later destination edit preserved: ' + str(dest))
                    require_state(dest, observed)
                    if observed is not None:
                        dest.unlink()
                    if saved:
                        require_state(dest, None)
                        saved.rename(dest)
                        require_state(dest, op['before'])
                except (OSError, ValueError) as exc:
                    uncertain.append(str(exc))
            if not uncertain and active_written:
                try:
                    require_state(active_file, active_after)
                    if previous:
                        write_json(active_file, previous)
                    else:
                        active_file.unlink()
                except (OSError, ValueError) as exc:
                    uncertain.append(str(exc))
        if uncertain:
            pending_record.update(phase='recovery-required', errors=uncertain)
            write_json(pending, pending_record)
            raise ValueError('Installation recovery incomplete; preserve ' + str(pending) + ': ' + '; '.join(uncertain)) from original
        if (backup / 'receipt.json').exists():
            (backup / 'receipt.json').rename(backup / 'failed-receipt.json')
        pending.rename(backup / 'failed-plan.json')
        raise


def relocate(home, root, previous_repository, tree_hash):
    """Move an installation to a new checkout of the same estate, under the caller's home lock.

    Release IDs include the repository path, so each referenced release is copied
    into a new release for the new checkout, byte for byte, and activated with the
    same links. The old releases stay in the store, and the activation receipt
    can restore the previous links.
    """
    home, root = Path(home).absolute(), Path(root).resolve(strict=True)
    require_no_pending(home)
    active_file = state(home) / 'active.json'
    if not active_file.exists():
        raise ValueError('No managed installation to relocate; use install')
    active = json.loads(active_file.read_text())
    old = active['repository']
    if previous_repository != old:
        raise ValueError('The installation belongs to ' + old + '; pass that path with --from')
    if old == str(root):
        return {'release_id': active['release_id'], 'repository': old, 'links_changed': 0, 'backup': None}
    pointer = home / '.config/skills-estate/repository'
    for destination, target in active['links'].items():
        dest = Path(destination)
        if dest == pointer:
            if os.path.lexists(dest) and (not dest.is_symlink() or os.readlink(dest) not in (old, str(root))):
                raise ValueError('Repository pointer names a third location; review it before relocating')
            continue
        if not dest.is_symlink() or dest.resolve() != Path(target).resolve():
            raise ValueError('Installed link changed; resolve drift before relocating: ' + destination)
    mapping = {}
    for destination, target in active['links'].items():
        if Path(destination) == pointer:
            continue
        version = Path(target).relative_to(store(home)).parts[0]
        if version in mapping:
            continue
        folder, record = load(home, version, tree_hash)
        if record['repository'] != old:
            raise ValueError('Linked release belongs to another repository: ' + version)
        provenance = dict(record.get('provenance') or {})
        provenance['relocated_from'] = {'release_id': version, 'repository': old}
        packages = {name: folder / 'skills' / name for name in record['packages']}
        mapping[version] = snapshot(root, home, packages, record['source_sha256'], record['kind'], tree_hash,
                                    provenance=provenance)
    links = {}
    for destination, target in active['links'].items():
        if Path(destination) == pointer:
            links[destination] = str(root)
            continue
        version, _, name = Path(target).relative_to(store(home)).parts
        links[destination] = str(store(home) / mapping[version] / 'skills' / name)
    release_id = mapping.get(active['release_id']) or next(iter(mapping.values()))
    result = activate(root, home, release_id, tree_hash, links=links, relocate_from=old)
    return {**result, 'repository': str(root), 'previous_repository': old, 'releases': mapping}


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
                'source_commit': (record.get('provenance', {}).get('source_commit') or record.get('provenance', {}).get('git_head')) if len(versions) <= 1 else None,
                'release_ids': sorted(versions), 'changed_links': changed, 'packages': packages}
    except (OSError, ValueError, KeyError) as exc:
        return {'state': 'damaged', 'ok': False, 'error': str(exc)}
