---
skill: plan-sprint
title: Sprint plan for an offline-mode push
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 9e41c15db883c84ae5377ff1e011cfdb9dc1605eab23fde6a352a2f07ecc0ef9
---

## Request

Plan Sprint 41 for the Packwise team. Capacity, velocity and the ready backlog are in ./inputs/. Give me the sprint goal, what's in and out, and the risks.

## Inputs

Run of the built `plan-sprint` task package. All inputs below are invented. The run had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so. Files it also produced, not shown here: `sprint-41-gate-report.md`.

#### sprint-context.md

#### Packwise — Sprint 41 planning inputs (fictional)

Sprint: 2 weeks, 10 working days. Sprint goal candidate: "Crews can complete a job with no signal."
Team: 5 developers, 1 QA. Availability: Ana out 3 days; Ravi on-call (counts at 50%); a public holiday on day 6 for everyone.
Velocity: last 4 sprints 34, 29, 38, 31 points.
Carry-over: OFF-12 (13 pts, 60% done by the dev's estimate).

Ready backlog (refined, estimated):
| Key | Story | Points | Notes |
|---|---|---|---|
| OFF-12 | Cache today's jobs on device | 13 | carry-over |
| OFF-14 | Queue status updates offline and sync | 8 | depends on OFF-12 |
| OFF-15 | Conflict rule when office edits job while crew offline | 5 | needs PM decision on "last write wins" |
| OFF-16 | Offline photo capture with deferred upload | 8 | |
| OFF-18 | Offline indicator banner | 2 | |
| QBO-3 | QuickBooks sync spike | 3 | timeboxed |
| BUG-221 | Invoice PDF cuts off long addresses | 2 | customer-reported, P2 |
| BUG-230 | Login loop on Android 15 | 3 | P1, 11 tickets |

## Output

### Sprint 41 plan for Packwise

I'd commit 18 points: finish the offline cache, build offline queue and sync, fix the Android 15 login loop, and add the offline banner. That is 71% of what this team can deliver this sprint. The plan is proposed until the team commits.

#### Sprint goal

Crews can complete a job with no signal. I kept your candidate wording. The Product Owner should confirm it.

#### Capacity

Availability cuts the team to 46.5 of 60 person-days: Ana is out 3 days, Ravi is on-call at 50%, and day 6 is a holiday for everyone. That is 193.2 effective hours.

| Person | Hours | Basis |
|---|---:|---|
| Ana | 22.4 | 6 days after holiday and PTO |
| Ravi | 14.0 | 9 days, half of them on-call |
| Developers 3, 4, 5 | 39.2 each | 9 days |
| QA | 39.2 | 9 days |

Assumptions I made because the inputs don't say: 8 hours per day, 10 meeting hours and 6 interrupt hours per person, focus factor 0.7. Names for the other three developers weren't given.

No item has an hour estimate, so I sized the commitment in points. Velocity averages 33.0 (34, 29, 38, 31). Scaling by 77.5% availability gives a forecast of about 25.6 points (range 22.5 to 29.5). That assumes the four earlier sprints ran at full availability, which the inputs don't state.

#### In

| ID | Item | Points | Note |
|---|---|---:|---|
| OFF-12 | Cache today's jobs on device (remaining work) | about 5 | 40% of 13. The 60% done figure is the developer's own estimate. Re-estimate the remainder on day 1. |
| OFF-14 | Queue status updates offline and sync | 8 | Starts after OFF-12 |
| BUG-230 | Login loop on Android 15 (P1, 11 tickets) | 3 | Start on day 1 |
| OFF-18 | Offline indicator banner | 2 | First to drop if the sprint slips, unless the Product Owner ranks it higher |

Committed: 18.2 points, 71% of forecast.

**Stretch, in order:**

| ID | Item | Points | Condition |
|---|---|---:|---|
| OFF-15 | Conflict rule for office edits while crew is offline | 5 | PM decides on "last write wins" by day 2 |
| BUG-221 | Invoice PDF cuts off long addresses (P2) | 2 | none |

Stretch of 7 points is above the usual 15% target (about 4). Commit plus stretch totals 25.2, equal to the forecast, so pulling both means the team hit its full adjusted velocity.

#### Out

| ID | Item | Points | Why |
|---|---|---:|---|
| OFF-16 | Offline photo capture with deferred upload | 8 | Adding it takes the commitment to 26.2 points, 102% of forecast. Suggest Sprint 42. |
| QBO-3 | QuickBooks sync spike | 3 | Doesn't serve the goal. The Product Owner can swap it for BUG-221 if it has a deadline. |

#### Risks

| Risk | Mitigation | Owner |
|---|---|---|
| OFF-12's remaining work is larger than 40% of 13 points, which pushes OFF-14 (8 points) past the sprint | Re-estimate on day 1. Check that OFF-12 is done by day 4. | OFF-12 developer |
| OFF-14 has about 5 working days after OFF-12 lands, with day 6 a holiday | Start the queue against the cache interface from day 1 | OFF-14 developer |
| The conflict rule isn't decided, so OFF-14 sync could ship with undefined behaviour when the office edits a job | PM decision by day 2. If it slips, OFF-15 stays out and the team agrees an interim behaviour. | PM |
| BUG-230's cause is unknown and 3 points may be low | Start on day 1, report on day 2 | Android developer |
| Ravi's on-call load exceeds 50% | Keep him off the OFF-12 to OFF-14 critical path | Scrum Master |
| The forecast rests on an assumption about past availability | Replace it with actual committed and delivered points after this sprint | Scrum Master |

If the sprint slips, drop stretch first, then the committed item the Product Owner ranks lowest. Add nothing without removing something of equal size.

#### Checkpoints

Dependencies confirmed before day 1. PM decision day 2. OFF-12 done day 4. Mid-sprint check-in day 5, before the holiday. Sprint dates weren't supplied, so these are day numbers.

#### Gate

I couldn't run `sprint_check.py` in this session, so I applied its rules by hand in points. Result: 0 fail, 18 warn, 0 info. The warnings are: no hour estimates (6), no assignees (6), unconfirmed dependencies with no RAID ID (5), and no definition of done (1). No readiness report or RAID log was supplied, so I took readiness from your description of the backlog as refined and estimated. I did not verify it against criteria.

#### Open items for the team

1. The definition of done, which the gate needs to check completion criteria.
2. Names for the OFF-12 developer, the PM and the assignees. The team assigns work.
3. Sprint dates and which three days Ana is out.
4. Whether OFF-12 at 13 points should be split. It exceeds the 5-day limit for a committed item, so I planned only the remainder.
5. Proposed RAID entries for track-delivery: two dependencies (OFF-14 on OFF-12; the PM conflict-rule decision) and three risks (OFF-12 remainder, Ravi's on-call load, BUG-230 cause). I did not write the log.

#### Files

- `out/sprint-41-plan.md`: the full plan from the team template, with the per-person capacity basis
- `out/sprint-41-gate-report.md`: the gate rules applied by hand, with the findings table
- `out/answer.md`: this summary

### File: sprint-41-plan.md

#### Sprint 41 plan

Dates: not supplied (10 working days; the public holiday falls on day 6)
Team: Packwise, 5 developers and 1 QA
Status: proposed until the team commits at sprint planning

##### Goal

Crews can complete a job with no signal. (Goal candidate from the planning inputs; the Product Owner confirms it.)

##### Capacity

| Person | Hours | Basis |
|---|---:|---|
| Ana | 22.4 | 10 days - 1 holiday - 3 PTO = 6 days; (6 d x 8 h - 16 h) x 0.7 |
| Ravi | 14.0 | 9 days; on-call at 50% = 36 h; (72 h - 36 h - 16 h) x 0.7 |
| Developer 3 | 39.2 | 9 days; (72 h - 16 h) x 0.7 |
| Developer 4 | 39.2 | 9 days; (72 h - 16 h) x 0.7 |
| Developer 5 | 39.2 | 9 days; (72 h - 16 h) x 0.7 |
| QA | 39.2 | 9 days; (72 h - 16 h) x 0.7 |

Capacity: 193.2 h, or 46.5 person-days of 60 (77.5%). The 16 h deduction per person is an assumption: 10 h meetings plus 6 h interrupts. Focus factor 0.7 and 8 h per day are also assumptions.

Recent velocity: 34, 29, 38, 31 (average 33.0). Adjusted for this sprint's availability, 33.0 x 0.775 = 25.6 points (range 22.5 to 29.5 from the lowest and highest sprints). This assumes the four earlier sprints ran at full availability, which the inputs do not say.
Commit target: 80% of 25.6 = about 20 points. Stretch target: 15%, about 4 points.

The team's estimates are in points and no item has an hour estimate, so commitment is sized in points. Hours capacity is shown for the per-person view only.

##### Committed work

| ID | Item | Owner | Points | Dependencies (RAID) | Main risk and mitigation |
|---|---|---|---:|---|---|
| OFF-12 | Cache today's jobs on device (remaining work, carry-over) | Team to assign | about 5 (40% of 13) | none | The 60% done figure is the developer's own estimate. Re-estimate the remainder on day 1; if it is larger, OFF-14 slips. |
| OFF-14 | Queue status updates offline and sync | Team to assign | 8 | OFF-12 (D-### to be proposed) | Starts after OFF-12 and has about 5 working days once OFF-12 lands, with day 6 a holiday. Build the queue against the cache interface from day 1. |
| BUG-230 | Login loop on Android 15 (P1, 11 tickets) | Team to assign | 3 | none | Root cause is not yet known and could exceed 3 points. Start on day 1 and report on day 2. |
| OFF-18 | Offline indicator banner | Team to assign | 2 | none | Low risk. It is the first committed item to drop if OFF-12 or BUG-230 overruns, unless the Product Owner ranks it higher. |

Committed total: 18.2 points (71% of the 25.6-point forecast). Average velocity is 33.0, so the velocity warning does not apply.

##### Stretch work

Pull these only after the committed work is done, in this order.

| ID | Item | Points | Condition |
|---|---|---:|---|
| OFF-15 | Conflict rule when office edits a job while crew is offline | 5 | The PM decides on "last write wins" by day 2 |
| BUG-221 | Invoice PDF cuts off long addresses (P2) | 2 | none |

Stretch total: 7 points, above the 15% target of about 4. Commit plus stretch is 25.2 points, which equals the adjusted forecast.

##### Out of the sprint

| ID | Item | Points | Reason |
|---|---|---:|---|
| OFF-16 | Offline photo capture with deferred upload | 8 | Adding it to the commitment gives 26.2 points, 102% of the forecast. Propose for Sprint 42. |
| QBO-3 | QuickBooks sync spike | 3 | Does not serve the goal. The Product Owner can swap it in for BUG-221 if it has a deadline. |

##### Dependencies to confirm before day one

| RAID ID | Needed from | Owner | Needed by | Confirmed |
|---|---|---|---|---|
| D-### (propose) | OFF-12 finishing before OFF-14 starts its sync work | OFF-12 developer (name to confirm) | Day 4 | No |
| D-### (propose) | "Last write wins" decision for OFF-15 | PM (name to confirm) | Day 2 | No |

No RAID log was supplied, so the D-### numbers are not assigned.

##### Definition of done

Not supplied. The team states its list at planning; until then the gate cannot check completion criteria.

##### Checkpoints

- Dependency confirmations: before day 1
- PM decision on conflict rule: day 2
- OFF-12 complete: day 4
- Mid-sprint check-in: day 5 (day 6 is the holiday)
- Sprint review and retrospective: last day of the sprint (dates not supplied)

Descoping order if the sprint slips: stretch items first, then the committed item the Product Owner ranks lowest. Add nothing without removing something of equal size.

##### Gate

Applied by hand (see sprint-41-gate-report.md): 0 fail, 18 warn, 0 info. Passed for review. Not final until the team commits.

Proposed RAID entries for track-delivery:
- D: OFF-14 depends on OFF-12 (owner OFF-12 developer, needed by day 4)
- D: PM decision on the offline conflict rule (owner PM, needed by day 2)
- R: OFF-12 remainder may be larger than 40% of 13 points (owner OFF-12 developer)
- R: Ravi's on-call load may exceed 50% (owner Scrum Master)
- R: BUG-230 root cause unknown, estimate may grow (owner Android developer)
