#!/usr/bin/env python3
"""Prepare versioned, audience-scoped candidates without installing or publishing."""
import argparse
import datetime as dt
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import zipfile

import estate
from catalog import entries, check_public_names, excluded_sources

PROFILE_FILE = 'config/distribution-profiles.json'
HISTORY_FILE = 'config/release-history.json'


def read(path):
    import plugins
    return json.loads(Path(path).read_text(), object_pairs_hook=plugins.strict_object)


def version(value):
    if not isinstance(value, str) or not re.fullmatch(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)', value):
        raise ValueError('Version must be major.minor.patch without leading zeroes')
    return tuple(map(int, value.split('.')))


def load_profile(root, name, allow_blocked=False):
    settings = read(root / PROFILE_FILE)
    if settings.get('format') != 1 or name not in settings.get('profiles', {}):
        raise ValueError('Unknown distribution profile: ' + name)
    row = settings['profiles'][name]
    version(row['version'])
    for key in ('plugin', 'marketplace'):
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', row[key]):
            raise ValueError('Invalid profile ' + key)
    if row.get('audience') not in ('personal', 'workplace'):
        raise ValueError('Profile must declare personal or workplace audience')
    selected = row.get('entries')
    if not isinstance(selected, list) or not selected or len(selected) != len(set(selected)):
        raise ValueError('Profile needs an explicit nonempty unique entrypoint list')
    check_public_names(root, selected)
    if set(selected) - set(entries(root)):
        raise ValueError('Profile selects an unknown task entrypoint')
    if not isinstance(row.get('description'), str) or not row['description'].strip():
        raise ValueError('Profile needs a description')
    if row.get('blocked_reason') and not allow_blocked:
        raise ValueError('Profile blocked: ' + row['blocked_reason'])
    if row['audience'] == 'workplace' and not allow_blocked:
        review = row.get('privacy_review') or {}
        if not review.get('evidence') or not re.fullmatch(r'[0-9a-f]{64}', review.get('payload_sha256', '')):
            raise ValueError('Workplace profile requires review of the complete payload')
    return row


def payload_hash(package):
    records = []
    for p in estate.files(package):
        content = p.read_bytes()
        if p == package / 'estate-release.json':
            receipt = read(p)
            receipt.pop('source_sha256', None)
            receipt.pop('host_adapter', None)
            content = json.dumps(receipt, sort_keys=True).encode()
        records.append((str(p.relative_to(package)), estate.sha(content), p.stat().st_mode & 0o111))
    return estate.sha(json.dumps(records, separators=(',', ':')).encode())


def verify_payload(root, profile, package, *, review_only=False):
    discovered = {p.parent.name for p in (package / 'skills').glob('*/SKILL.md')}
    check_public_names(root, discovered)
    if discovered != set(profile['entries']):
        raise ValueError('Generated plugin entrypoints differ from profile')
    for p in estate.files(package):
        if set(p.relative_to(package).parts) & excluded_sources(root):
            raise ValueError('Excluded source in generated package')
    if profile['audience'] == 'workplace':
        receipt = read(package / 'estate-release.json')
        if set(receipt) != {'status', 'host_adapter', 'source_sha256', 'entries', 'required_modules'}:
            raise ValueError('Unexpected workplace receipt metadata')
        if receipt['host_adapter'] not in ('claude', 'codex') or not re.fullmatch(r'[0-9a-f]{64}', receipt['source_sha256']):
            raise ValueError('Invalid workplace receipt metadata')
        review = profile.get('privacy_review') or {}
        if not review_only and (not review.get('evidence') or review.get('payload_sha256') != payload_hash(package)):
            raise ValueError('Workplace privacy review is stale or excludes payload dependencies')


def adapt_workplace_resources(root, profile, package, manifest):
    """Apply explicit workplace-only resource edits without changing personal sources."""
    path = profile.get('reference_adaptations')
    if not path:
        return
    relative = Path(path)
    if (profile['audience'] != 'workplace' or relative.is_absolute() or '..' in relative.parts
            or relative.parts[:1] != ('config',) or relative.suffix != '.json'):
        raise ValueError('Reference adaptations require a workplace configuration file')
    settings = read(root / relative)
    if settings.get('format') != 1 or not isinstance(settings.get('references'), list):
        raise ValueError('Invalid reference adaptations')
    seen = set()
    for row in settings['references']:
        source = Path(row['source'])
        special = {
            'skills/writing-integrity/SKILL.md',
            'skills/writing-integrity/scripts/learning.py',
            'skills/writing-integrity/assets/setup/setup-prompt.md',
            'skills/writing-integrity/assets/setup/README.md',
            'skills/writing-integrity/scripts/build_kit.py',
            'skills/writing-integrity/assets/setup/web-instructions.md',
            'skills/prose-pass/scripts/prose_receipt_selftest.py',
            'skills/prose-pass/scripts/prose_check_selftest.py',
        }
        reference = (len(source.parts) >= 4 and source.parts[0] == 'skills'
                     and source.parts[2] == 'references' and source.suffix == '.md')
        if (source.is_absolute() or '..' in source.parts or str(source) in seen
                or not (reference or str(source) in special)):
            raise ValueError('Adaptation is outside the allowed workplace resource paths')
        seen.add(str(source))
        original = root / source
        if original.is_symlink() or estate.sha(original.read_bytes()) != row['source_sha256']:
            raise ValueError('Reference adaptation source changed: ' + str(source))
        module, tail = source.parts[1], Path(*source.parts[2:])
        targets = []
        for entry in profile['entries']:
            record = manifest['packages'][entry]
            if record['source_module'] == module:
                targets.append(package / 'skills' / entry / tail)
            elif module in record['runtime_dependencies']:
                targets.append(package / 'skills' / entry / '_runtime' / module / ('WORKFLOW.md' if tail == Path('SKILL.md') else tail))
        if not targets:
            raise ValueError('Adaptation is outside selected dependency closure: ' + str(source))
        for target in targets:
            text = target.read_text()
            for edit in row['edits']:
                before, after, count = edit['before'], edit['after'], edit.get('count', 1)
                if not before or not isinstance(after, str) or type(count) is not int or count < 1 or text.count(before) != count:
                    raise ValueError('Reference adaptation does not match exact text: ' + str(source))
                text = text.replace(before, after)
            target.write_text(text)


def review_fixture(root, name):
    """Build private review bytes; never record approval or create distribution output."""
    import plugins
    result = plugins.build_plugins(root, candidate=True, profile_name=name, review_only=True)
    profile = load_profile(root, name, allow_blocked=True)
    base = root / '.local/privacy-review' / name
    hashes = {host: payload_hash(base / host / 'plugins' / profile['plugin']) for host in ('claude', 'codex')}
    return {**result, 'directory': str(base), 'payload_sha256': hashes,
            'ready_for_distribution': False, 'next': 'Review every file and record the exact payload digest before preparation.'}


def history(root):
    data = read(root / HISTORY_FILE)
    if data.get('format') != 1 or not isinstance(data.get('changes'), list) or not isinstance(data.get('prepared'), list):
        raise ValueError('Invalid release history')
    return data


def bump(root, name, part, note):
    row = load_profile(root, name, allow_blocked=True)
    if not note.strip():
        raise ValueError('Describe the change for the changelog')
    data = read(root / PROFILE_FILE)
    numbers = list(version(row['version']))
    index = ('major', 'minor', 'patch').index(part)
    numbers[index] += 1
    numbers[index + 1:] = [0] * (2 - index)
    next_version = '.'.join(map(str, numbers))
    ledger = history(root)
    ledger['changes'].append({'profile': name, 'from': row['version'], 'version': next_version,
                              'note': note, 'at': dt.datetime.now(dt.timezone.utc).isoformat()})
    # Keep the old configuration for recovery; a failed write never loses it.
    backup = root / '.local/version-backups' / (name + '-' + next_version)
    backup.mkdir(parents=True, exist_ok=False)
    for path in (PROFILE_FILE, HISTORY_FILE):
        shutil.copy2(root / path, backup / Path(path).name)
    data['profiles'][name]['version'] = next_version
    try:
        estate.write_json(root / PROFILE_FILE, data)
        estate.write_json(root / HISTORY_FILE, ledger)
    except BaseException:
        for path in (PROFILE_FILE, HISTORY_FILE):
            shutil.copy2(backup / Path(path).name, root / path)
        raise
    return {'profile': name, 'version': next_version, 'backup': str(backup), 'next': 'Run estate.py sync, then prepare with its source hash.'}


def verify(root, name):
    profile = load_profile(root, name)
    manifest = estate.current_build(root)
    base = root / 'dist/profiles' / name
    result = read(base / 'release.json')
    if result['source_sha256'] != manifest['source_sha256'] or result['selected'] != [profile['plugin']]:
        raise ValueError('Profile build is stale or selects different plugins')
    for host in ('claude', 'codex'):
        package = base / host / 'plugins' / profile['plugin']
        archive = base / host / (profile['plugin'] + '.zip')
        expected = result['packages'][host + '/' + profile['plugin']]
        if estate.tree_hash(package) != expected['tree_sha256'] or estate.sha(archive.read_bytes()) != expected['zip_sha256']:
            raise ValueError('Generated plugin or ZIP changed')
        verify_payload(root, profile, package)
        metadata = read(package / '.claude-plugin/plugin.json')
        if metadata['version'] != profile['version'] or metadata['name'] != profile['plugin']:
            raise ValueError('Plugin manifest version or name differs from profile')
        with zipfile.ZipFile(archive) as zipped:
            actual = {str(p.relative_to(package)): p.read_bytes() for p in estate.files(package)}
            if len(zipped.namelist()) != len(actual) or set(zipped.namelist()) != set(actual):
                raise ValueError('ZIP inventory differs from plugin')
            if any(zipped.read(path) != content for path, content in actual.items()):
                raise ValueError('ZIP content differs from plugin')
        market = read(base / host / ('.claude-plugin/marketplace.json' if host == 'claude' else '.agents/plugins/marketplace.json'))
        listing = {'name': profile['plugin'], 'source': './plugins/' + profile['plugin']} if host == 'claude' else {
            'name': profile['plugin'], 'source': {'source': 'local', 'path': './plugins/' + profile['plugin']},
            'policy': {'installation': 'AVAILABLE', 'authentication': 'ON_INSTALL'}, 'category': 'Productivity'}
        expected_market = {'name': profile['marketplace'], 'plugins': [listing]}
        if host == 'claude':
            expected_market['owner'] = {'name': 'Skills Estate'}
            expected_market['description'] = profile['description']
        if market != expected_market:
            raise ValueError('Marketplace differs from profile')
    return result


def prepared_records(root, name, ledger):
    records = {(r['version'], r['source_sha256']): r for r in ledger['prepared'] if r['profile'] == name}
    base = root / '.local/prepared-releases' / name
    for file in base.glob('*/receipt.json'):
        row = read(file)
        if row['profile'] != name or file.parent.name != row['version'] + '-' + row['source_sha256']:
            raise ValueError('Prepared receipt identity differs from its directory')
        key = (row['version'], row['source_sha256'])
        if key in records and records[key] != row:
            raise ValueError('Prepared receipt differs from release history')
        records[key] = row
    return sorted(records.values(), key=lambda r: (version(r['version']), r['prepared_at']))


def prepare(root, name, expected_source):
    import plugins
    profile = load_profile(root, name)
    manifest = estate.current_build(root)
    if expected_source != manifest['source_sha256']:
        raise ValueError('Preparation requires the current --expected-source hash')
    ledger = history(root)
    prior = prepared_records(root, name, ledger)
    if prior:
        last = prior[-1]
        if version(profile['version']) < version(last['version']) or (
                profile['version'] == last['version'] and expected_source != last['source_sha256']):
            raise ValueError('Source changed without a version bump; run release bump then sync')
    result = plugins.build_plugins(root, candidate=True, profile_name=name)
    if result['source_sha256'] != expected_source:
        raise ValueError('Source changed while preparing the release')
    verify(root, name)
    record = {'profile': name, 'version': profile['version'], 'source_sha256': expected_source,
              'prepared_at': dt.datetime.now(dt.timezone.utc).isoformat(),
              'packages': result['packages'], 'status': 'candidate',
              'ready_for_distribution': False, 'installed': False, 'published': False,
              'review_gaps': result['review_gaps'],
              'remaining': ['Review exact candidate behavior and content.', 'Verify the intended host before distribution.'],
              'previous_prepared': ({k: prior[-1][k] for k in ('profile', 'version', 'source_sha256')} if prior else None)}
    # Immutable local candidates support rollback preparation without host mutation.
    receipt_dir = root / '.local/prepared-releases' / name / (profile['version'] + '-' + expected_source)
    if receipt_dir.exists():
        old = read(receipt_dir / 'receipt.json')
        if old['packages'] != record['packages']:
            raise ValueError('Existing prepared version has different package bytes')
    else:
        receipt_dir.parent.mkdir(parents=True, exist_ok=True)
        stage = Path(tempfile.mkdtemp(prefix='.preparing-', dir=receipt_dir.parent))
        try:
            shutil.copytree(root / 'dist/profiles' / name, stage / 'artifacts')
            estate.write_json(stage / 'receipt.json', record)
            stage.rename(receipt_dir)
        finally:
            if stage.exists():
                shutil.rmtree(stage)
    # Recover a completed snapshot whose subsequent ledger write was interrupted.
    old = read(receipt_dir / 'receipt.json')
    if old not in ledger['prepared']:
        ledger['prepared'].append(old)
        estate.write_json(root / HISTORY_FILE, ledger)
    return {**old, 'receipt': str(receipt_dir / 'receipt.json')}


def main(argv=None, root=estate.ROOT):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for command in ('plan', 'verify', 'prepare', 'bump', 'review'):
        p = sub.add_parser(command)
        p.add_argument('--profile', choices=('personal', 'telix'), required=True)
        if command == 'prepare':
            p.add_argument('--expected-source', required=True)
        if command == 'bump':
            p.add_argument('--part', choices=('major', 'minor', 'patch'), default='patch')
            p.add_argument('--note', required=True)
    args = parser.parse_args(argv)
    root = Path(root)
    try:
        with estate.lock(root):
            if args.command == 'bump':
                result = bump(root, args.profile, args.part, args.note)
            elif args.command == 'prepare':
                result = prepare(root, args.profile, args.expected_source)
            elif args.command == 'review':
                result = review_fixture(root, args.profile)
            elif args.command == 'verify':
                result = verify(root, args.profile)
            else:
                result = {'profile': args.profile, **load_profile(root, args.profile, allow_blocked=True),
                          'source_sha256': estate.source_hash(root), 'installs_or_uploads': False}
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, ValueError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
