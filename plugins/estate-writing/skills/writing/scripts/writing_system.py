#!/usr/bin/env python3
"""Build, check and report on the copies of the owner's writing rules.

    writing_system.py build   [--rules-dir DIR] [--preferences FILE] [--out DIR]
    writing_system.py check   [--rules-dir DIR] [--out DIR] [--living FILE ...] [--json]
    writing_system.py nightly [--rules-dir DIR] [--since HOURS] [--weekly] [--json]

build writes, from the rules folder and the Writing section of preferences.md:

    <out>/core/core.md                         the core every chat loads, with the habits that recur
                                               and before-and-after pairs from corrections.md
    <out>/claude-ai/style.txt                  the same core, shaped as a Claude custom style
    <out>/claude-ai-skill/<name>/SKILL.md      the full rules, for hosts that cannot reach the drive
    <out>/chatgpt/custom-instructions.txt      ChatGPT's two boxes: chatgpt-about.md (beside the rules
                                               folder) in the 1,500-character one, and rules.md then
                                               voice-profile.md, word for word and in order, in the
                                               5,000-character one until it is full

Each output opens with a stamp naming the sha256 of its sources. A copy is never
edited by hand; change the sources and build again.

check lists every living file that still carries wording retired in
retired-wording.json (in the rules folder), and every built copy whose stamp no
longer matches its sources. Exit 1 when it finds either.

nightly scans deliverables changed in the last --since hours with check.py, and
with --weekly adds hit counts per tool, gate releases, corrections logged and the
habits that recur. It prints JSON for the nightly scan's report.

Standard library only.
"""
import argparse
import datetime as dt
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import hook  # noqa: E402  one gate config and one deliverable test for the hook and the nightly scan

CHECK = HERE / 'check.py'
AGENT = Path(os.environ.get('WRITING_AGENT_HOME') or Path.home() / '.agents' / 'writing').expanduser()
HITS = [AGENT / 'hits.jsonl', Path.home() / '.agents' / 'humanize' / 'hits.jsonl']
STAMP = re.compile(r'sources sha256 ([0-9a-f]{12})')
SKILL_NAME = 'megan-writing-style'
CHATGPT_LIMIT = 5000        # "Custom instructions" box
CHATGPT_ABOUT_LIMIT = 1500  # "More about you" box
CHATGPT_RULES = ('My writing rules apply to everything you write for me or my readers, chat replies included. '
                 'Code and exact quotations are exempt. My correction in the current chat outranks them. '
                 'Apply them silently. The full set is in 05-ai-context/writing/rules.md and voice-profile.md; '
                 'read both through BeastMode\'s read_file before writing anything I will keep or send, '
                 'because this box holds only the rules that fit.')
SKILL_DESCRIPTION = ("Megan's full writing rules and voice profile, bundled for hosts that cannot reach her drive or "
                     "the Knowledge Hub. Read before writing anything she or her readers will see.")
DEFAULT_LIVING = [
    '{drive}/05-ai-context/preferences.md', '{drive}/05-ai-context/ways-of-working.md',
    '{drive}/05-ai-context/generated/claude-ai/project-instructions.txt',
    '{drive}/05-ai-context/generated/claude-code/CLAUDE.md', '{drive}/05-ai-context/generated/codex/AGENTS.md',
    '{drive}/05-ai-context/generated/chatgpt/custom-instructions.txt',
    '{drive}/80-system/beastmode-rebuild/work/paste-instructions-v001.md',
    '{home}/.claude/CLAUDE.md', '{home}/.codex/AGENTS.md',
]


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def rules_home(arg):
    if arg:
        return Path(arg).expanduser()
    if os.environ.get('WRITING_HOME'):
        return Path(os.environ['WRITING_HOME']).expanduser()
    pointer = Path(os.environ.get('WRITING_POINTER') or Path.home() / '.agents' / 'writing' / 'home')
    if pointer.is_file():
        return Path(pointer.read_text(encoding='utf-8').strip()).expanduser()
    sys.exit('no rules folder: pass --rules-dir, set WRITING_HOME or write the path to ~/.agents/writing/home')


def body(text):
    """Text without its YAML front matter."""
    return re.sub(r'^---\n.*?\n---\n', '', text, flags=re.S)


def section(text, title):
    """The body of a '## title' section, without its heading."""
    m = re.search(r'^## ' + re.escape(title) + r'\s*$(.*?)(?=^## |\Z)', text, re.M | re.S)
    return m.group(1).strip() if m else ''


def rule_lines(rules_md):
    out = {}
    for m in re.finditer(r'^- ([A-Z]\d+)\. (.+)$', rules_md, re.M):
        out[m.group(1)] = m.group(2).strip()
    return out


def corrections(path):
    rows = []
    if not path.is_file():
        return rows
    for line in path.read_text(encoding='utf-8').splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) >= 6 and re.fullmatch(r'\d{4}-\d{2}-\d{2}', cells[0]):
            rows.append({'date': cells[0], 'what': cells[1], 'channel': cells[2], 'rule': cells[3],
                         'pattern': cells[4], 'tool': cells[5]})
    return rows


def pairs(rows, rules, limit=10):
    """Habit and fix: each logged correction that quotes the words, with the rule it broke."""
    out, seen = [], set()
    for row in reversed(rows):
        quotes = [m.group(1) for m in re.finditer(r'"([^"]{6,120})"', row['what'])
                  if not re.search(r'\b(?:as|read as|means)\s*$', row['what'][:m.start()])]
        ids = re.findall(r'\b[A-Z]\d+\b', row['rule'])
        if not quotes or not ids or ids[0] not in rules or quotes[0] in seen:
            continue
        seen.add(quotes[0])
        out.append((quotes[0], ids[0], rules[ids[0]]))
        if len(out) == limit:
            break
    return out


def judged_rules(ledger):
    return {r.get('id') for r in ledger.get('rules', []) if r.get('judge') == 'line-pass'}


def recurring(ledger, days=14, top=3):
    skip = judged_rules(ledger)
    repairs = {r.get('id'): r.get('repair', '') for r in ledger.get('rules', [])}
    since = (dt.date.today() - dt.timedelta(days=days)).isoformat()
    counts = {}
    for path in HITS:
        if not path.is_file():
            continue
        with open(path, encoding='utf-8') as f:
            for line in f:
                try:
                    h = json.loads(line)
                except ValueError:
                    continue
                rule = h.get('rule')
                if rule and rule not in skip and rule in repairs and h.get('d', '') >= since \
                        and h.get('src') in ('reply', 'file'):
                    counts[rule] = counts.get(rule, 0) + 1
    out, seen = [], set()
    for rule, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        habit = re.sub(r'\W+', ' ', repairs[rule].lower())[:30]
        if habit in seen:
            continue
        seen.add(habit)
        out.append((rule, n, repairs[rule]))
        if len(out) == top:
            break
    return out


def sources_sha(*paths):
    return sha_bytes(b''.join(Path(p).read_bytes() for p in paths if Path(p).is_file()))[:12]


def built_copies(home, out, prefs):
    """Each built copy and the source files its stamp hashes, in stamp order."""
    core = [prefs, home / 'rules.md', home / 'corrections.md', home / 'patterns.json']
    copies = {out / 'core' / 'core.md': core, out / 'claude-ai' / 'style.txt': core,
              out / 'claude-ai-skill' / SKILL_NAME / 'SKILL.md': [home / 'rules.md', home / 'voice-profile.md']}
    about = home.parent / 'chatgpt-about.md'
    if about.is_file():
        copies[out / 'chatgpt' / 'custom-instructions.txt'] = [about, home / 'rules.md', home / 'voice-profile.md']
    return copies


def stamp(digest, sources):
    return (f'Built by writing_system.py on {dt.date.today().isoformat()} from {", ".join(sources)}; '
            f'sources sha256 {digest}. Edit the sources and build again; never edit this copy by hand.')


def fill(head, items, limit=CHATGPT_LIMIT):
    """Add items to head, one per line, while the text stays within limit. Returns the text and what is left."""
    text, rest = head, list(items)
    while rest and len(text) + 1 + len(rest[0]) <= limit:
        text += '\n' + rest.pop(0)
    return text, rest


def chatgpt_boxes(about, rules_md, voice_md):
    """The about text alone in one box; the rules in order, then the voice, in the other until it is full.
    Each line keeps its rule ID, because some rules cite others by ID. Returns both boxes and the IDs left out."""
    pattern = r'^- ([A-Z]\d+)\. (.+)$'
    items = [m.group(1) + '. ' + m.group(2).strip() for m in re.finditer(pattern, rules_md, re.M)]
    voice = [m.group(1) + '. ' + m.group(2).strip() for m in re.finditer(pattern, voice_md, re.M)]
    box1 = about.strip()
    if len(box1) > CHATGPT_ABOUT_LIMIT:
        sys.exit(f'chatgpt-about.md is {len(box1)} characters; ChatGPT allows {CHATGPT_ABOUT_LIMIT}')
    box2, left = fill(CHATGPT_RULES, items + (['When writing as me:'] + voice if voice else []))
    return box1, box2, [item.split('.')[0] for item in left if item != 'When writing as me:']


def build(args):
    home = rules_home(args.rules_dir)
    prefs = Path(args.preferences or home.parent / 'preferences.md')
    out = Path(args.out or home.parent / 'generated')
    rules_md = (home / 'rules.md').read_text(encoding='utf-8')
    ledger = json.loads((home / 'patterns.json').read_text(encoding='utf-8'))
    writing = section(prefs.read_text(encoding='utf-8'), 'Writing')
    if not writing:
        sys.exit(f'no "## Writing" section in {prefs}')
    copies = built_copies(home, out, prefs)

    def stamp_for(path):  # the stamp always names the preferences source preferences.md
        names = ['preferences.md' if p == prefs else p.name for p in copies[path]]
        return stamp(sources_sha(*copies[path]), names)

    core_path, style_path = out / 'core' / 'core.md', out / 'claude-ai' / 'style.txt'
    skill_path, chat_path = out / 'claude-ai-skill' / SKILL_NAME / 'SKILL.md', out / 'chatgpt' / 'custom-instructions.txt'
    rules = rule_lines(rules_md)
    habits = recurring(ledger)
    examples = pairs(corrections(home / 'corrections.md'), rules)
    core = [f'<!-- {stamp_for(core_path)} -->', '', '# Writing core', '', writing, '']
    if habits:
        core += ['## Habits that recur', '']
        core += [f'- {rule}, {n} times in 14 days. {repair}' for rule, n, repair in habits]
        core.append('')
    if examples:
        core += ['## Corrections she made', '']
        core += [f'- "{quote}" broke {rid}: {text}' for quote, rid, text in examples]
        core.append('')
    style = [stamp_for(style_path), '', 'Write every reply and document by these rules.', '', writing]
    if examples:
        style += ['', 'Corrections she has made, with the rule each one broke:']
        style += [f'- "{quote}" broke {rid}: {text}' for quote, rid, text in examples]
    voice = home / 'voice-profile.md'
    skill = ['---', f'name: {SKILL_NAME}', f'description: "{SKILL_DESCRIPTION}"', '---', '',
             f'<!-- {stamp_for(skill_path)} -->', '',
             '# Megan\'s writing rules', '',
             'Use these rules when the Knowledge Hub and her drive cannot be reached. When either can, the rules '
             'folder on the drive is newer and wins. Apply them without mentioning which copy you used.', '',
             '## Rules', '', body(rules_md).strip(), '']
    voice_text = voice.read_text(encoding='utf-8') if voice.is_file() else ''
    if voice.is_file():
        skill += ['## Voice when she is the author', '', body(voice_text).strip(), '']
    outputs = [(core_path, '\n'.join(core)), (style_path, '\n'.join(style) + '\n'), (skill_path, '\n'.join(skill))]
    left_out = None
    if chat_path in copies:
        about_text = body(copies[chat_path][0].read_text(encoding='utf-8'))
        box1, box2, left_out = chatgpt_boxes(about_text, rules_md, voice_text)
        outputs.append((chat_path, '\n'.join([stamp_for(chat_path), '', '=== Box 1: More about you ===', '', box1, '',
                                              '=== Box 2: Custom instructions ===', '', box2, ''])))
    written = []
    for path, text in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text if text.endswith('\n') else text + '\n', encoding='utf-8')
        written.append(str(path))
    print(json.dumps({'written': written, 'sources_sha256': sources_sha(*copies[core_path]),
                      'habits': [h[0] for h in habits], 'pairs': len(examples), 'style_chars': len('\n'.join(style)),
                      'chatgpt_left_out': left_out}, indent=1))
    return 0


def living_files(args):
    drive = os.environ.get('BEASTMODE_MAC_ROOT', '/Volumes/BeastMode')
    paths = args.living or [p.format(drive=drive, home=str(Path.home())) for p in DEFAULT_LIVING]
    return [Path(p) for p in paths]


def check(args, quiet=False):
    home = rules_home(args.rules_dir)
    out = Path(args.out or home.parent / 'generated')
    retired = json.loads((home / 'retired-wording.json').read_text(encoding='utf-8')) \
        if (home / 'retired-wording.json').is_file() else []
    stale = []
    for path in living_files(args):
        if not path.is_file():
            continue
        text = path.read_text(encoding='utf-8', errors='replace')
        for item in retired:
            if item['text'] in text:
                stale.append({'path': str(path), 'text': item['text'], 'replaced_by': item.get('replaced_by', '')})
    expected = {path: sources_sha(*sources)
                for path, sources in built_copies(home, out, home.parent / 'preferences.md').items()}
    outdated = []
    for path, digest in expected.items():
        m = STAMP.search(path.read_text(encoding='utf-8')) if path.is_file() else None
        if not m or m.group(1) != digest:
            outdated.append({'path': str(path), 'built_from': m.group(1) if m else None, 'sources_now': digest})
    result = {'retired_wording': stale, 'outdated_copies': outdated, 'ok': not stale and not outdated}
    if not quiet:
        print(json.dumps(result, indent=1) if args.json else
              ('ok' if result['ok'] else '\n'.join([f'retired wording in {s["path"]}: {s["text"]}' for s in stale]
                                                   + [f'outdated copy: {o["path"]}' for o in outdated])))
    return result


def roots(cfg, depth=4):
    """Directories to walk. A pattern such as /drive/*/artifacts/* is found with glob at one to four levels,
    so the walk never lists the whole drive."""
    out = set()
    for pat in cfg['include']:
        m = re.match(r'^(.*?)/\*/([^*?\[]+)/\*$', pat)
        if m:
            for level in range(1, depth + 1):
                out.update(Path(p) for p in glob.glob(m.group(1) + '/*' * level + '/' + m.group(2)))
            continue
        prefix = re.split(r'[*?\[]', pat)[0]
        out.add(Path(prefix if prefix.endswith('/') else os.path.dirname(prefix)))
    return sorted(out)


def nightly(args):
    cfg = hook.gate_config()
    since = time.time() - args.since * 3600
    scanned, failing = 0, []
    for root in roots(cfg):
        if not root.is_dir():
            continue
        for parent, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('node_modules', 'archive')]
            for name in files:
                path = Path(parent) / name
                text = str(path)
                if not hook.is_deliverable(path, cfg):
                    continue
                try:
                    if path.stat().st_mtime < since:
                        continue
                except OSError:
                    continue
                scanned += 1
                try:
                    res = json.loads(subprocess.run([sys.executable, str(CHECK), '--file', text, '--json',
                                                     '--receipt-dir', str(AGENT / 'nightly-receipts')],
                                                    capture_output=True, text=True, timeout=300).stdout or '{}')
                except (OSError, ValueError, subprocess.TimeoutExpired):
                    res = {'status': 'error'}
                if res.get('status') != 'pass':
                    failing.append({'path': text, 'status': res.get('status', 'error'),
                                    'findings': len(res.get('findings') or [])})
    report = {'deliverables_scanned': scanned, 'deliverables_failing': failing,
              'copies': check(args, quiet=True)}
    if args.weekly:
        home = rules_home(args.rules_dir)
        week = (dt.date.today() - dt.timedelta(days=7)).isoformat()
        per_tool, released = {}, []
        hits = HITS[0]  # weekly counts read the current log only
        if hits.is_file():
            with open(hits, encoding='utf-8') as f:
                for line in f:
                    try:
                        h = json.loads(line)
                    except ValueError:
                        continue
                    if h.get('d', '') < week:
                        continue
                    if h.get('src') in ('reply', 'file'):
                        key = h.get('tool', 'unknown')
                        per_tool[key] = per_tool.get(key, 0) + 1
                    if h.get('rule') == 'gate-unreviewed':
                        released.append(h.get('text'))
        ledger = json.loads((home / 'patterns.json').read_text(encoding='utf-8'))
        report['weekly'] = {
            'hits_per_tool': per_tool,
            'released_unreviewed': released,
            'corrections_logged': [r for r in corrections(home / 'corrections.md') if r['date'] >= week],
            'recurring': [{'rule': r, 'count': n} for r, n, _ in recurring(ledger, days=7)],
        }
    print(json.dumps(report, indent=1))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    for name in ('build', 'check', 'nightly'):
        p = sub.add_parser(name)
        p.add_argument('--rules-dir')
        p.add_argument('--out')
        p.add_argument('--json', action='store_true')
        if name == 'build':
            p.add_argument('--preferences')
        if name == 'check':
            p.add_argument('--living', nargs='*')
        if name == 'nightly':
            p.add_argument('--since', type=float, default=24)
            p.add_argument('--weekly', action='store_true')
            p.add_argument('--living', nargs='*')
    args = ap.parse_args(argv)
    if args.cmd == 'build':
        return build(args)
    if args.cmd == 'check':
        return 0 if check(args)['ok'] else 1
    return nightly(args)


if __name__ == '__main__':
    sys.exit(main())
