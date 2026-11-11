---
name: evidence-core
description: 'Builds and validates the Knowledge Hub evidence records for Estate consulting work. Use before creating or materially revising a client artifact whose factual claims must trace to governed sources. Owns source authority, atomic claims, confidence, staleness, conflicts, inline claim references, and evidence sufficiency; it does not own Hub storage or the consulting lifecycle layout.'
---

<!-- ESTATE-WRITING:BEGIN -->
Before writing, read the [writing standard](references/estate/writing.md). Apply it to every authored sentence. Review instructions and internal records too. Audience labels and file formats do not exempt prose from review.
<!-- ESTATE-WRITING:END -->


# Estate evidence core

> **Before writing: [`build-card.md`](../_shared/build-card.md) plus
> [`readout-brief.md`](../prose-pass/references/registers/readout-brief.md). Inputs, not a final pass.**

Build the evidence foundation before planning an artifact. The visible document
is never the first deliverable. The evidence ledger is.

## Non-negotiable behavior

- An absent fact becomes a named gap. Never fill it with plausible language.
- Preserve source conflicts. Never silently choose the convenient version.
- A recent message does not override an executed commitment without explicit
  authority.
- Worked examples and generated artifacts have zero evidentiary authority.
- Every load-bearing claim carries governed claim IDs and source IDs.
- Unknown or contested load-bearing claims require an owner and closure
  condition.
- If a required load-bearing domain is Insufficient, output a compact
  readiness-gap memo and stop. Do not continue into the requested full artifact.

## Inputs

Accept source files and exports in any practical format, but normalize their
meaning into `schemas/evidence-ledger.schema.json`. The ledger carries a stable
client, opportunity, or engagement context. Legacy engagement metadata remains
readable during migration.

Each source records:

- source ID and type
- title and resolvable locator
- authority score
- observed and effective dates
- supersession relationships
- notes about limitations

Each claim records:

- claim ID and statement
- Confirmed, Inferred, Unknown, Contested, or Superseded status
- source IDs
- as-of time
- load-bearing flag
- artifact domains
- confidence rationale
- owner and closure condition when unresolved

## Authority model

The validator caps authority by source type. Highest authority belongs to
executed commitments and current authorized design or commercial records.
Meeting records, client documents, CRM, internal models, and messages have
bounded authority. Generated artifacts and worked examples have authority zero.

Do not inflate a source's authority to make a claim pass.

## Knowledge Hub ownership

Knowledge Hub owns where `evidence.sources` and `evidence.claims` live, how they
are resolved across storage surfaces, and whether a write persisted. This skill
owns what those records mean and whether the evidence is sufficient. Do not
create a second evidence store beside the Hub.

An inline marker such as `[CLM-0042]` is a pointer to a complete claim in the
ledger. It does not replace the ledger entry. Preserve an existing governed ID
when importing another research workspace; map its fields before minting a new
identifier.

## Source register

The logical Hub record `evidence.sources` records where facts came from. Every
inventoried source gets a register row with the source fields listed under
Inputs. When a source supersedes
another, record that lineage in the register and mark the dependent claims
Superseded rather than deleting them. Evidence status in the register follows
the claim statuses above; the register row and its claims may never disagree.

The register enforces one rule at finalization: every load-bearing claim in a
client artifact names its source. Quantified and factual claims, meaning
dollar and hour figures, percentages, counts, dates, named capabilities, and
vague quantifiers such as "most" or "several", each need an adjacent source
marker: a document name, a `[SOURCE: ...]` tag, a confirmed quote id, or an
evidence reference resolving to a register row. A claim with no marker fails
the artifact. A vague quantifier warns even when sourced; prefer the number
with its source. Honest uncertainty is never the failure: Confirmed, Inferred,
Unknown, estimated, ranges, and "not priced" all stand.

Numerical agreement with the quote does not establish a narrative claim's
origin. This rule checks that every claim names an origin. No script
enforces it yet; apply it by hand at finalization and note the manual pass in
the release record.

## Workflow

1. Resolve the Knowledge Hub, then inventory sources into `evidence.sources` and identify lineage,
   supersession, and staleness.
2. Create atomic claims. Split mixed statements when their sources or confidence
   differ.
3. Record open conflicts and their materiality.
4. Populate the shared scope, estimate, decision, risk, assumption,
   stakeholder, and timeline registers when relevant.
5. Choose the artifact contract from `reference/artifact-registry.json`.
6. Evaluate required domains with the standalone validator:

```bash
python3 scripts/evidence_core.py path/to/ledger.json solution_brief --output gate-report.json
```

7. If the result is Insufficient, produce the named readiness-gap memo with:
   direction worth retaining, blockers, closure conditions, ownership gaps,
   evidence references, and the next gate. Stop.
8. If Sufficient or permitted Conditional, pass the validated ledger and gate
   report to the artifact-specific skill.

The CLI exits nonzero for a terminal result so automation cannot accidentally
continue into full generation.

## The event log, a trial

Inside a pursuit workspace the ledger is authored as `evidence/evidence-ledger.jsonl`,
an append-only event log under git, one JSON object per line. This is the
authoring form agreed with the workspace standard on 2026-09-01. The schema
document above stays the form the gate reads; `scripts/ledger_events.py project`
produces it, so nothing downstream changes, and if the trial fails the projection
step is dropped and the document is authored directly.

Events: `context` first, then `source`, `claim`, `supersede`, `conflict`, and
`register` (scope, estimate, decisions, risks, assumptions, stakeholders,
timeline). A claim carries the inline authoring tag from the workspace
standard: `STATED` and `OBSERVED` project to Confirmed when a supporting source
has authority 70 or higher and to Inferred otherwise, `INFERRED` to Inferred,
`ASSUMED` to Unknown with an owner and closure condition when load-bearing. A
decision is a `register` row in `decisions`, never a claim; the check refuses a
`DECIDED` claim because tagging a decision as evidence launders judgment. A
superseded claim gets a `supersede` line, never an edit; a restated claim is a new
line with the same id and the latest wins. Open conflicts project their claims as
Contested. Only load-bearing claims are recorded.

```bash
python3 scripts/ledger_events.py check evidence/evidence-ledger.jsonl
python3 scripts/ledger_events.py project evidence/evidence-ledger.jsonl \
  --output evidence/evidence-ledger.json
```

Run `check` at every orchestrator gate commit, alongside `knowledge-hub`'s
`hub_workspace.py check`, which proves the file is append-only against the
committed copy and resolves the ids cited in prose. The projection then goes
through `evidence_core.py` at finalization as before. `fixtures/pursuit-ledger.jsonl`
is a worked example with every event kind.

## Conditional coverage

Conditional is valid only when the unresolved item has:

- a named owner
- a closure condition
- affected entities or artifact domains
- a clear rule preventing dependent work from proceeding early

Otherwise mark the domain Insufficient.

## Validation and maintenance

Run the selftest after any script, schema, or registry change:

```bash
python3 scripts/evidence_core_selftest.py
python3 scripts/ledger_events_selftest.py
```

The fixtures are synthetic and cover rich evidence, sparse evidence, an open
load-bearing conflict, and superseded pricing.

## Handoff to artifact skills

Pass these together:

- validated evidence ledger
- gate report
- artifact contract
- source manifest

The downstream skill may reason from the ledger. It may not bypass the gate,
change source authority, or treat an example as content.
