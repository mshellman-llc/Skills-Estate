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
import subprocess
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
ASSERTION_KINDS = FAIL_CLOSED | {"narrative", "other"}
STYLE_CAPABLE_SUFFIXES = {".html", ".htm", ".pptx", ".docx", ".xlsx", ".pdf"}

REQUIRED_FIELDS = (
    "artifact",
    "controls_selected",
    "checks",
    "release",
    "hub_update",
)

# The controls the skill body routes to, keyed by the content that triggers them.
ROUTED_CONTROLS = {
    "client_prose": "writing-diagnostics",
    "brand_render": "brand-renderer",
    "contract_scope": "review-contract-scope",
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


def _receipt_validator(module: Path) -> Optional[Path]:
    outer = module.parent.parent
    nested = (module.parent.name == '_runtime'
              and (outer / 'references/estate/writing.md').is_file())
    packaged = module.parent.name == '_runtime' or (module / 'references/estate/writing.md').is_file()
    package_root = outer if nested else module
    candidates = [module / '_runtime/writing-diagnostics/scripts/prose_receipt.py']
    if nested:
        candidates.append(outer / '_runtime/writing-diagnostics/scripts/prose_receipt.py')
    elif not packaged:
        candidates.append(module.parent / 'writing-diagnostics/scripts/prose_receipt.py')
    for candidate in candidates:
        if not candidate.is_file():
            continue
        if packaged:
            try:
                candidate.resolve().relative_to(package_root.resolve())
            except ValueError:
                continue
        return candidate
    return None


def validate(record: Any, base_dir: Optional[Path] = None) -> GateVerdict:
    explicit_base = base_dir is not None
    base_dir = Path(base_dir or Path.cwd()).resolve()
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

    artifact = record.get("artifact")
    if not isinstance(artifact, dict):
        error("artifact-shape", "artifact must be an object naming the thing graded")
    else:
        for flag in (*ROUTED_CONTROLS, "narrative_final"):
            if flag in artifact and type(artifact[flag]) is not bool:
                error("artifact-flag", "artifact.{} must be a boolean".format(flag))
        path = artifact.get("path")
        if (isinstance(path, str) and Path(path).suffix.lower() in STYLE_CAPABLE_SUFFIXES
                and "brand_render" not in artifact):
            error("brand-applicability", "artifact.brand_render must explicitly declare whether this file needs styled-output review")
    selected = record.get("controls_selected")
    if (not isinstance(selected, list) or not selected
            or any(not isinstance(c, str) or not c.strip() for c in selected)):
        error("selected-shape", "controls_selected must list nonempty control names")
    elif len(selected) != len(set(selected)):
        error("selected-duplicate", "controls_selected repeats a control")
    release = record.get("release")
    if not isinstance(release, dict) or type(release.get("released")) is not bool:
        error("release-shape", "release.released must be a boolean")
    assertions = record.get("assertions", [])
    if not isinstance(assertions, list):
        error("assertions-shape", "assertions must be a list")
    else:
        for index, assertion in enumerate(assertions):
            if (not isinstance(assertion, dict)
                    or not isinstance(assertion.get("kind"), str)
                    or not assertion["kind"].strip()):
                error("assertion-shape", "assertions[{}] needs a named kind".format(index))
            elif assertion["kind"] not in ASSERTION_KINDS:
                error("assertion-kind", "assertions[{}] has an unknown kind; use one of {}".format(
                    index, ", ".join(sorted(ASSERTION_KINDS))))
    hub = record.get("hub_update")
    if (not isinstance(hub, dict) or not isinstance(hub.get("status"), str)
            or not hub["status"].strip()):
        error("hub-update", "hub_update must record a nonempty write status")
    if findings:
        return GateVerdict(False, blockers, findings)

    seen = set()
    for index, check in enumerate(checks):
        where = "checks[{}]".format(index)
        if not isinstance(check, dict):
            error("check-shape", "{} is not an object".format(where))
            continue
        control = check.get("control")
        if not isinstance(control, str) or not control.strip():
            error("check-control", "{} names no control".format(where))
            continue
        if control in seen:
            error("duplicate-check", "{} repeats control {}".format(where, control))
        seen.add(control)
        verdict = check.get("verdict")
        if not isinstance(verdict, str) or verdict not in VERDICTS:
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

    for control in selected:
        if control not in seen:
            error("selected-missing", "selected control has no check: {}".format(control))

    # Every routed control the artifact's content requires must appear.
    # not_applicable contradicts a declaration that the control is needed.
    ran = {c.get("control") for c in checks
           if isinstance(c, dict) and isinstance(c.get("control"), str)
           and c.get("verdict") in ("pass", "fail", "blocked")}
    for flag, control in sorted(ROUTED_CONTROLS.items()):
        if artifact.get(flag) and control not in ran:
            error("unrouted-control",
                  "artifact declares {} but no check ran {}".format(flag, control))

    # A narrative artifact marked final needs a writing-diagnostics RECEIPT, not a
    # mention. A receipt binds current bytes and reruns diagnostics; the
    # recorded review declaration does not prove a person read the artifact.
    # prose_receipt.py (in the writing-diagnostics skill) judges the receipt itself;
    # this gate refuses a record that claims finality without one.
    if artifact.get("narrative_final"):
        prose_checks = [c for c in checks if isinstance(c, dict)
                        and c.get("control") == "writing-diagnostics"]
        if not prose_checks:
            error("prose-receipt-missing",
                  "artifact is narrative and final but no writing-diagnostics check ran")
            blockers.append("writing-diagnostics: no receipt")
        elif prose_checks[0].get("verdict") == "pass":
            receipt = prose_checks[0].get("receipt")
            if not (isinstance(receipt, str) and receipt.strip()):
                error("prose-receipt-missing",
                      "writing-diagnostics check carries no receipt; a pass without a "
                      "receipt is a mention, not enforcement")
                blockers.append("writing-diagnostics: no receipt")
            else:
                artifact_path = artifact.get("path")
                if not isinstance(artifact_path, str) or not artifact_path.strip():
                    error("prose-artifact-missing", "final narrative needs artifact.path to bind its receipt")
                elif not explicit_base and (not Path(receipt).is_absolute() or not Path(artifact_path).is_absolute()):
                    error("prose-path-base", "validate(record) needs base_dir when artifact or receipt paths are relative")
                else:
                    try:
                        receipt_path = (base_dir / receipt).resolve()
                        receipt_data = json.loads(receipt_path.read_text(encoding="utf-8"))
                        covered = receipt_data.get("artifact") if isinstance(receipt_data, dict) else None
                        if not isinstance(covered, str) or not covered.strip():
                            raise ValueError("receipt names no artifact")
                        if not Path(covered).is_absolute():
                            raise ValueError("receipt artifact path is relative; regenerate the receipt with an absolute artifact path")
                        if not Path(covered).samefile(base_dir / artifact_path):
                            raise ValueError("receipt covers a different artifact")
                        module = Path(__file__).resolve().parents[1]
                        validator = _receipt_validator(module)
                        if validator is None:
                            raise ValueError("bundled prose receipt validator is missing")
                        result = subprocess.run([sys.executable, str(validator), "validate", str(receipt_path)],
                                                cwd=base_dir, capture_output=True, text=True, timeout=30)
                        if result.returncode:
                            detail = (result.stdout.strip() + "\n" + result.stderr.strip()).strip()[-600:] or "validator returned exit {}".format(result.returncode)
                            raise ValueError("prose receipt validation failed: " + detail)
                    except (OSError, ValueError, RecursionError, subprocess.SubprocessError) as exc:
                        error("prose-receipt-invalid", str(exc))
                        blockers.append("writing-diagnostics: invalid receipt")
        elif prose_checks[0].get("verdict") not in ("fail", "blocked"):
            error("prose-receipt-missing", "a final narrative requires a passing prose check or an explicit blocker")

    # The fail-closed rule.
    for assertion in assertions:
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

    released = release["released"]
    if released and blockers:
        error("released-with-blockers",
              "record claims release while {} blocker(s) stand: {}".format(
                  len(blockers), "; ".join(blockers)))

    valid = not any(f.level == "error" for f in findings)
    return GateVerdict(released and not blockers and valid, blockers, findings)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path, help="a quality record as JSON")
    parser.add_argument("--json", action="store_true", help="emit the verdict as JSON")
    args = parser.parse_args(argv)

    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
    except (OSError, ValueError, RecursionError) as exc:
        print("{}: unreadable ({})".format(args.record, exc))
        return 2

    verdict = validate(record, args.record.resolve().parent)
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
