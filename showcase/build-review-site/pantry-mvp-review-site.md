---
skill: build-review-site
title: Review site for a food pantry check-in MVP
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: ebef4607fe151c273003a3065e535d5fb21353e91687bca81207c110e34b8277
---

## Request

Build a review site for our pantry check-in MVP from the attached Jira export and refinement notes, ready for Thursday's MoSCoW review with the board. The class definitions and the 60% Must limit are in the notes.

## Inputs

Run of the built `build-review-site` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### jira-2026-11-02.csv

Summary,Issue key,Issue id,Issue Type,Status,Priority,Created,Updated,Sprint,Sprint,Labels,Labels,Description,Custom field (Story point estimate),Inward issue link (Blocks),Inward issue link (Blocks),Outward issue link (Blocks),Parent,Parent key,Parent summary,Comment
Client check-in,AV-1,2001,Epic,In Progress,Medium,02-Oct-26 09:00 AM,30-Oct-26 10:00 AM,,,,,,,,,,,,,
Pantry stock,AV-2,2002,Epic,In Progress,Medium,02-Oct-26 09:00 AM,30-Oct-26 10:00 AM,,,,,,,,,,,,,
Pickup day,AV-3,2003,Epic,To Do,Medium,02-Oct-26 09:00 AM,30-Oct-26 10:00 AM,,,,,,,,,,,,,
Register a household,AV-11,2011,Story,Done,Medium,02-Oct-26 09:00 AM,28-Oct-26 04:00 PM,Sprint 1,,,,"*Acceptance Criteria*
#### A household needs a name, a postcode and a size.",3,,,AV-12,2001,AV-1,Client check-in,
Check in at the desk,AV-12,2012,Story,In Progress,Medium,02-Oct-26 09:00 AM,30-Oct-26 11:00 AM,Sprint 2,,,,"*Acceptance Criteria*
#### A volunteer finds a household by name and records the visit.",2,AV-11,,,2001,AV-1,Client check-in,
Visit limit warning,AV-13,2013,Story,To Do,Medium,02-Oct-26 09:00 AM,29-Oct-26 09:00 AM,Sprint 2,,,,"*Acceptance Criteria*
#### The desk screen warns when a household has visited twice this month.",,,,,2001,AV-1,Client check-in,
Log a donation delivery,AV-21,2021,Story,In Review,Medium,02-Oct-26 09:00 AM,30-Oct-26 02:00 PM,Sprint 2,,,,"*Acceptance Criteria*
#### A delivery records donor, items and a received date.",5,,,AV-22,2002,AV-2,Pantry stock,
Expiry date alerts,AV-22,2022,Story,To Do,Medium,02-Oct-26 09:00 AM,29-Oct-26 10:00 AM,Sprint 3,,,,"*Acceptance Criteria*
#### Items expiring within 7 days show on a list.",3,AV-21,,,2002,AV-2,Pantry stock,
Scan item barcodes,AV-23,2023,Story,Canceled,Medium,02-Oct-26 09:00 AM,20-Oct-26 03:00 PM,,,,,,,,,,2002,AV-2,Pantry stock,
Volunteer shift sign-up,AV-24,2024,Story,Needs Refinement,Medium,02-Oct-26 09:00 AM,27-Oct-26 08:00 AM,,,,,,,,,,2003,AV-3,Pickup day,
Pickup-day packing list,AV-31,2031,Story,To Do,Medium,02-Oct-26 09:00 AM,30-Oct-26 09:00 AM,Sprint 3,,,,"*Acceptance Criteria*
#### The list shows each booked household and its size.",2,,,,2003,AV-3,Pickup day,
Reminder texts,AV-32,2032,Story,To Do,Medium,02-Oct-26 09:00 AM,29-Oct-26 09:00 AM,,,,,,3,,,,2003,AV-3,Pickup day,

#### refinement-notes.md

#### Refinement notes, 29 October 2026
Alder Valley Food Share. Priya (operations), Tomas (stock lead), Hannah (board).

##### Classes
- Must: we cannot open the new desk without it.
- Should: volunteers can work around it on paper.
- Could: if time allows.
- Won't: next release.
- Must points stay under 60% of open points.

##### Decisions
- Register, check-in, donation logging and packing list are Must.
- Visit limit warning and expiry alerts are Should.
- Reminder texts are Won't this release.
- Volunteer training before opening day is Must. No ticket yet.
- Shift sign-up is not classed. Hannah decides after the board meets.

##### Roles
- Desk volunteer: finds the household, records the visit. Today: paper sign-in sheet; a lead checks the monthly limit from memory.
- Stock lead: receives deliveries. Today: shared spreadsheet; expiry dates checked by walking the shelves.
- Packer: builds boxes on pickup day. Today: handwritten list from the desk.

##### Questions
1. Does the limit count Saturday pop-up visits? Priya. Open.
2. Who sets the threshold if it is not two visits? Proposed: Priya. Tomas agrees.
3. Do regional food bank donations need a different record? Tomas. Open.
4. Barcode scanning was canceled: the tablets have no camera. Deferred.
5. Is the packing list printed or on a tablet? Priya. Open.

## Output

I've written the source files for the pantry check-in review site. I haven't rendered, checked or published it. This environment can't run `review_site.py`, so the build, the `check` gates and the publish step are still to do. The files are in `out/build-review-site/`. The tracker export the site is built from is `jira-2026-11-02.csv`.

#### The main finding for Thursday

Must work is **75%** of open points, against your 60% limit. This is my hand calculation, not a script result.

| Class | Open tickets | Points |
|---|---|---|
| Must | Check in at the desk (2), Log a donation delivery (5), Pickup-day packing list (2) | 9 |
| Should | Expiry date alerts (3), Visit limit warning (no estimate) | 3 |
| Could | none | 0 |

- 9 of 12 open Must, Should and Could points is 75%.
- Register a household (Done) and Reminder texts (Won't) are not counted.
- Visit limit warning has no estimate, so the real figure is slightly lower. The page counts it separately as an unestimated Should.
- Volunteer training is a Must with no ticket, so it adds no points yet. Once it has an estimate, the share goes up.

The board will need to move a Must down or accept a higher limit. I haven't changed any class.

#### What the site contains

I used four pages: Scope, Decisions, Workflow and Build. I left out Mockups because no mockup files were supplied. The brand profile is unset, so the estate's neutral profile applies.

**Scope** has 8 stories on a map with three steps (Check in a household, Receive stock, Pickup day):

| Story | Class | Ticket | Status in the export |
|---|---|---|---|
| Register a household | Must | AV-11 | Done |
| Check in at the desk | Must | AV-12 | In Progress |
| Visit limit warning | Should | AV-13 | To Do, no estimate |
| Log a donation delivery | Must | AV-21 | In Review |
| Expiry date alerts | Should | AV-22 | To Do, blocked by AV-21 |
| Pickup-day packing list | Must | AV-31 | To Do |
| Reminder texts | Won't | AV-32 | To Do |
| Volunteer training | Must | none, planned in AV-3 | not in the tracker |

**Decisions** has five questions grouped by epic:
- Open: whether the monthly limit counts Saturday pop-up visits (Priya), whether regional food bank donations need a different record (Tomas), and whether the packing list is printed or on a tablet (Priya).
- Proposed: Priya sets the warning threshold, and Tomas agrees.
- Deferred: barcode scanning, because the tablets have no camera.

**Workflow** has three roles (Desk volunteer, Stock lead, Packer) with today's behavior from your notes. A today-versus-after table has three rows: checking in, stock and packing. I recorded only what the notes and tickets support.

**Build** has three lanes (Check-in, Stock, Pickup day) with seven steps. Each step names its tickets. I left the design section empty because the sources have no design records.

#### Tickets and classes that need attention

- **Volunteer shift sign-up (AV-24):** not classed. Your notes say Hannah decides after the board meets, so it stays in "Not yet classed". This is a next action on the Scope page.
- **Volunteer training:** a Must with no ticket. A next action asks for one to be created.
- **Scan item barcodes (AV-23):** canceled. I did not map it to a story. It appears only in the deferred barcode question. Please confirm it was canceled, not merged into another ticket.
- **Needs Refinement:** this status was unknown to the tracker adapter. I mapped it to `todo` in `config/site.json`, which is what the adapter would have done by default. Tell me if it should count as something else.

#### Readiness I expect when it is built

- Visit limit warning: no estimate, and two open questions.
- Expiry date alerts: blocked by Log a donation delivery, which is still In Review.
- Log a donation delivery and Pickup-day packing list: each has an open question.
- Reminder texts: no acceptance criteria in the export.

#### Questions still open with no owner

None. Every open question has an owner. Barcode scanning is deferred and has no owner, which is fine for a deferred item. No tracker import is planned.

#### Gaps and assumptions

- I couldn't run the build, so `tracker/tickets.json` and `dist/` don't exist yet. The gates (D1, D2, D3, W1 and the browser rules) have not run.
- I checked the authored text for the writing standard by reading it, not with `writing_check.py`.
- The browser checks and the desktop and phone reading pass are pending.
- There was no one to ask, so I made two assumptions: "open" points exclude Done, Canceled and Won't tickets, and the "twice this month" threshold in the AV-13 acceptance criteria is the ticket's, not a new rule.
- Nothing is published or shared. When it is, it will go out as a private artifact with shared answers, class reviews and comments. Sharing with the board is your action.

#### Files

All paths are under `out/build-review-site/`.

- `config/site.json`: title "Pantry check-in MVP"; the `jira-csv` adapter; the roles; the four class definitions in your words; release epics AV-1, AV-2 and AV-3; a Must limit of 0.6; the readiness rules (acceptance criteria, estimate, no open questions, no blocked dependency); three next actions; and two sources.
- `content/stories.json`: the 8 stories above, with Check in at the desk depending on Register a household and Expiry date alerts depending on Log a donation delivery.
- `content/questions.json`: the 5 questions above.
- `content/journeys.json`: the three roles and the three-row today-versus-after table.
- `content/processes.json`: three lanes and seven steps.

Next, I would copy `jira-2026-11-02.csv` into `tracker/`, run `build` and `check`, fix any failures, and read each page at desktop and phone width before publishing.
