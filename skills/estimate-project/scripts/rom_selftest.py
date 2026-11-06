#!/usr/bin/env python3
"""Standalone selftest for rom_gate.py, for estate sync gating.

Runs the gate as a subprocess against both fixtures and asserts exit codes and
key printed findings. Exits nonzero if any expectation fails.
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(HERE, "rom_gate.py")


def run_gate(fixture):
    path = os.path.join(HERE, "fixtures", fixture)
    p = subprocess.run([sys.executable, GATE, path],
                       capture_output=True, text=True)
    return p.returncode, p.stdout


def expect(cond, label, failures):
    print("  %s: %s" % (label, "OK" if cond else "FAIL"))
    if not cond:
        failures.append(label)


def main():
    failures = []

    rc, out = run_gate("rom_pass.json")
    print("fixture rom_pass.json (exit %d)" % rc)
    expect(rc == 0, "passing fixture exits 0", failures)
    expect("RESULT: PASS (0 failures)" in out, "prints PASS result", failures)
    expect("three-way tie: PASS" in out, "three-way tie printed and passing", failures)
    expect("FLAG:" not in out, "no flags on the passing fixture", failures)

    rc, out = run_gate("rom_fail.json")
    print("fixture rom_fail.json (exit %d)" % rc)
    expect(rc == 1, "failing fixture exits 1", failures)
    expect("RESULT: FAIL" in out, "prints FAIL result", failures)
    expect("two-way tie: FAIL" in out, "hour tie failure detected", failures)
    expect("does not reconcile to the quote fee" in out,
           "fee mismatch flagged", failures)
    expect("do not bracket the quote total" in out,
           "range bracket failure flagged", failures)
    expect("never coexist" in out or "conflicts with pricing model" in out,
           "model card conflict flagged", failures)

    print("rom_selftest: %d expectation failure%s"
          % (len(failures), "" if len(failures) == 1 else "s"))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
