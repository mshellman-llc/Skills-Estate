---
name: cutover-closeout
description: 'Run stage 06 Deploy and Closeout after an approved go or no-go: build the cutover runbook, track Go-Live Acceptance against the executed SOW, manage hypercare triage, prepare transition records, and capture outcomes and reusable assets. Use for cutover, go-live, runbooks, hypercare, deemed acceptance, closeout, support transition, or lessons learned. Route UAT to estate-uat-validation, ongoing status and changes to delivery-status, managed operations to their service owner, and contract authoring to sow.'
---

<!-- ESTATE-WRITING:BEGIN -->
Before writing, read the [writing standard](references/estate/writing.md). Apply it to every authored sentence. Review instructions and internal records too. Audience labels and file formats do not exempt prose from review.
<!-- ESTATE-WRITING:END -->


# Estate cutover and closeout

> **Before writing: [`build-card.md`](../_shared/build-card.md) plus
> [`readout-brief.md`](../prose-pass/references/registers/readout-brief.md).**

This skill brings an approved release into production and closes the engagement
on the record. Humans approve acceptance, rollback, and closeout. The skill
assembles the evidence, computes contractual dates, tracks the work, and drafts
the records.

## Source authority

Read `engagement.front_door`, `engagement.contract_commitments`,
`engagement.delivery_status`, `engagement.test_acceptance`, and
`deliverables.register`. The executed SOW owns scope, acceptance terms, fees,
and dates. The signed readiness pack owns the release decision. Timesheets own
actual effort. Record a missing load-bearing fact as a gap with an owner, due
date, and blocked gate.

Run `evidence-core` before drafting. Use `prose-pass` for every prose artifact
and `brand-renderer` for a client-facing render. This skill records commercial
impact but never creates rates, hours, fees, or a change price.

## Workflow

### Cutover runbook

Build the executable plan from `references/runbook-format.md` and
`assets/cutover-runbook-template.md`. Name owners, timing, prerequisites,
verification, rollback triggers, communications, and evidence locations. Every
step must be observable. A rollback decision remains human-owned.

### Go-Live Acceptance

Read the exact executed-SOW clause. Compute its deadline from the actual go-live
date and the contract's business-day rules. Track delivery, client response,
exceptions, and deemed-acceptance status with
`references/acceptance-tracker-spec.md`. Never infer acceptance from silence
before the contractual clock expires.

### Hypercare

Classify each item with `references/hypercare-spec.md`. A defect inside the
accepted scope follows hypercare. A request that changes scope becomes a
change-order candidate for `delivery-status`. Keep severity, owner, evidence,
resolution, and verification. Only the authorized client owner closes a client
acceptance issue.

### Closeout and transition

Use `assets/hypercare-closeout-template.md`. Record delivered artifacts,
acceptance state, unresolved items, support ownership, access changes, final
communications, and transition evidence. Update `engagement.test_acceptance`,
`engagement.outcomes_closeout`, and `deliverables.register` with confirmed
states.

### Harvest

Use `references/harvest-spec.md` to capture measured outcomes, lessons, reusable
assets, comparable-engagement facts, referenceability, and follow-on needs.
Proposed reusable material retains its client restrictions until an authorized
owner approves promotion. Route a qualified follow-on need to
`engagement.expansion` or a new opportunity.

## Gate

Validate every runbook, acceptance tracker, and closeout record:

```bash
python3 scripts/closeout_gate.py artifact.json
```

Exit 0 passes. Exit 1 reports content defects. Exit 2 reports invocation or
parse failure. Correct the source record and regenerate the artifact.

Before delivery, run the applicable prose, brand, and quality gates from
[`release-gate.md`](../_shared/release-gate.md). Return their receipts with the
artifact.

## Failure behavior

- Missing go or no-go approval blocks production cutover planning.
- Missing SOW acceptance language blocks the contractual deadline calculation.
- An unverified hypercare fix remains open.
- An unpriced scope change routes to `delivery-status` and the commercial owner.
- A headless run may prepare artifacts and findings. It cannot record human
  acceptance, rollback approval, closeout approval, or asset promotion.
- Read-only Hub access returns exact patches and `patch-returned`.

## Durable result

Return the artifact or a run record following
[`output-contract.md`](../_shared/output-contract.md). Include the Hub identity,
sources, gate counts, computed deadline, open items, persistence state, and named
human actions. Closeout gives `deliverables.register` its final engagement state.

## Files

- `references/runbook-format.md`: runbook fields and execution rules.
- `references/acceptance-tracker-spec.md`: contractual acceptance calculation.
- `references/hypercare-spec.md`: defect and change boundary.
- `references/harvest-spec.md`: harvest record requirements.
- `assets/cutover-runbook-template.md`: working runbook template.
- `assets/hypercare-closeout-template.md`: closeout template.
- `scripts/closeout_gate.py`: deterministic artifact gate.
- `scripts/closeout_gate_selftest.py`: expected pass and failure cases.
