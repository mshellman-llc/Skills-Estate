---
skill: deck-builder
title: Pilot approval deck for tablet check-in at two food pantry sites
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: f0f27ea1b6fa2ed0bbffa39963b983d4363de43470336f9cae9fdaa435113acb
---

## Request

Please build a deck for our board operations committee asking them to approve a six-week pilot of tablet check-in at two of our pantry sites. The brief and my pilot notes are in the inputs folder; the committee will read it ahead of the meeting rather than watch me present.

## Inputs

Run of the built `deck-builder` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### brief.md

#### Brief: tablet check-in pilot

Organisation: Tidewater Pantry Network (5 sites, mostly volunteer-run).

Audience: board operations committee. Chair Priya Anand; operations director Tomasz Wells; volunteer coordinator Ife Okafor. They have seen the paper sign-in sheets but have not seen the vendor's app.

Decision wanted: approve a six-week pilot at Eastgate and Mill Road, 6 Jan to 16 Feb 2027, with a spending cap of $4,200. Committee meets 18 Nov 2026.

Rule we enforce: a household may visit at most 2 times per calendar month.

Concerns the committee has raised before:
- Volunteers are not technical and turnover is high.
- Mill Road wifi is unreliable.
- No home addresses should sit on the tablets.
- Nobody wants a family turned away because of a software error.

The deck will be emailed in advance. Paper sign-in stays running alongside the tablets for the whole pilot.

#### pilot-notes.txt

PILOT NOTES (Tomasz's working notes, Oct 2026)

September 2026 audit of paper sheets, two sites:
- Eastgate: 236 visits, 17 over the 2-per-month cap.
- Mill Road: 176 visits, 14 over the cap.
- Total 412 visits, 31 over the cap. Cap is checked by hand at month end, so these were found weeks after the visit.

Wifi: Mill Road lost connection in 5 of 12 observed Saturday sessions. Eastgate stayed connected in all 12 observed sessions.

Vendor (app called "TallyDesk"):
- Tablets work offline and sync when wifi returns.
- Vendor documentation says that when two tablets sync changes to the same household record, "the most recent sync wins". We have not tested this and have not asked the vendor what it means for visit counts.
- Household record can be set to ID number and first name only; no address needed.

Our proposed handling (not yet confirmed with vendor): each tablet saves every visit as its own entry with tablet ID and time. The shared record counts entries after sync. A household with more than 2 entries in the month is flagged to the coordinator the next morning. Nobody is refused at the door on the basis of tablet data during the pilot.

Pilot costs (estimates):
- 4 tablets at $450 each
- Licence $60 per site per month, 2 sites, 2 billing months
- Volunteer training $600
Spending cap approved to ask for: $4,200.

Proposed pass test: after six weeks, every paper-sheet visit at the two sites appears in the tablet record, and every household over the cap is flagged within one day.

## Output

I've built the seven-slide reading deck as editable HTML, but I haven't seen it rendered or run any checks. This environment couldn't run scripts or open a browser. I wrote the HTML by hand, following the bundled `deck.css` rules, rather than running `build_html.py`. Please open it at 1280×720 and print to PDF before it goes to the committee.

**Main claim:** Approve the six-week, two-site pilot, and start it only after the vendor confirms in writing that two offline visits for one household are both kept.

I made the vendor question the centre of the deck because it is the one risk that could make tablets worse than paper. Your notes say the vendor's documentation reads "the most recent sync wins", and nobody has tested what that does to visit counts. Two tablets that were offline could each log a second visit for the same household. Keeping only the last sync would then show 2 visits when the household has made 3, and the over-cap visit would go unnoticed.

#### The deck

| # | Title | Visual |
|---|---|---|
| 1 | Approve a six-week tablet pilot, starting only after the vendor answers one question | Table of the request |
| 2 | Paper finds households over the visit cap weeks after the visit | Bar chart: 17 (Eastgate) and 14 (Mill Road) over-cap visits in September, on a 0–20 scale |
| 3 | Offline tablets could each accept a visit that together exceeds the cap | Sequence diagram: Shared record, Tablet A, Tablet B |
| 4 | Save every visit as its own entry, count after sync, flag the next morning | Flow with one decision ("More than 2 this month?") |
| 5 | Four tests decide whether the pilot passed | Table: test, expected result, record to keep |
| 6 | The pilot costs an estimated $2,640 and paper stays in place | Cost table |
| 7 | Vote on 18 November; start on 6 January only if the vendor says yes | Owners and dates table |

Figures reconciled against your notes:
- 17 + 14 = 31 over-cap visits, out of 236 + 176 = 412 visits.
- Costs: $1,800 + $240 + $600 = $2,640, which leaves $1,560 under the $4,200 cap.
- Mill Road lost its connection in 5 of 12 observed sessions, and Eastgate in none of 12.

Some things are labelled as proposed or estimated rather than established:
- Slide 4's handling (each visit saved as its own entry, counted after sync) comes from your notes and is not confirmed with the vendor.
- The pass tests have not been run.
- The costs are estimates.
- H-210 on slide 3 is an illustrative household.

Your four concerns appear as follows:
- **Mill Road wifi:** slides 3 and 5.
- **No addresses on tablets:** slide 6, which proposes the ID-and-first-name setting.
- **Nobody refused at the door:** slides 1 and 6.
- **Non-technical volunteers:** slide 5, as a new-volunteer test with a help log.

#### Gaps and assumptions to check
- **Owners and dates:** on slide 7, Tomasz Wells for the vendor question and the run, and Ife Okafor for training, are my proposals. So is the 2 Dec 2026 target for the vendor's answer. Please confirm them with the people named. The results review has no date yet.
- **Brand:** you gave no brand profile, so the deck uses the neutral Baseline profile (navy accent, Inter with system fallback, no logo). I worked that out by hand from the brand rules.
- **Training and licences:** I took the $600 training cost and the 2 billing months of licences straight from your notes. Please check that 2 months is right for a six-week pilot.
- **Not run:** the writing and brand checkers and the quality-gate receipt. I reviewed the writing by hand, including every title in order and every figure.
- **Layout risks:** the most likely overflow is slides 5, 6 and 7, which have long tables. Slide 3's diagram labels and slide 4's diamond text also need a look.
- **Input JSON:** I didn't generate the deck's input JSON, so the bundled collision checks haven't run. The storyboard is in `03_structure.md` and `04_copy.md`.

#### Files (all in `out/deck/`)
- `deck.html`: the deck, with live text and SVG diagrams.
- `00_brief.md`, `01_one_message.md`, `02_submessages.md`, `03_structure.md`, `04_copy.md`: the stage records, saved before the build.
- `05_design_notes.md`: the brand profile used and how it was applied.
- `06_polish_todo.md`: the fixes to verify on the rendered slides, with locations.
- `polish-learnings.md`: the project copy of the polish rules.
