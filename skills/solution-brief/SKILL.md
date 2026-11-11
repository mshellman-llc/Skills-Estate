---
name: solution-brief
description: 'Produce and validate Solution Briefs from an evidence-governed solution graph: judge whether a proposed solution is technically deliverable and make the delivery logic inspectable across systems, interfaces, failure paths, ADRs, scope, risks, assumptions, dependencies, staffing, phases, milestones, and financial reconciliation. Stops at a Technical Readiness Memo when load-bearing evidence is insufficient. Field guide mode builds the internal pursuit-team guide off the same graph for holding a scoping call or answering the in-house build we are up against. Requires evidence-core first. Do NOT use for the sourced client-facing architecture document (architecture-doc) or the SOW (sow).'
---

# Solution Brief

> **Before writing: [`build-card.md`](../_shared/build-card.md) plus
> [`readout-brief.md`](../prose-pass/references/registers/readout-brief.md). Inputs, not a final pass.**

Judge whether the proposed solution is technically deliverable and make the
delivery logic inspectable. Do not begin with a section template. Begin with the
evidence ledger, then build the normalized solution graph.

## Ownership

The Solution Brief owns:

- technical judgment and conditions
- system, process, data, and interface boundaries
- happy and failure behavior
- architecture decisions and alternatives
- included, excluded, conditional, and future scope
- technical risks, assumptions, dependencies, and closure conditions
- staffing feasibility and technical ownership
- phase, milestone, and decision-gate logic
- traceability among scope, effort, staffing, timing, and price

It does not approve margin, rates, discounts, capacity, staffing economics, or
commercial terms. Deal Desk owns those decisions. It does not perform signed
inheritance and safe-start onboarding. Sales-to-Delivery Handoff owns that job.

## Required prerequisite

Use the `evidence-core` skill first. The inputs to this skill are:

- validated evidence ledger
- gate report
- source manifest
- artifact contract for `solution_brief`

Do not bypass the evidence gate or change source authority here.

## Terminal branch

If the gate is Insufficient, do not assemble the graph and do not create a full
Solution Brief. Produce a compact Technical Readiness Memo containing:

1. the decision or direction worth retaining
2. blockers and closure conditions
3. ownership gaps
4. the next gate
5. lightweight evidence references

Then stop.

## Full-artifact workflow

1. Choose `approval`, `build_reference`, or `field_guide` mode.
2. Read `schemas/solution-brief-graph.schema.json` and
   `reference/validation-rules.md`.
3. Normalize the evidence into first-class graph nodes:
   systems, interfaces, ADRs, scope items, risks, assumptions, dependencies,
   roles, allocations, phases, milestones, financial lines, and reconciliation
   controls.
4. Create typed edges that preserve ownership, implementation, dependency,
   governance, risk, staffing, phase, price, exclusion, and closure logic.
5. Create the ten editorial views as references over the graph, not copied prose:
   technical judgment, system boundary, critical interfaces, architecture
   decisions, scope-to-solution trace, risk concentration, staffing and delivery
   shape, timeline and gates, financial reconciliation, and conditions and next
   action.
6. Select semantic components from `reference/component-library.md`. They are a
   component library, not a mandatory sequence.
7. Validate the graph:

```bash
python3 scripts/solution_graph.py path/to/solution-graph.json --output graph-report.json
```

8. Fix every error. Do not render a failed graph.
9. Draft the reader-facing views from the validated graph. Use the grammar named
   by each view: a system map remains a system map, an interface sequence keeps
   ordered exchanges and failure branches, an ADR preserves alternatives and
   rationale, staffing remains an allocation, and financials remain a
   reconciliation.
10. Use `brand-renderer` for brand, parity, visual, and prose gates.
    Never route all components through a generic card loop.

## Approval mode

Approval mode can compress implementation detail, but it must expose:

- the technical judgment and its force
- system and scope boundaries
- critical interfaces and failure behavior
- open and resolved load-bearing ADRs
- risk concentration and closure conditions
- staffing feasibility
- timeline and decision gates
- financial reconciliation status

## Build-reference mode

Build-reference mode requires approved interface contracts or an explicit block
on dependent work. Add detailed exchanges, failure paths, observability,
phase-level allocations, acceptance criteria, and work-prohibition rules.
Never turn approval-level inference into implementation-grade precision.

## Field guide mode

An internal artifact, never client-facing. It arms the pursuit team to hold a room:
what the solution is, how it works, and how to answer the person across the table
who believes they can build it themselves. It reads from the same graph as the
brief, so it inherits the evidence gate, the terminal branch, and claim governance.

Run the evidence gate under the `solution_brief` contract. There is no
`field_guide` artifact type, and the required evidence domains are the same
eleven. Record `metadata.gateArtifactType` so the divergence between the gate's
`solution_brief` verdict and the graph's `field_guide` output is visible rather
than silent.

Gate routing:

- Insufficient: Technical Readiness Memo, then stop. No guide on thin evidence.
- Conditional: build the guide. Every gate blocker becomes an entry in the
  `conditions_next_action` view with its owner and closure condition, and the
  masthead states that the guide rests on Conditional evidence. The validator
  rejects a Conditional field guide whose blockers never reach that register.
- Sufficient: build the guide.

Six view types exist for field-guide sections that have no brief equivalent:
`orientation`, `end_to_end_flow`, `data_model`, `pricing_architecture`,
`stakeholder_qa`, and `sources_evidence`. Intake options and output mechanics are
architecture decisions; model them as ADRs rather than as new sections.

### Sections are earned, not required

The brief infers required views from node presence. A field guide does not. Two
rules replace that inference:

- A section exists only when enough governed claim IDs sit behind it. Below the
  floor it is unearned. Omit it and record the reason. Never lengthen it.
- A load-bearing node must reach the reader somewhere, though not necessarily in a
  section of its own. Load-bearing, not merely present.

Propose the section set from the client's shape, then pause for confirmation before
building. Never generate a full set silently. Record every decision in
`sectionDispositions` as `included`, `thinned`, or `omitted`, each with a reason
and `confirmedInChat`.

Every candidate section needs a record, so a section cannot go missing quietly.
Nine are core: orientation, system boundary, end-to-end flow, data model, scope
trace, risk concentration, technical judgment, conditions and next action, and
sources. Five are conditional and earn their place from the client's shape:
pricing architecture, critical interfaces, architecture decisions, stakeholder
Q&A, and timeline gates. Staffing and financial reconciliation are not candidates,
because a field guide never staffs and never prices. A view with no record fails, a
record that contradicts what was built fails, and a candidate with no record at all
fails.

When the signature Q&A section has no inputs, because no technical counterpart is
named and no in-house build has been proposed, omit it and say so in the record.
Writing objections nobody raised invents evidence.

Gaps go to the seller in chat, never into the artifact body. No `[TBD]` markers.

### Ledger, Q&A, and money

The build ledger is a projection of scope items. Every row carries
`buildDisposition` of `native`, `config`, `custom`, or `dep`, so the ledger
cannot drift from scope. A field guide does not price, so its scope items owe no
financial trace, and a guide carrying reconciliation controls is the wrong artifact.
Pricing authority stays with the scoping system.

Each `qaEntry` carries the question in the stakeholder's voice, an answer leading
with the mechanism, and a `dependencyAsk` that ends it and puts work back on their
desk. The dependency ask is required. Handle the hardest question, usually the
build-it-ourselves case, explicitly rather than around the edges.

Render with `scripts/build_field_guide.py`, which reads the canonical brand profile through `brand-renderer` and embeds its colors and any declared font or logo files. Use `--profile path/to/brand.md` for a project profile; the neutral profile needs no proprietary assets. See
`reference/field-guide-widgets.md` for the four widgets and the pill vocabulary.
`assets/field-guide.body.html` is the synthetic worked reference.

Read `reference/field-guide-content.md` before writing. It carries the four things
that separate a guide that lands from one that reads like filler, plus the section
order and the money-and-gaps discipline.

Then exercise it in a real browser:

```bash
python3 scripts/qa_field_guide.py <built.html> qa/
```

The widgets are interactive, so a static render proves nothing about whether they
work. This clicks each one and screenshots the result. The browser check uses Node.js and Playwright. Set `ESTATE_NODE`, `ESTATE_NODE_MODULES`, and optionally `PW_CHROMIUM` to existing installations, or use Node and Playwright from the environment. Missing browser support and broken interactions fail the check. Each attempt saves its report and screenshots in a new directory. A successful interaction check still requires inspecting the screenshots and comparing the content with its sources.

## Adequacy gate

A full brief fails before visual review if it lacks any applicable core family:

- systems
- interfaces and failure paths
- ADRs
- scope traceability
- staffing and allocations
- phases and milestones
- financial lines and reconciliation
- typed relationships
- canonical views
- distinct semantic grammars

Generic headings plus one-sentence claim cards are a hard fail even if every
claim ID appears.

## Financial boundary

The graph may carry the authorized commercial baseline to prove technical
traceability. Reconciliation failure blocks content approval. The Solution Brief
surfaces the discrepancy and its technical consequence; it does not decide
whether the commercial position is acceptable.

## Fixtures and tests

All fixtures are synthetic and anonymized. Run after any script or schema edit:

```bash
python3 scripts/solution_graph_selftest.py
```

The selftest covers a rich graph, the terminal readiness branch, dangling edges,
missing failure behavior, orphan scope, bad allocations, failed reconciliation,
generic-card grammar, build-reference contract gaps, and sparse full-output
pressure. For field guide mode it covers a passing guide on Conditional evidence,
an unearned section, an unreached load-bearing node, a hidden gate blocker, a
section dropped with no recorded reason, and a ledger row with no disposition.

## Release rule

A passing graph is necessary but not sufficient. The artifact still needs the
brand renderer's parity, visual, and prose gates plus a human or model reading
pass. Preserve every caveat, conflict, condition, number, name, and evidence
reference through the final format.

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
