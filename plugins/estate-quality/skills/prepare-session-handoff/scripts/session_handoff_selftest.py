#!/usr/bin/env python3
"""Selftest for prepare-session-handoff. Stdlib only, no network.

This skill ships no executable, but it ships two things that break silently.

THE PROVENANCE COMMAND. Step 1 is a shell one-liner the skill runs verbatim at
the top of every handoff. If someone edits it and breaks a flag, the failure
shows up as a handoff with no timestamp, which is exactly the case the stamp
exists to prevent. So the test extracts the real command from SKILL.md and runs
it. It is read-only (date, pwd, git rev-parse, git status), so running it is safe.

THE OUTPUT TEMPLATE. The skill's first hard rule is that a section with nothing
to report says "none" rather than being dropped, because the next agent has to
be able to trust that a missing item means nothing happened. That guarantee is
only as good as the template, so every section the prose promises must exist in
it.

CANON. This file arrived carrying 36 em dashes, including inside the template,
which would have written them into every handoff file. Zero is now asserted.

Exit 0 when every case matches, 1 otherwise.
"""
from __future__ import annotations

import re
import subprocess
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


def expect(label: str, got, want):
    ok = got == want
    print(f"  {label:52} got={str(got):<7} want={want}")
    if not ok:
        fail.append(f"{label}: got {got}, want {want}")
    return ok


# --- canon -------------------------------------------------------------------
expect("no em dashes anywhere", text.count("—"), 0)
expect("no section sign", text.count("§"), 0)
expect("no emoji in the template", bool(re.search(r"[\U0001F300-\U0001FAFF]", text)), False)

# --- the provenance command still runs ---------------------------------------
fences = re.findall(r"```bash\n(.*?)```", text, re.S)
expect("SKILL.md ships a bash provenance block", len(fences) >= 1, True)
if fences:
    cmd = fences[0].strip()
    # The stamp must stay read-only: it runs unattended at the top of every
    # handoff. Discarding stderr (2>/dev/null, 2>&1) is fine; writing a file or
    # mutating the repo is not.
    probe = re.sub(r"2>\s*(/dev/null|&1)", "", cmd)
    for banned in ("rm ", "git commit", "git push", "git checkout", "git reset", ">"):
        if banned in probe:
            fail.append(f"provenance command is not read-only, contains {banned!r}")
    p = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True,
                       cwd=str(SKILL))
    out = p.stdout.strip().splitlines()
    expect("  it exits 0", p.returncode, 0)
    expect("  and emits a UTC timestamp",
           bool(out and re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2} UTC", out[0])), True)
    expect("  and an absolute cwd",
           bool(len(out) > 1 and out[1].startswith("/")), True)
    print(f"  provenance produced {len(out)} lines")

# --- the output template is structurally complete ----------------------------
template = re.search(r"## Step 3\. Output template.*?\n```\n(.*?)```", text, re.S)
expect("SKILL.md ships an output template", bool(template), True)
if template:
    body = template.group(1)
    REQUIRED_SECTIONS = [
        "Where it started",
        "Decisions locked",
        "Key files for next session",
        "Running state",
        "Verification",
        "Deferred + open questions",
        "Pick up here",
    ]
    absent = [s for s in REQUIRED_SECTIONS if s not in body]
    expect("every promised section is in the template", absent, [])

    # the stamp line carries all four provenance fields
    for field in ("Written:", "branch", "tree", "cwd"):
        if field not in body:
            fail.append(f"template stamp line is missing {field!r}")
    print("  stamp line carries timestamp, branch, tree state and cwd")

    # the template must not teach an em dash into a written file
    expect("template itself is em-dash free", body.count("—"), 0)

    # sections the hard rules name must be the ones the template has
    for named in ("Running state", "Tried and rejected"):
        if named not in text.split("## Hard rules")[-1] + text:
            fail.append(f"hard rules reference {named!r} but it is not in the template")

# --- the write path is resolved, not asserted --------------------------------
expect("no bare hardcoded handoffs path in a fence",
       bool(re.search(r"```\n~/\.claude/handoffs/", text)), False)
expect("the path is documented as resolved in order",
       "Resolve it, do" in text or "whichever of these the environment" in text, True)
expect("the ephemeral-filesystem case is handled",
       "ephemeral" in text.lower(), True)

# --- integrity ---------------------------------------------------------------
promised = set(re.findall(r"`([A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:md|py|json))`", text))
missing = [r for r in sorted(promised)
           if not _resolves(r)]
print(f"\n  SKILL.md promises {len(promised)} files, missing: {missing or 'none'}")
if missing:
    fail.append(f"missing promised files: {missing}")

if fail:
    print("\nSELFTEST FAILED")
    for f in fail:
        print("  -", f)
    sys.exit(1)
print("\nSELFTEST PASSED")
