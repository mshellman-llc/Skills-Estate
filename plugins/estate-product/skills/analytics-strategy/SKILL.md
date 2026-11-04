---
name: analytics-strategy
description: "Design a measurement strategy, event tracking plan, metric definitions, or a decision-focused analytics dashboard. Use for explicit measurement design and tracking audits; calculating known metrics or drawing an existing dataset's chart does not need this workflow."
license: MIT
---


# Analytics strategy

Start with the decision the measurement should inform. Read existing metric definitions and inspect the available data. Check the project's approved data policy before selecting collection methods. Use [Measurement decisions](references/measurement-decisions.md) to define the smallest plan that answers the question.

Define each metric's calculation and eligible population. State its time window and source, with any exclusions. Use a baseline or target only when its authority is available. A missing baseline can become a measurement task; it does not prevent a proposed plan.

Select events that support those definitions. Describe each event's exact trigger and minimum properties. Give its destination and current state, with a method for validation. Include an owner and retention requirement when established; mark them pending when unknown. Prefer an existing event or aggregate source over collecting duplicate data.

Use only approved identifiers and properties. Do not default to user IDs, email addresses, IP addresses, persistent fingerprints, or identity stitching. Free text and URLs can contain personal or sensitive information. Review their contents before proposing them as properties. If consent or retention rules are unknown, keep collection choices pending and draft only the supported design. A measurement plan does not authorize new tracking, a service connection, or deployment.

Connect dashboard views to decisions and review cadence when needed. Avoid a universal SaaS funnel, compulsory north-star metric, or decorative KPI list. One well-defined metric can be sufficient for a bounded decision.

Distinguish a proposed event from an implemented one and from delivery verified at the destination. Check delivery for missing or duplicate events. Inspect payloads for unintended properties before treating the data as reliable. Do not label a template row “Live.”

Describe observational patterns as observations. Attribution assigns credit under a model; it does not establish causality. Claims about lift or intervention impact need evidence appropriate to that claim.

Deliver the requested plan with the decisions it supports and the evidence still needed. Existing privacy, source, writing, brand, and completion rules govern implementation and handoff.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
