"""Prepare verified GitHub main in isolation, then activate its immutable packages."""
import datetime as dt
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import uuid

import estate
import marketplace_guard
import releases

REPOSITORY = 'mshellman-llc/Skills-Estate'
REMOTE = 'https://github.com/' + REPOSITORY + '.git'


def command(args, cwd=None, log=None, env=None):
    if log is not None:
        with Path(log).open('w') as output:
            result = subprocess.run(args, cwd=cwd, env=env, stdout=output, stderr=subprocess.STDOUT)
        if result.returncode:
            raise ValueError(f'Update step failed ({result.returncode}); see {log}')
        return ''
    result = subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True)
    if result.returncode:
        raise ValueError('Update command failed: ' + (result.stderr or result.stdout).strip())
    return result.stdout.strip()


def fetch_main(candidate, evidence):
    command(['git', 'init', '-q', str(candidate)])
    command(['git', '-C', str(candidate), 'remote', 'add', 'origin', REMOTE])
    command(['git', '-C', str(candidate), 'fetch', '--no-tags', '--depth=2', 'origin',
             'refs/heads/main:refs/remotes/origin/main'], log=evidence / 'fetch.log')
    revision = command(['git', '-C', str(candidate), 'rev-parse', 'refs/remotes/origin/main'])
    command(['git', '-C', str(candidate), '-c', 'core.hooksPath=/dev/null', 'checkout', '--detach', revision])
    return revision


def workflow_runs(revision):
    gh = shutil.which('gh')
    if gh is None:
        configured = Path.home() / '.local/bin/gh'
        gh = str(configured) if configured.is_file() else None
    if gh is None:
        raise ValueError('The configured GitHub CLI is required to verify main')
    endpoint = f'repos/{REPOSITORY}/actions/workflows/verify.yml/runs?branch=main&head_sha={revision}&per_page=100'
    pages = json.loads(command([gh, 'api', '--paginate', '--slurp', endpoint]))
    return [run for page in pages for run in page.get('workflow_runs', [])]


def verify_remote(candidate, revision, evidence):
    runs = workflow_runs(revision)
    if not marketplace_guard.matching_runs(revision, {'workflow_runs': runs}):
        parent = marketplace_guard.generated_only_parent(candidate, revision)
        runs += workflow_runs(parent)
    result = marketplace_guard.verify_publication(candidate, revision, {'workflow_runs': runs})
    result['repository'] = REPOSITORY
    result['run_url'] = f'https://github.com/{REPOSITORY}/actions/runs/{result["verified_run"]}'
    estate.write_json(evidence / 'remote-verification.json', result)
    return result


def local_environment(repository, candidate):
    env = dict(os.environ)
    # Reuse the explicitly configured runtime or the owner's existing dependency
    # installation only when the declared versions/lock match the fetched source.
    if not env.get('ESTATE_NODE_MODULES') and (repository / 'node_modules').is_dir():
        same = all((repository / name).is_file() and (repository / name).read_bytes() == (candidate / name).read_bytes()
                   for name in ('package.json', 'pnpm-lock.yaml'))
        if same:
            env['ESTATE_NODE_MODULES'] = str(repository / 'node_modules')
    modules = env.get('ESTATE_NODE_MODULES')
    if modules:
        env['NODE_PATH'] = os.pathsep.join(filter(None, (modules, env.get('NODE_PATH'))))
    return env


def test_candidate(repository, candidate, evidence):
    env = local_environment(repository, candidate)
    command([sys.executable, str(candidate / 'tools/verify.py'), '--refresh', '--integration', 'generated-map', '--json'],
            cwd=candidate, env=env, log=evidence / 'local-verification.log')
    report = json.loads((candidate / '.local/verify-tests.json').read_text())
    if (report.get('status') not in {'passed', 'passed_with_deferred'} or not report.get('executed')
            or report.get('failures') or report.get('errors') or report.get('other_skips')):
        raise ValueError('Local verification did not pass; installation preserved')
    estate.write_json(evidence / 'local-tests.json', report)
    return {'report': str(evidence / 'local-tests.json'), 'sha256': estate.sha((evidence / 'local-tests.json').read_bytes()),
            'executed': report['executed'], 'passed': report['passed'], 'deferred': report.get('deferred', []),
            'node_modules': env.get('ESTATE_NODE_MODULES')}


def build_candidate(candidate, home, revision, evidence):
    command([sys.executable, str(candidate / 'tools/estate.py'), '--home', str(home), 'sync'],
            cwd=candidate, log=evidence / 'build.log')
    manifest = json.loads((candidate / 'build/manifest.json').read_text())
    if manifest.get('source_commit') != revision or not manifest.get('packages'):
        raise ValueError('Built packages do not identify the fetched commit')
    if command(['git', '-C', str(candidate), 'rev-parse', 'HEAD']) != revision:
        raise ValueError('Fetched checkout changed during verification')
    # The fetched CLI checks its own committed toolchain and source before packaging.
    # Recheck every resulting package before handing it to the installed release store.
    for name, entry in manifest['packages'].items():
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name):
            raise ValueError('Invalid candidate package name')
        if estate.tree_hash(candidate / 'build/skills' / name) != entry['sha256']:
            raise ValueError('Candidate package changed after build: ' + name)
    estate.write_json(evidence / 'build-manifest.json', manifest)
    return manifest


def installation_state(home):
    """Observe active metadata and owned destinations across the preparation interval."""
    active_file = releases.state(home) / 'active.json'
    active = json.loads(active_file.read_text()) if active_file.exists() else None
    names = {Path(p).name for p in (active or {}).get('links', {}) if Path(p).name != 'repository'}
    paths = {Path(p) for p in (active or {}).get('links', {})}
    paths.update(home / '.claude/skills' / name for name in names)
    return {'active': active, 'paths': {str(p): releases.path_state(p) for p in sorted(paths)}}


def activate_candidate(repository, candidate, home, manifest, evidence, provenance, before):
    with releases.home_lock(home):
        if installation_state(home) != before:
            raise ValueError('Installation changed while preparing update; current state preserved')
        if before['active'] and not releases.inspect(home, estate.tree_hash)['ok']:
            raise ValueError('Current installation drift must be resolved before updating')
        packages = {name: candidate / 'build/skills' / name for name in manifest['packages']}
        duplicates = [home / '.claude/skills' / name for name in packages
                      if os.path.lexists(home / '.claude/skills' / name)]
        current = releases.inspect(home, estate.tree_hash)
        expected = {name: {'sha256': row['sha256']} for name, row in manifest['packages'].items()}
        active = before['active'] or {}
        folder = releases.store(home) / current.get('release_id', '') / 'skills'
        desired = {str(home / '.agents/skills' / name): str(folder / name) for name in packages}
        desired.update({str(home / '.codex/skills' / name): str(folder / name) for name in packages
                        if os.path.lexists(home / '.codex/skills' / name)})
        desired[str(home / '.config/skills-estate/repository')] = str(repository)
        inventory_matches = active.get('repository') == str(repository) and active.get('links') == desired
        if (current.get('ok') and len(current.get('release_ids', [])) == 1 and inventory_matches
                and current.get('source_commit') == manifest['source_commit']
                and current.get('packages') == expected and not duplicates):
            return {'release_id': current['release_id'], 'links_changed': 0, 'backup': None,
                    'source_commit': manifest['source_commit'], 'evidence': str(evidence),
                    'previous_release': current['release_id'], 'already_current': True,
                    'claude': {'route': 'skills-estate marketplace', 'cache_changed': False,
                               'local_duplicates_backed_up': []}}
        release_id = releases.snapshot(repository, home, packages, manifest['source_sha256'], 'owner',
                                       estate.tree_hash, provenance=provenance)
        _, release = releases.load(home, release_id, estate.tree_hash)
        if any(release['packages'][name]['sha256'] != row['sha256'] for name, row in manifest['packages'].items()):
            raise ValueError('Prepared packages changed before activation')
        # Policy comes from the fetched source; the release and pointer belong to
        # the durable authoring repository, never the disposable checkout.
        result = releases.activate(repository, home, release_id, estate.tree_hash,
                                   account_provided=packages, policy_root=candidate, remove_paths=duplicates)
        return {**result, 'source_commit': manifest['source_commit'], 'evidence': str(evidence),
                'previous_release': (before['active'] or {}).get('release_id'),
                'claude': {'route': 'skills-estate marketplace', 'cache_changed': False,
                           'local_duplicates_backed_up': [str(p) for p in duplicates]}}


def update(repository, home=None):
    repository = Path(repository).resolve()
    home = Path(home or Path.home()).expanduser().resolve()
    with releases.home_lock(home):
        releases.require_no_pending(home)
        before = installation_state(home)
        if before['active']:
            if before['active']['repository'] != str(repository):
                raise ValueError('This home already has another managed repository')
            if not releases.inspect(home, estate.tree_hash)['ok']:
                raise ValueError('Current installation drift must be resolved before updating')
    evidence = releases.state(home) / ('update-' + dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8])
    releases.safe_parents(evidence)
    evidence.mkdir(parents=True)
    receipt = {'repository': str(repository), 'remote': REMOTE, 'previous_release': (before['active'] or {}).get('release_id'),
               'state': 'preparing'}
    estate.write_json(evidence / 'update.json', receipt)
    try:
        with tempfile.TemporaryDirectory(prefix='estate-main-') as directory:
            candidate = Path(directory) / 'source'
            revision = fetch_main(candidate, evidence)
            receipt['source_commit'] = revision
            remote = verify_remote(candidate, revision, evidence)
            tests = test_candidate(repository, candidate, evidence)
            manifest = build_candidate(candidate, home, revision, evidence)
            provenance = {'source_commit': revision, 'remote': REMOTE, 'verification': remote,
                          'local_tests': tests, 'evidence': str(evidence)}
            # Verify latest run status again immediately before activation. A newer
            # main commit is a later update; this run remains pinned to the fetched SHA.
            if verify_remote(candidate, revision, evidence) != remote:
                raise ValueError('Remote verification changed during preparation; retry update')
            result = activate_candidate(repository, candidate, home, manifest, evidence, provenance, before)
            receipt.update(state='installed', **result)
            try:
                estate.write_json(evidence / 'update.json', receipt)
            except OSError as exc:
                # Activation has its own committed restore receipt. A reporting
                # write must not turn a successful installation into a false failure.
                receipt['reporting_warning'] = str(exc)
            return receipt
    except BaseException as exc:
        if receipt['state'] == 'installed':
            receipt['cleanup_warning'] = str(exc)
            return receipt
        receipt.update(state='failed', error=str(exc))
        try:
            estate.write_json(evidence / 'update.json', receipt)
        except OSError:
            pass  # Preserve the original failure; activation journals remain authoritative.
        raise
