#!/usr/bin/env python3
"""Selftest for check_brief.py. Runs the gate against the fixtures and verifies
exit codes and specific findings. Exits nonzero on any broken expectation."""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(HERE, "check_brief.py")
FIX = os.path.join(HERE, "fixtures")

failures = []


def run(fixture):
    proc = subprocess.run(
        [sys.executable, GATE, os.path.join(FIX, fixture)],
        capture_output=True, text=True,
    )
    return proc.returncode, proc.stdout


def expect(fixture, want_code, want_substrings=(), forbid_substrings=()):
    code, out = run(fixture)
    if code != want_code:
        failures.append("{}: expected exit {}, got {}\n{}".format(fixture, want_code, code, out))
        return
    for s in want_substrings:
        if s not in out:
            failures.append("{}: expected finding containing '{}', output was:\n{}".format(fixture, s, out))
    for s in forbid_substrings:
        if s in out:
            failures.append("{}: unexpected finding containing '{}':\n{}".format(fixture, s, out))
    print("ok: {} (exit {})".format(fixture, code))


# Clean JSON ledger passes.
expect("pass.json", 0, want_substrings=["0 fail"])

# Clean markdown brief passes.
expect("pass.md", 0, want_substrings=["0 fail"])

# Broken JSON ledger: every rule fires.
expect("fail.json", 1, want_substrings=[
    "no source token",                    # empty source on a Column A claim
    "confidence Unknown",                 # Unknown parked in Column A
    "must be Confirmed or Inferred",      # invalid confidence value
    "no scope line named",                # question with empty unblocks
    "rank must be High, Medium, or Low",  # invalid rank
    "must run in rank order",             # High after Low
])

# Empty Column B is a hard fail.
expect("fail_empty_open.json", 1, want_substrings=["Column B is empty"])

# Broken markdown brief: same rules through the table parser.
expect("fail.md", 1, want_substrings=[
    "no source token",
    "confidence Unknown",
    "no scope line named",
    "must run in rank order",
])

# Em dash detection, generated at runtime so no fixture file carries the
# character (the skill directory itself must scan clean).
import tempfile

with open(os.path.join(FIX, "pass.md"), encoding="utf-8") as f:
    clean = f.read()
tmp = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8")
tmp.write(clean + "\nA stray em dash \u2014 the gate must catch it.\n")
tmp.close()
proc = subprocess.run([sys.executable, GATE, tmp.name], capture_output=True, text=True)
os.unlink(tmp.name)
if proc.returncode != 1 or "em dash on line" not in proc.stdout:
    failures.append("em dash case: expected exit 1 with 'em dash on line', got {}\n{}".format(proc.returncode, proc.stdout))
else:
    print("ok: runtime em dash case (exit 1)")

# Markdown with no ledger tables at all.
expect("fail_no_tables.md", 1, want_substrings=[
    "no Column A table found",
    "no Column B table found",
])

if failures:
    print("\nSELFTEST FAILED: {} broken expectation(s)".format(len(failures)))
    for f in failures:
        print("- " + f)
    sys.exit(1)
print("\nSELFTEST PASSED: 7 cases, all expectations met")
