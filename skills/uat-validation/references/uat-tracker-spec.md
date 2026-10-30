# UAT execution tracker and coverage math

The tracker answers two questions at any moment: how much of the planned testing has run,
and how much of the requirement set is actually proven. Those are different numbers and the
pack shows both. Execution can be at 95 percent while half the Must Have requirements are
unproven; a tracker that shows only one number hides that.

## Tracker rows

One row per test script (or per example-row of a data-driven script). Fields: Test Script
ID, Title, Requirement IDs, Phase (SIT/UAT), Persona, Status, Executed by, Executed on,
Defect IDs (for failures and blocks), Notes.

Script status values, exactly these: `Not started`, `In progress`, `Passed`, `Failed`,
`Blocked`. Blocked means the script cannot run (environment, data, an upstream defect) and
must name what blocks it, usually a Defect ID. A script blocked by nothing nameable is Not
started, and saying so is more honest than the softer word.

Statuses are set by the person who executed, or recorded by the skill from what they
reported, with executed-by and date filled. Never mark a script Passed on inference or on a
developer's word; a pass with no named executor does not count as a pass.

## Requirement status (derived, never hand-set)

A requirement's status derives from all scripts tracing to it, worst wins:

1. `Failed` if any of its scripts failed
2. else `Blocked` if any are blocked
3. else `In progress` if any are in progress or a mix of passed and not started
4. else `Passed` if every script passed
5. else `Not started`

A requirement with zero scripts has no status; it is a named gap (see the gate) and is
reported as such, never blended into Not started.

## Coverage math

Compute these; the same definitions feed the go/no-go pack, and trace_check.py recomputes
the traceability counts, so derive them from the files rather than by hand.

Let R = total requirements in the workbook, S = total test scripts.

- **Traceability coverage** = requirements with at least one script / R. The gate requires
  this to be 100 percent minus named gaps; anything else is a build error in the test set,
  not a testing result.
- **Named gaps** = requirements with zero scripts, each with owner, reason, resolve-by.
- **Execution progress** = scripts in a terminal state (Passed + Failed) / S. Blocked is not
  terminal; a suite that is 40 percent blocked has not made 40 percent progress.
- **Requirement pass rate** = requirements with derived status Passed / R. This is the
  number the go/no-go decision actually turns on.
- **First-pass yield** (optional, useful for trend): scripts that passed without a defect /
  scripts executed.

Report each as "n of m (percent)", never percent alone. "34 of 41 requirements passed
(83 percent)" survives scrutiny; "83 percent" invites the question it should have answered.

Cut every count by MoSCoW priority (from the workbook) and by phase. A 90 percent pass rate
that conceals two failed Must Haves is the exact failure mode this tracker exists to
prevent.

## Cadence

During UAT, refresh the tracker at least daily and hand the movement summary (scripts
newly passed/failed, new defects, unblocked items) to delivery-status for the
weekly status. The tracker is the source; status reporting quotes it, never re-derives it.
