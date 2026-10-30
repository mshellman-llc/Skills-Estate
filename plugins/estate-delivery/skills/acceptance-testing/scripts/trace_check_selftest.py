#!/usr/bin/env python3
"""Selftest for trace_check.py.

Exercises the gate through the CLI with real files on disk, the same way the
skill runs it, plus the in-process fixture suite (trace_check.py --selftest).
Exits 0 when every case behaves as specified, 1 otherwise. Stdlib only.
"""

import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(HERE, "trace_check.py")

REQS = "Requirement Number,Name\nCPE-001,Auto-apply price\nCPE-002,Tiered pricing\nCPE-003,Audit trail\n"

SCRIPTS_PASS = (
    "Test Script ID,Requirement IDs,Orphan Flag,Title\n"
    "TS-001,CPE-001,,Auto-apply happy path\n"
    "TS-002,\"CPE-001, CPE-002\",,Tier boundaries\n"
    "TS-003,,orphan: legacy smoke test kept by client request,Legacy smoke\n"
)

GAPS_PASS = "Requirement ID,Owner,Reason,Resolve By\nCPE-003,BA,Audit object lands sprint 6,2026-09-01\n"

GONOGO_PASS = (
    '{"total_requirements": 3, "requirements_with_coverage": 2, "named_gaps": 1,'
    ' "test_scripts_total": 3, "orphan_scripts_flagged": 1}'
)

SCRIPTS_UNFLAGGED_ORPHAN = (
    "Test Script ID,Requirement IDs,Orphan Flag\n"
    "TS-001,CPE-001,\nTS-002,CPE-002,\nTS-003,CPE-003,\nTS-004,,\n"
)

SCRIPTS_FULL_COVERAGE = (
    "Test Script ID,Requirement IDs,Orphan Flag\n"
    "TS-001,CPE-001,\nTS-002,CPE-002,\nTS-003,CPE-003,\n"
)

GONOGO_WRONG = '{"total_requirements": 3, "requirements_with_coverage": 2, "test_scripts_total": 5}'


def run_gate(tmp, files, extra_args=()):
    paths = {}
    for name, content in files.items():
        path = os.path.join(tmp, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
        paths[name] = path
    cmd = [sys.executable, GATE, "--requirements", paths["reqs.csv"], "--scripts", paths["scripts.csv"]]
    if "gaps.csv" in paths:
        cmd += ["--gaps", paths["gaps.csv"]]
    if "gonogo.json" in paths:
        cmd += ["--gonogo", paths["gonogo.json"]]
    cmd += list(extra_args)
    return subprocess.run(cmd, capture_output=True, text=True)


def main():
    results = []

    def case(label, cond, detail=""):
        results.append((label, cond, detail))
        print("  %s: %s" % ("pass" if cond else "FAIL", label))
        if not cond and detail:
            print("    " + detail)

    with tempfile.TemporaryDirectory() as tmp:
        r = run_gate(tmp, {"reqs.csv": REQS, "scripts.csv": SCRIPTS_PASS, "gaps.csv": GAPS_PASS, "gonogo.json": GONOGO_PASS})
        case("passing fixture exits 0", r.returncode == 0, r.stdout + r.stderr)
        case("passing fixture prints recomputed counts", "requirements_with_coverage: 2" in r.stdout, r.stdout)

        r = run_gate(tmp, {"reqs.csv": REQS, "scripts.csv": SCRIPTS_PASS})
        case("uncovered requirement with no gap list exits 1", r.returncode == 1, r.stdout)
        case("failure names the requirement", "CPE-003" in r.stdout, r.stdout)

        r = run_gate(tmp, {"reqs.csv": REQS, "scripts.csv": SCRIPTS_UNFLAGGED_ORPHAN})
        case("unflagged orphan script exits 1", r.returncode == 1, r.stdout)
        case("failure names the orphan script", "TS-004" in r.stdout, r.stdout)

        r = run_gate(tmp, {"reqs.csv": REQS, "scripts.csv": SCRIPTS_FULL_COVERAGE, "gonogo.json": GONOGO_WRONG})
        case("go/no-go count mismatch exits 1", r.returncode == 1, r.stdout)
        case("mismatch report shows stated and recomputed values", "count mismatch" in r.stdout, r.stdout)

        r = run_gate(tmp, {"reqs.csv": REQS, "scripts.csv": SCRIPTS_FULL_COVERAGE})
        case("full coverage with no gaps file exits 0", r.returncode == 0, r.stdout)

        r = subprocess.run([sys.executable, GATE, "--requirements", os.path.join(tmp, "missing.csv"),
                            "--scripts", os.path.join(tmp, "scripts.csv")], capture_output=True, text=True)
        case("missing input file exits 2", r.returncode == 2, r.stderr)

    r = subprocess.run([sys.executable, GATE, "--selftest"], capture_output=True, text=True)
    print(r.stdout, end="")
    results.append(("embedded --selftest passes", r.returncode == 0, r.stdout))

    failed = [label for label, cond, _ in results if not cond]
    print("SELFTEST %s: %d/%d cases passed" % ("PASSED" if not failed else "FAILED", len(results) - len(failed), len(results)))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
