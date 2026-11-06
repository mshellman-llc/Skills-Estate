---
skill: develop-product
title: Turning a volunteer scheduling prototype into a first release
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 4e17a049ee5b802096c8580c78ce35759d159b0a0f11b469339b59a05c2c8f19
---

## Request

We built a volunteer shift-scheduling prototype for our food pantry network last year and want to turn it into something the three pantries can actually use by spring. I've put the prototype README, notes from our September meeting and the coordinator's wish list in inputs/. Can you work out what the product is, what a first release should and shouldn't include, and what we do next?

## Inputs

Run of the built `develop-product` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### coordinator-wishlist.txt

Dana's wish list (Oct 2026), in her order

1. Text reminders the day before a shift
2. Everyone's data in one place, not on my laptop
3. Tell me when someone cancels, and let me find a replacement fast
4. See which drivers are cleared
5. One view across pantries
6. Volunteer hours report for the funder (they ask every June)
7. A rota for the holiday food drive
8. Paper print-out of the week for volunteers without phones
9. Let volunteers swap shifts themselves
10. Photos on volunteer profiles

#### meeting-notes-sept.md

#### Network meeting, 18 Sept 2026

Present: Dana (Eastfield coordinator), Ravi (Northgate coordinator), Imogen (Millbrook coordinator), Tom (board treasurer).

- Eastfield trial: Dana says no-shows fell "noticeably" but nobody counted. She still phones people the night before.
- Ravi: Northgate uses a shared spreadsheet and a WhatsApp group; 70 active volunteers. Wants one view across all three pantries because people volunteer at more than one site.
- Imogen: Millbrook volunteers are mostly over 65; many have no smartphone. Some would need a phone call or a paper sheet.
- Tom: budget for this is £6,000 total, one-off, and no ongoing hosting spend above about £40 a month. Board must approve any spend over £1,000.
- Drivers must have licence and insurance checked before first delivery shift. Dana does it; Ravi says Northgate relies on honesty.
- Agreed: Dana will own product decisions for the pilot; Tom approves money. Target: live at Eastfield and Northgate by 1 April 2027, Millbrook later.
- Open: whether volunteers under 18 may sign up (no policy yet).

#### prototype-readme.md

#### ShiftBasket prototype (v0.3, built Oct 2025)

Single-page web app used in a two-week trial at Eastfield Pantry only.

##### What it does
- Coordinator creates shifts (date, start, end, role, headcount needed).
- Volunteers open a link, pick a name from a dropdown and sign up for a shift. No password.
- Shift page shows "3 of 5 filled".
- Coordinator can export the week as CSV.

##### Roles in the data
Sorter, Driver, Front desk. Drivers have a "licence checked" flag set by hand in the database.

##### Known limits
- Data lives in one browser's local storage per device; the Eastfield laptop was the source of truth.
- No reminders. The SMS reminder screen is a mock-up only (buttons do nothing).
- Cancelling a signup deletes it; nobody is told.
- Not tested with more than 24 volunteers.

## Output

I've written a product home for ShiftBasket with a proposed first release. It's ready for you to review, and nothing in it is accepted yet.

#### What the product is

ShiftBasket helps pantry coordinators fill volunteer shifts and keeps volunteers turning up. The coordinators are Dana, Ravi and Imogen. The volunteers include many people over 65, and some at Millbrook have no smartphone. Tom's board approves money.

Today Dana phones people the night before. Northgate uses a spreadsheet and a WhatsApp group for about 70 volunteers. The prototype keeps its data in one laptop's browser.

**What the prototype can do, from its README:**
- Create shifts and let volunteers sign up.
- Export a week as CSV.
- Hold a hand-set "licence checked" flag for drivers.

**What it can't do:**
- The SMS reminder screen is a mock-up, and its buttons do nothing.
- Cancelling deletes the signup and tells nobody.
- It has no shared storage and no cross-pantry view.

I could only read the README. I haven't seen the code, the database or the trial data, so every "can do" is the README's claim, not something I checked.

#### Proposed first release

**Target and constraints:** live at Eastfield and Northgate by 1 April 2027, which is about 21 weeks away. The budget is £6,000 one-off and about £40 a month to run. Tom approves anything over £1,000. Dana owns product decisions for the pilot.

| Priority | Items |
| --- | --- |
| Must | Shared data store; shifts and signup; day-before text reminders; cancellation notice to the coordinator; driver clearance before a delivery shift |
| Should | Replacement search; cross-pantry view; paper print-out of the week |
| Could | CSV export; hours report for the funder |
| Won't this horizon | Holiday-drive rota; volunteer shift swaps; photos; Millbrook rollout |

**Why these placements:**
- **Shared data** is first because two sites can't run from one laptop.
- **Reminders** are Dana's first priority and the reason for the pilot.
- **The hours report** is only Could because the funder asks in June, after launch. The CSV export plus a spreadsheet covers it until then.
- **Millbrook** comes later, as the September notes say.
- **Everything deferred** stays in the catalogue, each with a reason and a point to revisit.

These placements are my proposal. Nothing becomes a commitment until Dana accepts it.

#### Decisions needed

1. **Dana:** accept or change the priorities above.
2. **Dana, with Ravi:** how are driver licence and insurance checked at Northgate, and can a driver sign up before being cleared? Dana checks today. Ravi says Northgate relies on honesty.
3. **Dana:** how does a volunteer prove who they are? The name dropdown lets anyone book as anyone.
4. **Not assigned in the notes:** can volunteers under 18 sign up? There's no policy yet. This blocks signup design only.
5. **Dana:** you described three pantries by spring, but the September notes say Eastfield and Northgate by 1 April and Millbrook later. Which is the commitment?

#### Gaps and risks

- **SMS cost is unknown.** I can't tell whether reminders for about 70 volunteers fit inside £40 a month. If they don't, reminders drop to Should.
- **There's no no-show baseline.** Dana's "noticeably fewer" wasn't counted, so the benefit of reminders is a hypothesis.
- **Scale is untested.** The trial had 24 volunteers or fewer, and Northgate has about 70.
- **Nobody has compared this against existing scheduling tools.** I make no claim that it's unique, and I picked no technology stack.

#### Next step

I haven't contacted anyone or spent anything. Two things can run alongside the decisions:
- Get a written SMS price for roughly 70 volunteers at about two reminders a week.
- Have the coordinators count no-shows for four weeks.

Once the priorities are accepted, the next stage is designing the journey from creating a shift through reminders, cancellation and replacement. An architecture comparison inside the £40 limit comes with it.

I couldn't compute content hashes for the three input files, so they're identified by path and a full read.

#### File

`out/product-home.md` is the one place to start. It holds:
- Source records for the three inputs.
- The product definition.
- The 13-capability catalogue, with what the README says each can do.
- The 14 proposed release items.
- Decisions D1–D5.
- Risks and contradictions X1–X6.
- Stage gates, which show the decision gate blocked and architecture not yet assessed.
- A "Continue here" section with the next action.

### File: product-home.md

#### ShiftBasket product home

No product index existed, so this file is the home. It links to the three supplied sources and holds the records derived from them. Nothing here has been moved or edited in `inputs/`.

##### Current work

- **Product:** ShiftBasket (PROD-SB), volunteer shift scheduling for a three-pantry food network.
- **Requested outcome and stage:** work out what the product is, propose what a first release includes and excludes, and name the next action. Entry mode: historical product, bounded to one release. Stages 1, 2, 3 (release subset), 4 and 5 are in play; stage 6 onward is not started.
- **Finish line:** a product definition and a proposed release scope that the decider can accept or change. This is "ready for review". Nothing is accepted, built or deployed.
- **Authorized actions:** read the three supplied files and write local records. No outreach, spending, vendor contact or deployment.
- **Source boundary:** S1 `inputs/prototype-readme.md`, S2 `inputs/meeting-notes-sept.md`, S3 `inputs/coordinator-wishlist.txt`. All three were read in full. Content hashes were not computed (no script access in this session); each source is bound by path and the full-text read. The prototype code, its database and the trial data were not supplied and are not reviewed.
- **Conventions and task authority:** none supplied. IDs below are new (S, C, D, R, G, X prefixes).

##### Stage readiness

| Stage | State | Basis |
| --- | --- | --- |
| 1 Boundary | satisfied for the 3-file boundary | G1. Three supplied paths, all classified and read. Wider estate (code, database, trial data) not in scope. |
| 2 Review | satisfied for S1–S3; the prototype itself is unreviewed | G2. Coverage claim is "3 of 3 supplied files, 3 of 3 relevant"; it makes no claim about the code. |
| 3 Reconstruction | applicable as a subset | Behavior is taken from the README only (source_reported). No code or runtime was exercised. |
| 4 Definition | ready for review | G3. Audience, jobs and capabilities are linked; value and demand are unvalidated. |
| 5 Release and architecture | scope proposal ready for review; architecture `not_assessed` | G4. No decision is accepted. No stack was compared or chosen. |
| 6–8 | not_assessed | Design, build and maintenance wait on accepted scope. |

##### Source records

| ID | Location | Family and date | Authority role | Review state |
| --- | --- | --- | --- | --- |
| S1 | `inputs/prototype-readme.md` | README for v0.3, Oct 2025 | Describes the prototype; not current direction | reviewed |
| S2 | `inputs/meeting-notes-sept.md` | Network meeting, 18 Sept 2026 | Holds the only recorded decisions (owner, budget, target date) | reviewed |
| S3 | `inputs/coordinator-wishlist.txt` | Dana's list, Oct 2026 | Priorities of one coordinator; a wish list, not a decision | reviewed |

##### Product definition (proposed, ready for review)

**Audience.** Pantry coordinators (Dana at Eastfield, Ravi at Northgate, Imogen at Millbrook) fill shifts. Volunteers, many of them over 65 and some without smartphones at Millbrook (S2), sign up and show up. The board treasurer (Tom) approves spend (S2). Coordinators and volunteers are the daily users. The board approves money.

**Problem and workaround.** Eastfield coordinator phones people the night before; Northgate runs a spreadsheet and a WhatsApp group for about 70 volunteers (S2). The trial prototype held data in one laptop's browser (S1).

**Jobs.**
- J1 Coordinator fills each shift to its headcount. Trigger: a shift is created. Completion measure: shift filled before it starts.
- J2 Volunteer finds a shift and commits. Constraint: no password, possibly no smartphone.
- J3 Coordinator learns of a cancellation early enough to find a replacement.
- J4 Coordinator confirms a driver is cleared before a first delivery shift (S2: licence and insurance).
- J5 Coordinator answers the funder's yearly hours request (S3, every June).

**Journey in scope for review (JR1).** Coordinator creates shifts → volunteer signs up → volunteer is reminded the day before → volunteer cancels or doesn't come → coordinator is told and fills the gap → coordinator exports hours. Drivers pass a clearance step before the delivery signup. First value: a coordinator stops phoning everyone the night before. Exit and renewal are not applicable to a free internal tool; data retention for departed volunteers is unknown.

**Value hypotheses (none validated).** V1: automated reminders reduce no-shows. Basis: Dana's recollection that no-shows "fell noticeably" (S2). Nobody counted, so there is no baseline; it is a hypothesis. V2: one shared record removes the laptop as a single point of failure (S1 limit, S3 #2). Adoption burden: Northgate must move from spreadsheet and WhatsApp; Millbrook volunteers need a non-smartphone route. Delivery and maintenance cost: unknown beyond the budget envelope (£6,000 one-off, about £40 a month running, board approval above £1,000; S2).

**Differentiation.** Not assessed. No comparison with existing volunteer-scheduling tools was supplied, and none was researched. No uniqueness claim is made.

##### Capability catalogue

"Should" is the desired outcome; "can do" is what S1 reports. Implementation evidence is the README's claim; none of it was exercised here.

| ID | Capability | Can do now (S1) | Implementation evidence | Source |
| --- | --- | --- | --- | --- |
| C1 | Create shifts (date, time, role, headcount) | Yes | code_present (source_reported) | S1 |
| C2 | Volunteer signup by name, no password | Yes; shows "3 of 5 filled" | code_present (source_reported) | S1 |
| C3 | Shared central data store | No: per-browser local storage | intended | S1, S3 #2 |
| C4 | Day-before text reminders | Mock-up only; buttons do nothing | static_demo | S1, S3 #1 |
| C5 | Cancellation notice to coordinator and replacement search | Cancel deletes silently | intended | S1, S3 #3 |
| C6 | Driver clearance | Hand-set "licence checked" flag in the database | code_present (source_reported); insurance not covered | S1, S2, S3 #4 |
| C7 | Cross-pantry view | No | intended | S2, S3 #5 |
| C8 | Volunteer hours report | No; weekly CSV only | intended | S3 #6 |
| C9 | CSV export of the week | Yes | code_present (source_reported) | S1 |
| C10 | Holiday food-drive rota | No | intended | S3 #7 |
| C11 | Paper print-out of the week | No | intended | S2, S3 #8 |
| C12 | Volunteer-initiated shift swap | No | intended | S3 #9 |
| C13 | Volunteer photos | No | intended | S3 #10 |

##### Proposed release R1 (every item `proposed`, none accepted)

**Horizon and outcome.** Live at Eastfield and Northgate by 1 April 2027 (S2, agreed in the meeting; roughly 21 weeks from 4 Nov 2026). Outcome: both coordinators run their weekly rota in ShiftBasket instead of phone calls, spreadsheet and WhatsApp. Constraints: £6,000 one-off, about £40 a month running, board approval above £1,000 (S2). The decider for product scope is Dana; Tom decides money (S2).

| Release item | Capability | Proposed priority | Rationale and dependency | If not included |
| --- | --- | --- | --- | --- |
| R1-01 | C3 shared data | Must | Two sites cannot share rotas from one laptop's local storage. Everything else depends on it. | — |
| R1-02 | C1, C2 shifts and signup | Must | The core job. Identity without passwords needs a decision (D3). | — |
| R1-03 | C4 reminders | Must | Dana's first priority and the stated reason for the pilot. Depends on an SMS cost check (X1) staying inside £40 a month. | If SMS fits no budget: Should, with coordinator phone list printed from C11. |
| R1-04 | C5 cancellation notice (coordinator told) | Must | Silent deletion defeats J3. | — |
| R1-05 | C5 replacement search | Should | Coordinator can use the shift list as a workaround. | Reconsider after one month of cancellation data. |
| R1-06 | C6 driver clearance | Must | S2 requires checks before the first delivery shift; Northgate has no process today. Needs D2. | — |
| R1-07 | C7 cross-pantry view | Should | Real need at Northgate (S2) but Dana ranks it fifth. Workaround: separate site views, volunteers check both. | Reconsider if double-booking appears. |
| R1-08 | C11 paper print-out | Should | Cheap and serves volunteers without phones. Millbrook, where the need is greatest, is not in R1. | Reconsider when Millbrook is scheduled. |
| R1-09 | C9 CSV export | Could | Exists in the prototype; keep if cheap. | — |
| R1-10 | C8 hours report | Could | Funder asks in June, after launch. CSV export plus a spreadsheet is the workaround. | Trigger: May, if the CSV workaround proves too slow. |
| R1-11 | C10 holiday rota | Won't this horizon | Drive falls after the April launch. | Reconsider in September 2027. |
| R1-12 | C12 shift swap | Won't this horizon | Needs identity and rules not yet decided. | After D3 and one quarter of use. |
| R1-13 | C13 photos | Won't this horizon | No stated outcome; adds a privacy question. | Only on a stated need. |

[trimmed: the rest of this file, about 724 more words, is not shown]
