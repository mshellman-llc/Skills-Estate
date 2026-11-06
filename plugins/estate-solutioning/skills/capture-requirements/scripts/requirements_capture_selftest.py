#!/usr/bin/env python3
"""Selftest for capture-requirements. Stdlib only, no network, no Excel.

This skill ships no executable. Its output is a workbook whose exact column set
is the contract with whoever consumes it downstream, so the thing worth pinning
is that the format reference still specifies that contract completely.

Two live details get asserted by name because both have failed elsewhere in the
estate: the Requirement Count column must stay a live COUNTIF formula rather than
a hardcoded number, and the Epic column must be documented as matching the Epics
tab, which is what makes the formula resolve at all. A reference that quietly
loses either one produces a workbook that looks right and does not add up.

Exit 0 when every case matches, 1 otherwise.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
FORMAT = SKILL / "references" / "excel-workbook-format.md"
GHERKIN = SKILL / "references" / "gherkin-and-questions.md"


def _resolves(rel: str) -> bool:
    """True when a promised file exists, here or in a sibling skill.

    Skills cite files across the estate (a prose register, the shared build
    card). Those are real promises and must be checked, but they do not live
    under this skill, so a same-dir-only lookup reports them missing.
    """
    for cand in (SKILL / rel, SKILL / "scripts" / rel, SKILL / "references" / rel,
                 SKILL.parent / rel):
        if cand.exists():
            return True
    name = Path(rel).name
    return any(SKILL.parent.glob(f"*/**/{name}")) or any(SKILL.parent.glob(f"_shared/**/{name}"))


fail: list[str] = []


def expect(label: str, got, want):
    ok = got == want
    print(f"  {label:54} got={str(got):<7} want={want}")
    if not ok:
        fail.append(f"{label}: got {got}, want {want}")
    return ok


if not FORMAT.exists():
    print(f"  missing {FORMAT}")
    sys.exit(1)
fmt = FORMAT.read_text(encoding="utf-8")

# --- the workbook contract is fully specified --------------------------------
# Column names are the backtick-quoted cells in the format tables.
columns = set(re.findall(r"\|\s*\d+\s*\|\s*`([^`]+)`", fmt))
print(f"  format reference specifies {len(columns)} columns")

EPICS_TAB = {"Epic Name", "Prefix", "Capability", "Business Need", "Requirement Count"}
REQ_TAB = {"Requirement Number", "Name", "Epic", "Capability",
           "As A", "I Want To", "So That", "Acceptance Criteria"}

for label, need in (("Epics tab", EPICS_TAB), ("Requirements tab", REQ_TAB)):
    absent = sorted(need - columns)
    expect(f"{label} columns all documented", absent, [])

# both tabs are named
for tab in ("Epics", "Requirements"):
    expect(f'the "{tab}" tab is named', bool(re.search(rf'"{tab}"', fmt)), True)

# --- the two details that fail silently when lost ----------------------------
expect("Requirement Count is a live COUNTIF formula",
       bool(re.search(r"COUNTIF\(\s*Requirements!", fmt)), True)
expect("and is explicitly never hardcoded",
       bool(re.search(r"never a hardcoded number", fmt, re.I)), True)
expect("Epic column must match the Epics tab",
       bool(re.search(r"match.{0,40}Epics tab", fmt, re.I)), True)

# --- acceptance criteria are Gherkin, and the reference says how -------------
if GHERKIN.exists():
    g = GHERKIN.read_text(encoding="utf-8")
    for kw in ("Given", "When", "Then"):
        expect(f"gherkin reference documents {kw}", kw in g, True)
    expect("gherkin reference is substantive", len(g) > 500, True)
else:
    fail.append("missing references/gherkin-and-questions.md")

# SKILL.md and the format reference agree on Gherkin
skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
expect("SKILL.md names Gherkin", "gherkin" in skill_text.lower(), True)

# --- every file SKILL.md promises exists -------------------------------------
promised = set(re.findall(r"`([A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:md|py|json|xlsx|csv))`", skill_text))
# This skill deliberately borrows the public `xlsx` skill's recalc step and says
# so, with a "look for it in your available skills" caveat. It is not shipped
# here and must not be. The versioned workbooks are illustrative output names.
BORROWED = {"scripts/recalc.py", "recalc.py"}
EXAMPLES = {"requirements_v1.xlsx", "requirements_v2.xlsx"}
missing = [r for r in sorted(promised)
           if r not in BORROWED and r not in EXAMPLES
           and not r.startswith("_shared/") and not r.startswith("/mnt/")
           and not _resolves(r)]

# the borrowed dependency must stay caveated, not harden into a bare path
for b in BORROWED & promised:
    expect(f"{b} is marked as the xlsx skill's",
           bool(re.search(r"xlsx.{0,400}" + re.escape(b), skill_text, re.S | re.I)), True)
print(f"\n  SKILL.md promises {len(promised)} files, missing: {missing or 'none'}")
if missing:
    fail.append(f"missing promised files: {missing}")

if fail:
    print("\nSELFTEST FAILED")
    for f in fail:
        print("  -", f)
    sys.exit(1)
print("\nSELFTEST PASSED")
