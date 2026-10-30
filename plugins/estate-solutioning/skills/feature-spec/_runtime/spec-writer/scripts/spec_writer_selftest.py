#!/usr/bin/env python3
"""Selftest for spec-writer. Stdlib only, no network.

This skill carried 42 em dashes, the highest count in the estate, in a file whose
entire job is teaching someone to write a rigorous artifact. The checks pin the
canon and the parts of the method that make a spec verifiable rather than
descriptive: the file manifest with its verbs, the UI states, and done criteria
that can actually be checked.

Exit 0 when every case matches, 1 otherwise.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
MD = SKILL / ("WORKFLOW.md" if SKILL.parent.name == "_runtime" else "SKILL.md")


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
has("requires a file manifest", r"file manifest|manifest")
for verb in ("CREATE", "UPDATE", "DELETE", "READ"):
    if verb not in prose:
        fail.append(f"the {verb} manifest verb is gone")
print("  manifest verbs present")
has("requires all UI states", r"UI states|empty|loading|error")
has("requires observable acceptance", r"observable result")
has("requires a verification method", r"verification method")
has("produces a self-contained artifact", r"self-contained")
has("keeps specification proportional to the request", r"does not automatically require")
has("retains requested delivery form", r"requested form")
has("does not restore mandatory pre-code gate", r"Use before writing any code|Use before you code|Use before touching code", want=False)

if fail:
    print("\nSELFTEST FAILED")
    for f in fail:
        print("  -", f)
    sys.exit(1)
print("\nSELFTEST PASSED")
