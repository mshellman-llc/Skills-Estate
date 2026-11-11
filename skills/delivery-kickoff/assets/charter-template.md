# Project Charter: {{ENGAGEMENT_NAME}}

Prepared by Aleysian for {{CLIENT}}. Drafted {{DRAFT_DATE}} by {{AUTHOR_ROLE}}.
Status: DRAFT until the Sign-off section carries the client signature block.

## Engagement summary

{{ONE_PARAGRAPH_SUMMARY: what is being built, for whom, why now. Business outcome first, platform second. Every fact here traces to the SOW or the accepted handoff brief.}}

| Field | Value | Source |
|---|---|---|
| Client | {{CLIENT}} | SOW {{SOW_ID}} |
| Engagement | {{ENGAGEMENT_NAME}} | SOW {{SOW_ID}} |
| SOW id | {{SOW_ID}} | signed SOW |
| Delivery model | {{WATERFALL_OR_AGILE}} | SOW {{SOW_ID}}, confirmed by {{CONFIRMING_ROLE}} on {{CONFIRM_DATE}} |
| Start date | {{START_DATE}} | SOW {{SOW_ID}} |
| Duration | {{WEEKS}} weeks | SOW {{SOW_ID}} |
| Commercial structure | {{FIXED_FEE_OR_TM}} | SOW {{SOW_ID}} |

## Scope baseline

Source: SOW {{SOW_ID}}, as of {{SOW_AS_OF_DATE}}

The scope below restates the signed SOW. It is the baseline the project is measured against. It is not a renegotiation surface: any difference between what the client expects and what this section says is recorded as a flagged item in the table at the end of this section, never edited into the baseline.

### In scope

| # | Workstream | Description (SOW language) | Testable against |
|---|---|---|---|
| 1 | {{WORKSTREAM}} | {{SOW_SCOPE_TEXT}} | {{ACCEPTANCE_METHOD}} |

### Out of scope

| # | Item | SOW reference |
|---|---|---|
| 1 | {{OUT_OF_SCOPE_ITEM}} | {{SOW_CLAUSE}} |

### Flagged deltas

Differences between stated client expectations and the SOW baseline. Each is a flag for the Program Lead and the Pursuit Lead, not a fix.

| Flag | Expectation heard | What the SOW says | Heard from / where | Owner | Resolve by |
|---|---|---|---|---|---|
| F-001 | {{EXPECTATION}} | {{SOW_POSITION}} | {{SOURCE}} | {{OWNER_ROLE}} | {{DATE}} |

## Delivery model

{{DELIVERY_MODEL_PARAGRAPH: name the model (waterfall or agile) exactly as the SOW variant states it, who confirmed it and when, and what that means for cadence, demos, and acceptance rhythm on this engagement.}}

## Team and allocations

Source: SOW {{SOW_ID}} estimate and the accepted handoff brief, as of {{SOW_AS_OF_DATE}}

| Role | Named owner | Allocation | Source |
|---|---|---|---|
| CSE | {{NAME}} | {{ALLOC}} | handoff brief |
| Program Lead (PMO) | {{NAME}} | {{ALLOC}} | handoff brief |
| Solution Lead | {{NAME}} | {{ALLOC}} | handoff brief |

Client-side counterparts:

| Role | Named owner | Function |
|---|---|---|
| Executive sponsor | {{NAME}} | {{FUNCTION}} |
| Product owner / business lead | {{NAME}} | {{FUNCTION}} |

## RACI

Every activity row carries exactly one Accountable owner. Every role in the team table above appears at least once. An empty cell is a drafting failure, not a formatting choice.

| Activity | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| Project plan and schedule | Program Lead (PMO) | CSE | Solution Lead | Executive sponsor |
| {{ACTIVITY}} | {{ROLE}} | {{ONE_ROLE}} | {{ROLES}} | {{ROLES}} |

## Governance and cadence

| Ceremony | Frequency | Owner | Attendees | Output |
|---|---|---|---|---|
| Weekly status | Weekly, {{DAY}} | Program Lead (PMO) | {{ATTENDEES}} | Status report (governance pack template) |
| Steering committee | {{FREQ}} | CSE | {{ATTENDEES}} | Decisions logged as DEC items |
| {{DEMO_OR_STAGE_REVIEW}} | {{FREQ}} | Solution Lead | {{ATTENDEES}} | {{OUTPUT}} |

Escalation path: {{ESCALATION_PATH}}. Decision log, RAID log, and status reports live at {{ARTIFACT_LOCATION}} and are stewarded per the governance pack.

## Phase plan and milestones

Source: SOW {{SOW_ID}}, as of {{SOW_AS_OF_DATE}}

| Phase | Weeks | Exit gate | Gate owner |
|---|---|---|---|
| 01 Mobilize | {{WEEKS}} | Project Charter signed | Program Lead (PMO) |
| 02 Analyze | {{WEEKS}} | Requirements Document co-signed | {{ROLE}} |
| 03 Design | {{WEEKS}} | Solution Design Document co-signed | {{ROLE}} |
| 04 Build | {{WEEKS}} | Build complete in sandbox | {{ROLE}} |
| 05 Validate | {{WEEKS}} | Go / no-go co-signed | {{ROLE}} |
| 06 Deploy | {{WEEKS}} | Go-Live Acceptance and Hypercare Closeout | {{ROLE}} |

## Assumptions and open items

Assumptions the charter rests on, and the open questions inherited from the handoff brief. Every open item has an owner and a resolve-by date; the full working list lives in the RAID log with stable IDs.

| ID | Type | Item | Owner | Resolve by | Gate blocked |
|---|---|---|---|---|---|
| A-001 | Assumption | {{ASSUMPTION}} | {{OWNER}} | {{DATE}} | {{GATE}} |
| R-001 | Risk | {{RISK}} | {{OWNER}} | {{DATE}} | {{GATE}} |

## Sign-off

The charter takes effect when both signatures are present. Aleysian drafts; the client signs.

| Party | Name | Role | Signature | Date |
|---|---|---|---|---|
| {{CLIENT}} | {{NAME}} | Executive sponsor | | |
| Aleysian | {{NAME}} | CSE | | |
