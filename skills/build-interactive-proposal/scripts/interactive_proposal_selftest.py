#!/usr/bin/env python3
"""Selftest for build-interactive-proposal. Stdlib only, no network.

This test checks the supporting manifest and file references. Actual generation
and browser interactions are covered by test_proposal_behavior.py and qa_proposal.py.

The rule worth pinning is Explorer mode's central promise, stated in SKILL.md as
"zero currency on the surface". The manifest encodes that as a forbidden phrase.
If someone edits the manifest and drops it, an explorer page could ship with a
price on it and the gate would stay quiet. So that specific invariant is asserted
by name rather than left to a generic "the json parses" check.

Exit 0 when every case matches, 1 otherwise.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
REFS = SKILL / "references"


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
    print(f"  {label:52} got={str(got):<7} want={want}")
    if not ok:
        fail.append(f"{label}: got {got}, want {want}")
    return ok


# --- every shipped manifest parses and carries its contract ------------------
manifests = sorted(REFS.glob("*.manifest.json"))
print(f"  found {len(manifests)} release-gate manifest(s)")
if not manifests:
    fail.append("no *.manifest.json in references; the gate has nothing to run")

REQUIRED_KEYS = {"manifestVersion", "artifactId", "decisionJob",
                 "requiredPhrases", "forbiddenPhrases", "requiredViews"}

for m in manifests:
    try:
        data = json.loads(m.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fail.append(f"{m.name} does not parse: {e}")
        continue
    absent = sorted(REQUIRED_KEYS - set(data))
    expect(f"{m.name[:30]} has its contract keys", absent, [])
    for k in ("requiredPhrases", "forbiddenPhrases", "requiredViews"):
        if k in data:
            expect(f"  {k} is a non-empty list",
                   isinstance(data[k], list) and (k == "forbiddenPhrases" or bool(data[k])), True)

    # the explorer-mode invariant: no currency on the surface
    if "explorer" in m.name.lower() or "$" in data.get("forbiddenPhrases", []):
        expect("  explorer manifest forbids currency",
               "$" in data.get("forbiddenPhrases", []), True)

# --- SKILL.md and the manifest agree that explorer mode is priceless ---------
skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
says_no_currency = bool(re.search(r"zero currency|no pricing|not a quote", skill_text, re.I))
expect("SKILL.md states the no-currency rule", says_no_currency, True)

any_forbids = any("$" in json.loads(m.read_text(encoding="utf-8")).get("forbiddenPhrases", [])
                  for m in manifests
                  if m.read_text(encoding="utf-8").strip().startswith("{"))
expect("a manifest encodes it as a forbidden phrase", any_forbids, True)

# --- every file SKILL.md promises exists -------------------------------------
promised = set(re.findall(r"`([A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:md|py|json|html))`", skill_text))
INPUTS = {"proposal.json", "quote-export.json", "explorer.json"}  # the caller supplies the data contract instance
missing = [r for r in sorted(promised)
           if r not in INPUTS and not r.startswith("_shared/")
           and not _resolves(r)]
print(f"\n  SKILL.md promises {len(promised)} files, missing: {missing or 'none'}")
if missing:
    fail.append(f"missing promised files: {missing}")

for rel in ("references/quote-contract.md", "references/release-gates.md", "references/patterns.md"):
    p = SKILL / rel
    size = p.stat().st_size if p.exists() else 0
    print(f"  {rel:40} {size} bytes")
    if size < 200:
        fail.append(f"{rel} is empty or a stub ({size} bytes)")

if fail:
    print("\nSELFTEST FAILED")
    for f in fail:
        print("  -", f)
    sys.exit(1)
print("\nSELFTEST PASSED")
