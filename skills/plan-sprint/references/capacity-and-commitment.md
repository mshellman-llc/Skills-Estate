# Capacity and commitment

A sprint commonly misses because the commitment exceeded the time the team actually had (a practitioner observation, not a measured rate). A velocity number from last sprint already includes that sprint's PTO and interrupts; the next sprint will have different ones. Calculate capacity per person every sprint, then calibrate the inputs against what the team delivered.

The ranges below are starting assumptions carried from the upstream library. Replace each one with the team's measured value once three to five sprints of actuals exist, and say in the plan which values are assumptions.

## Per-person capacity

```
working days    = sprint days - holidays - PTO days
raw hours       = working days x hours per day
available hours = raw hours - meetings - on-call - interrupts
effective hours = available hours x focus factor
```

| Input | Starting assumption |
|---|---|
| Sprint days | 5 for one week, 10 for two weeks, 15 for three weeks |
| Hours per day | 8 standard, 7 with a lunch hour, 6 for a conservative plan |
| Meetings | 8 to 15 hours per person in a two-week sprint (standup 2.5, planning 2, retro 1, one-to-ones 2 to 4, cross-team 2 to 6) |
| Interrupts | 6 to 25 hours per sprint depending on role: chat questions about 5, reviews and pairing 1 to 3, production triage 0 to 10, escalations 0 to 8 |
| On-call | 5 to 10% of the week on a quiet service, 30% or more on a noisy one; plan no new work for a heavy on-call week |
| Support rotation | 50% or more of the person's time |
| New-hire ramp | about 25% in month one, 50% in month two, 75% in month three |
| Focus factor | 0.5 heavy-interrupt roles, 0.6 to 0.7 most product engineers, 0.7 to 0.8 a focused team, above 0.8 rarely |

Never use a focus factor of 1.0. Sum effective hours across the team; that total is the capacity the gate checks.

Worked example for a two-week sprint: 10 days less 1 day PTO is 9 days, 72 raw hours. Subtract 10 meeting hours, 4 on-call hours and 6 interrupt hours to get 52. At a 0.7 focus factor the person has about 36 effective hours. Eight people at that level give about 288 hours.

## Reserve capacity

Hold time for work that arrives whether or not it was planned. Technical debt takes 10 to 20% and production support 5 to 15%; reviewing teammates' code takes time every sprint, and a new hire's ramp reduces what that person can take on. A team with frequent incidents needs the higher reserve. Unreserved, this work appears as a missed commitment.

## Story points and velocity

If the team uses points, calibrate them to hours each quarter. The upstream rule of thumb is 1 point for 2 to 4 hours, 3 for about a day, 5 for 2 to 3 days, 8 for 4 to 5 days (split it), and 13 or more for a week or longer (always split). Each team's points mean something different.

Track committed, stretch, delivered and carried-over points every sprint. After three to five sprints, commit about `average delivered velocity x commit ratio`, where the commit ratio is delivered divided by committed. A team that committed 47 and delivered 40 has a ratio of about 0.85; with a 40-point average, the next commitment is about 34 points.

## Commitment bands

| Commitment as a share of capacity | What usually happens |
|---|---|
| Above 100% | The sprint misses. |
| 90 to 100% | Usually misses; there is no room for unknowns. |
| 80 to 90% | Often achievable. |
| 70 to 80% | Conservative and safer. |
| Below 70% | Under-committed; check whether the backlog is starved. |

The default target is 80% commit, 15% stretch and 5% reserve. Nothing committed may depend on a stretch item.

## Mid-sprint changes

Add nothing without removing something of equal size, and name the removed item. Descope in this order: stretch items, then the committed item the Product Owner ranks lowest. Borrowing capacity from the next sprint is rare and should be recorded. Pushing the sprint end date is the last resort and is reported in status with its reason. Late-night recovery produces defects and is not a plan.

## Diagnosing missed sprints

Compare the last three plans with their actuals before changing the process.

| Symptom in the records | Likely cause | Fix |
|---|---|---|
| Commit above 90% of capacity | Over-commitment | Commit 75 to 85% and add stretch |
| Capacity identical every sprint | Holidays, PTO, on-call rotation and new-hire ramp were ignored | Calculate per person per sprint |
| Items grew after the sprint started | Unrefined or oversized items | Commit only READY items of 5 days or less |
| Items waited on another team | Unconfirmed dependencies | Before the sprint starts, each dependency needs a named owner who has confirmed the needed-by date, and a RAID entry |
| Large unplanned hours | Interrupts or incidents | Track interrupts and raise the reserve |
| Repeated estimation misses | The estimator will not build the item | The person who will build it estimates; pair on new work |
| Every item marked top priority | No ordering | At most one or two top-priority items per sprint |
| Goal stated at planning and never again | Goal not used | Show the goal in the team channel and standup |
| Retro held with no follow-through | No action items | One to three retro actions with owners and dates |

## Definition of done

The team writes its own definition of done; the gate checks each item against that list. A common starting list: code merged and reviewed, tests added, telemetry firing in staging, documentation updated, accessibility checked, feature flag configured where used, QA passed. Add release-specific items such as a canary period when the sprint ships behind a flag.

## Checklist before the team commits

- The goal is one sentence that states an outcome.
- Capacity is calculated per person, after holidays, PTO, on-call rotation and new-hire ramp.
- Commitment is at or below 80% of capacity; stretch is at or below 15%.
- Every committed item is READY in the refinement report and 5 days or less.
- Every dependency has an owner, a needed-by date, a confirmation and a RAID ID.
- Each committed item lists its main risks with a mitigation and an owner.
- Each item lists the definition-of-done items it will meet.
- Reserve is held for incidents and support.
- Velocity history was considered, or its absence is stated.
- A mid-sprint check-in date is set.
