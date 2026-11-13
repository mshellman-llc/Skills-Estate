#!/usr/bin/env python3
"""Writing hook for Claude Code and Codex.

    hook.py --tool claude-code|codex [--register NAME]     # reads the hook event JSON on stdin

Events:

    SessionStart       adds the habits that reached the owner most often in the last 14 days
    UserPromptSubmit   carries findings a reply was allowed through with, and asks for a logged
                       correction when the owner corrects wording
    PostToolUse        scans each prose file a tool wrote and records deliverables for the gate
    Stop               scans the reply and holds it for one rewrite when a finding blocks; holds
                       the session while a deliverable it changed has no passing full review

The scan is check.py on the rules folder (--rules-dir, then WRITING_HOME, then
~/.agents/writing/home). A scan that cannot run never blocks. Hits go to
hits.jsonl beside the state, with the tool that produced them.

The gate reads gate.json beside the state: "include" and "exclude" are fnmatch
patterns for deliverable paths, "max_blocks_per_file" caps how often one file can
hold a session. A deliverable passes when a receipt in the receipts folder has
the file's current sha256, status pass, and the line pass, document pass and spot
audit all ok.

Standard library only.
"""
import argparse
import datetime as dt
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHECK = HERE / 'check.py'
BASE = Path(os.environ.get('WRITING_AGENT_HOME') or Path.home() / '.agents' / 'writing').expanduser()
STATE = BASE / 'state'
HITS = BASE / 'hits.jsonl'
GATE_CONFIG = BASE / 'gate.json'
RECEIPTS = Path(os.environ.get('WRITING_RECEIPTS') or BASE / 'receipts').expanduser()
PROSE = {'.md', '.markdown', '.mdx', '.txt', '.rst', '.html', '.htm'}
SKIP_NAMES = {'CLAUDE.md', 'AGENTS.md', 'SKILL.md', 'MEMORY.md', 'CHANGELOG.md', 'LICENSE.md', 'WORKFLOW.md'}
SKIP_PARTS = {'.git', 'node_modules', '.claude', '.codex', '.agents', 'dist', 'build', 'vendor', '.writing-receipts'}
MIN_WORDS = 40
FILE_NAG_LIMIT = 5
DEFAULT_GATE = {
    'include': ['/Volumes/BeastMode/*/artifacts/*', '/Volumes/BeastMode/Claude outputs/*',
                '/Volumes/BeastMode/Portfolio Site/site/*'],
    'exclude': ['*/archive/*', '*/99-archive/*', '*/sessions/*', '*.text.md', '*/.writing-receipts/*'],
    'extensions': ['.md', '.html', '.htm', '.docx', '.pptx', '.xlsx', '.txt'],
    'max_blocks_per_file': 2,
}
FULL_STEPS = ('line pass', 'document pass', 'spot audit')
CORRECTION = re.compile(
    r"\b(slop|sounds?\s+(like\s+)?(an?\s+)?(ai|chatgpt|robot)|ai[- ](sounding|written|tell)|too\s+ai|"
    r"de-?ai|humani[sz]e|stop\s+(saying|writing|using)|don'?t\s+(say|write|use)\b.{0,40}\bagain|"
    r"i\s+(hate|never)\s+(say|write|use)|ai\s+(writing\s+)?patterns?|writing\s+integrity|"
    r"formulaic|manufactured\s+urgency|checker\s+miss|i\s+loathe)", re.IGNORECASE)
WORD = re.compile(r"[A-Za-z0-9][\w'’-]*")


def today():
    return dt.date.today().isoformat()


def read_json(path, default):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return default


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, indent=1), encoding='utf-8')
    tmp.replace(path)


def state_path(session):
    safe = re.sub(r'[^A-Za-z0-9_.-]', '_', session or 'nosession')[:120]
    return STATE / f'{safe}.json'


def log_hits(tool, src, target, findings):
    if not findings:
        return
    HITS.parent.mkdir(parents=True, exist_ok=True)
    with open(HITS, 'a', encoding='utf-8') as f:
        for h in findings:
            f.write(json.dumps({'d': today(), 'tool': tool, 'src': src, 'target': target,
                                'rule': h.get('rule'), 'text': (h.get('text') or '')[:120]}) + '\n')


def scan_text(text, register, suffix='.md'):
    """Run check.py on text. Returns (status, blocking findings). Status 'error' when the check cannot run."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / f'reply{suffix}'
        path.write_text(text, encoding='utf-8')
        return scan_file(path, register, receipt_dir=tmp)


def scan_file(path, register, receipt_dir=None):
    cmd = [sys.executable, str(CHECK), '--file', str(path), '--json']
    if register:
        cmd += ['--register', register]
    with tempfile.TemporaryDirectory() as tmp:
        cmd += ['--receipt-dir', receipt_dir or tmp]
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            result = json.loads(out.stdout or '{}')
        except (OSError, ValueError, subprocess.TimeoutExpired):
            return 'error', []
    return result.get('status', 'error'), result.get('findings') or []


def describe(findings, limit=8):
    lines = []
    for h in findings[:limit]:
        fix = h.get('fix') or ''
        lines.append(f'- "{h.get("text", "")}" ({h.get("rule")}): {fix}'.rstrip(': '))
    if len(findings) > limit:
        lines.append(f'- and {len(findings) - limit} more of the same kinds')
    return '\n'.join(lines)


def changed_files(event, tool):
    name = event.get('tool_name') or ''
    data = event.get('tool_input') or {}
    paths = []
    if name in ('Write', 'Edit', 'MultiEdit', 'NotebookEdit') and data.get('file_path'):
        paths.append(data['file_path'])
    if name == 'apply_patch':
        patch = data.get('command') or data.get('patch') or data.get('input') or ''
        if isinstance(patch, list):
            patch = '\n'.join(str(p) for p in patch)
        for m in re.finditer(r'^\*\*\* (?:Add File|Update File|Move to): (.+)$', str(patch), re.M):
            paths.append(m.group(1).strip())
    cwd = event.get('cwd') or os.getcwd()
    out = []
    for p in paths:
        p = Path(p).expanduser()
        if not p.is_absolute():
            p = Path(cwd) / p
        out.append(p)
    return out


def is_prose(path):
    return (path.suffix.lower() in PROSE and path.name not in SKIP_NAMES
            and not any(part in SKIP_PARTS for part in path.parts))


def gate_config():
    cfg = dict(DEFAULT_GATE)
    cfg.update(read_json(GATE_CONFIG, {}))
    return cfg


def is_deliverable(path, cfg):
    text = str(path)
    if path.suffix.lower() not in cfg['extensions']:
        return False
    if any(fnmatch.fnmatch(text, pat) for pat in cfg['exclude']):
        return False
    return any(fnmatch.fnmatch(text, pat) for pat in cfg['include'])


def file_sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def reviewed(sha):
    """True when a receipt shows a passing full review of these exact bytes."""
    if not RECEIPTS.is_dir():
        return False
    for receipt in sorted(RECEIPTS.glob('*.json'), key=lambda p: p.stat().st_mtime, reverse=True)[:3000]:
        r = read_json(receipt, {})
        if r.get('sha256') != sha or r.get('status') != 'pass':
            continue
        steps = {s.get('step'): s.get('status') for s in r.get('steps') or []}
        if all(steps.get(s) == 'ok' for s in FULL_STEPS):
            return True
    return False


def emit(obj):
    print(json.dumps(obj))


def on_stop(event, args, state):
    reasons, tool = [], args.tool
    message = event.get('last_assistant_message') or ''
    active = bool(event.get('stop_hook_active'))
    if len(WORD.findall(message)) >= MIN_WORDS:
        status, findings = scan_text(message, args.register)
        log_hits(tool, 'reply', 'chat', findings)
        if status == 'fail' and findings:
            if active:
                state['carry'] = findings[:5]
            else:
                reasons.append('Your reply breaks the owner\'s writing rules. Rewrite these sentences, then give '
                               'the whole reply again without mentioning this check:\n' + describe(findings))
    cfg = gate_config()
    pending, blocked = [], state.setdefault('gate_blocks', {})
    for p in state.get('deliverables', []):
        path = Path(p)
        if not path.is_file():
            continue
        if reviewed(file_sha(path)):
            continue
        if blocked.get(p, 0) < cfg['max_blocks_per_file']:
            pending.append(p)
            blocked[p] = blocked.get(p, 0) + 1
        else:
            state.setdefault('released_unreviewed', [])
            if p not in state['released_unreviewed']:
                state['released_unreviewed'].append(p)
                log_hits(tool, 'gate', path.name, [{'rule': 'gate-unreviewed', 'text': p}])
    if pending:
        reasons.append('These deliverables changed without a passing full writing review of their current bytes:\n'
                       + '\n'.join(f'- {p}' for p in pending)
                       + '\nRun the writing skill\'s full review on each (check.py --prepare, line pass, document '
                         'pass, spot audit, then check.py --full). Give the line pass and the audit to separate '
                         'reviewers, from a different model family when one is available. Fix findings at the source '
                         'and run it again until the receipt passes.')
    if reasons:
        emit({'decision': 'block', 'reason': '\n\n'.join(reasons)})
    elif state.get('released_unreviewed') and not state.get('told_unreviewed'):
        state['told_unreviewed'] = True
        emit({'systemMessage': 'Not fully reviewed: ' + ', '.join(state['released_unreviewed'])})


def on_post_tool(event, args, state):
    cfg = gate_config()
    notes = []
    nags = state.setdefault('nags', {})
    for path in changed_files(event, args.tool):
        if is_deliverable(path, cfg) and str(path) not in state.setdefault('deliverables', []):
            state['deliverables'].append(str(path))
        if not is_prose(path) or not path.is_file():
            continue
        status, findings = scan_file(path, args.register)
        log_hits(args.tool, 'file', path.name, findings)
        if status == 'fail' and findings:
            count = nags.get(str(path), 0) + 1
            nags[str(path)] = count
            if count <= FILE_NAG_LIMIT:
                notes.append(f'{path.name} breaks the owner\'s writing rules. Rewrite these sentences in the file:\n'
                             + describe(findings))
            elif count == FILE_NAG_LIMIT + 1:
                log_hits(args.tool, 'file-limit', path.name, [{'rule': 'nag-limit', 'text': str(path)}])
    if notes:
        emit({'decision': 'block', 'reason': '\n\n'.join(notes)})


def on_prompt(event, args, state):
    notes = []
    carry = state.pop('carry', None)
    if carry:
        notes.append('Your last reply went out with these rule breaks; keep them out of this one:\n' + describe(carry))
    if CORRECTION.search(event.get('prompt') or ''):
        notes.append('The owner may be correcting wording. Fix every instance in the piece. Then add a row to '
                     'corrections.md in the rules folder: the date, the words before and after, the channel and '
                     'audience, the rule ID, the pattern ID if a script can catch it, and the tool. When a pattern '
                     'can catch it, add the pattern to patterns.json with status candidate.')
    if notes:
        emit({'hookSpecificOutput': {'hookEventName': 'UserPromptSubmit', 'additionalContext': '\n\n'.join(notes)}})


def recurring(days=14, top=3):
    """The blocking rules that reached the owner most often lately, with each rule's repair."""
    since = (dt.date.today() - dt.timedelta(days=days)).isoformat()
    counts = {}
    try:
        with open(HITS, encoding='utf-8') as f:
            for line in f:
                try:
                    h = json.loads(line)
                except ValueError:
                    continue
                if h.get('d', '') >= since and h.get('rule') and h.get('src') in ('reply', 'file'):
                    counts[h['rule']] = counts.get(h['rule'], 0) + 1
    except OSError:
        return []
    return sorted(counts.items(), key=lambda kv: -kv[1])[:top]


def on_session_start(event, args, state):
    top = recurring()
    if top:
        text = ('Writing habits that reached the owner most often in the last 14 days. Keep them out: '
                + '; '.join(f'{rule} ({n} times)' for rule, n in top) + '.')
        emit({'hookSpecificOutput': {'hookEventName': 'SessionStart', 'additionalContext': text}})


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--tool', default='claude-code')
    ap.add_argument('--register', default='megan')
    args = ap.parse_args(argv)
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    name = event.get('hook_event_name') or ''
    path = state_path(event.get('session_id'))
    state = read_json(path, {})
    handler = {'Stop': on_stop, 'PostToolUse': on_post_tool, 'UserPromptSubmit': on_prompt,
               'SessionStart': on_session_start}.get(name)
    if handler:
        try:
            handler(event, args, state)
        except Exception as error:  # a hook never breaks a session
            log_hits(args.tool, 'hook-error', name, [{'rule': 'hook-error', 'text': f'{type(error).__name__}: {error}'}])
        write_json(path, state)
    return 0


if __name__ == '__main__':
    sys.exit(main())
