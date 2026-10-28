---
name: architecture-doc
description: "Write a formal, sourced architecture or technical design reference covering intent, components, data, interfaces, security, operations, and trade-offs."
---

# Architecture doc

Read [shared workflow](references/estate/workflow.md). For a rendered or branded artifact, read [brand policy](references/estate/brand.md) before choosing visual values. These references are generated from the canonical policies when the estate builds.

Identify the governing requirements and decisions, the reader, and the system boundary. Name unresolved source conflicts. An explicit current authority outranks a document selected merely because its file date is newer.

Separate architecture intent from implementation design. The architecture explains the product shape, boundaries, rationale, ownership, security posture, costs, and risks. The technical design supplies component contracts, data models, APIs, identity flows, deployment topology, operational controls, and failure paths. Link the two without repeating the same prose.

Tie substantive factual claims to sources. Present a design choice as a proposal with alternatives considered, the trade-off, and conditions for revisiting it. Do not describe a planned control as operating or a projected cost as measured. State material open decisions where the reader needs them.

Use diagrams only where they clarify boundaries or flows. Apply the shared brand policy when rendering a formal artifact. Verify that diagrams, tables, prose, and source revisions agree and that no assumption turned into an assertion during rendering. Deliver the requested editable format and identify the next design decision or implementation step.

## Document skeletons and visual acceptance

Before drafting, read [the architecture and engineering skeletons](references/architecture-templates.md). Select the sections needed by the actual system. Use descriptive names and put detailed traceability in a reference section; do not fill the reading flow with IDs.

A system map must show labeled relationships, trust or ownership boundaries, and flow direction. For a load-bearing interaction, show ordered requests, responses, state changes, and failure handling. A collection of prose boxes is not an architecture diagram.

Before delivery, render and inspect the requested format. Check that diagrams, tables, claims, caveats, numbers, and source revisions survived; inspect print output when a printable artifact is requested. Resolve stale framing throughout the document set rather than placing a correction banner over contradictory content. Use the current design system without former-employer branding.
