#!/usr/bin/env python3
"""Selftest for the merged process skill. Stdlib only, no network.

process combines the old process-doc and process-optimization into two modes.
This holds both modes to the content that made each honest: the SOP template's
seven sections and single-accountable RACI, and the optimization method's five
waste categories and arithmetic discipline. Losing either mode's guarantees
would let the merge quietly drop half the skill.

Exit 0 when every case matches, 1 otherwise.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
MD = SKILL / "SKILL.md"

fail: list[str] = []
text = MD.read_text(encoding="utf-8")
prose = re.sub(r"```.*?```", "", text, flags=re.S)  # fenced examples are not sections


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
    expect("only house frontmatter keys", sorted(keys - {"name", "description", "license"}), [])
    expect("name matches the folder",
           re.search(r"^name:\s*(\S+)", fm.group(1), re.M).group(1), SKILL.name)
    desc = re.search(r"^description:\s*(.*)", fm.group(1), re.M | re.S).group(1).strip().strip('"')
    print(f"  description is {len(desc)} chars (claude.ai limit 1024)")
    expect("description under the surface limit", len(desc) <= 1024, True)
    expect("description names both modes",
           bool(re.search(r"document", desc, re.I)) and bool(re.search(r"optim", desc, re.I)), True)

# --- the conventions both modes share -----------------------------------------
print()
has("uses the not-captured convention", r"not captured")
has("uses the open-question convention", r"`?open:")
has("forbids inventing owners and metrics", r"[Dd]o not invent")
has("separates observed state from the redesign",
    r"[Dd]istinguish the current state|never present a recommendation as if it were observed")

# --- Document mode: the SOP template ------------------------------------------
print()
has("requires exactly one accountable per step", r"exactly one Accountable|single Accountable")
has("says the exceptions are the point", r"exceptions are the point")
tpl = re.search(r"```markdown\n(.*?)```", text, re.S)
expect("ships an SOP template", bool(tpl), True)
if tpl:
    t = tpl.group(1)
    for section in ("Purpose", "Scope", "RACI Matrix", "Process Flow",
                    "Detailed Steps", "Exceptions", "Metrics"):
        if section not in t:
            fail.append(f"SOP template lost its {section!r} section")
    print("  template carries all seven sections")
    expect("  RACI table has all four columns",
           all(c in t for c in ("Responsible", "Accountable", "Consulted", "Informed")), True)

# --- Optimize mode: the method and the arithmetic discipline ------------------
print()
for waste in ("Waiting", "Rework", "Hand-off", "Over-processing", "Manual"):
    if waste.lower() not in prose.lower():
        fail.append(f"the {waste!r} waste category is gone")
print("  all five waste categories present")
has("names a single largest constraint", r"single largest constraint|headline constraint")
has("ties impact to supplied numbers", r"trace to supplied|from captured durations")
has("marks magnitude rather than fabricating it", r"magnitude .{0,30}not captured|direction of the change")
has("calls a made-up duration a defect", r"defect")

# --- delivery -----------------------------------------------------------------
print()
has("falls back to inline when a write fails", r"inline|read-only|ephemeral")

if fail:
    print("\nSELFTEST FAILED")
    for f in fail:
        print("  -", f)
    sys.exit(1)
print("\nSELFTEST PASSED")
