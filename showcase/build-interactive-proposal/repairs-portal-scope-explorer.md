---
skill: build-interactive-proposal
title: Scope explorer for a housing repairs portal before any quote
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 3b993c5d1b1230ef6f5c2dc2b76cd5778eb5346b60c59247693f55a3aac219c5
---

## Request

Fernlea Housing Association hasn't had a quote from us yet, but I want to send them something clickable before the scoping call. Build an interactive scope explorer from their requirements and the workshop notes in inputs/, with versions based on the decisions they still have open.

## Inputs

Run of the built `compare-scope-options` task package in its "interactive proposal or explorer" mode. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so. Other files it produced, not shown here: `explorer.html`, `explorer.json`, `manifest.json`.

#### requirements.md

#### Fernlea Housing Association: tenant repairs portal requirements

Document: FHA-REQ-2026-07, version 3, last modified 2026-10-28
Opportunity Id: OPP-FHA-0412
Owner: Priya Nair, Head of Repairs

Fernlea manages about 6,200 homes. Repairs are reported by phone to a four-person contact team, who key each one into HomeDesk (the housing management system and system of record for repair jobs). The portal should take reports directly from tenants.

| ID | Requirement |
|----|-------------|
| R1 | Tenants report a repair online with address, category, description and preferred contact method. |
| R2 | Reports are triaged by category into the Repairs Coordinator queue. Reports tagged gas leak, no heating (winter) or flooding are flagged as emergencies. |
| R3 | Tenants see the status of each report: received, assigned, booked, completed. |
| R4 | Each report is written to a HomeDesk job record. HomeDesk stays the system of record. |
| R5 | Tenants choose an appointment slot from the contractor calendar in Tradeline, the contractor scheduling tool. |
| R6 | Contractors mark a job complete in Tradeline with notes, and the result is written back to the HomeDesk job. |
| R7 | Tenants receive SMS reminders and status texts. |
| R8 | Tenants receive a satisfaction survey after completion. |

Out of scope for the first release, per Priya: migration of repair history from before 2024.

Target volume: about 900 reports a month.

#### workshop-notes.md

#### Discovery workshop notes, 2026-10-21

Attendees: Priya Nair (Head of Repairs), Tom Okafor (Tenant Engagement Manager), Wei Zhang (Housing Systems Analyst), two delivery consultants.
Document: FHA-NOTES-2026-10-21, version 1, last modified 2026-10-23

##### Agreed
- R1 to R4 are needed in every case. The contact team cannot keep re-keying reports.
- HomeDesk is the only system of record for jobs. The portal holds no job data of its own beyond status display.
- No budget figure was shared in the workshop. Do not assume one.

##### Open decisions
1. **Contractor booking in release one (R5, R6).** Priya wants tenants to book slots, but Wei has not confirmed that Tradeline exposes a calendar interface. Owner: Priya Nair, with Wei Zhang to confirm Tradeline.
2. **Tenant messaging in release one (R7, R8).** Tom wants SMS and the survey. Fernlea has no SMS provider contract today. Owner: Tom Okafor.
3. Whether the two decisions above can both go in release one is not settled. Fernlea's board meets 2026-12-10 and wants a recommended shape before then.

##### Next
- Scoping call to be booked with Priya and Tom.
- Fernlea has asked how a quote would be produced.

## Output

**Mode: Explorer.** Fernlea has no quote, so the page shows no price, team or duration. The number that changes when you switch versions is a count of requirements, which Fernlea can check against their own document.

I've built the page, but I could not run the packaged builder, the browser QA or the prose and parity checkers in this environment. It is not release-ready until those have run. Details are under "What I could not verify".

#### What I built

`out/explorer.html` is one self-contained file. It has no external resources and no logo, because the neutral Baseline profile defines none. It opens from an email attachment.

Four tabs let the reader switch versions. The versions come from Fernlea's two open decisions from the 21 October workshop, not from a good/better/best split:

| Version | Decision outcome | Requirements included |
|---|---|---|
| A. Report and track | Neither booking nor messaging in release one | 4 of 8 (R1–R4) |
| B. Add contractor booking | Booking in, messaging out | 6 of 8 (R1–R6) |
| C. Add tenant messaging | Messaging in, booking out | 6 of 8 (R1–R4, R7, R8) |
| D. Booking and messaging | Both in | 8 of 8 |

- **Counting method:** each distinct requirement ID from FHA-REQ-2026-07 is counted once. The method is stated in the Sources disclosure.
- **Scope cards:** all eight requirement cards show on every tab. Items outside the selected version are dashed, labelled "Not in this version", and carry their route.
- **No-price block:** the header says "No pricing appears on this page", and the "Scope confirmation" block names the paid next step and its outputs.

The page also contains:
- **Open decisions:** three, with named owners.
- **Systems note:** HomeDesk is the system of record, and Tradeline owns contractor calendars.
- **Disclosures:** assumptions, excluded work with routes, and sources. In print, disclosures open and the dashed cards drop out.
- **Next steps:** four.

#### Source-backed boundaries

- **Priya Nair** owns the booking decision. Wei Zhang has not confirmed that Tradeline exposes a calendar interface, so B and D carry that as an assumption.
- **Tom Okafor** owns the messaging decision. Fernlea has no SMS provider contract, so C and D carry that as an assumption.
- **Pre-2024 repair history:** Priya excluded its migration from release one. It is listed as excluded in all four versions, with a route, and is not counted in the metric.
- **Budget:** the workshop shared no figure, and the page does not guess one.
- **Board date:** the board meets 2026-12-10 and wants a recommended shape. The page shows the date but makes no recommendation, because you gave no decision criteria. That is a gap you may want to fill.

#### Gaps and assumptions

- **Cost of the next step:** the page says Scope confirmation is a paid step but gives no fee. No source states one, and Explorer mode shows none.
- **Status "booked":** the source lists "booked" as a status. In Version A the booking scope is out, so I added an assumption that tenants would not see it. That is my inference from R3 and R5, not a source statement. Please confirm it with whoever owns the scope.
- **Hand-built output:** I could not run scripts. I assembled the page by hand from the packaged template, using the builder's rules (list below). The embedded data leaves `scope_sections` empty, because the page renders from the derived `_scope_items`. The packaged builder would keep them.
- **Roadmap kit:** I left the roadmap-kit CSS and JS out. Explorer mode draws no timeline, so they are unused.

#### Release note

```
Parity    Not run (script). Manual check: "$", "€" and "£" appear 0 times in explorer.html.
          Manifest written (out/manifest.json); main and h1 present.
Visual    Not run (no browser). Version switching, mobile and print are untested.
Prose     Not run (script). Read by hand against the SOW/proposal register.
Tie-out   n/a in explorer mode, no quote exists
```

**Input validation, done by hand against `build_proposal.py` rules:**
- Metrics: 4, 6, 6 and 8 each equal the count of that version's distinct included IDs.
- Shared IDs: R1–R8 carry identical wording and sections in every version.
- Excluded routes: every excluded item has a route.
- Source and owner references: every one resolves to a source.
- Fields: no price, duration, team or timeline fields are present.
- Currency: no currency symbol or code appears in the input.

**Prose read-through:**
- **Wording:** item names and descriptions follow the requirements table. I tightened grammar and changed no meaning.
- **Specifics:** the two figures in the assumptions, about 900 reports a month and about 6,200 homes, come from FHA-REQ-2026-07.
- **Commitments:** I kept uncertain delivery conditions visible, such as "holds only if" the Tradeline interface is confirmed.

#### What I could not verify

1. **Packaged builder and its receipt:** I did not run `build_proposal.py`, so there is no source hash.
2. **Browser QA:** I did not run `qa_proposal.py`. Please check every tab at 1280 and 390 px, the metric landing on its exact value, open disclosures, and the print PDF.
3. **Parity, prose and brand checks:** the scripts did not run, and the brand preflight did not run either. The palette is Baseline's neutral values, copied by hand.
4. **Quality gate:** not run, so please treat the page as a candidate and not as final.

#### Files

- `out/explorer.html`: the page.
- `out/explorer.json`: the sourced input data, with 4 versions, 8 requirement IDs, 3 decisions and 2 sources.
- `out/manifest.json`: the parity manifest. It requires the counts 4, 6 and 8, the OPP-FHA-0412 and document references, and the no-pricing line, and it forbids `$`.
- `out/answer.md`: this note.
