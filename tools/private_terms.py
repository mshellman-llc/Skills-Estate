#!/usr/bin/env python3
"""Keep configured private names out of every tracked text file.

    python3 tools/private_terms.py            # every tracked file except generated plugins/
    python3 tools/private_terms.py --staged   # the staged copy of each changed file

The names stay outside the repository. Supply them as a JSON list of strings,
either in ESTATE_PRIVATE_TERMS, which is how CI reads the repository secret of
that name, or in the file that ESTATE_PRIVATE_TERMS_FILE names. With neither set,
the check reports that it was skipped and exits 0.

Matches are case-insensitive. A report gives the path, the line and the term's
position in the list, never the term itself, so CI logs stay clean.

Exit codes: 0 no match or no terms, 1 a match, 2 the terms or files could not be read.
"""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ('plugins/',)


def load_terms(environ=os.environ):
    raw = environ.get('ESTATE_PRIVATE_TERMS', '').strip()
    if not raw and environ.get('ESTATE_PRIVATE_TERMS_FILE'):
        raw = Path(environ['ESTATE_PRIVATE_TERMS_FILE']).read_text(encoding='utf-8')
    if not raw:
        return None
    terms = json.loads(raw)
    if not isinstance(terms, list) or not terms or any(not isinstance(t, str) or not t.strip() for t in terms):
        raise ValueError('Private terms must be a JSON array of nonempty strings')
    return terms


def git(root, *args):
    done = subprocess.run(['git', '-C', str(root), *args], capture_output=True)
    if done.returncode:
        raise OSError(done.stderr.decode(errors='replace').strip())
    return done.stdout


def candidates(root, staged):
    if staged:
        names = git(root, 'diff', '--cached', '--name-only', '--diff-filter=ACMR', '-z').decode().split('\0')
        return [(n, lambda n=n: git(root, 'show', ':' + n)) for n in names if n]
    names = git(root, 'ls-files', '-z').decode().split('\0')
    return [(n, lambda n=n: (Path(root) / n).read_bytes()) for n in names
            if n and not n.startswith(GENERATED) and (Path(root) / n).is_file()]


def scan(root, terms, staged=False):
    patterns = [re.compile(re.escape(term), re.I) for term in terms]
    hits = []
    for name, read in candidates(root, staged):
        data = read()
        if b'\0' in data:
            continue
        text = data.decode('utf-8', errors='replace')
        for number, pattern in enumerate(patterns, 1):
            if pattern.search(name):
                hits.append((name, 0, number))
        for line_number, line in enumerate(text.splitlines(), 1):
            for number, pattern in enumerate(patterns, 1):
                if pattern.search(line):
                    hits.append((name, line_number, number))
    return hits


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--staged', action='store_true')
    args = parser.parse_args(argv)
    try:
        terms = load_terms()
        if terms is None:
            print('Private terms check skipped: neither ESTATE_PRIVATE_TERMS nor ESTATE_PRIVATE_TERMS_FILE is set.')
            return 0
        hits = scan(args.root, terms, args.staged)
    except (OSError, ValueError) as exc:
        print('Private terms check could not run: ' + str(exc), file=sys.stderr)
        return 2
    for name, line, number in hits:
        where = name + (':' + str(line) if line else ' (path)')
        print(f'{where}: private term #{number}')
    print(f'Private terms check: {len(hits)} match(es) for {len(terms)} configured term(s).')
    return 1 if hits else 0


if __name__ == '__main__':
    raise SystemExit(main())
