#!/usr/bin/env python3
"""PreToolUse guard: send whole-file reads of large rendered files to the extractor.

Claude Code and Codex both pass the tool call as JSON on stdin. The guard denies
one call when it would read a whole rendered or generated file (HTML, SVG,
workbook, Word document or deck) that is too large or too wide to read in one
pass. Reads with an offset and limit, line-range commands and every other tool
pass untouched. Any error lets the call through, so the guard never blocks work
it does not understand.
"""
import json
import os
import shlex
import sys
from pathlib import Path

MARKUP = {'.html', '.htm', '.svg'}
OFFICE = {'.xlsx', '.docx', '.pptx'}
MAX_BYTES = 100_000
MAX_LINE = 2_000
WHOLE_READERS = {'cat', 'less', 'more', 'bat', 'nl', 'tac'}
FILTERS = {'head', 'tail', 'grep', 'rg', 'sed', 'awk', 'wc', 'cut', 'jq', 'python3', 'python'}
SHELL_TOOLS = {'Bash', 'exec_command', 'functions.exec_command', 'shell', 'local_shell'}
EXTRACTOR = Path(__file__).resolve().with_name('extract_review_text.py')


def too_large(path):
    """Return a reason when the file at path is too large or too wide to read whole."""
    try:
        size = path.stat().st_size
    except OSError:
        return None
    suffix = path.suffix.lower()
    if suffix in OFFICE:
        return f'{path.name} is a binary {suffix} file'
    if suffix not in MARKUP:
        return None
    if size > MAX_BYTES:
        return f'{path.name} is {size:,} bytes'
    try:
        with path.open('rb') as handle:
            for line in handle:
                if len(line) > MAX_LINE:
                    return f'{path.name} has a line over {MAX_LINE:,} characters'
    except OSError:
        return None
    return None


def resolve(name, cwd):
    path = Path(os.path.expanduser(name))
    return path if path.is_absolute() else Path(cwd) / path


def read_targets(event):
    """Yield files a tool call would read in full."""
    tool = str(event.get('tool_name') or '')
    data = event.get('tool_input')
    data = data if isinstance(data, dict) else {}
    cwd = str(data.get('workdir') or event.get('cwd') or '.')
    if tool == 'Read':
        if data.get('offset') is None and data.get('limit') is None and data.get('file_path'):
            yield resolve(str(data['file_path']), cwd)
        return
    if tool not in SHELL_TOOLS:
        return
    command = data.get('command') or data.get('cmd') or ''
    if isinstance(command, list):
        command = ' '.join(shlex.quote(str(part)) for part in command)
    try:
        lexer = shlex.shlex(str(command), posix=True, punctuation_chars=';&|<>()\n')
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        return
    # Split into pipelines, then into piped segments. A whole-file reader whose
    # output is piped into a filter such as head or grep prints only part of the file.
    pipelines, segments, segment = [], [], []
    for token in tokens + [';']:
        if token in {';', '&&', '||', '&', '(', ')', '\n'}:
            segments.append(segment)
            pipelines.append(segments)
            segments, segment = [], []
        elif token == '|':
            segments.append(segment)
            segment = []
        else:
            segment.append(token)
    for segments in pipelines:
        for index, words in enumerate(segments):
            if not words or Path(words[0]).name not in WHOLE_READERS:
                continue
            if '>' in words or '>>' in words:
                continue  # Output goes to a file, not the transcript.
            if any(later and Path(later[0]).name in FILTERS for later in segments[index + 1:]):
                continue
            for word in words[1:]:
                if not word.startswith('-'):
                    yield resolve(word, cwd)


def main():
    try:
        event = json.load(sys.stdin)
        for path in read_targets(event):
            reason = too_large(path)
            if reason:
                message = (
                    f'{reason}, too large to read whole. For a writing review, extract its text: '
                    f'python3 {EXTRACTOR} extract "{path}" --out REVIEW/before, then read the parts. '
                    'To edit markup, read the lines you need with an offset and limit, or a line range.'
                )
                print(json.dumps({'hookSpecificOutput': {
                    'hookEventName': 'PreToolUse',
                    'permissionDecision': 'deny',
                    'permissionDecisionReason': message,
                }}))
                return
    except Exception:  # noqa: BLE001 - a guard error must never block the call
        return


if __name__ == '__main__':
    main()
