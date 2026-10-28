#!/usr/bin/env python3
"""Estate playbook build planner.

Reads a playbook manifest and emits an ordered build plan as JSON. The plan is the
contract between the orchestrator and whatever executes it. Today that executor is a
Claude skill reading the plan and calling other skills. In phase 2 it is a workflow
engine turning each step into a node. Both call this same file, so the phase 2 build
extends the orchestrator rather than replacing it.

    python3 plan.py manifest.json [--spec-version 1.1] [--format json|text]

--format json is the machine contract for a phase 2 executor and is the default.
A human or a Claude skill reading the plan should pass --format text, which is
roughly a seventh the size and carries the same totals, findings, and actions.

Exit 0 when a plan was produced. Exit 2 when the manifest is unusable.
This file decides nothing about content. It decides what must exist, in what order,
and what is currently blocking.
"""

import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spec_shapes

SPEC_VERSION = spec_shapes.SPEC_VERSION

# number -> (display name, builder). Format, scope, and per-shape requirement come
# from spec_shapes so the artifact set has one authority (SPEC.md).
ARTIFACT_META = {
    1:  ("README", "estate-playbook-suite"),
    2:  ("Overview", "estate-playbook-suite"),
    3:  ("One-pager", "estate-onepager"),
    4:  ("Talk Track and Objections", "estate-playbook-suite"),
    5:  ("Qualifier", "estate-playbook-suite"),
    6:  ("ROM deck", "estate-brand-renderer"),
    7:  ("DDOC", "estate-ddoc"),
    8:  ("Proposal", "estate-brand-renderer"),
    9:  ("Pre-Engagement Stage Gate", "template copy"),
    10: ("SOW", "estate-sow"),
}

# Artifacts that must exist before another can be built. Keys depend on values.
DEPENDS_ON = {
    2: [],
    3: [2],
    4: [2],
    5: [2],
    6: [2],
    7: [2, 5],
    8: [7],
    9: [],
    10: [7],
    1: [],
}

# Order artifacts are built in. Not the same as numeric order: 05 feeds 07, 07 feeds 08 and 10.
BUILD_ORDER = [2, 5, 3, 4, 9, 6, 7, 8, 10, 1]

GATES = ("parity", "visual", "prose")
TERMINAL_GATE_STATES = ("pass", "dispositioned")


def load(path):
    if not os.path.exists(path):
        fail(f"manifest not found: {path}")
    try:
        with open(path) as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        fail(f"manifest is not valid JSON: {exc}")


def fail(msg):
    print(json.dumps({"error": msg}, indent=2))
    sys.exit(2)


def required_artifacts(manifest):
    """Expand the artifact set against this playbook's shape, options, and band spread.
    A single-option playbook has an empty options list and gets one implicit option."""
    shape = manifest.get("shape")
    options = [o.get("name") for o in manifest.get("options", [])]
    spread = manifest.get("band_spread")
    rom_required = bool(spread) and spread > 2

    out = []
    for num in BUILD_ORDER:
        name, builder = ARTIFACT_META[num]
        slug, fmt, scope = spec_shapes.ARTIFACTS[num]
        req = spec_shapes.requirement(shape, num)
        if req is None:
            continue
        # 06 ROM is only planned when the band spread triggers it. The other
        # conditional artifacts (Front Door 07/09/10) are planned but flagged so
        # the motion can skip them when it carries no decision.
        if num == 6 and not rom_required:
            continue
        requirement = "always" if req == "R" else "conditional"
        if scope == "option" and options:
            for opt in options:
                out.append({"number": num, "name": name, "format": fmt,
                            "option": opt, "builder": builder, "requirement": requirement})
        else:
            out.append({"number": num, "name": name, "format": fmt,
                        "option": None, "builder": builder, "requirement": requirement})
    return out


def index_present(manifest):
    present = {}
    for a in manifest.get("artifacts", []):
        present[(a.get("number"), a.get("option"))] = a
    return present


def gate_state(entry):
    gates = (entry or {}).get("gates") or {}
    states = {g: gates.get(g, "not_run") for g in GATES}
    passed = all(states[g] in TERMINAL_GATE_STATES for g in GATES)
    failed = [g for g in GATES if states[g] == "fail"]
    return states, passed, failed


def build_plan(manifest):
    present = index_present(manifest)
    required = required_artifacts(manifest)
    steps = []
    done_numbers = set()

    for req in required:
        key = (req["number"], req["option"])
        entry = present.get(key)
        states, passed, failed = gate_state(entry)
        status = (entry or {}).get("status", "missing")

        blocked_by = [d for d in DEPENDS_ON[req["number"]] if d not in done_numbers]

        # Status enum is manifest.schema.json: present/missing/draft/needs-fix/retired.
        if entry and status == "present" and passed:
            action = "complete"
        elif failed:
            action = "fix_gate_failure"
        elif entry and status == "needs-fix":
            action = "fix_defect"
        elif entry and status == "present" and not passed:
            action = "run_gates"
        elif entry and status == "draft":
            action = "finish_and_gate"
        else:
            action = "build"

        steps.append({
            "artifact": req["number"],
            "name": req["name"],
            "option": req["option"],
            "format": req["format"],
            "builder": req["builder"],
            "filename": (entry or {}).get("filename"),
            "status": status,
            "gates": states,
            "gate_failures": failed,
            "blocked_by_artifacts": blocked_by,
            "action": action,
        })
        if action == "complete":
            done_numbers.add(req["number"])

    return steps


def quote_findings(manifest):
    out = []
    policy = manifest.get('commercial_policy') or {}
    floor = policy.get('margin_floor_pct')
    valid_policy = isinstance(policy.get('source'), str) and bool(policy['source'].strip())
    valid_policy &= isinstance(policy.get('verified_at'), str) and bool(policy['verified_at'].strip())
    if floor is not None:
        if isinstance(floor, bool) or not isinstance(floor, (int, float)) or not math.isfinite(floor) or not 0 <= floor <= 100:
            out.append('commercial_policy.margin_floor_pct must be a finite percentage from 0 to 100')
            floor = None
        elif not valid_policy:
            out.append('The margin policy needs its source and verification date before comparison')
            floor = None
    if manifest.get('options') and floor is None:
        out.append('No verified margin floor is available; commercial approval remains unresolved')
    for opt in manifest.get("options", []):
        name = opt.get("name")
        if not opt.get("quote_number"):
            out.append(f"option '{name}' has no Q-number; every artifact carrying a number needs one")
        if not opt.get("timeline_snapshot_id"):
            out.append(f"option '{name}' has no active timeline snapshot; revenue, cost, and margin are unsourced")
        margin = opt.get("margin_pct")
        if margin is not None:
            if isinstance(margin, bool) or not isinstance(margin, (int, float)) or not math.isfinite(margin):
                out.append(f"option '{name}' has an invalid margin percentage")
            elif floor is not None and margin < floor:
                out.append(f"option '{name}' has margin {margin} below the configured floor {floor}; "
                           "follow the confirmed project exception policy")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--spec-version", default=SPEC_VERSION)
    ap.add_argument("--format", choices=["json", "text"], default="json")
    args = ap.parse_args()

    manifest = load(args.manifest)
    for field in ("code", "name", "shape", "options"):
        if field not in manifest:
            fail(f"manifest is missing required field: {field}")

    steps = build_plan(manifest)
    findings = quote_findings(manifest)

    declared = manifest.get("spec_version")
    if declared != args.spec_version:
        findings.append(f"manifest declares spec_version {declared!r}; planner is spec {args.spec_version}. "
                        "Re-check the artifact set against SPEC.md before building.")

    todo = [s for s in steps if s["action"] != "complete"]
    ready = [s for s in todo if not s["blocked_by_artifacts"]]

    plan = {
        "playbook": manifest.get("code"),
        "playbook_name": manifest.get("name"),
        "spec_version": args.spec_version,
        "stage": manifest.get("stage"),
        "totals": {
            "required": len(steps),
            "complete": len(steps) - len(todo),
            "outstanding": len(todo),
            "ready_now": len(ready),
        },
        "findings": findings,
        "next_step": ready[0] if ready else None,
        "steps": steps,
    }

    if args.format == "json":
        print(json.dumps(plan, indent=2))
    else:
        print(f"{plan['playbook']} · {plan['playbook_name']} · stage {plan['stage']}")
        print(f"  {plan['totals']['complete']}/{plan['totals']['required']} complete, "
              f"{plan['totals']['ready_now']} ready to build now")
        for f in findings:
            print(f"  FINDING  {f}")
        for s in steps:
            tag = f"{s['artifact']:02d}"
            opt = f" [{s['option']}]" if s["option"] else ""
            blocked = f" blocked by {s['blocked_by_artifacts']}" if s["blocked_by_artifacts"] else ""
            print(f"  {tag} {s['name']}{opt}: {s['action']}{blocked}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
