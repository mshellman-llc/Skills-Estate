# The delivery stage map

The full map this suite routes against. `scripts/plan.py` carries the same table
in code; where they disagree, fix both in the same commit. The lifecycle itself
(stages, gates, acceptance methods) is Estate's codified delivery model,
recorded in the repository's delivery specifications in July 2026.

## Stages, gates, owners

| Stage | What happens | Exit gate (gate key) | Gate holder | Owning skill |
|---|---|---|---|---|
| S2D Handoff (pre-stage) | Sell-side team transfers the signed deal: handoff package at signature plus the 12-section brief | Handoff brief accepted (`brief_accepted`) | Delivery team | `s2d-handoff` |
| 01 Mobilize | Kickoff, charter, governance pack, sandbox provisioning, Sprint 0 planning, backlog seeding | Project Charter delivered and signed off (`charter_signed`) | Client | `estate-delivery-kickoff` |
| 02 Analyze | Requirements capture, process and journey mapping, integration and migration inventories, approval matrix | Requirements Document co-signed (`requirements_cosigned`) | Client | `requirements-capture` (epics, stories, Gherkin, delivery matrix) plus `journey-mapping` (process and journey maps) |
| 03 Design | Architecture and configuration design, integration design, migration plan, test plan authoring | Solution Design Document co-signed (`sdd_cosigned`) | Client | `architecture-doc` (architecture and system design docs); `solution-brief` in build-reference mode |
| 04 Build | Configuration, integration build, migration execution, iterative sprints, demos every two weeks, training materials | Build complete in sandbox (`build_complete`) | Delivery team | None by design. The build is human work; no artifact skill owns it. The status cadence continues via `delivery-status`. |
| 05 Validate | SIT, UAT, defect remediation, cutover readiness, training delivery | Go / no-go co-signed (`go_no_go`) | Client | `estate-uat-validation` (traceable test scripts, defect log, UAT tracker, go/no-go pack) |
| 06 Deploy | Production deployment, cutover, go-live monitoring | Go-Live Acceptance issued (`golive_acceptance`), on the deemed-acceptance clock from the SOW clause | Client | `cutover-closeout` (runbook, Go-Live Acceptance) |
| 06 Closeout | Two-week hypercare, support, closeout, lessons and asset harvest | Hypercare Closeout delivered (`hypercare_closeout`) | Delivery team | `cutover-closeout` (hypercare, closeout, harvest) |

## Cross-cutting, every stage from 01 Mobilize onward

| Concern | Owning skill |
|---|---|
| Weekly status, RAID and decision stewardship | `delivery-status` |
| Scope drift to change-order candidates | `delivery-status`, pricing the candidate via `sow-quality`'s Basis of Estimate framework |
| Evidence ledger for any load-bearing factual claim | `evidence-core` |
| Brand tokens, parity, visual and brand release gates | `brand-renderer` |
| Voice, on every prose deliverable, during the build | `prose-pass` |
| Every number: hours, rates, fees, timelines | The executed SOW and quote (Q-number). No skill authors a number. |

## Known gaps this suite flags rather than fills

Honesty over coverage. When a request lands on one of these, name the gap and hand
the work to a human; do not improvise a substitute.

| Gap | State as of 2026-08 |
|---|---|
| Prior-deal comparables library | Does not exist yet. The closeout harvest in `cutover-closeout` is designed to feed one. Until it exists, "what did we do on similar deals" is a human question. |
| CRM eventing | None. Nothing fires on stage change or opportunity close; every skill in this suite is user-invoked. Do not promise automation. |
| Sell-side deal governance gate tracking | No owning skill. The sales half tracks its own gates by hand; this suite starts at the signed SOW. |

## Routing edge cases

- A request that spans two stages (for example, "write the requirements and the
  design") routes to the earlier stage first; its gate blocks the later one.
- A rework request on a passed gate (the client wants requirements reopened after
  co-sign) is scope drift first: route to `delivery-status` to log it and
  assess the change-order candidate, then to the stage skill for the rework.
- Anything pre-signature (scoping, pricing, proposal, DDOC) goes to the named artifact owner. This suite begins where a signed SOW exists.
