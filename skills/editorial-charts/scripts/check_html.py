#!/usr/bin/env python3
"""
Static pre-publish checks for a chart or dashboard HTML page.

Checks:
  - every inline <script> parses under `node --check` (skipped with a note if node is absent)
  - every <script type="application/json"> block parses as JSON
  - every external script URL pins an exact version (name@1.2.3)
  - no monospace font families
  - no pie or arc generators and no second y-axis (axisRight) without a waiver

Usage:
    python3 -I check_html.py page.html [--allow axisRight]
Exit code 0 when no errors.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

PINNED = re.compile(r"@\d+\.\d+\.\d+(/|$)")


class Scripts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.blocks, self.srcs, self._cur = [], [], None

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            a = dict(attrs)
            if a.get("src"):
                self.srcs.append(a["src"])
            else:
                self._cur = {"type": (a.get("type") or "text/javascript").lower(), "text": ""}

    def handle_data(self, data):
        if self._cur is not None:
            self._cur["text"] += data

    def handle_endtag(self, tag):
        if tag == "script" and self._cur is not None:
            self.blocks.append(self._cur)
            self._cur = None


def check(path, allow=()):
    text = Path(path).read_text()
    p = Scripts()
    p.feed(text)
    errors, notes = [], []

    for src in p.srcs:
        if src.startswith("http") and not PINNED.search(src):
            errors.append(f"Unpinned script URL: {src}")

    node = shutil.which("node")
    for i, b in enumerate(p.blocks, 1):
        if b["type"] == "application/json":
            try:
                json.loads(b["text"])
            except json.JSONDecodeError as e:
                errors.append(f"JSON block {i} does not parse: {e}")
        elif b["type"] in ("text/javascript", "module", "application/javascript"):
            if not node:
                notes.append("node not found; inline scripts were not syntax-checked")
                continue
            suffix = ".mjs" if b["type"] == "module" else ".js"
            with tempfile.NamedTemporaryFile("w", suffix=suffix, delete=False) as f:
                f.write(b["text"])
            r = subprocess.run([node, "--check", f.name], capture_output=True, text=True)
            Path(f.name).unlink()
            if r.returncode:
                errors.append(f"Script block {i} fails node --check: {r.stderr.strip().splitlines()[-1]}")

    if re.search(r"font-family[^;{}]*(mono|Courier)", text, re.I):
        errors.append("Monospace font family found. Use Inter with tabular figures.")
    if re.search(r"d3\.pie\(|Plot\.arc|d3\.arc\(", text) and "pie" not in allow:
        errors.append("Pie or arc generator found. Use a sorted bar or stacked bar.")
    if "axisRight" in text and "axisRight" not in allow:
        errors.append("axisRight found: check for a dual y-axis. Pass --allow axisRight if it is a label axis.")

    return errors, sorted(set(notes)), len(p.blocks), len(p.srcs)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    allow = sys.argv[sys.argv.index("--allow") + 1].split(",") if "--allow" in sys.argv else ()
    errs, notes, nblocks, nsrcs = check(sys.argv[1], allow)
    print(f"{sys.argv[1]}: {nblocks} inline blocks, {nsrcs} external scripts")
    for n in notes:
        print(f"  note: {n}")
    for e in errs:
        print(f"  error: {e}")
    print("  ok" if not errs else f"  {len(errs)} error(s)")
    sys.exit(1 if errs else 0)
