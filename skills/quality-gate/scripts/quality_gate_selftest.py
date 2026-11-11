#!/usr/bin/env python3
"""Self-test for the quality gate validator.

Every case asserts a behaviour the skill body promises. The rejection cases matter
more than the acceptance one: a gate that cannot refuse is not a gate.

    python3 quality_gate_selftest.py
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from quality_gate import validate  # noqa: E402

PASSES = 0
FAILURES = []


def check(label, got, want):
    global PASSES
    if got == want:
        PASSES += 1
    else:
        FAILURES.append("{}: got {!r}, want {!r}".format(label, got, want))


def codes(record):
    return {f.code for f in validate(record).findings}


# A complete, releasable record. Every other case is a mutation of this one, so a
# failure points at the mutation rather than at incidental shape problems.
GOOD = {
    "artifact": {
        "id": "SOW-000181",
        "type": "sow",
        "audience": "client",
        "client_prose": True,
        "contract_scope": True,
        "brand_render": False,
        "narrative_final": True,
    },
    "controls_selected": ["prose-pass", "sow-quality"],
    "checks": [
        {"control": "prose-pass", "verdict": "pass", "citation": "section 3, lines 40-58",
         "receipt": "artifacts/sow-000181-prose-receipt.json"},
        {"control": "sow-quality", "verdict": "pass", "citation": "scope table, rows 1-9"},
        {"control": "deal-desk-tieout", "verdict": "pass", "citation": "quote Q-000181, role rollup"},
        {"control": "brand-renderer", "verdict": "not_applicable"},
    ],
    "assertions": [
        {"id": "A1", "kind": "financial_figure", "supported_by": "deal-desk-tieout"},
        {"id": "A2", "kind": "contract_scope", "supported_by": "sow-quality"},
    ],
    "release": {"released": True},
    "hub_update": {"status": "written", "file": "07-deliverables-register.md"},
}

verdict = validate(GOOD)
check("complete record is valid", verdict.ok, True)
check("complete record releases", verdict.released, True)
check("complete record has no blockers", verdict.blockers, [])

# Required fields.
for field in ("artifact", "controls_selected", "checks", "release", "hub_update"):
    record = copy.deepcopy(GOOD)
    del record[field]
    check("missing {} is rejected".format(field), "missing-field" in codes(record), True)

# A pass must cite something. This is the rule that stops a record from claiming a
# control ran when it was only named.
record = copy.deepcopy(GOOD)
record["checks"][0]["citation"] = ""
check("uncited pass is rejected", "uncited-pass" in codes(record), True)
record = copy.deepcopy(GOOD)
del record["checks"][0]["citation"]
check("absent citation is rejected", "uncited-pass" in codes(record), True)
record = copy.deepcopy(GOOD)
record["checks"][0]["citation"] = "   "
check("whitespace citation is rejected", "uncited-pass" in codes(record), True)

# Verdict vocabulary.
record = copy.deepcopy(GOOD)
record["checks"][0]["verdict"] = "probably fine"
check("unknown verdict is rejected", "check-verdict" in codes(record), True)

# not_applicable needs no citation.
record = copy.deepcopy(GOOD)
check("not_applicable without citation is accepted", validate(record).ok, True)

# The bypass regression: a narrative artifact marked final with no prose-pass
# check at all must be refused, not waved through on the checker's reputation.
record = copy.deepcopy(GOOD)
record["checks"] = [c for c in record["checks"] if c["control"] != "prose-pass"]
record["artifact"]["client_prose"] = False
record["assertions"] = []
check("narrative final without prose-pass is rejected",
      "prose-receipt-missing" in codes(record), True)
check("and does not release", validate(record).released, False)

# The mention-is-not-enforcement regression: prose-pass ran but left no receipt.
record = copy.deepcopy(GOOD)
del record["checks"][0]["receipt"]
check("prose-pass without a receipt is rejected",
      "prose-receipt-missing" in codes(record), True)
record = copy.deepcopy(GOOD)
record["checks"][0]["receipt"] = "   "
check("whitespace receipt is rejected",
      "prose-receipt-missing" in codes(record), True)

# A non-final draft does not need the receipt yet.
record = copy.deepcopy(GOOD)
record["artifact"]["narrative_final"] = False
del record["checks"][0]["receipt"]
check("draft without receipt is accepted", validate(record).ok, True)

# Fail-closed: a financial figure with nothing behind it.
record = copy.deepcopy(GOOD)
record["assertions"][0]["supported_by"] = "tieout-that-never-ran"
check("unsupported financial figure fails closed", "fail-closed" in codes(record), True)
check("and does not release", validate(record).released, False)

# Fail-closed: the supporting check exists but did not pass.
record = copy.deepcopy(GOOD)
record["checks"][2]["verdict"] = "blocked"
check("blocked support fails closed", "fail-closed" in codes(record), True)

# Fail-closed: the supporting check passed but cites nothing.
record = copy.deepcopy(GOOD)
record["checks"][2]["citation"] = ""
check("uncited support fails closed", "fail-closed" in codes(record), True)

# A low-risk assertion class is not subject to the fail-closed rule.
record = copy.deepcopy(GOOD)
record["assertions"] = [{"id": "A3", "kind": "narrative", "supported_by": "nothing"}]
check("narrative assertion is not fail-closed", validate(record).ok, True)

# Release may not stand while a blocker stands.
record = copy.deepcopy(GOOD)
record["checks"][1]["verdict"] = "fail"
check("release with a failed check is rejected",
      "released-with-blockers" in codes(record), True)
check("and reports the blocker", validate(record).blockers != [], True)

# A blocked record that admits it is not released stays valid; it is an honest
# refusal, which the gate must permit.
record = copy.deepcopy(GOOD)
record["checks"][1]["verdict"] = "fail"
record["release"]["released"] = False
record["assertions"] = []
check("honest refusal is valid", validate(record).ok, True)
check("honest refusal does not release", validate(record).released, False)

# Routed controls: the artifact declares client prose, so prose-pass must appear.
record = copy.deepcopy(GOOD)
record["checks"] = [c for c in record["checks"] if c["control"] != "prose-pass"]
record["assertions"] = []
check("declared client prose requires prose-pass",
      "unrouted-control" in codes(record), True)
record = copy.deepcopy(GOOD)
record["artifact"]["brand_render"] = True
record["checks"] = [c for c in record["checks"]
                    if c["control"] != "brand-renderer"]
check("declared brand render requires the renderer",
      "unrouted-control" in codes(record), True)

# Structural refusals.
check("non-object record is rejected", "shape" in codes([]), True)
record = copy.deepcopy(GOOD)
record["checks"] = []
check("empty checks list is rejected", "no-checks" in codes(record), True)
record = copy.deepcopy(GOOD)
record["checks"] = "prose-pass passed"
check("checks as a string is rejected", "no-checks" in codes(record), True)
record = copy.deepcopy(GOOD)
record["checks"].append({"control": "prose-pass", "verdict": "pass", "citation": "again"})
check("duplicate control is rejected", "duplicate-check" in codes(record), True)
record = copy.deepcopy(GOOD)
record["checks"].append({"verdict": "pass", "citation": "somewhere"})
check("check with no control is rejected", "check-control" in codes(record), True)
record = copy.deepcopy(GOOD)
record["hub_update"] = {}
check("hub_update without status is rejected", "hub-update" in codes(record), True)
record = copy.deepcopy(GOOD)
record["artifact"] = "SOW-000181"
check("artifact as a string is rejected", "artifact-shape" in codes(record), True)

if FAILURES:
    print("SELFTEST FAILED")
    for line in FAILURES:
        print("  {}".format(line))
    sys.exit(1)
print("{} assertions passed".format(PASSES))
print("SELFTEST PASSED")
