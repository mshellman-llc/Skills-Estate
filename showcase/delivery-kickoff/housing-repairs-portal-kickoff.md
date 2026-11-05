---
skill: delivery-kickoff
title: Mobilizing a housing repairs portal engagement from an accepted handoff
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: c60d6b255027410268c1b7c8562722d127c380d9435c4851c5817d6f525ac0af
---

## Request

The handoff for the Brackenfield repairs portal has been accepted and the SOW is signed. Please mobilize the engagement: draft the project charter and seed the RAID and decision logs from the attached handoff brief and SOW extract. Internal kickoff is next week.

## Inputs

Run of the built `delivery-kickoff` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### handoff-brief.md

#### Accepted handoff brief: Brackenfield Housing Association (accepted 2026-10-28)

**Company.** Brackenfield Housing Association manages about 6,800 social homes. Revenue is rent and service charges. Repairs are taken by phone and logged in a legacy spreadsheet-and-database tool; tenants complain they cannot see repair status.

**Team.** CSE Priya Raman (20%). Program Lead Tomas Weber (50%). Solution Lead Ines Okafor (60%).

**Stakeholders.** Executive sponsor Gareth Lindqvist (Chief Operating Officer) led the deal but will not attend delivery meetings; he delegated day-to-day to Hana Mbeki (Head of Customer Services, product owner). IT is one person, Sam Adeyemi (IT Manager), who also administers the Fieldline contractor scheduler.

**Sell-cycle promises.**
- Gareth, 2026-09-18 call: "Tenants will get text reminders before every repair visit."
- Priya to Hana, 2026-09-30 email: "Go-live before the January winter-repairs peak."

**Scope and risks.**
- Fieldline scheduler integration depends on a vendor API key that Sam has not yet requested.
- Sam is the only person who can grant Fieldline and legacy database access (single point of failure).
- Legacy repair data quality is unknown; Hana expects "some duplicates".

**Open questions.**
1. Who owns the legacy repair data and signs off the migration mapping? (Priya, raised in discovery; no date)
2. Has the Fieldline vendor confirmed API access on Brackenfield's licence tier? (Tomas)
3. Will Gareth attend steering committees, or does Hana hold his proxy? (Priya)
4. Where will project notes and documents live? (no owner)

**Risk profile note.** Brackenfield has not run a data migration or vendor API integration before (self-reported by Sam, discovery call 2026-09-22). Agreed oversight: Solution Lead reviews the mapping and API test results.

#### sow-extract.md

#### SOW extract: SOW-BHA-2026-014 (Waterfall variant), signed 2026-10-12

Client: Brackenfield Housing Association. Delivery: Cobalt Ridge Consulting. Engagement: Repairs Portal. Start 2026-11-16, 20 weeks, fixed fee.

##### 2. Scope
1. **Repairs case management.** Case records, triage rules and status workflow for repair requests. Tested by UAT scripts agreed in Analyze.
2. **Tenant self-service portal.** Tenants log in, report a repair and view its status. Tested by UAT scripts.
3. **Fieldline integration.** One integration that sends appointments to Fieldline and receives completion status. Tested by an end-to-end test in the sandbox.
4. **Data migration.** Repair history for the last 3 years (basis of estimate: about 42,000 records) loaded once. Tested by reconciliation counts signed by the client.

##### 4. Exclusions
4.1 Contractor mobile app. 4.2 Migration of records older than 3 years. 4.3 SMS or email notifications to tenants. 4.4 Integration with the rent accounts system. 4.5 Training beyond two sessions.

##### Exhibit A: basis of estimate
A1: legacy data is in one database with a documented schema. A2: Brackenfield provides Fieldline API credentials by Analyze week 1. A3: client reviewers return deliverables within 5 working days.

##### Phases (weeks)
Mobilize 1-2 (gate: Charter signed). Analyze 3-6 (Requirements co-signed). Design 7-9 (Design co-signed). Build 10-15 (Build complete in sandbox). Validate 16-18 (Go/no-go). Deploy 19-20 (Go-Live Acceptance).

## Output

### Repairs Portal: charter draft and governance pack ready for internal kickoff

I've drafted the Project Charter and seeded the RAID log and decision log from the accepted handoff brief (2026-10-28) and SOW-BHA-2026-014 (signed 2026-10-12). The charter is marked DRAFT. Nobody has signed it and nobody has confirmed anything, so the file records no confirmations.

#### Two things to settle before client kickoff

1. **F-001: text reminders.** Gareth Lindqvist told the team on 2026-09-18 that "tenants will get text reminders before every repair visit." SOW clause 4.3 excludes SMS and email notifications. I did not add it to the baseline or drop it. Priya Raman owns it, due 2026-11-12. If the client wants it, that is a Change Order conversation for the humans.
2. **F-002: go-live date.** Priya told Hana Mbeki on 2026-09-30 that go-live would come before the January winter peak. A 2026-11-16 start with 20 weeks puts Deploy in weeks 19 and 20, ending 2027-04-02. Same owner and date. R-006 is its companion risk.

#### What was produced

| File | Contents |
|---|---|
| `out/project-charter-DRAFT.md` | Nine-section charter, scope restated from the SOW with its source stamp, 2 flagged deltas, RACI, proposed cadence, phase plan |
| `out/raid-log.md` | 6 risks, 6 assumptions, 0 issues, 5 dependencies, each with owner, date, gate blocked and source |
| `out/decision-log.md` | Opened with no rows, because no named person has made a decision yet |
| `out/mobilization-plan-and-backlog-seed.md` | Nine-item mobilization plan with owners and dates, sandbox and access tracker, four epics and two discovery stories |

#### Charter key content

- **Engagement:** Brackenfield Housing Association, Repairs Portal, fixed fee, start 2026-11-16, 20 weeks, waterfall.
- **In scope:** repairs case management; tenant self-service portal; one Fieldline integration; one-time migration of 3 years of repair history (about 42,000 records).
- **Out of scope (clauses 4.1 to 4.5):** contractor mobile app; records older than 3 years; SMS or email notifications; rent accounts integration; training beyond two sessions.
- **Team:** Priya Raman (CSE, 20%), Tomas Weber (Program Lead, 50%), Ines Okafor (Solution Lead, 60%). Client side: Gareth Lindqvist (sponsor), Hana Mbeki (product owner), Sam Adeyemi (IT).
- **Phases:** Mobilize weeks 1-2, Analyze 3-6, Design 7-9, Build 10-15, Validate 16-18, Deploy 19-20, each with its SOW exit gate.
- **Cadence (proposed, not agreed):** weekly status on Thursdays, monthly steering, demo and gate review at each phase boundary.

#### RAID seeding

All four handoff open questions became owned items:

| Handoff open question | RAID item | Owner | Due |
|---|---|---|---|
| 1. Legacy data owner | D-003 | Priya Raman | 2026-11-12 (the brief gave no date) |
| 2. Fieldline API on the licence tier | D-001 | Tomas Weber | 2026-11-12 |
| 3. Sponsor attendance and proxy | R-001 | Priya Raman | 2026-11-12 |
| 4. Where documents live | A-001 | Tomas Weber (default, brief had no owner) | 2026-11-12 |

The rest came from the brief and SOW:
- **Handoff risks:** R-002 (Sam Adeyemi as single point of failure) and R-003 (unknown data quality).
- **Capability gap:** R-004, no prior migration or API integration experience, from the self-reported discovery call, with the agreed oversight of the Solution Lead reviewing the mapping and API tests.
- **Flagged deltas:** R-005 and R-006.
- **SOW basis of estimate:** A-003 to A-006.
- **Mobilization gaps:** D-002 (the API key has not been requested), D-004 (sandbox) and D-005 (charter signatory).

#### Gate results

`charter_check.py` can't run in this session, so I applied its six checks by hand against the saved file. This is a manual read, not a script run. Please run the script before anyone signs.

| Check | Result |
|---|---|
| required-sections | Pass: 9 of 9 present |
| scope-stamp | Pass: `Source: SOW SOW-BHA-2026-014, as of 2026-10-12` |
| raci-filled | Pass: 9 activities, every cell filled, one Accountable each |
| raci-coverage | Pass: CSE, Program Lead and Solution Lead all appear |
| placeholders | Pass: 0 template tokens, TBD or TODO |
| em-dash | Pass: 0 found |

The writing-integrity checker is also unavailable here. I did a manual read of the prose for filler and forced contrasts instead.

#### Assumptions and gaps

- **Delivery model not confirmed.** Waterfall comes from the SOW variant. The charter says so and A-002 tracks it. Tomas or Priya needs to confirm it, and the confirmation then goes into the decision log as DEC-001.
- **Evidence-core is not installed.** The manual substitute is that every charter fact traces to the two inputs, with the source in each row.
- **Dates are proposals.** The 2026-11-12 resolve-by date is my default of "before client kickoff", and the week-of-2026-11-09 internal kickoff is taken from your "next week". Week-start dates are plain calendar arithmetic with no holiday adjustment.
- **No signatory names.** Neither party's signatory appears in the inputs, so the sign-off blocks are empty and D-005 tracks the client's.
- **Sandbox and access are unverified.** The tracker marks nothing ready, because no source shows any provisioning.
- **Decks and research pack not built.** Both kickoff decks go through deck-builder, and I have not made them. The content contract is ready: the internal deck should lead with R-001 to R-006 and F-001 and F-002. The client research pack was left out as the first item to cut. The client deck's risk slide should show the client-safe subset only.

#### Needs a human next

1. Tomas or Priya confirms the delivery model.
2. The team agrees the document location at internal kickoff.
3. Priya resolves F-001 and F-002 with the client before 2026-11-12.
4. Tomas secures the charter signature, targeted at the end of Mobilize week 2 (2026-11-27). Once it lands, `charter_signed` is recorded in DELIVERY-STATE.md.

### File: decision-log.md

#### Decision log: Repairs Portal (SOW-BHA-2026-014)

Opened at Mobilize by delivery-kickoff, as of 2026-11-04.
Stewarded from here by delivery-status. IDs are permanent: never renumber, never reuse.

ID convention: DEC-### in creation order, zero-padded to three digits. DEC, not D, so decision IDs
never collide with the RAID log's dependency IDs.

A decision is logged when a human makes it, with the human named in Made by. This log records
decisions; it never contains a decision an agent made on the humans' behalf. A pending decision is
an open question in the RAID log (usually an A or D item), not a pre-filled row here.

Status values: Proposed, Decided, Superseded. A superseded decision keeps its row; the new row
names the old ID in Supersedes.

No decision has been made by a named person as of 2026-11-04. The three expected first entries are
tracked as open RAID items: delivery model confirmation (A-002), document location (A-001), and
cadence (proposed in the charter, agreed at client kickoff).

| ID | Decision | Date | Made by | Rationale | Options considered | Source | Status | Supersedes |
|---|---|---|---|---|---|---|---|---|

### File: mobilization-plan-and-backlog-seed.md

#### Mobilization plan and backlog seed: Repairs Portal (SOW-BHA-2026-014, as of 2026-10-12)

Waterfall engagement, so Sprint 0 content is the mobilization plan. Dates are proposed; none is agreed.

##### Mobilization plan

| # | Item | Owner | Date | Status |
|---|---|---|---|---|
| 1 | Confirm waterfall and record the confirmation as a DEC entry (A-002) | Tomas Weber | 2026-11-10 | Not started |
| 2 | Hold internal kickoff, with the risk and gap review off the RAID log | Tomas Weber | Week of 2026-11-09 | Not scheduled |
| 3 | Agree where documents live; log as a DEC entry (A-001) | Tomas Weber | 2026-11-12 | Not started |
| 4 | Disposition F-001 and F-002 with the client sponsor before client kickoff | Priya Raman | 2026-11-12 | Not started |
| 5 | Confirm sponsor proxy, data owner and charter signatory (R-001, D-003, D-005) | Priya Raman | 2026-11-12 | Not started |
| 6 | Fieldline API access confirmed and key requested (D-001, D-002) | Tomas Weber, Sam Adeyemi | 2026-11-12, 2026-11-20 | Not started |
| 7 | Sandbox and access tracker (below) | Tomas Weber | 2026-11-30 | Nothing verified |
| 8 | Schedule Analyze requirements sessions with Hana Mbeki's team (scheduling only) | Ines Okafor | 2026-11-20 | Not started |
| 9 | Hold client kickoff; charter to signature | Tomas Weber | 2026-11-16 to 2026-11-27 | Not scheduled |

Sandbox and access tracker: Cobalt Ridge sandbox, unverified. Fieldline test access for the team, not requested. Legacy database read access for Ines Okafor, not requested (Sam Adeyemi controls it). Nothing is marked ready.

##### Backlog seed (projection of the SOW scope; no sizing, no acceptance criteria)

| ID | Item | Description | Source | Testable against | Tags |
|---|---|---|---|---|---|
| E-001 | Data migration | Repair history for the last 3 years loaded once | SOW section 2, item 4 | Client-signed reconciliation counts | Early discovery (R-003, R-004) |
| E-001-S-01 | Migration discovery | Profile legacy data and draft the mapping for the data owner to sign | Handoff risks; D-003 | Mapping signed by the named data owner | R-003, R-004 |
| E-002 | Fieldline integration | Send appointments, receive completion status | SOW section 2, item 3 | Sandbox end-to-end test | Early discovery (D-001, R-004) |
| E-002-S-01 | API access discovery | Confirm licence tier, credentials and test endpoint | Handoff scope and risks | Access verified by the Solution Lead | D-001, D-002 |
| E-003 | Repairs case management | Case records, triage rules, status workflow | SOW section 2, item 1 | UAT scripts agreed in Analyze | |
| E-004 | Tenant self-service portal | Login, report a repair, view status | SOW section 2, item 2 | UAT scripts agreed in Analyze | |

Stories under E-003 and E-004 are not seeded: the SOW and brief name no objects or deliverables to split on. Requirements capture in Analyze owns that breakdown.

### File: project-charter-DRAFT.md

#### Project Charter: Repairs Portal

Prepared by Cobalt Ridge Consulting for Brackenfield Housing Association. Drafted 2026-11-04 by the delivery kickoff author for the Program Lead.
Status: DRAFT until the Sign-off section carries the client signature block.
Stamp: SOW-BHA-2026-014, signed 2026-10-12. Handoff brief accepted 2026-10-28.

##### Engagement summary

Brackenfield Housing Association manages about 6,800 social homes and takes repairs by phone into a legacy tool that gives tenants no view of repair status. This engagement gives tenants a self-service portal to report a repair and follow it, gives Customer Services a case management workflow behind it, sends appointments to the Fieldline contractor scheduler, and moves three years of repair history into the new system.

| Field | Value | Source |
|---|---|---|
| Client | Brackenfield Housing Association | SOW SOW-BHA-2026-014 |
| Engagement | Repairs Portal | SOW SOW-BHA-2026-014 |
| SOW id | SOW-BHA-2026-014 | signed SOW |
| Delivery model | Waterfall (detected from the SOW variant; confirmation by the Program Lead is outstanding, see A-002) | SOW SOW-BHA-2026-014 |
| Start date | 2026-11-16 | SOW SOW-BHA-2026-014 |
| Duration | 20 weeks | SOW SOW-BHA-2026-014 |
| Commercial structure | Fixed fee | SOW SOW-BHA-2026-014 |

##### Scope baseline

Source: SOW SOW-BHA-2026-014, as of 2026-10-12

The scope below restates the signed SOW. It is the baseline the project is measured against. It is not a renegotiation surface: any difference between what the client expects and what this section says is recorded as a flagged item in the table at the end of this section, never edited into the baseline.

###### In scope

| # | Workstream | Description (SOW language) | Testable against |
|---|---|---|---|
| 1 | Repairs case management | Case records, triage rules and status workflow for repair requests. | UAT scripts agreed in Analyze |
| 2 | Tenant self-service portal | Tenants log in, report a repair and view its status. | UAT scripts agreed in Analyze |
| 3 | Fieldline integration | One integration that sends appointments to Fieldline and receives completion status. | End-to-end test in the sandbox |
| 4 | Data migration | Repair history for the last 3 years (basis of estimate: about 42,000 records) loaded once. | Reconciliation counts signed by the client |

###### Out of scope

| # | Item | SOW reference |
|---|---|---|
| 1 | Contractor mobile app | SOW section 4, clause 4.1 |
| 2 | Migration of records older than 3 years | SOW section 4, clause 4.2 |
| 3 | SMS or email notifications to tenants | SOW section 4, clause 4.3 |
| 4 | Integration with the rent accounts system | SOW section 4, clause 4.4 |
| 5 | Training beyond two sessions | SOW section 4, clause 4.5 |

###### Flagged deltas

Differences between stated client expectations and the SOW baseline. Each is a flag for the Program Lead and the CSE, not a fix. If either resolves into paid work, the route is a Change Order conversation owned by those humans.

| Flag | Expectation heard | What the SOW says | Heard from / where | Owner | Resolve by |
|---|---|---|---|---|---|
| F-001 | "Tenants will get text reminders before every repair visit." | SMS or email notifications to tenants are excluded (clause 4.3). | Gareth Lindqvist, 2026-09-18 call, handoff brief | Priya Raman (CSE) | 2026-11-12 |
| F-002 | "Go-live before the January winter-repairs peak." | 20 weeks from a 2026-11-16 start; Deploy is weeks 19 and 20, ending 2027-04-02. | Priya Raman to Hana Mbeki, 2026-09-30 email, handoff brief | Priya Raman (CSE) | 2026-11-12 |

##### Delivery model

Waterfall, as the SOW variant states. This was detected from the SOW and has not yet been confirmed by the Program Lead or the CSE; the confirmation and its date are recorded in the decision log (DEC entry) once a named person gives it. On a waterfall engagement the Requirements and Design phases each end in a client co-signature, demos fall at phase boundaries, and a change to scope goes through change control as a Change Order rather than by reordering a backlog.

##### Team and allocations

Source: SOW SOW-BHA-2026-014 estimate and the accepted handoff brief, as of 2026-10-12

| Role | Named owner | Allocation | Source |
|---|---|---|---|
| CSE | Priya Raman | 20% | handoff brief |
| Program Lead (PMO) | Tomas Weber | 50% | handoff brief |
| Solution Lead | Ines Okafor | 60% | handoff brief |

Client-side counterparts:

| Role | Named owner | Function |
|---|---|---|
| Executive sponsor | Gareth Lindqvist (COO) | Led the deal; will not attend delivery meetings. Proxy status of Hana Mbeki is unconfirmed (R-001). |
| Product owner / business lead | Hana Mbeki (Head of Customer Services) | Day-to-day client lead, delegated by the sponsor. |
| Client IT and system administrator | Sam Adeyemi (IT Manager) | Only person able to grant Fieldline and legacy database access (R-002). |

##### RACI

Every activity row carries exactly one Accountable owner. Every role in the team table above appears at least once. An empty cell is a drafting failure, not a formatting choice.

| Activity | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| Project plan and schedule | Program Lead (PMO) | CSE | Solution Lead, Product owner | Executive sponsor |
| Requirements ownership | Product owner | Solution Lead | Program Lead (PMO), Client IT | CSE, Executive sponsor |
| Solution design | Solution Lead | CSE | Product owner, Client IT | Program Lead (PMO) |
| Build | Solution Lead | Program Lead (PMO) | Client IT | CSE, Product owner |
| Testing | Product owner | Solution Lead | Program Lead (PMO), Client IT | CSE, Executive sponsor |
| Deployment and cutover | Solution Lead | CSE | Program Lead (PMO), Client IT | Product owner, Executive sponsor |
| Status reporting | Program Lead (PMO) | Program Lead (PMO) | Solution Lead | CSE, Product owner, Executive sponsor |
| Decision escalation | Program Lead (PMO) | CSE | Solution Lead, Product owner | Executive sponsor |
| Change control | CSE | Executive sponsor | Program Lead (PMO), Solution Lead | Product owner |

##### Governance and cadence

Cadence below is proposed by the delivery team. It becomes agreed when the client accepts it at client kickoff and signs this charter.

| Ceremony | Frequency | Owner | Attendees | Output |
|---|---|---|---|---|
| Weekly status | Weekly, Thursday (proposed; reporting day and audience to be agreed with the Program Lead) | Program Lead (PMO) | Product owner, Solution Lead, CSE | Status report (governance pack template) |
| Steering committee | Monthly (proposed) | CSE | Executive sponsor or confirmed proxy, Product owner, Program Lead (PMO) | Decisions logged as DEC items |
| Phase-boundary demo and gate review | At each phase exit gate | Solution Lead | Product owner, Client IT, Program Lead (PMO) | Gate co-signature where the SOW requires one |

Escalation path: Program Lead (PMO) to CSE, then to the client executive sponsor or the proxy confirmed under R-001. Decision log, RAID log, and status reports live at a location the team has not yet agreed (A-001); the agreed location will be written here and logged as a decision, and they are stewarded per the governance pack.

##### Phase plan and milestones

Source: SOW SOW-BHA-2026-014, as of 2026-10-12

Week-start dates are calendar arithmetic from the 2026-11-16 start, with no holiday adjustment.

| Phase | Weeks | Exit gate | Gate owner |
|---|---|---|---|
| 01 Mobilize | 1-2 (from 2026-11-16) | Project Charter signed | Program Lead (PMO) |
| 02 Analyze | 3-6 (from 2026-11-30) | Requirements Document co-signed | Solution Lead |
| 03 Design | 7-9 (from 2026-12-28) | Solution Design Document co-signed | Solution Lead |
| 04 Build | 10-15 (from 2027-01-18) | Build complete in sandbox | Solution Lead |
| 05 Validate | 16-18 (from 2027-03-01) | Go / no-go co-signed | CSE |
| 06 Deploy | 19-20 (from 2027-03-22) | Go-Live Acceptance and Hypercare Closeout | CSE |

##### Assumptions and open items

Assumptions the charter rests on, and the open questions inherited from the handoff brief. Every open item has an owner and a resolve-by date; the full working list lives in the RAID log with stable IDs.

| ID | Type | Item | Owner | Resolve by | Gate blocked |
|---|---|---|---|---|---|
| A-001 | Assumption | The team agrees where notes and project documents live (handoff open question 4). | Tomas Weber | 2026-11-12 | Charter signed |
| A-002 | Assumption | Waterfall is the delivery model; detected from the SOW, not yet confirmed. | Tomas Weber | 2026-11-12 | Charter signed |
| A-003 | Assumption | Legacy data sits in one database with a documented schema (SOW Exhibit A1). | Ines Okafor | 2026-12-04 | Requirements Document co-signed |
| A-004 | Assumption | Brackenfield provides Fieldline API credentials by Analyze week 1 (Exhibit A2). | Sam Adeyemi | 2026-11-30 | Requirements Document co-signed |
| A-005 | Assumption | Client reviewers return deliverables within 5 working days (Exhibit A3). | Hana Mbeki | 2026-11-30 | Requirements Document co-signed |

[trimmed: the rest of this file, about 446 more words, is not shown]

### File: raid-log.md

#### RAID log: Repairs Portal (SOW-BHA-2026-014)

Seeded at Mobilize by delivery-kickoff from the accepted handoff brief, as of 2026-11-04.
Stewarded from here by delivery-status. IDs are permanent: never renumber, never reuse.

ID conventions: R-### risks, A-### assumptions, I-### issues, D-### dependencies. Numbers are
zero-padded to three digits and assigned in creation order within each type. A closed item keeps
its row and its ID; set Status to Closed and fill Resolution. New items append at the bottom of
their table.

Status values: Open, Mitigating, Closed. Every Open item has a named owner and a resolve-by date.
An unowned item is a seeding failure, not a backlog.

##### Risks

| ID | Risk | Impact | Likelihood | Owner | Status | Resolve by | Gate blocked | Source | Resolution |
|---|---|---|---|---|---|---|---|---|---|
| R-001 | Executive sponsor Gareth Lindqvist led the deal but will not attend delivery meetings; whether Hana Mbeki holds his proxy for steering and co-signatures is unconfirmed. | H | M | Priya Raman | Open | 2026-11-12 | Charter signed | Handoff brief, stakeholders and open question 3 | |
| R-002 | Sam Adeyemi is the only person who can grant Fieldline and legacy database access; absence or delay stalls Analyze and Build. | H | M | Tomas Weber | Open | 2026-11-12 | Requirements Document co-signed | Handoff brief, scope and risks | |
| R-003 | Legacy repair data quality is unknown; the client expects "some duplicates", which could change migration effort and reconciliation. | M | H | Ines Okafor | Open | 2026-12-04 | Requirements Document co-signed | Handoff brief, scope and risks | |
| R-004 | Brackenfield has not run a data migration or vendor API integration before (self-reported, discovery call 2026-09-22). Agreed oversight: Solution Lead reviews the mapping and API test results. | M | M | Ines Okafor | Open | 2026-11-12 | Requirements Document co-signed | Handoff brief, risk profile note | |
| R-005 | Client sponsor expects text reminders before repair visits; SMS or email notifications are excluded by SOW clause 4.3. Unresolved expectation may surface as a dispute at acceptance. | H | H | Priya Raman | Open | 2026-11-12 | Charter signed | Charter F-001; handoff brief, sell-cycle promises | |
| R-006 | Client was told go-live before the January winter peak; the SOW plan has Deploy in weeks 19 and 20, ending 2027-04-02. | H | H | Priya Raman | Open | 2026-11-12 | Charter signed | Charter F-002; handoff brief, sell-cycle promises; SOW phases | |

##### Assumptions

| ID | Assumption | Basis | Owner | Status | Validate by | Gate blocked | Source | Resolution |
|---|---|---|---|---|---|---|---|---|
| A-001 | Notes, requirements and these logs will live in one location the team agrees before client kickoff. | Nobody owned this in the handoff; Program Lead assigned by default. | Tomas Weber | Open | 2026-11-12 | Charter signed | Handoff brief, open question 4 | |
| A-002 | The delivery model is waterfall. | Detected from the SOW variant; no human has confirmed it. | Tomas Weber | Open | 2026-11-12 | Charter signed | SOW header; skill Phase 0 | |
| A-003 | Legacy repair data sits in one database with a documented schema. | SOW basis of estimate. | Ines Okafor | Open | 2026-12-04 | Requirements Document co-signed | SOW Exhibit A1 | |
| A-004 | Brackenfield provides Fieldline API credentials by Analyze week 1 (2026-11-30). | SOW basis of estimate; see D-001 and D-002. | Sam Adeyemi | Open | 2026-11-30 | Requirements Document co-signed | SOW Exhibit A2 | |
| A-005 | Client reviewers return deliverables within 5 working days. | SOW basis of estimate. | Hana Mbeki | Open | 2026-11-30 | Requirements Document co-signed | SOW Exhibit A3 | |
| A-006 | Three years of repair history is about 42,000 records. | SOW basis of estimate for the migration workstream. | Ines Okafor | Open | 2026-12-04 | Requirements Document co-signed | SOW section 2, item 4 | |

##### Issues

| ID | Issue | Impact | Owner | Status | Resolve by | Gate blocked | Source | Resolution |
|---|---|---|---|---|---|---|---|---|

##### Dependencies

| ID | Dependency | Depends on | Owner | Status | Needed by | Gate blocked | Source | Resolution |
|---|---|---|---|---|---|---|---|---|
| D-001 | Confirmation that Brackenfield's Fieldline licence tier includes API access. | Fieldline vendor | Tomas Weber | Open | 2026-11-12 | Requirements Document co-signed | Handoff brief, open question 2 | |
| D-002 | Request for the Fieldline vendor API key, not yet made. | Sam Adeyemi | Sam Adeyemi | Open | 2026-11-20 | Requirements Document co-signed | Handoff brief, scope and risks | |
| D-003 | A named owner of the legacy repair data who signs off the migration mapping. | Brackenfield (Hana Mbeki to nominate) | Priya Raman | Open | 2026-11-12 | Requirements Document co-signed | Handoff brief, open question 1 (raised in discovery, no date given; date set at seeding) | |
| D-004 | Sandbox environment and named-user access provisioned and verified. No source records any provisioning; status is unverified. | Cobalt Ridge platform administration and Sam Adeyemi | Tomas Weber | Open | 2026-11-30 | Build complete in sandbox | SOW phase gates; skill Phase 5 | |
| D-005 | Brackenfield names its authorized charter signatory. | Brackenfield | Priya Raman | Open | 2026-11-12 | Charter signed | Charter sign-off section | |
