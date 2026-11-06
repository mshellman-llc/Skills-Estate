---
name: design-software-system
description: 'Produce a fast, unbranded working design for a new system, service, API, or data architecture, usually inline. Covers requirements, components, data flow, data model, API contracts, storage, caching, queues, scaling, reliability, capacity, and explicit trade-offs. Use when someone asks how to build or structure a new product or service, how it will scale, which database, cache, queue, or API style fits, or wants component boundaries explored before decisions are formalized. Do NOT use for reviewing existing code, capturing one already-made decision as a short ADR. For a formal sourced architecture document, use the formal architecture reference mode and its write-architecture-reference workflow.'
---


# Design software system

> **Before writing: [`build-card.md`](../_shared/build-card.md) plus
> [`readout-brief.md`](../writing-diagnostics/references/registers/readout-brief.md). Inputs, not a final pass.**

Design systems and evaluate architectural choices. Lead with a recommended design, then show the reasoning and the trade-offs behind it.

## Ground rules

- When extending an existing system, inspect the supplied implementation, contracts and operating evidence first. State what was inspected and what remains unavailable; proposed extensions must respect confirmed behavior. This design inspection does not imply a completed code review.
- State assumptions before you design on them. If scale, latency, budget, or team constraints were not given, say what you are assuming and mark it. Do not invent load figures, SLAs, or user counts and present them as fact.
- Every choice has a cost. Name the trade-off you accept with each decision, not just the benefit.
- Simplest design that meets the stated requirements wins. Add mechanism only when a requirement forces it.

## When NOT to use

- Reviewing or debugging code that already exists.
- Recording one decision that is already made. That is an ADR, not a design.

For a formal sourced reference, select the formal architecture reference mode
and read [write-architecture-reference](../write-architecture-reference/SKILL.md). It preserves source
locators, the selected project profile, complementary architecture and engineering
views, and artifact review. The portable System Design package embeds that workflow.
The framework below covers exploratory working design; it does not replace the
formal mode or its acceptance checks.

## Framework

Walk these in order. Skip a section only when it plainly does not apply, and say so.

### 1. Requirements
- Functional: what it must do.
- Non-functional: scale, latency, availability, durability, cost.
- Constraints: team size, timeline, existing stack, compliance.
- If any of these are unknown, ask or assume-and-mark before proceeding.

### 2. High-level design
- Components and their responsibilities.
- Data flow between them.
- API contracts, data ownership and state changes at the boundaries.
- Identity and authorization: principals, relevant tenant or isolation key, allowed actions, enforcement location, and denial behavior. Tenant isolation does not establish permission to act on a record. Require every applicable identity, tenant, ownership or explicit grant check; deny when a required check fails or the governing policy is unavailable. Do not claim a tenant filter compensates for a missing permission check.
- Storage choices per component.

### 3. Deep dive
- Data model: entities, keys, relationships, access patterns.
- API endpoints: shape, method, idempotency (REST, GraphQL, or gRPC as fits).
- Caching: what, where, invalidation, staleness tolerance.
- Async: queues, events, ordering, delivery guarantees.
- Failure handling: timeouts, retries with backoff, idempotency keys, dead-letter paths. A read of completed state followed by a write does not prevent concurrent duplicate work. Specify the atomic claim or uniqueness constraint, idempotent state change, and treatment of external side effects before claiming a redelivery is safe. State any remaining failure window; do not promise exactly-once effects without supporting evidence. A failed claim does not prove work is complete. Distinguish completed, busy and expired claims; do not acknowledge unfinished work unless a separate durable recovery trigger has accepted responsibility. Otherwise defer or retry delivery under the queue contract. State what restarts work if the current owner dies.

### 4. Scale and reliability
- Load estimate: request rate, data volume, growth. Show the arithmetic.
- Scaling approach: horizontal vs vertical, statefulness, partitioning.
- Redundancy and failover: single points of failure and how they are removed.
- Observability: the metrics, logs, and alerts that would catch a problem first.

### 5. Trade-off analysis
- List the decisions that could reasonably have gone another way.
- For each: the alternative, why it lost, and the condition under which it would win.
- Weigh complexity, cost, team familiarity, time to market, maintainability.

## Output

Produce a structured design: recommendation first, then components, data model, APIs, scaling, and trade-offs. Include a diagram (ASCII, or described in words if ASCII is too coarse). State assumptions explicitly and flag them. Close with what you would revisit as the system grows, and the earliest signal that would trigger each revisit.

Write the design to a file when a working filesystem is available and the user wants an artifact. In an ephemeral or hosted environment where writes will not persist, deliver the full design inline in the reply instead.

## Release gate (required)

Before you deliver, run the gate. This is a required step, not a suggestion. Full
spec in [`release-gate.md`](../_shared/release-gate.md).

1. Apply review-writing to the prose. Use the bundled diagnostic tools to check saved writing. For
   a final artifact it emits a receipt the quality gate requires.
2. Run review-deliverable before you call it final.

Do not present the artifact as finished until both checks have passed.
