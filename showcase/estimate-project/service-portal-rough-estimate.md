---
skill: estimate-project
title: Rough estimate for a service and customer portal phase one
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 5c4e72f9e50282c5c3a43c366fc34a82600b0df5606cace94c7cd48ceac16045
---

## Request

Give me a rough order of magnitude for Tidewater Freight Co. phase one so Dana can take a range to her CFO. Scope notes and our rate card are in ./inputs/. It's an early estimate, not a quote.

## Inputs

Run of the built `scope-project` task package in its "rough estimate" mode. All inputs below are invented. The run had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so. Files it also produced, not shown here: `scope.json`.

#### rate-card.md

#### Fictional rate card (USD per hour) — for illustration only

| Role | Rate |
|---|---|
| Engagement manager | 210 |
| Solution architect | 230 |
| Senior consultant (Service/Experience Cloud) | 185 |
| Developer (integration) | 175 |
| QA analyst | 130 |
| Data migration specialist | 165 |


#### scope-notes.md

#### Tidewater Freight Co. — phase one scope notes (fictional)

Confirmed in discovery (calls 1 and 2):
- Salesforce Service Cloud for 62 contact-center agents and 9 claims adjusters (71 users).
- Experience Cloud customer portal: shipment tracking lookup by PRO number, online freight-claim filing with photo upload, claim status.
- Integration with RouteLine 9 TMS (vendor-hosted REST API): read shipment status and proof-of-delivery images. Read-only; no write-back in phase one.
- Email-to-case for the shared claims inbox; migrate ~3,500 open and last-12-month claims from a spreadsheet and ServiceDesk Pro export.
- Knowledge base: ~120 articles to migrate from SharePoint.
- Out of scope for phase one: telephony/CTI, field driver app, billing disputes.
- Target go-live: before October peak, about 10 months from contract.
- Client team: 3-person IT apps team (Marcus), part-time.

## Output

### Tidewater Freight Co. phase one: rough order of magnitude

**For the six scoped workstreams, the estimate is 1,240 to 2,719 hours, or $221,120 to $484,570 at the supplied rate card. The expected case is 1,780 hours and $317,280.** Two items Dana's team will probably ask about, portal customer sign-in and training with post-go-live support, have no basis yet and are not in these numbers. The range is therefore not the full phase-one cost, and the CFO should see it that way.

This is a planning range from early discovery notes. It is not a quote, and it gives no commitment on price or schedule.

#### What the range stands on

- **Scope:** `inputs/scope-notes.md` (discovery calls 1 and 2, no revision stamp).
- **Rates:** `inputs/rate-card.md`, USD per hour, no revision stamp. The card does not say whether these are cost rates or client billing rates. The dollar figures assume they are billing rates; confirm that before the range goes to the CFO.
- **Hours:** I built them by role for each item from the volumes in the notes. No comparable engagement or hours anchor was supplied, so every hour figure is an inference (my judgement of volume and complexity) rather than a confirmed number. The low and high bounds come from the conditions in the table below, not from a percentage.
- **Hand calculation:** I could not run the bundled calculator in this session. I followed its rules by hand: exact decimal arithmetic, no contingency uplift, no rounding, and an `incomplete-estimate` status because two items are unestimated. The input is saved in `out/scope.json` in the calculator's format, so the script can reproduce these figures.
- **Not used:** the quote-reconciliation gate. No quote exists, so there is nothing to tie out.

#### Estimate by work item

| Work item | Hours (low / expected / high) | Fee, USD (low / expected / high) | What moves it |
|---|---|---|---|
| Service Cloud claims case management (71 users) | 370 / 500 / 710 | 67,700 / 91,800 / 130,300 | Claims workflow rules, adjuster approval steps, page layouts and reports by role |
| Email-to-case, shared claims inbox | 70 / 104 / 158 | 12,580 / 18,660 / 28,450 | Routing rules and attachment handling on the inbox |
| Experience Cloud customer portal | 364 / 522 / 788 | 66,040 / 94,520 / 142,780 | Photo upload limits, claim form complexity, branding |
| RouteLine 9 read-only integration | 202 / 303 / 510 | 35,620 / 53,430 / 90,200 | API documentation quality, sandbox access, proof-of-delivery image size and volume |
| Claims data migration (about 3,500 records) | 168 / 252 / 398 | 27,680 / 41,620 / 65,940 | Spreadsheet cleanliness, duplicates, attachments, mapping between the two sources |
| Knowledge base migration (about 120 articles) | 66 / 99 / 155 | 11,500 / 17,250 / 26,900 | Amount of article cleanup and reformatting |
| **Estimated subtotal** | **1,240 / 1,780 / 2,719** | **221,120 / 317,280 / 484,570** | |
| Portal customer identity and access | Unestimated | Unestimated | Needs the discovery below |
| End-user training and post-go-live support | Unestimated | Unestimated | Needs the discovery below |

Engagement management is spread across the items rather than shown as an overhead row.

#### Hours and fees by role

| Role | Rate | Low | Expected | High | Fee low | Fee expected | Fee high |
|---|---|---|---|---|---|---|---|
| Engagement manager | 210 | 82 | 113 | 175 | 17,220 | 23,730 | 36,750 |
| Solution architect | 230 | 128 | 193 | 318 | 29,440 | 44,390 | 73,140 |
| Senior consultant | 185 | 520 | 720 | 1,020 | 96,200 | 133,200 | 188,700 |
| Developer (integration) | 175 | 160 | 240 | 400 | 28,000 | 42,000 | 70,000 |
| QA analyst | 130 | 214 | 310 | 486 | 27,820 | 40,300 | 63,180 |
| Data migration specialist | 165 | 136 | 204 | 320 | 22,440 | 33,660 | 52,800 |
| **Total** | | **1,240** | **1,780** | **2,719** | **221,120** | **317,280** | **484,570** |

Reconciliation: the item hours and role hours both total 1,240, 1,780 and 2,719. The item fees and role fees both total $221,120, $317,280 and $484,570. As a spot check, the RouteLine low case is 120 developer hours at 175 ($21,000), 30 architect hours at 230 ($6,900), 40 QA hours at 130 ($5,200) and 12 engagement manager hours at 210 ($2,520), which sums to $35,620 and matches the table.

#### Unknowns that make the range wide

| Dimension | Value assumed | Confidence | How to confirm |
|---|---|---|---|
| Users on Service Cloud | 62 agents and 9 claims adjusters (71) | Confirmed (discovery calls) | None needed |
| Customer portal functions | PRO-number lookup, claim filing with photo upload, claim status | Confirmed | None needed |
| RouteLine 9 interface | One read-only REST integration for shipment status and proof-of-delivery images | Confirmed scope, Unknown complexity | Get the API documentation and a sandbox from the vendor; ask for image sizes and daily call volume |
| Claims to migrate | About 3,500 records (open plus last 12 months) | Confirmed count, Unknown quality | Ask Marcus's team for a sample of the spreadsheet and the ServiceDesk Pro export |
| Knowledge articles to migrate | About 120 from SharePoint | Confirmed count, Unknown cleanup | Review a sample of 10 to 15 articles |
| Client capacity | 3-person IT apps team, part-time | Confirmed | Ask for named hours per week; slow client reviews would lengthen the schedule |

#### What would reopen the estimate

- RouteLine 9 needs write-back, a second system, or a vendor API without a sandbox. That resizes the integration and adds testing.
- The claims data turns out to be well over 3,500 records, or the two sources need heavy deduplication. That resizes the migration.
- Customers must sign in with accounts, SSO, or verified identities. This is the first unestimated item and could add a new workstream.
- Training and post-go-live support are included. This is the second unestimated item.
- Telephony/CTI, the field driver app, or billing disputes move into phase one. They are out today.

#### Discovery needed to complete the number

1. **Portal customer identity and access.** Is tracking anonymous? How is a claimant tied to a claim? Is SSO required?
2. **Training and post-go-live support.** Is either in phase one? How many sessions, and who trains on the client side?

#### Schedule

The notes give a target go-live before October peak, about 10 months from contract. I did not test that against capacity, because no staffing plan or weekly availability was supplied and I did not assume a working week. The client's part-time three-person team and the vendor's API access are the likeliest dependencies. A schedule needs those inputs.

#### For Dana's CFO conversation

- Present $221K to $485K as the range for the six scoped workstreams, with about $317K expected, and say plainly that portal sign-in and training are still to be sized.
- Say the figures rest on an inferred effort basis and a rate card that is not marked cost or billing.
- Do not treat the high end as a ceiling. It reflects the bounds above, not a cap.

#### Gaps and checks

- Run `estimate.py` on `out/scope.json` once scripts are available, and compare its output with the figures above.
- I read the prose by hand and did not run the bundled writing checker or the quality gate, since I could not run scripts. The ROM document is a Markdown answer, not a branded artifact, so I did not run brand rendering.

#### Files

- `out/scope.json`: calculator input with items, role-hour allocations, rate sources, assumptions and exclusions.
- `out/answer.md`: this answer.
