#!/usr/bin/env python3
"""Run priority_score.py against its fixtures. Exit 0 when every case behaves as specified."""

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIX = HERE / "fixtures"
UPSTREAM_RICE = {"SRCH": 2666.67, "MOB": 1500.0, "SSO": 1080.0, "DASH": 1050.0, "RATE": 855.0}


def run(*args):
    proc = subprocess.run([sys.executable, str(HERE / "priority_score.py"), *map(str, args)], capture_output=True, text=True)
    return proc.returncode, proc.stdout


def main():
    failures = []
    code, out = run(FIX / "rice_sourced.json", "--framework", "rice", "--format", "json")
    scores = {r["id"]: r["score"] for r in json.loads(out)["ranking"]}
    if code != 0 or scores != UPSTREAM_RICE:
        failures.append(f"sourced RICE: expected the upstream demo scores {UPSTREAM_RICE}, got {scores} (exit {code})")

    code, out = run(FIX / "rice_unsourced.json", "--framework", "rice", "--format", "json")
    report = json.loads(out)
    a = next((r for r in report["ranking"] if r["id"] == "A"), None)
    if code != 1:
        failures.append(f"unsourced RICE: expected exit 1 for the missing field and duplicate ID, got {code}")
    if not a or a["score"] != 750.0:
        failures.append("unsourced RICE: confidence 0.9 without a source should be capped at 0.5 (score 750)")
    if not any("appears more than once" in e for e in report["errors"]) or not any("Missing effort" in e for e in report["errors"]):
        failures.append("unsourced RICE: expected errors for the duplicate ID and the missing effort")

    code, out = run(FIX / "odi.json", "--framework", "odi", "--format", "json")
    rows = {r["id"]: r for r in json.loads(out)["ranking"]}
    if rows["OUT-1"]["score"] != 15.0 or rows["OUT-2"]["score"] != 9.0:
        failures.append("ODI: expected 9 + max(9 - 3, 0) = 15 and 8 + max(8 - 7, 0) = 9")
    if not any("hypothesis" in f for f in rows["OUT-2"]["flags"]):
        failures.append("ODI: an outcome without a customer source should be flagged as a hypothesis")

    code, out = run(FIX / "odi.json", "--framework", "opportunity", "--format", "json")
    rows = {r["id"]: r for r in json.loads(out)["ranking"]}
    if rows["OUT-1"]["score"] != 6.3:
        failures.append(f"Olsen opportunity: expected 9 x (1 - 0.3) = 6.3, got {rows['OUT-1']['score']}")

    for line in failures:
        print("FAIL " + line)
    print(f"{4 - len({f.split(':')[0] for f in failures})} of 4 cases passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
