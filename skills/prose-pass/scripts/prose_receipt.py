#!/usr/bin/env python3
"""Machine-checkable receipts for a prose-pass rewrite.

The failure this closes: every mechanism that referenced prose-pass invoked the
checker and called that a pass. The checker is the floor. The rewrite job, the
one that grows thin prose into specific prose and strips the machine voice, left
no evidence, so nothing downstream could tell a real pass from a mention. A
receipt is that evidence, and the quality gate refuses a narrative artifact
marked final without one.

Two commands:

    python3 prose_receipt.py emit ARTIFACT --out receipt.json \
        [--before-file COPY] [--protected ITEM ...] [--change NOTE ...] \
        [--no-change-justification TEXT]

    python3 prose_receipt.py validate receipt.json

`emit` measures what it can measure: hashes, the checker's findings by category
on the artifact as it stands, and, when a pre-rewrite copy is given, the
before-state findings and a figure tie-out. `validate` re-derives every
measurable claim and fails the receipt when the record and the artifact
disagree.

Validation rules, each a named failure:

  missing-field        a required field is absent
  artifact-missing     the artifact the receipt describes is gone
  hash-mismatch        the artifact changed after the receipt was written
  lazy-pass            byte-identical before and after with no justified
                       no-change assessment
  hollow-justification a no-change claim on prose with a checker finding
  unlogged-changes     the text changed but the receipt records no changes
  standing-findings    the checker reports one or more findings on the artifact
  unresolved-not-allowed an old receipt attempts to waive a standing finding
  figure-invention     a number in the artifact absent from the before copy and
                       not declared with a source via --added-figure (only
                       checked when the before copy is available). A rewrite may
                       add a specific, but only one it can attribute.

Exit 0: receipt valid. Exit 1: one or more failures. Exit 2: unusable input.

Standard library only. The checker is invoked from this same skill folder.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHECKER = HERE / "writing_check.py"
CONFIG = HERE.parent / "house.json"

RECEIPT_VERSION = "1"

REQUIRED_FIELDS = (
    "receipt_version",
    "artifact",
    "before_sha256",
    "after_sha256",
    "protected",
    "issues_found",
    "changes_made",
    "unresolved_flags",
    "generated_at",
)

NUMBER = re.compile(r"(?<![\w.])(\$?\d[\d,]*(?:\.\d+)?%?)(?![\w])")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_checker(path: Path) -> dict:
    """The checker's findings for one file, keyed by rule, with severities."""
    proc = subprocess.run(
        [sys.executable, str(CHECKER), "--config", str(CONFIG), "--json", str(path)],
        capture_output=True, text=True)
    if proc.returncode == 2:
        raise RuntimeError("prose_check could not read {}: {}".format(
            path, proc.stderr.strip() or proc.stdout.strip()))
    try:
        report = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("prose_check emitted unparseable output: {}".format(exc))
    findings = next(iter(report.values()), {}).get("findings", [])
    by_rule: dict = {}
    for finding in findings:
        by_rule[finding["rule"]] = {
            "severity": finding["severity"],
            "message": finding["message"],
        }
    return by_rule


def numbers_in(text: str) -> set:
    return {m.group(1).replace(",", "") for m in NUMBER.finditer(text)}


def emit(args: argparse.Namespace) -> int:
    artifact = Path(args.artifact).resolve()
    if not artifact.is_file():
        print("artifact not found: {}".format(artifact))
        return 2
    after_hash = sha256_file(artifact)
    issues_after = run_checker(artifact)

    before_hash = after_hash
    issues_before: dict = {}
    invented: list = []
    if args.before_file:
        before = Path(args.before_file)
        if not before.is_file():
            print("before copy not found: {}".format(before))
            return 2
        before_hash = sha256_file(before)
        issues_before = run_checker(before)
        invented = sorted(
            numbers_in(artifact.read_text(encoding="utf-8"))
            - numbers_in(before.read_text(encoding="utf-8")))

    figures_added = []
    for entry in args.added_figure or []:
        value, _, source = entry.partition(":")
        figures_added.append({"value": value.strip().replace(",", ""),
                              "source": source.strip() or "unstated"})

    receipt = {
        "receipt_version": RECEIPT_VERSION,
        "artifact": str(artifact),
        "before_sha256": before_hash,
        "after_sha256": after_hash,
        "protected": list(args.protected or []),
        "issues_found": {
            "before": issues_before,
            "after": issues_after,
        },
        "changes_made": list(args.change or []),
        "no_change_justification": args.no_change_justification or None,
        "unresolved_flags": [],
        "figures_added": figures_added,
        "figure_check": {
            "ran": bool(args.before_file),
            "invented_numbers": invented,
        },
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    out = Path(args.out)
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print("receipt written: {}".format(out))
    verdict = validate_receipt(receipt, quiet=False)
    return 0 if not verdict else 1


def validate_receipt(receipt: dict, quiet: bool = True) -> list:
    """Every failure as (code, message). Empty means valid."""
    failures = []

    def fail(code: str, message: str) -> None:
        failures.append((code, message))
        if not quiet:
            print("FAIL {}: {}".format(code, message))

    if not isinstance(receipt, dict):
        fail("receipt-shape", "receipt must be an object")
        return failures
    for field in REQUIRED_FIELDS:
        if field not in receipt:
            fail("missing-field", "required field absent: {}".format(field))
    if failures:
        return failures
    for field in ("artifact", "before_sha256", "after_sha256", "generated_at"):
        if not isinstance(receipt[field], str) or not receipt[field].strip():
            fail("receipt-shape", "{} must be nonempty text".format(field))
    for field in ("protected", "changes_made", "unresolved_flags"):
        if not isinstance(receipt[field], list):
            fail("receipt-shape", "{} must be a list".format(field))
    if not isinstance(receipt["issues_found"], dict):
        fail("receipt-shape", "issues_found must be an object")
    if receipt.get("no_change_justification") is not None and not isinstance(receipt["no_change_justification"], str):
        fail("receipt-shape", "no_change_justification must be text")
    if "figure_check" in receipt and not isinstance(receipt["figure_check"], dict):
        fail("receipt-shape", "figure_check must be an object")
    added = receipt.get("figures_added", [])
    if not isinstance(added, list) or any(not isinstance(item, dict) or not isinstance(item.get("value"), str) or not isinstance(item.get("source"), str) for item in added):
        fail("receipt-shape", "figures_added must list values and sources as text")
    figure = receipt.get("figure_check", {})
    if isinstance(figure, dict) and (type(figure.get("ran", False)) is not bool or not isinstance(figure.get("invented_numbers", []), list) or any(not isinstance(v, str) for v in figure.get("invented_numbers", []))):
        fail("receipt-shape", "figure_check needs a boolean ran flag and a list of number strings")
    if failures:
        return failures

    artifact = Path(receipt["artifact"])
    if not artifact.is_file():
        fail("artifact-missing", "artifact not found: {}".format(artifact))
        return failures

    current = sha256_file(artifact)
    if current != receipt["after_sha256"]:
        fail("hash-mismatch",
             "artifact changed after the receipt was written; re-run the pass")
        return failures

    issues_now = run_checker(artifact)
    standing_findings = set(issues_now)
    unresolved = receipt.get("unresolved_flags") or []
    if unresolved:
        fail("unresolved-not-allowed",
             "checker findings must be fixed; unresolved flags cannot waive them")

    unchanged = receipt["before_sha256"] == receipt["after_sha256"]
    justification = (receipt.get("no_change_justification") or "").strip()
    if unchanged:
        if not justification:
            fail("lazy-pass",
                 "byte-identical result with no justified no-change assessment")
        if standing_findings:
            fail("hollow-justification",
                 "no-change claim while the checker reports findings: {}".format(
                     ", ".join(sorted(standing_findings))))
    else:
        if not receipt.get("changes_made"):
            fail("unlogged-changes",
                 "the text changed but the receipt records no changes")

    if standing_findings and not unchanged:
        fail("standing-findings",
             "checker findings remain after the rewrite: {}".format(
                 ", ".join(sorted(standing_findings))))

    figure_check = receipt.get("figure_check") or {}
    if figure_check.get("ran"):
        declared = {entry.get("value") for entry in receipt.get("figures_added") or []
                    if (entry.get("source") or "unstated") != "unstated"}
        undeclared = [n for n in figure_check.get("invented_numbers") or []
                      if n.replace(",", "").lstrip("$").rstrip("%") not in
                      {d.lstrip("$").rstrip("%") for d in declared}]
        if undeclared:
            fail("figure-invention",
                 "numbers absent from the before copy and declared with no "
                 "source: {}".format(", ".join(undeclared)))

    return failures


def validate(args: argparse.Namespace) -> int:
    path = Path(args.receipt)
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print("unreadable receipt {}: {}".format(path, exc))
        return 2
    failures = validate_receipt(receipt, quiet=False)
    if failures:
        print("receipt INVALID: {} failure(s)".format(len(failures)))
        return 1
    print("receipt valid: {} covers {} at {}".format(
        path.name, receipt["artifact"], receipt["generated_at"]))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p_emit = sub.add_parser("emit", help="measure the artifact and write a receipt")
    p_emit.add_argument("artifact")
    p_emit.add_argument("--out", required=True)
    p_emit.add_argument("--before-file",
                        help="pre-rewrite copy, enabling before-state findings and figure tie-out")
    p_emit.add_argument("--protected", action="append",
                        help="protected content the pass must not alter (repeatable)")
    p_emit.add_argument("--change", action="append",
                        help="a change the pass made, by category (repeatable)")
    p_emit.add_argument("--no-change-justification",
                        help="why sound prose was left alone, when nothing changed")
    p_emit.add_argument("--added-figure", action="append",
                        help="VALUE:SOURCE for a number the rewrite added from evidence (repeatable)")
    p_emit.set_defaults(func=emit)

    p_val = sub.add_parser("validate", help="re-derive and judge an existing receipt")
    p_val.add_argument("receipt")
    p_val.set_defaults(func=validate)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except RuntimeError as exc:
        print(str(exc))
        return 2


if __name__ == "__main__":
    sys.exit(main())
