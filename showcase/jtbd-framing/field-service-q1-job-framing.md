---
skill: jtbd-framing
title: Choosing two roadmap bets from five switch interviews
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: dc4e8ee3ebe54647a5c574c0565a6f36e2aa41ba5eda03e9c768d3a9b20e0c98
---

## Request

We can only fund two of our five Q1 candidates for Kestrel Field and sales and support are pulling in different directions. I've attached notes from five recent switch interviews and the candidate list; can you frame the candidates by job and tell us which two to fund and what we still don't know?

## Inputs

Run of the built `jtbd-framing` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### interview-notes.md

#### Switch interviews, Sept–Oct (Kestrel Field: scheduling and dispatch for small plumbing and HVAC shops)

**I1, plumbing, 4 techs, switched TO Kestrel 5 weeks ago from a shared Google Calendar.**
"A tech called in sick at 6:40am and I spent an hour texting customers to move jobs. That was the morning I looked for software." Chose Kestrel because it was live in a day. Hasn't used reports.

**I2, HVAC, 9 techs, switched TO Kestrel 7 weeks ago from paper and a whiteboard.**
"Customers kept calling asking where the tech was. I couldn't answer without calling the tech." Liked the arrival-window text messages.

**I3, HVAC, 14 techs, switched AWAY to a competitor 3 weeks ago.**
"Every Friday I rebuilt next week's routes by hand because Kestrel put a tech in Dover at 9 and Marlow at 10." Also: "I was exporting jobs to a spreadsheet to see which customers were due for a service visit." Competitor does route grouping.

**I4, plumbing, 11 techs, switched AWAY 6 weeks ago.**
"Two techs showed up at the same job after a reschedule, and nobody could tell me who changed it." Left for a tool with a change log.

**I5, HVAC, 6 techs, still on Kestrel, nearly left.**
"The recurring maintenance reminders are my whole business, and I set each one by hand. I forgot a batch in August and lost about a dozen visits." Stayed because migration looked painful.

Note: both joiners have 9 or fewer techs; both leavers have 11 or more.

#### q1-candidates.md

#### Q1 candidates (capacity: two)

1. **Route grouping suggestions** — suggests job order by location. Sales: lost two demos to a competitor on this.
2. **Job change history** — log of who edited or reassigned a job and when. Support: 9 tickets since July asking "who moved this job?"
3. **Recurring service reminders** — automatic repeat maintenance reminders to customers. Requested by 14 accounts in the feature-request board.
4. **Customer portal** — customers log in to see their job history. Requested by the CEO after a conference.
5. **Dark mode for the technician app** — 6 votes on the request board.

## Output

### Q1: fund route grouping and job change history

Fund **route grouping suggestions** (candidate 1) and **job change history** (candidate 2). They are the two things the two customers who left said they left over.¹ ² Recurring service reminders (candidate 3) is the strongest runner-up. Defer the customer portal and dark mode, because nothing in the interviews points to a job either one serves.

This rests on five interviews, so treat it as a strong lead and not a measured result.

#### What the interviews show

The two shops that joined Kestrel (9 techs or fewer) came for one job, and Kestrel already does it well. The two shops that left (11 techs or more) left over problems that appear as a shop grows.³

| Job (situation → outcome) | Interviews | Role | Served today? |
|---|---|---|---|
| When a tech cancels or customers ask where the tech is, re-plan the day and tell customers fast, so the morning isn't lost to phone calls | I1, I2 | Hire criteria: live in a day, arrival-window texts | Yes |
| When I build next week's routes, avoid sending techs back and forth across the territory, so I don't rebuild the schedule by hand every Friday | I3 | Fire criterion: switched to a competitor that groups routes | No |
| When a job is rescheduled or reassigned, see who changed it, so two techs don't arrive at the same door | I4 | Fire criterion: switched to a tool with a change log | No |
| When maintenance visits come due, keep them booked without remembering each one, so repeat revenue doesn't leak | I5, I3 (partly) | Near-fire: I5 stayed only because migrating looked painful | Partly |

#### The struggling moments

1. A tech called in sick at 6:40am and the owner spent an hour texting customers (I1).
2. Customers called asking where the tech was, and the owner couldn't answer without calling the tech (I2).
3. Every Friday, rebuilding next week's routes by hand because one tech was booked in Dover at 9 and Marlow at 10 (I3).
4. Two techs arrived at the same job after a reschedule, and nobody could say who changed it (I4).
5. A batch of reminders was forgotten in August, and about a dozen visits were lost (I5).

#### How the five candidates map to jobs

| # | Candidate | Job it serves | Decision |
|---|---|---|---|
| 1 | Route grouping | Build routes without Friday rework (I3) | **Fund.** Matches a stated reason for leaving, and sales has lost two demos on it.⁴ |
| 2 | Job change history | Know who changed a job (I4) | **Fund.** Matches a stated reason for leaving, and support logged 9 tickets since July.⁵ |
| 3 | Recurring reminders | Keep maintenance visits booked (I5) | **Next in line.** There is real cost in I5, but it is one near-switch, not a departure. |
| 4 | Customer portal | None found | **Defer.** The request came from the CEO after a conference, and no interviewee mentioned it. |
| 5 | Dark mode | None found | **Defer.** It has 6 votes and no job behind it. |

#### Why not recurring reminders instead

It has the loudest request count (14 accounts), and the request board is a feature list. The interviews do give it a job: I5 lost about a dozen visits, and I3 exported jobs to a spreadsheet to see who was due.⁶ But I5 stayed, and neither leaver named it as the reason they left. If the team has evidence that reminder gaps cause churn beyond these two interviews, that would change the ranking, and it is the first thing to check.

#### What we don't know

- **How many accounts are in the 11+ tech segment.** If it is a small share of revenue, fixing scaling problems protects little. If your growth plan depends on that segment, the case is stronger. This needs billing data, which wasn't supplied.
- **Whether route grouping is the real job or just the competitor's solution.** I3 describes the pain as hand rebuilding. A smaller fix, such as warning when two consecutive jobs are far apart, might do the same job. The next interview should ask what a good Friday looks like.
- **Whether "who changed this" is about accountability or about preventing double-booking.** The two lead to different designs: an audit log versus a conflict warning at reschedule time. I4 mentions both.
- **How many of the 9 tickets come from larger shops.** Sorting them by account size would test the segment pattern.
- **Interview coverage.** There are two leavers and two joiners. Three more recent leavers would show whether routes and accountability repeat, or whether other reasons appear.
- **Emotional and social dimensions.** Nothing in the notes supports a claim about how owners want to feel or be seen, so none is made.

#### Where the framing didn't add much

Candidates 4 and 5 had no job to map, so the framing only confirmed they lack support. The ranking of 3 against 1 and 2 depends on judgement about one near-switch, which the interviews cannot settle.

#### Evidence

1. Interview I3, switched away 3 weeks ago: weekly manual route rebuild, left for a competitor that groups routes.
2. Interview I4, switched away 6 weeks ago: duplicate dispatch after a reschedule, left for a tool with a change log.
3. Interviews I1 and I2 (joined 5 and 7 weeks ago, 4 and 9 techs) against I3 and I4 (left, 14 and 11 techs). The size pattern is the interviewer's own note, from four people.
4. Candidate list: sales reports two demos lost to a competitor on this feature. Not independently checked.
5. Candidate list: support reports 9 tickets since July asking who moved a job. Ticket text was not supplied.
6. Interview I5 (still a customer, 6 techs) and I3's spreadsheet export. The ~12 lost visits are I5's own estimate.

#### Method notes

I read the interview notes and candidate list only. No bundled script was run: the prose and brand checks were not available, so I reviewed the wording by hand. I did not build the HTML page, because you asked for a recommendation and not a page. The readout is Markdown and can be rebuilt with the roadmap components if you want a shareable version.
