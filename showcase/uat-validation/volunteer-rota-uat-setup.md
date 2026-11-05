---
skill: uat-validation
title: UAT scripts, tracker and readiness check for a volunteer rota system
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: df12e4024062a0e9c7a2ee8ac55358d26599110a8acfe9c134f493f8163925ad
---

## Request

We start UAT on the volunteer rota system next Monday. Can you write the test scripts from the requirements workbook, set up the UAT tracker and defect log, and tell me whether we're ready to start? The workbook extract, Test Plan extract and build status are attached.

## Inputs

Run of the built `acceptance-testing` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so. Other files it produced, not shown here: `coverage-gaps.csv`, `defect-log.csv`, `requirements.csv`, `uat-tracker.csv`.

#### requirements-workbook-extract.md

#### Requirements workbook extract (Volunteer Rota, v1.3, 2026-10-28)

| ID | Priority | As a | Requirement |
|---|---|---|---|
| VRS-001 | Must Have | Volunteer | Book an open shift from my phone |
| VRS-002 | Must Have | Volunteer | Be stopped from booking two overlapping shifts |
| VRS-003 | Must Have | Rota coordinator | See unfilled shifts for the next 14 days |
| VRS-004 | Should Have | Volunteer | Get a reminder 48 hours before a booked shift |
| VRS-005 | Must Have | Rota coordinator | Block clinical-area shifts when a volunteer's safeguarding check has expired |
| VRS-006 | Could Have | Rota coordinator | Export monthly volunteer hours as CSV |

##### Acceptance criteria (Gherkin)

VRS-001
Given I am a signed-in volunteer with a valid safeguarding check
And shift "Ward Tea Round, Sat 09:00" has 1 open place
When I select "Book" on that shift
Then the shift appears under "My shifts"
And the open places on the shift drop to 0

VRS-002
Given I am booked on "Ward Tea Round, Sat 09:00-12:00"
When I try to book "Garden Team, Sat 11:00-14:00"
Then the booking is refused with the message "This overlaps a shift you already have"

VRS-003
Given 3 shifts in the next 14 days have no volunteer
When I open the Coordinator dashboard
Then I see exactly those 3 shifts, ordered by start time

VRS-004
Scenario Outline: reminder timing
Given I am booked on a shift starting <start>
When the reminder job runs at <run>
Then a reminder email <result>
Examples:
| start | run | result |
| Sat 09:00 | Thu 09:00 | is sent |
| Sat 09:00 | Wed 09:00 | is not sent |

VRS-005
No acceptance criteria recorded yet.

VRS-006
Given March has 40 logged hours for volunteer V-0042
When I choose "Export hours" for March
Then the CSV contains V-0042 with 40 hours

#### test-plan-and-build-status.md

#### Test Plan extract (co-signed 2026-09-30) and build status (2026-11-03)

##### Environments
- SIT sandbox: "Rota-SIT". UAT sandbox: "Rota-UAT", refreshed 2026-11-02.

##### Test data (section 4)
Dataset "Rota-UAT-Seed": 25 masked volunteers (V-0001 to V-0025), 40 shifts over 4 weeks, one volunteer (V-0019) with an expired safeguarding check. Provisioned by the Solution Lead (Priya Nand).

##### Severity (section 5)
- Sev 1: stops testing or a core process, no workaround.
- Sev 2: major function wrong, workaround not acceptable for go-live.
- Sev 3: impaired, acceptable workaround.
- Sev 4: cosmetic.

##### UAT entry criteria (section 6)
- All Must Have requirements have a script.
- Rota-UAT seeded with Rota-UAT-Seed.

##### Build status, Rota-UAT
Built: VRS-001, VRS-002, VRS-003, VRS-004, VRS-005.
Not built: VRS-006 (export), due sprint 6, ends 2026-11-27.

##### Notes from the project manager
The client UAT executors are Grace Okafor (volunteer role) and Tomasz Weir (coordinator role). The safeguarding rule for VRS-005 was agreed verbally; no AC was written.

## Output

### Volunteer Rota: UAT scripts, tracker and readiness check

Every requirement except VRS-006 now has a script, and the traceability check passes. UAT can start on Monday for the five built requirements, but three items need a person before then (listed under "Decisions and open questions"). Nothing has been executed yet, so every result is "Not started".

Sources: requirements workbook extract v1.3 (2026-10-28), Test Plan extract co-signed 2026-09-30 (sections 4 to 6), build status 2026-11-03. The SOW acceptance section was not in the material you sent, so this is a run record, not a go/no-go pack.

#### Traceability gate

I could not run `scripts/trace_check.py` here, so I applied its three rules by hand to the files below.

| Check | Result |
|---|---|
| Requirements in workbook | 6 |
| Requirements with at least one script | 5 of 6 (83 percent) |
| Named gaps | 1 (VRS-006) |
| Requirements neither scripted nor named as a gap | 0 |
| Scripts | 6 |
| Scripts tracing to an unknown or missing ID | 0 (no orphans) |

Hand-applied result: gate would pass, 0 findings. Please run the script on the three CSVs to confirm.

#### Coverage numbers (as of the 2026-11-03 build status)

| Measure | All | Must Have | Should Have | Could Have |
|---|---|---|---|---|
| Requirements | 6 | 4 | 1 | 1 |
| Requirements with a script | 5 of 6 | 4 of 4 | 1 of 1 | 0 of 1 |
| Execution progress (Passed + Failed over scripts) | 0 of 6 (0 percent) | 0 of 4 | 0 of 1 | no script |
| Requirement pass rate | 0 of 6 (0 percent) | 0 of 4 | 0 of 1 | 0 of 1 |

Every Must Have has a UAT script for the client persona (TS-001 and TS-002 volunteer, TS-003 and TS-006 coordinator). VRS-004 is covered by SIT scripts only; it is Should Have, so this is not the Must Have finding the skill treats as mandatory, but you may want a volunteer to see a real reminder email.

#### Test scripts

| Script | Requirement | Phase | Persona | Source |
|---|---|---|---|---|
| TS-001 Book the last open place on a shift | VRS-001 | UAT | Volunteer | inferred from AC (phone step) |
| TS-002 Overlapping booking is refused | VRS-002 | UAT | Volunteer | mechanical from AC |
| TS-003 Coordinator sees exactly the 3 unfilled shifts | VRS-003 | UAT | Rota coordinator | mechanical from AC |
| TS-004 Reminder sent, job runs Thu 09:00 | VRS-004 | SIT | QA | mechanical from AC (outline row 1) |
| TS-005 Reminder not sent, job runs Wed 09:00 | VRS-004 | SIT | QA | mechanical from AC (outline row 2) |
| TS-006 Expired check blocks a clinical-area shift | VRS-005 | UAT | Rota coordinator | authored (no AC) |

Example: TS-002 has one step. Action: try to book "Garden Team, Sat 11:00-14:00" while booked on "Ward Tea Round, Sat 09:00-12:00". Expected: refused with "This overlaps a shift you already have". That text comes from the AC unchanged.

#### Named gap

| Requirement | Owner | Reason | Resolve by | Gate blocked |
|---|---|---|---|---|
| VRS-006 Export monthly hours as CSV (Could Have) | Solution Lead (Priya Nand) | Not built in Rota-UAT; due sprint 6, which ends 2026-11-27 | 2026-11-27 | Go/no-go |

The AC for VRS-006 exists, so a script can be written once the build lands. I did not write one against an unbuilt feature.

#### Defect log

`defect-log.csv` is set up empty with the full field set: DEF-### IDs, found-by source with script and step, severity, triage decision kept separate from severity, owner, status and fix evidence. Severity uses Test Plan section 5 (Sev 1 to 4), not the skill's fallback table. A defect closes only with a recorded retest (who, when, environment, result); a developer saying "fixed" moves it to Retest. Sev 1 and 2 defects should go to the RAID log through delivery-status.

#### Decisions and open questions

1. **VRS-005 has no acceptance criteria.** The rule was agreed verbally. I authored TS-006 with provisional steps and marked three inferences inline: the blocking message, which shifts count as clinical-area, and that non-clinical shifts stay bookable. This goes back to requirements-backlog (owner: BA) for written Given/When/Then. I did not change the requirement inside the script. VRS-005 is a Must Have, so until the AC exists a TS-006 pass would rest on an unsigned rule.
2. **Seed data is not confirmed.** Test Plan section 6 requires Rota-UAT to be seeded with Rota-UAT-Seed. The build status says Rota-UAT was refreshed on 2026-11-02 but does not say the seed was loaded. TS-003 also needs exactly 3 unfilled shifts in the next 14 days, and TS-006 needs a known clinical-area shift. Owner: Solution Lead (Priya Nand). Status of this entry criterion: cannot assess.
3. **Executors.** Grace Okafor (volunteer role) and Tomasz Weir (coordinator role) are named as the client executors. Scripts hold roles only; the tracker's Executed By and Executed On fields stay empty until they report results.

#### Readiness for Monday

| Entry criterion (Test Plan section 6) | Status | Evidence |
|---|---|---|
| All Must Have requirements have a script | Met | TS-001, TS-002, TS-003, TS-006; 4 of 4 |
| Rota-UAT seeded with Rota-UAT-Seed | Cannot assess | Refresh dated 2026-11-02; seed load not stated |

Beyond the two criteria, VRS-005's missing AC and the unbuilt VRS-006 are known limits on what Monday's UAT can prove. Whether to start with those open is your call and the sponsor's. I have not marked any gate as met.

#### Files

- `out/test-scripts.md`: the six scripts with preconditions, steps, expected results and inference flags.
- `out/uat-tracker.csv`: six rows, all "Not started"; columns Test Script ID, Title, Requirement IDs, Phase, Persona, Priority, Status, Executed By, Executed On, Defect IDs, Orphan Flag, Notes.
- `out/requirements.csv`: the six workbook IDs with priority, used as the gate input.
- `out/coverage-gaps.csv`: VRS-006, owner, reason, resolve-by 2026-11-27.
- `out/defect-log.csv`: empty log, header only.

Prose in these files was checked by reading; the bundled `writing_check.py` was not run because scripts cannot run in this environment.

### File: test-scripts.md

#### Volunteer Rota test scripts

Sources: requirements workbook extract v1.3 (2026-10-28); Test Plan extract co-signed 2026-09-30 (sections 4 to 6); build status 2026-11-03. Status for every script lives in `uat-tracker.csv`. Environment for UAT scripts is Rota-UAT; for SIT, Rota-SIT. Dataset: Rota-UAT-Seed.

##### TS-001: Book the last open place on a shift
| Field | Value |
|---|---|
| Requirement IDs | VRS-001 |
| Phase / Persona | UAT / Volunteer |
| Environment | Rota-UAT |
| Test data | Rota-UAT-Seed; a volunteer with a valid check; shift "Ward Tea Round, Sat 09:00" set to 1 open place |
| Source | inferred from AC |
| Orphan Flag | |

Preconditions
1. Signed in as a volunteer with a valid safeguarding check.
2. Shift "Ward Tea Round, Sat 09:00" has 1 open place.

| Step | Action | Expected result |
|---|---|---|
| 1 | Open the rota on a phone browser [INFERRED: the requirement says "from my phone"; the AC names no device] | Shift list shows "Ward Tea Round, Sat 09:00" with 1 open place |
| 2 | Select "Book" on that shift | The shift appears under "My shifts" |
| 3 | Reopen the shift | Open places show 0 |

##### TS-002: Overlapping booking is refused
| Field | Value |
|---|---|
| Requirement IDs | VRS-002 |
| Phase / Persona | UAT / Volunteer |
| Test data | Rota-UAT-Seed; "Ward Tea Round, Sat 09:00-12:00" and "Garden Team, Sat 11:00-14:00" |
| Source | mechanical from AC |

Preconditions
1. Volunteer is booked on "Ward Tea Round, Sat 09:00-12:00".

| Step | Action | Expected result |
|---|---|---|
| 1 | Try to book "Garden Team, Sat 11:00-14:00" | Booking refused with the message "This overlaps a shift you already have" |

##### TS-003: Coordinator sees unfilled shifts
| Field | Value |
|---|---|
| Requirement IDs | VRS-003 |
| Phase / Persona | UAT / Rota coordinator |
| Test data | Rota-UAT-Seed adjusted so exactly 3 shifts in the next 14 days have no volunteer |
| Source | mechanical from AC |

Preconditions
1. 3 shifts in the next 14 days have no volunteer.

| Step | Action | Expected result |
|---|---|---|
| 1 | Open the Coordinator dashboard | Exactly those 3 shifts are listed, ordered by start time |

##### TS-004 and TS-005: Reminder timing (Scenario Outline, one script per example row)
| Field | Value |
|---|---|
| Requirement IDs | VRS-004 |
| Phase / Persona | SIT / QA (UAT by Volunteer is a candidate addition; see run record) |
| Environment | Rota-SIT |
| Source | mechanical from AC |

Preconditions
1. A volunteer is booked on a shift starting Sat 09:00.

| Script | Start | Job runs | Action | Expected result |
|---|---|---|---|---|
| TS-004 | Sat 09:00 | Thu 09:00 | Run the reminder job | A reminder email is sent |
| TS-005 | Sat 09:00 | Wed 09:00 | Run the reminder job | No reminder email is sent |

##### TS-006: Expired safeguarding check blocks a clinical-area shift
| Field | Value |
|---|---|
| Requirement IDs | VRS-005 |
| Phase / Persona | UAT / Rota coordinator |
| Test data | Rota-UAT-Seed volunteer V-0019 (expired check); one clinical-area shift [INFERRED: the seed does not say which shifts are clinical-area] |
| Source | authored (no AC) |

The workbook records no acceptance criteria for VRS-005, and the rule was agreed verbally. Raised as an open question to requirements-backlog (see run record). The steps below are provisional and must not be treated as co-signed.

Preconditions
1. V-0019 has an expired safeguarding check.
2. A clinical-area shift has an open place.

| Step | Action | Expected result |
|---|---|---|
| 1 | Try to book the clinical-area shift for V-0019 | The booking does not complete [INFERRED: exact message and who sees it are unspecified] |
| 2 | Open the shift as coordinator | V-0019 is not on the shift roster and open places are unchanged |
| 3 | Book a non-clinical shift for V-0019 | Booking completes [INFERRED: rule is stated for clinical areas only] |
