#!/usr/bin/env python3
"""Selftest for deck-builder. Stdlib only, no network.

This skill is an orchestrator: it owns the process and defers brand to
brand-renderer and copy to prose-pass. That deferral is the reason it
does not collide with anything, so it is asserted by name, along with the
one-message gate that stops a deck being designed before its argument is settled.

It also used to hardcode ~/Work paths from one person's filing convention. A
skill that assumes your folder layout breaks for everyone else.

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
prose = re.sub(r"```.*?```", "", text, flags=re.S)


def expect(label, got, want):
    ok = got == want
    print(f"  {label:54} got={str(got):<7} want={want}")
    if not ok:
        fail.append(f"{label}: got {got}, want {want}")
    return ok


def has(label, pattern, want=True):
    return expect(label, bool(re.search(pattern, prose, re.I | re.S)), want)


expect("no em dashes", text.count("\u2014"), 0)
expect("no section sign", text.count("\u00a7"), 0)
size = len(text.encode())
print(f"  SKILL.md is {size} bytes (budget 12288)")
expect("under the size budget", size <= 12288, True)

fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
expect("has frontmatter", bool(fm), True)
if fm:
    keys = set(re.findall(r"^([A-Za-z_][\w-]*):", fm.group(1), re.M))
    expect("only house frontmatter keys", sorted(keys - {"name", "description", "license"}), [])
    expect("name matches the folder",
           re.search(r"^name:\s*\"?([\w-]+)", fm.group(1), re.M).group(1), SKILL.name)
    desc = re.search(r"^description:\s*(.*)", fm.group(1), re.M | re.S).group(1).strip().strip('"')
    print(f"  description is {len(desc)} chars (claude.ai limit 1024)")
    expect("description under the surface limit", len(desc) <= 1024, True)

# no path that only exists on one surface or one machine
for pat, label in ((r"/mnt/skills", "hardcoded /mnt/skills path"),
                   (r"/Users/\w+", "absolute home path")):
    expect(f"no {label}", bool(re.search(pat, text)), False)

promised = set(re.findall(r"references/([a-z0-9-]+\.md)", text))
missing = [r for r in sorted(promised) if not _resolves(r)]
print(f"\n  cites {len(promised)} reference(s), missing: {missing or 'none'}")
if missing:
    fail.append(f"missing references: {missing}")
refdir = SKILL / "references"
if refdir.exists():
    orphans = [f.name for f in refdir.glob("*.md") if f.name not in promised]
    expect("no orphaned references", orphans, [])


print()
has("defers brand to the renderer", r"brand-renderer")
has("defers copy to prose-pass", r"prose-pass")
expect("no hardcoded engagement folder", bool(re.search(r"~/Work", text)), False)
has("resolves the folder instead of assuming", r"[Rr]esolve it, do not assume|do not assume one")

has("keeps the one-message gate", r"one-message gate|gate up front")
has("locks the argument before design", r"lock the argument|argument before")
has("keeps the polish loop", r"polish")

if fail:
    print("\nSELFTEST FAILED")
    for f in fail:
        print("  -", f)
    sys.exit(1)
print("\nSELFTEST PASSED")
