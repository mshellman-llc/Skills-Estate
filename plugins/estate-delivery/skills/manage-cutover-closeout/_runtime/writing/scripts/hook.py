#!/usr/bin/env python3
"""Writing hook for Claude Code and Codex.

    hook.py --tool claude-code|codex [--register NAME]     # reads the hook event JSON on stdin

Events:

    SessionStart       adds the habits that reached the owner most often in the last 14 days
    UserPromptSubmit   carries findings a reply was allowed through with, and asks for a logged
                       correction when the owner corrects wording
    PreToolUse         holds a publish call (an artifact or a page going out) until the exact
                       bytes it publishes have a passing full review
    PostToolUse        scans each prose file a tool wrote, records deliverables for the gate and
                       logs which session wrote each file to writers.jsonl
    Stop               scans the reply and holds it for one rewrite when a finding blocks; holds
                       the session while a deliverable it changed has no passing full review

The scan is check.py on the rules folder (--rules-dir, then WRITING_HOME, then
~/.agents/writing/home). A scan that cannot run never blocks. Hits go to
hits.jsonl beside the state, with the tool that produced them.

The gate reads gate.json beside the state: "include" and "exclude" are fnmatch
patterns for deliverable paths, "max_blocks_per_file" caps how often one file can
hold a session. A deliverable passes when a receipt in the receipts folder has
the file's current sha256, status pass (a scan alone is scan-pass), and the line
pass, document pass and spot audit all ok.

The publish check reads "publish_tools" (fnmatch patterns for tool names) and
"publish_requires" from gate.json. With "full", the default, a publish call is
denied unless a receipt shows a passing full review of the exact bytes it sends:
the file it names, or the content it carries. With "scan", the call is denied
when check.py finds a blocking line in those bytes. A call whose content the
hook cannot read is denied, and the reason names what it could not read: a
missing or unreadable file, a call with no file or text content, or bytes the
scan could not read. Any other error in the publish check denies the call too,
with the error as the reason, and the hook prints one decision. On an error, a
call counts as a publish call when the built-in publish_tools list or the
configured one names it; the built-in list is checked first and cannot fail.

Each gate.json setting is checked when it loads. A value of the wrong type or
shape (publish_tools as a string, a number, a list holding non-strings, null or
an empty list; publish_requires other than "full" or "scan"; include, exclude
or extensions not a list of strings; max_blocks_per_file not a whole number of
1 or more) is ignored and its built-in default used. A gate.json that is not a
JSON object, or cannot be read, leaves every setting at its default. The
session is told which settings were ignored: at session start, on the first
write or stop after the problem appears, and in every publish decision. A
ledger setting check.py ignored ("config_ignored") is told the same way.

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
WRITERS = BASE / 'writers.jsonl'   # check.py reads it to reject verdicts from the session that wrote the piece
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
    'publish_tools': ['Artifact', 'mcp__*publish*', 'mcp__*Publish*'],
    'publish_requires': 'full',
}
DEFAULT_PUBLISH_TOOLS = tuple(DEFAULT_GATE['publish_tools'])   # the error path reads this copy, never gate.json


def _strings(value, empty_ok=True):
    return (isinstance(value, list) and (empty_ok or bool(value))
            and all(isinstance(item, str) and item for item in value))


# gate.json settings: (test, what a valid value is). A value that fails its test is replaced by the default.
GATE_SETTINGS = {
    'include': (_strings, 'a list of fnmatch patterns (strings)'),
    'exclude': (_strings, 'a list of fnmatch patterns (strings)'),
    'extensions': (_strings, 'a list of file suffixes (strings)'),
    'max_blocks_per_file': (lambda v: isinstance(v, int) and not isinstance(v, bool) and v >= 1,
                            'a whole number of 1 or more'),
    'publish_tools': (lambda v: _strings(v, empty_ok=False), 'a non-empty list of fnmatch patterns (strings)'),
    'publish_requires': (lambda v: isinstance(v, str) and v in ('full', 'scan'), '"full" or "scan"'),
}
SCAN_NOTES = []   # settings check.py reported as ignored during this run of the hook
PUBLISH_PATH_KEYS = ('file_path', 'path', 'file', 'source_path')
PUBLISH_TEXT_KEYS = ('content', 'html', 'markdown', 'body', 'text', 'source')
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
    if receipt_dir is None:  # a scan's receipt is thrown away unless the caller keeps it
        with tempfile.TemporaryDirectory() as tmp:
            return scan_file(path, register, tmp)
    cmd = [sys.executable, str(CHECK), '--file', str(path), '--json', '--receipt-dir', str(receipt_dir)]
    if register:
        cmd += ['--register', register]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        result = json.loads(out.stdout or '{}')
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return 'error', []
    if not isinstance(result, dict):
        return 'error', []
    for note in result.get('config_ignored') or []:
        if isinstance(note, str) and note not in SCAN_NOTES:
            SCAN_NOTES.append(note)
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


def shown(value):
    text = json.dumps(value, ensure_ascii=False)
    return text if len(text) <= 60 else text[:57] + '...'


def load_gate():
    """(settings, notes): gate.json over the defaults, with every malformed setting replaced by its default.

    A missing gate.json is the defaults with no note. Never raises."""
    cfg = {key: list(value) if isinstance(value, list) else value for key, value in DEFAULT_GATE.items()}
    try:
        data = json.loads(GATE_CONFIG.read_text(encoding='utf-8'))
    except FileNotFoundError:
        return cfg, []
    except (OSError, ValueError) as error:
        return cfg, [f'{GATE_CONFIG} could not be read ({type(error).__name__}: {error}), so every gate setting '
                     'uses its built-in default']
    if not isinstance(data, dict):
        return cfg, [f'{GATE_CONFIG} holds {shown(data)}, not a JSON object, so every gate setting uses its '
                     'built-in default']
    notes = []
    for key, value in data.items():
        if key not in GATE_SETTINGS:
            continue
        valid, want = GATE_SETTINGS[key]
        if valid(value):
            cfg[key] = value
        else:
            notes.append(f'gate.json setting "{key}" was ignored: it is {shown(value)} and must be {want}, so the '
                         f'built-in default {shown(DEFAULT_GATE[key])} is used')
    return cfg, notes


def gate_config():
    return load_gate()[0]


def untold(state):
    """Notes on ignored settings this session has not been told yet; marks them told."""
    notes = load_gate()[1] + SCAN_NOTES
    told = state.get('told_settings')
    told = told if isinstance(told, list) else []
    fresh = [n for n in dict.fromkeys(notes) if n not in told]
    if fresh:
        state['told_settings'] = told + fresh
    return fresh


def settings_text(notes):
    return 'Writing hook settings ignored:\n' + '\n'.join(f'- {n}' for n in notes)


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
    """True when a receipt shows a passing full review of these exact bytes. A receipt of the wrong shape is
    skipped, never counted and never an error."""
    if not RECEIPTS.is_dir():
        return False
    for receipt in sorted(RECEIPTS.glob('*.json'), key=lambda p: p.stat().st_mtime, reverse=True)[:3000]:
        r = read_json(receipt, {})
        if not isinstance(r, dict) or r.get('sha256') != sha or r.get('status') != 'pass':
            continue
        listed = r.get('steps')
        if not isinstance(listed, list):
            continue
        steps = {str(s.get('step')): s.get('status') for s in listed if isinstance(s, dict)}
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
    notes = untold(state)
    if reasons:
        emit({'decision': 'block', 'reason': '\n\n'.join(reasons + ([settings_text(notes)] if notes else []))})
        return
    messages = [settings_text(notes)] if notes else []
    if state.get('released_unreviewed') and not state.get('told_unreviewed'):
        state['told_unreviewed'] = True
        messages.append('Not fully reviewed: ' + ', '.join(state['released_unreviewed']))
    if messages:
        emit({'systemMessage': '\n\n'.join(messages)})


def log_writers(event, args, paths):
    """One line per file a session wrote with a file tool, with the file's sha256 after the write.

    A file written from a shell command is not seen."""
    session = str(event.get('session_id') or '').strip()
    if not session or not paths:
        return None
    lines = []
    for path in paths:
        item = {'d': today(), 'tool': args.tool, 'session': session, 'path': str(Path(path).resolve())}
        try:
            item['sha256'] = file_sha(path)   # check.py counts writers up to the content under review
        except OSError:
            pass
        lines.append(json.dumps(item) + '\n')
    try:
        WRITERS.parent.mkdir(parents=True, exist_ok=True)
        with open(WRITERS, 'a', encoding='utf-8') as f:
            f.write(''.join(lines))
    except OSError as error:
        # A lost line hides this session as a writer, so a later review of the file could count as independent.
        return (f'The writer log {WRITERS} could not record that this session wrote '
                + ', '.join(Path(p).name for p in paths) + f' ({type(error).__name__}: {error}). Do not review '
                'these files from this session, and pass this session ID to check.py with --writer when another '
                'session reviews them.')
    return None


def on_post_tool(event, args, state):
    cfg = gate_config()
    notes = []
    nags = state.setdefault('nags', {})
    paths = changed_files(event, args.tool)
    unlogged = log_writers(event, args, paths)
    if unlogged:
        notes.append(unlogged)
        log_hits(args.tool, 'writer-log-error', 'writers.jsonl', [{'rule': 'writer-log-error', 'text': unlogged}])
    for path in paths:
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
    told = untold(state)
    if notes:
        emit({'decision': 'block', 'reason': '\n\n'.join(notes + ([settings_text(told)] if told else []))})
    elif told:
        emit({'hookSpecificOutput': {'hookEventName': 'PostToolUse', 'additionalContext': settings_text(told)},
              'systemMessage': settings_text(told)})


def published_bytes(data):
    """The bytes a publish call sends and where they came from, or (None, what could not be read)."""
    unread = []
    for key in PUBLISH_PATH_KEYS:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            path = Path(value).expanduser()
            try:
                if not path.is_file():   # is_file raises for a name too long or a folder it cannot enter
                    unread.append(f'the file {path} named in {key}, which does not exist or is not a file')
                    continue
                return path.read_bytes(), str(path)
            except (OSError, ValueError) as exc:
                # A file that exists but cannot be read is what the call sends, so no text content stands in.
                return None, f'the file {path} named in {key} ({type(exc).__name__}: {getattr(exc, "strerror", None) or exc})'
    for key in PUBLISH_TEXT_KEYS:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.encode('utf-8'), f'the {key} of the call'
    if not unread:
        unread.append('the call names no file (' + ', '.join(PUBLISH_PATH_KEYS) + ') and carries no text content ('
                      + ', '.join(PUBLISH_TEXT_KEYS) + ')')
    return None, '; '.join(unread)


def deny(reason):
    emit({'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'permissionDecision': 'deny',
                                 'permissionDecisionReason': reason}})


def note_hits(tool, src, target, findings):
    """log_hits for the publish path: a log that cannot be written never stops the denial."""
    try:
        log_hits(tool, src, target, findings)
    except OSError:
        pass


def tool_name(event):
    name = event.get('tool_name') if isinstance(event, dict) else None
    return name if isinstance(name, str) else ''


def is_publish_tool(event, cfg):
    """True when the gate's validated publish_tools patterns name the tool."""
    return any(fnmatch.fnmatchcase(tool_name(event), pat) for pat in cfg['publish_tools'])


def may_publish(event):
    """The error path's detector. True when the built-in list or the configured list names the tool, and True
    when even that cannot be decided. Never raises."""
    try:
        name = tool_name(event)
        if any(fnmatch.fnmatchcase(name, pat) for pat in DEFAULT_PUBLISH_TOOLS):
            return True
    except Exception:
        return True
    try:
        return is_publish_tool(event, gate_config())
    except Exception:
        return False   # the built-in list already said no


def on_pre_tool(event, args, state):
    """The denial reason for a publish call, or None when it may go out. main() denies on any exception."""
    cfg = gate_config()
    if not is_publish_tool(event, cfg):
        return None
    name = event.get('tool_name') or ''
    tool_input = event.get('tool_input')
    data, where = published_bytes(tool_input if isinstance(tool_input, dict) else {})
    if data is None:
        note_hits(args.tool, 'publish-unresolved', name, [{'rule': 'publish-unresolved', 'text': where}])
        return (f'Not published: the writing check could not read what {name} sends. It could not read {where}. '
                'Save the content to a file, review it, and pass that file path or the content itself in the call.')
    sha = hashlib.sha256(data).hexdigest()
    if cfg['publish_requires'] == 'scan':
        try:
            suffix = Path(where).suffix if Path(where).suffix else '.html'
            with tempfile.TemporaryDirectory() as tmp:
                piece = Path(tmp) / f'publish{suffix}'
                piece.write_bytes(data)
                status, findings = scan_file(piece, args.register, receipt_dir=tmp)
        except (OSError, ValueError) as exc:
            note_hits(args.tool, 'publish-unresolved', name, [{'rule': 'publish-unresolved', 'text': where}])
            return (f'Not published: the writing check could not set up the scan of {where} '
                    f'({type(exc).__name__}: {exc}). Save the content to a file with a short name, then publish again.')
        if status == 'fail' and findings:
            note_hits(args.tool, 'publish', name, findings)
            return f'{where} breaks the writing rules. Rewrite these lines, then publish again:\n' + describe(findings)
        if status not in ('pass', 'scan-pass'):
            note_hits(args.tool, 'publish-unresolved', name, [{'rule': 'publish-unresolved', 'text': where}])
            return (f'Not published: the writing check could not read {where} (status {status}). Save the content '
                    'in a format check.py reads, then publish again.')
        return None
    if reviewed(sha):
        return None
    note_hits(args.tool, 'publish', name, [{'rule': 'publish-without-review', 'text': where}])
    return (f'Not published: no passing full review covers {where} (sha256 {sha[:12]}). Save these exact bytes to a '
            'file, run the full review (check.py --file FILE --full with the line pass, document pass and spot audit '
            'by a reviewer other than the writer) until it returns pass, then publish the same bytes.')


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
    parts = []
    if top:
        parts.append('Writing habits that reached the owner most often in the last 14 days. Keep them out: '
                     + '; '.join(f'{rule} ({n} times)' for rule, n in top) + '.')
    notes = untold(state)
    if notes:
        parts.append(settings_text(notes))
    if parts:
        out = {'hookSpecificOutput': {'hookEventName': 'SessionStart', 'additionalContext': '\n\n'.join(parts)}}
        if notes:
            out['systemMessage'] = settings_text(notes)
        emit(out)


def pre_tool(event, args, state):
    """Run the publish check and emit at most one decision. A publish call is denied on any error, because the
    host lets a call through when the hook prints nothing or exits with an error other than 2."""
    try:
        reason = on_pre_tool(event, args, state)
    except Exception as error:
        if not may_publish(event):
            return 0
        name = tool_name(event) or 'the publish tool'
        note_hits(args.tool, 'publish-unresolved', name,
                  [{'rule': 'publish-unresolved', 'text': f'{type(error).__name__}: {error}'}])
        reason = (f'Not published: the writing check failed while reading what {name} sends '
                  f'({type(error).__name__}: {error}), so no review can cover it. Save the content to a readable '
                  'file with a short name, review it, and publish that file.')
    notes = []
    try:
        if reason or is_publish_tool(event, gate_config()):
            notes = load_gate()[1] + SCAN_NOTES
    except Exception:
        notes = []
    if reason:
        deny(reason + ('\n\n' + settings_text(notes) if notes else ''))
    elif notes:
        emit({'systemMessage': settings_text(notes)})
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--tool', default='claude-code')
    ap.add_argument('--register', default='megan')
    args = ap.parse_args(argv)
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    if not isinstance(event, dict):
        return 0
    name = event.get('hook_event_name') or ''
    path = state_path(str(event.get('session_id') or ''))
    state = read_json(path, {})
    if not isinstance(state, dict):
        state = {}
    if name == 'PreToolUse':
        return pre_tool(event, args, state)
    handler = {'Stop': on_stop, 'PostToolUse': on_post_tool,
               'UserPromptSubmit': on_prompt, 'SessionStart': on_session_start}.get(name)
    if handler:
        try:
            handler(event, args, state)
        except Exception as error:  # a hook never breaks a session
            log_hits(args.tool, 'hook-error', name, [{'rule': 'hook-error', 'text': f'{type(error).__name__}: {error}'}])
        write_json(path, state)
    return 0


if __name__ == '__main__':
    sys.exit(main())
