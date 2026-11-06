#!/usr/bin/env python3
"""Selftest for check_pursuit_brief.py. Runs the gate against the fixtures and
verifies exit codes and specific findings. Exits nonzero on any broken
expectation."""

import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(HERE, "check_pursuit_brief.py")
FIX = os.path.join(HERE, "fixtures")

failures = []
cases = 0


def run(*args):
    proc = subprocess.run(
        [sys.executable, GATE, *args], capture_output=True, text=True,
    )
    return proc.returncode, proc.stdout


def expect(name, args, want_code, want_substrings=(), forbid_substrings=()):
    global cases
    cases += 1
    code, out = run(*args)
    if code != want_code:
        failures.append("{}: expected exit {}, got {}\n{}".format(name, want_code, code, out))
        return
    for s in want_substrings:
        if s not in out:
            failures.append("{}: expected finding containing '{}', output was:\n{}".format(name, s, out))
    for s in forbid_substrings:
        if s in out:
            failures.append("{}: unexpected finding containing '{}':\n{}".format(name, s, out))
    print("ok: {} (exit {})".format(name, code))


def fx(name):
    return os.path.join(FIX, name)


# A complete Pursuit Brief passes.
expect("pursuit pass", [fx("pursuit_pass.md")], 0, want_substrings=["0 fail"])

# A broken Pursuit Brief: every pursuit rule fires.
expect("pursuit fail", [fx("pursuit_fail.md")], 1, want_substrings=[
    "missing section: no heading matches 'desired business outcomes'",
    "missing section: no heading matches 'confirmed facts'",
    "missing section: no heading matches 'important unknowns'",
    "missing section: no heading matches 'risks and warning signs'",
    "missing section: no heading matches 'qualification status'",
    "missing section: no heading matches 'decisions needed'",
    "assumptions entry not labeled as an assumption",
    "no last-updated provenance line",
    "no Desired outcome line",
    "no Prerequisites line",
    "unresolved placeholder (TBD)",
], forbid_substrings=[
    "missing section: no heading matches 'situation'",
    "missing section: no heading matches 'recommended calls'",
])

# A complete Upcoming Call Brief passes.
expect("call pass", ["--mode", "call", fx("call_pass.md")], 0, want_substrings=["0 fail"])

# A broken Upcoming Call Brief: the call rules fire.
expect("call fail", ["--mode", "call", fx("call_fail.md")], 1, want_substrings=[
    "missing section: no heading matches 'attendees and roles'",
    "missing section: no heading matches 'run of show'",
    "missing section: no heading matches 'follow-up plan'",
    "no explicit relationship to the rolling Pursuit Brief",
    "unresolved placeholder ({{ }} slot)",
], forbid_substrings=[
    "missing section: no heading matches 'call objective'",
    "missing section: no heading matches 'agenda'",
])

# Idempotency pair: an update that preserves the human block passes.
expect("human block preserved",
       ["--before", fx("pursuit_pass.md"), "--after", fx("pursuit_after_good.md")],
       0, want_substrings=["0 fail"])

# An update that rewrites the human block fails.
expect("human block rewritten",
       ["--before", fx("pursuit_pass.md"), "--after", fx("pursuit_after_bad.md")],
       1, want_substrings=["human-authored block was rewritten or dropped"])

# Combined run: validate the after file and the marker pair together.
expect("combined file plus markers",
       ["--before", fx("pursuit_pass.md"), "--after", fx("pursuit_after_good.md"),
        fx("pursuit_pass.md")],
       0, want_substrings=["0 fail"])

# Em dash detection, generated at runtime so no fixture file carries the
# character (the skill directory itself must scan clean).
with open(fx("pursuit_pass.md"), encoding="utf-8") as f:
    clean = f.read()
tmp = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8")
tmp.write(clean + "\nA stray em dash \u2014 the gate must catch it.\n")
tmp.close()
cases += 1
proc = subprocess.run([sys.executable, GATE, tmp.name], capture_output=True, text=True)
os.unlink(tmp.name)
if proc.returncode != 1 or "em dash on line" not in proc.stdout:
    failures.append("em dash case: expected exit 1 with 'em dash on line', got {}\n{}".format(
        proc.returncode, proc.stdout))
else:
    print("ok: runtime em dash case (exit 1)")

# An unpaired marker in the after file fails.
tmp = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8")
tmp.write(clean + "\n<!-- human -->\nAn opened block nobody closed.\n")
tmp.close()
cases += 1
proc = subprocess.run(
    [sys.executable, GATE, "--before", fx("pursuit_pass.md"), "--after", tmp.name],
    capture_output=True, text=True)
os.unlink(tmp.name)
if proc.returncode != 1 or "unpaired human marker" not in proc.stdout:
    failures.append("unpaired marker case: expected exit 1 with 'unpaired human marker', got {}\n{}".format(
        proc.returncode, proc.stdout))
else:
    print("ok: unpaired marker case (exit 1)")

# --before without --after is a usage error.
expect("before without after", ["--before", fx("pursuit_pass.md")], 2,
       want_substrings=["--before and --after must be given together"])

if failures:
    print("\nSELFTEST FAILED: {} broken expectation(s)".format(len(failures)))
    for f in failures:
        print("- " + f)
    sys.exit(1)
print("\nSELFTEST PASSED: {} cases, all expectations met".format(cases))
