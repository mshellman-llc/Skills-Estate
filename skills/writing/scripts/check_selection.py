#!/usr/bin/env python3
"""Check text selected in any app, from the "Check writing" Services menu action.

Reads the text on stdin, runs check.py on it and shows the result in a
notification. The full list of findings goes to ~/.agents/writing/last-selection.txt.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path.home() / '.agents' / 'writing' / 'last-selection.txt'


def notify(title, text):
    script = f'display notification {json.dumps(text[:220])} with title {json.dumps(title)}'
    subprocess.run(['osascript', '-e', script], capture_output=True)


def main():
    text = sys.stdin.read()
    if not text.strip():
        return 0
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / 'selection.md'
        path.write_text(text, encoding='utf-8')
        out = subprocess.run([sys.executable, str(HERE / 'check.py'), '--file', str(path), '--register', 'megan',
                              '--json', '--receipt-dir', tmp], capture_output=True, text=True, timeout=60)
    try:
        result = json.loads(out.stdout or '{}')
    except ValueError:
        result = {}
    status = result.get('status', 'error')
    findings = result.get('findings') or []
    review = result.get('review') or []
    lines = [f'Status: {status}']
    lines += [f'- "{h.get("text")}" ({h.get("rule")}): {h.get("fix", "")}' for h in findings]
    lines += [f'- check by hand: "{h.get("text")}" ({h.get("rule")})' for h in review]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    if status == 'pass' and not review:
        notify('Check writing', 'No rule breaks found.')
    elif status == 'pass':
        notify('Check writing', f'{len(review)} lines to check by hand. Details in {OUT}')
    elif status == 'fail':
        first = findings[0] if findings else {}
        notify('Check writing', f'{len(findings)} rule breaks. First: "{first.get("text", "")}". Details in {OUT}')
    else:
        notify('Check writing', 'The check could not run. Details in ' + str(OUT))
    return 0


if __name__ == '__main__':
    sys.exit(main())
