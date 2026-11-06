---
name: plan-sprint
description: 'Plan one sprint on an agile engagement or product team: sprint goal, per-person capacity, commit and stretch work sized against that capacity, owned dependencies recorded in the RAID log, risks and the team definition of done, checked by a blocking gate before the team commits. Use for "plan the next sprint", "sprint planning", "how much can we commit", "capacity for sprint N", "why do we keep missing sprints", or a Sprint 1 plan after kickoff. Do NOT use for grading or splitting backlog items (refine-backlog), ranking candidates (prioritization), the Sprint 0 mobilization plan (start-delivery), weekly status or RAID upkeep (track-delivery), or a quarter or release roadmap (build-roadmap).'
---

# Plan sprint

> **Before writing: [`build-card.md`](_shared/build-card.md) plus
> [the planning chain](_shared/planning-chain.md). Inputs, not a final pass.**

A sprint plan says what the team will finish, what it will attempt if the commitment lands early, and what could stop it. This skill drafts the plan from the refined backlog and the team's real capacity, runs the gate, and hands the plan to the team. The team decides the commitment. The skill never commits on the team's behalf and never estimates work the team has not estimated.

## Project context required

Use only the caller-confirmed engagement or product team, its backlog, its RAID log and the intended audience. Map roles such as Program Lead, Scrum Master and Product Owner to the people the project actually names. A connected Jira or Linear workspace is a read source when the user authorizes it; this skill does not create sprints, move issues or write to the tracker.

## Inputs

| Input | Source | If missing |
|---|---|---|
| Candidate items with IDs and team estimates | The readiness report from `refine-backlog` | Run refine-backlog first. Without it the gate relies on self-reported flags and says so. |
| Capacity per person | Sprint length, working days, PTO, meetings, on-call and interrupt hours, focus factor | Ask for the two or three that change the total most. Use a 0.7 focus factor otherwise and state it. |
| Velocity for the last three to five sprints | The tracker or the previous sprint reports | Plan on hours only and say velocity was unavailable. |
| RAID log | Seeded by `start-delivery`, maintained by `track-delivery` | Dependencies stay in the plan with a warning; propose RAID entries through track-delivery. |
| Team definition of done | The team's working agreement | Ask once. Without it, completion criteria cannot be checked and the gate warns. |
| Sprint goal candidates | The Product Owner, the roadmap Now column, the quarter objective | Draft one and mark it proposed. |

## Workflow

1. **Pin the sprint.** Name, dates, team and the previous sprint's report. Carry unfinished items forward explicitly; an item that disappears between sprints is the failure mode.
2. **Write the goal.** One sentence that states the outcome, such as "a new admin can finish guided setup without a support ticket". A list of features is not a goal. The goal is what lets the team refuse off-goal requests mid-sprint.
3. **Calculate capacity per person.** Multiply working days after PTO by hours per day, subtract the person's overhead hours, then apply the focus factor. Read [capacity and commitment](references/capacity-and-commitment.md) for the worked calculation and calibration against actuals.
4. **Select items.** Only READY items from the refinement report are eligible to commit. A REFINE or DISCOVERY item goes back to refine-backlog with its failed criteria, not into the sprint.
5. **Split commit and stretch.** Commit roughly 75 to 85% of capacity and hold 10 to 15% for stretch. Nothing in the commitment depends on a stretch item.
6. **Record dependencies.** Every dependency gets an owner, a needed-by date, the owner's confirmation and a RAID dependency ID (D-###). New dependencies are proposed to track-delivery for the RAID log; this skill does not write the log.
7. **Record risks.** One or two per committed item where they exist: technical, dependency, estimate or capacity risk, each with a mitigation and an owner. Risks that outlive the sprint go to the RAID log as R-### entries through track-delivery.
8. **Check the definition of done.** List which team DoD items each item plans to meet.
9. **Run the gate** and fix the plan until it passes, then fill [the template](assets/sprint-plan-template.md).

## Gate

```bash
python3 scripts/sprint_check.py plan.json --readiness readiness.json --raid-log RAID.md
```

The plan format is in [plan format](references/plan-format.md). The gate exits 1 on any fail finding: no goal, no capacity, committed work above capacity, a committed item that is not READY or not in the refinement report, a committed item's dependency with no owner, or a RAID ID that is not in the log. Warnings and information findings do not block. Report the counts it prints and the utilization percentage in place of adjectives.

`scripts/sprint_check_selftest.py` runs the gate against passing and failing fixtures. Run it after any change to the gate.

## Diagnosing missed sprints

When sprints keep missing, compare the last three plans with their actuals before changing anything. Each cause listed in [capacity and commitment](references/capacity-and-commitment.md) has its own fix and its own evidence, so name the cause the records show. Report what the records show and what remains unknown.

## Durable output

Each run leaves `sprint-NN-plan.md` (the filled template) and the gate report in the engagement or team folder, named by sprint number, per `_shared/output-contract.md`. A run that stops at a failed gate still leaves the gate report and the open questions. Deliver or link the files.

## Boundaries

- Does not grade, estimate or split items. That is `refine-backlog`.
- Does not rank candidates. That is `prioritize-work`; the Product Owner orders the backlog.
- Does not write the RAID log or the status report. That is `track-delivery`.
- Does not plan Sprint 0 or mobilization. That is `start-delivery`.
- Does not commit, approve or start the sprint. The team commits; the tracker is changed by a person or an authorized workflow.

## Files

- `references/capacity-and-commitment.md`: how to calculate capacity and size the commitment, plus mid-sprint descoping and missed-sprint diagnosis.
- `references/plan-format.md`: the plan JSON fields the gate reads.
- `assets/sprint-plan-template.md`: the plan the team reviews.
- `scripts/sprint_check.py`: the gate. Standard library only.
- `scripts/sprint_check_selftest.py` and `scripts/fixtures/`: passing and failing cases.
- `UPSTREAM.md` and `LICENSE-UPSTREAM`: the source this skill adapts and its license.

## Release gate (required)

Before you deliver, run the gate. Full spec in [`release-gate.md`](_shared/release-gate.md).

1. Apply review-writing to the plan prose.
2. Run review-deliverable before you call it final.

Do not present the plan as final until both checks have passed.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
