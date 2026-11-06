#!/usr/bin/env python3
"""Run the same checks as CI's verify job, in the same order, from one command.

    python3 tools/verify.py            # check only; report what is stale
    python3 tools/verify.py --refresh  # rebuild generated pages first, then check
    python3 tools/verify.py --all-integrations   # also run browser, loopback, map and toolchain tests
    python3 tools/verify.py --strict-writing     # fail when changed Markdown has writing findings

The command sets the Node variables CI sets (ESTATE_NODE, ESTATE_NODE_MODULES,
NODE_PATH, PW_MODULE) when they are unset, so local results match CI instead of
failing on a missing pptxgenjs or docx module. It never installs, promotes or
records a plugin version; when the version record is stale it prints the
command to run.

The last step runs writing-diagnostics `writing_check.py`, the estate's authoritative
writing check, on Markdown under skills/, agents/ and policies/ that differs
from origin/main. Its findings are advisory unless --strict-writing is given,
because CI does not run it and a finding can be a quoted example.

Exit codes: 0 every step passed, 1 a step failed, 2 the checkout cannot be checked.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def ci_environment():
    env = dict(os.environ)
    node = env.get('ESTATE_NODE') or shutil.which('node')
    modules = env.get('ESTATE_NODE_MODULES') or str(ROOT / 'node_modules')
    if node:
        env.setdefault('ESTATE_NODE', node)
    env.setdefault('ESTATE_NODE_MODULES', modules)
    env['NODE_PATH'] = os.pathsep.join(filter(None, [modules, env.get('NODE_PATH')]))
    entry = Path(modules) / 'playwright' / 'index.mjs'
    if entry.is_file():
        env.setdefault('PW_MODULE', entry.resolve().as_uri())
    return env


def map_baseline(env):
    """CI compares the map with origin/main; use the local remote-tracking ref the same way."""
    ref = subprocess.run(['git', 'rev-parse', '--verify', '--quiet', 'refs/remotes/origin/main'],
                         cwd=ROOT, capture_output=True, text=True, env=env)
    return ref.stdout.strip() or None


def steps(args, env):
    python = sys.executable
    plan = []
    if args.refresh:
        base = map_baseline(env)
        if base:
            plan.append(('rebuild skills map', [python, 'artifacts/skills-map/build.py', '--base', base]))
        else:
            plan.append(('rebuild skills map', None))
        plan.append(('rebuild reuse review', [python, 'tools/skill_guide.py', '--report']))
        plan.append(('rebuild browse pages', [python, 'tools/browse.py']))
    plan += [
        ('browse pages current', [python, 'tools/browse.py', '--check']),
        ('validate', [python, 'tools/estate.py', 'validate']),
        ('plugin version recorded', [python, 'tools/plugin_version.py']),
    ]
    tests = [python, 'tools/run_tests.py', '--report', str(ROOT / '.local/verify-tests.json')]
    if args.all_integrations:
        tests.append('--all-integrations')
    for capability in args.integration:
        tests += ['--integration', capability]
    plan.append(('tests', tests))
    return plan


WRITING_SCOPES = ('skills/', 'agents/', 'policies/')
CHECKER = 'skills/writing-diagnostics/scripts/writing_check.py'


def changed_markdown(env):
    base = map_baseline(env)
    if not base:
        return None
    listed = subprocess.run(['git', 'diff', '--name-only', '--diff-filter=d', base, '--'],
                            cwd=ROOT, capture_output=True, text=True, env=env)
    untracked = subprocess.run(['git', 'ls-files', '--others', '--exclude-standard'],
                               cwd=ROOT, capture_output=True, text=True, env=env)
    names = set(listed.stdout.splitlines()) | set(untracked.stdout.splitlines())
    return sorted(n for n in names if n.endswith('.md') and n.startswith(WRITING_SCOPES)
                  and (ROOT / n).is_file())


def writing_step(env, strict):
    files = changed_markdown(env)
    row = {'step': 'writing check (changed Markdown)', 'advisory': not strict}
    if files is None:
        row.update(ok=not strict, output='No origin/main ref to compare with.', hint=HINTS['rebuild skills map'])
        return row
    if not files:
        row.update(ok=True, files=0, findings=0)
        return row
    done = subprocess.run([sys.executable, CHECKER, '--json', *files], cwd=ROOT, env=env,
                          capture_output=True, text=True)
    try:
        report = json.loads(done.stdout)
    except json.JSONDecodeError:
        row.update(ok=False, output=(done.stdout + done.stderr).strip()[-3000:])
        return row
    counts = {name: len(entry.get('findings', [])) for name, entry in report.items()}
    total = sum(counts.values())
    row.update(ok=not (strict and total), files=len(files), findings=total)
    if total:
        row['output'] = '\n'.join(f'{name}: {n}' for name, n in sorted(counts.items()) if n)
        row['hint'] = f'Run python3 {CHECKER} <file> to read the findings, then rewrite those sentences.'
    return row


HINTS = {
    'plugin version recorded': 'Bump "version" in config/plugin-bundles.json, then run '
                               'python3 tools/plugin_version.py --record "<change note>".',
    'browse pages current': 'Run python3 tools/verify.py --refresh, or python3 tools/browse.py.',
    'rebuild skills map': 'Fetch origin (git fetch origin main) so the map has a baseline.',
}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--refresh', action='store_true', help='Rebuild the map, reuse review and browse pages first')
    parser.add_argument('--all-integrations', action='store_true')
    parser.add_argument('--integration', action='append', default=[])
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--strict-writing', action='store_true',
                        help='Fail when changed Markdown has writing findings')
    args = parser.parse_args(argv)
    if not (ROOT / 'tools/estate.py').is_file():
        print('error: not a Skills Estate checkout', file=sys.stderr)
        return 2
    env = ci_environment()
    results = []
    for label, command in steps(args, env):
        if command is None:
            results.append({'step': label, 'ok': False, 'hint': HINTS.get(label)})
            continue
        done = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True)
        row = {'step': label, 'ok': done.returncode == 0}
        if not row['ok']:
            row['output'] = (done.stdout + done.stderr).strip()[-3000:]
            row['hint'] = HINTS.get(label)
        if label == 'tests':
            report = ROOT / '.local/verify-tests.json'
            if report.is_file():
                summary = json.loads(report.read_text())
                row['tests'] = {key: summary.get(key) for key in
                                ('executed', 'passed', 'failures', 'errors', 'deferred_count', 'status')}
        results.append(row)
    results.append(writing_step(env, args.strict_writing))
    ok = all(row['ok'] for row in results)
    if args.json:
        print(json.dumps({'ok': ok, 'steps': results}, indent=2))
    else:
        for row in results:
            line = ('PASS ' if row['ok'] else 'FAIL ') + row['step']
            if 'findings' in row:
                line += f" ({row['findings']} findings in {row['files']} files"
                line += ', advisory)' if row.get('advisory') else ')'
            if row.get('tests'):
                t = row['tests']
                line += f" ({t['passed']}/{t['executed']} passed, {t['deferred_count']} deferred, {t['status']})"
            print(line)
            if not row['ok'] or row.get('findings'):
                if row.get('output'):
                    print('  ' + row['output'].replace('\n', '\n  '))
                if row.get('hint'):
                    print('  Next: ' + row['hint'])
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
