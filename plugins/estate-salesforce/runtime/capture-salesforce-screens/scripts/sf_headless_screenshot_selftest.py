#!/usr/bin/env python3
"""Selftest for capture-salesforce-screens. Stdlib only, no network.

Checks SKILL.md structural correctness (frontmatter, size, house canon),
that promised references exist, that key operational concepts are documented
(credential safety, readiness detection, sfqa commands), and that the skill
correctly delineates from sf-browser-automation.

Does NOT test the sfqa CLI itself or require Chromium / SF CLI.

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
    """True when a promised file exists, here or in a sibling skill."""
    for cand in (SKILL / rel, SKILL / "scripts" / rel, SKILL / "references" / rel,
                 SKILL.parent / rel):
        if cand.exists():
            return True
    name = Path(rel).name
    return any(SKILL.parent.glob(f"*/**/{name}")) or any(SKILL.parent.glob(f"_shared/**/{name}"))


fail: list[str] = []
text = MD.read_text(encoding="utf-8")
# Strip fenced blocks so heading-shaped lines inside examples are not mistaken
# for sections.
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
expect("no em dashes", text.count("—"), 0)
expect("no section sign", text.count("§"), 0)

size = len(text.encode())
print(f"  SKILL.md is {size} bytes (budget 12288)")
expect("under the size budget", size <= 12288, True)

fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
expect("has frontmatter", bool(fm), True)
if fm:
    keys = set(re.findall(r"^([A-Za-z_][\w-]*):", fm.group(1), re.M))
    expect("only house frontmatter keys",
           sorted(keys - {"name", "description", "license"}), [])
    expect("name matches the folder",
           re.search(r"^name:\s*(\S+)", fm.group(1), re.M).group(1),
           SKILL.name)
    desc = re.search(r"^description:\s*(.*)", fm.group(1), re.M | re.S).group(1).strip().strip("'\"")
    print(f"  description is {len(desc)} chars (claude.ai limit 1024)")
    expect("description under the surface limit", len(desc) <= 1024, True)
    expect("description says when to trigger",
           bool(re.search(r"use (this )?(skill )?wh|triggers? on|trigger when|use it when", desc, re.I)), True)

# --- no hardcoded paths -------------------------------------------------------
expect("no /mnt/skills paths", bool(re.search(r"/mnt/skills", text)), False)
expect("no /Users/ paths", bool(re.search(r"/Users/[a-z]", text, re.I)), False)

# --- promised files exist -----------------------------------------------------
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

# --- skill.yaml exists and is consistent --------------------------------------
print()
yaml_path = SKILL / "skill.yaml"
expect("skill.yaml exists", yaml_path.exists(), True)
if yaml_path.exists():
    ytext = yaml_path.read_text(encoding="utf-8")
    ym = re.search(r"^name:\s*(\S+)", ytext, re.M)
    if ym:
        expect("skill.yaml name matches folder", ym.group(1), SKILL.name)

# --- sfqa CLI commands documented ---------------------------------------------
print()
has("documents sfqa doctor", r"sfqa.*doctor", in_prose=False)
has("documents sfqa shot", r"sfqa.*shot", in_prose=False)
has("documents sfqa batch", r"sfqa.*batch", in_prose=False)
has("documents sfqa flow", r"sfqa.*flow", in_prose=False)
has("documents sfqa watch", r"sfqa.*watch", in_prose=False)

# --- credential safety --------------------------------------------------------
print()
has("credential safety section", r"credential safety|no credential|no bearer")
has("warns against pasting tokens", r"never.*run.*url-only|never.*paste|do not.*paste")
has("frontdoor URL is single-use", r"single-use")

# --- readiness detection ------------------------------------------------------
has("explains readiness heuristic", r"readiness|stopped? changing|mutation")
has("documents settle caveat", r"do not pass.*settle|settle.*disables")

# --- boundary with sf-browser-automation --------------------------------------
print()
has("names sf-browser-automation", r"sf-browser-automation")
has("states the headless-only boundary", r"headless")

# --- exit ---------------------------------------------------------------------
if fail:
    print("\nSELFTEST FAILED")
    for f in fail:
        print("  -", f)
    sys.exit(1)
print("\nSELFTEST PASSED")
