---
skill: manage-decision-register
title: Decision register from refinement notes and a client email
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: f4625f40a6198c4297a44a4df43ef2ab2669e146d612f295ccef81fd50616341
---

## Request

Here are my notes from the 29 October refinement session and the follow-up email from the client. Please turn the open questions into a decision register grouped by epic, tell me which have no owner, and prepare the export so I can send it to their team for the tracker.

## Inputs

Run of the built `manage-decision-register` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### refinement-notes-2026-10-29.md

#### Refinement notes, 29 October 2026
Repairs portal release 1. Epics: RP-10 Report a repair, RP-20 Contractor scheduling, RP-30 Contractor invoicing.

##### RP-10 Report a repair
- Photos: how many can a tenant attach? Team suggests 5 at 10 MB each. Priya Nand (Housing Operations) to confirm. Affects RP-112 (photo upload).
- Emergency repairs (gas leak, no heating with vulnerable occupant): does the form show the emergency phone number and stop, or still take the report? Nobody took this away. Affects RP-115.
- Do tenants without an account report as a guest? Tomasz Weber (Digital) said guest reporting is out for release 1 and will be revisited after launch. RP-118.

##### RP-20 Contractor scheduling
- Appointment slots: half-day (AM/PM) or fixed two-hour windows? Priya Nand says contractors only work AM/PM today. Team has not confirmed. RP-131, story "Book a slot".
- What happens when a contractor misses an appointment? Waiting on the contractor framework review, which Housing Operations says is not finished. Blocked until then. RP-134.
- Text-message reminders: depends on whether the SMS provider contract covers the portal. Ana Cordeiro (Procurement) is checking. RP-136.

##### RP-30 Contractor invoicing
- Does an invoice need the tenant's sign-off before payment? Open, no owner agreed. RP-142.
- Can contractors invoice per visit, or only per job? Not discussed beyond mention.
- Sandbox: confirm the finance system's test environment accepts our purchase-order format. Needs a run in the sandbox. RP-145.

#### Follow-up email from Priya Nand, 2 November
Hi, thanks for Thursday. On photos, decision: "maximum 4 photos per repair, 8 MB each, no video". On slots, we'll look at half-day vs two-hour again once the contractors have been asked, so don't treat that as settled. Also for the invoice sign-off, Finance are meeting next week and will come back.

## Output

I recorded nine questions across the three epics. One is answered, and five have no owner. The export is prepared locally and nothing has been sent or imported.

#### Register

| Epic | Question | Status | Owner | Ticket |
|---|---|---|---|---|
| RP-10 Report a repair | Photo count and size limit | Answered | Priya Nand | RP-112 |
| RP-10 | Emergency repairs: show the phone number and stop, or still take the report? | Open | none | RP-115 |
| RP-10 | Guest reporting for tenants without an account | Deferred | Tomasz Weber | RP-118 |
| RP-20 Contractor scheduling | Half-day or two-hour slots | Proposed | Priya Nand | RP-131 |
| RP-20 | Contractor misses an appointment | Blocked | none | RP-134 |
| RP-20 | SMS contract covers portal reminders | Blocked | Ana Cordeiro | RP-136 |
| RP-30 Contractor invoicing | Tenant sign-off before payment | Open | none | RP-142 |
| RP-30 | Invoice per visit or per job | Open | none | none |
| RP-30 | Test environment accepts our purchase-order format | Sandbox check | none | RP-145 |

By status: Open 3, Blocked 2, Answered 1, Proposed 1, Deferred 1, Sandbox check 1.

#### Judgement calls

- **Photos is the only recorded answer.** Priya's 2 November email states it, so I kept her words: "maximum 4 photos per repair, 8 MB each, no video". It replaces the team's 5 photos at 10 MB suggestion.
- **Slots stay Proposed.** The notes say contractors work AM/PM today, and I recorded half-day as the proposed answer. Priya's email says not to treat it as settled, so it is not marked Answered.
- **Invoice sign-off stays Open.** The email only says Finance will come back after their meeting next week. That mentions the topic without recording a decision.
- **Guest reporting is Deferred, with Tomasz Weber as owner.** The notes show him stating the position. If he is not the person who should answer it, clear the owner.
- **Missed appointments has no owner.** The notes say Housing Operations has not finished the contractor framework review, but that is a team, not a named person, so I left the owner blank.
- **Emergency repairs, invoice sign-off, per-visit invoicing and the sandbox check** have no owner in the sources. I did not assign one. Please name someone, or tell me who.

#### Checks

I could not run `decisions.py check`, so I applied its rules by hand. Every question has a known group (RP-10, RP-20 or RP-30), and no question id is repeated. I could not check tickets because there is no tracker export, so the RP-112 to RP-145 keys are unverified against the tracker. I also left the `stories` lists empty. The notes mention a "Book a slot" story, but no story id was supplied.

#### Export

I followed the export rules by hand. No saved answers from the published page were available, so both files use the authored statuses and answers. The CSV has one row per question and ticket. `q-granularity` has no ticket, so its issue key is blank and the tracker import will need to handle that row.

Before importing, please confirm with the client that they want the file brought into their tracker. That step is theirs to approve.

#### Files

- `out/content/questions.json`: the register, in the `questions.json` format.
- `out/exports/decisions.csv`: columns Issue key, Question id, Question, Status, Answer, Conditions, Updated. Nine rows.
- `out/exports/decisions.md`: decision log grouped by epic. For example, under Report a repair it reads: "How many photos can a tenant attach to a repair, and how large can each be? (Answered). Answer: maximum 4 photos per repair, 8 MB each, no video. Tickets: RP-112".
