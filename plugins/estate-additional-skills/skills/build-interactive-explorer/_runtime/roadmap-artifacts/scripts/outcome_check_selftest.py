#!/usr/bin/env python3
"""Run outcome_check.py against the worked example and its fixtures. Exit 0 when every case behaves as specified."""

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent


def run(path):
    proc = subprocess.run([sys.executable, str(HERE / "outcome_check.py"), str(path), "--format", "json"],
                          capture_output=True, text=True)
    return proc.returncode, proc.stdout


def main():
    failures = []
    code, out = run(SKILL / "examples" / "01-now-next-later.json")
    if code != 0:
        failures.append(f"worked example: expected exit 0, got {code}")
    elif any(f["level"] == "fail" for f in json.loads(out)["findings"]):
        failures.append("worked example: expected no failures")

    code, out = run(HERE / "fixtures" / "outcome_fail.json")
    messages = [f"{f['level']}:{f['card']}:{f['message']}" for f in json.loads(out)["findings"]] if out else []
    expected = [
        ("fail:None:Now holds 4 cards", "the Now cap"),
        ("fail:n2:Now card has no Outcome", "a Now card without an Outcome"),
        ("fail:n3:Now Outcome names no number", "an Outcome without a number"),
        ("warn:n4:Outcome repeats card n1", "a repeated Outcome"),
        ("warn:x1:Next card has no Outcome", "a Next card without an Outcome"),
        ("warn:l1:Later card carries precision", "dates and priority labels in Later"),
    ]
    if code != 1:
        failures.append(f"failure plan: expected exit 1, got {code}")
    for prefix, label in expected:
        if not any(m.startswith(prefix) for m in messages):
            failures.append(f"failure plan: expected a finding for {label}")

    code, _ = run(HERE / "fixtures" / "no_board.json")
    if code != 2:
        failures.append(f"plan without a Now column: expected exit 2, got {code}")
    code, _ = run(HERE / "fixtures" / "missing.json")
    if code != 2:
        failures.append(f"missing file: expected exit 2, got {code}")

    for line in failures:
        print("FAIL", line)
    print("SELFTEST PASSED" if not failures else f"SELFTEST FAILED ({len(failures)})")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
