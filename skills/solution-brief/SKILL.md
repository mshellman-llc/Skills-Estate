---
name: solution-brief
description: "Assess whether a proposed solution can be delivered and explain its systems, interfaces, scope, ownership, risks, and implementation decisions. Use for solution approval, build references, and internal scoping guides."
---

# Solution brief

Read [shared workflow](references/estate/workflow.md). For a rendered or branded artifact, read [brand policy](references/estate/brand.md) before choosing visual values. These references are generated from the canonical policies when the estate builds.

Identify the decision and choose approval, build-reference, or internal field-guide mode. Read current requirements, evidence, scope, architecture decisions, and delivery constraints. Keep a working graph of systems, interfaces, data, dependencies, work packages, owners, phases, risks, and decisions with stable IDs.

Connect each implementation claim to its source and affected component. Identify authentication, data ownership, error handling, retry behavior, operational ownership, and failure recovery for integrations. Record unresolved load-bearing questions rather than filling them with a plausible design.

If feasibility cannot yet be established, deliver a technical readiness memo: direction worth retaining, blockers, closure conditions, owners, and the next decision. Otherwise explain the solution from the reader's perspective and include the implementation detail needed for the selected mode.

Check that every scoped outcome has an implementation path and owner, each dependency has a resolution plan, and proposed decisions state their trade-off. Reconcile financial figures with the quote instead of deriving new commercial commitments. For an internal field guide, include likely buyer questions and supported answers. Preserve the distinction between an assessed design, an implemented system, and behavior observed in production.

## Depth, calibration, and release

Read [the output contract](references/output-contract.md) before drafting. Derive the structure from this engagement's evidence, then inspect [the worked architecture example](example/architecture-calibration.html) as a depth yardstick. The example is fictional: never import its systems, counts, owners, or retry policy into a real brief.

Show actual system relationships and ordered exchanges. Boxes of prose do not substitute for a system map or sequence. Lead with descriptive system, interface, and decision names; keep stable IDs in the working graph and references, not as reader-facing labels.

For structured graph work, use [the graph contract](schemas/solution-brief-graph.schema.json) and [validation rules](reference/validation-rules.md), then run `python3 scripts/solution_graph.py graph.json --output graph-report.json`. Fix errors before rendering. The validator is a consistency check, not evidence retrieval or proof that the design is implemented. The graph fixture format preserves existing machine IDs; those IDs do not dictate display labels. Field-guide section confirmation follows the user's existing authorization; do not fabricate a confirmation value. This optional graph adapter is not a requirement to invent a graph for a brief that the user requested in another form.

Run `python3 scripts/solution_graph_selftest.py` after modifying the validator or schema. Before delivery, compare the rendered artifact against its evidence and inspect the actual diagrams, narrow-screen layout, and print output. A passing graph alone is not a visual sign-off.

## Interactive internal field guide

For an internal field guide, read [the field-guide workflow](references/field-guide-workflow.md). The restored local renderer and synthetic four-widget example provide an executable build path without private services or employer assets. Its interactive panels supplement real system and sequence diagrams; they do not replace the architecture output contract.
