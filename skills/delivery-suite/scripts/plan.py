#!/usr/bin/env python3
"""Deterministic delivery planner for delivery-suite.

Reads a per-engagement DELIVERY-STATE.md (spec: references/delivery-state-spec.md)
and prints the ordered remaining stages, the owning skill for each, and the next
gate. Content-free: it never invents facts, it only reads gate statuses.

Usage:
    python3 plan.py [path/to/DELIVERY-STATE.md] [--json]

If the path is omitted or the file does not exist, the planner assumes a brand
new engagement (nothing signed yet) and prints the full plan from the handoff,
plus an instruction to create the state file.

Exit codes: 0 on success (findings are printed, not fatal), 2 on unreadable input.
"""

import json
import re
import sys

# The map. Order is the lifecycle. Never renumber.
# (stage_id, stage_name, gate_key, gate_label, gate_holder, owner)
STAGES = [
    ("S2D", "Handoff", "brief_accepted",
     "Handoff brief accepted by the delivery team",
     "delivery team",
     "s2d-handoff"),
    ("01", "Mobilize", "charter_signed",
     "Project Charter delivered and signed off",
     "client",
     "aleysian-delivery-kickoff"),
    ("02", "Analyze", "requirements_cosigned",
     "Requirements Document co-signed",
     "client",
     "requirements-capture + journey-mapping"),
    ("03", "Design", "sdd_cosigned",
     "Solution Design Document co-signed",
     "client",
     "architecture-doc + solution-brief (build-reference mode)"),
    ("04", "Build", "build_complete",
     "Build complete in sandbox",
     "delivery team",
     "no artifact skill by design (human build; delivery-status keeps the cadence)"),
    ("05", "Validate", "go_no_go",
     "Go / no-go co-signed",
     "client",
     "aleysian-uat-validation"),
    ("06", "Deploy", "golive_acceptance",
     "Go-Live Acceptance issued (deemed-acceptance clock per the SOW clause)",
     "client",
     "cutover-closeout"),
    ("06b", "Closeout", "hypercare_closeout",
     "Hypercare Closeout delivered (lessons and asset harvest complete)",
     "delivery team",
     "cutover-closeout"),
]

GATE_KEYS = [s[2] for s in STAGES]
PASSED = {"signed", "met", "accepted", "issued", "delivered"}
OPEN = {"open", "pending", "blocked"}

CROSS_CUTTING = ("delivery-status (weekly status, RAID and decision "
                 "stewardship, scope drift to change-order candidates) runs from "
                 "01 Mobilize onward")
GOVERNORS = "evidence-core, brand-renderer, prose-pass"
TRUTH = ("executed SOW/quote > artifact files > DELIVERY-STATE.md > memory > chat")


def parse_state(text):
    """Parse a DELIVERY-STATE.md. Returns (meta, declared_stage, gates, findings)."""
    findings = []
    meta = {}
    declared_stage = None
    gates = {}
    section = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        m = re.match(r"^##+\s+(.*)$", line)
        if m:
            section = m.group(1).strip().lower()
            continue
        if section is None and line.startswith("- "):
            m = re.match(r"^-\s*([^:]+):\s*(.*)$", line)
            if m:
                meta[m.group(1).strip().lower()] = m.group(2).strip()
            continue
        if section == "stage":
            m = re.match(r"^(?:-\s*)?current:\s*(\S+)", line, re.I)
            if m:
                declared_stage = m.group(1).strip().lower()
            continue
        if section == "gates" and line.startswith("- "):
            m = re.match(r"^-\s*([a-z0-9_]+):\s*(\S+)(?:\s+(\S.*))?$", line)
            if not m:
                findings.append("unparseable gate line: %r" % line)
                continue
            key, status = m.group(1), m.group(2).lower().rstrip(",.")
            if key not in GATE_KEYS:
                findings.append("unknown gate key %r (valid: %s)"
                                % (key, ", ".join(GATE_KEYS)))
                continue
            if status not in PASSED | OPEN:
                findings.append("gate %s has unknown status %r "
                                "(passed: %s; open: %s)"
                                % (key, status,
                                   "/".join(sorted(PASSED)), "/".join(sorted(OPEN))))
                status = "open"
            gates[key] = status
    return meta, declared_stage, gates, findings


def compute(meta, declared_stage, gates, findings):
    """Derive the current position from gates. Gates outrank the declared stage."""
    # First gate in lifecycle order that is not passed marks the current stage.
    current_idx = len(STAGES)
    for i, stage in enumerate(STAGES):
        if gates.get(stage[2], "open") not in PASSED:
            current_idx = i
            break
    # Out-of-order passes: a passed gate after the first open one.
    for stage in STAGES[current_idx + 1:]:
        if gates.get(stage[2], "open") in PASSED:
            findings.append(
                "gate %s is marked passed but earlier gate %s is not; the plan "
                "restarts at the earliest open gate. Verify against the artifact "
                "files (truth hierarchy: %s)."
                % (stage[2], STAGES[current_idx][2], TRUTH))
    # Declared stage that disagrees with the gates.
    if declared_stage is not None and current_idx < len(STAGES):
        want = STAGES[current_idx][1].lower()
        if declared_stage not in (want, STAGES[current_idx][0].lower()):
            findings.append(
                "declared stage %r disagrees with the gate ledger, which puts the "
                "engagement at %s %s. Gates win; fix the Stage line."
                % (declared_stage, STAGES[current_idx][0], STAGES[current_idx][1]))
    remaining = STAGES[current_idx:]
    return current_idx, remaining


def render_text(meta, current_idx, remaining, findings, state_note):
    out = []
    eng = meta.get("engagement", "(engagement not named in state file)")
    asof = meta.get("as of", meta.get("as-of", "(no as-of date)"))
    out.append("DELIVERY PLAN  engagement: %s  as of: %s" % (eng, asof))
    out.append("State source: %s" % state_note)
    out.append("Truth hierarchy: %s" % TRUTH)
    out.append("")
    if current_idx >= len(STAGES):
        out.append("All gates passed. Engagement complete.")
        out.append("Confirm the closeout harvest landed: lessons and reusable "
                   "assets from cutover-closeout feed the next handoff. "
                   "No prior-deal comparables library exists yet to receive them; "
                   "flag that gap, do not invent a destination.")
    else:
        cur = STAGES[current_idx]
        out.append("Current stage: %s %s" % (cur[0], cur[1]))
        out.append("Next gate: %s (held by: %s)" % (cur[3], cur[4]))
        out.append("Owning skill now: %s" % cur[5])
        out.append("")
        out.append("Remaining stages, in order:")
        for sid, name, _key, gate, _holder, owner in remaining:
            out.append("  %-4s %-9s owner: %s" % (sid, name, owner))
            out.append("       gate: %s" % gate)
    out.append("")
    out.append("Cross-cutting: %s" % CROSS_CUTTING)
    out.append("Governors, always: %s" % GOVERNORS)
    out.append("")
    if findings:
        out.append("Findings (%d):" % len(findings))
        for f in findings:
            out.append("  - %s" % f)
    else:
        out.append("Findings: 0")
    return "\n".join(out)


def main(argv):
    args = [a for a in argv[1:] if a != "--json"]
    as_json = "--json" in argv[1:]
    path = args[0] if args else "DELIVERY-STATE.md"
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        meta, declared, gates, findings = parse_state(text)
        state_note = path
    except FileNotFoundError:
        meta, declared, gates, findings = {}, None, {}, []
        state_note = ("%s not found: treating this as a new engagement at the "
                      "handoff. Create the state file per "
                      "references/delivery-state-spec.md before the first gate."
                      % path)
    except OSError as exc:
        print("plan.py: cannot read %s: %s" % (path, exc), file=sys.stderr)
        return 2
    current_idx, remaining = compute(meta, declared, gates, findings)
    if as_json:
        payload = {
            "engagement": meta.get("engagement"),
            "as_of": meta.get("as of", meta.get("as-of")),
            "state_source": state_note,
            "complete": current_idx >= len(STAGES),
            "current_stage": None if current_idx >= len(STAGES) else {
                "id": STAGES[current_idx][0],
                "name": STAGES[current_idx][1],
                "gate": STAGES[current_idx][3],
                "gate_holder": STAGES[current_idx][4],
                "owner": STAGES[current_idx][5],
            },
            "remaining": [
                {"id": s[0], "name": s[1], "gate_key": s[2], "gate": s[3],
                 "gate_holder": s[4], "owner": s[5]}
                for s in remaining
            ],
            "cross_cutting": CROSS_CUTTING,
            "governors": GOVERNORS,
            "truth_hierarchy": TRUTH,
            "findings": findings,
        }
        print(json.dumps(payload, indent=2))
    else:
        print(render_text(meta, current_idx, remaining, findings, state_note))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
