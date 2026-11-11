# Defect log and triage

The defect log is the single record of everything found broken during SIT and UAT. It feeds
three consumers: the daily triage, the RAID log (via estate-delivery-status), and the open
defect table in the go/no-go pack. One log, stable IDs, no side lists.

## Defect fields

| Field | Rule |
|---|---|
| Defect ID | Stable, never reused, `DEF-###` in capture order. The ID survives dedup: a duplicate is closed pointing at the survivor, not deleted. |
| Title | The observed failure in one sentence, symptom first. "Discount recalculates to zero when quote is cloned", not "Cloning issue". |
| Found by (source) | Who reported it and where: name or role, the Test Script ID and step that surfaced it, the environment, and the date. A defect with no source is a rumor; capture the source or capture it as an open question. |
| Requirement IDs | Inherited from the failing script. This is how the go/no-go pack shows which requirements have open defects against them. |
| Severity | 1 to 4, per the table below. Severity is impact, set at capture and revised only in triage with the change logged. |
| Triage decision | One of: `fix now`, `defer` (to a named release or hypercare), `won't fix`, `duplicate of DEF-###`, `not a defect`. Empty until triage happens. |
| Priority / owner | Assigned at triage. Every open defect has exactly one owner, a role plus a name. |
| Status | Lifecycle below. |
| Fix evidence | Required to close. See closure. |

## Severity

Use the Test Plan's severity definitions when it has them; the SOW or Test Plan definition
always wins over this table. Where none exist, use these and say the Test Plan was silent:

| Sev | Meaning |
|---|---|
| 1 | Blocks testing or a core business process, no workaround. |
| 2 | Major function wrong or unusable; workaround exists but is not acceptable for go-live. |
| 3 | Function impaired with an acceptable workaround, or wrong in an edge case. |
| 4 | Cosmetic, copy, or nuisance. No functional impact. |

Severity describes impact; the triage decision describes the response. Do not encode "we
will not fix this" as severity 4. A severity 2 can be deferred and a severity 4 can be
fixed now; the two fields exist so those calls are visible.

## Lifecycle

`New` -> `Triaged` -> `Assigned` -> `Fixed (dev asserts)` -> `Retest` -> `Closed` or back to
`Assigned`. Deferred and won't-fix defects leave the active lifecycle at Triaged but stay in
the log and stay in the go/no-go pack; deferral is a human decision to present, not a way to
shrink the open count.

## Closure requires verified evidence

Never close a defect on a developer's assertion that it is fixed. Closure requires a passing
retest of the originating script (or the failing steps), executed in the test environment,
recorded in Fix evidence as: who retested, when, in which environment, and the result. This
is a hard rule from the delivery spec: the agent does not close what it cannot verify. If
the fix is asserted but the retest has not run, the status is Retest and the defect is open
for every count that reaches the go/no-go pack.

## Triage cadence

Run triage as a short standing review during test execution (daily during UAT). The skill
prepares the triage sheet: new defects since last triage, proposed severity with basis, and
suspected duplicates. Humans make the triage decision; record who decided and when. Sev 1
and 2 defects also go to the RAID log as issues, with the gate they block, through
estate-delivery-status; do not maintain a parallel risk list inside the defect log.
