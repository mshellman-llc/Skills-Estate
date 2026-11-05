---
skill: playbook-builder
title: Add a paid metrics workshop between a free check and a rebuild
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 733792bc5580e8b71e491f7ef69287e99ff5db1e4eceafed0324fd0a8f49d93b
---

## Request

We want to add a new paid offering to our catalog (catalog.md, with my notes in notes.md): a short metrics definition workshop that sits between the free health check and the rebuild project. Can you define it and write the entry in our house format, and tell me if it's really a separate offering or just overlaps with 01 or 02?

## Inputs

Run of the built `service-offering` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### catalog.md

#### Larkfield Analytics service catalog

Version 1.2 (one-pagers omitted from this paste for length)

##### 01 · Reporting Health Check (free)

**In scope**
- One 45-minute call with the head of finance or operations
- Review of up to three existing management reports

**Out of scope**
- Changes to any report (route to play 02)
- Data cleanup (route to play 02)

**Deliverables promised**
- One-page findings note

**Business value**
- Client sees where reports disagree with each other
- Qualifies buyers for play 02

**Target buyer**
- Finance or operations lead at a 50 to 300 person company whose monthly reports are disputed in meetings

###### Tldr
A free call and a one-page note on why your reports disagree. Leads to play 02.

---

##### 02 · Reporting Rebuild Project (paid, project fee)

**In scope**
- Rebuild of the monthly management pack on the client's warehouse
- Metric definitions, data models, dashboards, handover training

**Out of scope**
- Ongoing report support (route to a retainer)
- Source system replacement (route to client's IT)

**Deliverables promised**
- Rebuilt monthly pack, metric dictionary, model documentation

**Business value**
- One agreed set of numbers in the monthly meeting

**Target buyer**
- Finance or operations lead with budget authority and a warehouse already in place

###### Tldr
A full rebuild of the monthly pack on one agreed set of definitions.

---

#### notes.md

#### Notes on the metrics workshop idea

- Clients keep saying "we can't start the rebuild until finance and sales agree what revenue, active customer and churn mean."
- Three of our last five rebuilds lost the first month to definition arguments.
- Idea: a paid workshop, two half-day sessions, run by one senior consultant plus one analyst, with the finance lead, a sales or ops lead and one data owner in the room.
- Output: a signed-off metric dictionary for the 8 to 12 metrics that appear in the monthly pack, with owner and calculation for each.
- Not building anything. No dashboards, no models, no data fixes.
- If they sign off the dictionary, the rebuild starts with definitions done, so the rebuild should run faster. I would like to credit part of the workshop fee against a rebuild if they sign within a set window. Not decided.
- Price: not decided. Hamza thinks fixed fee, Priya thinks day rate. Nobody has costed it.
- Some clients have no warehouse yet, so the workshop may be useful to them before play 02 is possible.
- Worry: the metric dictionary is already a deliverable of play 02. Is this just play 02 split in half?

## Output

#### Short answer

The workshop is a separate offering. Keep it as play 03, between the free check (01) and the rebuild (02). It is not a duplicate of either, but it does overlap with 02 on one deliverable, and that boundary needed fixing.

The entry is written in your house format and saved as an updated catalog. The fee, any rebuild credit and a few delivery details are left open for you to decide.

#### Does it overlap with 01 or 02?

I put the new offering next to each existing play on the seven questions.

| | 01 Health Check | 02 Rebuild | 03 Workshop |
| --- | --- | --- | --- |
| Tier | Free | Paid project | Paid, fee open |
| Buyer | Finance or ops lead | Finance or ops lead with budget and a warehouse | Finance or ops lead who can approve a fee; no warehouse needed |
| Work | 45-minute call, review of up to 3 reports | Build the pack, models, dashboards, training | Two half-day sessions to agree 8 to 12 metrics |
| Output | One-page note | Pack, metric dictionary, model docs | Signed-off metric dictionary |

- **Against 01:** different tier and different work. 01 diagnoses and is free. 03 is paid and produces an agreement. No collision.
- **Against 02:** the slot differs (earlier rung, different buyer condition, no warehouse required), so it is a different rung and both stay. The real overlap is the metric dictionary, which 02 already promises. Your worry that this is 02 split in half is half right, so the boundary has to be explicit.
- **How I handled it:** play 03 owns the facilitated sign-off of disputed definitions. I added one out-of-scope line to play 02 that routes that work to 03. I left 02's in-scope line "Metric definitions" alone, because shrinking it changes what existing clients were sold. That is a decision for you (see below).

#### What I did to the catalog

File: `out/catalog-v1.3.md`

- Play 01: unchanged.
- Play 02: one added out-of-scope bullet: "Facilitated sign-off of metric definitions that departments dispute (route to play 03, which can run before this play)".
- Play 03: new entry with the five fact blocks, Tldr, Eli5, internal one-pager and external one-pager.
- Preamble: version bumped from 1.2 to 1.3, with a revision note stating what changed and what is still open.

**Verification.** I cannot run `scripts/verify_corpus.py` here, so I did the check by hand using its rules. I compared 01 and 02 against `inputs/catalog.md` line by line. Play 01 is identical. Play 02 differs only by the one declared bullet. The preamble differs only in the version number and the added revision note. The check confirms the untouched text is unchanged. It does not confirm that play 03 is right, so the grounding review below is separate.

#### Play 03 in brief

**Tldr:** Two half-day sessions that end with a signed-off dictionary of 8 to 12 metrics your departments agree on. It is the step before the rebuild in play 02.

**Eli5:** Before a game starts, everyone agrees what counts as a point. This workshop gets finance and sales in one room to write the rules down and sign them, so nobody argues about the score later.

**Seven questions, with maturity:**

| Question | Answer | Status |
| --- | --- | --- |
| Who | Finance or ops lead who can approve a fee; sales or ops lead accepted as sponsor. Disqualify where nobody disagrees, or where the client wants dashboards built in the same engagement | open (company size and the no-disagreement disqualifier are inferred) |
| What | Paid two-session workshop producing a signed metric dictionary. Not a build, audit or report review | locked |
| Why they care | Meetings stop stalling on what a number means; one owner and one calculation per metric; works before any warehouse exists | locked |
| Why we care | Removes the definition dispute that cost three of five recent rebuilds their first month; qualifies buyers for 02; reaches clients with no warehouse. Handoff is the signed dictionary | open (rebuild credit undecided) |
| Included | 2 half-day sessions, 3 client attendees, 8 to 12 metrics each with owner and calculation, sign-off | locked |
| Not included | Dashboards, models, data fixes (02); report review (01); over 12 metrics or extra sessions (change order); warehouse work (client IT); dictionary upkeep (retainer). Last three inferred | open |
| Delivery | One senior consultant and one analyst; timing between sessions, prep effort and format not given | open |

The offering is not ready to sell until all seven are locked.

**External one-pager.** It drops "why should we care", has no pipeline or credit language, and says only what the fact blocks say. Its exclusions route to the Reporting Rebuild Project, the free Reporting Health Check, a change, and a retainer. Delivery reads "We agree dates and format with you when you book."

#### Decisions to lock

1. **Fee and structure.** Fixed fee (Hamza) or day rate (Priya). Nobody has costed it, so the entry carries no figure. The heading says "fee open". Until someone costs the two sessions plus preparation, any number would be invented.
2. **Rebuild credit.** Whether part of the workshop fee is credited against play 02 if the client signs within a window, and the size of the credit and the window. Not decided, so it appears nowhere in the external copy.
3. **Play 02's "Metric definitions" scope line.** When a client arrives with a signed dictionary, should 02 shrink to validating and implementing it, with a corresponding price effect? I left 02 as sold.
4. **Numbering.** I took 03 so that nothing is renumbered. By ladder position it could sit between 01 and 02, but that would renumber 02 and every "(see play 02)" reference, including in play 01's text. If your CRM or worksheets use the same numbers, say which scheme is canonical.
5. **Delivery details.** Days between sessions, preparation effort, and on site or remote.
6. **Inferred boundaries.** Over 12 metrics, warehouse work, and dictionary upkeep are marked `(inferred)` because your notes did not state them. Confirm or strike them.
7. **Company profile.** I assumed the 50 to 300 person profile from 01 and 02. Confirm.
8. **Speed claim.** The notes say the rebuild "should run faster". There is no measured figure, so the entry calls it an expectation and quotes no time saving. The "three of our last five rebuilds" fact appears only in the internal copy. Keep it out of anything a client sees.
9. **Contract home.** Boundaries need a letter of engagement or SOW to bind them. I have not drafted one.

#### Checks and limits

- **Voice:** no em dashes, and I read the entry for antithesis flips, trailing "-ing" benefit clauses and filler openers. I could not run the bundled prose or writing checkers, so this was a manual read only. A scanner pass is still outstanding.
- **Brand and rendering:** you asked for a catalog entry, not a PDF handout, so I did not run the one-pager renderer or the brand preflight. If you want the two one-pagers as formatted internal and external documents, that is a separate rendering step on this entry.
- **Source limits:** the pasted catalog omitted the one-pagers for 01 and 02, so I could not check them against the new boundary. Please confirm that neither says anything about metric definitions that conflicts with 03.

#### Files

- `out/catalog-v1.3.md`: updated catalog (01 verbatim, 02 plus one bullet, new 03, version 1.3 and revision note)
- `out/answer.md`: this reply

### File: catalog-v1.3.md

#### Larkfield Analytics service catalog

Version 1.3 (one-pagers omitted from this paste for length)

Revision note (v1.3): added play 03, Metrics Definition Workshop. Play 02 gained one out-of-scope line that names play 03 as the step before it. Play 01 is unchanged. Open: fee, rebuild credit, number of days between sessions, and whether play 02's "Metric definitions" scope line should shrink when a signed-off dictionary exists. See the decisions list delivered with this file.

##### 01 · Reporting Health Check (free)

**In scope**
- One 45-minute call with the head of finance or operations
- Review of up to three existing management reports

**Out of scope**
- Changes to any report (route to play 02)
- Data cleanup (route to play 02)

**Deliverables promised**
- One-page findings note

**Business value**
- Client sees where reports disagree with each other
- Qualifies buyers for play 02

**Target buyer**
- Finance or operations lead at a 50 to 300 person company whose monthly reports are disputed in meetings

###### Tldr
A free call and a one-page note on why your reports disagree. Leads to play 02.

---

##### 02 · Reporting Rebuild Project (paid, project fee)

**In scope**
- Rebuild of the monthly management pack on the client's warehouse
- Metric definitions, data models, dashboards, handover training

**Out of scope**
- Ongoing report support (route to a retainer)
- Source system replacement (route to client's IT)
- Facilitated sign-off of metric definitions that departments dispute (route to play 03, which can run before this play)

**Deliverables promised**
- Rebuilt monthly pack, metric dictionary, model documentation

**Business value**
- One agreed set of numbers in the monthly meeting

**Target buyer**
- Finance or operations lead with budget authority and a warehouse already in place

###### Tldr
A full rebuild of the monthly pack on one agreed set of definitions.

---

##### 03 · Metrics Definition Workshop (paid, fee open)

**In scope**
- Two half-day facilitated sessions
- Attendees: the finance lead, a sales or operations lead, and one data owner
- Agreement on 8 to 12 metrics that appear in the monthly pack (for example revenue, active customer, churn), with a named owner and a written calculation for each
- Sign-off of the resulting dictionary by the attendees

**Out of scope**
- Dashboards, data models and report changes (route to play 02)
- Data fixes and cleanup (route to play 02)
- Warehouse setup or source system replacement (route to client's IT) (inferred, mirrors play 02)
- More than 12 metrics, or extra sessions (change order) (inferred)
- Ongoing upkeep of the dictionary after sign-off (route to a retainer) (inferred, mirrors play 02)
- Review of existing reports (route to play 01, free)

**Deliverables promised**
- Signed-off metric dictionary: metric name, owner, calculation, for 8 to 12 metrics

**Business value**
- Finance and sales stop arguing in the monthly meeting about what a number means
- The client can start a rebuild with definitions already settled
- Useful to a client with no warehouse yet, because it needs no data platform
- Commercial: removes the definition dispute that cost three of our last five rebuilds their first month; qualifies buyers for play 02

**Target buyer**
- Finance or operations lead who can approve a fee and has two other departments disagreeing on core numbers
- Same company profile as plays 01 and 02 (50 to 300 people) (inferred)
- Accepted sponsor: a sales or operations lead, as a path to the finance lead who signs

###### Tldr
Two half-day sessions that end with a signed-off dictionary of 8 to 12 metrics your departments agree on. It is the step before the rebuild in play 02.

###### Eli5
Before a game starts, everyone has to agree what counts as a point. This workshop gets the finance and sales teams in one room to write the rules down and sign them, so nobody argues about the score later.

###### Internal one-pager
**What is it**
A two-session paid workshop that produces a signed-off dictionary of the 8 to 12 metrics in a company's monthly management pack. It is a facilitated agreement exercise, not a build, an audit or a report review.

**Who is it for**
Design for the finance or operations lead who can approve a fee and whose departments dispute core definitions. Accept a sales or operations lead as a sponsor if they can bring the finance lead into the room. Disqualify a client where one person already owns every definition and nobody disagrees (inferred). Disqualify a client that wants dashboards built in the same engagement; that is play 02.

**Why should they care**
The monthly meeting stops stalling on what revenue, active customer or churn means. Finance and sales leave with one written calculation and one named owner per metric. A client with no warehouse can get this done before any platform work.

**Why should we care**
Three of our last five rebuilds lost their first month to definition arguments. Running the workshop first moves that argument out of the rebuild and gets it paid for separately. It also qualifies buyers for play 02, and clients without a warehouse reach us earlier than they otherwise would. The handoff is the signed dictionary: play 02 starts from it instead of from a blank page. Whether the rebuild runs faster is our expectation, not a measured result, and no figure should be quoted. Whether to credit part of the fee against a rebuild is an open decision.

**What's included**
- Two half-day facilitated sessions
- Attendees: finance lead, a sales or operations lead, one data owner
- 8 to 12 metrics, each with an owner and a written calculation
- Sign-off of the dictionary by the attendees

**What's not included**
- Dashboards, models, report changes, data fixes: play 02
- Review of existing reports: play 01, free
- More than 12 metrics or extra sessions: change order (inferred)
- Warehouse setup or source system replacement: client's IT (inferred)
- Ongoing upkeep of the dictionary: retainer (inferred)
Each boundary is the on-ramp to a paid next step.

**How do we deliver it**
One senior consultant and one analyst run two half-day sessions with three client attendees. The time between sessions, preparation effort and location or format (on site or remote) are open decisions.

###### External one-pager
**What is it**
A two-session workshop where your finance and sales teams agree, in writing, what each number in your monthly pack means.

**Who is it for**
Finance and operations leaders whose teams read the same report and disagree about what the numbers mean. You do not need a data warehouse to take part.

**Why should you care**
Your monthly meeting spends its time on what a number means instead of what to do about it. You leave with one written calculation and one named owner for each of your 8 to 12 key metrics, signed off by the people who use them.

**What's included**
- Two half-day facilitated sessions
- A place in the room for your finance lead, a sales or operations lead and one data owner
- A signed-off metric dictionary: name, owner and calculation for each of 8 to 12 metrics

**What's not included**
- Building dashboards, data models or report changes. That is our Reporting Rebuild Project, which can start from your signed dictionary.
- Cleaning up data. That is also part of the Reporting Rebuild Project.
- Review of your current reports. Our free Reporting Health Check covers that.
- More than 12 metrics or extra sessions. We scope these as a change.
- Ongoing upkeep of the dictionary after sign-off. We can set up a retainer for that.

**How we deliver it**
A senior consultant and an analyst run two half-day sessions with your three attendees. We agree dates and format with you when you book.

---
