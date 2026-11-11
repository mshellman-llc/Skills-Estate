#!/usr/bin/env python3
"""Selftest for skill-creation-walkthrough. Stdlib only, no network.

This skill teaches how to write a skill, so two things can go wrong that
would not matter elsewhere.

It used to state its own quality bar (SKILL.md under 250 lines, references under
400) alongside the house STANDARD.md. Two standards for one thing is how an
estate drifts, which is the failure this repo exists to prevent, so the check is
that it defers to STANDARD.md and states no competing numbers.

It also ships a SKILL.md template inside a code fence. That fence contains
heading-shaped lines, and an earlier edit to this very file matched them as real
sections and truncated it. The fence is asserted intact.

Exit 0 when every case matches, 1 otherwise.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
MD = SKILL / "SKILL.md"
HOUSE = SKILL.parents[1]
GOVERNANCE_TEMPLATE = HOUSE / "tooling" / "templates" / "skill" / "governance.yaml"
METADATA_TEMPLATE = HOUSE / "tooling" / "templates" / "skill" / "skill.yaml"


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


# --- it defers to the house bar rather than competing with it -----------------
print()
has("cites STANDARD.md as the bar", r"STANDARD\.md")
expect("states no competing line limit",
       bool(re.search(r"under \d{3} lines", prose)), False)
expect("states no competing reference limit",
       bool(re.search(r"references under \d{3}", prose)), False)

# --- the template fence survived editing --------------------------------------
fences = re.findall(r"```(.*?)```", text, re.S)
expect("ships a template fence", len(fences) >= 1, True)
tpl = next((f for f in fences if "name:" in f and "description:" in f), None)
expect("the template is a SKILL.md skeleton", tpl is not None, True)
if tpl:
    for section in ("When to use", "When NOT to use", "Workflow", "Reference files"):
        if section not in tpl:
            fail.append(f"template lost its {section!r} section")
    print("  template carries its standard sections")
    expect("  template has frontmatter delimiters", tpl.count("---") >= 2, True)
expect("fences are balanced", text.count("```") % 2, 0)

# --- the teaching that matters ------------------------------------------------
has("explains progressive disclosure", r"progressive disclosure")
has("says the description is what triggers", r"trigger.{0,60}description|description.{0,60}trigger")
has("warns about the under-triggering default", r"under-?trigger")
has("links the governed intake", r"governed-intake\.md")
has("documents local sketches", r"local sketches?")
has("gates candidate status", r"before candidate")
has("keeps unmeasured cost unknown", r"cost and efficiency.{0,80}unknown")
has("explains three validation scopes",
    r"changed-skill.{0,160}overlap-group.{0,160}full estate")

# --- governed scaffolder templates -------------------------------------------
expect("governance template exists", GOVERNANCE_TEMPLATE.exists(), True)
if GOVERNANCE_TEMPLATE.exists():
    governance = GOVERNANCE_TEMPLATE.read_text(encoding="utf-8")
    for key in ("job:", "position:", "contract:", "selection:", "relationships:",
                "capabilities:", "risks:", "cost:", "efficiency:", "stewardship:"):
        if key not in governance:
            fail.append(f"governance template lost {key}")
    expect("collision starts undecided", "disposition: undecided" in governance, True)
    expect("cost starts unknown", "cost:\n  status: unknown" in governance, True)
    expect("efficiency starts unknown",
           "efficiency:\n  status: unknown" in governance, True)

expect("metadata template exists", METADATA_TEMPLATE.exists(), True)
if METADATA_TEMPLATE.exists():
    metadata = METADATA_TEMPLATE.read_text(encoding="utf-8")
    expect("metadata declares runtime placeholder",
           "replace-with-runtimes" in metadata, True)
    expect("metadata declares Knowledge Hub requirement",
           "requirement: replace-with-hub-requirement" in metadata, True)
    expect("metadata declares Knowledge Hub contract",
           "replace-with-hub-contract" in metadata, True)
    expect("metadata declares Knowledge Hub target",
           "replace-with-hub-target" in metadata, True)
    expect("metadata declares connector contract",
           "replace-with-connectors-contract" in metadata, True)
    expect("metadata declares dependency contract",
           "replace-with-depends-on-contract" in metadata, True)
    expect("metadata declares tier", "tier: replace-with-tier" in metadata, True)
    expect("metadata omits rejected plugin field", "\nplugin:" in metadata, False)
    expect("metadata uses canonical skill identifiers",
           "aleysian-knowledge-hub" in metadata
           or "aleysian-evidence-core" in metadata
           or "aleysian-quality-gate" in metadata, False)

if fail:
    print("\nSELFTEST FAILED")
    for f in fail:
        print("  -", f)
    sys.exit(1)
print("\nSELFTEST PASSED")
