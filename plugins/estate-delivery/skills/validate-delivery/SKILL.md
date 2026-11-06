---
name: validate-delivery
description: 'Run delivery validation: test scripts traced to the requirements workbook, the defect log and triage, the UAT tracker with coverage, the cutover readiness checklist and the go/no-go evidence pack. Use when testing starts or someone asks for test scripts, a traceability matrix, test coverage, "are we ready for UAT" or "can we go live". Not for writing requirements (capture-requirements), executing cutover or hypercare (manage-cutover-closeout) or weekly status (track-delivery).'
---


# Validate delivery

Stage 05 of the delivery lifecycle: prove the build against the requirements the client
co-signed, and put complete evidence in front of the humans who decide go or no-go.

The identity of this skill is traceability. Every requirement in the workbook has at least
one test script or is a named gap with an owner; every test script traces to requirement IDs
or is flagged as an orphan; every count in the go/no-go pack recomputes from the files. A
requirement nobody tested is invisible until go-live, which is the most expensive place to
find it. `scripts/trace_check.py` enforces all three invariants and exits nonzero when any
breaks; a prose checklist can be skipped, the gate cannot.

The second identity is the draft/decide boundary. This skill prepares and tracks. Humans
execute UAT, triage defects, sign off scripts, and make the go/no-go call. The skill never
marks a gate met, never waives a failed script, never closes a defect without verified
retest evidence, and ships the decision block of the pack empty.

## Project context required

Use only the caller-confirmed engagement, source records, private output location,
and intended audience. Map reference roles such as Program Lead, CSE, Solution Lead,
and Pursuit Lead to that project's authorized owners; these labels do not impose
an employer organization chart or signing authority. The executed agreement and
accepted project plan determine gates, commercial rules, and support obligations.
Keep account history, risk assessments, credentials, and client evidence outside
portable skill sources. A cached account, attached Project, or available connector
is not authorization to read, write, or publish.

## Governors

- **evidence-core** owns provenance. Run it before assembling the go/no-go pack:
  every fact in the pack (a pass, a defect state, an acceptance criterion status) traces to
  a source with a date. Test results are evidence only when they carry an executor and a
  date. If a load-bearing input (requirements workbook, Test Plan, SOW acceptance section)
  is missing or insufficient, produce a readiness-gap memo naming what is missing and stop;
  a go/no-go pack built on an unsourced requirement set is a hard fail.
- **brand-renderer** owns brand for any client-facing render of these artifacts.
  Never inline hex values here.
- **review-writing** owns writing review; a confirmed profile supplies voice. Run its checker on every prose deliverable, including the pack.
- **The SOW owns acceptance.** UAT gates, acceptance criteria, and deemed-acceptance
  language live in the SOW and the co-signed Test Plan. Cite them by section, quote
  criteria verbatim where the pack must state them, never restate contractual clauses in
  your own words. Money and timeline figures come from the quote or SOW; this skill renders
  them, never authors them.

If a governor is not installed on the current surface, state the check it would have run,
do the best manual substitute, and say that is what you did. Never silently skip.

## Phase 0: orient

Find the real objects before writing anything:

1. **The requirements workbook** from capture-requirements: the Excel delivery
   matrix with epics and requirements, Gherkin acceptance criteria, MoSCoW priorities, and
   prefix-numbered requirement IDs (for example `CPE-001`). Those IDs, verbatim, are the
   traceability keys for everything downstream. If no workbook exists, requirements capture
   has not finished; route there and stop rather than testing against memory.
2. **The Test Plan** from Design: severity definitions, test data approach, environments,
   entry and exit criteria.
3. **The SOW**: the acceptance mechanism and UAT gate language, by section number.
4. **Build status**: which requirements are actually built in the sandbox. Testing what is
   not built produces noise dressed as findings.

Stamp every artifact you generate with its sources and as-of dates. Workbook versions
change and sandboxes refresh; an unstamped tracker is stale the moment it is written. Truth
hierarchy: the live workbook beats any prior extract, which beats memory, which beats chat.

## Phase 1: test scripts, traced

Read `references/test-script-format.md` before writing the first script.

Convert Gherkin acceptance criteria to test steps mechanically wherever the AC allows:
Given becomes preconditions, When becomes action steps, Then becomes expected results,
Scenario Outlines become data-driven scripts. Mechanical is the goal because a step lifted
from a co-signed AC inherits its authority; label anything you had to infer, and route
missing AC back through capture-requirements as an open question rather than
quietly repairing the requirement inside a test script.

Coverage rules: every requirement gets at least one script; Must Haves get a UAT script
executed by the client persona; a requirement that cannot be scripted yet goes on the named
gap list with owner, reason, and resolve-by. A script tracing to nothing is scope drift:
flag it in its Orphan Flag field and route it to track-delivery so the drift
surfaces in status, not in a test asset.

Then run the gate:

```bash
python3 scripts/trace_check.py --requirements reqs.csv --scripts tracker.csv --gaps gaps.csv
```

Fix failures at the source files and rerun. Do not proceed to execution tracking with a
failing gate; the failures are exactly the coverage holes UAT exists to prevent.

## Phase 2: defect log and triage

Read `references/defect-log-spec.md`. Stand the log up before the first execution session
so defects land in it from minute one, not in chat.

The non-negotiables: stable `DEF-###` IDs that never get reused; severity per the Test
Plan's definitions (fall back to the reference table only when the Test Plan is silent, and
say so); a source on every defect (who reported, which script and step, which environment,
when); a triage decision distinct from severity; and closure only on verified retest
evidence recorded in the log. "Dev says it's fixed" moves a defect to Retest, never to
Closed. Sev 1 and 2 defects also route to the RAID log as issues via
track-delivery.

## Phase 3: UAT tracker and coverage

Read `references/uat-tracker-spec.md`. One row per script, statuses set only from reported
execution with an executor and date. Requirement status derives worst-wins from its
scripts; never hand-set it.

Report two numbers, always both: execution progress (terminal scripts over total) and
requirement pass rate (requirements fully passed over total), each cut by MoSCoW priority.
Report counts as "n of m (percent)". Refresh daily during UAT and hand the movement summary
to track-delivery; the tracker is the source, status quotes it.

## Phase 4: cutover readiness and the go/no-go pack

Read `references/go-no-go-pack.md` before assembling. The pack's nine sections are always
present; a section you cannot fill is a known unknown with an owner, never an omission.

The core discipline:

- Coverage counts come from the gate, not from hand-tallying. Write the counts into a JSON
  file as they will appear in the pack and verify them:

```bash
python3 scripts/trace_check.py --requirements reqs.csv --scripts tracker.csv \
  --gaps gaps.csv --gonogo pack-counts.json
```

- Every open and deferred defect appears, by severity, with owner and triage decision.
- Every acceptance criterion from the SOW and Test Plan gets a Met / Not met / Cannot
  assess status with an evidence pointer, cited by document and section.
- The cutover readiness checklist carries per-item status and owner; executing it belongs
  to manage-cutover-closeout, which inherits it along with the open defect list.
- Framing is neutral: counts before adjectives, no inflation, no minimizing. The
  recommendation appears once, in the final section, followed by the honest case for the
  other answer. The signature block ships empty.

Present evidence as if you did not know which way the decision should go. Implying "go" by
framing is a named failure mode of this stage.

When the humans co-sign the go/no-go, update the engagement's DELIVERY-STATE.md in the same
session (`go_no_go` with date, pack path, append-only dated log line) per
delivery-orchestrator's `references/delivery-state-spec.md`.

## Durable output

Every run leaves a Markdown record per `_shared/output-contract.md`: the
go/no-go pack when the stage completes, or a run record with the gate counts,
the coverage numbers, the named gaps, and the outstanding human decisions when
it does not. The CSV trackers and defect log are secondary artifacts listed in
that record with their paths. Deliver or link the file; never just say it was
written.

## Running unattended

Triage decisions, script sign-offs, and the go/no-go call need humans. On a scheduled or
headless run: refresh the tracker from reported results, recompute coverage, run the gate,
draft the triage sheet, and stop with the findings. Never record an execution result,
triage decision, or approval nobody gave.

## Degradation ladder

When time is short, cut in this order and say what you cut:

1. Per-script narrative polish; keep title, trace, steps, expected results.
2. First-pass yield and trend cuts in the tracker; keep the two core numbers.
3. Individually narrated sev 3 and 4 defects in the pack; keep the full table.

Never cut: the traceability gate, requirement IDs on scripts, defect closure evidence, the
named gap list, or source stamps. Those are what make the pack signable.

## Boundaries

In the delivery chain (SOW, then prepare-delivery-handoff, then kickoff, then status, then
UAT, then manage-cutover-closeout), this skill's upstream producer is the Build stage
tracked by track-delivery, whose cadence hands over a
sandbox-complete build and the co-signed requirements to prove it against. Its
downstream consumer is manage-cutover-closeout, which inherits the readiness
checklist and the open defect list from the pack. UAT does not accept scope
changes: a script or ask that traces to no requirement is drift, flagged and
routed to track-delivery, never absorbed into the test assets.

- Does not author requirements or acceptance criteria; that is capture-requirements.
- Does not execute cutover, go-live, or hypercare; that is manage-cutover-closeout, which
  inherits the readiness checklist and open defect list from the pack.
- Does not run status cadence or own the RAID log; that is track-delivery. This
  skill feeds it defects and test progress.
- Does not build or fix the system; defects go to owners, not to this skill.
- Does not decide go or no-go, sign off UAT, waive failed scripts, or close unverified
  defects. Humans do all four.

## Files

- `scripts/trace_check.py` · the gate: requirement coverage, orphan flags, go/no-go count
  recompute. Stdlib only, `--selftest` runs embedded fixtures, exits nonzero on failure.
- `scripts/trace_check_selftest.py` · CLI-level selftest with pass and fail fixtures on disk.
- `references/test-script-format.md` · script fields, Gherkin-to-steps mapping, coverage
  and orphan rules, test data approach.
- `references/defect-log-spec.md` · defect fields, severity, lifecycle, triage, closure
  evidence rule.
- `references/uat-tracker-spec.md` · tracker fields, derived requirement status, coverage
  math and reporting rules.
- `references/go-no-go-pack.md` · the nine pack sections, SOW authority rules, cutover
  readiness checklist, neutrality rules.
- `assets/test-script-template.md` · single-script template with the Gherkin-derived layout.
- `assets/uat-tracker-template.csv` · tracker header plus example rows; this file is also
  the `--scripts` input to the gate.
- `assets/defect-log-template.csv` · defect log header plus example rows, including a
  correctly evidenced closure.
- `assets/coverage-gaps-template.csv` · named gap list format the gate reads via `--gaps`.
- `assets/gonogo-counts-example.json` · the count keys the gate recomputes via `--gonogo`.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
