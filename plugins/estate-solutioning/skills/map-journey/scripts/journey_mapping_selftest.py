#!/usr/bin/env python3
"""Selftest for map-journey. Stdlib only, no network.

The estate migration on 2026-10-19 cut this skill to one paragraph per view
and dropped its template. The restore put the method back, so the checks guard
what that cut removed:

  1. The template still carries the lanes, the blueprint layers, the ledger,
     the validation table, the opportunity map, and all six phase presets.
  2. The labeled-hypothesis mode stays in the complete bundled method with its basis note,
     visible marking, and validation questions, and the template carries the
     Hypothesis confidence level.
  3. The render layout and HTML starter exist, and the starter draws the
     line of visibility and a dashed hypothesis curve.
  4. Every relative link in SKILL.md and the references resolves, and no
     an unrelated organization appears in the output.

Exit 0 when every case matches, 1 otherwise.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
MD = SKILL / "SKILL.md"
METHOD = SKILL / "references" / "method.md"
REF = SKILL / "references" / "journey-map-template.md"
LAYOUT = SKILL / "references" / "rendered-map-layout.md"
HTML = SKILL / "assets" / "journey-map.html"

fail: list[str] = []


def expect(label: str, got, want):
    print(f"  {label:58} got={str(got):<7} want={want}")
    if got != want:
        fail.append(f"{label}: got {got}, want {want}")


for path in (MD, METHOD, REF, LAYOUT, HTML, SKILL / "LICENSE"):
    if not path.exists():
        print(f"  missing {path.relative_to(SKILL)}")
        sys.exit(1)

entry = MD.read_text(encoding="utf-8")
text = entry + "\n" + METHOD.read_text(encoding="utf-8")
ref = REF.read_text(encoding="utf-8")
layout = LAYOUT.read_text(encoding="utf-8")
html = HTML.read_text(encoding="utf-8")

# --- frontmatter -------------------------------------------------------------
fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
expect("frontmatter present", bool(fm), True)
if fm:
    desc = re.search(r'^description:\s*"(.*)"\s*$', fm.group(1), re.M)
    n = len(desc.group(1)) if desc else 0
    print(f"  description is {n} chars (surface limit 1024)")
    expect("description under the surface limit", 0 < n <= 1024, True)
    expect("no upstream name outside LICENSE", "exampleco" in fm.group(1).lower(), False)

# --- template carries the structure ------------------------------------------
print()
REQUIRED_IN_REF = {
    "the eight-lane table": r"\|\s*Phase\s*\|\s*Step\s*\|\s*Touchpoint\s*\|\s*Goal\s*\|\s*Thoughts\s*\|\s*Emotion",
    "emotional intensity for the curve": r"Emotional intensity",
    "service blueprint layers": r"##\s*Service blueprint layers",
    "front-stage actions": r"Front-stage actions",
    "back-stage actions": r"Back-stage actions",
    "supporting systems": r"Supporting systems",
    "line-of-visibility issues": r"Line-of-visibility issues",
    "the source and confidence ledger": r"##\s*Source and confidence ledger",
    "a Hypothesis confidence level": r"\|\s*Hypothesis\s*\|",
    "the validation questions table": r"##\s*Validation questions",
    "the opportunity map": r"##\s*Opportunity map",
    "critical friction": r"###\s*Critical friction",
    "the pre-ship checklist": r"##\s*Pre-ship checklist",
}
for label, pattern in REQUIRED_IN_REF.items():
    expect(f"template carries {label}", bool(re.search(pattern, ref, re.I)), True)

PRESETS = ("Most products", "SaaS", "Service business", "CX engagement",
           "Consulting prospect-to-client lifecycle", "Product role journey")
expect("all six phase presets present", [p for p in PRESETS if p not in ref], [])
expect("presets kept their sequences", ref.count("->") >= 40, True)

# --- hypothesis mode ---------------------------------------------------------
print()
expect("workflow has the labeled-hypothesis section", "## Labeled-hypothesis mode" in text, True)
for phrase in ("State the basis once", "Name the hypothesized layers",
               "Never attribute a hypothesized thought", "validation questions"):
    expect(f"  hypothesis rule: {phrase}", phrase in text, True)

# --- render layout and starter -----------------------------------------------
print()
for row in ("Emotion", "Line of visibility", "Front-stage", "Back-stage", "Supporting", "Critical friction"):
    expect(f"layout names {row}", row.lower() in layout.lower(), True)
expect("starter draws the line of visibility", "Line of visibility" in html, True)
expect("starter dashes a hypothesis curve", "stroke-dasharray" in html and "hypothesis" in html, True)
expect("starter lists evidence once instead of tagging cells", 'id="evidence"' in html and "basis-tag" not in html, True)

# --- links resolve and the identity stays out --------------------------------
print()
packaged = (SKILL / "references/estate/writing.md").is_file()
for doc in (MD, METHOD, REF, LAYOUT):
    body = doc.read_text(encoding="utf-8")
    for target in re.findall(r"\]\(([^\s)]+)\)", body):
        if target.startswith(("http:", "https:", "#")):
            continue
        if not packaged and target.startswith(("references/estate/", "estate/")):
            continue
        expect(f"{doc.name} link {target}", (doc.parent / target.split("#")[0]).exists(), True)

for doc in (MD, METHOD, REF, LAYOUT, HTML):
    hits = re.findall(r"(?i)exampleco|exampleproject", doc.read_text(encoding="utf-8"))
    expect(f"no former identity in {doc.name}", hits, [])

if fail:
    print("\nSELFTEST FAILED")
    for f in fail:
        print("  -", f)
    sys.exit(1)
print("\nSELFTEST PASSED")
