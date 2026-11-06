---
skill: delivery-orchestrator
title: Routing a UAT script request when the design gate is still open
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 39b3a3e46eae49ae780f245a616eeb4b1a42824a53027735c577768d149d0372
---

## Request

The Northgate client team wants to start user acceptance testing the week of 16 November, so can you get the UAT test scripts going? The engagement state file and my notes from this morning's call are in inputs/.

## Inputs

Run of the `delivery-orchestrator` source module, which has no task package of its own. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### DELIVERY-STATE.md

#### DELIVERY-STATE

- Engagement: Northgate Veterinary Group Appointment Scheduling Rollout
- SOW: SOW-2026-031 (executed 2026-02-24, engagements/northgate-scheduling/contract/sow-2026-031.pdf)
- Quote: Q-000208
- As of: 2026-10-12

##### Stage

current: build

##### Gates

- brief_accepted: accepted 2026-03-02
- charter_signed: signed 2026-03-16
- requirements_cosigned: signed
- sdd_cosigned: open
- build_complete: open
- go_no_go: open
- golive_acceptance: open
- hypercare_closeout: open

##### Artifacts

- Handoff brief: engagements/northgate-scheduling/handoff/handoff-brief.md
- Project charter: engagements/northgate-scheduling/mobilize/charter.docx
- Requirements document: engagements/northgate-scheduling/analyze/requirements-v3.docx
- Solution design document: engagements/northgate-scheduling/design/sdd-v2.docx

##### Open decisions

- Client IT lead to confirm SMS provider for reminders, owner: client IT lead, resolve by 2026-10-30, blocks sdd_cosigned

##### Log (append only)

- 2026-03-02: Handoff brief accepted by delivery team
- 2026-03-16: Charter signed by client sponsor
- 2026-05-08: Requirements document v3 co-signed (Program Lead)
- 2026-09-14: SDD v2 sent to client for co-signature
- 2026-10-12: Sandbox configuration started for clinic booking module

#### call-notes.md

#### Call notes, 4 Nov 2026

Call with the Northgate operations manager.

- They want UAT to start the week of 16 Nov. Their clinic managers have blocked time.
- Operations manager said the SDD "is basically fine" and the sponsor will sign it "when she is back from leave".
- SMS reminder provider still not confirmed by their IT lead. Said she would chase.
- Sandbox booking module is partly configured. Reminders module not started.
- They asked whether the go-live date of 7 December still holds. I said I would check.
- Nothing yet on who on their side signs the go/no-go.

## Output

### Northgate UAT: the engagement is not at the testing stage yet

**Position: 03 Design. Next gate: Solution Design Document co-signed, held by the client. Findings: 4.**

I couldn't run `plan.py` here, so I applied its documented rules to your state file by hand. The result is below.

#### Why UAT can't start the week of 16 November

UAT belongs to 05 Validate, whose owner is `validate-delivery`. The ledger puts the engagement at 03 Design:

| Gate | Status |
| --- | --- |
| brief_accepted | accepted 2026-03-02 |
| charter_signed | signed 2026-03-16 |
| requirements_cosigned | signed (no date in the file; log says 2026-05-08) |
| **sdd_cosigned** | **open** (SDD v2 sent 2026-09-14, no signature on file) |
| build_complete, go_no_go, golive_acceptance, hypercare_closeout | open |

- The operations manager said the SDD is "basically fine", but without a signature the gate is open.
- Build is only partly done. The booking module is partly configured and the reminders module hasn't started. UAT needs `build_complete` first.
- Scripts built now would be rebuilt if the SMS provider choice changes the design.

#### Findings

1. **Stage line wrong.** The file says `current: build`, but the gates say Design. Gates win, so I corrected the line.
2. **Undated pass.** `requirements_cosigned` had no date. I used 2026-05-08 from the log. Please check it against the signed requirements-v3 copy.
3. **Overdue decision.** The SMS provider confirmation was due 2026-10-30 and is still outstanding. It blocks `sdd_cosigned`.
4. **Unowned signatories.** The sponsor is on leave, so nobody is named to co-sign the SDD. No one is named for the go/no-go either. I added both as open decisions with no resolve-by date, because I can't set one. Please agree dates with the client.

#### Routing decision

- **Now:** `design-software-system` (with `assess-solution-delivery` if feasibility is in question) owns the work that closes the open gate. The work is to get the SMS provider confirmed, reflect it in the SDD if needed, and get the SDD signed by the sponsor or a delegate.
- **UAT scripts:** owner is `validate-delivery`. I'd hand off a draft only. It would cover the booking flows traced to co-signed requirements-v3 and be marked draft, and the reminder scenarios would wait for the provider decision. Scripts based on the unsigned SDD would be rebuilt if the design changes.
- **Go-live date:** I haven't checked whether 7 December holds. With Design open, Build unfinished and a UAT window still to run, I can't confirm it. Route that question to `track-delivery` and the commercial owner. Don't tell the client it holds. If the date slips, check the SOW for any change-control implications.
- **Reporting:** `track-delivery` should log the client's request to start UAT early and the overdue decision.

#### What to tell the client

UAT can't be scheduled until the SDD is co-signed and the sandbox build is complete. We need two things from them: the SMS provider decision, and a named person who can sign the SDD while the sponsor is away. The UAT window can be held provisionally, but not committed.

#### Files

- `out/run-record.md`: planner output, findings and routing decision.
- `out/DELIVERY-STATE.md`: corrected state file. Changes: Stage `design`; requirements_cosigned dated 2026-05-08 (to confirm); As of 2026-11-04; two open decisions added; three dated log lines appended, covering the two corrections and today's client call. No gate was marked passed.

### File: DELIVERY-STATE.md

#### DELIVERY-STATE

- Engagement: Northgate Veterinary Group Appointment Scheduling Rollout
- SOW: SOW-2026-031 (executed 2026-02-24, engagements/northgate-scheduling/contract/sow-2026-031.pdf)
- Quote: Q-000208
- As of: 2026-11-04

##### Stage

current: design

##### Gates

- brief_accepted: accepted 2026-03-02
- charter_signed: signed 2026-03-16
- requirements_cosigned: signed 2026-05-08
- sdd_cosigned: open
- build_complete: open
- go_no_go: open
- golive_acceptance: open
- hypercare_closeout: open

##### Artifacts

- Handoff brief: engagements/northgate-scheduling/handoff/handoff-brief.md
- Project charter: engagements/northgate-scheduling/mobilize/charter.docx
- Requirements document: engagements/northgate-scheduling/analyze/requirements-v3.docx
- Solution design document: engagements/northgate-scheduling/design/sdd-v2.docx

##### Open decisions

- Client IT lead to confirm SMS provider for reminders, owner: client IT lead, resolve by 2026-10-30 (past due as of 2026-11-04), blocks sdd_cosigned
- Client signatory for SDD co-signature while the sponsor is on leave, owner: Program Lead with client sponsor, resolve by: not set (to be agreed), blocks sdd_cosigned
- Client signatory for go/no-go, owner: Program Lead with client sponsor, resolve by: not set (to be agreed), blocks go_no_go

##### Log (append only)

- 2026-03-02: Handoff brief accepted by delivery team
- 2026-03-16: Charter signed by client sponsor
- 2026-05-08: Requirements document v3 co-signed (Program Lead)
- 2026-09-14: SDD v2 sent to client for co-signature
- 2026-10-12: Sandbox configuration started for clinic booking module
- 2026-11-04: Correction: Stage line read "build" but sdd_cosigned is open; set to "design" (gates outrank the Stage line)
- 2026-11-04: Correction: requirements_cosigned lacked a date; 2026-05-08 taken from the 2026-05-08 log line. Date to be confirmed against the signed requirements-v3 copy
- 2026-11-04: Client call: operations manager asked for UAT to start the week of 2026-11-16; SDD unsigned, sponsor on leave; SMS provider still unconfirmed; go-live date 2026-12-07 queried by client and not yet checked

### File: run-record.md

#### Delivery-suite run record: Northgate scheduling rollout, 2026-11-04

##### Planner output (plan.py run by hand)

I could not execute `scripts/plan.py`, so I applied its documented rules to `inputs/DELIVERY-STATE.md` (the first gate in lifecycle order that is not passed marks the current stage; gates outrank the Stage line).

```
DELIVERY PLAN  engagement: Northgate Veterinary Group Appointment Scheduling Rollout  as of: 2026-10-12
Truth hierarchy: executed SOW/quote > artifact files > DELIVERY-STATE.md > memory > chat

Current stage: 03 Design
Next gate: Solution Design Document co-signed (held by: client)
Owning skill now: design-software-system; assess-solution-delivery for delivery feasibility

Remaining stages, in order:
  03   Design    owner: design-software-system; assess-solution-delivery for delivery feasibility
       gate: Solution Design Document co-signed
  04   Build     owner: the configured project implementation workflow
       gate: Build complete in sandbox
  05   Validate  owner: validate-delivery
       gate: Go / no-go co-signed
  06   Deploy    owner: manage-cutover-closeout
       gate: Go-Live Acceptance issued
  06b  Closeout  owner: manage-cutover-closeout
       gate: Hypercare Closeout delivered

Findings (1):
  - declared stage 'build' disagrees with the gate ledger, which puts the engagement at 03 Design. Gates win; fix the Stage line.
```

Findings I added by reading the file, not from the planner:
- `requirements_cosigned` is marked signed with no date. The log shows 2026-05-08. Undated passes are suspect.
- Open decision "SMS provider" passed its 2026-10-30 resolve-by date.
- The go/no-go signatory is not named anywhere.

##### Routing decision

Request: start UAT scripts for a UAT window from 2026-11-16.
Owning skill: `validate-delivery` (05 Validate). The engagement is at 03 Design, two gates earlier.
Decision: do not hand off for a full script build. The design gate is open and the design (including the reminder provider) is not final, so scripts written now would be rebuilt. Hand off to `validate-delivery` for a draft limited to the booking flows that trace to co-signed requirements-v3, marked draft and not executable, and keep the gate unpassed.

Handoff details (when sent): engagement folder `engagements/northgate-scheduling/`; state file `DELIVERY-STATE.md`; artifact asked for: UAT test script draft traced to `analyze/requirements-v3.docx`.

##### State-file corrections

See `out/DELIVERY-STATE.md`: Stage line changed to design; requirements_cosigned dated 2026-05-08 (from log, to confirm against signed copy); two open decisions added; three dated log lines appended.
