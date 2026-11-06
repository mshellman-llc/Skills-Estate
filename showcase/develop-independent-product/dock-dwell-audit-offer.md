---
skill: develop-independent-product
title: Turning an employer-era dock audit into a fixed-price consulting offer
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: cfeebb0f638e7359af4d6a58b7730e104c8088b9c473b96c4069dcaefc17194c
---

## Request

I'm going independent and want to turn the dock dwell audit I built at my last job into a fixed-price consulting offer I can put on my site. The source notes and my rights/claims ledger are in inputs/. Please build the offer page copy and a synthetic worked example, and tell me what I still have to decide before I publish.

## Inputs

Run of the built `develop-independent-product` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### rights-and-claims-ledger.md

#### Rights and claims ledger (Priya Nandakumar, updated 2026-10-28)

##### Rights
- Separation letter, 2026-09-12, clause 7: I may reuse "general methods, templates and know-how" I developed. Brightwell data, names, systems access and confidential figures stay with Brightwell.
- No written clearance exists for naming Brightwell or Calloway as a reference.
- The workbook DwellAudit_v7.xlsx was built on company time; I am rebuilding the logic, not copying the file.

##### Claims
| Claim | State |
|---|---|
| Method splits dwell into four segments | Mine to describe |
| Median dwell fell 94 to 71 minutes at one DC | True at Brightwell; not cleared for public use; no independent replication |
| $212,000 detention figure | Confidential. Do not use |
| "Typically finds the biggest wait is not unloading" | Seen at one site only |

##### Offer I'm planning
- Name: Dock Dwell Audit
- Fixed price: $6,500, two weeks, one site
- Client supplies 4 weeks of yard and door timestamps
- Deliverable: findings report plus a door-assignment rule proposal
- I have not run it for any paying client yet.

#### source-notes.md

#### Dock dwell audit: working notes (Brightwell Grocery Distribution, Calloway DC)

Author: Priya Nandakumar, operations analyst, 2024–2026.

##### What it does
Measures how long trucks sit at the dock from gate check-in to gate release, and splits the time into four waits: yard queue, door assignment, unload/load, paperwork release. The finding is usually that the biggest wait is not unloading.

##### Method
1. Pull 4 weeks of gate and door-scan timestamps (we used the YMS export `calloway_gate_log.csv` and the WMS door scan table).
2. Match each visit by trailer ID. Drop visits with a missing timestamp and report how many were dropped.
3. Compute the four segments per visit and the median and 90th percentile for each, by hour of day.
4. Mark "idle door" minutes: a door empty while a truck waits in the yard.
5. Review the top three hours with the dock supervisor and propose door-assignment rules.

##### Calloway results
- 1,840 visits in the sample, 6% dropped for missing scans.
- Median dwell 94 minutes; door-assignment wait was the largest segment (31 min median).
- After a rule change (reserve doors 4–6 for frozen, assign by appointment time), median dwell fell to 71 minutes over 12 weeks.
- Carrier detention charges at Calloway: about $212,000 a year. Do not quote.

##### Dependencies
- Workbook `DwellAudit_v7.xlsx` lives on the Brightwell SharePoint (contains Calloway data, carrier names such as Tristate Haulage, and Brightwell's login for the YMS API: do not copy).
- Needs any yard system export with check-in, door-in, door-out and gate-out times.

##### Next
Rebuild the calculation from scratch in a clean workbook or Python script.

## Output

I've written the Dock Dwell Audit offer page and a worked example built on made-up data. Neither is published. Three decisions are still open, listed at the end.

#### What I relied on

Clause 7 of your separation letter lets you reuse general methods, templates and know-how. I treated the four-segment dwell method as covered. I did not reuse Brightwell's data, names, systems access or confidential figures, and I did not copy the workbook. I rebuilt the example from the method description alone.

#### Migration map

| Item | Detail |
|---|---|
| Useful mechanism | Split gate-to-gate time into yard queue, door assignment, unload and paperwork. Report median and 90th percentile by hour, count idle-door minutes, then review the worst hours with the dock supervisor. |
| Original dependencies | `DwellAudit_v7.xlsx` on the former employer's SharePoint, their yard and warehouse exports, their API login, and their carrier names. |
| Independent form | A two-week, $6,500, one-site audit. The client sends a CSV, so no system access is needed. |
| Next build step | Write a clean script or workbook from the five method steps and run it on the example data. |

#### The offer page

The page covers what the client receives, what you need from them (four weeks of timestamps with a trailer ID on each visit), a day-by-day schedule, and a link to the example. Its "About" line says the offer is new and has not yet been delivered as a paid engagement, because your ledger says that is the case.

#### The worked example

The example uses eight invented visits at a fictional site. I computed the medians by hand:

| Wait | Median (min) |
|---|---|
| Yard queue | 11.0 |
| Door assignment | 30.5 |
| Unload | 41.0 |
| Paperwork | 10.5 |
| Total visit | 93.0 |

In this sample, unloading is the longest wait and door assignment comes second. That is deliberate. Your ledger records "biggest wait is not unloading" as seen at one site only, so I didn't build the example to prove it. The example omits the 90th percentile because eight visits are too few for it to mean anything.

#### What I left out, and why

- **Brightwell and Calloway names, the carrier name, file names, the API login.** These are employer details and no reference clearance exists.
- **94 to 71 minute improvement.** The ledger says it is true at Brightwell but not cleared for public use, and no one has replicated it.
- **$212,000 detention figure.** Confidential.
- **"Typically finds the biggest wait is not unloading."** This rests on one site, so the page doesn't claim it.

The page makes no claim about results, customers or deployment.

#### What I checked, and what I couldn't

- I compared every number and claim on the page and the example against the ledger. Nothing on them comes from Brightwell.
- I recomputed the medians from the eight rows by hand. Each row's four waits add up to its total.
- I couldn't run `writing_check.py` here. I read each file through for filler, repeated sentence shapes and unsupported claims instead. That is a reading pass, not a scanner result.
- The page has not been rendered or put on a site. It exists only as local Markdown.
- I invented the contact address `priya@example.com` as a placeholder. Replace it with your real one.

#### Decisions for you

1. **Your "About" line.** I wrote "two years on dock scheduling at a grocery distribution centre". Decide whether that wording is acceptable or whether you want to say less about the previous employer. The ledger gives no clearance for naming Brightwell, so I left the name out.
2. **The 94 to 71 minute result.** Decide whether to ask Brightwell for written clearance before using it. Until you have clearance, the page stays as written.
3. **When to publish.** Publishing is a separate step. I'd rebuild and test the calculation first, so the example reflects code you have actually run.

#### Files

- `out/offer-page.md`: the public page copy, with the price, schedule, client inputs and about line described above.
- `out/worked-example.md`: the made-up eight-visit tables, medians, an idle-door illustration and an illustrative rule proposal.
- `out/migration-map-private.md`: the map above plus the source links and the list of omitted items. Keep it out of the public site.

### File: migration-map-private.md

#### Migration map (private record, keep out of the public site)

| Item | Detail |
|---|---|
| Useful mechanism | Four-segment split of gate-to-gate time per visit; median and P90 by hour; idle-door minutes; supervisor review of worst hours |
| Original dependencies | DwellAudit_v7.xlsx on the former employer's SharePoint; employer YMS/WMS exports; employer YMS API login; employer carrier names |
| Independent form | Fixed-price two-week audit, client supplies a CSV; calculation rebuilt from the method description |
| Next build step | Write a clean script or workbook from the five method steps and test it on the synthetic data (eight-visit example hand-computed here) |

##### Source links used
- inputs/source-notes.md: method, dependencies, next step
- inputs/rights-and-claims-ledger.md: separation letter clause 7, claims table, offer terms

##### Left out on purpose
- Employer and site names, the carrier name, file names, the API login: not copied.
- 94 to 71 minute result: ledger says not cleared for public use.
- $212,000 detention figure: confidential.
- "Biggest wait is not unloading": one site only. The worked example shows unloading as the longest wait.
- Workbook file: not copied; rebuilt.

### File: offer-page.md

#### Dock Dwell Audit

Find out where your trucks wait between the gate and the door, and which door-assignment rules would shorten it.

**$6,500 fixed price. Two weeks. One distribution site.**

##### What you get

A report that splits each truck visit into four waits: yard queue, door assignment, loading or unloading, and paperwork release. It gives the median and 90th-percentile time for each wait by hour of day, and it flags the hours when a door sat empty while a truck waited in the yard.

I then review the three worst hours with your dock supervisor and propose door-assignment rules for them. The rule proposal is a recommendation. You decide what to change and when.

##### What I need from you

Four weeks of yard and door timestamps for one site: check-in, door-in, door-out and gate-out, with a trailer ID on each. A CSV export from your yard or warehouse system is enough. I do not need login access to either system.

##### How it runs

1. Days 1–2: you send the export. I match visits by trailer ID, drop any with a missing timestamp, and tell you how many that was.
2. Days 3–7: I calculate the four waits and the idle-door minutes.
3. Days 8–10: I review the worst hours with your dock supervisor.
4. Days 11–14: you receive the report and the rule proposal, and we walk through it together.

##### Example

[A worked example with made-up data](worked-example.md) shows the tables you would receive.

##### About

I am an operations analyst who spent two years on dock scheduling at a grocery distribution centre. This offer is new, and I have not yet delivered it as a paid engagement.

Contact: priya@example.com

### File: worked-example.md

#### Worked example: made-up data

This example uses eight invented truck visits at a fictional site. The data, carriers and numbers are synthetic. A real audit uses four weeks of your visits, often well over a thousand.

##### Time per visit, in minutes

| Visit | Yard queue | Door assignment | Unload | Paperwork | Total |
|---|---|---|---|---|---|
| V1 | 12 | 35 | 40 | 10 | 97 |
| V2 | 8 | 10 | 45 | 12 | 75 |
| V3 | 20 | 42 | 38 | 9 | 109 |
| V4 | 5 | 6 | 50 | 15 | 76 |
| V5 | 15 | 28 | 35 | 11 | 89 |
| V6 | 10 | 38 | 42 | 8 | 98 |
| V7 | 9 | 12 | 30 | 10 | 61 |
| V8 | 14 | 33 | 44 | 13 | 104 |

##### Median per wait

| Wait | Median (min) |
|---|---|
| Yard queue | 11.0 |
| Door assignment | 30.5 |
| Unload | 41.0 |
| Paperwork | 10.5 |
| Total visit | 93.0 |

In this sample unloading is still the longest single wait. Door assignment is second at 30.5 minutes, and it ranges from 6 to 42 minutes across visits, which is the spread a rule change would target. With eight visits the 90th percentile is not meaningful, so the example omits it.

##### Idle doors

In the invented 06:00–09:00 window, door 5 was empty for 55 minutes while V1, V3 and V6 were in the yard. The audit would list each such stretch with the door, the trucks waiting and the minutes lost.

##### Rule proposal (illustration)

Assign the next truck to the first free door that suits its load type, instead of holding it for the door it was originally booked to. Check this against the three worst hours with the dock supervisor before recommending it, since door equipment and temperature zones may limit which doors can take a given load.
