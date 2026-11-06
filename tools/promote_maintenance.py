#!/usr/bin/env python3
"""Promote a reviewed maintainer from an isolated checkout of this estate."""
import argparse
import json
from pathlib import Path
import subprocess

import estate
import plugins
import releases

PACKAGE = 'maintain-skills-estate'
MODES = ('author-estate-skill', 'release-skill-package')


def reviewed_candidate(candidate, expected_source):
    manifest = estate.current_build(candidate)
    if expected_source != manifest['source_sha256']:
        raise ValueError('Candidate differs from the reviewed source hash')
    with estate.source_snapshot(candidate) as (source, _):
        settings = plugins.config(source)
        gaps = plugins.release_gaps(source, settings, settings['bundles'], manifest,
                                    entrypoints=[PACKAGE])
    if gaps:
        raise ValueError('Maintenance review pending: ' + ', '.join(x['subject'] for x in gaps))
    for mode in MODES:
        if not (candidate / 'build/skills' / PACKAGE / '_runtime' / mode / 'WORKFLOW.md').is_file():
            raise ValueError('Candidate lacks maintenance mode: ' + mode)
    return manifest


def current_identity(repository, home):
    active = json.loads((releases.state(home) / 'active.json').read_text())
    pointer = home / '.config/skills-estate/repository'
    if active['repository'] != str(repository) or not pointer.is_symlink() or pointer.resolve() != repository:
        raise ValueError('Canonical repository identity or pointer differs')
    if not releases.inspect(home, estate.tree_hash)['ok']:
        raise ValueError('Current installation drift must be resolved')
    return active


def promote(candidate, repository, home, expected_source):
    candidate, repository, home = (Path(p).resolve() for p in (candidate, repository, home))
    manifest = reviewed_candidate(candidate, expected_source)
    package = candidate / 'build/skills' / PACKAGE
    with releases.home_lock(home):
        current_identity(repository, home)
        head = subprocess.run(['git', '-C', str(candidate), 'rev-parse', 'HEAD'],
                              capture_output=True, text=True)
        release_id = releases.snapshot(repository, home, {PACKAGE: package},
            expected_source, 'reviewed-isolated-candidate', estate.tree_hash,
            provenance={'source_checkout': str(candidate),
                        'git_head': head.stdout.strip() if head.returncode == 0 else None,
                        'canonical_repository': str(repository)})
        _, record = releases.load(home, release_id, estate.tree_hash)
        if record['packages'][PACKAGE]['sha256'] != manifest['packages'][PACKAGE]['sha256']:
            raise ValueError('Candidate package changed after review')
        if estate.committed_identity(candidate)['source_sha256'] != expected_source:
            raise ValueError('Candidate source changed after review')
        # Confirm review and build state again immediately before activation.
        reviewed_candidate(candidate, expected_source)
        return releases.activate(repository, home, release_id, estate.tree_hash,
                                 preserve_existing=True)


def verify_native_receipt(native_receipt, expected_package):
    if native_receipt.get('package_sha256') != expected_package or set(native_receipt.get('hosts', {})) != {'codex', 'claude'}:
        raise ValueError('Native receipt belongs to another package or omits a host')
    for row in native_receipt['hosts'].values():
        output = Path(row.get('output', ''))
        modes = row.get('modes', [])
        if row.get('verified') is not True or len(modes) != len(MODES) or set(modes) != set(MODES):
            raise ValueError('Native receipt must verify both maintenance modes in each host')
        if not output.is_absolute() or not output.is_file() or estate.sha(output.read_bytes()) != row.get('output_sha256'):
            raise ValueError('Native output is missing or changed')


def retire(candidate, repository, home, expected_source, plan, native_receipt, cleanup_lock, owner):
    candidate, repository, home = (Path(p).resolve() for p in (candidate, repository, home))
    manifest = reviewed_candidate(candidate, expected_source)
    lock_owner = json.loads((Path(cleanup_lock) / 'owner.json').read_text())
    if lock_owner.get('chat_id') != owner or lock_owner.get('state') != 'active':
        raise ValueError('Shared cleanup lock is not owned by this retirement run')
    expected_package = manifest['packages'][PACKAGE]['sha256']
    verify_native_receipt(native_receipt, expected_package)
    with releases.home_lock(home):
        active = current_identity(repository, home)
        if releases.digest(active) != plan.get('active_sha256'):
            raise ValueError('Active installation changed after retirement planning')
        desired = dict(active['links'])
        expected_paths = {str(home / host / mode) for host in ('.agents/skills', '.claude/skills') for mode in MODES}
        if set(plan.get('remove', {})) != expected_paths:
            raise ValueError('Retirement must name exactly the four predecessor links')
        for host in ('.agents/skills', '.claude/skills'):
            installed = home / host / PACKAGE
            if estate.tree_hash(installed.resolve()) != expected_package:
                raise ValueError('Installed maintainer differs from native verification')
        for name, target in plan['remove'].items():
            if desired.get(name) != target:
                raise ValueError('Predecessor target changed: ' + name)
            del desired[name]
        reviewed_candidate(candidate, expected_source)
        verify_native_receipt(native_receipt, expected_package)
        if json.loads((Path(cleanup_lock) / 'owner.json').read_text()) != lock_owner:
            raise ValueError('Shared cleanup lock owner changed')
        return releases.activate(repository, home, active['release_id'], estate.tree_hash, links=desired)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['promote', 'retire'])
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--repository', type=Path, required=True)
    parser.add_argument('--home', type=Path, default=Path.home())
    parser.add_argument('--expected-source', required=True)
    parser.add_argument('--plan', type=Path)
    parser.add_argument('--native-receipt', type=Path)
    parser.add_argument('--cleanup-lock', type=Path)
    parser.add_argument('--owner')
    args = parser.parse_args()
    try:
        common = (args.candidate, args.repository, args.home, args.expected_source)
        if args.operation == 'promote':
            result = promote(*common)
        else:
            if not all((args.plan, args.native_receipt, args.cleanup_lock, args.owner)):
                raise ValueError('Retirement requires a plan, native receipt and owned cleanup lock')
            result = retire(*common, json.loads(args.plan.read_text()), json.loads(args.native_receipt.read_text()),
                            args.cleanup_lock, args.owner)
        print(json.dumps(result, indent=2))
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
