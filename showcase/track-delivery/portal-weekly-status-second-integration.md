---
skill: track-delivery
title: Weekly status with a second-integration scope drift candidate
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: d9f5fd583a023be196ed21e40f88e2dcc2c8674fe726c40c3325af5843e2c672
---

## Request

Can you do the weekly status for Brightwater for the week of 26 to 30 October? The workshop transcript, our SOW excerpt with the RAID and decision logs, and the timesheet export are in the inputs folder.

## Inputs

Run of the built `track-delivery` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### engagement-record.md

#### Brightwater customer portal: engagement record as of 2026-10-23

##### SOW-BW-2026-04 (signed 2026-08-14), excerpt

- Section 3.2: "The Services include one (1) integration, between the Portal and the Brightwater billing system."
- Exhibit A, line 4: "Integrations: 1 (billing). Any additional integration is a Binary Workstream Addition and is handled by Change Order."
- Exhibit A, line 1: "Estimate: 320 hours."
- Gate: Requirements sign-off 2026-11-13.

##### RAID log

| ID | Item | Owner | Status | Resolve-by | Gate blocked | Source |
|---|---|---|---|---|---|---|
| R-001 | Client SMEs available only two days a week | Dana Whitlock | Open | 2026-11-13 | Requirements sign-off | Priya Nandakumar, 2026-10-07 kickoff |
| R-002 | Outage-notice wording needs legal review | Priya Nandakumar | Open | 2026-11-20 | none | Kickoff 2026-10-07 |
| R-003 | Billing API documentation is out of date | Sam Okoye | Open | 2026-11-06 | Requirements sign-off | Tomas Reyes, 2026-10-14 |
| A-001 | Portal serves residential customers only | Dana Whitlock | Open | 2026-11-13 | none | SOW section 2 |
| D-001 | Client IT delivers IdP metadata file | Tomas Reyes | Open | 2026-10-28 | Requirements sign-off | Kickoff 2026-10-07 |
| D-002 | Client delivers billing API sandbox credentials | Tomas Reyes | Delivered 2026-10-21 | 2026-10-21 | none | Kickoff 2026-10-07 |

##### Decision log

| ID | Decision | Date | Made by | Rationale | Status |
|---|---|---|---|---|---|
| DEC-001 | Weekly status goes out Fridays | 2026-10-07 | Priya Nandakumar | Matches client steering rhythm | Standing |
| DEC-002 | Portal launches with email notifications only | 2026-10-14 | Priya Nandakumar | SMS needs a separate carrier contract | Standing |

##### Previous status: status-2026-10-23.md

Reported 3 risks open, 0 issues, 2 dependencies open (D-001, D-002), 1 assumption open. Scope drift: none observed. Burn: 104 h to date of 320 h. Next gate: Requirements sign-off 2026-11-13.

#### timesheet-export-2026-10-30.txt

Timesheet export, SOW-BW-2026-04, exported 2026-10-30
Week 2026-10-26 to 2026-10-30: 38.0 h
To date: 142.0 h

#### transcript-2026-10-28.md

#### Requirements workshop 2, 2026-10-28 (Brightwater customer portal)

Attendees: Priya Nandakumar (Brightwater product owner), Tomas Reyes (Brightwater IT), Dana Whitlock (Program Lead), Sam Okoye (CSE).

**Priya:** For sign-in, customers will use our existing identity provider. No separate portal passwords. That's decided.

**Dana:** Then we need the IdP metadata file to configure it.

**Tomas:** It's still with our security team. I can't promise it before 6 November.

**Priya:** When there's an outage, crews need to see it too. We'll need the portal to push outage notices into Fieldwise, our crew scheduling system. That's the same kind of thing as the billing connection, right?

**Sam:** That would be a second system on the integration side. I'll note it. I'm not saying yes or no.

**Tomas:** The billing API sandbox caps us at 60 calls a minute. Our nightly account sync might hit that.

**Priya:** We're assuming the billing account data is clean. It was cleaned in September.

**Dana:** Next session is 2026-11-04, notification templates.

## Output

The Brightwater status for 2026-10-26 to 2026-10-30 is written and held as a draft for the Program Lead. It has 4 flags, 1 scope-drift candidate and 4 proposed log entries.

#### Flags

1. **Scope-drift candidate: Fieldwise integration (hard trigger).** On 2026-10-28 Priya Nandakumar said: "We'll need the portal to push outage notices into Fieldwise, our crew scheduling system." SOW-BW-2026-04 section 3.2 says: "The Services include one (1) integration, between the Portal and the Brightwater billing system." Exhibit A line 4 treats any additional integration as a Binary Workstream Addition handled by Change Order. Sam Okoye answered in the room: "I'm not saying yes or no." The candidate is routed to the Program Lead and CSE. I have not decided whether it is in scope and have not drafted a change order. It will stay in the report until a human decision is logged.
2. **D-001 (IdP metadata) is late.** It was due 2026-10-28. Tomas Reyes said he can't promise it before 2026-11-06. It blocks Requirements sign-off on 2026-11-13.
3. **Source conflict on D-002.** The previous status listed the billing sandbox credentials as open. The RAID log says they were delivered 2026-10-21. The report follows the log and shows both.
4. **Proposed entries need your confirmation.**

#### Log changes (appended, none renumbered)

| ID | Entry | Source |
|---|---|---|
| DEC-003 | Customers sign in through the client's existing identity provider, with no separate portal passwords. Made by Priya Nandakumar. | Priya, 2026-10-28: "That's decided." |
| R-004 | The billing API sandbox cap of 60 calls a minute may be hit by the nightly sync. | Tomas Reyes, 2026-10-28 |
| A-002 | Billing account data is clean. | Priya, 2026-10-28 |
| D-003 | The client confirms whether the Fieldwise push is a requirement or a wish. | Priya, 2026-10-28 |

No decision entry was written for the Fieldwise ask, because nobody decided it. D-001 got a dated history line; its original resolve-by date was left as it was.

#### Counts and burn

- Risks: 4 open (1 new), 0 closed. Issues: 0. Dependencies: 2 open (1 new), 1 delivered earlier. Assumptions: 2 open (1 new).
- Burn: 38.0 h this period, 142.0 h to date of 320 h (44.4%), 178.0 h remaining. Source: timesheet export 2026-10-30 and Exhibit A line 1. The previous status said 104 h, and 104 + 38.0 = 142.0, so the figures reconcile.

#### Gaps and assumptions

- **Plan file:** none was supplied, so on-track or off-track status per workstream is a named gap. Owner: Program Lead.
- **DELIVERY-STATE.md:** not supplied, so I couldn't check it. No gate moved this period. Owner: Program Lead.
- **Previous status:** I reconciled against the summary in the engagement record, not the `status-2026-10-23.md` file itself.
- **Proposed fields:** the owners for R-004 and D-003 and the 2026-11-06 resolve-by on D-003 are my proposals. The transcript gives no rationale for DEC-003, and the log says so.
- **Unattended run:** with no one to confirm, the new entries are marked proposed.

#### Checks

- **Gate:** I couldn't run `status_check.py`, so I applied its rules by hand. The `Period:` line is present. Every ID in the report (R-001 to R-004, A-001, A-002, D-001 to D-003, DEC-003) is in the logs. The scope-drift section holds 1 candidate with 2 `Evidence:` lines. The burn section names a source. No placeholders remain. Result: pass, 0 failures.
- **Writing:** the writing-diagnostics diagnostics were not run. I made a manual pass for em dashes, sentence-case headings, counts instead of adjectives and a source on every line about scope, hours or dates.
- **Brand renderer:** not run. The report is Markdown only.

#### Judgment call for you

Should the Fieldwise ask be raised with Brightwater now, before D-003 is answered?

- **Raise it now:** Requirements sign-off is 2026-11-13, and a new integration changes the requirements document. Waiting costs a week.
- **Wait for D-003:** Priya phrased it as a question, so it may be a wish. Raising a change order early could harden a casual remark into a commercial position.

I'd confirm D-003 with Priya at the 2026-11-04 session first, then decide. That is your decision and the CSE's.

#### Files

- `out/status-2026-10-30.md`: the weekly status. It is the full report, so the key content above is all in it.
- `out/RAID.md`: the updated RAID log (R-004, A-002 and D-003 added, a D-001 history line, and the earlier entries left as they were).
- `out/DECISIONS.md`: the updated decision log (DEC-003 added).

### File: DECISIONS.md

#### Brightwater customer portal: decision log

| ID | Decision | Date | Made by | Rationale | Source | Status |
|---|---|---|---|---|---|---|
| DEC-001 | Weekly status goes out Fridays | 2026-10-07 | Priya Nandakumar | Matches client steering rhythm | Kickoff 2026-10-07 | Standing |
| DEC-002 | Portal launches with email notifications only | 2026-10-14 | Priya Nandakumar | SMS needs a separate carrier contract | Engagement record | Standing |
| DEC-003 | Customers sign in through the client's existing identity provider; no separate portal passwords | 2026-10-28 | Priya Nandakumar | Not stated in the transcript beyond the decision itself; Program Lead to add if known | Priya Nandakumar, 2026-10-28 workshop: "For sign-in, customers will use our existing identity provider. No separate portal passwords. That's decided." | Standing (proposed entry, awaiting Program Lead confirmation) |

### File: RAID.md

#### Brightwater customer portal: RAID log

Updated 2026-11-04 from the 2026-10-28 workshop. Entries marked proposed await confirmation by the Program Lead.

| ID | Type | Item | Owner | Status | Resolve-by | Gate blocked | Source | History |
|---|---|---|---|---|---|---|---|---|
| R-001 | Risk | Client SMEs available only two days a week | Dana Whitlock | Open | 2026-11-13 | Requirements sign-off | Priya Nandakumar, 2026-10-07 kickoff | none |
| R-002 | Risk | Outage-notice wording needs legal review | Priya Nandakumar | Open | 2026-11-20 | none | Kickoff 2026-10-07 | none |
| R-003 | Risk | Billing API documentation is out of date | Sam Okoye | Open | 2026-11-06 | Requirements sign-off | Tomas Reyes, 2026-10-14 | none |
| R-004 | Risk | Billing API sandbox cap of 60 calls a minute may be hit by the nightly account sync | Sam Okoye (proposed owner) | Open (proposed) | 2026-11-13 | Requirements sign-off | Tomas Reyes, 2026-10-28 workshop: "The billing API sandbox caps us at 60 calls a minute. Our nightly account sync might hit that." | 2026-11-04: proposed from transcript |
| A-001 | Assumption | Portal serves residential customers only | Dana Whitlock | Open | 2026-11-13 | none | SOW section 2 | none |
| A-002 | Assumption | Billing account data is clean | Priya Nandakumar | Open (proposed) | 2026-11-13 | Requirements sign-off | Priya Nandakumar, 2026-10-28 workshop: "We're assuming the billing account data is clean. It was cleaned in September." | 2026-11-04: proposed from transcript |
| D-001 | Dependency | Client IT delivers IdP metadata file | Tomas Reyes | Open | 2026-10-28 | Requirements sign-off | Kickoff 2026-10-07 | 2026-10-28: Tomas Reyes: "It's still with our security team. I can't promise it before 6 November." Resolve-by passed; client-stated earliest date 2026-11-06. |
| D-002 | Dependency | Client delivers billing API sandbox credentials | Tomas Reyes | Delivered 2026-10-21 | 2026-10-21 | none | Kickoff 2026-10-07 | none |
| D-003 | Dependency | Client confirms whether the Fieldwise outage-notice push is a requirement or a wish | Priya Nandakumar (proposed owner) | Open (proposed) | 2026-11-06 (proposed) | Requirements sign-off | Priya Nandakumar, 2026-10-28 workshop: "We'll need the portal to push outage notices into Fieldwise, our crew scheduling system." | 2026-11-04: proposed from transcript |

### File: status-2026-10-30.md

#### Brightwater : Customer portal : weekly status

Period: 2026-10-26 to 2026-10-30
Issued: draft 2026-11-04, held for Program Lead review | Prepared from: 1 transcript (2026-10-28), RAID log, decision log, timesheet export 2026-10-30
Previous status: status-2026-10-23.md | SOW baseline: SOW-BW-2026-04, signed 2026-08-14

##### Flags

1. **Candidate: second integration (Fieldwise).** Priya Nandakumar asked for outage notices to be pushed into Fieldwise on 2026-10-28. The SOW names one integration, billing. This needs a decision from the Program Lead and CSE; see Scope drift and D-003.
2. **D-001 is late.** The IdP metadata file was due 2026-10-28. Tomas Reyes said on 2026-10-28 he cannot promise it before 2026-11-06. D-001 blocks Requirements sign-off (2026-11-13), which leaves 5 working days between 2026-11-06 and the gate.
3. **Source conflict on D-002.** The previous status listed D-002 as open. The RAID log records it delivered 2026-10-21, before that status was issued. This report follows the log (signed SOW, then logs, then previous status) and counts D-002 as delivered.
4. **Proposed entries await review.** R-004, A-002, D-003 and DEC-003 were drafted from the 2026-10-28 transcript and are marked proposed. Owners for R-004 and D-003 and the resolve-by date on D-003 are proposals, not confirmed assignments.

##### Outcomes this period

- Sign-in approach is fixed: customers use the client's existing identity provider, with no separate portal passwords (DEC-003, Priya Nandakumar, 2026-10-28 workshop).
- Requirements workshop 2 was held on 2026-10-28 with 4 attendees; it produced 3 new RAID entries (R-004, A-002, D-003), 1 decision (DEC-003) and 1 scope-drift candidate (2026-10-28 transcript).

##### Plan position

Current phase: Requirements. Next gate: Requirements sign-off (2026-11-13). Source: engagement record as of 2026-10-23; the gate date is unchanged from the previous status.

Workstream on-track or off-track status is not stated: no plan file was supplied. Named gap, owner: Program Lead, resolve by next status.

##### RAID movement

Risks: 4 open (1 new: R-004), 0 closed. Issues: 0 open, 0 new. Dependencies: 2 open (1 new: D-003), 1 delivered earlier (D-002, 2026-10-21). Assumptions: 2 open (1 new: A-002), 0 invalidated.

Previous status reported 3 risks, 0 issues, 2 open dependencies and 1 assumption open. Reconciliation: R-001, R-002, R-003, A-001 and D-001 are still open and unchanged in status; D-002 is delivered per the log (see flag 3).

- R-004 (new, proposed): billing API sandbox cap of 60 calls a minute may be hit by the nightly account sync. Source: Tomas Reyes, 2026-10-28.
- A-002 (new, proposed): billing account data is clean. Source: Priya Nandakumar, 2026-10-28.
- D-003 (new, proposed): client to confirm whether the Fieldwise push is a requirement. Source: Priya Nandakumar, 2026-10-28.
- D-001 (moved): resolve-by 2026-10-28 passed; client-stated earliest date is 2026-11-06. Source: Tomas Reyes, 2026-10-28.

##### Decisions

New this period: DEC-003, customers sign in through the client's existing identity provider. Made by Priya Nandakumar on 2026-10-28. The transcript gives no rationale beyond the decision itself.

Decisions needing attention:

- Whether the Fieldwise push is in the project (D-003, blocks Requirements sign-off 2026-11-13). The decision on scope belongs to the Program Lead and CSE; the requirement question belongs to Priya Nandakumar.
- No decision has been taken on the Fieldwise ask. Sam Okoye on 2026-10-28: "I'll note it. I'm not saying yes or no."

##### Scope drift

Compared 1 transcript (2026-10-28) against SOW section 3.2 and Exhibit A (2 lines read: line 1 estimate, line 4 integrations). 1 candidate raised. No delivered work outside baseline was observed in the timesheet export, which carries hours only (no task detail).

###### Candidate: Fieldwise outage-notice integration

- Trigger class: hard
- The ask or work observed: "When there's an outage, crews need to see it too. We'll need the portal to push outage notices into Fieldwise, our crew scheduling system." (Priya Nandakumar, 2026-10-28, requirements workshop 2)
- Baseline position: SOW section 3.2: "The Services include one (1) integration, between the Portal and the Brightwater billing system." Exhibit A line 4: "Integrations: 1 (billing). Any additional integration is a Binary Workstream Addition and is handled by Change Order."
- Evidence: transcript 2026-10-28, Sam Okoye: "That would be a second system on the integration side. I'll note it. I'm not saying yes or no."
- Evidence: RAID D-003 (proposed), client confirmation of requirement versus wish outstanding.
- First observed: 2026-10-28 | Periods open: 1
- Routed to: Program Lead, CSE
- Status: raised

The ask is not yet confirmed as a requirement (Priya framed it as a question: "That's the same kind of thing as the billing connection, right?"). It is reported now because a hard-trigger ask is a leading indicator. It appears in every report until a human decision is logged.

##### Hours and burn

Burn: 38.0 h this period, 142.0 h to date of 320 h estimated (44.4%; 142.0 / 320). Remaining: 178.0 h.
Reconciliation: previous status reported 104 h to date; 104 + 38.0 = 142.0 h, matching the export.
Source: timesheet export 2026-10-30 (SOW-BW-2026-04); estimate from Exhibit A line 1.

##### Upcoming period

Next gate: Requirements sign-off (2026-11-13). Next session: 2026-11-04, notification templates (Dana Whitlock, 2026-10-28).

Needed from client:

- Tomas Reyes: IdP metadata file (D-001), earliest 2026-11-06 by his own statement.
- Priya Nandakumar: confirm whether the Fieldwise push is a requirement (D-003), proposed by 2026-11-06.
- Tomas Reyes: confirm billing sandbox rate limit handling for the nightly sync (R-004), proposed by 2026-11-13.
- Priya Nandakumar: confirm billing account data state (A-002), proposed by 2026-11-13.

##### Artifact and gate register delta

No gate moved this period and no artifact was delivered in the supplied record. DELIVERY-STATE.md was not supplied, so its currency is unverified. Named gap, owner: Program Lead.
