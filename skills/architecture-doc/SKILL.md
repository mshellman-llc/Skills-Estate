---
name: architecture-doc
description: Write a sourced architecture or technical design reference covering intent, components, interfaces, data, security, operations and trade-offs. Use for a formal reference document; use system-design for an exploratory working design.
---

# Architecture reference

Turn the current source material and confirmed decisions into an architecture reference. Separate requirements, observed behavior and proposed design choices. Use the project's selected brand or neutral defaults.

## Required inputs

Identify the system, intended reader, requested format and source authority. Read the relevant brief, decisions record, requirements and operating notes completely. Resolve source precedence from their authority and accepted decisions; a newer timestamp alone does not settle a conflict.

Select the rendering runtime and project brand profile before building. Logos, typography, colors and layout rules come from that profile. A neutral document needs no logo or brand footer. Apply the intended author's confirmed voice when supplied and use `writing-integrity` for prose review.

If a missing source prevents a supported design, identify that gap and the decision it blocks. Continue the supported portion when useful. Never supply a plausible number or undocumented behavior as fact.

## Scope

Use this mode for a formal architecture reference, platform architecture or complementary architecture and engineering design set. Route proposals and delivery feasibility to `solution-brief`, contract scope to `sow`, journeys to `journey-mapping`, and backlog preparation to `requirements-capture`. Use `system-design` for early design exploration.

## The two documents

**Architecture doc, the what and why.** Overview, product shape, architecture at a glance,
security posture, cost and ownership, stand-up or build, jobs to be done, growth, risks.

**System design, the engineering how.** Overview, requirements, high-level design, identity and
authorization, data model, API, credential and serving, records and cascade, governance and
audit, scale and reliability, trade-offs.

Read [architecture-templates.md](references/architecture-templates.md) for the fillable sections, diagrams, schema and trade-off patterns. Select sections that serve the actual system and requested decision. Keep intent and engineering views complementary. Link shared decisions instead of copying them into conflicting descriptions.

A system map shows labeled, directed relationships and trust or ownership boundaries. Name the operation or data crossing each boundary. For a load-bearing interaction, show ordered requests, responses, state changes and failure handling. Distinguish the confirmed system from a proposed model.

Security posture belongs in the architecture view; enforcement details belong in the engineering view. Identify the principal, relevant tenant or isolation key, allowed actions, enforcement location and denial behavior. Tenant isolation and permission to act are separate checks; all required checks must pass. Missing policy or failed authorization denies the action.

For retries and redelivery, distinguish sequential recovery from concurrent duplicate execution. Checking completed state alone is insufficient. Name the atomic claim or uniqueness boundary, idempotent writes and external side-effect handling needed by the proposal; retain unproven failure windows and avoid unsupported exactly-once claims. A failed claim does not prove work is complete. Distinguish completed, busy and expired claims; do not acknowledge unfinished work unless a separate durable recovery trigger has accepted responsibility. Otherwise defer or retry delivery under the queue contract. State what restarts work if the current owner dies. Use sourced infrastructure and people costs. Identify volume assumptions before extending a cost model. Each design choice states its trade-off and the condition for revisiting it.

---

## Build the reference

1. Read the source set and name its authority. Associate each factual claim with a source locator. State which accepted decision resolves a source conflict.
2. Select the requested document or set. Outline the relevant sections and source each before drafting. Explain the system in ordinary language before expanding its technical views.
3. Frame design choices as proposals with their rationale and trade-offs. Report consequential open decisions to the user. Include an unresolved condition in the document when readers need it to make or implement the decision.
4. Read [the build card](../_shared/build-card.md) to resolve the runtime and apply the selected brand profile during the build. Use its available assets and configured runtime. If HTML is requested, embed the required styles and assets and reject unresolved template placeholders.
5. Review all prose, including interface labels and captions. Use the bundled `prose-pass` diagnostic tools where applicable, and read the result for meaning. A scanner result does not select the author's voice.
6. For styled artifacts, run the configured `brand-renderer` checks. Use `quality-gate` to assess the completed content and applicable review records.
7. Render and inspect every page or view. Check diagrams, tables, source locators, accessible contrast and technical content against the source. Exercise interactions when present.
8. Cascade changed figures and accepted decisions through the document set. Deliver the requested editable source and exported format with their actual validation state.

## Output and acceptance

Use the requested format. A self-contained HTML reference is a useful default when none is specified. Include a title and metadata identifying the owner, date and decision state. Put source locators with their claims or sections. Use a systems diagram to show boundaries and interfaces and tables to compare real choices.

A source line may read `Source: architecture decisions, section 2.` A proposal may read `Design proposal, consistent with [named requirement].` Do not style a proposal as an established requirement.

Before delivery, check that the source set supports the claims; important unknowns remain visible to the people who must act on them; the design choices name their trade-offs; and superseded decisions have been removed throughout the set. Compare rendered content with the editable source. Review both prose and interface text. Confirm that the selected profile was applied and that no unrelated identity remains in the output.

Keep [the release gate](../_shared/release-gate.md) as the shared artifact review procedure. Retain the templates and validation resources when packaging this mode inside `system-design`.
