---
name: system-design
description: 'Produce a fast, unbranded working design for a new system, service, API, or data architecture, usually inline. Covers requirements, components, data flow, data model, API contracts, storage, caching, queues, scaling, reliability, capacity, and explicit trade-offs. Use when someone asks how to build or structure a new product or service, how it will scale, which database, cache, queue, or API style fits, or wants component boundaries explored before decisions are formalized. Do NOT use for reviewing existing code, capturing one already-made decision as a short ADR, or a formal, sourced, client-facing, Aleysian-branded architecture document (that is architecture-doc).'
---

# System Design

> **Before writing: [`build-card.md`](../_shared/build-card.md) plus
> [`readout-brief.md`](../prose-pass/references/registers/readout-brief.md). Inputs, not a final pass.**

Design systems and evaluate architectural choices. Lead with a recommended design, then show the reasoning and the trade-offs behind it.

## Ground rules

- State assumptions before you design on them. If scale, latency, budget, or team constraints were not given, say what you are assuming and mark it. Do not invent load figures, SLAs, or user counts and present them as fact.
- Every choice has a cost. Name the trade-off you accept with each decision, not just the benefit.
- Simplest design that meets the stated requirements wins. Add mechanism only when a requirement forces it.

## When NOT to use

- Reviewing or debugging code that already exists.
- Recording one decision that is already made. That is an ADR, not a design.
- An Aleysian client-facing or branded architecture document. Use
  `architecture-doc`, which sources every claim, applies brand canon during the build,
  and runs the brand and prose gates. This skill is the working-design version: faster, inline,
  unbranded, and it invents nothing about Aleysian.

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
- API contracts at the boundaries.
- Storage choices per component.

### 3. Deep dive
- Data model: entities, keys, relationships, access patterns.
- API endpoints: shape, method, idempotency (REST, GraphQL, or gRPC as fits).
- Caching: what, where, invalidation, staleness tolerance.
- Async: queues, events, ordering, delivery guarantees.
- Failure handling: timeouts, retries with backoff, idempotency keys, dead-letter paths.

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

1. Run prose-pass on the prose. It rewrites AI patterns and gates the result. For
   a final artifact it emits a receipt the quality gate requires.
2. Run quality-gate before you call it final.

Do not present the artifact as finished until both checks have passed.
