#!/usr/bin/env python3
"""Copy writing corrections saved in the Knowledge Hub into corrections.md.

    sync_corrections.py [--rules-dir DIR] [--hub-db FILE] [--apply] [--seed ID ...] [--json]

A correction made in Claude.ai or ChatGPT reaches the Hub through save_update,
kind decision, with a key that starts writing-correction. Until it is copied
into corrections.md in the rules folder it has not reached the rules. This
script reads the Hub's database read-only, finds every such decision and adds
one row to the Log table of corrections.md for each one not yet copied.

A row records the date, the start of the correction, the channel and audience
when the record states them, the rule IDs it names, "candidate" for the
pattern, and "Hub decision N" with the tool. Each row ends with the marker
`hub:N`, and a decision whose ID appears as `hub:N` or as "Hub decision N"
anywhere in corrections.md is never copied again. Corrections copied by hand
before this script ran can be marked with --seed ID; the IDs are saved to
.hub-corrections.json beside corrections.md on that run, with or without --apply.

Without --apply the script only lists the rows it would add to corrections.md. The Hub database is
opened read-only and never changed. Standard library only.
"""
import argparse
import datetime as dt
import json
import os
import re
import sqlite3
import sys
from pathlib import Path

DEFAULT_DB = Path.home() / 'Library' / 'Application Support' / 'beastmode-hub-v2' / 'hub.sqlite'
STATE = '.hub-corrections.json'
LOG_HEADING = '## Log'
RULE = re.compile(r'\b[A-Z]{1,2}\d{1,3}\b')
KEY_DATE = re.compile(r'writing-correction[:-](?:.*?)(\d{4}-\d{2}-\d{2})')
CHANNEL = re.compile(r'(?:Channel and audience|Channel)\s*:\s*(.+?)(?=\.(?:\s|$)|\n|$)', re.I)
TOOL = re.compile(r'\bTool\s*:\s*(.+?)(?=\.(?:\s|$)|\n|$)', re.I)
COPIED = re.compile(r'(?:\bhub:|Hub decisions? )(\d+(?:(?:, | and )\d+)*)')
SUMMARY_CHARS = 280


def rules_home(arg):
    for value in (arg, os.environ.get('WRITING_HOME')):
        if value:
            return Path(value).expanduser()
    pointer = Path.home() / '.agents' / 'writing' / 'home'
    if pointer.is_file():
        return Path(pointer.read_text(encoding='utf-8').strip()).expanduser()
    raise SystemExit('no rules folder: pass --rules-dir, set WRITING_HOME or write the path in ~/.agents/writing/home')


def hub_corrections(db):
    """Writing corrections in the Hub, oldest first: id, key, project, body, actor, at."""
    uri = Path(db).expanduser().resolve().as_uri() + '?mode=ro'
    with sqlite3.connect(uri, uri=True) as conn:
        rows = conn.execute(
            "SELECT u.id, r.key, u.project_id, u.body, u.actor, u.at FROM receipts r "
            "JOIN updates u ON u.id = r.record_id "
            "WHERE r.record_table = 'updates' AND r.key LIKE 'writing-correction%' AND u.kind = 'decision' "
            "ORDER BY u.id").fetchall()
    return [dict(zip(('id', 'key', 'project', 'body', 'actor', 'at'), row)) for row in rows]


def copied_ids(text, state):
    ids = set(state)
    for match in COPIED.finditer(text):
        ids.update(int(n) for n in re.findall(r'\d+', match.group(1)))
    return ids


def cell(text):
    return ' '.join(str(text).replace('|', '/').split())


def summary(body):
    text = ' '.join(body.split())
    if len(text) <= SUMMARY_CHARS:
        return text
    cut = text[:SUMMARY_CHARS]
    stop = max(cut.rfind('. '), cut.rfind('; '))
    return (cut[:stop + 1] if stop > SUMMARY_CHARS // 2 else cut.rsplit(' ', 1)[0]) + ' (continues in the Hub)'


def row(item):
    match = KEY_DATE.search(item['key'] or '')
    date = match.group(1) if match else str(item['at'])[:10]
    channel = CHANNEL.search(item['body'])
    tool = TOOL.search(item['body'])
    rules = sorted(set(RULE.findall(item['body'])), key=lambda r: (r[0], int(re.sub(r'\D', '', r))))
    cells = [date, summary(item['body']),
             channel.group(1).strip() if channel else 'see the Hub record',
             ', '.join(rules) if rules else 'none yet',
             'candidate',
             f'Hub decision {item["id"]} ({tool.group(1).strip() if tool else item["actor"]}) hub:{item["id"]}']
    return '| ' + ' | '.join(cell(c) for c in cells) + ' |'


def insert_rows(text, rows):
    """Add rows at the end of the table under the Log heading."""
    lines = text.split('\n')
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == LOG_HEADING)
    except StopIteration:
        raise SystemExit(f'corrections.md has no "{LOG_HEADING}" heading')
    last = None
    for i in range(start + 1, len(lines)):
        if lines[i].startswith('## '):
            break
        if lines[i].startswith('|'):
            last = i
    if last is None:
        raise SystemExit('the Log section of corrections.md has no table')
    return '\n'.join(lines[:last + 1] + rows + lines[last + 1:])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--rules-dir')
    ap.add_argument('--hub-db', default=os.environ.get('HUB_DB_FILE') or str(DEFAULT_DB))
    ap.add_argument('--apply', action='store_true', help='write corrections.md; without it, list what would be added')
    ap.add_argument('--seed', type=int, nargs='+', default=[], help='Hub decision IDs already copied by hand')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args(argv)
    home = rules_home(args.rules_dir)
    target, state_file = home / 'corrections.md', home / STATE
    if not target.is_file():
        raise SystemExit(f'{target} does not exist')
    state = json.loads(state_file.read_text(encoding='utf-8')).get('copied', []) if state_file.is_file() else []
    if args.seed:   # saved at once: a seed only marks IDs and never writes corrections.md
        state = sorted(set(state) | set(args.seed))
        state_file.write_text(json.dumps({'copied': state}, indent=1) + '\n', encoding='utf-8')
    if not Path(args.hub_db).expanduser().is_file():
        raise SystemExit(f'Hub database not found: {args.hub_db}')
    text = target.read_text(encoding='utf-8')
    done = copied_ids(text, state)
    pending = [c for c in hub_corrections(args.hub_db) if c['id'] not in done]
    rows = [row(c) for c in pending]
    if rows and args.apply:
        text = insert_rows(text, rows)
        text = re.sub(r'^updated: .*$', f'updated: {dt.date.today().isoformat()}', text, count=1, flags=re.M)
        target.write_text(text, encoding='utf-8')
    report = {'corrections_md': str(target), 'applied': bool(args.apply and rows),
              'already_copied': sorted(done), 'added' if args.apply else 'would_add':
              [{'hub_id': c['id'], 'key': c['key'], 'project': c['project']} for c in pending]}
    if args.json:
        print(json.dumps(report, indent=1))
    else:
        verb = 'Added' if args.apply else 'Would add'
        print(f'{verb} {len(rows)} corrections to {target}')
        for c, r in zip(pending, rows):
            print(f'  hub {c["id"]} {c["key"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
