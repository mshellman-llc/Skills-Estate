---
name: discovery-brief
description: 'Maintain the discovery record for a pursuit: supported facts and ranked open questions tied to the scope they unblock. Use to prepare discovery content, identify questions that affect scope or price, ingest a post-call transcript, close answered questions, log decisions, or propose scope revisions. Route company research and a packaged call brief to call-prep, scope and pricing changes to scoping-agent, and signed-engagement requirements to requirements-capture.'
---

Run this module's relative commands from the directory containing this WORKFLOW.md. Resolve that directory to an absolute path first. A command that explicitly names another working directory keeps that requirement. This file is a supporting workflow, not another installed skill entrypoint.



# Discovery brief

## Caller context and source boundary

Use only the current task's supplied or explicitly authorized account, project sources and destinations. Resolve record names such as `client.profile` within that confirmed context; they are logical slots, not a default personal store. Connector availability alone does not authorize searching another account. Organization-specific pricing, capability catalogs, approval roles and policies must be supplied or confirmed; absent material context remains an explicit gap. Keep reusable package files immutable during a client task and save client records outside them. Never populate an example with private source material.


> **Before writing: [`build-card.md`](../../_shared/build-card.md) plus
> [`readout-brief.md`](../prose-pass/references/registers/readout-brief.md).**

This skill owns `opportunity.discovery`. It maintains a two-column ledger before
and after each pursuit discovery session. `call-prep` uses that ledger to package
one upcoming call. `scoping-agent` decides whether proposed findings change
scope or price.

## The ledger

Build the ledger before writing a brief. Detailed fields and examples are in
[`ledger-spec.md`](references/ledger-spec.md).

**Column A: supported knowledge.** Each atomic claim carries a source ID, source
date, as-of date, and Confirmed or Inferred status. Confirmed needs authoritative
evidence. Inferred states its basis. A searched-for fact that remains absent
becomes a Column B question.

**Column B: open questions.** Write each question as it should be asked. Record
what was searched, the scope line or capability it unblocks, and its impact:

- High blocks sizing, creates a wide cost range, or gates a phase.
- Medium changes effort inside a workstream that can still be sized.
- Low refines the estimate at the margin.

Ask higher-impact questions first. For equal impact, prioritize the question
that gates other work. Remove questions that cannot change scope, effort, price,
or a delivery decision. An unresolved item carries `do not size until Q-nn` in
the relevant scope row.

## Inspection and persistence state

Record only sources actually inspected. If the input summarizes what “transcript line N says,” cite the supplied summary of line N; do not claim that the transcript itself was searched. A search field can say “supplied summary only; full transcript unavailable.” An excerpt or summary is not a full-transcript search; record its exact available lines and keep the missing source as a retrieval gap. An attributed statement establishes what that speaker said, not independently verified authority for sizing or approval. Narrow a question when the available evidence answers only part of it.

When no write occurred, present an unapplied ledger patch. If a write was attempted but its result or readback is missing, report persistence as unverified or unknown and inspect the destination before retrying; do not call that patch unapplied. Label evidence registration, refresh and validation as proposed actions unless they ran. Preserve supplied human text exactly; if the human block is absent, retain a placeholder for its unchanged contents rather than inventing a note or claiming it was checked.

## Evidence and commercial rules

Run `evidence-core` before building the ledger. Register sources in
`evidence.sources` and claims in `evidence.claims`. Generated artifacts and
worked examples have no evidence authority. A load-bearing Insufficient result
produces a discovery readiness gap memo and stops the full brief.

Every commercial number comes from an approved quote or explicit user-supplied
source. This skill can identify an unsized line. It cannot create hours, rates,
fees, or totals.

## Prepare discovery

1. Resolve the client and opportunity. Confirm the session, attendees, purpose,
   available time, opportunity ID, and quote identifier when one exists.
2. Read `client.front_door`, `client.profile`, `opportunity.front_door`,
   `opportunity.discovery`, and the relevant evidence index.
3. Read authoritative internal sources before asking a person. Include the RFP,
   capability scoring, CRM record, workshop transcripts, client documents, and
   approved commercial records that are available.
4. Build Column A from governed claims. Preserve conflicts.
5. Build and rank Column B from the remaining gaps. Tie every question to a
   named scope line or decision.
6. Validate the ledger before projecting the brief.

Use the section catalog in
[`section-catalog.md`](references/section-catalog.md) for the brief. The ranked
unknowns remain its spine. Add a flex section only when the ledger supports it.

## Ingest the call

Use `transcript-ingestion` to preserve and normalize the raw source when it is
installed. Follow
[`post-call-ingestion.md`](references/post-call-ingestion.md):

1. Resolve the speaker-labeled transcript by stable context identity.
2. Walk each open question. Move a supported answer to Column A; narrow a partial
   answer; retain an unanswered question.
3. Extract new facts and decisions with transcript locations.
4. Send proposed claims through `evidence-core`.
5. Write supported findings to `opportunity.discovery`. Update `client.profile`
   only for durable client facts.
6. Send proposed scope changes to `scoping-agent` for confirmation.
7. Re-rank the remaining questions and refresh the brief.

Never close a question without transcript evidence. Preserve human-authored
blocks between `<!-- human -->` and `<!-- /human -->`. When revising a complete
Pursuit Brief, run call-prep's before-and-after preservation check.

## Validate and release

```bash
python3 scripts/check_brief.py ledger.json
```

The gate checks source tokens, valid ranks, named scope lines, rank order,
unknown placement, and object structure. An empty JSON open-question list passes only when discovery_complete is explicitly true; punctuation alone does not fail this evidence gate. Exit 0 passes. A nonzero result
blocks release.

Apply `writing-integrity` to the brief and `brand-renderer` on any branded surface. Apply
`quality-gate` before final delivery. The shared sequence is in
[`release-gate.md`](../../_shared/release-gate.md).

## Failure behavior

- Unavailable sources remain retrieval gaps; they do not prove absence.
- A question already answered by the record is removed from Column B.
- A priced unresolved item fails the brief.
- A source conflict stays visible until an authorized owner resolves it.
- A headless run may build and gate the ledger. It cannot invent an answer,
  approve scope, or close a client decision.
- Read-only Hub access returns exact patches and `patch-returned`.

## Durable result

Return the ledger, projected brief, or readiness gap memo under
[`output-contract.md`](../../_shared/output-contract.md). Name the client and
opportunity, sources searched, records read, top open questions, gate result,
proposed scope changes, and persistence state.

## Files

- `references/ledger-spec.md`: Column A and B formats.
- `references/section-catalog.md`: brief sections and retrieval targets.
- `references/post-call-ingestion.md`: transcript-to-ledger protocol.
- `scripts/check_brief.py`: Markdown and JSON gate.
- `scripts/check_brief_selftest.py`: passing and failing fixtures.
