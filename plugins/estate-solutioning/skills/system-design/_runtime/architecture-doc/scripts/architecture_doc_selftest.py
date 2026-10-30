#!/usr/bin/env python3
"""Selftest for architecture-doc. Stdlib only, no network.

The skill lists each document's section spine in SKILL.md and keeps the fillable
skeleton for those sections in references/architecture-templates.md. Two places
naming one spine is a drift risk, and it got sharper when SKILL.md was trimmed to
fit the size budget: the prose list is now the only copy in the body, and the
reference is the only copy of the detail. So the first case checks that every
section SKILL.md names still exists as a heading in the reference.

The skill also states the house voice rules in its own House rules section, then
has to obey them. A skill that tells you to avoid em dashes while using them is
not credible, and this one shipped with one.

Exit 0 when every case matches, 1 otherwise.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
MD = SKILL / "SKILL.md"
REF = SKILL / "references" / "architecture-templates.md"
SKILLS_ROOT = SKILL.parent


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


def expect(label: str, got, want):
    ok = got == want
    print(f"  {label:54} got={str(got):<7} want={want}")
    if not ok:
        fail.append(f"{label}: got {got}, want {want}")
    return ok


# --- it obeys the voice rules it states --------------------------------------
expect("no em dashes", text.count("—"), 0)
expect("no en dashes", text.count("–"), 0)
expect("no section sign", text.count("§"), 0)
expect("no emoji", bool(re.search(r"[\U0001F300-\U0001FAFF]", text)), False)

# --- G5: it was at the ceiling, keep it under ---------------------------------
size = len(text.encode())
print(f"  SKILL.md is {size} bytes (budget 12288)")
expect("SKILL.md under the 12 KB budget", size <= 12288, True)

# --- frontmatter matches the house shape --------------------------------------
fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
expect("has frontmatter", bool(fm), True)
if fm:
    keys = set(re.findall(r"^([A-Za-z_][\w-]*):", fm.group(1), re.M))
    extra = sorted(keys - {"name", "description", "license"})
    expect("only house frontmatter keys", extra, [])
    desc = re.search(r"description:\s*(.*)", fm.group(1), re.S)
    n = len(desc.group(1).strip().strip('"')) if desc else 0
    print(f"  description is {n} chars (claude.ai limit 1024)")
    expect("description under the surface limit", n <= 1024, True)

# --- the spine in SKILL.md matches the skeleton in the reference --------------
print()
if not REF.exists():
    fail.append("references/architecture-templates.md is missing")
else:
    ref = REF.read_text(encoding="utf-8")
    ref_headings = {h.strip().lower() for h in re.findall(r"^###\s+(.+)$", ref, re.M)}

    # Scope to "The two documents". The spine is stated once, there, on purpose:
    # a second copy elsewhere in the file is the drift this check exists to catch.
    section = re.search(r"## The two documents\n(.*?)\n---", text, re.S)
    if not section:
        fail.append("SKILL.md has no 'The two documents' section")
        section_text = ""
    else:
        section_text = section.group(1)

    for label in ("Architecture doc", "System design"):
        elsewhere = text.replace(section_text, "").count(f"**{label}")
        expect(f"{label} spine stated once", elsewhere, 0)

    spine = {}
    for label, key in (("Architecture doc", "architecture"), ("System design", "system design")):
        m = re.search(rf"\*\*{label}[^*]*\*\*\s*(.+?)\n\n", section_text, re.S)
        if not m:
            fail.append(f"SKILL.md no longer lists the {label} section spine")
            continue
        sections = [s.strip().rstrip(".").lower()
                    for s in re.split(r",\s*", m.group(1).replace("\n", " ")) if s.strip()]
        spine[key] = sections

    for key, sections in spine.items():
        absent = [s for s in sections if s not in ref_headings]
        print(f"  {key}: {len(sections)} sections named in SKILL.md")
        expect(f"  all have a skeleton in the reference", absent, [])

    # the reference must not have quietly grown sections the skill never mentions
    named = {s for v in spine.values() for s in v}
    structural = {"hero", "footer"}  # layout, not content sections
    orphan = sorted(h for h in ref_headings - named - structural)
    print(f"  reference-only sections: {orphan or 'none'}")

# --- the gates it cites are real ---------------------------------------------
print()
GATES = {
    "brand-renderer": "scripts/brand_check.py",
    "prose-pass": "scripts/prose_check.py",
}
for skill_name, rel in GATES.items():
    cited = skill_name in text
    expect(f"cites {skill_name}", cited, True)
    target = SKILLS_ROOT / skill_name / rel
    if not SKILLS_ROOT.joinpath(skill_name).exists():
        print(f"  note: {skill_name} not reachable, gate-path check skipped")
        continue
    expect(f"  {rel} exists", target.exists(), True)

# --- integrity ----------------------------------------------------------------
promised = set(re.findall(r"`([A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:md|py|json|html|css))`", text))
missing = [r for r in sorted(promised)
           if not r.startswith("_shared/")
           and not _resolves(r)
           and not any((SKILLS_ROOT / g / r).exists() for g in GATES)]
print(f"\n  SKILL.md promises {len(promised)} files, missing: {missing or 'none'}")
if missing:
    fail.append(f"missing promised files: {missing}")

if fail:
    print("\nSELFTEST FAILED")
    for f in fail:
        print("  -", f)
    sys.exit(1)
print("\nSELFTEST PASSED")
