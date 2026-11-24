#!/usr/bin/env python3
"""Check a handoff readiness gap memo for its required sections.

Usage:
    python3 check_gap_memo.py MEMO.md

Exit codes: 0 pass, 1 a section is missing or out of order, 2 usage or read error.
The memo is Markdown; an HTML memo is checked on its extracted text, one heading per line.
Stdlib only.
"""
import re
import sys

SECTIONS = [
    "What stops the handoff",
    "What already holds",
    "Blockers",
    "Ownership gaps",
    "Promises made before signature",
    "Evidence",
    "Next gate",
]
HEADING = re.compile(r"^##\s+(.*?)\s*$")


def check(text):
    found = [m.group(1) for line in text.splitlines() if (m := HEADING.match(line))]
    findings = []
    for name in SECTIONS:
        if name not in found:
            findings.append(f"missing section: {name}")
    order = [name for name in found if name in SECTIONS]
    if not findings and order != SECTIONS:
        findings.append("sections are out of order: expected " + ", ".join(SECTIONS))
    if "—" in text:
        findings.append("em dash found")
    return findings


def main(argv):
    if len(argv) != 2:
        print("usage: python3 check_gap_memo.py MEMO.md")
        return 2
    try:
        text = open(argv[1], encoding="utf-8").read()
    except OSError as exc:
        print(f"cannot read memo: {exc}")
        return 2
    findings = check(text)
    for finding in findings:
        print(f"FAIL: {finding}")
    print("RESULT: " + (f"FAIL ({len(findings)} finding(s))" if findings else "PASS"))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
