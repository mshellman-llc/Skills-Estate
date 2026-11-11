# Solution Brief semantic component library v0.2

These are semantic components, not mandatory sections. Select them after the
evidence gate from the normalized solution graph. Never render them all through
one generic card grammar.

| ID | Component | Audience task | Primary graph entities | Renderer grammar |
| --- | --- | --- | --- | --- |
| SB-C01 | Technical judgment | Know whether the solution is deliverable and under which conditions | ADRs, interfaces, risks, conditions, milestones | Decision and condition statement |
| SB-C02 | Engagement frame | Understand the client problem, objective, and artifact purpose | Engagement, problem, outcome, audience | Editorial lede and fact rail |
| SB-C03 | Solution-at-a-glance | Understand one responsibility per technical surface | Systems, responsibilities, scope | Responsibility ledger |
| SB-C04 | Scope boundary | See included, excluded, conditional, and future work | Scope, exclusions, assumptions, financial lines | Four-state scope matrix |
| SB-C05 | Phase roadmap | Understand sequence, deferral, and gates | Phases, milestones, scope, financial lines | Phased roadmap |
| SB-C06 | Operational problem flow | See current work and embedded breakpoints | Processes, actors, systems, pain | Swimlane with break markers |
| SB-C07 | Current-to-future trace | See which capability closes each break | Pain, capability, scope, systems | Before/after trace matrix |
| SB-C08 | System landscape | Know what stays, changes, connects, and owns each responsibility | Systems, disposition, ownership | Layered system map |
| SB-C09 | Access and dependency gate | Know what blocks work and who closes it | Dependencies, systems, milestones, owners | Gate table aligned to phases |
| SB-C10 | Architecture principles | Understand design rules that constrain choices | Principles, systems, interfaces, ADRs | Principle ledger |
| SB-C11 | End-to-end data flow | Trace critical objects and events across boundaries | Systems, interfaces, payloads, events | Directed system/data flow |
| SB-C12 | Critical interface sequence | Understand ordered exchanges and failure behavior | Interfaces, triggers, systems, failure paths | Sequence diagram with failure branches |
| SB-C13 | Interface inventory | See direction, trigger, contract state, and owner for every interface | Interfaces and endpoints | Dense interface table |
| SB-C14 | ADR set | Know what was decided, why, what remains open, and what it affects | ADRs, alternatives, affected entities | Expandable ADR register |
| SB-C15 | Role and responsibility model | Understand why each role is technically required | Roles, skills, systems, interfaces, scope | Role-to-ownership matrix |
| SB-C16 | Phase allocation | See when roles are active and where effort peaks | Allocations, roles, phases, milestones | Staffing Gantt or heatmap |
| SB-C17 | Effort distribution | Understand where effort concentrates | Workstreams, scope, allocations, hours | Proportional bars or treemap |
| SB-C18 | Staffing-change rationale | Understand why the model changed with scope or architecture | Role changes, ADRs, scope versions | Change rationale ledger |
| SB-C19 | Investment reconciliation | Verify scope, effort, staffing, timing, and price coherence | Financial lines, scope, roles, phases, controls | Reconciliation table and variance control |
| SB-C20 | Exclusions and unpriced work | Know what the baseline does not fund | Exclusions, future work, financial lines | Excluded-work ledger |
| SB-C21 | Risk concentration | See where exposure attaches and whether mitigation is real | Risks and affected technical/delivery entities | Risk table plus architecture/timeline overlay |
| SB-C22 | Conditions and if-false consequences | Understand what the plan stands on and what changes when false | Assumptions, dependencies, affected entities | Conditional logic ledger |
| SB-C23 | Deal and decision journey | Understand which decisions changed the current baseline | Events, ADRs, scope and quote versions, milestones | Annotated decision timeline |
| SB-C24 | Stakeholder authority terrain | Know who decides and owns technical gates and dependencies | Stakeholders, authority, risks, systems, milestones | Authority map or responsibility matrix |
| SB-C25 | Latest technical exception | Understand a new scenario that changed the recommendation | Scenario, ADRs, systems, data objects | Focused exception brief |

## Canonical editorial views

Views project graph entities. They do not copy data into a second truth store.

- Technical judgment: SB-C01 and SB-C02
- System boundary: SB-C03, SB-C04, SB-C08, SB-C09, SB-C10
- Critical interfaces and failure behavior: SB-C11, SB-C12, SB-C13
- Architecture decisions: SB-C14 and material SB-C25
- Scope-to-solution trace: SB-C04, SB-C05, SB-C06, SB-C07
- Risk concentration: SB-C21 and SB-C22 projected onto affected entities
- Staffing and delivery shape: SB-C15 through SB-C18
- Timeline and decision gates: SB-C05, SB-C09, SB-C23
- Financial reconciliation: SB-C19 and SB-C20
- Conditions and next action: SB-C01, SB-C09, SB-C22, forward-looking SB-C23

The same ADR may appear in several views by reference. Do not restate it by hand.
The same scope item may appear in the boundary, roadmap, staffing, and financial
views because all four project the same graph relationships.

## Ownership boundaries

Solution Brief owns technical deliverability, system and interface logic, ADRs,
scope-solution trace, failure behavior, technical risks and conditions, staffing
feasibility, phase logic, and financial traceability.

Deal Desk owns approval of margin, rate, discount, capacity, commercial terms,
commercial protections, and acceptance of staffing economics. The Solution
Brief may expose the reconciled baseline and causal technical changes; it cannot
approve the commercial position.

Sales-to-Delivery Handoff owns signed inheritance, contract-versus-current-intent
deltas, inherited approval conditions, safe-start access, and week-one
validation. The Solution Brief may identify technical decision and dependency
owners; it does not perform onboarding.

## Hard fail

A renderer that emits every component as a heading, one sentence, status
metadata, and an evidence chip has failed even if every phrase is present.
