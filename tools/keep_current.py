#!/usr/bin/env python3
"""Keep this computer's Skills Estate tools on the version published on GitHub main.

    keep_current.py run      [--source DIR] [--state FILE] [--dry]
    keep_current.py install  [--interval SECONDS] [--source DIR] [--state FILE]
    keep_current.py status   [--state FILE]

run refreshes a shallow clone of main that this tool owns (default ~/.agents/estate-main)
and brings three things up to that version, touching only what lags:

- the writing hooks and gate in ~/.agents/writing/bin, through the writing skill's install_local.py
- the Skills Estate plugins installed in Claude Code, with `claude plugin update`
- the Skills Estate plugins installed in Codex, with `codex plugin marketplace upgrade`

It writes what it found and did to ~/.agents/writing/state/keep-current.json and exits 1
when anything is still behind or a step failed. --dry reports without changing anything.

install writes a LaunchAgent that runs `run` from the clone at login and every hour, so the
job itself stays on main. Claude Code and Codex apply an updated plugin when a session restarts.
Never edit the clone; it is reset to main on every run.

Standard library only.
"""
import argparse
import datetime as dt
import json
import os
import plistlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

REMOTE = 'https://github.com/mshellman-llc/Skills-Estate.git'
MARKETPLACE = 'skills-estate'
LABEL = 'com.mshellman.estate-keep-current'
HOME = Path.home()
DEFAULT_SOURCE = HOME / '.agents' / 'estate-main'
DEFAULT_STATE = HOME / '.agents' / 'writing' / 'state' / 'keep-current.json'
HOOKS = HOME / '.agents' / 'writing' / 'bin'
PATH_DIRS = [str(HOME / '.local' / 'bin'), '/opt/homebrew/bin', '/usr/local/bin', '/usr/bin', '/bin']


def sh(args, cwd=None, timeout=600):
    try:
        r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, '', str(exc)
    return r.returncode, (r.stdout or '').strip(), (r.stderr or '').strip()


def refresh_source(source):
    """Clone or reset the owned clone to main. Returns (commit, plugin version)."""
    if not (source / '.git').is_dir():
        source.parent.mkdir(parents=True, exist_ok=True)
        code, _, err = sh(['git', 'clone', '-q', '--depth', '1', '--branch', 'main', REMOTE, str(source)])
        if code:
            raise RuntimeError('git clone failed: ' + err)
    else:
        for step in (['git', 'fetch', '-q', '--depth', '1', 'origin', 'main'],
                     ['git', 'reset', '-q', '--hard', 'FETCH_HEAD']):
            code, _, err = sh(step, cwd=source)
            if code:
                raise RuntimeError(' '.join(step[:2]) + ' failed: ' + err)
    _, commit, _ = sh(['git', 'rev-parse', 'HEAD'], cwd=source)
    version = json.loads((source / 'config' / 'plugin-bundles.json').read_text(encoding='utf-8'))['version']
    return commit, version


def hooks_commit(hooks=HOOKS):
    try:
        return json.loads((hooks / 'MANIFEST.json').read_text(encoding='utf-8')).get('commit')
    except (OSError, ValueError):
        return None


def claude_plugins(text):
    """Skills Estate plugins in `claude plugin list --json`, as (id, version, scope)."""
    try:
        items = json.loads(text)
    except ValueError:
        return []
    return [(i['id'], i.get('version'), i.get('scope') or 'user') for i in items
            if isinstance(i, dict) and str(i.get('id', '')).endswith('@' + MARKETPLACE)]


def codex_plugins(text):
    """Installed Skills Estate plugins in `codex plugin list`, as (id, version)."""
    out = []
    for line in text.splitlines():
        m = re.match(r'^(\S+@' + re.escape(MARKETPLACE) + r')\s+installed\b[^0-9]*?(\d+\.\d+\.\d+)', line)
        if m:
            out.append((m.group(1), m.group(2)))
    return out


def published(source, plugin_id):
    """Version of a plugin as published in the clone. The publish workflow writes it a few
    minutes after a merge, so it can trail config/plugin-bundles.json for that long."""
    name = plugin_id.split('@')[0]
    for rel in ('.claude-plugin/plugin.json', 'plugin.json'):
        try:
            return json.loads((source / 'plugins' / name / rel).read_text(encoding='utf-8'))['version']
        except (OSError, ValueError, KeyError):
            continue
    return None


def lagging(found, version):
    """Plugins whose installed version differs from the target. version is one string, or a
    function from plugin id to the published version (None means not published; skipped)."""
    target = version if callable(version) else (lambda _id: version)
    return [p for p in found if target(p[0]) is not None and p[1] != target(p[0])]


def tool(name):
    return shutil.which(name, path=os.pathsep.join(PATH_DIRS + [os.environ.get('PATH', '')]))


def keep_claude(version, report, dry):
    claude = tool('claude')
    if not claude:
        report['claude_code'] = {'missing': True}
        return
    found = claude_plugins(sh([claude, 'plugin', 'list', '--json'])[1])
    entry = report['claude_code'] = {'before': {p: v for p, v, _ in found}}
    lag = lagging(found, version)
    if lag and not dry:
        code, _, err = sh([claude, 'plugin', 'marketplace', 'update', MARKETPLACE])
        if code:
            report['errors'].append('claude marketplace update: ' + err)
        for pid, _, scope in lag:
            code, out, err = sh([claude, 'plugin', 'update', pid, '-s', scope, '--json'], timeout=300)
            if code:
                report['errors'].append(f'claude plugin update {pid}: {err or out}')
        found = claude_plugins(sh([claude, 'plugin', 'list', '--json'])[1])
        before = entry['before']
        report['actions'] += [f'Claude Code: {p} {before.get(p)} to {v}' for p, v, _ in found if before.get(p) != v]
    entry['after'] = {p: v for p, v, _ in found}
    entry['behind'] = [p for p, _, _ in lagging(found, version)]


def keep_codex(version, report, dry):
    codex = tool('codex')
    if not codex:
        report['codex'] = {'missing': True}
        return
    found = codex_plugins(sh([codex, 'plugin', 'list'])[1])
    entry = report['codex'] = {'before': dict(found)}
    if lagging(found, version) and not dry:
        for _ in range(2):  # Codex's own clone gives up after 30 seconds; one retry covers a slow fetch
            code, out, err = sh([codex, 'plugin', 'marketplace', 'upgrade', MARKETPLACE], timeout=300)
            if not code:
                break
        if code:
            report['errors'].append('codex marketplace upgrade: ' + (err or out))
        else:
            report['actions'].append('Codex: upgraded the skills-estate marketplace')
        found = codex_plugins(sh([codex, 'plugin', 'list'])[1])
    entry['after'] = dict(found)
    entry['behind'] = [p for p, _ in lagging(found, version)]


def keep_hooks(source, commit, report, dry, hooks=HOOKS):
    entry = report['hooks'] = {'before': hooks_commit(hooks)}
    if entry['before'] != commit and not dry:
        code, out, err = sh([sys.executable, str(source / 'skills' / 'writing' / 'scripts' / 'install_local.py')])
        if code:
            report['errors'].append('install_local.py: ' + (err or out)[-400:])
        else:
            report['actions'].append('Writing hooks reinstalled from main')
    entry['after'] = hooks_commit(hooks)
    entry['behind'] = entry['after'] != commit


def write_state(state, report):
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text(json.dumps(report, indent=1) + '\n', encoding='utf-8')


def run_once(source, state, dry=False):
    report = {'checked_at': dt.datetime.now().astimezone().isoformat(timespec='seconds'),
              'dry': dry, 'actions': [], 'errors': []}
    try:
        commit, version = refresh_source(source)
    except (RuntimeError, OSError, ValueError, KeyError) as exc:
        report['errors'].append(str(exc))
        report['current'] = False
        write_state(state, report)
        print(json.dumps(report, indent=1))
        return 1
    report.update(main_commit=commit, main_version=version,
                  published_version=published(source, 'estate-writing@' + MARKETPLACE))
    target = lambda plugin_id: published(source, plugin_id)  # noqa: E731
    keep_hooks(source, commit, report, dry)
    keep_claude(target, report, dry)
    keep_codex(target, report, dry)
    report['current'] = (not report['errors'] and not report['hooks']['behind']
                         and not report['claude_code'].get('behind') and not report['codex'].get('behind'))
    write_state(state, report)
    print(json.dumps(report, indent=1))
    return 0 if report['current'] else 1


def install(interval, source, state):
    refresh_source(source)
    logs = state.parent
    logs.mkdir(parents=True, exist_ok=True)
    agent = {
        'Label': LABEL,
        'ProgramArguments': ['/usr/bin/python3', str(source / 'tools' / 'keep_current.py'), 'run',
                             '--source', str(source), '--state', str(state)],
        'EnvironmentVariables': {'PATH': os.pathsep.join(PATH_DIRS), 'HOME': str(HOME)},
        'RunAtLoad': True,
        'StartInterval': interval,
        'StandardOutPath': str(logs / 'keep-current.out'),
        'StandardErrorPath': str(logs / 'keep-current.err'),
    }
    plist = HOME / 'Library' / 'LaunchAgents' / f'{LABEL}.plist'
    plist.parent.mkdir(parents=True, exist_ok=True)
    plist.write_bytes(plistlib.dumps(agent))
    domain = f'gui/{os.getuid()}'
    sh(['launchctl', 'bootout', domain, str(plist)])
    code, _, err = sh(['launchctl', 'bootstrap', domain, str(plist)])
    if code:
        raise SystemExit('launchctl bootstrap failed: ' + err)
    print(json.dumps({'installed': str(plist), 'runs_every_seconds': interval, 'runs': str(source)}, indent=1))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    for name in ('run', 'install', 'status'):
        p = sub.add_parser(name)
        p.add_argument('--state', type=Path, default=DEFAULT_STATE)
        if name != 'status':
            p.add_argument('--source', type=Path, default=DEFAULT_SOURCE)
        if name == 'run':
            p.add_argument('--dry', action='store_true')
        if name == 'install':
            p.add_argument('--interval', type=int, default=3600)
    args = ap.parse_args(argv)
    if args.cmd == 'run':
        return run_once(args.source.expanduser(), args.state.expanduser(), args.dry)
    if args.cmd == 'install':
        return install(args.interval, args.source.expanduser(), args.state.expanduser())
    if not args.state.is_file():
        print('no run recorded yet')
        return 1
    print(args.state.read_text(encoding='utf-8'), end='')
    return 0 if json.loads(args.state.read_text(encoding='utf-8')).get('current') else 1


if __name__ == '__main__':
    sys.exit(main())
