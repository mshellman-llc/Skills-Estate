---
skill: cutover-closeout
title: Cutover runbook and deemed-acceptance deadline for a scheduling migration
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 583fb89bee016741de40cafa78ec1a29c44e9d5109a4e67fc68ee4a4de7ce00f
---

## Request

Steering committee signed the go decision for the Fernbank scheduling migration, and cutover is this weekend. Can you build the cutover runbook from the attached plan and set up the Go-Live Acceptance tracker with the deemed-acceptance deadline from the SOW clause?

## Inputs

Run of the built `cutover-closeout` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### cutover-plan.md

#### Cutover plan v0.9 and readiness notes

Go decision: signed 2026-11-03 by the Fernbank steering committee (Dana Okafor, Client Sponsor; Priya Raman, Program Lead). Minutes ref SC-2026-11-03.

Window: Friday 2026-11-13 22:00 to Saturday 2026-11-14 04:00, Australia/Melbourne. War room: #fernbank-cutover, bridge https://meet.example.com/fernbank-cutover.

Team: Program Lead Priya Raman; Solution Lead Tomas Beck; TA/deploy Lena Ito; CSE Marcus Webb. Client: Dana Okafor (sponsor), Samir Qureshi (clinic ops IT), Joy Adeyemi (front-desk lead).

Sequence as planned:
1. Freeze legacy scheduler to read-only (Samir). Check: write attempt returns the read-only banner.
2. Full legacy database backup (Lena), stored in the vault bucket. Check: restore of the backup to staging reconciles row counts.
3. Export appointments for 42 clinics (Lena). Check: export count equals legacy count per clinic (last dry run: 18,406 total).
4. Import into new platform (Lena). Check: per-clinic counts match export. Reversible by wiping import and unfreezing legacy.
5. Switch DNS for booking.fernbank.example.com to new platform (Lena). TTL 300s. Reversible by repointing.
6. Enable SMS reminder job (Tomas). Check: test reminder received on Joy's test phone. Messages sent to patients cannot be recalled.
7. Test booking round-trip (Joy). Check: booking appears in clinic calendar and confirmation email arrives.
8. Send Go-Live Notice (Priya) on completion of steps 1-7.

Point of no return: step 6 (first real patient SMS). Rollback call: Priya, with Dana consulted, by 02:30.
Open defects at sign-off: DEF-017 (Sev 3, calendar colours reset on import; fix in hypercare), DEF-021 (Sev 4, report footer typo; accepted as known issue, ref SC-2026-11-03).
Freeze: code freeze since 2026-11-09. Backup: not yet taken.
Monitoring: booking error rate watched by Tomas through 2026-11-20; over 2% of bookings failing in any hour opens a hypercare issue. Legacy rollback needs about 45 minutes.

#### sow-excerpt.md

#### SOW-FB-2026-014 excerpt (Fernbank Dental Group, Appointment Scheduling Migration)

Executed 2026-07-20 by Fernbank Dental Group and the delivery firm.

Section 9.1 Definitions. "Business Day" means a day other than a Saturday, Sunday or public holiday in Victoria, Australia. "Go-Live Notice" means the written notice from the delivery firm to the Client Sponsor that the Cutover Verification steps in the agreed cutover plan are complete.

Section 9.3 Go-Live Acceptance. "The Client must, within seven (7) Business Days after receipt of the Go-Live Notice, either (a) sign the Go-Live Acceptance Certificate or (b) notify the delivery firm in writing of any material non-conformance with the Accepted Scope. If the Client does neither within that period, the Go-Live Deliverables are deemed accepted at the end of the seventh Business Day."

Section 9.5 Hypercare. Hypercare runs 15 Business Days from Go-Live Notice and covers defects in the Accepted Scope only.

Acceptance criteria (Test Plan v1.2): AC-1 all 42 clinic calendars migrated with matching appointment counts; AC-2 online booking round-trips a test booking; AC-3 SMS reminders sent for next-day appointments.

## Output

I've built the cutover runbook and the Go-Live Acceptance tracker. The deemed-acceptance deadline is **Tuesday 2026-11-24**, if the Go-Live Notice goes out on Saturday 2026-11-14. Both files need a few facts confirmed before cutover (listed below).

#### Deadline

SOW-FB-2026-014 section 9.3 gives the client 7 Business Days after receipt of the Go-Live Notice to sign the certificate or contest in writing. Section 9.1 defines a Business Day as a day other than a Saturday, Sunday or Victorian public holiday. The clause is quoted word for word in the tracker.

Notice Saturday 2026-11-14 + 7 business days = **2026-11-24 (Tuesday)**. Days counted: Nov 16-20 and Nov 23-24. Weekend skipped: Nov 14-15. No holidays in the window.

Hypercare (section 9.5, 15 Business Days from the notice) ends 2026-12-04.

The trigger is the notice, not the end of the cutover window. If the notice moves, the deadline moves, so recompute it then.

#### Runbook

The window is 2026-11-13 22:00 to 2026-11-14 04:00 Melbourne time. It has eight steps, each with a named owner, a check a second person could run, and a rollback point:

| # | Step | Owner | Rollback point |
|---|------|-------|----------------|
| 1 | Set legacy scheduler to read-only | Samir Qureshi | RB-1 |
| 2 | Full legacy backup; staging restore reconciles | Lena Ito | RB-1 |
| 3 | Export appointments for 42 clinics | Lena Ito | RB-1 |
| 4 | Import; per-clinic counts match | Lena Ito | RB-1 |
| 5 | Repoint booking DNS (TTL 300s) | Lena Ito | RB-1 |
| 6 | Enable SMS reminders | Tomas Beck | No rollback: sent SMS cannot be recalled; remedy is a corrective message approved by the Client Sponsor |
| 7 | Test booking round-trip | Joy Adeyemi | No rollback: committed after step 6; failures go to hypercare |
| 8 | Send Go-Live Notice | Priya Raman | No rollback: starts the SOW clock; withdrawal is a CSE decision |

- **Point of no return:** step 6, because it sends the first real patient SMS. The rollback call is Priya Raman's, with Dana Okafor consulted, by 02:30. RB-1 takes about 45 minutes, so that time leaves room to finish inside the window.
- **RB-1:** returns to the legacy scheduler. It repoints DNS, wipes the import, unfreezes legacy and confirms a test write.
- **Monitoring:** Tomas Beck watches the booking error rate through 2026-11-20. More than 2% failing in any hour opens a hypercare issue.
- **Defects at sign-off:** DEF-017 (Sev 3, fix in hypercare) and DEF-021 (Sev 4, accepted as known issue, ref SC-2026-11-03).

#### Tracker

The tracker holds the three acceptance criteria (AC-1 to AC-3, from Test Plan v1.2), the two open defects, the status line and a surfacing log. The status is "Clock not started" because the notice has not been sent. Nothing is recorded as accepted. Only the client can accept, and only a human can record it.

#### Gaps and assumptions

- **Documents missing:** I had only cutover plan v0.9. There was no readiness pack, no Solution Design Document and no final signed plan. Tomas Beck should supply the first two and Priya Raman the signed plan, by 2026-11-10. Until then the step list is unconfirmed.
- **Code freeze:** the plan says it has been in place since 2026-11-09, but no evidence link was supplied. Tomas Beck, by 2026-11-10.
- **Phone numbers:** the escalation path has no contact numbers. Priya Raman, by 2026-11-12.
- **Holidays:** no Victorian holiday calendar was supplied, so I listed none. Priya Raman should confirm none falls on 2026-11-16 to 2026-11-24 by 2026-11-12. If one does, the deadline moves a day.
- **Time of day:** the clause says acceptance happens "at the end of the seventh Business Day". The calculator gives a date only, with no time cutoff. Marcus Webb and counsel should confirm before the notice goes out.
- **Receipt:** I assumed the client receives the notice the day it is sent. Dana Okafor's written acknowledgement (step 8) fixes the date.
- **Contests:** what counts as a "material non-conformance", and whether a contest stops the clock, is for Marcus Webb and counsel. The tracker does not interpret it.
- **Backup:** it has not yet been taken. Step 2 takes it, and step 3 should not start until the staging restore reconciles.

#### Checks

I couldn't run scripts here. I applied the rules of `closeout_gate.py` by hand instead, so no gate receipt exists yet.

- **Runbook:** all 8 rows have an owner, a verification and a rollback point or a reasoned "No rollback:". I found no failures by hand.
- **Acceptance:** the stated deadline matches my recomputation under the gate's convention (day 1 is the first qualifying day after the trigger). I found no failures by hand.
- **Style:** there are no em dashes, and I read all the prose myself. The prose, brand and quality validators were not run, and the files are plain Markdown with no branded render.
- **Next step:** please run `python3 scripts/closeout_gate.py <file> --type runbook` and `--type acceptance` before the files circulate.
- **Not persisted:** nothing is written back to the Hub records. `engagement.test_acceptance` and `deliverables.register` are unchanged.

#### Human actions

- Priya Raman and Dana Okafor approve the final runbook and make any rollback call.
- Priya Raman sends the notice and logs the first surfacing entry to herself and Marcus Webb.
- Dana Okafor, or an authorized client delegate, signs or contests.

#### Files

- `./out/cutover-runbook.md`: header, roles, entry conditions, the eight-step table, RB-1, the rollback rule, monitoring and gaps G1-G4.
- `./out/go-live-acceptance-tracker.md`: the verbatim clause, go-live date 2026-11-14, period 7 business days, deadline 2026-11-24, the worked count, criteria, defects, status line and gaps A1-A4.

### File: cutover-runbook.md

#### Cutover runbook: Fernbank Dental Group scheduling migration

- Client: Fernbank Dental Group
- Engagement: Appointment Scheduling Migration (SOW SOW-FB-2026-014)
- Cutover window: 2026-11-13 22:00 to 2026-11-14 04:00, Australia/Melbourne
- Go / no-go: signed 2026-11-03 by the Fernbank steering committee, Dana Okafor (Client Sponsor) and Priya Raman (Program Lead) (source: minutes SC-2026-11-03)
- War room: #fernbank-cutover, bridge https://meet.example.com/fernbank-cutover
- Sources: cutover plan v0.9 and readiness notes (no separate readiness pack or Solution Design Document was supplied; see gaps)
- As of: 2026-11-04, built from the cutover plan v0.9 only

##### Roles on the day

| Role | Delivery team | Client counterpart | Reachable via |
|------|---------------|--------------------|---------------|
| Program Lead | Priya Raman | Dana Okafor (Client Sponsor) | #fernbank-cutover, bridge |
| Solution Lead | Tomas Beck | Samir Qureshi (clinic ops IT) | #fernbank-cutover, bridge |
| TA / deploy | Lena Ito | Samir Qureshi | #fernbank-cutover, bridge |
| Front-desk verification | none | Joy Adeyemi (front-desk lead) | #fernbank-cutover, bridge |

Escalation path: first Priya Raman, then Tomas Beck, then CSE Marcus Webb. Phone numbers are not in the supplied plan (gap G3).

##### Go / no-go entry conditions

- Open defects at sign-off: DEF-017 (Sev 3, calendar colours reset on import; disposition: fix in hypercare). DEF-021 (Sev 4, report footer typo; disposition: accepted as known issue, client sign-off ref SC-2026-11-03).
- Environment freeze: code freeze in place since 2026-11-09 (source: cutover plan; evidence link not supplied, gap G2).
- Pre-cutover backup: not yet taken. Step 2 takes it, and step 3 does not start until the staging restore reconciles.

##### Step table

| # | Step | Owner | Verification | Rollback point |
|---|------|-------|--------------|----------------|
| 1 | Set the legacy scheduler to read-only | Samir Qureshi | A test write in the legacy scheduler returns the read-only banner | RB-1 |
| 2 | Take a full legacy database backup to the vault bucket | Lena Ito | Restoring the backup to staging gives row counts equal to the legacy counts | RB-1 |
| 3 | Export appointments for all 42 clinics from legacy | Lena Ito | Export count equals legacy count for each clinic; the total is compared with the 18,406 from the last dry run and any difference is explained in the channel | RB-1 |
| 4 | Import the export into the new platform | Lena Ito | Per-clinic counts in the new platform equal the export counts for all 42 clinics | RB-1 |
| 5 | Repoint DNS for booking.fernbank.example.com to the new platform (TTL 300s) | Lena Ito | `nslookup` from two networks returns the new platform address | RB-1 |
| 6 | Enable the SMS reminder job | Tomas Beck | A test reminder arrives on Joy Adeyemi's test phone | No rollback: reminders sent to patients cannot be recalled; the remedy is a corrective SMS approved by Dana Okafor |
| 7 | Run a test booking through online booking | Joy Adeyemi | The booking shows in the clinic calendar and the confirmation email arrives | No rollback: after step 6 the cutover is committed; failures go to hypercare as issues, not to rollback |
| 8 | Send the Go-Live Notice to the Client Sponsor | Priya Raman | Sent timestamp recorded in the tracker; Dana Okafor acknowledges receipt in writing | No rollback: the notice starts the SOW clock; a withdrawal is a CSE decision with the commercial owner |

Steps 1 to 5 precede step 6. Step 8 follows only when steps 1 to 7 are all verified.

##### Rollback procedures

###### RB-1: Return to the legacy scheduler

- Trigger: any verification in steps 1 to 5 fails and cannot be corrected before 02:30.
- Owner: Lena Ito, on Priya Raman's call
- Steps: 1. Repoint booking.fernbank.example.com to the legacy host (if step 5 ran). 2. Wipe the imported data in the new platform (if step 4 ran). 3. Remove the read-only flag on the legacy scheduler. 4. Confirm a test write succeeds in legacy.
- Duration: about 45 minutes (source: cutover plan)
- End state: legacy scheduler live and writable, new platform empty, no patient messages sent

##### Rollback decision rule

- Who can call it: Priya Raman, with Dana Okafor consulted. The decision is theirs; this runbook does not make it.
- Point of no return: after step 5 and before step 6 starts, because step 6 sends the first real patient SMS. The call must be made by 02:30 so RB-1 (about 45 minutes) finishes inside the window.
- Client communication on rollback: Priya Raman tells Dana Okafor in the bridge, then confirms in writing. Joy Adeyemi tells front-desk staff to keep using the legacy scheduler.

##### Post-cutover monitoring

| What | Watched by | Through | Threshold that opens a hypercare issue |
|------|------------|---------|----------------------------------------|
| Online booking error rate | Tomas Beck | 2026-11-20 | More than 2% of bookings failing in any one hour |
| DEF-017 calendar colours | Joy Adeyemi | 2026-12-04 | Any clinic reporting reset colours opens an HC issue carried from DEF-017 |

##### Open gaps

- G1: Readiness pack and Solution Design Document were not supplied. Owner: Tomas Beck. Due 2026-11-10. Blocks confirming the step list.
- G2: Evidence link for the code freeze. Owner: Tomas Beck. Due 2026-11-10.
- G3: On-call phone numbers for the escalation path. Owner: Priya Raman. Due 2026-11-12.
- G4: The plan is v0.9; a signed final version is needed. Owner: Priya Raman. Due 2026-11-10.

### File: go-live-acceptance-tracker.md

#### Go-Live Acceptance tracker: Fernbank Dental Group scheduling migration

- SOW: SOW-FB-2026-014, executed 2026-07-20
- Go-live date: 2026-11-14 (planned date of the Go-Live Notice, the trigger named in section 9.3; cutover runbook step 8. Recompute if the notice is sent on another date.)
- Acceptance period: 7 business days
- SOW clause (verbatim): Section 9.3, SOW-FB-2026-014, executed 2026-07-20: "The Client must, within seven (7) Business Days after receipt of the Go-Live Notice, either (a) sign the Go-Live Acceptance Certificate or (b) notify the delivery firm in writing of any material non-conformance with the Accepted Scope. If the Client does neither within that period, the Go-Live Deliverables are deemed accepted at the end of the seventh Business Day."
- Business Day definition (section 9.1): a day other than a Saturday, Sunday or public holiday in Victoria, Australia.
- Deemed-acceptance deadline: 2026-11-24
- Holidays observed: none listed; no Victorian public holiday calendar was supplied (gap A1)

##### Computation

Go-Live Notice Saturday 2026-11-14 + 7 business days = 2026-11-24 (Tuesday). Days counted: Nov 16-20, Nov 23-24. Weekend skipped: Nov 14-15. No holidays in window. Gate rule applied by hand: day 1 is the first qualifying day after the trigger date.

Hypercare (section 9.5, 15 Business Days from Go-Live Notice) ends 2026-12-04 on the same count: Nov 16-20, Nov 23-27, Nov 30-Dec 4.

##### Acceptance criteria

| Criterion | Source | Status | Owner | Date |
|-----------|--------|--------|-------|------|
| AC-1 All 42 clinic calendars migrated with matching appointment counts | Test Plan v1.2 | Open; evidence is runbook step 4 | Lena Ito | 2026-11-14 |
| AC-2 Online booking round-trips a test booking | Test Plan v1.2 | Open; evidence is runbook step 7 | Joy Adeyemi | 2026-11-14 |
| AC-3 SMS reminders sent for next-day appointments | Test Plan v1.2 | Open; evidence is runbook step 6 (test reminder only; first real reminders go out after cutover) | Tomas Beck | 2026-11-15 |

##### Open defect disposition

| Defect | Severity | Disposition |
|--------|----------|-------------|
| DEF-017 | Sev 3 | Fix in hypercare |
| DEF-021 | Sev 4 | Accepted as known issue, client sign-off ref SC-2026-11-03 |

##### Status line

Clock not started: the Go-Live Notice has not been sent (as of 2026-11-04).

##### Surfacing log

| Date | Surfaced to | Channel |
|------|-------------|---------|
| none yet | Priya Raman, Marcus Webb | First entry due when the notice is sent; then at 3 business days and 1 business day before 2026-11-24 |

##### Gaps and reviews for humans

- A1: Confirm no Victorian public holiday falls between 2026-11-16 and 2026-11-24. Owner: Priya Raman. Due 2026-11-12. If one does, add it to Holidays observed and recompute.
- A2: Clause says deemed acceptance occurs "at the end of the seventh Business Day". The calculator has no time-of-day cutoff, so the date is the only output. Owner: Marcus Webb with counsel. Due before the notice is sent.
- A3: "Receipt" of the notice is the trigger. The tracker assumes it is received the day it is sent; Dana Okafor's written acknowledgement (runbook step 8) fixes the date.
- A4: What counts as a "material non-conformance" and its effect on the clock are CSE and counsel questions.
