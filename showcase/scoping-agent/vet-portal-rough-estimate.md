---
skill: scoping-agent
title: Rough estimate for a veterinary client portal with an unscoped migration
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 5c42af24098dabd808faddcbe450c622c97f2f9ae3c8845cbeb4a446f1b48e52
---

## Request

Can you put together a rough estimate for the Northgate client portal? My call notes, our Q4 rate card and the dental-group project we'd use as a comparable are in the inputs folder. I need an hours and cost range for the partners' meeting on Friday.

## Inputs

Run of the built `project-scoping` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so. Other files it produced, not shown here: `scope.json`.

#### call-notes.md

#### Northgate Veterinary Group: discovery call notes (2026-10-29)

Attendees: Priya Raman (operations manager, Northgate), our side: Tomas Eriksen.

##### What they want
A client portal in three parts:
1. Online appointment booking. Owners pick a clinic, a vet and a time slot, and can cancel or reschedule. Each clinic has its own opening hours and vet rosters. If no slot is free in the next 14 days, Priya wants the owner shown the earliest slot at any other clinic.
2. Appointment reminders by SMS and email, 48 hours and 4 hours before the visit.
3. Owner login with a read-only view of pet profiles, vaccination dates and past visit summaries.

Priya also wants old patient records moved from their legacy system (PawFile) into the new practice system so the portal can show history. She said "about 40,000 patients" and "some X-ray images". She does not know the PawFile export format, and nobody has looked at the images.

##### Clinics
The brief Priya emailed says 6 clinics. On the call she said a 7th opens in April and should be bookable from day one of the portal if possible.

##### Open items
- Deposits for surgery bookings: "maybe, the partners haven't decided". No payment gateway chosen.
- Target go-live: before the April opening.
- Practice system: the portal reads from a vendor API. Priya will ask the vendor for API documentation; not received yet.

##### Our delivery team (Tomas)
Developer 1 person, 32 h/week, 75% available. Business analyst 1 person, 16 h/week, 100%. QA 1 person, 24 h/week, 50%. Project manager 1 person, 8 h/week, 100%.

#### comparable-dental-portal.md

#### Comparable: Lakeside Dental booking portal (completed 2026-03)

Scope: online booking for 3 clinics, 9 dentists, cancel and reschedule, SMS and email reminders at 24 hours. One SMS vendor. No login, no record migration. Actual hours, time and materials.

| Part | BA | Dev | QA | PM | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Booking (3 clinics) | 30 | 120 | 40 | 10 | 200 |
| Reminders | 6 | 30 | 10 | 3 | 49 |

Notes: about 30% of booking development went to per-clinic hours and roster rules. A late request to add a second reminder time cost 8 extra developer hours. Reminders used the vendor's ready-made SMS library.

#### rate-card.md

#### Client billing rate card, 2026-Q4, revision v2

Currency: USD per hour. These are billing rates to clients, not cost rates.

| Role | Rate |
| --- | ---: |
| Project manager | 140 |
| Business analyst | 125 |
| Developer | 150 |
| QA engineer | 105 |

Approved by the finance lead on 2026-10-01. Time-and-materials engagements use these rates unchanged.

## Output

The portal work we can size comes to **411 to 652 hours, expected 501, or USD 56,240 to 89,200, expected 68,610**. That is not the full project cost. Legacy patient record migration has no effort basis yet, so I left it unestimated and have not given a project total.

#### Range

| Scenario | Hours | Fee (USD) |
| --- | ---: | ---: |
| Low | 411 | 56,240 |
| Expected | 501 | 68,610 |
| High | 652 | 89,200 |

Fees use the 2026-Q4 v2 client billing rates (project manager 140, business analyst 125, developer 150, QA 105 per hour), unrounded and with no contingency added.

| Item | Low h | Expected h | High h | Expected USD |
| --- | ---: | ---: | ---: | ---: |
| Online appointment booking | 250 | 299 | 382 | 40,980 |
| Appointment reminders | 59 | 72 | 96 | 9,880 |
| Owner login and read-only pet records view | 102 | 130 | 174 | 17,750 |
| Legacy patient record migration | unestimated | | | |

By role (low / expected / high): developer 246 / 300 / 386, business analyst 64 / 78 / 102, QA 80 / 96 / 126, project manager 21 / 27 / 38. Project management is carried inside each item, so it is not counted twice.

#### How the numbers were built

- **Booking and reminders (Inferred).** Both come from the Lakeside Dental project: 200 hours for booking at 3 clinics and 49 for reminders. About 36 of the booking developer hours there went to per-clinic hours and roster rules, roughly 12 per clinic. Six clinics adds about 36, and the cross-clinic "earliest slot elsewhere" rule is new work. Northgate wants email as well as SMS, at two reminder times. Lakeside had SMS only, and adding a second time late cost it 8 developer hours.
- **Owner login and records view (Inferred, weaker).** The comparable has no login. I decomposed it by role from general knowledge of similar screens, so treat this line as the least anchored of the three.
- **What moves the high bound.** Booking reaches 382 hours if the seventh clinic (opening in April) must be bookable on day one, or if the vendor API is awkward. Reminders reach 96 if a different SMS vendor is needed. The low bound assumes the API documentation arrives and matches what the portal needs.

#### Items to confirm before Friday

| Dimension | Value assumed | Confidence | Confirmation action |
| --- | --- | --- | --- |
| Clinics bookable at launch | 6 | Unknown | The emailed brief says 6; Priya said on the call a 7th opens in April and should be bookable from day one if possible. These conflict. Ask Priya whether the 7th is in launch scope. |
| Practice system vendor API: reading vet rosters and writing appointments | Supported | Unknown | Documentation has not arrived. Priya is requesting it from the vendor. I cannot say whether it exists or is adequate. |
| Reminder channels and times | SMS and email at 48 h and 4 h | Confirmed (call notes) | None needed. |
| SMS vendor | One vendor with a ready-made library | Unknown | Ask which vendor Northgate prefers. |
| Patient records to migrate | About 40,000 plus X-ray images (client's figure) | Unknown | Get a sample PawFile export, real patient and image counts, image sizes and the practice system's import options. |

The seventh clinic is a conflict between sources. The estimate stands on 6, and the 7-clinic case is covered only by the high bound.

#### Schedule

If the team is as described in your notes (developer 32 h/week at 75%, business analyst 16 h, QA 12 h effective, project manager 8 h), the developer sets the pace. The minimum is **10.25, 12.5 and 16.08 weeks** for the low, expected and high cases. That is a workload bound for the sized items only. It ignores client review time, waiting on the vendor API, and the migration. Counting back from the April opening is a separate exercise once the migration is sized.

#### Excluded

- Deposit payments for surgery bookings: the partners have not decided and no gateway is chosen. If included, this becomes a new item.
- Hosting, SMS and email usage fees, and practice system licences.
- Legacy record migration, until the discovery above is done.

#### What would reopen the estimate

- Seventh clinic needed at launch (resize booking).
- API documentation that lacks roster reads or appointment writes (resize booking and reminders).
- Deposits added (new item).
- Migration sized (adds to the total, and affects the schedule and the April target).
- A different SMS vendor (resize reminders).

#### Limits of this work

- This is a planning range. It is not a quote and does not replace any agreed commercial terms.
- I could not run the local calculator (`scripts/estimate.py`) here. I did its arithmetic by hand with its rules, and checked that the item totals add up to the role totals: 411, 501 and 652 hours both ways. The fees reconcile the same way. Rerun the calculator on `scope.json` to produce the hashed JSON output.
- The evidence, quality, brand and prose-pass checkers were not available. I reviewed the confidence labels, calculations and wording by hand instead. The estimate is a plain Markdown file with no branded rendering.
- The ROM reconciliation gate applies to quote-anchored estimates, and there is no quote here.

#### Files

- `out/scope.json`: calculator input with items, bases, rates, capacity, assumptions and exclusions.
- `out/estimate.md`: the estimate tables above, with the role effort, capacity bound, assumptions and exclusions.
- `out/answer.md`: this summary.

### File: estimate.md

#### Project estimate

Working estimate from Northgate discovery call notes 2026-10-29 and the Lakeside Dental comparable, revision: call notes as of 2026-10-29; rate card 2026-Q4 v2. Calculated by hand following the local calculator's rules (the script was not run).

Some scope remains unestimated. Full-project hours and price are withheld.

##### Estimated work subtotal (excludes legacy patient record migration)

| Scenario | Hours | Fee (USD) |
| --- | ---: | ---: |
| Low | 411 | 56240 |
| Expected | 501 | 68610 |
| High | 652 | 89200 |

##### Items

| Item | Low h | Expected h | High h | Low USD | Expected USD | High USD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Online appointment booking (BOOK) | 250 | 299 | 382 | 34220 | 40980 | 52360 |
| Appointment reminders (REMIND) | 59 | 72 | 96 | 8080 | 9880 | 13090 |
| Owner login and read-only pet records view (LOGIN) | 102 | 130 | 174 | 13940 | 17750 | 23750 |
| Legacy patient record migration (MIGRATE) | unestimated | | | | | |

Migration discovery needed: a sample PawFile export and its format, the actual patient and image counts, image sizes, and the practice system's import options.

##### Role effort

| Role | Low | Expected | High | Rate (USD/h) |
| --- | ---: | ---: | ---: | ---: |
| Business analyst | 64 | 78 | 102 | 125 |
| Developer | 246 | 300 | 386 | 150 |
| QA engineer | 80 | 96 | 126 | 105 |
| Project manager | 21 | 27 | 38 | 140 |

Rates: client billing rate card 2026-Q4 v2.

##### Capacity (estimated items only)

Developer 24 h/week effective (1 x 32 x 0.75), business analyst 16, QA 12, project manager 8. The developer is the constraining role.

| Scenario | Minimum weeks at supplied capacity |
| --- | ---: |
| Low | 10.25 |
| Expected | 12.5 |
| High | 16.08 (386 / 24) |

This is a workload bound. Vendor API access, client reviews and the migration are not in it.

##### Assumptions

- Six clinics are in scope (the emailed brief). If the seventh clinic is live at launch, the booking high bound applies.
- The practice system vendor API supports reading rosters and writing appointments. Documentation has not been received, so its availability and content are unknown.
- One SMS vendor with a ready-made library, as in the comparable.
- Project management hours sit inside each item.

##### Exclusions

- Legacy patient record migration (unestimated).
- Deposit payments for surgery bookings (undecided, no gateway).
- Hosting, SMS and email usage fees, practice system licences.
