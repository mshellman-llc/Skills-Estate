#!/usr/bin/env python3
"""Show release-review state and record the owner's approvals in one step.

    python3 tools/release_review.py status [--json]
    python3 tools/release_review.py accept --approved-by "Megan Shellman" \\
        --evidence "Reviewed PR #35 diff and CI run" (--module NAME ... | --router NAME ... |
        --shared | --bundle estate-delivery ... | --stale)

`status` lists every module, router and the shared assembly as current,
stale (accepted for different bytes) or pending, with the digest a new
approval would record.

`accept` writes `accepted`, the current digest and a dated evidence line for
the named subjects only. It records an approval the owner gave; it does not
decide one. It refuses without --approved-by and --evidence, and it never
accepts subjects nobody named: `--bundle` covers the modules and router that
bundle packages, and `--stale` covers subjects that were accepted before and
changed since. Pending subjects that were never accepted must be named.

Exit codes: 0 done (status: nothing awaits review), 1 status found subjects
awaiting review, 2 invalid request.
"""
import argparse
import datetime as dt
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import estate  # noqa: E402
import plugins  # noqa: E402

SETTINGS = 'config/plugin-bundles.json'


def load(root):
    return json.loads((root / SETTINGS).read_text())


def digests(root, settings):
    rows = {('shared', 'shared assembly'): plugins.shared_hash(root, settings)}
    for name in settings['release']['modules']:
        rows[('module', name)] = estate.tree_hash(root / 'skills' / name)
    for name in settings['release']['routers']:
        rows[('router', name)] = estate.sha((root / 'agents' / f'{name}.md').read_bytes())
    return rows


def record(settings, kind, name):
    release = settings['release']
    return release['shared'] if kind == 'shared' else release[kind + 's'][name]


def state(review, digest):
    if review.get('status') == 'accepted' and review.get('reviewed_sha256') == digest and review.get('evidence'):
        return 'current'
    if review.get('reviewed_sha256'):
        return 'stale'
    return 'pending'


def status(root):
    settings = load(root)
    rows = []
    for (kind, name), digest in digests(root, settings).items():
        rows.append({'kind': kind, 'name': name, 'state': state(record(settings, kind, name), digest),
                     'current_sha256': digest})
    return rows


def bundle_subjects(root, settings, bundle):
    if bundle not in settings['bundles']:
        raise ValueError('Unknown bundle: ' + bundle)
    item = settings['bundles'][bundle]
    manifest = estate.build(root)
    subjects = {('module', name) for name in plugins.required_modules(root, item, manifest)}
    if item.get('router_source'):
        subjects.add(('router', Path(item['router_source']).stem))
    return subjects


def accept(root, subjects, approved_by, evidence, today=None):
    if not approved_by.strip() or not evidence.strip():
        raise ValueError('Name who approved and what they reviewed (--approved-by, --evidence)')
    if not subjects:
        raise ValueError('Name at least one subject to accept')
    settings = load(root)
    current = digests(root, settings)
    unknown = sorted(f'{k} {n}' for k, n in subjects if (k, n) not in current)
    if unknown:
        raise ValueError('Not release subjects: ' + ', '.join(unknown))
    stamp = (today or dt.date.today()).isoformat()
    line = f'Owner approval by {approved_by.strip()} on {stamp}. Basis: {evidence.strip()}'
    changed = []
    for kind, name in sorted(subjects):
        review = record(settings, kind, name)
        digest = current[(kind, name)]
        if state(review, digest) == 'current':
            continue
        review.clear()
        review.update({'status': 'accepted', 'reviewed_sha256': digest, 'evidence': line})
        changed.append({'kind': kind, 'name': name, 'sha256': digest})
    path = root / SETTINGS
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + '\n')
    temporary.replace(path)
    return changed


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--root', type=Path, default=ROOT)
    sub = parser.add_subparsers(dest='command', required=True)
    show = sub.add_parser('status')
    show.add_argument('--json', action='store_true')
    take = sub.add_parser('accept')
    take.add_argument('--approved-by', required=True)
    take.add_argument('--evidence', required=True)
    take.add_argument('--module', action='append', default=[])
    take.add_argument('--router', action='append', default=[])
    take.add_argument('--bundle', action='append', default=[])
    take.add_argument('--shared', action='store_true')
    take.add_argument('--stale', action='store_true', help='Every previously accepted subject whose bytes changed')
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.command == 'status':
            rows = status(root)
            waiting = [r for r in rows if r['state'] != 'current']
            if args.json:
                print(json.dumps({'subjects': rows, 'awaiting_review': len(waiting)}, indent=2))
            else:
                counts = {s: sum(1 for r in rows if r['state'] == s) for s in ('current', 'stale', 'pending')}
                print(f"{counts['current']} current, {counts['stale']} stale, {counts['pending']} pending")
                for r in waiting:
                    print(f"- {r['state']:7} {r['kind']:6} {r['name']}  {r['current_sha256']}")
            return 1 if waiting else 0
        settings = load(root)
        subjects = {('module', n) for n in args.module} | {('router', n) for n in args.router}
        if args.shared:
            subjects.add(('shared', 'shared assembly'))
        for bundle in args.bundle:
            subjects |= bundle_subjects(root, settings, bundle)
        if args.stale:
            subjects |= {(r['kind'], r['name']) for r in status(root) if r['state'] == 'stale'}
        changed = accept(root, subjects, args.approved_by, args.evidence)
        print(json.dumps({'accepted': changed}, indent=2))
        return 0
    except (ValueError, KeyError, OSError) as error:
        print(f'error: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
