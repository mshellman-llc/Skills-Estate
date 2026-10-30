# Project Charter: Northwind Revenue Cloud build

Synthetic test fixture. Names, figures, dates and project facts are example inputs, not a real engagement.

Prepared by Example Delivery Team for Northwind Traders. Drafted 2026-08-10 by the Program Lead.
Status: DRAFT until the Sign-off section carries the client signature block.

## Engagement summary

Northwind Traders is replacing spreadsheet-based quoting with Revenue Cloud so pricing survives
the life of a program. The example delivery team delivers the configuration, two integrations, and a clean-source
data migration over fourteen weeks.

| Field | Value | Source |
|---|---|---|
| Client | Northwind Traders | SOW-2026-014 |
| SOW id | SOW-2026-014 | signed SOW |
| Delivery model | Agile | SOW-2026-014, confirmed by the Program Lead on 2026-08-08 |
| Start date | 2026-08-24 | SOW-2026-014 |
| Duration | 14 weeks | SOW-2026-014 |
| Commercial structure | Fixed fee | SOW-2026-014 |

## Scope baseline

Source: SOW-2026-014, as of 2026-08-01

The scope below restates the signed SOW and is the baseline the project is measured against.

### In scope

| # | Workstream | Description (SOW language) | Testable against |
|---|---|---|---|
| 1 | Revenue Cloud configuration | Configure product catalog, pricing, and quote flows for the NA sales team | UAT scripts per approved requirements |
| 2 | ERP integration | Bidirectional order sync with NetSuite | SIT test plan |

### Out of scope

| # | Item | SOW reference |
|---|---|---|
| 1 | CPQ amendment migration | SOW-2026-014 section 4.2 |

### Flagged deltas

| Flag | Expectation heard | What the SOW says | Heard from / where | Owner | Resolve by |
|---|---|---|---|---|---|
| F-001 | Client expects EMEA quote flows in phase one | NA sales team only | handoff transcript 2026-08-05 | Program Lead (PMO) | 2026-08-20 |

## Delivery model

Agile, per the SOW variant, confirmed by the Program Lead with the client sponsor on 2026-08-08.
Two-week sprints inside the phase-gated lifecycle, demo at each sprint close, backlog ordered with
the client product owner.

## Team and allocations

Source: SOW-2026-014 estimate and the accepted handoff brief, as of 2026-08-01

| Role | Named owner | Allocation | Source |
|---|---|---|---|
| CSE | Synthetic Commercial Owner | 10% | handoff brief |
| Program Lead (PMO) | Synthetic Project Owner | 50% | handoff brief |
| Solution Lead | Synthetic Technical Owner | 75% | handoff brief |
| BA | Synthetic Analyst | 100% | handoff brief |

Client-side counterparts:

| Role | Named owner | Function |
|---|---|---|
| Executive sponsor | Synthetic Sponsor | VP Revenue Operations |

## RACI

| Activity | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| Project plan and schedule | Program Lead (PMO) | CSE | Solution Lead | Executive sponsor |
| Requirements ownership | Solution Lead | Solution Lead | Program Lead (PMO) | CSE |
| Solution design | Solution Lead | Solution Lead | CSE | Executive sponsor |
| Status reporting | Program Lead (PMO) | Program Lead (PMO) | CSE | Executive sponsor |
| Change control | Program Lead (PMO) | CSE | Solution Lead | Executive sponsor |

## Governance and cadence

| Ceremony | Frequency | Owner | Attendees | Output |
|---|---|---|---|---|
| Weekly status | Weekly, Thursday | Program Lead (PMO) | Both teams | Status report |
| Steering committee | Monthly | CSE | Sponsors and leads | Decisions logged as DEC items |
| Sprint demo | Every two weeks | Solution Lead | Both teams | Demo notes |

Escalation path: Program Lead to CSE to client sponsor. Artifacts live in the shared Northwind
Drive folder.

## Phase plan and milestones

Source: SOW-2026-014, as of 2026-08-01

| Phase | Weeks | Exit gate | Gate owner |
|---|---|---|---|
| 01 Mobilize | 1-2 | Project Charter signed | Program Lead (PMO) |
| 02 Analyze | 3-4 | Requirements Document co-signed | BA |
| 03 Design | 5-6 | Solution Design Document co-signed | Solution Lead |
| 04 Build | 7-11 | Build complete in sandbox | Solution Lead |
| 05 Validate | 12-13 | Go / no-go co-signed | Program Lead (PMO) |
| 06 Deploy | 14 | Go-Live Acceptance and Hypercare Closeout | Program Lead (PMO) |

## Assumptions and open items

| ID | Type | Item | Owner | Resolve by | Gate blocked |
|---|---|---|---|---|---|
| A-001 | Assumption | NetSuite sandbox mirrors production schema | Solution Lead | 2026-08-28 | Design |
| R-001 | Risk | EMEA expectation delta (F-001) widens scope pressure | Program Lead (PMO) | 2026-08-20 | Charter sign-off |

## Sign-off

| Party | Name | Role | Signature | Date |
|---|---|---|---|---|
| Northwind Traders | Synthetic Sponsor | Executive sponsor | | |
| Example Delivery Team | Synthetic Commercial Owner | CSE | | |
