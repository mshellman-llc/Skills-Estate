#!/usr/bin/env python3
"""Selftest for design-software-system. Stdlib only, no network.

This skill overlaps write-architecture-reference's second altitude, which
covers the same requirements, data model, API and trade-offs ground. They are
different jobs: this one produces a working design inline, that one produces a
sourced, gated, branded artifact. An overlap that is not stated is an overlap
that routes at random, so the boundary is asserted from both sides. The
cross-skill half resolves the embedded workflow in a portable package and fails
when the promised formal workflow is missing.

The other check is the assumption rule. A design that invents load figures and
presents them as fact is worse than one that says it does not know.

Exit 0 when every case matches, 1 otherwise.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
MD = SKILL / "SKILL.md"


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
# This skill documents structure, so heading-shaped lines inside a fence are
# examples, not sections. Strip fences before any structural check.
prose = re.sub(r"```.*?```", "", text, flags=re.S)


def expect(label, got, want):
    ok = got == want
    print(f"  {label:54} got={str(got):<7} want={want}")
    if not ok:
        fail.append(f"{label}: got {got}, want {want}")
    return ok


def has(label, pattern, in_prose=True, want=True):
    hay = prose if in_prose else text
    return expect(label, bool(re.search(pattern, hay, re.I | re.S)), want)


# --- house canon --------------------------------------------------------------
expect("no em dashes", text.count("\u2014"), 0)
expect("no section sign", text.count("\u00a7"), 0)

size = len(text.encode())
print(f"  SKILL.md is {size} bytes (budget 12288)")
expect("under the size budget", size <= 12288, True)

fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
expect("has frontmatter", bool(fm), True)
if fm:
    keys = set(re.findall(r"^([A-Za-z_][\w-]*):", fm.group(1), re.M))
    expect("only house frontmatter keys",
           sorted(keys - {"name", "description", "license"}), [])
    expect("name matches the folder", re.search(r"^name:\s*(\S+)", fm.group(1), re.M).group(1),
           SKILL.name)
    desc = re.search(r"^description:\s*(.*)", fm.group(1), re.M | re.S).group(1).strip().strip('"')
    print(f"  description is {len(desc)} chars (claude.ai limit 1024)")
    expect("description under the surface limit", len(desc) <= 1024, True)
    expect("description is nonempty",
           bool(desc.strip()), True)

# --- promised files exist ------------------------------------------------------
promised = set(re.findall(r"`?\[?`?([a-z0-9-]+\.md)`?\]?\(references/", text))
promised |= set(re.findall(r"references/([a-z0-9-]+\.md)", text))
missing = [r for r in sorted(promised) if not _resolves(r)]
print(f"\n  cites {len(promised)} reference(s), missing: {missing or 'none'}")
if missing:
    fail.append(f"missing references: {missing}")

refdir = SKILL / "references"
if refdir.exists():
    thin = [f.name for f in refdir.glob("*.md") if f.stat().st_size < 400]
    expect("no stub references", thin, [])
    orphans = [f.name for f in refdir.glob("*.md") if f.name not in promised]
    expect("no orphaned references", orphans, [])


# --- the boundary is stated, from both sides -----------------------------------
print()
has("names write-architecture-reference", r"write-architecture-reference")
has("says what routes to the other one", r"formal sourced reference|branded|client-facing|gated")
has("has a When NOT to use", r"##\s*When NOT to use")

sibling = (SKILL / "_runtime/write-architecture-reference/WORKFLOW.md"
           if (SKILL / "_runtime").is_dir()
           else SKILL.parent / "write-architecture-reference" / "SKILL.md")
if sibling.exists():
    sib = sibling.read_text(encoding="utf-8")
    expect("  the sibling points back here", "design-software-system`" in sib or "`design-software-system" in sib, True)
else:
    fail.append("required formal architecture workflow is missing")

# --- the rule that keeps a design honest ---------------------------------------
has("requires assumptions be stated and marked", r"state assumptions|assume-and-mark|assumptions? before")
has("forbids inventing load figures", r"do not invent|Do not invent")
has("requires a named trade-off per choice", r"trade-?off")
has("requires the arithmetic be shown", r"show the arithmetic|Show the arithmetic")
has("degrades when the filesystem is ephemeral", r"ephemeral")

if fail:
    print("\nSELFTEST FAILED")
    for f in fail:
        print("  -", f)
    sys.exit(1)
print("\nSELFTEST PASSED")
