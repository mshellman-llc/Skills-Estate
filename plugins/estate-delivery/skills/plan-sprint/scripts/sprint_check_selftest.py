#!/usr/bin/env python3
"""Run sprint_check.py against its fixtures. Exit 0 when every case behaves as specified."""

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIX = HERE / "fixtures"


def run(*args):
    proc = subprocess.run([sys.executable, str(HERE / "sprint_check.py"), *map(str, args)], capture_output=True, text=True)
    return proc.returncode, proc.stdout


def main():
    failures = []
    common = ["--readiness", FIX / "readiness.json", "--raid-log", FIX / "RAID.md", "--format", "json"]

    code, out = run(FIX / "plan_pass.json", *common)
    report = json.loads(out)
    if code != 0 or report["counts"]["fail"]:
        failures.append(f"plan_pass: expected exit 0 with no fail findings, got {code} and {report['counts']}")
    if report["capacity_hours"] != 75.6:
        failures.append(f"plan_pass: expected 75.6 h capacity, got {report['capacity_hours']}")

    code, out = run(FIX / "plan_fail.json", *common)
    report = json.loads(out)
    messages = " ".join(f["message"] for f in report["findings"] if f["severity"] == "fail")
    expected = ["No sprint goal", "verdict is REFINE", "D-009 has no owner", "D-009 is not in the RAID log", "against 30 h of capacity"]
    if code != 1:
        failures.append(f"plan_fail: expected exit 1, got {code}")
    failures += [f"plan_fail: missing fail finding '{e}'" for e in expected if e not in messages]

    code, _ = run(FIX / "missing.json")
    if code != 2:
        failures.append(f"missing input: expected exit 2, got {code}")

    for line in failures:
        print("FAIL " + line)
    print(f"{3 - len({f.split(':')[0] for f in failures})} of 3 cases passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
