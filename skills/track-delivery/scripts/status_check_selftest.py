#!/usr/bin/env python3
"""Selftest for status_check.py. Builds passing and failing fixtures and
asserts the gate's verdict on each. Exit 0 when every case behaves, 1
otherwise. Stdlib only. Run from anywhere:

  python3 status_check_selftest.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import status_check  # noqa: E402

RAID_LOG = """# RAID log: Acme CPQ

R-001 | Risk | Client SSO metadata not confirmed | J. Ortiz | Open | 2026-08-15 | Design gate | transcript 2026-08-01
A-001 | Assumption | Source data is deduplicated | PMO | Open | 2026-08-22 | Build gate | SOW section 7.2
I-002 | Issue | Sandbox refresh wiped test data | SA | Mitigating | 2026-08-12 | none | standup 2026-08-06
D-003 | Dependency | Client to deliver ERP field map | B. Chen | Open | 2026-08-18 | Design gate | requirements session 2026-08-05
"""

DECISION_LOG = """# Decision log: Acme CPQ

DEC-001 | Approvals use standard Advanced Approvals | 2026-07-30 | K. Malhotra | Custom flow adds 60 h for no gain | kickoff transcript | Standing
DEC-002 | Phase 2 excludes usage-based billing | 2026-08-05 | K. Malhotra | Not in Q-000043 baseline | requirements session | Standing
"""

PASSING_REPORT = """# Acme : CPQ Foundation : weekly status

Period: 2026-08-04 to 2026-08-08
Issued: 2026-08-08 | Prepared from: 3 transcripts, RAID log, decision log, timesheet export
Previous status: status-2026-08-01.md | SOW baseline: SOW-2026-014

## Flags

No flags this period.

## Outcomes this period

- Requirements Document co-signed 2026-08-06 (gate met; DEC-002 recorded the UBB exclusion).

## Plan position

Current phase: Analyze. Next gate: Solution Design co-sign (2026-08-29).

## RAID movement

Risks: 1 open (R-001). Issues: 1 mitigating (I-002). Dependencies: 1 open (D-003). Assumptions: 1 open (A-001).

## Decisions

DEC-001 stands. DEC-002 made 2026-08-05 by K. Malhotra.

## Scope drift

### Candidate: second ERP integration (NetSuite)

- Trigger class: hard
- The ask: "we will also need this flowing into NetSuite" (B. Chen, 2026-08-05, requirements session)
- Baseline position: SOW section 2.3 names a single integration (Workday)
- Evidence: requirements session transcript 2026-08-05, 00:41:12
- Routed to: Program Lead, CSE
- Status: raised

## Hours and burn

Burn: 118 h this period, 642 h to date of 960 h estimated (66.9%).
Source: timesheet export 2026-08-08 (Q-000043 baseline).

## Upcoming period

Solution design sessions 2026-08-11 and 2026-08-13.

## Artifact and gate register delta

Requirements Document v1.0 delivered and co-signed 2026-08-06.
"""

NONE_OBSERVED_REPORT = PASSING_REPORT.replace(
    """### Candidate: second ERP integration (NetSuite)

- Trigger class: hard
- The ask: "we will also need this flowing into NetSuite" (B. Chen, 2026-08-05, requirements session)
- Baseline position: SOW section 2.3 names a single integration (Workday)
- Evidence: requirements session transcript 2026-08-05, 00:41:12
- Routed to: Program Lead, CSE
- Status: raised""",
    "None observed. Compared 3 transcripts against SOW sections 2.1 to 2.4 "
    "and Exhibit A (6 footprint lines).")


def run_case(name, report, expect_pass, expect_substr=None):
    failures, _counts = status_check.check(report, RAID_LOG, DECISION_LOG)
    ok = (not failures) if expect_pass else bool(failures)
    if ok and expect_substr and not expect_pass:
        ok = any(expect_substr in f for f in failures)
    verdict = "ok" if ok else "SELFTEST FAIL"
    print(f"  {verdict}: {name} "
          f"(expected {'pass' if expect_pass else 'fail'}, "
          f"got {len(failures)} failures)")
    if not ok:
        for f in failures:
            print(f"      {f}")
    return ok


def main():
    print("status_check selftest")
    results = []

    results.append(run_case("passing report with candidate",
                            PASSING_REPORT, True))
    results.append(run_case("passing report with none observed",
                            NONE_OBSERVED_REPORT, True))
    results.append(run_case(
        "missing period line",
        PASSING_REPORT.replace("Period: 2026-08-04 to 2026-08-08", ""),
        False, "period:"))
    results.append(run_case(
        "unknown RAID id",
        PASSING_REPORT.replace("R-001", "R-099"),
        False, "R-099"))
    results.append(run_case(
        "unknown decision id",
        PASSING_REPORT.replace("DEC-002 made", "DEC-044 made"),
        False, "DEC-044"))
    results.append(run_case(
        "scope-drift section missing",
        "\n".join(l for l in PASSING_REPORT.splitlines()
                  if "Scope drift" not in l).replace(
                      "### Candidate", "### Removed"),
        False, "scope-drift"))
    results.append(run_case(
        "candidate without evidence",
        PASSING_REPORT.replace(
            "- Evidence: requirements session transcript 2026-08-05, 00:41:12\n", ""),
        False, "no Evidence"))
    results.append(run_case(
        "drift section neither none-observed nor candidates",
        PASSING_REPORT.replace(
            "### Candidate: second ERP integration (NetSuite)",
            "Some vague prose about scope.").replace("- Evidence:", "- Note:"),
        False, "neither"))
    results.append(run_case(
        "unfilled placeholder",
        PASSING_REPORT.replace("118 h", "{{BURN_HOURS}}"),
        False, "placeholder"))
    results.append(run_case(
        "burn without source",
        PASSING_REPORT.replace(
            "Source: timesheet export 2026-08-08 (Q-000043 baseline).", ""),
        False, "burn:"))
    results.append(run_case(
        "burn with named gap passes",
        PASSING_REPORT.replace(
            "Source: timesheet export 2026-08-08 (Q-000043 baseline).",
            "Named gap: burn unavailable; no timesheet export provided. "
            "Owner: Program Lead."),
        True))

    passed = sum(results)
    print(f"selftest: {passed}/{len(results)} cases behaved as expected")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
