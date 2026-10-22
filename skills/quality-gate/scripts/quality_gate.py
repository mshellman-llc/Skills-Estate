#!/usr/bin/env python3
"""Deterministic validator for an Estate quality record.

The skill body states the contract: a quality record names the artifact, the
controls it selected, every check with a verdict and its supporting citation, and
a release verdict. This turns the four "fail closed" rules in that body into
mechanical checks, so a record cannot claim release while a high-risk assertion
rests on nothing.

The rule that matters most is the last one. A record may not release when a
financial figure, contract scope, approval status, or go/no-go conclusion has no
passing check behind it. Stating the control's name is not running it, so a check
that cites nothing is treated as not having run.

Standard library only, Python 3.9 compatible.

    python3 quality_gate.py record.json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

VERDICTS = {"pass", "fail", "blocked", "not_applicable"}

# Release-blocking assertion classes, taken verbatim from the skill body's
# fail-closed rule. Each needs a passing, cited check before release.
FAIL_CLOSED = {
    "financial_figure",
    "contract_scope",
    "approval_status",
    "go_no_go",
}

REQUIRED_FIELDS = (
    "artifact",
    "controls_selected",
    "checks",
    "release",
    "hub_update",
)

# The controls the skill body routes to, keyed by the content that triggers them.
ROUTED_CONTROLS = {
    "client_prose": "prose-pass",
    "brand_render": "brand-renderer",
    "contract_scope": "sow-quality",
}


@dataclass
class Finding:
    level: str
    code: str
    message: str

    def to_dict(self) -> Dict[str, str]:
        return {"level": self.level, "code": self.code, "message": self.message}


@dataclass
class GateVerdict:
    released: bool
    blockers: List[str] = field(default_factory=list)
    findings: List[Finding] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(f.level == "error" for f in self.findings)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "released": self.released,
            "blockers": self.blockers,
            "findings": [f.to_dict() for f in self.findings],
            "valid": self.ok,
        }


def _cited(check: Dict[str, Any]) -> bool:
    """A citation must name a location, not merely exist as an empty key."""
    citation = check.get("citation")
    return isinstance(citation, str) and citation.strip() != ""


def validate(record: Any) -> GateVerdict:
    findings: List[Finding] = []
    blockers: List[str] = []

    def error(code: str, message: str) -> None:
        findings.append(Finding("error", code, message))

    if not isinstance(record, dict):
        return GateVerdict(False, [], [Finding("error", "shape", "record is not an object")])

    for key in REQUIRED_FIELDS:
        if key not in record:
            error("missing-field", "required field absent: {}".format(key))
    if findings:
        return GateVerdict(False, blockers, findings)

    checks = record.get("checks")
    if not isinstance(checks, list) or not checks:
        error("no-checks", "checks must be a non-empty list; a record with no checks "
                           "grades nothing")
        return GateVerdict(False, blockers, findings)

    seen = set()
    for index, check in enumerate(checks):
        where = "checks[{}]".format(index)
        if not isinstance(check, dict):
            error("check-shape", "{} is not an object".format(where))
            continue
        control = check.get("control")
        if not control:
            error("check-control", "{} names no control".format(where))
            continue
        if control in seen:
            error("duplicate-check", "{} repeats control {}".format(where, control))
        seen.add(control)
        verdict = check.get("verdict")
        if verdict not in VERDICTS:
            error("check-verdict", "{}: verdict {!r} is not one of {}".format(
                where, verdict, ", ".join(sorted(VERDICTS))))
            continue
        # A pass has to point at something. This is the "do not claim a
        # downstream control ran" rule, enforced rather than asserted.
        if verdict == "pass" and not _cited(check):
            error("uncited-pass", "{}: control {} passed with no citation".format(
                where, control))
        if verdict in ("fail", "blocked"):
            blockers.append("{}: {}".format(control, verdict))

    # Every routed control the artifact's content requires must appear.
    artifact = record.get("artifact")
    if not isinstance(artifact, dict):
        error("artifact-shape", "artifact must be an object naming the thing graded")
        return GateVerdict(False, blockers, findings)
    # not_applicable contradicts a declaration that the control is needed.
    ran = {c.get("control") for c in checks
           if isinstance(c, dict) and c.get("verdict") in ("pass", "fail", "blocked")}
    for flag, control in sorted(ROUTED_CONTROLS.items()):
        if artifact.get(flag) and control not in ran:
            error("unrouted-control",
                  "artifact declares {} but no check ran {}".format(flag, control))

    # A narrative artifact marked final needs a prose-pass RECEIPT, not a
    # mention. The checker alone is the floor; the receipt proves the rewrite
    # pass ran and either changed the text or justified leaving it alone.
    # prose_receipt.py (in the prose-pass skill) judges the receipt itself;
    # this gate refuses a record that claims finality without one.
    if artifact.get("narrative_final"):
        prose_checks = [c for c in checks if isinstance(c, dict)
                        and c.get("control") == "prose-pass"]
        if not prose_checks:
            error("prose-receipt-missing",
                  "artifact is narrative and final but no prose-pass check ran")
            blockers.append("prose-pass: no receipt")
        else:
            receipt = prose_checks[0].get("receipt")
            if not (isinstance(receipt, str) and receipt.strip()):
                error("prose-receipt-missing",
                      "prose-pass check carries no receipt; a pass without a "
                      "receipt is a mention, not enforcement")
                blockers.append("prose-pass: no receipt")

    # The fail-closed rule.
    for assertion in record.get("assertions") or []:
        if not isinstance(assertion, dict):
            error("assertion-shape", "assertions entries must be objects")
            continue
        kind = assertion.get("kind")
        if kind not in FAIL_CLOSED:
            continue
        support = assertion.get("supported_by")
        backing = [c for c in checks if isinstance(c, dict)
                   and c.get("control") == support
                   and c.get("verdict") == "pass" and _cited(c)]
        if not backing:
            error("fail-closed",
                  "assertion {!r} of kind {} has no passing cited check; "
                  "release must fail closed".format(
                      assertion.get("id") or assertion.get("text") or "?", kind))
            blockers.append("fail-closed: {}".format(kind))

    released = bool(record.get("release", {}).get("released")) \
        if isinstance(record.get("release"), dict) else False
    if released and blockers:
        error("released-with-blockers",
              "record claims release while {} blocker(s) stand: {}".format(
                  len(blockers), "; ".join(blockers)))

    hub = record.get("hub_update")
    if not isinstance(hub, dict) or "status" not in hub:
        error("hub-update", "hub_update must record the Knowledge Hub write status")

    return GateVerdict(released and not blockers, blockers, findings)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path, help="a quality record as JSON")
    parser.add_argument("--json", action="store_true", help="emit the verdict as JSON")
    args = parser.parse_args(argv)

    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print("{}: unreadable ({})".format(args.record, exc))
        return 2

    verdict = validate(record)
    if args.json:
        print(json.dumps(verdict.to_dict(), indent=2))
    else:
        for finding in verdict.findings:
            print("{}: {} ({})".format(finding.level.upper(), finding.message, finding.code))
        print("release: {}".format("yes" if verdict.released else "no"))
        if verdict.blockers:
            print("blockers: {}".format("; ".join(verdict.blockers)))
    return 0 if verdict.ok else 1


if __name__ == "__main__":
    sys.exit(main())
