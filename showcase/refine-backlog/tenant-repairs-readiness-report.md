---
skill: refine-backlog
title: Readiness report for six tenant repair portal stories
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 89c830ca620b58762d812090bb255fa50050aa9da3f0ccb697063efdd2937f7a
---

## Request

We held refinement this morning for our tenant repairs portal and I need the readiness report for sprint planning. The requirements export, the RAID log and the estimates the team gave in the session are attached; please grade the six candidates, say what to fix on the ones that aren't ready, and tell me where the stuck ones should go.

## Inputs

Run of the built `refine-backlog` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### RAID.md

#### RAID log: Hollin Court tenant repairs portal

| ID | Type | Description | Owner | Due |
|---|---|---|---|---|
| D-002 | Dependency | Photo storage bucket provisioned by the co-op IT contractor | Priya Nand | 2026-11-13 |
| D-005 | Dependency | Sign-in service accepts tenant accounts from the housing system | Tomás Quirke | 2026-11-06 |
| R-003 | Risk | Contractor calendar data may not be available before January | Priya Nand | 2026-11-20 |

#### requirements.csv

Requirement Number,Name,Epic,As A,I Want To,So That,Acceptance Criteria,Priority,Status,Assumptions & Notes,Estimate Days,Depends On,Refinement Sessions
RPR-001,Report a repair online,Reporting,tenant,report a repair from my phone without calling the office,my repair is logged the same day and I get a reference number,"Scenario: Valid report
Given I am signed in
When I submit the repair form with a room and a description
Then I see a reference number
Scenario: Missing description
Given I am signed in
When I submit the form without a description
Then I see a message asking me to describe the problem",Must,Reviewed,,,,1
RPR-002,Attach photos to a report,Reporting,tenant,attach up to three photos to my repair report,the surveyor can judge urgency before visiting,"Scenario: Photos attached
Given I am filling in a repair report
When I add two photos and submit
Then the surveyor sees both photos on the report",Should,Reviewed,,,D-002,1
RPR-003,See repair status,Tracking,tenant,call the repair status API and show the JSON result,so that it works,"Scenario: Open repair
Given I have an open repair
When I open My repairs
Then I see its current status",Must,Reviewed,,,,2
RPR-004,Book a visit slot,Scheduling,tenant,choose a visit slot for my repair and have the contractor confirm it,I do not wait at home all day for an unknown arrival time,"Scenario: Slot confirmed
Given a contractor has been assigned
When I choose a morning slot
Then I am told when the contractor confirms it",Must,Reviewed,,,D-009,2
RPR-005,Escalate emergency repairs,Reporting,tenant,flag a repair as an emergency,gas leaks and no-heating cases are handled within the response time the co-op promises tenants,"Scenario: Emergency flagged
Given a tenant flags an emergency
When they submit the report
The on-call team is told",Must,Draft,,,,3
RPR-006,Match contractor invoices to repairs,Finance,finance officer,see contractor invoices against each repair,I can check what each repair cost,,Could,Draft,,,finance system export,1

#### session-notes.txt

Refinement session, 4 November 2026
Present: Wen Adeyemi (Product Owner), Dara Okonjo and Lior Vance (engineers), Sam Reyes (QA)

Team estimates in days: RPR-001 3, RPR-002 2, RPR-003 4, RPR-004 12.
RPR-005: engineers declined to estimate. Nobody knows whether the promised emergency response time is 4 hours or 24 hours; the tenancy agreement and the housing officer's guidance disagree. Third session on this item.
RPR-006: not estimated; Lior thinks the finance export may not exist yet.
RPR-004: the contractor calendar feed (R-003 in the RAID log) is what "D-009" refers to; Wen mistyped the ID. No D-009 entry exists.
Sprint length: 2 weeks. Team keeps the 5-day Small limit.
Wen wants the report saved for sprint planning on Monday.

## Output

Two of the six stories are ready for sprint planning: RPR-001 and RPR-002. Two need rework (RPR-003, RPR-004) and two should go back to discovery (RPR-005, RPR-006).

I could not run `readiness_check.py` here. I applied its rules by hand and wrote the JSON in the script's format. Re-run the script on the real workbook export before Monday to confirm the counts: `python3 scripts/readiness_check.py requirements.csv --raid-log RAID.md --format json --output readiness.json`.

#### Result

| ID | Name | Priority | Estimate (days) | Score | Verdict | Failed |
|---|---|---|---:|---:|---|---|
| RPR-001 | Report a repair online | Must | 3 | 6/6 | READY | none |
| RPR-002 | Attach photos to a report | Should | 2 | 6/6 | READY | none |
| RPR-003 | See repair status | Must | 4 | 4/6 | REFINE | Negotiable, Valuable |
| RPR-004 | Book a visit slot | Must | 12 | 4/6 | REFINE | Independent, Small |
| RPR-005 | Escalate emergency repairs | Must | none | 3/6 | DISCOVERY | Estimable, Small, Testable |
| RPR-006 | Match contractor invoices to repairs | Could | none | 2/6 | DISCOVERY | Independent, Estimable, Small, Testable |

The estimates are the ones the team gave in the session notes (Small limit 5 days, as the team keeps). I entered them as given and supplied none for RPR-005 or RPR-006.

A READY verdict means the story is well formed. It does not mean it is the right work or that stakeholders approved it.

#### Ready

- **RPR-001** has no dependencies, a 3-day estimate and two complete scenarios, including the failure path.
- **RPR-002** depends on D-002 (photo storage bucket, Priya Nand, due 2026-11-13), which is in the RAID log. Sprint planning should treat that date as a commit risk. The story has no failure scenario, such as a file that is too large. The definition of ready asks for the main failure path, so the team may want to add one. The check does not require it.

#### Fix before the next session

**RPR-003 See repair status.** It scores 4 and fails two criteria.
- Negotiable: "call the repair status API and show the JSON result" prescribes the build. Rewrite as "see the current status of each repair I have reported".
- Valuable: "so that it works" says nothing about what changes. A suggested replacement for Wen Adeyemi to confirm: "I know whether anyone has picked up my repair without phoning the office".
- The scenario and the 4-day estimate stand. After the rewrite the team should confirm the estimate still holds, since the original wording may have shaped it.

**RPR-004 Book a visit slot.** It scores 4 and fails two criteria.
- Independent: `D-009` is not in the RAID log. The session notes say it was a mistyped reference to the contractor calendar feed, which the log holds as risk R-003. A risk is not a dependency entry, so I left the column as written. I proposed a new dependency entry for track-delivery in `proposed-raid-entries-2026-11-04.md`. Once track-delivery assigns the ID, put it in the Depends On column.
- Small: 12 days against a 5-day limit. Proposed split by workflow step. These are suggestions for the team to estimate, and each needs its own Requirement Number, story and scenario through capture-requirements:
  1. The tenant requests a morning or afternoon window for the repair and sees it recorded as pending. This slice may not need the contractor calendar at all.
  2. The contractor confirms or declines the request, and the tenant is told.
  3. The tenant changes or cancels a confirmed slot.
  - Slice 1 is the smallest useful one. If the team finds it cannot ship without the calendar feed, that is a spike question for the team, with a written question and a limit of two to three days.
  - The original row keeps its number, records "Split into" with the new numbers in Assumptions & Notes, and Wen Adeyemi confirms the MoSCoW priority of each slice. The split does not set it.

#### Send back to discovery

**RPR-005 Escalate emergency repairs.** This is the third session on the item, and discussion is standing in for an answer.
- Open question: is the promised emergency response time 4 hours or 24 hours? The tenancy agreement and the housing officer's guidance disagree, and engineers declined to estimate until it is settled.
- Owner: the client contact who owns the tenancy terms. I do not know who that is; Wen Adeyemi should name them. Route it through the client contact rather than `synthesize-discovery`, since the answer is a fact held by the co-op, not a research finding.
- Once answered, add the missing Then line to the scenario ("Then the on-call team is notified") and a scenario for the response-time breach. The story is still Draft, so it also needs stakeholder review.

**RPR-006 Match contractor invoices to repairs.** It has no acceptance criteria, no estimate, a Draft status and an untracked dependency, "finance system export". Lior Vance thinks that export may not exist yet.
- Open question: does the finance system produce an invoice export, and with which fields?
- Owner: not known. It needs a finance contact. I proposed a dependency entry in the RAID proposals.
- This is a Could item, so it can wait without harming Monday's sprint.

#### Files

All in `out/refinement/`:

- `readiness-2026-11-04.json`: the report for plan-sprint, in the script's format. Summary: 6 graded, 2 READY, 2 REFINE, 2 DISCOVERY, threshold 5, Small limit 5 days.
- `readiness-2026-11-04.md`: the Markdown report with the per-item reasons above.
- `proposed-raid-entries-2026-11-04.md`: two proposed dependency entries (contractor calendar feed; finance invoice export) and the open question for RPR-005. The RAID log is unchanged.

#### Gaps and assumptions

- The script was not run, and neither was the quality gate or the prose checker, because no scripts can run here. I read the report prose myself against the writing standard. Treat the release gate as outstanding until both are run on the final files.
- I did not change the workbook. Estimates, the corrected dependency and the splits should go in a new requirements version through capture-requirements.
- Sessions counts come from the Refinement Sessions column in the export (RPR-005 is at 3).
- The proposed wording for RPR-003 is a suggestion. Wen Adeyemi decides what goes in the workbook.
