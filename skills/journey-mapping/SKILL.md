---
name: journey-mapping
description: "Build a customer or role journey map, service blueprint, and opportunity map from touchpoints, goals, thoughts, emotions, friction, and the systems underneath, with every claim sourced or labeled as a hypothesis. Use for a client deliverable, a product's user or seller journey, or an internal lifecycle map. Triggers on customer journey, journey map, service blueprint, user journey, experience map, touchpoint analysis, friction map, emotional curve, line of visibility, CX blueprint, and on teams that hold different mental models of one experience. Testing one screen is a usability test; generative research comes first when no map exists."
license: MIT
metadata:
  upstream: "rampstackco/claude-skills"
  upstream-commit: "98d8cfe773f975a465f11c56d8fb2ae618307805"
  adapted: "2026-10-22"
---

<!-- ESTATE-WRITING:BEGIN -->
Before writing, read the [writing standard](references/estate/writing.md). Apply it to authored prose while preserving quotations and required literals.
<!-- ESTATE-WRITING:END -->

Before drafting, read the [build card](../_shared/build-card.md) and [readout brief](../prose-pass/references/registers/readout-brief.md).

# Journey mapping

Read [shared workflow](references/estate/workflow.md). For a rendered or branded artifact, read [brand policy](references/estate/brand.md) before choosing visual values. These references are generated from the canonical policies when the estate builds.

A journey map shows what one actor tries to do across an experience, where it hurts, and what sits underneath each step. This skill produces three linked views: the journey map, the service blueprint, and the opportunity map. The opportunity map is the deliverable that produces decisions; the other two are its evidence.

The method is stack-neutral. Name whatever the actor and the business actually use: a CRM, a homegrown app, a ticketing system, a data warehouse, spreadsheets, an AI agent. On a Salesforce engagement, the template carries optional prompts for clouds, flows, and agents.

Common orientations:

1. A client deliverable that maps the client's customer journey across channels, systems, and AI touchpoints.
2. A product journey that maps one role through a product, such as a seller working one deal from lead to recorded outcome. Related roles get their own maps with shared phase IDs where their paths meet.
3. An internal lifecycle map of the business's own path from first contact through delivery and growth.

## Rules that apply throughout

Identify the actor, scenario, journey boundary, outcome, and intended decision before mapping. Write the scope as one sentence: one actor, one journey, from a starting event to an ending event. Separate the current state from a proposed future state. A future-state map does not prove the process has changed.

Source every claim. Each pain point, emotion, drop-off, and behavior traces to a named transcript, interview, ticket set, analytics query, system record, or built-system behavior. When an input does not capture something, write "not captured" rather than a plausible fill.

Give every claim an evidence basis: observed (system records, analytics, built behavior), reported (what a participant said), or hypothesis (reasoned without participant evidence). Do not label one interview as universal behavior.

Use one map per segment. Merging two buyer types into one map produces a map that describes neither.

Keep the same phase IDs across the journey map, blueprint, and opportunity map.

Plain language leads. Method labels, stage codes, and internal IDs stay off a client-facing surface.

## Labeled-hypothesis mode

The human layers (thoughts, emotions, and the pain the actor feels) may be drafted as hypotheses when no interviews exist yet. This is useful for a first map of a new product role, where the front-stage and back-stage can be grounded in the built system while the human read cannot. The hypothesis mode has five conditions:

1. State the basis once, next to the map, in plain words. Example: "Front-stage and back-stage are grounded in the built system. Thoughts, emotions, and pain are reasoned from the role and the system's known failure modes, not from interviews. This is a first map to validate with real users."
2. Mark every hypothesized layer visibly. In a rendered map, draw a hypothesized emotional curve with a dashed line or a "hypothesis" label, and style hypothesized thoughts differently from sourced quotes. In the source ledger, the confidence column reads "Hypothesis".
3. Name the reasoning for each hypothesis: the role's constraints, a measured system behavior, or a known failure mode. A process diagram alone is not a basis for an emotion.
4. Never attribute a hypothesized thought to a person, transcript, or count of participants. Hypothesized thoughts are written as the likely thought, not as a quote from someone.
5. Pair the map with validation questions: what to ask, whom to ask, and which hypothesis each answer confirms or overturns.

System facts used as a basis stay observed. "5 of 35 playbooks are published" can sit beside a hypothesized emotion when the number comes from the system record. Once interviews exist, replace each hypothesis with the evidence or record that the evidence contradicted it.

## When to use

- Departments or workstreams hold different mental models of the same experience.
- A customer experience feels disjointed across systems and channels.
- A specific friction or drop-off point needs a diagnosis.
- Strategic planning needs a shared, evidence-grounded view of the actor.
- Front-stage and back-stage need to be aligned, including the CRM and integration layer.
- A new feature, workflow, or AI agent needs to be designed in the context of the whole journey.

Do not use it for testing one page or screen (use `usability-testing`), generative discovery before any map exists, process mapping with no actor in it (use `process` or `sales-process-mapping`), or single-step funnel optimization.

## Required inputs

- One named persona, role, or segment.
- Evidence about that segment: discovery transcripts, interviews, support tickets, survey data, product analytics, CRM records, or the built system. Without participant evidence, use the labeled-hypothesis mode.
- Cross-functional access. The back-stage cannot be mapped without input from the people who run sales, service, operations, and the platform, or from the system itself.
- Stakeholder time. A real journey map is an engagement, not an afternoon.

## The three deliverables

**1. Journey map, the actor's view.** Eight lanes per step: phase, step, touchpoint, goal, thoughts, emotion, pain point, opportunity. Let phases emerge from the real experience instead of forcing a preset. Name the real channel at each touchpoint. Thoughts are a real quote where a transcript has one. Score emotional intensity from 1 to 5 per phase or step so the emotional curve can be drawn; the troughs mark the critical friction and the peaks mark what to protect.

**2. Service blueprint, what makes each step work.** Add front-stage actions (visible to the actor), back-stage actions (staff or system work out of view), supporting systems, and the two lines between them: the line of visibility and the line of internal interaction. Connect each layer to owners, data, handoffs, and failure points, and show where responsibility or evidence is missing. The blueprint traces a front-stage symptom ("my case took a week") to its back-stage cause ("no routing rule, so it sat unassigned"). Back-stage failures cluster at the line of visibility: a broken automation, a stale integration, a data-quality gap, or an empty table that should hold outcomes.

**3. Opportunity map, the output that drives decisions.** List critical friction with evidence, quick wins (often configuration rather than build), strategic bets, front-stage to back-stage disconnects, and gaps that need more than one team. Link each opportunity to the friction it addresses, an intervention, the expected outcome, an owner, dependencies, an effort basis, and how it will be measured. Distinguish reported severity from your prioritization. Effort and impact are labels, not prices; route anything that needs a price to `scoping-agent` or `rom`.

The fillable version of all three, with the lane tables, blueprint layers, source-and-confidence ledger, and opportunity tables, is in [the journey map template](references/journey-map-template.md).

## Phase presets

Six presets are in [the journey map template](references/journey-map-template.md): most products, SaaS, service business, client-customer CX engagement, consulting prospect-to-client lifecycle, and a product role journey. They are a starting point. A preset forced onto an experience it does not fit produces a map that reads well and describes nothing.

## Gathering the inputs

A credible map compares three views that usually disagree, and the disagreements are findings.

From users or clients: interview transcripts walked through a real, recent instance; diary or over-time logs when the journey spans weeks; surveys for scale, which trade depth for reach.

From the business and platform: internal interviews with sales, service, success, and operations, who each see a different slice; operational data such as funnel drop-off, ticket categories, NPS verbatims, and churn reasons; a system inventory of touchpoints, the systems behind them, and where data flows or stalls.

Cross-validate what the user says happens, what the data says happened, and what the internal team believes happens. Record each gap.

## Workflow

1. Scope: one actor, one journey, one timeframe, written down before mapping.
2. Gather transcripts, interviews, operational data, and the system inventory.
3. Draft the spine: phases, steps, and touchpoints. Get to a rough draft fast, then iterate.
4. Add the human layers: goals, thoughts, emotions, and pain points, each with a source or a hypothesis label.
5. Blueprint the back-stage: front-stage, back-stage, supporting systems, and the visibility lines.
6. Find the opportunities from friction and disconnects, not from a wish list. The critical friction sits where the emotional curve drops.
7. Validate with the actors. Correct the map and convert hypotheses to evidence.
8. Walk the map with stakeholders and agree on the top opportunities.
9. Translate to action: named projects, owners, and sequence.
10. Maintain the map. Re-map on a major change or on a set cadence.

Reconcile the three views before rendering.

## Rendering the map

For a visual map, read [the rendered map layout](references/rendered-map-layout.md). It describes the board: phase columns, an emotional curve row, the human lanes, the line-of-visibility band with front-stage, back-stage, and supporting rows, the evidence-basis note, and the critical friction callouts. [The HTML starter](assets/journey-map.html) renders that layout from one data object with neutral brand values; apply the confirmed project profile through `client-brand` when one exists.

## Failure patterns

- Mapped from assumptions that are presented as findings. A hypothesis map is allowed only when it is labeled as one.
- One map for every user. Different buyers have different journeys.
- No back-stage. Symptoms appear without causes because the map never reaches the workflow or integration that broke.
- Beautiful and inert. Production value was spent and no decision came out.
- Filed and never reopened.
- Emotion dropped. The map shows what happened and not how it felt, so the troughs cannot be found.
- Vague pain. "Onboarding is frustrating" is not a finding. Name the step, the moment, the cause, and the source.
- Fabricated fill. A plausible detail with no source is worse than "not captured".
- Quick wins found and never shipped.

## Output format

Default outputs are the journey map (a visual plus a Markdown narrative), the service blueprint (in the same visual, or its own document when the back-stage is deep), and the opportunity map in prioritized Markdown. Copy [the journey map template](references/journey-map-template.md) and fill it rather than rebuilding the structure.

## Before shipping

Before delivering a map, follow the [release gate](../_shared/release-gate.md): reconcile the ledger with `evidence-core`, review the prose with `writing-integrity`, and inspect the rendered result. Resolve the brand through `client-brand` and run `brand-renderer` on styled output. Run `quality-gate`; do not call the map final until every applicable check passes. The map carries labeled effort and impact, not prices. A hypothesis map ships with its basis note and validation questions.

`scripts/journey_mapping_selftest.py` checks that this file and its references still carry the lanes, blueprint layers, ledger, presets, hypothesis mode, and render layout.

Adapted from [RampStack's journey-mapping](https://github.com/rampstackco/claude-skills/tree/98d8cfe773f975a465f11c56d8fb2ae618307805/skills/journey-mapping). The original MIT notice is in [LICENSE](LICENSE).
