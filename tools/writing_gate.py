#!/usr/bin/env python3
"""Hold changed Markdown to the estate writing check before it can merge.

    python3 tools/writing_gate.py --staged            # pre-commit: the staged copy of each file
    python3 tools/writing_gate.py --base origin/main  # CI and verify.py: changes since the merge base
    python3 tools/writing_gate.py FILE [FILE ...]     # named files, compared with HEAD
    python3 tools/writing_gate.py --receipt FILE      # show what a receipt still has to cover

The gate covers Markdown under skills/, agents/, policies/ and docs/. Upstream
LICENSE, NOTICE and COPYING files keep their exact text and are not checked.

A file passes when writing_check.py, run with house.json, reports nothing. It
can also pass with a receipt at .writing-receipts/<path>.json. The receipt
lists protected text, quoted exactly, with a kind and a reason. Each kind is
one of these: an exact source quotation, executable syntax, a required
identifier or a teaching example in a file about writing patterns. The gate
masks that text and runs the check again. After masking, only C24 to C27
candidates may remain, and only when the receipt retains them with a reason
and a source. No other finding can be waived.

A file that had findings before the change may keep them when the change
leaves its prose alone, as with a renamed identifier or a corrected path. Such
a change cannot add a finding, and the file stays on the clean-up list. Any
prose edit brings the whole file to a pass.

Exit codes: 0 every file passes, 1 a file fails, 2 the check could not run.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

TOOL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = TOOL_ROOT / 'skills/writing-diagnostics/scripts'
HOUSE = TOOL_ROOT / 'skills/writing-diagnostics/house.json'
SCOPES = ('skills/', 'agents/', 'policies/', 'docs/')
UPSTREAM_TEXT = re.compile(r'^(LICENSE|NOTICE|COPYING)', re.I)
RECEIPTS = '.writing-receipts'
KINDS = {'quotation', 'syntax', 'identifier', 'example'}
CANDIDATES = {'C24-formulaic-the-framing', 'C25-table-narration-candidate',
              'C26-action-basis-candidate', 'C27-reaffirmation-candidate'}

sys.path.insert(0, str(SCRIPTS))
import writing_check  # noqa: E402  (the estate checker, loaded from the writing-diagnostics skill)

CONFIG = writing_check.strict_config(HOUSE)


class GateError(Exception):
    """The gate could not read an input it needs."""


def git(root, *args, check=True):
    done = subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True)
    if check and done.returncode:
        raise GateError(done.stderr.strip() or 'git ' + ' '.join(args) + ' failed')
    return done


def in_scope(path):
    return (path.endswith('.md') and path.startswith(SCOPES)
            and not UPSTREAM_TEXT.match(Path(path).name))


def findings(text):
    found, _words = writing_check.check(text, CONFIG)
    return [item.as_dict() for item in found]


def measure(finding):
    """Size of a finding: the count its message leads with, or its samples."""
    lead = re.match(r'\s*(\d+)', finding.get('message', ''))
    return int(lead.group(1)) if lead else len(finding.get('samples') or [])


def added_findings(before, after):
    """Rules that are new or larger after the change."""
    old = {item['rule']: measure(item) for item in before}
    return sorted(item['rule'] for item in after
                  if item['rule'] not in old or measure(item) > old[item['rule']])


FENCE = re.compile(r'^\s*(```|~~~).*?^\s*\1[^\n]*$', re.M | re.S)
LINK_TARGET = re.compile(r'\]\([^)]*\)')
CODE_SPAN = re.compile(r'`[^`\n]*`')
URL = re.compile(r'https?://\S+')
IDENTIFIER = re.compile(r'\S*[A-Za-z0-9][_/.:=$~@][A-Za-z0-9]\S*|\b[A-Z0-9]+(?:_[A-Z0-9]+)+\b')


def prose_words(text):
    """The words a reader meets, without code, link targets, URLs and identifiers."""
    for pattern in (FENCE, LINK_TARGET, CODE_SPAN, URL, IDENTIFIER):
        text = pattern.sub(' ', text)
    return re.findall(r"[A-Za-z0-9][A-Za-z0-9'’-]*", text.lower())


def mask(text, protected):
    """Replace protected text the way prose_check treats quoted material."""
    for number, item in enumerate(sorted(protected, key=lambda i: -len(i['text'])), 1):
        value = item['text']
        whole_lines = re.search(r'(^|\n)' + re.escape(value) + r'(\n|$)', text)
        if whole_lines:
            replacement = '\n' * value.count('\n')
        else:
            replacement = ' qzxprotected' + ''.join(chr(97 + int(d)) for d in str(number)) + ' '
        text = text.replace(value, replacement)
    return text


def check_receipt(root, path, text, remaining):
    """Problems with the receipt for PATH, or None when it accounts for every finding."""
    receipt_path = Path(root) / RECEIPTS / (path + '.json')
    if not receipt_path.is_file():
        return ['no receipt at ' + receipt_path.relative_to(root).as_posix()]
    try:
        receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        return ['unreadable receipt: ' + str(exc)]
    problems = []
    if receipt.get('format') != 1 or receipt.get('artifact') != path:
        problems.append('the receipt must use format 1 and name ' + path)
    protected = receipt.get('protected', [])
    candidates = receipt.get('candidates', [])
    if not isinstance(protected, list) or not isinstance(candidates, list):
        return problems + ['protected and candidates must be lists']
    for item in protected:
        if (not isinstance(item, dict) or item.get('kind') not in KINDS
                or not str(item.get('reason', '')).strip() or not isinstance(item.get('text'), str)
                or not item['text'].strip()):
            problems.append('each protected entry needs a kind (' + ', '.join(sorted(KINDS)) +
                            '), a reason and the exact text')
        elif item['text'] not in text:
            problems.append('protected text is not in the file: ' + item['text'][:60])
    if problems:
        return problems
    after = findings(mask(text, protected))
    retained = {}
    for item in candidates:
        if (not isinstance(item, dict) or item.get('rule') not in CANDIDATES
                or not str(item.get('reason', '')).strip() or not str(item.get('source', '')).strip()):
            problems.append('a retained candidate needs a C24 to C27 rule, a reason and a source')
        else:
            retained[item['rule']] = item
    for rule in sorted(set(retained) - {item['rule'] for item in after}):
        problems.append('stale retention: ' + rule + ' no longer appears')
    left = sorted(item['rule'] for item in after if item['rule'] not in retained)
    if left:
        problems.append('findings outside protected text: ' + ', '.join(left))
    return problems or None


def judge(root, path, before, after):
    """Return (passed, note) for one file."""
    now = findings(after)
    if not now:
        return True, 'clean'
    problems = check_receipt(root, path, after, now)
    if problems is None:
        return True, 'clean with a receipt'
    rules = ', '.join(item['rule'] for item in now)
    if before is not None and findings(before):
        if prose_words(before) == prose_words(after):
            grown = added_findings(findings(before), now)
            if not grown:
                return True, 'older findings kept by a change outside the prose; on the clean-up list (' + rules + ')'
            return False, 'the change adds findings: ' + ', '.join(grown)
        return False, 'a prose edit needs a full pass; findings: ' + rules + '; ' + '; '.join(problems)
    return False, 'findings: ' + rules + '; ' + '; '.join(problems)


def name_status(root, *args):
    """Changed paths mapped to their earlier names, so a renamed file keeps its history."""
    fields = git(root, 'diff', '--name-status', '-M', '--diff-filter=ACMR', '-z', *args).stdout.split('\0')
    changes, index = {}, 0
    while index < len(fields) and fields[index]:
        status = fields[index]
        if status.startswith(('R', 'C')):
            changes[fields[index + 2]] = fields[index + 1]
            index += 3
        else:
            changes[fields[index + 1]] = fields[index + 1]
            index += 2
    return changes


def staged_files(root):
    return name_status(root, '--cached')


def changed_since(root, base):
    merge_base = git(root, 'merge-base', base, 'HEAD').stdout.strip()
    changes = name_status(root, merge_base)
    untracked = git(root, 'ls-files', '--others', '--exclude-standard', '-z').stdout.split('\0')
    changes.update({n: n for n in untracked if n})
    return merge_base, changes


def show(root, revision, path):
    done = git(root, 'show', revision + ':' + path, check=False)
    return done.stdout if done.returncode == 0 else None


def with_receipt_targets(changes):
    """A changed receipt puts its file under the gate too."""
    targets = dict(changes)
    for name in changes:
        if name.startswith(RECEIPTS + '/') and name.endswith('.json'):
            target = name[len(RECEIPTS) + 1:-len('.json')]
            targets.setdefault(target, target)
    return {n: old for n, old in sorted(targets.items()) if in_scope(n)}


def run(root, mode, base=None, files=()):
    root = Path(root)
    if mode == 'staged':
        changes, before_rev = staged_files(root), 'HEAD'
        read_after = lambda n: show(root, '', n)  # an empty revision reads the index
    elif mode == 'base':
        before_rev, changes = changed_since(root, base)
        read_after = lambda n: (root / n).read_text(encoding='utf-8') if (root / n).is_file() else None
    else:
        changes, before_rev = {n: n for n in files}, 'HEAD'
        read_after = lambda n: (root / n).read_text(encoding='utf-8')
    results = []
    for name, earlier in with_receipt_targets(changes).items():
        after = read_after(name)
        if after is None:
            continue
        passed, note = judge(root, name, show(root, before_rev, earlier), after)
        results.append({'path': name, 'passed': passed, 'note': note})
    return results


def describe_receipt(root, path):
    """The findings a receipt for PATH must cover, before and after its protected text is masked."""
    text = (Path(root) / path).read_text(encoding='utf-8')
    receipt_path = Path(root) / RECEIPTS / (path + '.json')
    protected = []
    if receipt_path.is_file():
        protected = json.loads(receipt_path.read_text(encoding='utf-8')).get('protected', [])
    return {'artifact': path, 'findings': findings(text),
            'after_masking': findings(mask(text, [p for p in protected if p.get('text') in text])),
            'problems': check_receipt(root, path, text, None) or []}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('files', nargs='*')
    parser.add_argument('--root', type=Path, default=TOOL_ROOT)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--staged', action='store_true')
    group.add_argument('--base')
    group.add_argument('--receipt')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    try:
        if args.receipt:
            print(json.dumps(describe_receipt(args.root, args.receipt), indent=2, ensure_ascii=False))
            return 0
        mode = 'staged' if args.staged else 'base' if args.base else 'files'
        if mode == 'files' and not args.files:
            parser.error('name files, or use --staged or --base')
        results = run(args.root, mode, args.base, args.files)
    except (GateError, OSError, ValueError, SyntaxError, RecursionError) as exc:
        print('Writing gate could not run: ' + str(exc), file=sys.stderr)
        return 2
    failed = [r for r in results if not r['passed']]
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for row in results:
            print(('pass  ' if row['passed'] else 'FAIL  ') + row['path'] + ': ' + row['note'])
        print(f'Writing gate: {len(results)} file(s) checked, {len(failed)} failed.')
        if failed:
            print('Run python3 skills/writing-diagnostics/scripts/writing_check.py --config '
                  'skills/writing-diagnostics/house.json FILE to read the findings. '
                  'policies/skill-standard.md explains receipts.')
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
