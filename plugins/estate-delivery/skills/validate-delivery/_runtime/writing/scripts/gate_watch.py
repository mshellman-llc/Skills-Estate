#!/usr/bin/env python3
"""Run the full writing review on every file that lands in a watched folder.

    gate_watch.py --folder DIR [--dry]

launchd starts this when DIR changes (install_local.py --watch DIR). For each
file in DIR that has settled, has no passing review receipt for its current
bytes and has not already been tried at those bytes, it runs Claude Code
headless with /gate on the file. /gate fixes findings in the file and repeats
until check.py --full passes, then files the reviewed file by the workspace
standard. A macOS notification reports each result, and every run is logged
to ~/.agents/writing/gate-watch.jsonl.

Standard library only. One run at a time; a second start exits.
"""
import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import hook  # noqa: E402  reviewed() reads the receipts check.py writes

AGENT = Path(os.environ.get('WRITING_AGENT_HOME') or Path.home() / '.agents' / 'writing').expanduser()
LOG = AGENT / 'gate-watch.jsonl'
STATE = AGENT / 'gate-watch-state.json'
LOCK = AGENT / 'gate-watch.lock'
CLAUDE = os.environ.get('CLAUDE_BIN') or str(Path.home() / '.local' / 'bin' / 'claude')
SUFFIXES = {'.md', '.markdown', '.txt', '.html', '.htm', '.docx', '.pptx', '.xlsx', '.json'}
SETTLE_SECONDS = float(os.environ.get('GATE_WATCH_SETTLE', '5'))
RUN_SECONDS = 45 * 60
HUBS = ['mcp__beastmode-hub', 'mcp__claude_ai_BeastMode_personal_Hub']  # local server, then the claude.ai connector
TOOLS = ['Read', 'Write', 'Edit', 'Glob', 'Grep', 'Bash(python3:*)', 'Bash(codex exec:*)', 'Bash(codex:*)',
         'Bash(mv:*)', 'Bash(mkdir:*)', 'Bash(shasum:*)', 'Bash(ls:*)', *HUBS]
BLOCKED = [f'{hub}__{name}' for hub in HUBS for name in ('write_record', 'bulk_edit_records', 'edit_file',
                                                          'archive_file', 'add_file', 'create_project')]
SOURCES = ('Find the documents it was written from first in the folder beside it named {stem}-sources, then '
           'with the Knowledge Hub\'s search and read_file. A file that lists sources counts as a source. '
           'Run Codex as `codex exec`. ')
TRIAL = ('/gate {path}\n\nThis is a trial run of the review folder. ' + SOURCES + 'Run every step of the gate, '
         'including the evidence scan, and fix the file in place. Do not move it. '
         'End with one line: PASS or FAIL, then the path.')
PROMPT = ('/gate {path}\n\n'
          'This file landed in the review folder, so it goes to a client or goes public. ' + SOURCES + 'Run every step of the '
          'gate, including the evidence scan. When the receipt passes, file the reviewed file by section 5 of the '
          'highest-numbered workspace standard in /Volumes/BeastMode/80-system/standards/, into its project\'s '
          'artifacts/ under the standard name, with its sources folder in the project\'s sources/; when no project matches, move it to '
          '/Volumes/BeastMode/90-inbox/unsorted/ with a one-line note beside it saying what it is. '
          'Save a session note with save_update for the project it went to. '
          'When the review cannot finish, leave the file where it is and say in the last line what it needs. '
          'End with one line: PASS or FAIL, then the path the file now has or what it needs.')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path, default):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return default


def log(entry):
    AGENT.mkdir(parents=True, exist_ok=True)
    entry = {'at': dt.datetime.now().isoformat(timespec='seconds'), **entry}
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')


def notify(title, text):
    if os.environ.get('GATE_WATCH_QUIET'):
        return
    script = f'display notification {json.dumps(text)} with title {json.dumps(title)}'
    subprocess.run(['osascript', '-e', script], capture_output=True)


def size(path):
    try:
        return path.stat().st_size if path.is_file() else -1
    except OSError:
        return -1


def settled(found):
    """The (path, sha256) pairs whose files are not empty and kept their size over one shared wait."""
    before = {path: size(path) for path, _ in found}
    if found:
        time.sleep(SETTLE_SECONDS)
    return [(path, digest) for path, digest in found if before[path] > 0 and size(path) == before[path]]


def candidates(folder, state):
    for path in sorted(folder.iterdir()):
        if not path.is_file() or path.name.startswith('.') or path.suffix.lower() not in SUFFIXES:
            continue
        if path.name.endswith('.note.md'):
            continue  # the one-line note a filed piece leaves behind
        digest = sha(path)
        if hook.reviewed(digest) or state.get(str(path)) == digest:
            continue
        yield path, digest


def review(path, workdir, trial=False):
    command = [CLAUDE, '-p', (TRIAL if trial else PROMPT).format(path=path, stem=path.stem), '--permission-mode', 'acceptEdits',
               '--allowedTools', *TOOLS, '--disallowedTools', *BLOCKED, '--add-dir', str(path.parent),
               '--add-dir', '/Volumes/BeastMode', '--output-format', 'json']
    env = dict(os.environ, PATH=os.pathsep.join([str(Path.home() / '.local' / 'bin'), '/opt/homebrew/bin',
                                                  '/usr/local/bin', os.environ.get('PATH', '/usr/bin:/bin')]))
    try:
        out = subprocess.run(command, cwd=workdir, capture_output=True, text=True, timeout=RUN_SECONDS, env=env)
    except subprocess.TimeoutExpired:
        return 'timeout', ''
    try:
        text = json.loads(out.stdout).get('result', '')
    except ValueError:
        text = out.stdout[-2000:] or out.stderr[-2000:]
    return ('ok' if out.returncode == 0 else f'exit {out.returncode}'), text


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--folder', required=True)
    ap.add_argument('--dry', action='store_true', help='list what would be reviewed and stop')
    ap.add_argument('--trial', action='store_true', help='review in place without filing the file')
    args = ap.parse_args(argv)
    folder = Path(args.folder).expanduser()
    if not folder.is_dir():
        return 0  # the drive is not mounted; launchd tries again on the next change
    AGENT.mkdir(parents=True, exist_ok=True)
    with open(LOCK, 'w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return 0
        state = read_json(STATE, {})
        pending = settled(list(candidates(folder, state)))
        if args.dry:
            print(json.dumps([str(p) for p, _ in pending], indent=1))
            return 0
        for path, digest in pending:
            if not path.is_file() or sha(path) != digest:
                continue  # changed again while waiting; the next run takes it
            state[str(path)] = digest
            STATE.write_text(json.dumps(state, indent=1), encoding='utf-8')
            notify('Writing review started', path.name)
            workdir = AGENT / 'gate-work' / digest[:12]
            workdir.mkdir(parents=True, exist_ok=True)
            status, text = review(path, workdir, args.trial)
            last = (text.strip().splitlines() or [''])[-1]
            passed = last.upper().startswith('PASS')
            log({'file': str(path), 'sha256': digest, 'run': status, 'result': last[:300]})
            if passed:
                notify('Writing review passed', last[5:].strip() or path.name)
            else:
                notify('Writing review needs you', f'{path.name}: {last[:120] or status}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
