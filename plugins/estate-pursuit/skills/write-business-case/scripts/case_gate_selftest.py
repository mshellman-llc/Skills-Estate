#!/usr/bin/env python3
"""Selftest for case_gate.py. Runs the gate against the fixtures and asserts
exit codes and the specific check that fired. The em-dash fixture is
materialized at runtime so the shipped tree contains no em dash anywhere.

Usage: python3 case_gate_selftest.py
Exit 0 on pass, 1 on fail. Stdlib only.
"""

import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(HERE, "case_gate.py")
FIXTURES = os.path.join(HERE, "fixtures")


def run_gate(path):
    proc = subprocess.run(
        [sys.executable, GATE, path], capture_output=True, text=True
    )
    return proc.returncode, proc.stdout + proc.stderr


CASES = [
    ("pass_case.md", 0, "0 fail"),
    ("fail_missing_case_against.md", 1, "missing: case against"),
    ("fail_thin_case_against.md", 1, "case-against section too thin"),
    ("fail_unsourced_figure.md", 1, "figure without a source token"),
    ("fail_bad_arithmetic.md", 1, "arithmetic does not compute"),
]


def main():
    failures = []

    for name, want_code, want_text in CASES:
        path = os.path.join(FIXTURES, name)
        code, out = run_gate(path)
        if code != want_code:
            failures.append(f"{name}: exit {code}, wanted {want_code}")
        if want_text not in out:
            failures.append(f"{name}: output missing {want_text!r}")

    # em-dash fixture, built at runtime so no em dash ships in the tree
    base = open(os.path.join(FIXTURES, "pass_case.md"), encoding="utf-8").read()
    dashed = base.replace(
        "The decisive factor is", "The decisive factor \u2014 timing \u2014 is", 1
    )
    with tempfile.NamedTemporaryFile(
        "w", suffix=".md", encoding="utf-8", delete=False
    ) as tmp:
        tmp.write(dashed)
        tmp_path = tmp.name
    try:
        code, out = run_gate(tmp_path)
        if code != 1:
            failures.append(f"em-dash fixture: exit {code}, wanted 1")
        if "em dash present" not in out:
            failures.append("em-dash fixture: output missing 'em dash present'")
    finally:
        os.unlink(tmp_path)

    # usage error path
    code, _ = run_gate(os.path.join(FIXTURES, "does_not_exist.md"))
    if code != 2:
        failures.append(f"missing-file path: exit {code}, wanted 2")

    total = len(CASES) + 2
    if failures:
        for f in failures:
            print(f"SELFTEST FAIL {f}")
        print(f"case_gate_selftest: {len(failures)} failed of {total} checks")
        return 1
    print(f"case_gate_selftest: PASS ({total} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
