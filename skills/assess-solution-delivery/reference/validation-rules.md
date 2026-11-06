# Solution Brief graph and adequacy rules

## Full artifact gate

A full Solution Brief requires Sufficient or explicitly valid Conditional
coverage across:

- scope boundary
- system ownership
- critical interfaces
- ADRs
- failure behavior
- risks, assumptions, and dependencies
- staffing feasibility
- timeline and gates
- financial traceability
- technical approval conditions

Insufficient is terminal. Produce a compact Technical Readiness Memo and stop
before graph assembly or rendering.

Conditional is valid only when every conditional item has an owner, closure
condition, affected graph entities, and a rule blocking dependent work.

## Normalized entity families

The graph stores systems, interfaces, ADRs, scope items, risks, assumptions,
dependencies, roles, allocations, phases, milestones, financial lines, and
reconciliation controls. Every load-bearing node references governed claim IDs.

Relationships are typed edges. They preserve ownership, implementation,
dependency, governance, risk, staffing, phase, price, exclusion, and closure
logic. Prose proximity is not a relationship.

## Required validations

The standalone validator rejects:

- duplicate or missing IDs
- dangling and incompatible edges
- undeclared claim references
- load-bearing interfaces without failure paths
- build-reference interfaces without approved contracts or explicit blocks
- ADRs without affected entities or decision points
- included scope without solution, phase, role, and financial trace
- excluded scope contributing to the baseline
- risks without owner, affected entity, mitigation, trigger, and residual risk
- assumptions and dependencies without owner, affected entity, consequence, and
  closure condition
- allocations that fail to join a role, phase, scope, and milestone window
- phases without observable exits
- failed or inconsistent reconciliation controls
- missing canonical editorial views
- fewer than five semantic grammar families for a rich artifact
- the rejected generic-claim-card grammar
- a rich graph missing systems, interfaces, ADRs, scope, staffing, phases,
  financials, reconciliation, or typed relationships

## Approval versus build-reference mode

Approval mode may compress detail but must preserve the critical path, open ADRs,
load-bearing interfaces, failure behavior, staffing feasibility, timeline gates,
financial reconciliation, and conditions.

Build-reference mode requires approved interface contracts or explicit blocks on
dependent work, detailed failure sequences, phase-level allocations, acceptance
criteria, and work-prohibition rules. It cannot invent implementation precision.

## Adequacy, not volume

Do not benchmark a result by word count. Evaluate:

- entity-family coverage
- relationship coverage
- canonical-view coverage
- semantic-grammar diversity
- audience-task completion
- evidence coverage
- reconciliation status

A short artifact can be adequate. A long artifact can still be empty. A rich
artifact that has zero system maps, zero interface grammar, zero ADR grammar,
zero staffing or timeline grammar, and zero reconciliation grammar fails before
visual review.
