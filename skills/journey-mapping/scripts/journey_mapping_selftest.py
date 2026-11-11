#!/usr/bin/env python3
"""Selftest for journey-mapping. Stdlib only, no network.

This skill was 24 percent over the size budget because SKILL.md restated what
references/journey-map-template.md already held: the lane structure, the
blueprint layers, the opportunity tables, and a full markdown template. The trim
moved that detail to the reference and left pointers. So the checks guard the two
things that trim put at risk.

  1. The pointers resolve. Every claim SKILL.md makes about what lives in the
     reference must be true, or the skill sends a reader to a file that does not
     answer them.
  2. The detail did not simply vanish. The reference must still carry the lanes,
     the blueprint layers, the ledger, the opportunity map, and all five phase
     presets. A trim that deletes rather than relocates is a regression wearing
     the costume of a fix.

Plus canon: the skill's own House rules forbid em dashes and the section sign,
and a skill that states a rule then breaks it is not credible.

Exit 0 when every case matches, 1 otherwise.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
MD = SKILL / "SKILL.md"
REF = SKILL / "references" / "journey-map-template.md"


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
text = MD.read_text(encoding="utf-8")


def expect(label: str, got, want):
    ok = got == want
    print(f"  {label:54} got={str(got):<7} want={want}")
    if not ok:
        fail.append(f"{label}: got {got}, want {want}")
    return ok


# --- it obeys the rules it states --------------------------------------------
expect("no em dashes", text.count("—"), 0)
expect("no section sign", text.count("§"), 0)
expect("it states the no-em-dash rule", "No em dashes" in text, True)

size = len(text.encode())
print(f"  SKILL.md is {size} bytes (budget 12288)")
expect("SKILL.md under the 12 KB budget", size <= 12288, True)

fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
if fm:
    keys = set(re.findall(r"^([A-Za-z_][\w-]*):", fm.group(1), re.M))
    expect("only house frontmatter keys", sorted(keys - {"name", "description", "license"}), [])
    desc = re.search(r"description:\s*(.*)", fm.group(1), re.S)
    n = len(desc.group(1).strip().strip('"')) if desc else 0
    print(f"  description is {n} chars (claude.ai limit 1024)")
    expect("description under the surface limit", n <= 1024, True)

# --- the reference still carries what the trim relocated ----------------------
print()
if not REF.exists():
    print(f"  missing {REF}")
    sys.exit(1)
ref = REF.read_text(encoding="utf-8")

REQUIRED_IN_REF = {
    "the journey-map lane table": r"\|\s*Phase\s*\|\s*Step\s*\|\s*Touchpoint",
    "service blueprint layers": r"##\s*Service blueprint layers",
    "front-stage actions": r"Front-stage actions",
    "back-stage actions": r"Back-stage actions",
    "supporting systems": r"Supporting systems",
    "the source and confidence ledger": r"##\s*Source and confidence ledger",
    "the opportunity map": r"##\s*Opportunity map",
    "the pre-ship checklist": r"##\s*Pre-ship checklist",
}
for label, pattern in REQUIRED_IN_REF.items():
    expect(f"reference carries {label}", bool(re.search(pattern, ref, re.I)), True)

# all five phase presets survived the move out of SKILL.md
PRESETS = ("Most products", "SaaS", "Service business", "CX engagement",
           "Estate internal lifecycle")
absent = [p for p in PRESETS if p.lower() not in ref.lower()]
expect("all five phase presets are in the reference", absent, [])
arrows = ref.count("->")
print(f"  reference carries {arrows} phase-sequence arrows")
expect("the presets kept their sequences", arrows >= 30, True)

# --- every pointer SKILL.md makes actually resolves ---------------------------
print()
pointers = re.findall(r"`references/([A-Za-z0-9_.-]+)`", text)
expect("SKILL.md points at the reference", len(pointers) >= 1, True)
for name in sorted(set(pointers)):
    expect(f"  references/{name} exists", (SKILL / "references" / name).exists(), True)

# SKILL.md must not have kept a second copy of the detail it moved out
expect("no lane table left in SKILL.md",
       bool(re.search(r"\|\s*Phase\s*\|\s*Step\s*\|", text)), False)
expect("no markdown output template left in SKILL.md",
       "```markdown" in text, False)

# --- the skill's self-containment claim is honest -----------------------------
# It states it needs no other skill. Verify it does not secretly require one.
claims_self_contained = "self-contained" in text.lower()
expect("claims to be self-contained", claims_self_contained, True)
if claims_self_contained:
    # a hard dependency would look like a path into a sibling skill
    sibling = re.findall(r"`(?:\.\./)?(estate-[a-z-]+|prose-pass)/", text)
    expect("  and cites no sibling skill path", sorted(set(sibling)), [])

# --- integrity ----------------------------------------------------------------
promised = set(re.findall(r"`([A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:md|py|json))`", text))
missing = [r for r in sorted(promised)
           if not _resolves(r)]
print(f"\n  SKILL.md promises {len(promised)} files, missing: {missing or 'none'}")
if missing:
    fail.append(f"missing promised files: {missing}")

if fail:
    print("\nSELFTEST FAILED")
    for f in fail:
        print("  -", f)
    sys.exit(1)
print("\nSELFTEST PASSED")
