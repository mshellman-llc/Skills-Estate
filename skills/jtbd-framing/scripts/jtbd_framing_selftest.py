#!/usr/bin/env python3
"""Selftest for jtbd-framing. Stdlib only, no network.

This skill was 67 percent over the size budget because the body restated
its own eight reference files. The trim moved that detail out, so the checks
guard what the trim put at risk: every reference still cited and still
substantive, and the body no longer re-teaching what the references hold.

The other check is the differentiator. Plenty of JTBD material explains job
statements. What makes this one worth loading is that it is honest about where
the framework becomes ritual, so that section is asserted by name.

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
    expect("description says when to trigger",
           bool(re.search(r"use (this )?(skill )?wh|triggers? on|use it when", desc, re.I)), True)

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


# --- the honesty that differentiates this from generic JTBD material ----------
print()
has("keeps the ritual-versus-clarity section", r"becomes ritual")
has("names workshop-as-deliverable", r"workshop.{0,40}deliverable")
has("gives the litmus test for real use", r"litmus|traced? to the (JTBD )?analysis")
has("requires jobs come from data", r"jobs come from data|derived from data|from the data")

# --- the mechanics are named, but not re-taught at length ---------------------
for term in ("situation", "motivation", "outcome", "struggling moment",
             "hire", "fire", "functional", "emotional", "social"):
    if term not in prose.lower():
        fail.append(f"the {term!r} mechanic is no longer mentioned")
print("  all nine mechanics still named")

# The trim's failure mode is deleting rather than relocating. The references must
# still be where the detail went.
sizes = {f.name: f.stat().st_size for f in (SKILL / "references").glob("*.md")}
print(f"  references hold {sum(sizes.values())} bytes across {len(sizes)} files")
expect("references carry the detail", sum(sizes.values()) > 60000, True)
expect("body is smaller than its references", len(text.encode()) < sum(sizes.values()), True)

if fail:
    print("\nSELFTEST FAILED")
    for f in fail:
        print("  -", f)
    sys.exit(1)
print("\nSELFTEST PASSED")
