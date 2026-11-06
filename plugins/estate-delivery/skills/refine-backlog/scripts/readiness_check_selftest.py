#!/usr/bin/env python3
"""Run readiness_check.py against its fixtures. Exit 0 when every case behaves as specified."""

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIX = HERE / "fixtures"
EXPECTED = {"ONB-001": "READY", "ONB-002": "READY", "ONB-003": "REFINE", "ONB-004": "DISCOVERY"}


def run(*args):
    proc = subprocess.run([sys.executable, str(HERE / "readiness_check.py"), *map(str, args)], capture_output=True, text=True)
    return proc.returncode, proc.stdout


def main():
    failures = []
    code, out = run(FIX / "requirements.csv", "--raid-log", FIX / "RAID.md", "--format", "json")
    verdicts = {row["id"]: row["verdict"] for row in json.loads(out)["items"]}
    if code != 1:
        failures.append(f"full backlog: expected exit 1 because two items are not ready, got {code}")
    if verdicts != EXPECTED:
        failures.append(f"full backlog: expected {EXPECTED}, got {verdicts}")

    code, _ = run(FIX / "requirements.csv", "--raid-log", FIX / "RAID.md", "--ids", "ONB-001,ONB-002")
    if code != 0:
        failures.append(f"ready subset: expected exit 0, got {code}")

    code, out = run(FIX / "requirements.csv", "--format", "json")
    onb1 = next(r for r in json.loads(out)["items"] if r["id"] == "ONB-001")
    if onb1["verdict"] != "READY":
        failures.append("no RAID log: a D-### dependency should still count as tracked")

    code, _ = run(FIX / "requirements.csv", "--ids", "ONB-404")
    if code != 2:
        failures.append(f"unknown ID: expected exit 2, got {code}")

    for line in failures:
        print("FAIL " + line)
    print(f"{4 - len(failures)} of 4 cases passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
