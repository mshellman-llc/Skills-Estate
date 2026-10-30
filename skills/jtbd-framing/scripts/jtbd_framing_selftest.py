#!/usr/bin/env python3
"""Selftest for jtbd-framing. Stdlib only, no network.

The estate migration on 2026-10-19 cut this skill to four paragraphs and
dropped its eight references. The restore put them back, so the checks guard
what that cut removed: every reference cited and substantive, the four
mechanics named, the audit intact, and the section on where JTBD becomes
ritual, which is what separates this skill from generic JTBD material. They
also guard the hypothesis rule and the link to journey-mapping.

Exit 0 when every case matches, 1 otherwise.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
MD = SKILL / "SKILL.md"
REFDIR = SKILL / "references"

fail: list[str] = []
text = MD.read_text(encoding="utf-8")


def expect(label, got, want):
    print(f"  {label:58} got={str(got):<7} want={want}")
    if got != want:
        fail.append(f"{label}: got {got}, want {want}")


def has(label, pattern):
    expect(label, bool(re.search(pattern, text, re.I | re.S)), True)


# --- frontmatter -------------------------------------------------------------
fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
expect("has frontmatter", bool(fm), True)
if fm:
    expect("name matches the folder", re.search(r"^name:\s*(\S+)", fm.group(1), re.M).group(1), SKILL.name)
    desc = re.search(r'^description:\s*"(.*)"\s*$', fm.group(1), re.M)
    n = len(desc.group(1)) if desc else 0
    print(f"  description is {n} chars (surface limit 1024)")
    expect("description under the surface limit", 0 < n <= 1024, True)
    expect("description says when to trigger", bool(desc and re.search(r"triggers? on|use it", desc.group(1), re.I)), True)
    expect("no upstream name outside LICENSE", "rampstack" in fm.group(1).lower(), False)
expect("license file present", (SKILL / "LICENSE").exists(), True)

# --- references cited, present, substantive ----------------------------------
print()
cited = set(re.findall(r"\]\(references/([a-z0-9-]+\.md)\)", text))
present = {f.name for f in REFDIR.glob("*.md")}
expect("eight references present", len(present), 8)
expect("every cited reference exists", sorted(cited - present), [])
expect("no orphaned references", sorted(present - cited), [])
expect("no stub references", [f.name for f in REFDIR.glob("*.md") if f.stat().st_size < 4000], [])
total = sum(f.stat().st_size for f in REFDIR.glob("*.md"))
print(f"  references hold {total} bytes")
expect("references carry the detail", total > 60000, True)
expect("eleven failures in the failures reference",
       len(re.findall(r"^## Failure \d+", (REFDIR / "common-jtbd-failures.md").read_text(encoding="utf-8"), re.M)), 11)

# --- the method --------------------------------------------------------------
print()
has("keeps the ritual-versus-clarity section", r"## Where JTBD adds clarity and where it becomes ritual")
has("names workshop-as-deliverable", r"workshop.{0,60}deliverable")
has("gives the litmus test", r"litmus test")
has("requires jobs come from data", r"Jobs come from data")
has("marks hypotheses instead of fabricating", r"marked as hypotheses")
has("shows evidence as references, not repeated labels", r"## Showing evidence.{0,600}evidence list")
has("links job framing to journey-mapping", r"`journey-mapping`")
for term in ("situation", "motivation", "outcome", "struggling moment",
             "hire", "fire", "functional", "emotional", "social"):
    if term not in text.lower():
        fail.append(f"the {term!r} mechanic is no longer mentioned")
expect("twelve audit checks", len(re.findall(r"^\d+\. ", text.split("## The audit")[1].split("##")[0], re.M)), 12)

# --- identity ----------------------------------------------------------------
print()
for doc in [MD, *sorted(REFDIR.glob("*.md"))]:
    hits = re.findall(r"(?i)aleysian|meridian", doc.read_text(encoding="utf-8"))
    if hits:
        fail.append(f"former identity in {doc.name}")
print("  identity check done")

if fail:
    print("\nSELFTEST FAILED")
    for f in fail:
        print("  -", f)
    sys.exit(1)
print("\nSELFTEST PASSED")
