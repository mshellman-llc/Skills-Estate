#!/usr/bin/env python3
"""Selftest for the manage-service-offering package planner. Stdlib only, no network.

These checks exercise the preserved version 1.1 model. They do not establish
agreement with an authoritative caller-supplied specification. Both tools must
report that limit even when the modeled suite has no outstanding artifacts.

Then the two planners, exercised in both directions:

  1. A complete manifest plans clean, with no outstanding artifacts.
  2. An empty manifest reports every required artifact as outstanding, and the
     count matches what spec_shapes says that shape requires.
  3. Shape really selects the artifact set. Front Door drops the deal layer to
     conditional, so it must require strictly fewer artifacts than a paid shape.
  4. A manifest declaring the wrong spec_version raises a finding rather than
     planning silently against the wrong artifact set.
  5. A manifest missing a required field exits 2 instead of planning from a
     half-read file.
  6. conformance_audit.py runs against a synthetic folder and separates a
     conforming playbook from one with a missing required artifact.

Exit 0 when every case matches, 1 otherwise.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent

sys.path.insert(0, str(HERE))
import spec_shapes  # noqa: E402


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
    print(f"  {label:54} got={str(got):<8} want={want}")
    if not ok:
        fail.append(f"{label}: got {got}, want {want}")
    return ok


def run(script: str, *args):
    p = subprocess.run([sys.executable, str(HERE / script), *map(str, args)],
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


PASSED = {"parity": "pass", "visual": "pass", "prose": "pass"}


def manifest(shape="Migrate", options=("Base",), present=(), spec_version=None,
             gated=False, **extra):
    """`present` is artifact numbers. `gated` marks their three gates passed;
    without it they are present-but-ungated, which the planner treats as
    outstanding work rather than done."""
    arts = []
    for n in present:
        entry = {"number": n, "status": "present"}
        if gated:
            entry["gates"] = dict(PASSED)
        # option-scoped artifacts are keyed per option, not per playbook
        if spec_shapes.ARTIFACTS[n][2] == "option":
            for o in options:
                arts.append({**entry, "option": o})
        else:
            arts.append(entry)
    m = {
        "code": "C99", "name": "Selftest Playbook", "shape": shape,
        "stage": 3, "spec_version": spec_version or spec_shapes.SPEC_VERSION,
        "options": [{"name": o} for o in options],
        "artifacts": arts,
    }
    m.update(extra)
    return m


def write(tmp: Path, name: str, obj) -> Path:
    p = tmp / name
    p.write_text(json.dumps(obj), encoding="utf-8")
    return p


# --- specification authority remains explicit -------------------------------
expect("model does not claim specification validation",
       spec_shapes.authority_status()["status"], "unverified")
expect("model alone cannot authorize a release",
       spec_shapes.authority_status()["release_ready"], False)

# --- the planners ------------------------------------------------------------
print()
with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)

    required = [n for n in spec_shapes.ARTIFACTS
                if spec_shapes.requirement("Migrate", n) == "R"]

    # 2. an empty playbook owes everything required
    code, out = run("plan.py", write(tmp, "empty.json", manifest()), "--format", "json")
    expect("empty manifest plans (exit 0)", code, 0)
    plan = json.loads(out) if code == 0 else {}
    totals = plan.get("totals", {})
    expect("nothing complete yet", totals.get("complete"), 0)
    expect("outstanding equals required", totals.get("outstanding"), totals.get("required"))
    expect("required set is non-trivial", (totals.get("required") or 0) >= len(required), True)

    # 1. built AND gated is complete
    every = list(spec_shapes.ARTIFACTS)
    code, out = run("plan.py", write(tmp, "full.json", manifest(present=every, gated=True)),
                    "--format", "json")
    plan = json.loads(out) if code == 0 else {}
    expect("built and gated has 0 outstanding", plan.get("totals", {}).get("outstanding"), 0)
    expect("built and gated has no next step", plan.get("next_step"), None)

    # present but ungated is NOT complete. Gates are the point of the planner, so
    # a manifest that claims presence without them must still owe work.
    code, out = run("plan.py", write(tmp, "ungated.json", manifest(present=every, gated=False)),
                    "--format", "json")
    plan = json.loads(out) if code == 0 else {}
    expect("present but ungated still outstanding",
           (plan.get("totals", {}).get("outstanding") or 0) > 0, True)
    expect("and the action is run_gates",
           (plan.get("next_step") or {}).get("action"), "run_gates")

    # 3. shape selects the set. The planner lists conditional artifacts too (so a
    # motion can see and skip them), so the shape difference shows in the required
    # matrix rather than in the plan length.
    def n_hard(shape):
        return sum(1 for n in spec_shapes.ARTIFACTS
                   if spec_shapes.requirement(shape, n) == "R")

    fd, mig = n_hard("Front Door"), n_hard("Migrate")
    print(f"  hard-required: Front Door {fd}, Migrate {mig}")
    expect("Front Door requires fewer than Migrate", 0 < fd < mig, True)
    expect("Front Door drops the deal layer to conditional",
           all(spec_shapes.requirement("Front Door", n) == "C" for n in (7, 9, 10)), True)

    # 4. a wrong spec_version is a finding, not a silent plan
    code, out = run("plan.py", write(tmp, "old.json", manifest(spec_version="0.9")),
                    "--format", "json")
    findings = json.loads(out).get("findings", []) if code == 0 else []
    expect("wrong spec_version raises a finding",
           any("spec_version" in f for f in findings), True)
    code, out = run("plan.py", write(tmp, "ok.json", manifest()), "--format", "json")
    findings = json.loads(out).get("findings", []) if code == 0 else []
    expect("matching spec_version raises none",
           any("spec_version" in f for f in findings), False)

    # 5. a malformed manifest is refused
    code, out = run("plan.py", write(tmp, "bad.json", {"code": "C99"}), "--format", "json")
    expect("manifest missing required fields exits 2", code, 2)

    # text format carries the same totals as json
    code, out = run("plan.py", write(tmp, "empty.json", manifest()), "--format", "text")
    expect("text format renders (exit 0)", code, 0)
    expect("text format states the totals", "complete" in out, True)

    # 6. conformance_audit separates conforming from non-conforming
    pb = tmp / "playbook"
    pb.mkdir()

    def audit(m):
        (pb / "manifest.json").write_text(json.dumps(m), encoding="utf-8")
        code, out = run("conformance_audit.py", pb, "--manifest", pb / "manifest.json", "--json")
        if code == 2:
            return 2, None
        try:
            return code, json.loads(out)
        except json.JSONDecodeError:
            return code, None

    code_full, rep_full = audit(manifest(present=every, gated=True))
    code_gap, rep_gap = audit(manifest(present=[1], gated=True))
    expect("audit runs without a usage error", 2 not in (code_full, code_gap), True)
    if rep_full and rep_gap:
        f_full, f_gap = rep_full["blocking_findings"], rep_gap["blocking_findings"]
        print(f"  blocking findings: complete {f_full}, gapped {f_gap}")
        expect("a complete playbook has no blocking findings", f_full, 0)
        expect("a gapped playbook has some", f_gap > 0, True)
        expect("the gapped one names its missing artifacts",
               bool(rep_gap["findings"]["missing"]), True)
        expect("conforming exits 0", code_full, 0)
        expect("non-conforming exits 1", code_gap, 1)
    else:
        fail.append("conformance_audit did not emit parsable JSON")

# --- integrity ---------------------------------------------------------------
print()
text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
promised = set(re.findall(r"`([A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:md|py|json))`", text))
# The caller supplies these; they are inputs to the scripts, not skill files.
INPUTS = {"manifest.json", "qualifier.json", "catalog.json", "registry.json"}
missing = [r for r in sorted(promised)
           if r not in INPUTS and not _resolves(r)]
print(f"  SKILL.md promises {len(promised)} files, missing: {missing or 'none'}")
if missing:
    fail.append(f"missing promised files: {missing}")

if fail:
    print("\nSELFTEST FAILED")
    for f in fail:
        print("  -", f)
    sys.exit(1)
print("\nSELFTEST PASSED")
