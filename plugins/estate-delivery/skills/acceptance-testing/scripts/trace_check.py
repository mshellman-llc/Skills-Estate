#!/usr/bin/env python3
"""Traceability gate for estate-uat-validation.

Verifies the identity invariant of the skill: every requirement is covered by
at least one test script or appears as a named gap with an owner and a reason;
every test script traces to known requirement IDs or is explicitly flagged as
an orphan; and the coverage counts presented in the go/no-go pack recompute
from the underlying files.

Inputs (CSV with a header row; column matching is case-insensitive):
  --requirements  one row per requirement. Uses the column named
                  "Requirement ID" or "Requirement Number", else the first
                  column.
  --scripts       one row per test script. Uses "Test Script ID" or
                  "Script ID" (else first column) for the script ID,
                  "Requirement IDs" / "Requirements" / "Traces To" for the
                  traced IDs (split on ; | or ,), and "Orphan Flag" /
                  "Orphan" for the orphan acknowledgement.
  --gaps          optional. One row per named coverage gap: "Requirement ID",
                  "Owner", "Reason" (and optionally "Resolve By").
  --gonogo        optional. JSON object of coverage counts as they appear in
                  the go/no-go pack. Every key present is recomputed and must
                  match. Recognized keys: total_requirements,
                  requirements_with_coverage, named_gaps, test_scripts_total,
                  orphan_scripts_flagged.

Exit codes: 0 gate passed, 1 gate failed, 2 usage or input error.
Run with --selftest to execute the embedded passing and failing fixtures.

Stdlib only. No third-party packages.
"""

import argparse
import csv
import io
import json
import re
import sys

SPLIT_RE = re.compile(r"[;|,]")

GONOGO_KEYS = (
    "total_requirements",
    "requirements_with_coverage",
    "named_gaps",
    "test_scripts_total",
    "orphan_scripts_flagged",
)


def _norm(name):
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())


def _pick_column(fieldnames, candidates):
    normed = {_norm(f): f for f in fieldnames or []}
    for cand in candidates:
        if _norm(cand) in normed:
            return normed[_norm(cand)]
    return None


def _read_csv(path_or_text, from_text=False):
    if from_text:
        handle = io.StringIO(path_or_text)
    else:
        handle = open(path_or_text, newline="", encoding="utf-8-sig")
    with handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("empty CSV (no header row)")
        return reader.fieldnames, [row for row in reader]


def load_requirements(source, from_text=False):
    fields, rows = _read_csv(source, from_text)
    col = _pick_column(fields, ["requirement id", "requirement number", "req id"]) or fields[0]
    ids = []
    for row in rows:
        rid = (row.get(col) or "").strip()
        if rid:
            ids.append(rid)
    return ids


def load_scripts(source, from_text=False):
    fields, rows = _read_csv(source, from_text)
    id_col = _pick_column(fields, ["test script id", "script id"]) or fields[0]
    req_col = _pick_column(fields, ["requirement ids", "requirements", "traces to", "requirement id"])
    orphan_col = _pick_column(fields, ["orphan flag", "orphan"])
    scripts = []
    for row in rows:
        sid = (row.get(id_col) or "").strip()
        if not sid:
            continue
        raw = (row.get(req_col) or "").strip() if req_col else ""
        req_ids = [r.strip() for r in SPLIT_RE.split(raw) if r.strip()]
        orphan_flag = (row.get(orphan_col) or "").strip() if orphan_col else ""
        scripts.append({"id": sid, "req_ids": req_ids, "orphan_flag": orphan_flag})
    return scripts


def load_gaps(source, from_text=False):
    fields, rows = _read_csv(source, from_text)
    id_col = _pick_column(fields, ["requirement id", "requirement number", "req id"]) or fields[0]
    owner_col = _pick_column(fields, ["owner"])
    reason_col = _pick_column(fields, ["reason", "why"])
    gaps = {}
    for row in rows:
        rid = (row.get(id_col) or "").strip()
        if not rid:
            continue
        gaps[rid] = {
            "owner": (row.get(owner_col) or "").strip() if owner_col else "",
            "reason": (row.get(reason_col) or "").strip() if reason_col else "",
        }
    return gaps


def run_checks(req_ids, scripts, gaps, gonogo):
    """Returns (failures, counts). failures is a list of strings; empty means pass."""
    failures = []

    seen = set()
    dupes = sorted({r for r in req_ids if r in seen or seen.add(r)})
    if dupes:
        failures.append("duplicate requirement IDs: " + ", ".join(dupes))
    req_set = set(req_ids)

    sid_seen = set()
    sid_dupes = sorted({s["id"] for s in scripts if s["id"] in sid_seen or sid_seen.add(s["id"])})
    if sid_dupes:
        failures.append("duplicate test script IDs: " + ", ".join(sid_dupes))

    covered = set()
    orphan_flagged = 0
    for s in scripts:
        known = [r for r in s["req_ids"] if r in req_set]
        unknown = [r for r in s["req_ids"] if r not in req_set]
        covered.update(known)
        is_orphan = not s["req_ids"] or bool(unknown)
        if is_orphan:
            if s["orphan_flag"]:
                orphan_flagged += 1
            else:
                if unknown:
                    failures.append(
                        "orphan script not flagged: %s traces to unknown requirement ID(s) %s "
                        "(scope drift; flag it and route to estate-delivery-status)"
                        % (s["id"], ", ".join(unknown))
                    )
                else:
                    failures.append(
                        "orphan script not flagged: %s traces to no requirement "
                        "(scope drift; flag it and route to estate-delivery-status)" % s["id"]
                    )

    uncovered = sorted(req_set - covered)
    for rid in uncovered:
        gap = gaps.get(rid)
        if gap is None:
            failures.append(
                "requirement %s has no test script and no named gap "
                "(unnamed coverage gaps block go/no-go)" % rid
            )
        elif not gap["owner"] or not gap["reason"]:
            failures.append(
                "named gap for %s is incomplete: owner and reason are both required" % rid
            )

    stale = sorted(set(gaps) - set(uncovered))
    for rid in stale:
        if rid in covered:
            failures.append("stale gap entry: %s is covered by a script; remove it from the gap list" % rid)
        else:
            failures.append("gap entry for unknown requirement ID: %s" % rid)

    counts = {
        "total_requirements": len(req_set),
        "requirements_with_coverage": len(covered & req_set),
        "named_gaps": len([r for r in uncovered if r in gaps]),
        "test_scripts_total": len(scripts),
        "orphan_scripts_flagged": orphan_flagged,
    }

    if gonogo is not None:
        for key in GONOGO_KEYS:
            if key in gonogo and int(gonogo[key]) != counts[key]:
                failures.append(
                    "go/no-go count mismatch: %s is stated as %s, recomputes to %s"
                    % (key, gonogo[key], counts[key])
                )
        unrecognized = sorted(set(gonogo) - set(GONOGO_KEYS))
        if unrecognized:
            failures.append("unrecognized go/no-go count key(s): " + ", ".join(unrecognized))

    return failures, counts


def report(failures, counts, out=sys.stdout):
    print("traceability counts (recomputed from source files):", file=out)
    for key in GONOGO_KEYS:
        print("  %s: %d" % (key, counts[key]), file=out)
    if failures:
        print("GATE FAILED: %d finding(s)" % len(failures), file=out)
        for f in failures:
            print("  FAIL: " + f, file=out)
        return 1
    print("GATE PASSED: 0 findings", file=out)
    return 0


# ---------------------------------------------------------------------------
# Embedded selftest fixtures. trace_check_selftest.py exercises the same
# checks through the CLI with files on disk; this covers the logic in-process.
# ---------------------------------------------------------------------------

FIX_REQS = "Requirement Number,Name\nCPE-001,Auto-apply price\nCPE-002,Tiered pricing\nCPE-003,Audit trail\n"
FIX_SCRIPTS_PASS = (
    "Test Script ID,Requirement IDs,Orphan Flag,Title\n"
    "TS-001,CPE-001,,Auto-apply happy path\n"
    "TS-002,CPE-001;CPE-002,,Tier boundaries\n"
    "TS-003,,orphan: regression suite carryover,Legacy smoke test\n"
)
FIX_GAPS_PASS = "Requirement ID,Owner,Reason,Resolve By\nCPE-003,BA,Audit object not built until sprint 6,2026-09-01\n"
FIX_GONOGO_PASS = {
    "total_requirements": 3,
    "requirements_with_coverage": 2,
    "named_gaps": 1,
    "test_scripts_total": 3,
    "orphan_scripts_flagged": 1,
}
FIX_SCRIPTS_FAIL_ORPHAN = (
    "Test Script ID,Requirement IDs,Orphan Flag\n"
    "TS-001,CPE-001,\n"
    "TS-002,CPE-002,\n"
    "TS-003,CPE-999,\n"
    "TS-004,CPE-003,\n"
)
FIX_GONOGO_FAIL = {"total_requirements": 3, "requirements_with_coverage": 3}


def selftest():
    ok = True

    def expect(label, cond):
        nonlocal ok
        status = "pass" if cond else "FAIL"
        print("  selftest %s: %s" % (status, label))
        ok = ok and cond

    reqs = load_requirements(FIX_REQS, from_text=True)
    scripts = load_scripts(FIX_SCRIPTS_PASS, from_text=True)
    gaps = load_gaps(FIX_GAPS_PASS, from_text=True)

    failures, counts = run_checks(reqs, scripts, gaps, FIX_GONOGO_PASS)
    expect("clean fixture passes with matching go/no-go counts", failures == [])
    expect("clean fixture counts recompute as expected", counts == FIX_GONOGO_PASS)

    failures, _ = run_checks(reqs, scripts, {}, None)
    expect("uncovered requirement without a named gap fails", any("CPE-003" in f and "no named gap" in f for f in failures))

    bad_gaps = load_gaps("Requirement ID,Owner,Reason\nCPE-003,,\n", from_text=True)
    failures, _ = run_checks(reqs, scripts, bad_gaps, None)
    expect("gap without owner and reason fails", any("incomplete" in f for f in failures))

    failures, _ = run_checks(reqs, load_scripts(FIX_SCRIPTS_FAIL_ORPHAN, from_text=True), gaps, None)
    expect("unflagged orphan (unknown requirement ID) fails", any("TS-003" in f and "orphan" in f for f in failures))

    failures, _ = run_checks(reqs, scripts, gaps, FIX_GONOGO_FAIL)
    expect("stated go/no-go count that does not recompute fails", any("count mismatch" in f for f in failures))

    stale = load_gaps("Requirement ID,Owner,Reason\nCPE-001,BA,already covered\n", from_text=True)
    failures, _ = run_checks(reqs, scripts, dict(gaps, **stale), None)
    expect("stale gap entry for a covered requirement fails", any("stale gap" in f for f in failures))

    print("SELFTEST %s" % ("PASSED" if ok else "FAILED"))
    return 0 if ok else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description="Traceability gate: requirements to test scripts to go/no-go counts.")
    parser.add_argument("--requirements", help="requirements CSV")
    parser.add_argument("--scripts", help="test scripts CSV")
    parser.add_argument("--gaps", help="named coverage gaps CSV (optional)")
    parser.add_argument("--gonogo", help="go/no-go coverage counts JSON (optional)")
    parser.add_argument("--selftest", action="store_true", help="run embedded fixtures and exit")
    args = parser.parse_args(argv)

    if args.selftest:
        return selftest()

    if not args.requirements or not args.scripts:
        parser.print_usage(sys.stderr)
        print("error: --requirements and --scripts are required (or use --selftest)", file=sys.stderr)
        return 2

    try:
        reqs = load_requirements(args.requirements)
        scripts = load_scripts(args.scripts)
        gaps = load_gaps(args.gaps) if args.gaps else {}
        gonogo = None
        if args.gonogo:
            with open(args.gonogo, encoding="utf-8") as fh:
                gonogo = json.load(fh)
            if not isinstance(gonogo, dict):
                raise ValueError("go/no-go counts JSON must be an object")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("error reading inputs: %s" % exc, file=sys.stderr)
        return 2

    if not reqs:
        print("error: requirements file contains no requirement IDs", file=sys.stderr)
        return 2

    failures, counts = run_checks(reqs, scripts, gaps, gonogo)
    return report(failures, counts)


if __name__ == "__main__":
    sys.exit(main())
