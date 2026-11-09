#!/usr/bin/env python3
"""Selftest for verify-salesforce-org. Stdlib only, no network, no Salesforce.

This gate exists to refuse, so the test is weighted toward refusal. Every path
that must stop is driven, and each is checked to exit 2 rather than merely
non-zero, because a crash also exits non-zero and a crash is not a refusal.

The cases that matter most, in order of what they would cost if they regressed:

  1. Production without the explicit second affirmation must stop. This is the
     production-write-meant-for-sandbox case the skill was written for.
  2. Incomplete identity must stop. A gate that passes when it was told nothing
     is worse than no gate, because it produces a PASS line in the transcript.
  3. An unresolvable --expect must stop. An unknown alias is not an assumption.
  4. Registry disagreeing with the org must stop, with the org winning. A stale
     registry that quietly relabels production as sandbox is the subtle version
     of the same accident.

Exit 0 when every case matches, 1 otherwise.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent

PROD = "00D000000000000EAA"
SBX = "00D000000000001EAA"
UNKNOWN = "00D0000000000ZZEAA"

fail: list[str] = []


def expect(label: str, got, want):
    ok = got == want
    print(f"  {label:56} got={str(got):<5} want={want}")
    if not ok:
        fail.append(f"{label}: got {got}, want {want}")
    return ok


def run(script: Path, *args):
    p = subprocess.run([sys.executable, str(script), *map(str, args)],
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def with_registry(tmp: Path, orgs: dict) -> Path:
    """A copy of the script beside a registry we control."""
    d = tmp / f"reg{len(list(tmp.iterdir()))}"
    d.mkdir()
    shutil.copy(HERE / "preflight.py", d / "preflight.py")
    (d / "orgs.json").write_text(json.dumps({"orgs": orgs}), encoding="utf-8")
    return d / "preflight.py"


POPULATED = {
    PROD: {"alias": "prod", "kind": "production"},
    SBX: {"alias": "uat", "kind": "sandbox"},
}

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    script = with_registry(tmp, POPULATED)
    empty = with_registry(tmp, {})

    # --- the happy paths, so the gate is not merely always-refusing ----------
    code, out = run(script, "--live-id", SBX, "--is-sandbox", "true", "--expect", "uat")
    expect("sandbox write to the intended sandbox passes", code, 0)
    expect("  and says PASS", "PREFLIGHT PASS" in out, True)

    code, _ = run(script, "--live-id", SBX, "--is-sandbox", "true", "--expect", "sandbox")
    expect("kind alone cannot identify the intended sandbox", code, 2)

    code, _ = run(script, "--live-id", SBX, "--is-sandbox", "true", "--expect", SBX)
    expect("expect-by-org-id passes", code, 0)

    code, out = run(script, "--live-id", PROD, "--is-sandbox", "false",
                    "--expect", "prod", "--allow-production")
    expect("production WITH the affirmation passes", code, 0)
    expect("  and does not grant authorization", "does not authorize" in out, True)

    # --- 1. production without the affirmation ------------------------------
    code, out = run(script, "--live-id", PROD, "--is-sandbox", "false", "--expect", "prod")
    expect("production WITHOUT the affirmation refuses", code, 2)
    expect("  and names production in the reason", "PRODUCTION" in out, True)

    # the affirmation alone does not authorise the wrong org
    code, _ = run(script, "--live-id", PROD, "--is-sandbox", "false",
                  "--expect", "uat", "--allow-production")
    expect("affirmation does not excuse the wrong org", code, 2)

    # --- 2. incomplete identity ---------------------------------------------
    for label, args in (
        ("no identity at all", ("--expect", "uat")),
        ("id but no sandbox flag", ("--live-id", SBX, "--expect", "uat")),
        ("sandbox flag but no id", ("--is-sandbox", "true", "--expect", "uat")),
        ("no --expect", ("--live-id", SBX, "--is-sandbox", "true")),
        ("malformed org id", ("--live-id", "not-an-org", "--is-sandbox", "true",
                              "--expect", "uat")),
    ):
        code, _ = run(script, *args)
        expect(f"{label} refuses", code, 2)

    # --- 3. unresolvable --expect -------------------------------------------
    code, out = run(script, "--live-id", SBX, "--is-sandbox", "true", "--expect", "staging")
    expect("unknown alias refuses", code, 2)
    expect("  and lists the known aliases", "prod" in out and "uat" in out, True)

    code, out = run(empty, "--live-id", SBX, "--is-sandbox", "true", "--expect", "uat")
    expect("empty registry refuses an alias", code, 2)
    expect("  and says so plainly", "orgs.json is empty" in out, True)

    # an unregistered org id still works, so an empty registry is not a wall
    code, _ = run(empty, "--live-id", SBX, "--is-sandbox", "true", "--expect", SBX)
    expect("empty registry still accepts a full org id", code, 0)

    # --- 4. the org outranks the registry ------------------------------------
    lying = with_registry(tmp, {PROD: {"alias": "prod", "kind": "sandbox"}})
    code, out = run(lying, "--live-id", PROD, "--is-sandbox", "false", "--expect", "prod")
    expect("registry mislabelling production refuses", code, 2)
    expect("  and says the org wins", "org wins" in out, True)

    bad_kind = with_registry(tmp, {SBX: {"alias": "uat", "kind": "dev"}})
    code, _ = run(bad_kind, "--live-id", SBX, "--is-sandbox", "true", "--expect", SBX)
    expect("invalid kind in the registry refuses", code, 2)

    # a corrupt registry refuses rather than silently running unregistered
    corrupt = tmp / "corrupt"
    corrupt.mkdir()
    shutil.copy(HERE / "preflight.py", corrupt / "preflight.py")
    (corrupt / "orgs.json").write_text("{not json", encoding="utf-8")
    code, _ = run(corrupt / "preflight.py", "--live-id", SBX, "--is-sandbox", "true",
                  "--expect", SBX)
    expect("unparsable registry refuses", code, 2)

    # --- an unregistered org is not silently trusted -------------------------
    code, _ = run(script, "--live-id", UNKNOWN, "--is-sandbox", "false", "--expect", "prod")
    expect("unregistered production org refuses", code, 2)

# --- the shipped registry is empty and parses --------------------------------
print()
shipped = json.loads((HERE / "orgs.json").read_text(encoding="utf-8"))
expect("shipped orgs.json parses with an empty registry", shipped.get("orgs"), {})

text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
for promise in ("scripts/preflight.py", "orgs.json"):
    present = promise in text
    print(f"  SKILL.md mentions {promise:22} {present}")
    if not present:
        fail.append(f"SKILL.md does not mention {promise}")
expect("SKILL.md no longer claims draft status", "Draft status" in text, False)

if fail:
    print("\nSELFTEST FAILED")
    for f in fail:
        print("  -", f)
    sys.exit(1)
print("\nSELFTEST PASSED")
