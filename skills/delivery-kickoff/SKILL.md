---
name: delivery-kickoff
description: 'Mobilizes an Aleysian delivery engagement: turns an accepted sales-to-delivery handoff brief and a signed SOW into a draft Project Charter (scope, team, RACI, cadence, ready for client signature), a live governance pack (RAID log, decision log, weekly status template with stable IDs), internal and client kickoff decks in the correct waterfall or agile variant, a Sprint 0 plan with a seeded backlog, and tracked (never performed) sandbox and access setup. Use when a deal has closed and delivery is starting: "kick off the project", "mobilize the engagement", "draft the charter", "set up the RAID log", "build the kickoff deck", "help me get ready for kickoff", "the handoff is accepted, what now", "stand up governance", "Sprint 0 plan", or any Mobilize-phase request. Do NOT use for the handoff itself (that is aleysian-s2d-handoff), ongoing status reports or RAID upkeep after kickoff (aleysian-delivery-status), requirements sessions (aleysian-requirements-capture), or scoping and pricing (the SOW is fixed input).'
---

# Aleysian delivery kickoff

Mobilization is the stage between an accepted handoff and real delivery work. It produces one
signed artifact (the Project Charter), one living system (the governance pack), and two meetings
(internal kickoff, then client kickoff). A weak start compounds: recovering lost efficiency in
weeks one and two costs roughly 110 percent effort later, which is why this stage is fast,
complete, and standardized rather than improvised per project.

One boundary carries the whole skill: **this skill drafts, humans sign.** It never signs the
charter, never commits the client to a cadence, never closes a handoff open question on its own,
and never provisions an environment. It prepares the artifacts the humans act on, and it tracks
what the humans did, truthfully.

## Phase 0: orient on the sources

Find the real objects before writing anything:

1. **The accepted handoff brief.** Its sections (team, stakeholder map with deal-versus-delivery
   mismatches, sell-cycle promises, scope and risks, open questions with owners) are this skill's
   raw material. If no accepted brief exists, stop: the handoff is not done, and that is
   aleysian-s2d-handoff's job, not a gap to paper over.
2. **The signed SOW**, with its id and as-of date. The SOW is fixed input. Scope, phases, figures,
   and commercial structure come from it; this skill renders them and authors none of them. Any
   figure ultimately traces to the quote the SOW was built from, per the money rule.
3. **The delivery model.** Detect waterfall or agile from the SOW variant, then confirm with the
   Program Lead or CSE before building anything variant-specific. Detected is not confirmed;
   never assume. Record the confirmation (who, when) in the charter and as a decision log entry.
4. **The shared engagement record**, where one exists. Read what the handoff populated (meta,
   scope_baseline, stakeholders, team, open_questions, gates); write only this stage's sections
   (raid, decisions, artifacts, gates, confirmed team) and log every change.

Stamp everything generated with SOW id and as-of date. Record IDs do not survive sandbox
refreshes; the stamp is what makes an artifact auditable later.

## Phase 1: draft the Project Charter

Read `references/charter-spec.md`, then fill `assets/charter-template.md`. The two rules that
matter most:

- **Scope is the SOW scope restated, never renegotiated.** The charter is where the client
  re-accepts what they signed. When the handoff brief or a transcript shows the client expecting
  something the SOW does not say (or vice versa), that delta becomes a flagged item (F-###) with
  an owner and a resolve-by date before client kickoff. Neither write it into the baseline nor
  silently drop it. If it implies paid work, humans take it to a Change Order conversation.
- **Every section is always present.** A section the sources cannot fill carries a known unknown
  with an owner, a resolve-by date, and the gate it blocks. A blank is an open question, not an
  invitation to invent.

Gate the draft before any human reads it:

```bash
python3 scripts/charter_check.py CHARTER.md
```

It verifies required sections, the scope source stamp (SOW id plus as-of date), a fully assigned
RACI with exactly one Accountable per activity and every team role covered, no leftover
placeholder tokens, and no em dashes. Exit 0 passes. Report the printed counts, not an adjective.
Then run the prose-pass checker over the charter prose. Fix the source and re-render; never
hand-patch output the next regeneration would lose.

The Program Lead secures the signature. Mark the charter DRAFT until they do. When the
signature lands, update the engagement's DELIVERY-STATE.md in the same session
(`charter_signed` with date, charter path, append-only dated log line) per
aleysian-delivery-suite's `references/delivery-state-spec.md`.

## Phase 2: stand up the governance pack

Read `references/governance-pack-spec.md`. Three artifacts from `assets/`: the RAID log, the
decision log, and the weekly status template. This skill creates and seeds them;
aleysian-delivery-status stewards them from kickoff onward, which is why the ID conventions are a
contract, not a style: R/A/I/D-### for RAID items, DEC-### for decisions, zero-padded, permanent,
append-only. Downstream stewardship diffs these tables by ID; a renumbered log breaks every later
report.

Seeding is the substance: every handoff open question becomes an owned RAID item with a resolve-by
date (letting one vanish is the named failure mode of this stage), handoff risks become R items,
SOW basis-of-estimate assumptions become A items, and maturity-gap capabilities (CPQ and Billing
amendments, ERP integrations, RCA migrations, DRO, UBB, CLM) each get a raised-oversight risk.
Every seeded item cites its source. Do not pad the log to look thorough.

Agree with the team where the pack lives before client kickoff, and log that location as a
decision. The decision log records only decisions humans actually made, with the human named.

## Phase 3: kickoff decks

Read `references/kickoff-deck-contracts.md` for what every slide must carry, per deck and per
variant. This skill owns the content contract only. Mechanics are delegated: deck-builder runs
the stage-gated build, pptx owns the file format, aleysian-brand-renderer owns brand tokens and
the visual, parity, and brand gates, prose-pass gates the copy. Do not inline hex values or
restate any of their rules.

Two decks, in order. The **internal kickoff** runs first, always: it is where the Program Lead
leads the risk and gap review off the seeded RAID log, and where the team agrees tools and the
note-keeping location, before the client sees anything. The **client kickoff** ends with explicit
agreement on cadence and the path to charter signature. Both decks are populated from this
engagement's record; a deck reusable on another client unchanged is a failed deck.

Build the confirmed variant only. If the SOW is ambiguous about the model, that is a flagged
delta and a human decision, not a hybrid deck.

## Phase 4: Sprint 0 plan, seeded backlog, research pack

Read `references/sprint0-backlog-seeding.md`. The Sprint 0 plan (mobilization plan on waterfall)
lists every item standing between the charter and productive Analyze work, each with an owner and
a date. The backlog seed is a projection of the SOW scope baseline: one E-### epic per
workstream, stories only where the SOW gives real basis, every item source-cited, no invented
scope, no sizing, no acceptance-criteria authoring (that is Analyze work, owned by
aleysian-requirements-capture). The client research pack is a two-page sourced extension of the
handoff overview, not pursuit-grade research; a meeting-specific prep pack is aleysian-call-prep.

## Phase 5: track the operational setup

Sandbox provisioning and access grants are human or system actions. This skill records their
status per environment and per person (provisioned, requested, blocked, verified), flags blockers
as RAID items, and prompts the Program Lead on what is stuck. It never performs the setup and
never marks anything ready that nobody verified. Claiming unverified sandbox readiness is a named
failure mode; track real status only.

## Durable output

Every run leaves a Markdown record per `_shared/output-contract.md`. On a full
mobilization that record is the charter draft plus the seeded governance pack;
on a partial or headless run it is a run record carrying the gate counts, the
flagged deltas, and the human actions still outstanding. Deliver or link the
files; never just say they were written.

## Governance delegation

- **aleysian-evidence-core** governs load-bearing factual claims (client context, stakeholder
  facts, sell-cycle promises). Run it before drafting where installed. If a load-bearing domain is
  insufficient, produce the readiness-gap memo and stop; a full charter on insufficient evidence
  is a hard fail.
- **aleysian-brand-renderer** owns brand for every rendered artifact, applied during the build.
- **prose-pass** owns voice; run its checker on every prose deliverable, including the charter.
- **The quote and SOW own every number.** This skill renders figures and authors none.

Where a governor is not installed on the current surface, state the check it would have run, do
the best manual substitute, and say that is what happened. Never silently skip, never pretend.

## Running unattended

Phase 0's variant confirmation, the charter signature, cadence agreement, and both kickoff
meetings need humans. On a scheduled or headless run: draft the charter, run the gate, seed the
governance pack, and stop with findings and open items. Never record a confirmation, agreement,
or signature nobody gave.

## When time is short

Cut in this order, and say what was cut: (1) the client research pack, (2) the internal deck's
client-context depth, keep the risk and gap slide, (3) backlog stories, keep the epics. Never
cut: the charter gate, RAID seeding from handoff open questions, flagged deltas, source citations,
or the internal-before-client kickoff order.

## Boundaries

In the delivery chain (SOW, then s2d-handoff, then kickoff, then status, then
UAT, then cutover-closeout), this skill's upstream producer is
aleysian-s2d-handoff, whose accepted brief is the raw material, and its
downstream consumer is aleysian-delivery-status, which stewards the logs this
stage seeds. Kickoff does not re-scope: the SOW baseline is restated, never
renegotiated, and every delta is a flag for humans.

- Does not run the handoff or write the handoff brief; that is aleysian-s2d-handoff.
- Does not steward status, RAID, or decisions after kickoff; that is aleysian-delivery-status,
  which takes over the exact files this skill seeds.
- Does not capture requirements or author acceptance criteria; that is
  aleysian-requirements-capture, in Analyze.
- Does not scope, price, or amend scope. The SOW is fixed input; deltas are flags for humans.
- Does not sign, approve, or gate. It drafts what humans sign and tracks what humans did.
- Does not provision sandboxes or grant access; it tracks them.
- Does not build deck files itself; deck-builder, pptx, and aleysian-brand-renderer do.

## Files

- `references/charter-spec.md` charter section spec and the scope-restatement rules.
- `references/governance-pack-spec.md` governance templates, stable-ID contract, seeding rules.
- `references/kickoff-deck-contracts.md` slide-by-slide content contracts, both decks, both variants.
- `references/sprint0-backlog-seeding.md` Sprint 0 checklist, backlog seeding rules, research pack.
- `assets/charter-template.md`, `assets/raid-log-template.md`, `assets/decision-log-template.md`,
  `assets/status-report-template.md` the shells to fill; content, not structure.
- `scripts/charter_check.py` the charter gate. Stdlib only; exits nonzero on failure.
- `scripts/charter_check_selftest.py` runs the gate against `scripts/fixtures/` (one passing
  charter, five shipped failing ones, plus an em-dash case synthesized at runtime so the shipped
  tree itself stays em-dash free). Run it after any change to the gate.
