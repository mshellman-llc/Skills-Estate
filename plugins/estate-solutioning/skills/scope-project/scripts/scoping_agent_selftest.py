#!/usr/bin/env python3
"""Selftest for scope-project. Stdlib only, no network, no MCP.

This skill ships no executable, so there is no behaviour to drive. What it does
ship is example MCP payloads that a person or a model copies verbatim into a live
call against the Pricing System. A malformed example is therefore a live defect:
it does not fail here, it fails against a real quote.

So the test is: every ```json block in the references must parse, and every file
the SKILL.md promises must exist. The connector itself is never contacted.

Exit 0 when every case matches, 1 otherwise.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent


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
FENCE = re.compile(r"^```json\s*$(.*?)^```\s*$", re.M | re.S)
# Some payloads elide a repetitive section with a `/* ... */` note. That is not
# JSON, and it is deliberate: the block shows shape, not a literal body. Strip
# the elisions and the remaining skeleton must still parse, so a real syntax
# error in the surrounding structure is still caught.
ELISION = re.compile(r"/\*.*?\*/", re.S)


def check_json_fences(path: Path) -> tuple:
    """Every ```json block parses once elisions are removed.
    Returns (blocks checked, blocks that carried an elision)."""
    if not path.exists():
        fail.append(f"missing file: {path.name}")
        return 0, 0
    text = path.read_text(encoding="utf-8")
    blocks = FENCE.findall(text)
    elided = 0
    for i, block in enumerate(blocks, 1):
        line = text[:text.index(block)].count("\n") + 1
        stripped = ELISION.sub("", block)
        if stripped != block:
            elided += 1
            # an elided list or object leaves a dangling comma: [ , ] -> []
            stripped = re.sub(r",\s*([}\]])", r"\1", stripped)
            stripped = re.sub(r"([\[{])\s*,", r"\1", stripped)
        try:
            json.loads(stripped)
        except json.JSONDecodeError as e:
            fail.append(f"{path.name}: json block {i} near line {line} does not parse: {e}")
    return len(blocks), elided


total = 0
for rel in ("references/payloads.md", "references/methodology.md", "SKILL.md"):
    n, elided = check_json_fences(SKILL / rel)
    total += n
    note = f" ({elided} with elisions)" if elided else ""
    print(f"  {rel:34} {n} json block(s) checked{note}")
print(f"  {total} json payload block(s) parsed in total")
if total == 0:
    fail.append("no json payload blocks found; the references lost their examples")

# every file SKILL.md promises exists
text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
promised = set(re.findall(r"`([A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:md|py|json))`", text))
missing = [r for r in sorted(promised)
           if not r.startswith("_shared/")
           and not _resolves(r)]
print(f"\n  SKILL.md promises {len(promised)} files, missing: {missing or 'none'}")
if missing:
    fail.append(f"missing promised files: {missing}")

# the references the SKILL.md names by section must be non-empty
for rel in ("references/methodology.md", "references/payloads.md"):
    p = SKILL / rel
    size = p.stat().st_size if p.exists() else 0
    print(f"  {rel:34} {size} bytes")
    if size < 200:
        fail.append(f"{rel} is empty or a stub ({size} bytes)")

if fail:
    print("\nSELFTEST FAILED")
    for f in fail:
        print("  -", f)
    sys.exit(1)
print("\nSELFTEST PASSED")
