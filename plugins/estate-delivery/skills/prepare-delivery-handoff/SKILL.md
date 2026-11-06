---
name: prepare-delivery-handoff
description: 'Owns the Estate sales-to-delivery handoff at signature: the handoff package built from the executed SOW, quote, and deal record, and the incoming delivery handoff brief accepted before kickoff. Use when a deal signs and someone asks for the handoff package, the delivery handoff brief, the warm transfer, what delivery inherits, or what was promised on a signed deal. Do NOT use for technical deliverability judgment (assess-solution-delivery), the kickoff meeting or project charter (start-delivery), requirements extraction (capture-requirements), or pre-sale research and call prep (prepare-sales-pursuit).'
---


# Prepare delivery handoff

> **Before writing: [`build-card.md`](_shared/build-card.md) plus
> [Writing Integrity review](_runtime/review-writing/references/detailed-review.md). Inputs, not a final pass.**

A signed deal crosses from the people who sold it to the people who deliver it, and
most of what the seller knows is about to walk out of the room. This skill captures
it in one artifact family with one schema, produced at two moments:

- **Moment 1, at signature: the handoff package.** Assembled from the executed SOW,
  the quote, and the deal record. What was sold, what was decided and why, who was in
  the room, what was promised, what is still open. The SSL walks it to the delivery
  team in a recorded warm-transfer session.
- **Moment 2, at delivery acceptance: the handoff brief.** The incoming team's
  orientation document. Same sections, now completed with the readiness view, the
  week-one discovery agenda, and the definition of done. Delivery accepting this
  brief is the gate into Mobilize.

Both moments share the 12-section catalog and one manifest schema. Earlier drafts
split this across a sell-side agent and a delivery-side agent with two divergent
schemas and no defined mapping between them; facts died at the seam. That defect is
why this is one skill. The package is the brief at an earlier state of completion,
never a different document.

## Project context required

Use only the caller-confirmed engagement, source records, private output location,
and intended audience. Map reference roles such as Program Lead, CSE, Solution Lead,
and Pursuit Lead to that project's authorized owners; these labels do not impose
an employer organization chart or signing authority. The executed agreement and
accepted project plan determine gates, commercial rules, and support obligations.
Keep account history, risk assessments, credentials, and client evidence outside
portable skill sources. A cached account, attached Project, or available connector
is not authorization to read, write, or publish.

## Governance, delegated

- **evidence-core runs first.** Every load-bearing claim enters the ledger
  with source, confidence, and as-of date before any section is written. If a
  required domain is Insufficient, produce the handoff readiness gap memo and stop;
  a full handoff after an Insufficient gate is a hard fail. The artifact contract is
  `sales_to_delivery_handoff` in evidence-core's `reference/artifact-registry.json`.
- **brand-renderer owns the rendered surface.** No inlined hex, no
  duplicated palette. Brand applies during the build.
- **Writing-integrity owns writing review.** Run its bundled diagnostics on the rendered prose. No em
  dashes, sentence-case headings, no AI-tell constructions.
- **The money rule.** Contract figures come from the executed SOW and its quote
  (Q-number) only. Never from Slack, never from memory, never from the proposal
  deck, which may predate the final negotiation. This skill renders figures; it
  never authors them.

If a governor is not installed on the current surface, state the check it would
have run, do the best manual substitute, and say that is what you did.

## Source authority, in order

The executed SOW is the most authoritative source; read its scope, exclusions,
deliverables, fee model, dates, and assumptions verbatim. Then, in order: the quote,
Salesforce (account, opportunity, stage history, contact roles), Drive (proposal,
discovery decks, transcripts), Slack and Gmail (late changes, verbal commitments,
access blockers), calendar and call notes. The AE/CSE debrief comes last and narrow:
only the tacit room context no system holds. Mine the systems before interviewing
anyone. Recency can override authority on current state: a recent thread reopening a
settled clause outranks the SOW on where things stand now, and that conflict is
surfaced, never silently resolved. Full connector table, search anchors, and
corroboration rules: `references/source-authority.md`.

## The 12 sections

Full catalog with each section's job and bar: `references/brief-catalog.md`.

| # | Section | # | Section |
|---|---------|---|---------|
| 01 | The engagement | 07 | Sell-cycle promises |
| 02 | What came before | 08 | Risks, assumptions, gaps |
| 03 | Process and current state | 09 | The people |
| 04 | System landscape | 10 | Relevant prior engagements |
| 05 | Solution shape | 11 | Discovery sessions |
| 06 | Decisions inherited | 12 | What good looks like |

Structural rule, inherited from the provenance doctrine: **sections are never
dropped.** Every section is present in every handoff. It is either filled with
sourced facts, or it carries an explicit named gap with an owner, a resolve-by
date, and the gate it blocks. A section that genuinely does not apply (greenfield,
no prior engagement) says so in one sourced line. A blank is a gate failure.

Three sections carry special rules:

- **07 Sell-cycle promises.** Anything said to the client that is not in the
  executed SOW is a flagged liability, sourced to where and when it was said, with
  an owner. Promises confirmed to be in the SOW are listed with the clause. This
  section exists because unwritten promises are the single most common way sales
  gets pulled back into delivery after signature.
- **11 Discovery sessions.** The week-one agenda, built directly from the ledger's
  Unknowns and Inferreds. Every session names an owner, the right attendees, and
  the concrete output that closes the question. Never droppable.
- **12 What good looks like.** The definition of done plus the readiness checklist.
  Every criterion is observable, carries a binary test, and ladders to the one
  outcome stated in section 01. Never droppable.

Specs for 11 and 12, including the readiness checklist items:
`references/week-one-definition-of-done.md`.

## Workflow

1. **Orient.** Find the executed SOW and the Q-number. Confirm the deal is signed;
   this skill does not run pre-signature. Pin the moment: package (signature) or
   brief (delivery acceptance). Stamp the manifest with client, engagement,
   source snapshot, and as-of date.
2. **Run evidence-core.** Harvest in the authority order above. Read transcripts
   verbatim, never summaries. An un-searched source is an Unknown, not a confirmed
   absence. Carry the delivery-lens and maturity-gap flags forward from the pursuit
   so delivery inherits them instead of rediscovering them.
3. **Build the manifest.** JSON, schema in `references/package-spec.md`. Fill the
   12 sections from the ledger: roughly 80 percent of a clean deal assembles
   mechanically from the SOW and quote. Everything the ledger could not source
   becomes a gap entry with owner, resolve-by, and blocked gate. Mark every scope
   item in or out. Log promises with where they were said and whether they are in
   the SOW.
4. **Gate it.**
   ```bash
   python3 scripts/check_handoff.py manifest.json
   ```
   Exit 0 passes, 1 fails, 2 is a usage or parse error. Report the counts it
   prints, never an adjective. The gate is blocking at both moments.
5. **Render.** Project the manifest through brand-renderer as the styled
   HTML or portable Markdown brief. Confidence maps to presentation: Confirmed
   reads as fact, Inferred as inference with its basis, Unknown as a named open
   question, conflicts as flagged divergences with both values shown. Run
   review-writing on the rendered prose. Never hand-patch the render; fix the manifest
   and re-render.
6. **Transfer and land.** Moment 1: support the warm transfer (the SSL walks the
   package to the Program Lead and Solution Lead in a recorded session), then
   ingest that session's transcript to close open questions. Moment 2: delivery
   accepts the brief; record the acceptance. Deliver the file, commit it to the
   client folder, write session memory pointing at the files.
7. **Close the loop.** Top three things delivery inherits, then the landmines.
   Flag the biggest judgment call in the handoff and argue the other side of it.

### Seed DELIVERY-STATE.md at acceptance

When delivery accepts the brief (Moment 2), create `DELIVERY-STATE.md` at the
engagement folder root per delivery-orchestrator's `references/delivery-state-spec.md`:
engagement meta, current stage, all eight gate statuses with `brief_accepted` marked
accepted with the date, artifact locations (including the brief), and the first
append-only dated log line. If the file already exists, update the gate and log
instead of recreating it.

## Durable output

Every run leaves a Markdown record per `_shared/output-contract.md`: the
rendered brief itself when one ships, or a run record carrying the gate
counts, the open gaps with owners, and the outstanding human actions when the
run stops early. Deliver or link the file with the manifest; never just say
it was written.

## Depth tests during authoring

- Name real things: systems, people, numbers, clauses, each with a source. No
  "the platform", no "various stakeholders".
- State the success spine early in 01 and return to it in 12.
- Decisions carry status, owner, and rationale; open ones are visible, not buried.
- Every assumption states what breaks if it is false.
- People postures are sourced, never asserted; deal-versus-delivery stakeholder
  mismatches are explicitly flagged, because a sponsor who vanishes at kickoff is
  a top cause of failed starts.
- Section 11 is built from the Unknowns: every open question maps to a session
  whose output closes it, or names why it waits.

## When time is short

Cut in this order, and say what you cut: 10 (prior engagements, keep a one-line
pointer), 03 (keep the breaks list, drop the full as-is map), 05 (point at the
Solution Brief), depth in 02. Never cut: sourcing, section 07, the gap entries
with owners, sections 11 and 12, or the gate.

## Running unattended

The warm transfer and the acceptance need humans. On a headless run: build the
manifest, run the gate and review with review-writing, and stop with the findings and the open
gaps. Say plainly that the transfer session and acceptance are outstanding. Never
record an acceptance nobody gave.

## Boundaries

This skill is the first delivery link in the chain that runs SOW, then
prepare-delivery-handoff, then kickoff, then status, then UAT, then manage-cutover-closeout. Its
upstream producer is the sales side: the executed SOW and quote arrive as
fixed input. Its downstream consumer is start-delivery, which
turns the accepted brief into the charter and governance pack.

- Does not judge technical deliverability or carry implementation depth. Section
  05 is orientation only; the deep answer is assess-solution-delivery.
- Does not run the kickoff or write the project charter. That is
  start-delivery.
- Does not extract or structure requirements. That is capture-requirements.
- Does not do pursuit research or call prep. That is prepare-sales-pursuit, pre-sale
  only.
- Does not price, staff, commit dates, or reinterpret scope. The quote owns every
  number; the Pursuit Lead and delivery leads own the decisions. It assembles and
  transfers.
- Does not initiate change orders. If delivery intent already differs from the
  SOW, that is a flagged conflict for the Pursuit Lead, not a rewrite.

## Files

- `scripts/check_handoff.py`: the gate. Validates a handoff manifest: all 12
  sections present and either sourced or gapped with owner and resolve-by, 11 and
  12 non-empty, every scope item marked in or out, promises sourced, contract
  figures traced to the SOW or quote, no em dashes. Stdlib only.
- `scripts/s2d_selftest.py`: runs the gate against the shipped fixtures and fails
  loudly on any drift. Run it after any edit to the checker.
- `scripts/fixtures/`: passing and failing manifests the selftest uses.
- `references/brief-catalog.md`: the 12 sections, each with its job and its bar.
- `references/package-spec.md`: the manifest schema, moment semantics, warm
  transfer, and record seeding.
- `references/week-one-definition-of-done.md`: section 11 and 12 specs and the
  readiness checklist.
- `references/source-authority.md`: connector table, search anchors, corroboration
  and conflict rules.

## Release gate (required)

Before you deliver, run the gate. This is a required step, not a suggestion, and
not something a reviewer does later. Full spec in
[`release-gate.md`](_shared/release-gate.md).

1. Apply review-writing to the prose. Use the bundled diagnostic tools to check saved writing. For
   a final artifact it emits a receipt the quality gate requires.
2. Run brand-renderer on the branded artifact: palette, borders, radii, logo,
   footer.
3. Run review-deliverable before you call it final.

Do not present the artifact as finished until every check that applies has passed.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
