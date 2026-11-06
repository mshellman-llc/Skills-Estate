---
name: write-feature-spec
description: "Write a feature specification, PRD or implementation brief from supplied product evidence. Include relevant user flows, UI states, APIs, data changes and testable acceptance criteria. Use for requested specifications; ordinary bug fixes do not require a separate spec."
license: MIT
---

## Choose the requested task

Use the primary workflow below unless the request matches a mode in this table. For a matching mode, read its complete linked workflow and required references, then produce that mode's output. Preserve its calculations, failure handling and acceptance checks. One request does not require every mode.

| Requested mode | Complete workflow |
| --- | --- |
| detailed UI and API specification | [specify-implementation](_runtime/specify-implementation/WORKFLOW.md) |



# Write feature spec

Write a spec that lets the next owner understand the requested behavior and verify it. Read the current brief, supplied sources, and existing decisions before drafting. Separate a confirmed requirement from a proposed choice or open decision.

Read [Spec decisions](references/spec-decisions.md) to choose the appropriate depth. A bounded change can use a compact development brief. A cross-system feature may need a fuller spec. A reproducible defect needs expected behavior and evidence of actual behavior, not a fabricated product strategy.

For UI, API or persistence detail, read [the detailed feature workflow](_runtime/specify-implementation/WORKFLOW.md). Select the sections the requested feature needs; retain its state transitions and failure paths.

Use the audience's vocabulary. Describe the problem and intended outcome, the behavior in scope, and the constraints that affect implementation. Include exclusions only when they prevent a plausible misunderstanding. Give dependencies and unresolved decisions their actual owners when known.

Make acceptance criteria observable. Cover the main path and the edge cases that matter to this feature. Specify how to check the outcome at its real destination. Do not turn implementation preferences into product requirements without evidence.

Ask only for a missing decision that materially changes the spec or blocks useful work. Draft the supported portions while that decision is pending. Do not impose a fixed discovery questionnaire, require a universal “why now,” or invent a baseline, effort estimate, target, date, or owner to fill a template.

Use an existing work item when supplied. Preserve its ID and current state; drafting a spec does not close a Brain task or create a competing task system. Keep implementation and external release separate from specification unless the user requested those actions too.

Deliver the requested document at the depth its reader needs. Identify the decisions still needed to make its acceptance criteria executable. Existing source authority, claim checks, voice, brand, and completion rules govern the result.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
