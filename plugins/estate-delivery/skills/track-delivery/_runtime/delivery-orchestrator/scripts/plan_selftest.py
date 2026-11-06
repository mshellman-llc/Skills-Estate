#!/usr/bin/env python3
"""Selftest for plan.py. Deterministic, exits nonzero on any failure."""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.join(HERE, "plan.py")
FIX = os.path.join(HERE, "fixtures")

failures = []


def run(args):
    return subprocess.run(
        [sys.executable, PLAN] + args,
        capture_output=True, text=True)


def check(name, cond, detail=""):
    if cond:
        print("PASS %s" % name)
    else:
        print("FAIL %s %s" % (name, detail))
        failures.append(name)


# 1. Missing state file: full plan from the handoff, new-engagement note.
r = run([os.path.join(FIX, "does_not_exist.md")])
check("missing_state_exit0", r.returncode == 0, r.stderr)
check("missing_state_starts_at_handoff", "Current stage: S2D Handoff" in r.stdout)
check("missing_state_names_handoff_skill", "prepare-delivery-handoff" in r.stdout)
check("missing_state_says_create_file",
      "treating this as a new engagement" in r.stdout)
check("missing_state_lists_all_stages",
      all(s in r.stdout for s in
          ["Mobilize", "Analyze", "Design", "Build", "Validate",
           "Deploy", "Closeout"]))
check("missing_state_zero_findings", "Findings: 0" in r.stdout)

# 2. Mid-engagement at Analyze.
r = run([os.path.join(FIX, "mid_analyze.md")])
check("mid_exit0", r.returncode == 0, r.stderr)
check("mid_current_stage", "Current stage: 02 Analyze" in r.stdout)
check("mid_next_gate", "Requirements Document co-signed" in r.stdout)
check("mid_owner",
      "capture-requirements; map-journey when needed" in r.stdout)
check("mid_handoff_not_remaining", "S2D  Handoff" not in r.stdout)
check("mid_build_no_skill", "the configured project implementation workflow" in r.stdout)
check("mid_cross_cutting", "track-delivery" in r.stdout)
check("mid_governors",
      "evidence-core, brand-renderer, review-writing" in r.stdout)
check("mid_zero_findings", "Findings: 0" in r.stdout)
check("mid_engagement_name", "Acme Corp CPQ Implementation" in r.stdout)

# 2b. Same fixture, JSON contract.
r = run([os.path.join(FIX, "mid_analyze.md"), "--json"])
check("mid_json_exit0", r.returncode == 0, r.stderr)
payload = json.loads(r.stdout)
check("mid_json_stage", payload["current_stage"]["id"] == "02")
check("mid_json_remaining_count", len(payload["remaining"]) == 6,
      "got %d" % len(payload["remaining"]))
check("mid_json_no_findings", payload["findings"] == [])
check("mid_json_not_complete", payload["complete"] is False)

# 3. Everything signed: complete, closeout harvest reminder, comparables gap.
r = run([os.path.join(FIX, "complete.md")])
check("complete_exit0", r.returncode == 0, r.stderr)
check("complete_says_complete", "All recorded gates passed. Verify the project acceptance" in r.stdout)
check("complete_flags_comparables_gap",
      "Use the project's actual reusable-asset destination" in r.stdout)
check("complete_zero_findings", "Findings: 0" in r.stdout)

# 4. Out-of-order gates: requirements signed while charter open. Plan restarts
#    at Mobilize; two findings (out-of-order pass, declared stage disagrees).
r = run([os.path.join(FIX, "out_of_order.md")])
check("ooo_exit0", r.returncode == 0, r.stderr)
check("ooo_restarts_at_mobilize", "Current stage: 01 Mobilize" in r.stdout)
check("ooo_flags_out_of_order",
      "requirements_cosigned is marked passed but earlier gate charter_signed"
      in r.stdout)
check("ooo_flags_declared_stage", "declared stage 'design' disagrees" in r.stdout)
check("ooo_two_findings", "Findings (2):" in r.stdout)

# 5. Malformed lines: unparseable line, unknown gate key, unknown status.
#    All flagged, none fatal, unknown status treated as open.
r = run([os.path.join(FIX, "malformed.md")])
check("malformed_exit0", r.returncode == 0, r.stderr)
check("malformed_flags_unparseable", "unparseable gate line" in r.stdout)
check("malformed_flags_unknown_key", "unknown gate key 'kickoff_party'" in r.stdout)
check("malformed_flags_unknown_status", "unknown status 'probably'" in r.stdout)
check("malformed_current_stage", "Current stage: 01 Mobilize" in r.stdout)

# 6. Determinism: identical output across two runs.
a = run([os.path.join(FIX, "mid_analyze.md")]).stdout
b = run([os.path.join(FIX, "mid_analyze.md")]).stdout
check("deterministic", a == b)

# 7. No em dashes in any output.
outs = [run([os.path.join(FIX, f)]).stdout for f in os.listdir(FIX)]
outs.append(run([os.path.join(FIX, "does_not_exist.md")]).stdout)
check("no_em_dashes_in_output", all("\u2014" not in o for o in outs))

print()
if failures:
    print("SELFTEST FAILED: %d failure(s): %s" % (len(failures), ", ".join(failures)))
    sys.exit(1)
print("SELFTEST PASSED: all checks green")
