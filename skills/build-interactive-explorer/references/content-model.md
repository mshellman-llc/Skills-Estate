# Content guidance

Choose the content model for the project. Do not require a particular JSON schema, paths, stages, personas or section count. Store content in the format appropriate to the chosen implementation.

## Structure around the reader's task

- Use ordered stages for an actual sequence, decision process or journey. Where supported, explain the goal, action, decision, handoff, finding and open question. Omit irrelevant fields rather than filling them with invented material.
- Use distinct paths when audiences or tasks genuinely need different routes. A single shared view may be clearer.
- Use thematic sections for research findings, a comparison for choices, a map for relationships, or search and filters for a large reference collection when these better fit the material.
- Add people and jobs, role journeys, capabilities, priorities, dependencies and open decisions only when supported by sources and relevant to the reader.
- Adapt domain labels and level of detail. Do not import another project's roles, phases, release commitments or terminology.

## Preserve evidence and relationships

- Give claims human-readable source titles and useful locators. Provide a consolidated source index when it helps readers audit the material, with contextual links from the relevant details.
- Use internal IDs only as linking keys, not as primary UI copy. Ensure every internal reference resolves to a present item.
- Use real, safe HTTP(S) URLs; omit unavailable links. A review date must record an actual review, not an assumed current state.
- Record source date and authority. Distinguish findings, proposals, hypotheses, approved decisions, verified behavior and unresolved questions. Mark fictional examples explicitly if the task calls for them.
- Keep newer scope decisions visible with their dates when they qualify rather than replace earlier evidence.
- Verify current product capabilities through official sources rather than carrying over claims from another project.
- Store original evidence outside the skill. Summarize only for the authorized audience and preserve original source permissions.

## Check completeness without adding filler

Ensure each visible section has a clear purpose and substantive content. Remove empty optional sections and derive counts from the actual content. Do not invent research, quotations, metrics, emotions, roles or approvals to complete a visual pattern. Identify material gaps and the questions needed to resolve them.

## Optional roadmaps

Use `build-roadmap` when sources describe planned work over time. Validate its plan with that skill’s tooling before embedding the snapshot components. Reject live bindings in an explorer; keep source access read-only and preserve the no-network presentation behavior. Use the roadmap for sequence and separate scope categories for priorities. If a dependency is missing or the plan is invalid, report the exact issue and leave the roadmap unbuilt rather than inventing an implementation.
