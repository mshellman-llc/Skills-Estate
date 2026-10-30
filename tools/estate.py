#!/usr/bin/env python3
"""Build portable skills and reconcile explicitly managed local installations."""
import argparse
import contextlib
import datetime as dt
import errno
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import releases
from portable import assemble, runtime_closure
from catalog import entries as catalog_entries, dependencies as catalog_dependencies, apply_entrypoint

IGNORED = {'.DS_Store', '__pycache__', '.git', '.local', '.venv', 'node_modules'}
DEPENDENCY_INPUTS = ('package.json', 'pnpm-lock.yaml', 'requirements-test.txt')


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


def output_inventory(folder, server_metadata=False):
    """Read every generated file; reject links and special files before mutation."""
    releases.safe_parents(folder)
    result = {}
    if not folder.exists():
        return result
    for parent, dirs, names in os.walk(folder, followlinks=False):
        for name in dirs + names:
            path = Path(parent) / name
            if path.is_symlink() or not (path.is_file() or path.is_dir()):
                raise ValueError(f'Unsupported generated output: {path}')
        for name in names:
            p = Path(parent) / name
            if Path(parent) == folder and re.fullmatch(r'\.smbdelete[A-Za-z0-9]+', name):
                if server_metadata:
                    continue  # SMB owns this open-file deletion placeholder.
                raise ValueError(f'Server-reserved name in staged output: {p}')
            result[str(p.relative_to(folder))] = {'sha256': sha(p.read_bytes()), 'mode': p.stat().st_mode & 0o777}
    return result


def output_modes(root, stage, cache):
    """Plan actual destination permissions before hashing, including SMB mode emulation."""
    releases.safe_parents(root / '.local')
    for path in files(stage):
        requested = path.stat().st_mode & 0o777
        if requested not in cache:
            fd, name = tempfile.mkstemp(prefix='mode-probe-', dir=root / '.local')
            os.close(fd)
            probe = Path(name)
            try:
                probe.chmod(requested)
                cache[requested] = probe.stat().st_mode & 0o777
            finally:
                probe.unlink()
        if cache[requested] != requested:
            path.chmod(cache[requested])


def replace_outputs(root, stage, destination):
    """Publish generated files under the estate lock, including on SMB shares."""
    local = root / '.local'
    releases.safe_parents(local)
    pending = local / ('pending-' + destination.name + '.json')
    if pending.exists():
        raise ValueError(f'Interrupted output replacement requires review: {pending}')
    expected = output_inventory(stage)
    before = output_inventory(destination, server_metadata=True)
    previous = local / ('previous-' + destination.name + '-' + uuid.uuid4().hex)
    # Prefer a directory switch when both paths share a filesystem and it permits rename.
    if stage.stat().st_dev == destination.parent.stat().st_dev:
        moved = False
        try:
            if destination.exists():
                destination.rename(previous)
                moved = True
            stage.rename(destination)
        except OSError as exc:
            if moved:
                previous.rename(destination)
            if exc.errno not in (errno.EACCES, errno.EPERM, errno.EBUSY, errno.EXDEV):
                raise
            if previous.exists():
                raise ValueError(f'Ambiguous directory replacement; inspect {previous}') from exc
        else:
            if previous.exists():
                shutil.rmtree(previous)
            return
    # Network shares can deny directory rename while permitting file writes. Back up
    # only changed files, retain a journal, publish the manifest last, then verify.
    changed = sorted(name for name in set(before) | set(expected) if before.get(name) != expected.get(name))
    if not changed:
        return
    previous.mkdir()
    record = {'destination': str(destination), 'backup': str(previous), 'before': before,
              'expected': expected, 'changed': changed, 'state': 'preparing'}
    try:
        for name in changed:
            if name in before:
                target = previous / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(destination / name, target)
        saved = output_inventory(previous)
        if saved != {name: before[name] for name in changed if name in before}:
            raise ValueError('Generated-output backup verification failed')
        if output_inventory(destination, server_metadata=True) != before or output_inventory(stage) != expected:
            raise ValueError('Generated output changed during replacement preparation')
        record['state'] = 'replacing'
        write_json(pending, record)
        applied = []
        try:
            # File/dir shape changes are refused; never recursively remove a destination.
            for name in changed:
                p = destination / name
                releases.safe_parents(p)
                if p.exists() and not p.is_file():
                    raise ValueError(f'Output shape changed: {p}')
                if any(parent.is_file() for parent in p.parents if parent != destination.parent):
                    raise ValueError(f'Output parent is a file: {p}')
            order = sorted(changed, key=lambda name: (name in ('manifest.json', 'release.json'), name))
            for name in order:
                p = destination / name
                observed = {'sha256': sha(p.read_bytes()), 'mode': p.stat().st_mode & 0o777} if p.is_file() else None
                if observed != before.get(name):
                    raise ValueError(f'Output changed after preflight: {p}')
                applied.append(name)  # Include a partially written file in recovery.
                if name in expected:
                    p.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(stage / name, p)
                else:
                    p.unlink()
            if output_inventory(destination, server_metadata=True) != expected:
                raise ValueError('Published generated output failed verification')
        except BaseException:
            record['state'] = 'failed; restoring'
            write_json(pending, record)
            # Preserve a later edit or an indeterminate partial write for explicit recovery.
            for name in applied:
                p = destination / name
                observed = {'sha256': sha(p.read_bytes()), 'mode': p.stat().st_mode & 0o777} if p.is_file() else None
                if observed not in (before.get(name), expected.get(name)):
                    raise ValueError(f'Output changed or partially written; preserve {pending} for recovery: {p}')
            for name in reversed(applied):
                p = destination / name
                releases.safe_parents(p)
                if name in before:
                    p.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(previous / name, p)
                else:
                    p.unlink(missing_ok=True)
            if output_inventory(destination, server_metadata=True) != before:
                raise ValueError(f'Output restoration incomplete; preserve {pending} and {previous}')
            record['state'] = 'failed; prior files restored'
            write_json(previous / 'replacement-receipt.json', record)
            pending.unlink()
            raise
        record['state'] = 'published; generated output verified'
        pending.unlink()
        shutil.rmtree(previous)
        # Remove only empty generated directories left after obsolete files were removed.
        for parent, dirs, _ in os.walk(destination, topdown=False):
            for name in dirs:
                try:
                    (Path(parent) / name).rmdir()
                except OSError:
                    pass
    except BaseException:
        # A prepared backup is retained for diagnosis; a pending journal blocks reuse.
        if not pending.exists() and not (previous / 'replacement-receipt.json').exists():
            record['state'] = ('published; backup cleanup failed' if record['state'].startswith('published;')
                               else 'preparation failed; destination unchanged')
            write_json(previous / 'replacement-receipt.json', record)
        raise


def source_hash(root=ROOT):
    records = []
    for directory in ('skills', 'policies', 'tools', 'agents', 'tests', 'examples', 'config'):
        records += [(str(p.relative_to(root)), sha(p.read_bytes()), p.stat().st_mode & 0o111)
                    for p in files(root / directory)]
    for name in DEPENDENCY_INPUTS:
        path = root / name
        if path.is_symlink():
            raise ValueError(f'Symlink dependency input: {name}')
        if path.exists():
            if not path.is_file():
                raise ValueError(f'Dependency input is not a file: {name}')
            records.append((name, sha(path.read_bytes()), path.stat().st_mode & 0o111))
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
    releases.safe_parents(local / 'estate.lock')
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


def build(root=ROOT, home=None):
    root = Path(root).resolve()
    homes = {Path.home().resolve(), Path(home or Path.home()).expanduser().resolve()}
    parents = [parent for destination in homes for parent in [*local_targets(destination).values(), destination / '.codex/skills']]
    for parent in parents:
        if parent.is_dir():
            for dest in parent.iterdir():
                if dest.is_symlink() and dest.exists() and dest.resolve().parent == Path(root).resolve() / 'build/skills':
                    raise ValueError('Build would change a legacy installation; run pin-installed first')
    result = validate(root)
    # Keep unchanged packages in place, especially on mounted volumes. Verify
    # their bytes before accepting the existing build; repair damaged builds.
    try:
        return current_build(root)
    except ValueError:
        pass
    stage = Path(tempfile.mkdtemp(prefix='estate-build-')).resolve()
    package_dir = stage / 'skills'
    package_dir.mkdir()
    entries = {}
    mode_cache = {}
    try:
        for name, item in catalog_entries(root).items():
            target = package_dir / name
            source = item['source']
            dependencies = catalog_dependencies(root, item, runtime_closure)
            mapping = assemble(root, source, target, dependencies)
            apply_entrypoint(target, name, item)
            output_modes(root, target, mode_cache)
            entries[name] = {'sha256': tree_hash(target), 'runtime_dependencies': dependencies,
                             'source_files': len(mapping), 'source_module': source,
                             'pack': item['pack'], 'modes': item.get('modes', {})}
        if source_hash(root) != result['source_sha256']:
            raise ValueError('Sources changed during the build; rerun from a stable source tree')
        manifest = {**result, 'packages': entries, 'format': 2}
        write_json(stage / 'manifest.json', manifest)
        output_modes(root, stage, mode_cache)
        destination = root / 'build'
        replace_outputs(root, stage, destination)
        return manifest
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def current_build(root=ROOT):
    if (root / '.local/pending-build.json').exists():
        raise ValueError('Interrupted build replacement requires review before use')
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


def account_skills(home):
    """Skill names the Claude account syncs into Claude Code, under ~/.claude/skills/synced/<account>/<name>."""
    return {path.parent.name for path in (home / '.claude/skills/synced').glob('*/*/SKILL.md')}


def account_renames(root, names):
    """Account skills uploaded under a module name that a public package now carries under its own name."""
    owners = {}
    for entry, item in catalog_entries(root).items():
        for module in [item['source'], *item.get('modes', {}).values()]:
            if module != entry:
                owners.setdefault(module, entry)
    return {name: owners[name] for name in sorted(names) if name in owners and name not in owners.values()}


def local_targets(home):
    return {'claude-code': home / '.claude' / 'skills', 'codex': home / '.agents' / 'skills'}


def install(root=ROOT, home=None, adopt=False, expected_source=None, skills=None, owner=False, claude_code=True):
    home = Path(home or Path.home()).expanduser().resolve()
    manifest = current_build(root)
    selected = set(manifest['packages']) if skills is None else set(skills)
    if not selected or not selected <= set(manifest['packages']):
        raise ValueError('Select existing task package names for targeted promotion')
    if home == Path.home().resolve() and not owner:
        if expected_source != manifest['source_sha256']:
            raise ValueError('Everyday promotion requires --expected-source with the reviewed source hash')
        import plugins
        settings = plugins.config(root)
        gaps = plugins.release_gaps(root, settings, settings['bundles'], manifest, entrypoints=sorted(selected) if skills is not None else None)
        if gaps:
            raise ValueError('Everyday release review pending: ' + ', '.join(x['subject'] for x in gaps))
    with releases.home_lock(home):
        release_id = releases.snapshot(root, home,
            {name: root / 'build/skills' / name for name in sorted(selected)},
            manifest['source_sha256'], 'owner' if owner else 'reviewed' if home == Path.home().resolve() else 'isolated-candidate', tree_hash)
        _, record = releases.load(home, release_id, tree_hash)
        if any(record['packages'][name]['sha256'] != entry['sha256'] for name, entry in manifest['packages'].items() if name in selected):
            raise ValueError('Build changed after verification; refusing promotion')
        if source_hash(root) != manifest['source_sha256']:
            raise ValueError('Source changed after verification; refusing promotion')
        # Skills Claude Code already gets elsewhere (the account, or the marketplace plugins) are linked for Codex only.
        provided = account_skills(home) | (set() if claude_code else set(manifest['packages']))
        return releases.activate(root, home, release_id, tree_hash, adopt=adopt, preserve_existing=skills is not None,
                                 account_provided=provided)


def clear_claude_copies(home, names):
    """Move other copies of estate skills out of ~/.claude/skills into a dated backup with a receipt."""
    moved = {}
    backup = releases.state(home) / ('claude-copies-' + dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    for name in names:
        dest = home / '.claude/skills' / name
        if os.path.lexists(dest):
            backup.mkdir(parents=True, exist_ok=True)
            os.rename(dest, backup / name)
            moved[str(dest)] = str(backup / name)
    if moved:
        write_json(backup / 'receipt.json', {'moved': moved})
    return moved


def update(root=ROOT, home=None, pull=True):
    """The owner's one-step refresh from GitHub main.

    Gets the latest skills, rebuilds, links every public skill for Codex, and moves other
    copies of the same skills out of Claude Code, which uses the marketplace plugins instead.
    """
    home = Path(home or Path.home()).expanduser().resolve()
    if pull:
        pulled = subprocess.run(['git', '-C', str(root), 'pull', '--ff-only', 'origin', 'main'], capture_output=True, text=True)
        if pulled.returncode:
            raise ValueError('Could not get the latest skills from GitHub: ' + (pulled.stderr or pulled.stdout).strip())
    build(root, home=home)
    bundle(root)
    cleared = clear_claude_copies(home, sorted(current_build(root)['packages']))
    result = install(root, home, adopt=True, owner=True, claude_code=False)
    return {**result, 'cleared_from_claude_code': cleared,
            'next': 'Claude Code and Cowork: install the plugins from the skills-estate marketplace.'}


def pin_installed(root=ROOT, home=None):
    """Preserve existing managed bytes; do not promote the candidate source."""
    home = Path(home or Path.home()).expanduser().resolve()
    with releases.home_lock(home):
        current = releases.inspect(home, tree_hash)
        if current['ok']:
            return {'release_id': current['release_id'], 'links_changed': 0, 'backup': None}
        if current['state'] != 'legacy-or-unmanaged':
            raise ValueError('Repair the existing pinned installation before migrating')
        packages, destinations = {}, {}
        for parent in [*local_targets(home).values(), home / '.codex/skills']:
            releases.safe_parents(parent)
            if not parent.exists():
                continue
            for dest in parent.iterdir():
                source = dest.resolve()
                if dest.is_symlink() and source.parent == Path(root).resolve() / 'build/skills' and source.is_dir():
                    packages[source.name] = source
                    destinations[dest] = source.name
        if not packages:
            raise ValueError('No legacy managed links found; unrelated installations preserved')
        release_id = releases.snapshot(root, home, packages, None, 'preserved-existing', tree_hash)
        # Verify every original again before replacing any link.
        for dest, name in destinations.items():
            if dest.resolve() != packages[name]:
                raise ValueError('Installation changed during migration')
        return releases.activate(root, home, release_id, tree_hash, destinations=destinations)


def rollback(root, home, release_id):
    home = Path(home or Path.home()).expanduser().resolve()
    with releases.home_lock(home):
        active = releases.inspect(home, tree_hash)
        if not active['ok']:
            raise ValueError('Current installation drift must be resolved before rollback')
        # Only a previously activated version can be a rollback target.
        history = releases.state(home)
        receipts = [json.loads(p.read_text()) for p in sorted(history.glob('backup-*/receipt.json'), key=lambda p: p.stat().st_mtime_ns, reverse=True)]
        prior = next((r['active'] for r in receipts if r.get('phase') == 'committed' and r.get('active', {}).get('release_id') == release_id), None)
        if prior is None:
            raise ValueError('Rollback target was never activated')
        return releases.activate(root, home, release_id, tree_hash, links=prior['links'])


def restore(receipt_path):
    receipt = json.loads(receipt_path.read_text())
    home = Path(receipt['home']).resolve()
    with releases.home_lock(home):
        operations = receipt['operations']
        active_file = releases.state(home) / 'active.json'
        if receipt.get('format') == 2:
            if not active_file.exists() or json.loads(active_file.read_text()) != receipt['active']:
                raise ValueError('Changed active installation; refusing restore')
        for op in operations:
            dest = Path(op['destination'])
            if receipt.get('format') == 2 and op['backup']:
                saved = Path(op['backup'])
                legacy = saved.resolve()
                if saved.is_symlink() and legacy.parent == Path(receipt['active']['repository']) / 'build/skills':
                    _, pinned = releases.load(home, receipt['active']['release_id'], tree_hash)
                    if not legacy.is_dir() or tree_hash(legacy) != pinned['packages'][legacy.name]['sha256']:
                        raise ValueError('Legacy build changed; keep the pinned release instead of restoring mutable links')
            if op['source']:
                if not dest.is_symlink() or dest.resolve() != Path(op['source']).resolve():
                    raise ValueError(f'Changed since installation; refusing restore: {dest}')
            elif os.path.lexists(dest):
                raise ValueError(f'Changed retired destination; refusing restore: {dest}')
            if op['backup'] and not os.path.lexists(op['backup']):
                raise ValueError(f'Missing backup: {op["backup"]}')
        for op in reversed(operations):
            dest = Path(op['destination'])
            if op['source']:
                dest.unlink()
            if op['backup']:
                Path(op['backup']).rename(dest)
        if receipt.get('format') == 2:
            if receipt['previous_active']:
                write_json(active_file, receipt['previous_active'])
            else:
                active_file.unlink()
        return {'restored': len(operations)}


def bundle(root=ROOT):
    root = Path(root).resolve()
    manifest = current_build(root)
    stage = Path(tempfile.mkdtemp(prefix='estate-dist-')).resolve()
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
        output_modes(root, stage, {})
        destination = root / 'dist'
        replace_outputs(root, stage, destination)
        return release
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def status(root=ROOT, home=None):
    home = Path(home or Path.home()).expanduser().resolve()
    inspection_errors = {}
    try:
        desired_source = source_hash(root)
    except (ValueError, OSError) as exc:
        desired_source = None
        inspection_errors['source'] = str(exc)
    def read_manifest(path, label):
        if not path.exists():
            return {'packages': {}}
        try:
            data = json.loads(path.read_text())
            if not isinstance(data, dict) or not isinstance(data.get('packages'), dict):
                raise ValueError('Invalid package manifest')
            return data
        except (ValueError, OSError) as exc:
            inspection_errors[label] = str(exc)
            return {'packages': {}}
    manifest = read_manifest(root / 'build/manifest.json', 'build')
    release = read_manifest(root / 'dist/release.json', 'dist')
    try:
        current_build(root)
        build_state = 'current'
    except (ValueError, OSError, KeyError, TypeError) as exc:
        build_state = str(exc)
    installed = releases.inspect(home, tree_hash)
    try:
        catalog_names = set(catalog_entries(root))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        inspection_errors['catalog'] = str(exc)
        catalog_names = set()
    public_names = catalog_names | set(manifest['packages']) | set(installed.get('packages', {})) | set(release['packages'])
    surfaces = {}
    verified_releases = {}
    account = account_skills(home)
    owner_release = installed.get('kind') == 'owner'
    ok = build_state == 'current' and installed['ok']
    content_cache = {}
    for surface, target in local_targets(home).items():
        rows = {}
        for name in sorted(public_names):
            dest = target / name
            entry = manifest['packages'].get(name)
            if surface == 'claude-code' and (name in account or (owner_release and name in manifest['packages'])):
                # One copy per skill in Claude Code: the account's, or after `update` the marketplace plugin's.
                rows[name] = 'duplicate' if os.path.lexists(dest) else 'account-provided' if name in account else 'marketplace'
                ok &= rows[name] != 'duplicate'
                continue
            if not dest.is_dir():
                value = 'broken-link' if dest.is_symlink() else 'missing'
            else:
                try:
                    resolved = dest.resolve()
                    if resolved not in content_cache:
                        content_cache[resolved] = tree_hash(resolved)
                    actual = content_cache[resolved]
                    same = bool(entry and actual == entry['sha256'])
                    pinned = releases.managed_link(dest, home, root, tree_hash, verified_releases) and '/releases/' in str(dest.resolve())
                    value = ('linked-current' if pinned else 'legacy-mutable') if same and build_state == 'current' else ('pinned-older' if pinned else 'drift')
                except (ValueError, OSError, KeyError, TypeError) as exc:
                    inspection_errors[str(dest)] = str(exc)
                    value = 'drift'
            rows[name] = value
            ok &= value == 'linked-current'
        surfaces[surface] = rows
    dist_rows = {}
    for name in sorted(public_names):
        entry = (release or {}).get('packages', {}).get(name)
        value = 'missing'
        if entry:
            try:
                file = root / 'dist' / entry['file']
                if file.parent != root / 'dist' or file.is_symlink():
                    value = 'invalid-path'
                elif not file.is_file():
                    value = 'missing'
                elif sha(file.read_bytes()) != entry['sha256']:
                    value = 'modified'
                else:
                    value = 'current' if desired_source and release.get('source_sha256') == desired_source else 'stale-source'
            except (OSError, KeyError, TypeError) as exc:
                inspection_errors['dist/' + name] = str(exc)
                value = 'invalid-metadata'
        dist_rows[name] = value
    ok &= bool(dist_rows) and all(value == 'current' for value in dist_rows.values())
    ledger_path = root / '.local/cloud-publications.json'
    try:
        ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {}
        if not isinstance(ledger, dict):
            raise ValueError('Invalid publication ledger')
    except (OSError, ValueError) as exc:
        ledger = {}
        inspection_errors['publication_ledger'] = str(exc)
    cloud = {}
    for surface in ['claude-account', 'cowork', 'codex-account', 'chatgpt-personal']:
        rows = {}
        for name in sorted(public_names):
            recorded = ledger.get(surface, {}).get(name)
            expected = (release or {}).get('packages', {}).get(name, {}).get('sha256')
            rows[name] = 'reported-current' if dist_rows[name] == 'current' and recorded and recorded['sha256'] == expected else 'pending'
        cloud[surface] = {'packages': rows, 'verified_live': False}
    external = []
    for base in [home / '.codex/skills', home / '.agents/skills/synced', home / '.claude/skills/synced']:
        if base.exists():
            for parent, dirs, fs in os.walk(base, followlinks=False):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                if 'SKILL.md' in fs:
                    external.append({'path': parent, 'name': Path(parent).name})
    legacy_rows = {}
    for name in sorted(public_names):
        dest = home / '.codex/skills' / name
        if os.path.lexists(dest):
            try:
                expected = manifest['packages'].get(name, {}).get('sha256')
                same = dest.is_dir() and tree_hash(dest.resolve()) == expected and build_state == 'current'
                legacy_rows[name] = 'current' if same else 'drift'
            except (ValueError, OSError) as exc:
                inspection_errors[str(dest)] = str(exc)
                legacy_rows[name] = 'drift'
            ok &= legacy_rows[name] == 'current'
    try:
        renamed = account_renames(root, account)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        inspection_errors['account_renames'] = str(exc)
        renamed = {}
    return {'build': build_state, 'source_sha256': desired_source, 'dist': dist_rows,
            'account': {'skills': sorted(account), 'replace_with_package': renamed},
            'installed_release': installed, 'local': surfaces, 'legacy_codex_aliases': legacy_rows,
            'external_skill_locations': external, 'inspection_errors': inspection_errors,
            'cloud': cloud, 'ok': bool(ok and not inspection_errors)}


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
    for command in ['validate', 'build', 'bundle', 'sync', 'status', 'pin-installed', 'update']:
        sub.add_parser(command)
    for command in ['install', 'adopt']:
        install_parser = sub.add_parser(command)
        install_parser.add_argument('--expected-source')
        install_parser.add_argument('--skill', action='append', help='Promote only this task package; repeat to select more')
    sub.add_parser('rollback').add_argument('release_id')
    rp = sub.add_parser('restore')
    rp.add_argument('receipt', type=Path)
    pub = sub.add_parser('record-publication')
    pub.add_argument('--surface', choices=['claude-account', 'cowork', 'codex-account', 'chatgpt-personal'], required=True)
    pub.add_argument('--skill', required=True)
    pub.add_argument('--reference', required=True, help='Account and upload record; a report, not independent verification')
    args = ap.parse_args()
    try:
        with lock():
            if args.command == 'validate': result = validate()
            elif args.command == 'build': result = build(home=args.home)
            elif args.command == 'bundle': result = bundle()
            elif args.command in {'install', 'adopt'}: result = install(home=args.home, adopt=args.command == 'adopt', expected_source=args.expected_source, skills=args.skill)
            elif args.command == 'pin-installed': result = pin_installed(home=args.home)
            elif args.command == 'update': result = update(home=args.home)
            elif args.command == 'rollback': result = rollback(ROOT, args.home, args.release_id)
            elif args.command == 'restore': result = restore(args.receipt)
            elif args.command == 'status': result = status(home=args.home)
            elif args.command == 'record-publication': result = record_publication(ROOT, args.surface, args.skill, args.reference)
            elif args.command == 'sync':
                build(home=args.home); bundle()
                result = {'build': 'current', 'dist': 'current', 'installed': 'unchanged', 'ok': True}
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1 if args.command in {'status', 'sync'} and not result['ok'] else 0
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as e:
        print(str(e), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
