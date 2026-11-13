#!/usr/bin/env python3
"""Self-test for evidence_scan.py with synthetic fixtures."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from evidence_scan import per_line, scan  # noqa: E402

LEDGER = """# Results

Approval time fell 75% from 4.2 days to 1.1 days across 1,400 quotes in 6 weeks, saving $310K.
"""
CLEAN = """# Results

Discount rules now run before a quote reaches finance, so approvals that took most of a week now close the next day.
"""
RIGOR = """# Why it works

Our data-driven approach is backed by hard data, and every figure in this case study is fully sourced.
"""
LEAK = """# Approach

The load-bearing claim sits in the evidence file, checked at the gate packet stage [S12].
"""
STEPS = """# Inputs

1. The goal for the run.
2. A filled owner profile.
3. The rules folder, see [guide](https://example.com/2024/04/guide).
"""
PARTS = """[0001] L2: # Results
[0002] L3: Approval time fell from most of a week to the next day.
[0003] L4: The pilot ran with one sales team in Atlanta.
[0004] L5: Quotes now reach finance with discounts already checked.
"""
LABELS = """# Run

Steps in order: 1 scout topics, where you pick one; 2 research; 3 collect your evidence; 4 write the brief; 5 draft; 5b make figures; 6 edit.

Step 3 asks for the opening, Figure 2 shows steps 1 to 9, and gates 7 and 9 need a signature.
"""
COUNTS = """# Scale

We moved 3 regions, 12 teams and 40% of quotes in one quarter.
"""
YEARS = """# Timeline

The team started in 2024 and finished in 2026 after one pilot.
"""


def rules(findings):
    return {f["rule"] for f in findings}


def run():
    assert {"figures-per-paragraph", "section-density"} <= rules(scan(LEDGER)), "ledger paragraph not flagged"
    assert scan(LEDGER, data_piece=True) == [], "data piece should skip density limits"
    assert scan(CLEAN) == [], f"clean paragraph flagged: {scan(CLEAN)}"
    r = scan(RIGOR)
    assert sum(1 for f in r if f["rule"] == "rigor-talk") >= 3, f"rigor talk missed: {r}"
    leak = scan(LEAK)
    assert sum(1 for f in leak if f["rule"] == "production-vocabulary") >= 4, f"leak missed: {leak}"
    assert scan(LEAK, published=False) == [], "internal documents may use production vocabulary"
    assert scan(YEARS) == [], "years are dates, not figures"
    assert scan(STEPS) == [], f"list markers and link targets are not figures: {scan(STEPS)}"
    assert scan(per_line(PARTS)) == [], f"one line per paragraph: {scan(per_line(PARTS))}"
    assert per_line(PARTS).splitlines()[0] == "# Results", "review prefixes are removed"
    assert scan(LABELS) == [], f"step and figure labels are not figures: {scan(LABELS)}"
    assert "figures-per-paragraph" in rules(scan(COUNTS)), "real counts must still be flagged"
    print("evidence_scan selftest: 12 checks passed")


if __name__ == "__main__":
    run()
