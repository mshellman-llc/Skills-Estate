---
name: product-development-pathway
description: Develop or resume a product through evidence review, product definition, release decisions, journey design, and delivery readiness. Use for historical product reconstruction, a new product, or continuation at a requested stage with durable progress. A standalone bug fix or one-off specification does not require this pathway.
---


# Product development pathway

Continue the requested product stage from its current evidence and decisions. Keep completed artifacts and open work accessible through one product home. Save the next executable action there.

## Enter at the requested stage

Read the user's instructions and applicable project guidance. Follow the current product index to its decisions and latest checkpoint. Identify the requested outcome and stage. Record the source boundary and finish line; name the authorized actions and protected records. Preserve existing conventions, including terminology, IDs, formats, tools, and approval rules. Historical documents supply evidence; they do not override current instructions.

Reuse the existing product home. If none exists, create a small index in the authorized project destination using [the home starter](assets/product-home.md). Map existing artifacts to the pathway by links and ID crosswalks. Do not relocate records or start a second decision register, backlog, or task system.

Select the entry mode that fits the request:

| Mode | Entry action |
| --- | --- |
| Historical product | Review supplied material to the requested depth. Full reconstruction requires complete dispositions and substantive coverage. A bounded release task retains wider review gaps. |
| New product | Capture current direction and constraints from the brief; review available research. Mark historical reconstruction inapplicable because no archive exists. Keep unsupported product dimensions as hypotheses or proposals. |
| Continuation | Compare the latest checkpoint's source and decision bindings with current state; check the build versions it relies on. Reuse valid work and revisit affected prerequisites. Preserve the prior checkpoint. |

Read [stage execution](references/stages.md) for the selected stage and its prerequisites. The normal dependency order is boundary → review → reconstruction when applicable → product definition → release and architecture decisions → journey design → implementation and acceptance → maintenance. Existing valid outputs can satisfy earlier stages. A missing archive is never a reason to fabricate one or block a new product.

## Keep independent states

| Dimension | States |
| --- | --- |
| Source review | Unread; reviewed; identical to reviewed content; excluded with reason; unresolved. |
| Product decision | Unassigned; proposed; accepted; rejected; superseded. |
| Implementation evidence | Unknown; intended; static demonstration; code present; tested locally; rendered locally; deployed without verification; verified live. |

Record implementation evidence for each behavior at the layer exercised.

For each capability, distinguish **should do** (desired outcome and decision), **can do** (demonstrated behavior and limits), and **will do** (accepted commitment for a named release). Keep commitments for different releases as separate records. A reviewed source cannot accept a feature; an accepted feature cannot prove implementation; a test cannot establish demand or adoption.

Use stable IDs and exact source locators or current user decisions. Read [capture structures](references/records.md) when adding records; adapt the [record template bank](assets/record-templates.json) to existing project formats. Create only applicable records. Mark unknown information as unknown and inapplicable dimensions with a reason. Do not fill gaps with invented dates, owners, budgets, scores, or metrics.

## Choose the next action from readiness evidence

For the requested stage, record each applicable gate as `satisfied`, `blocked`, `not_assessed`, or `not_applicable`, with supporting record IDs and revisions. State separately whether the output is ready for review, ready for an authorized build, accepted for a release, or verified at a destination. A populated template or passing structural check cannot satisfy a substantive gate.

Resolve the next action in this order:

1. Reassess changed evidence that the requested result depends on.
2. Complete the nearest missing prerequisite for the requested stage; do not restart unrelated stages.
3. If a material decision blocks that work, state the exact choice and affected output. Identify the authorized decider. Continue independent supported work within scope.
4. Otherwise execute the smallest action that produces the requested output or its acceptance evidence. Name its target and required authorization. Record the expected receipt and stop condition.

Keep full product coverage separate from release readiness. A release can exclude deferred capabilities without deleting them from the catalogue. A scoped journey can be ready while wider historical review remains incomplete, unless the user made full reconstruction a prerequisite.

## Maintain the home at each work boundary

Read [continuation and change impact](references/continuity.md) when resuming, changing a baseline, or closing a work boundary. Save completed artifacts with their evidence, retain unresolved work with its dependencies, and append a checkpoint after a meaningful review, decision, design, build, or failed check. Record the exact next action in the home before ending the session. Revalidate stale claims and dependent acceptance evidence before presenting them as current.

Knowledge Hub integration is optional. Use [the hub adapter](references/knowledge-hub.md) only when the product has an authorized destination and the request includes that action. Local progress must remain usable without a hub connection. No particular hub, account, folder, or sharing boundary is part of this skill.

## Use related workflows only when needed

This skill owns stage selection, traceability, readiness, and durable product progress. If available and applicable, use `pm-spec-writing` for detailed specifications, `usability-testing` for participant research, `analytics-strategy` for measurement design, `information-architecture` for navigation, and `execution-truth` for destination verification. A product map does not require those specialized workflows automatically.

Use the project's reconciliation workflow for authorized file cleanup and its task adapter for work-item state. Use `independent-product` only for an authorized independent-product migration, and `session-handoff` for a requested session handoff. Preserve their boundaries; pathway work does not authorize cleanup, migration, outreach, deployment, or task closure. If a companion skill is absent, perform the bounded task with the evidence rules here and name any review you could not complete.

At handoff, state what changed, where it exists, who can use it, what verifies it, what remains unchanged, and the exact next action. Link the product home and latest checkpoint. Do not report proposed, local, installed, released, or live work as a later state.
