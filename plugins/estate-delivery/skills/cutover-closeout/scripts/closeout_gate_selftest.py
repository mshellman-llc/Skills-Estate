#!/usr/bin/env python3
"""Selftest for closeout_gate.py. Runs the gate against embedded passing and
failing fixtures and verifies the exit codes. Exit 0 if every case behaves,
1 otherwise. Stdlib only."""

import io
import contextlib
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import closeout_gate  # noqa: E402

RUNBOOK_PASS = """# Cutover runbook: Northwind go-live

| # | Step | Owner | Verification | Rollback point |
|---|------|-------|--------------|----------------|
| 1 | Freeze production changes | Program Lead | Change-freeze notice acknowledged in writing by client IT | Lift freeze notice |
| 2 | Deploy package to production | TA | Deployment status Succeeded; post-deploy smoke script green | RB-1: destructive-changes package staged; redeploy prior release |
| 3 | Run data migration final delta | DEV | Row counts reconcile to extract manifest, printed | RB-2: restore from pre-cutover backup taken in step 2 |
| 4 | Enable integration users | SA | Test transaction round-trips in both systems | Disable integration users |
| 5 | Send go-live notice | Program Lead | Notice sent; client sponsor confirms receipt | No rollback: a notice cannot be unsent; correction notice is the remedy |
"""

RUNBOOK_FAIL = """# Cutover runbook

| # | Step | Owner | Verification | Rollback point |
|---|------|-------|--------------|----------------|
| 1 | Deploy package | TA | Deployment status Succeeded | |
| 2 | Migrate data | | Row counts reconcile | RB-1: restore backup |
| 3 | Notify users | Program Lead | TBD | No rollback |
"""

ACCEPT_PASS = """# Go-Live Acceptance tracker: Northwind

- Go-live date: 2026-08-14
- Acceptance period: 10 business days
- SOW clause (verbatim): "Deliverables shall be deemed accepted ten (10)
  business days after go-live unless Client contests in writing." (SOW
  MER-2026-011, section 7.2, executed 2026-05-02)
- Deemed-acceptance deadline: 2026-08-28
"""

ACCEPT_PASS_HOLIDAY = """# Go-Live Acceptance tracker

- Go-live date: 2026-08-28
- Acceptance period: 10 business days
- Holidays observed: 2026-09-07 (Labor Day, per client calendar)
- SOW clause (verbatim): "deemed accepted ten (10) business days after
  go-live unless contested in writing" (SOW section 7.2)
- Deemed-acceptance deadline: 2026-09-14
"""

ACCEPT_FAIL_MATH = ACCEPT_PASS.replace("2026-08-28", "2026-08-24")

ACCEPT_FAIL_NO_CLAUSE = """# Go-Live Acceptance tracker

- Go-live date: 2026-08-14
- Acceptance period: 10 business days
- Deemed-acceptance deadline: 2026-08-28
"""

CLOSEOUT_PASS = """# Hypercare Closeout Report: Northwind

## Hypercare issue log

| ID | Severity | Issue | Disposition |
|----|----------|-------|-------------|
| HC-001 | Sev 2 | Quote PDF missing terms block | Closed: fix deployed 2026-08-19, verified by client AP lead on live quote |
| HC-002 | Sev 4 | Report label typo | Closed: corrected, verified in production 2026-08-20 |
| HC-003 | Sev 3 | New approval path requested | Change-order candidate, routed to delivery-status 2026-08-21 |

## Actuals vs estimate

| Workstream | Estimated hours | Actual hours | Variance | Source |
|------------|-----------------|--------------|----------|--------|
| Configuration | 320 | 355 | +35 | Q-000112 estimate; timesheets export 2026-08-25 |
| Integration | 180 | 240 | +60 | Q-000112 estimate; timesheets export 2026-08-25 |
| Migration | 120 | 118 | -2 | GAP: timesheet coding merged migration into config through week 3; PL to split, owner named, due 2026-08-29 |
"""

CLOSEOUT_FAIL = """# Hypercare Closeout Report

## Hypercare issue log

| ID | Severity | Issue | Disposition |
|----|----------|-------|-------------|
| HC-001 | Sev 2 | Quote PDF missing terms | Closed: redeployed |
| 17 | high | Label typo | Closed: verified in production |

## Actuals vs estimate

| Workstream | Estimated hours | Actual hours | Variance | Source |
|------------|-----------------|--------------|----------|--------|
| Configuration | 320 | 355 | +35 | |
| Integration | 180 | 240 | +60 | GAP |
"""

EMDASH_FAIL = RUNBOOK_PASS.replace("Lift freeze notice",
                                   "Lift freeze notice " + "\u2014" + " easy")

CASES = [
    ("runbook pass", RUNBOOK_PASS, "runbook", 0),
    ("runbook fail (empty rollback, no owner, TBD verify, reasonless no-rollback)",
     RUNBOOK_FAIL, "runbook", 1),
    ("acceptance pass (10 business days over two weekends)", ACCEPT_PASS,
     "acceptance", 0),
    ("acceptance pass (holiday excluded)", ACCEPT_PASS_HOLIDAY, "acceptance", 0),
    ("acceptance fail (deadline does not match computation)", ACCEPT_FAIL_MATH,
     "acceptance", 1),
    ("acceptance fail (SOW clause not quoted)", ACCEPT_FAIL_NO_CLAUSE,
     "acceptance", 1),
    ("closeout pass", CLOSEOUT_PASS, "closeout", 0),
    ("closeout fail (bad ID, bad severity, unverified close, empty source, "
     "reasonless GAP)", CLOSEOUT_FAIL, "closeout", 1),
    ("em dash anywhere fails", EMDASH_FAIL, "runbook", 1),
    ("auto-detect acceptance", ACCEPT_PASS, "auto", 0),
    ("auto-detect closeout", CLOSEOUT_PASS, "auto", 0),
    ("auto-detect runbook", RUNBOOK_PASS, "auto", 0),
]


def main():
    failures = 0
    for name, text, kind, expected in CASES:
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False,
                                         encoding="utf-8") as fh:
            fh.write(text)
            path = fh.name
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                rc = closeout_gate.main([path, "--type", kind])
        finally:
            os.unlink(path)
        ok = rc == expected
        print(f"{'PASS' if ok else 'FAIL'}: {name} (exit {rc}, expected {expected})")
        if not ok:
            failures += 1
            print(buf.getvalue())
    print(f"selftest: {len(CASES) - failures}/{len(CASES)} cases behaved as expected")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
