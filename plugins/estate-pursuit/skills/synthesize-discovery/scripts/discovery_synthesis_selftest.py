#!/usr/bin/env python3
"""Selftest for synthesize-discovery. Stdlib only, no network.

Two things this skill got wrong were invisible until checked.

It pointed at the granola skill path for pulling transcripts. No Granola skill
exists, on any surface. Granola is an MCP connector, so the instruction sent the
reader to a file that was never there.

It is distinct from `maintain-discovery-record`, which owns the deal's discovery record: both
produce job statements from interview data. They are pipeline and method rather
than duplicates, but an unstated overlap routes at random, so the boundary is
asserted from both sides.

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
expect("no dead granola skill path", bool(re.search(r"granola/SKILL\.md", text, re.I)), False)
has("routes Granola through the connector", r"Granola MCP connector|get_meeting_transcript")
has("says there is no Granola skill", r"no Granola skill")
expect("no /mnt paths for docx or pdf", bool(re.search(r"/mnt/skills/public", text)), False)
has("tells the reader to resolve skills, not paths", r"available skills")

has("states the maintain-discovery-record boundary", r"##\s*Boundary with the discovery brief")
has("names maintain-discovery-record as the record owner", r"maintain-discovery-record")

for output in ("JTBD", "pain point", "verbatim", "TL;DR", "next step"):
    if output.lower() not in prose.lower():
        fail.append(f"the {output!r} output is no longer produced")
print("  all five outputs still named")
has("attributes insights to speakers", r"speaker")

if fail:
    print("\nSELFTEST FAILED")
    for f in fail:
        print("  -", f)
    sys.exit(1)
print("\nSELFTEST PASSED")
