---
name: delivery-status
description: 'Continuous delivery documentation for Aleysian engagements: the weekly client status report, stewardship of the RAID and decision logs with stable IDs, and scope-drift detection against the SOW baseline that raises change-order candidates with an evidence trail. Use for a weekly or project status report, delivery update, what moved this week, logging a decision or risk from a meeting, updating the RAID log, or checking did we agree to that in scope. Do NOT use for authoring change orders or SOWs (sow-quality, sow), kickoff or charter (aleysian-delivery-kickoff), UAT tracking (aleysian-uat-validation), pricing (the Aleysian Pricing System), or sales pursuits (call-prep).'
---

# Aleysian delivery status

> **Before writing: [`build-card.md`](../_shared/build-card.md) plus
> [`readout-brief.md`](../prose-pass/references/registers/readout-brief.md). Inputs, not a final pass.**

Keep the engagement record honest, week after week. Three jobs, always together: issue the status report from the record, steward the RAID and decision logs so nothing is re-litigated, and compare observed work against the SOW scope baseline so drift is flagged with evidence before it eats margin. Undocumented decisions cause the same conversation twice; unflagged drift becomes a change order handled reactively or, worse, absorbed silently.

This skill is invoked per cadence by a human. No eventing exists, so never assume you ran last week. Every run states exactly what period it covers and reconciles against the previous status file on disk, not against memory of a prior session.

## Inputs at a glance

| Input | Role | If missing |
|-------|------|------------|
| Meeting transcripts for the period | Evidence for log entries, drift, and quotes | Named gap in the report; ask the user what happened |
| RAID log and decision log | The record this skill stewards | Stop; offer to seed per `references/log-stewardship.md` |
| SOW scope baseline (scope body + Exhibit A) | The drift comparison target | Drift degrades to "no baseline on file", flagged |
| Previous status file | Reconciliation baseline | State this is the first status |
| Timesheet export or quote (Q-number) | The only legitimate burn source | Burn becomes a named gap, never an estimate |
| The user | Owner assignments, off-transcript events, decisions | Entries stay proposed, not written |

## Governance this skill delegates

- **evidence-core** owns provenance. Every log entry and every status claim carries a named source with a date. An absent fact is a named gap with an owner and a resolve-by date, never a blank or a plausible fill.
- **prose-pass** owns voice. Run its checker on the finished status report. No em dashes, sentence-case headings, counts not adjectives.
- **brand-renderer** owns brand if the status ships as anything beyond markdown. The markdown report itself needs no brand pass.
- **The money rule.** Burn, remaining hours, and fee figures come from a timesheet export, the quote (Q-number), or an explicit user-supplied source. If no source is available this period, the figure is a named gap ("burn unavailable: no timesheet export provided, owner: Program Lead"). Never estimate burn silently. Never compute remaining from memory of last week's number.

Portability fallback: if a governor is not installed on the current surface, state the check it would have run, do the best manual substitute, and say that is what you did. Never silently skip.

## Phase 0: orient and pin the period

Pin all five before writing anything:

1. **The engagement.** Client, engagement name, SOW identifier. From the kickoff record or the user.
2. **The period.** Explicit start and end dates. Ask if ambiguous. The report header carries `Period: YYYY-MM-DD to YYYY-MM-DD`; the gate fails without it.
3. **The previous status file.** Find it in the engagement folder and read it. Open items, RAID counts, and last-reported burn come from that file. If none exists, say this is the first status of the engagement and that there is no prior baseline to reconcile against.
4. **The governance logs.** The RAID log and decision log seeded at kickoff by `aleysian-delivery-kickoff`, using the stable ID convention in `references/log-stewardship.md` (R-001, A-001, I-001, D-001 for RAID, where D is a dependency; DEC-001 for decisions). If the logs do not exist, stop and offer to seed them per that reference before producing any status.
5. **The SOW scope baseline.** The signed SOW's scope section and its Exhibit A Basis of Estimate where one exists. Without a baseline, scope-drift detection degrades to "no baseline on file" as a named gap, flagged in the report, not skipped.

## Phase 1: harvest the period's evidence

Read the meeting transcripts for the period verbatim, never summaries. A summary says "the client raised integration concerns"; the transcript says who asked for a second ERP integration and in which sentence. Pull direct quotes and attribute them by speaker and date; quotes are what make a drift flag or a decision entry defensible when it is challenged.

Also gather: the timesheet or burn source for the period, any artifact or gate movement (documents delivered, sign-offs obtained), and anything the user says happened off-transcript (record it as user-reported, with the user as the source).

Where transcripts live in Granola, Drive, or Slack, read what is actually there through the available integrations. Never substitute a similarly titled meeting for the one that was named.

## Phase 2: steward the logs

Rules in full in `references/log-stewardship.md`. The short version:

- **Append-only.** New entries get the next sequential ID. Existing entries are never renumbered, deleted, or rewritten; a correction is a new dated status line on the entry.
- **Every entry sourced.** Transcript quote with speaker and date, SOW clause, or a named person's statement. An unsourced item is proposed to the user, not written.
- **Every entry owned and dated.** Owner, status, resolve-by date, and the gate it blocks where applicable. Unowned actions evaporate.
- **Closure needs a sourced basis.** Never close a risk or mark a decision superseded because it stopped being mentioned. No source, stays open.
- Extract from each transcript: decisions made, new risks, new issues, new dependencies, assumptions stated as fact, and action items. Propose the batch to the user before appending when running interactively.

## Phase 3: detect scope drift

Protocol and evidence-trail format in `references/scope-drift-protocol.md`. The posture:

Compare every observed work item and client ask from the period against the SOW scope baseline. Classify using the Basis of Estimate trigger taxonomy owned by `sow-quality` (read its `references/basis-of-estimate.md` when classifying): **soft triggers** are volumetric, footprint materially exceeding Exhibit A; **hard triggers** are binary workstream additions such as a second integration or org, which trigger regardless of size.

When drift is found, raise a **change-order CANDIDATE**: the ask quoted verbatim with attribution, the baseline clause it exceeds cited by section, the trigger class, and the routing (Program Lead and CSE). That is the whole move. This skill never decides in-scope versus out-of-scope (a human call), never silently absorbs the work into status as if it were baseline, and never authors the change order itself; authoring runs through the `sow-quality` Basis of Estimate framework and humans.

A period with no drift still gets a scope-drift section reading "None observed" with a one-line statement of what was compared. The gate requires the section either way; silence is not evidence of a check.

## Phase 4: write the status report

Fill `assets/weekly-status-template.md`. Section spec, ordering rules, and worked line examples in `references/status-report-spec.md`. The rules that carry it:

- **Outcome-first.** Lead with what the client can now do or decide, not with activity. "UAT entry criteria met" beats "the team worked on testing".
- **Counts, not adjectives.** "3 risks open, 1 new, 1 closed" rather than "good progress on risks". Every RAID and decision reference in the report uses its stable ID so the reader can find it in the log.
- **Red flags never buried.** Anything red or newly slipped goes in the flags section at the top of the report, stated plainly with its ID. A banner over a stale document body is not resolution: if a flag is cleared, the body lines that referenced it change too.
- **Every line about scope, hours, or dates carries a source.** Transcript, SOW clause, timesheet export, log entry ID, or a named gap.
- **Reconcile against the previous status.** Items reported open last period are either moved with a sourced basis or restated as still open. An item that vanishes between reports without explanation is the failure mode.

## Phase 5: gate before issuing

```bash
python3 scripts/status_check.py STATUS.md --raid-log RAID.md --decision-log DECISIONS.md
```

The gate is blocking. It verifies: the period is stated in the header; every stable ID referenced in the report exists in the corresponding log file; the scope-drift section is present and is either "None observed" or candidates each carrying at least one evidence citation; the hours-and-burn section names a source or a named gap; and no unfilled placeholders remain. Exit 0 passes; nonzero blocks issue. Report the counts it prints, not an adjective, and write a one-line disposition.

Then run the prose gate from `prose-pass` on the report (or the manual substitute, stated).

## Worked example, end to end

Input: a requirements-session transcript in which the client asks for a NetSuite integration; the SOW names a single integration (Workday). Correct output across the three jobs:

1. **Logs**: a dependency entry (D-0NN, client to confirm whether NetSuite is a requirement or a wish, owner and resolve-by date) and, if a human decided anything in the room, a decision entry. No decision entry for the ask itself; nobody decided anything yet.
2. **Drift**: a candidate block in the scope-drift section. Trigger class hard, the ask quoted verbatim with speaker and date, the SOW integration clause cited by section and quoted, at least one evidence line, routed to Program Lead and CSE.
3. **Status**: the candidate appears in the flags section as well as the scope-drift section, because it needs a decision. It reappears every period until a decision lands and gets a D-0NN.

The wrong outputs, for contrast: logging it as an action item for the team (silent absorption), deciding it is out of scope in the report (a human call), or drafting the change order (that is the `sow-quality` framework plus humans).

## State discipline

- Record IDs and quote totals are not durable anchors across sandbox refreshes. Stamp the report with its source objects and as-of dates: the SOW identifier and signed date, the timesheet export date, the transcript dates, the previous status filename.
- Truth hierarchy when sources disagree: signed SOW and its exhibits > governance logs > previous status file > chat context > memory. A conflict between them is flagged in the report, never silently resolved; show both and say which the report uses and why.
- Never hand-patch an issued report. Fix the log or the source, regenerate, and reissue with a new issue date; otherwise the next cadence run resurrects the error.

## Running unattended

Phases 2 and 3 normally propose before appending. On a scheduled or headless run: append log entries with a clearly marked `proposed` status, produce the report, run the gate, and state in the flags section that the proposed entries and any drift candidates await human review. Never record a decision nobody made, never close a RAID item unattended, and never issue the report to the client without a human in the loop; leave it as a draft for the Program Lead.

## Phase 6: land it

If any lifecycle gate moved this period, verify the engagement's DELIVERY-STATE.md reflects it (status, date, append-only log line) per delivery-suite's `references/delivery-state-spec.md`; a stale state file is a flag in the report.

Deliver the report, and commit the report plus the updated logs to the engagement folder so the next cadence run can find them; the previous-status reconciliation in Phase 0 depends on this. Name the report with the period end date (`status-2026-08-08.md`) so ordering is unambiguous. Close with the user on: the flags, any change-order candidates raised, and the biggest judgment call of the period argued from both sides.

Status reports are issued, not signed. Drift flags are proposals for a human decision.

## Durable output

The status report is the run's durable Markdown record and follows `_shared/output-contract.md`: the period, the sources used, the counts, the flags, and the change-order candidates all live in the file, named by period end date and committed to the engagement folder. A run that stops before issuing still leaves a record of what was checked and what blocked it. Deliver or link the file; never just say it was written.

## When time is short

Cut in this order, and say what you cut: (1) the narrative accomplishments detail, keep the outcome bullets; (2) upcoming-period detail beyond the next gate; (3) artifact-register updates beyond what moved. Never cut: the period header, log stewardship for decisions and new risks, the scope-drift section, sourcing, or the gate.

## Boundaries

In the delivery chain (SOW, then s2d-handoff, then kickoff, then status, then UAT, then cutover-closeout), this skill's upstream producer is aleysian-delivery-kickoff, which seeds the logs it stewards, and its downstream consumer is aleysian-uat-validation, which feeds it defects and test progress once Validate starts. Status does not re-plan: the plan, the baseline, and the gates stay where they were signed, and what this skill produces is the honest record of movement against them.

- Does not author change orders or scope language. Candidates route to the `sow-quality` Basis of Estimate framework and humans.
- Does not run kickoff, seed the charter, or create the governance logs from scratch on its own initiative. That is `aleysian-delivery-kickoff`; this skill stewards what kickoff seeded.
- Does not track UAT execution or defects. That is `aleysian-uat-validation`.
- Does not price, estimate hours, or compute burn from anything but a named source. The Pricing System and timesheets own the numbers.
- Does not produce client-facing proposals or sales artifacts.

## Files

- `references/status-report-spec.md` : section-by-section spec for the weekly status, with worked line examples.
- `references/log-stewardship.md` : RAID and decision log rules, the stable ID convention, entry and closure formats.
- `references/scope-drift-protocol.md` : detection protocol, trigger classification, the evidence-trail format for a candidate.
- `assets/weekly-status-template.md` : the report template the model fills. Placeholders are `{{LIKE_THIS}}`; the gate fails on any that survive.
- `scripts/status_check.py` : the deterministic gate. Stdlib only.
- `scripts/status_check_selftest.py` : passing and failing fixtures; run it after any change to the gate.

## Release gate (required)

Before you deliver, run the gate. This is a required step, not a suggestion, and
not something a reviewer does later. Full spec in
[`release-gate.md`](../_shared/release-gate.md).

1. Run prose-pass on the prose. It rewrites AI patterns and gates the result. For
   a final artifact it emits a receipt the quality gate requires.
2. Run brand-renderer on the branded artifact: palette, borders, radii, logo,
   footer.
3. Run quality-gate before you call it final.

Do not present the artifact as finished until every check that applies has passed.
