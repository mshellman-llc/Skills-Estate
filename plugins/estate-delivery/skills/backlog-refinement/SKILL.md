---
name: backlog-refinement
description: 'Get backlog items ready for a sprint: grade each requirement against INVEST and the team definition of ready, record team estimates and dependencies, split oversized items vertically, and send items that cannot be made ready back to discovery. Reads the requirements-capture Requirements tab and writes a readiness report that sprint-planning reads. Use for "refine the backlog", "groom these stories", "are these sprint-ready", "split this story", "definition of ready", INVEST checks, or a weekly refinement session. Do NOT use for writing requirements or Gherkin from sources (requirements-capture), ranking items (prioritization), building the sprint (sprint-planning), or the Sprint 0 backlog seed (delivery-kickoff).'
---

# Backlog refinement

> **Before writing: [`build-card.md`](_shared/build-card.md) plus
> [the planning chain](_shared/planning-chain.md). Inputs, not a final pass.**

Refinement turns captured requirements into items a team can commit to. This skill grades each item, records the team's estimates and dependencies, splits what is too large, and routes what cannot be fixed. The delivery team owns estimates and the definition of ready; the client or Product Owner owns priority. The skill records their decisions and never supplies an estimate or a priority itself.

## Project context required

Use only the caller-confirmed engagement or product team, its requirements workbook, its RAID log and the intended audience. Read a tracker such as Jira or Linear only when the user authorizes it, and do not change tracker issues from this skill.

## Inputs

| Input | Source | If missing |
|---|---|---|
| Requirements | The Requirements tab from `requirements-capture`, exported to CSV, or the same fields as JSON | Run requirements-capture first. Items written elsewhere need a Requirement Number, a user story and Gherkin acceptance criteria before grading. |
| Team estimates | The delivery team, in the refinement session | Items stay unestimated and cannot be READY. Never fill an estimate. |
| Dependencies | The RAID log maintained by `delivery-status` | Record each dependency as a proposed D-### entry for delivery-status. |
| Team definition of ready | The team's working agreement | Start from [the checklist](assets/definition-of-ready-and-done.md) and mark it proposed until the team adopts it. |
| Sprint length | The engagement plan or team | Use 5 days as the Small limit and state it. |

Refinement adds three columns to the Requirements tab export: `Estimate Days`, `Depends On` (RAID D-### IDs, separated by commas, semicolons or spaces; a dependency on another requirement is recorded as a D-### entry that names it) and `Refinement Sessions`. They are working columns for the delivery team; requirements-capture leaves them empty.

## Workflow

1. **Pick candidates.** Take the next 8 to 12 items in the Product Owner's order. Ranking is `prioritization` work, not refinement.
2. **Triage quickly.** Run the check on the candidates and spend about a minute per item sorting them into READY, REFINE and DISCOVERY.
3. **Fix REFINE items.** For each failed criterion, make the change the report names. Rewrite acceptance criteria as observable outcomes in Gherkin; split items over the Small limit with [the splitting reference](references/splitting.md); move untracked dependencies into the RAID log through delivery-status.
4. **Estimate.** The people who will build the item estimate it. Record the estimate in `Estimate Days`.
5. **Route DISCOVERY items.** An item scoring 2 or less, or one refined three times without becoming ready, has an open question that refinement cannot answer. Name the question and its owner, then send it to `discovery-synthesis`, `jtbd-framing` or the client contact who can answer it.
6. **Run the check again** and save the JSON report for sprint-planning.

Record splits and wording changes in the requirements workbook through requirements-capture's iteration phase so the workbook stays the single record. The readiness report never replaces the workbook.

## Gate

```bash
python3 scripts/readiness_check.py requirements.csv --raid-log RAID.md --format json --output readiness.json
python3 scripts/readiness_check.py requirements.csv --raid-log RAID.md      # Markdown report
```

| Criterion | Passes when |
|---|---|
| Independent | No dependencies, or every dependency is a D-### entry in the RAID log |
| Negotiable | The I Want To statement exists, is 400 characters or fewer and names no implementation terms such as an API, endpoint or component |
| Valuable | The So That statement says what changes, does not repeat I Want To and is not a placeholder such as "so that it works" |
| Estimable | The team recorded an estimate |
| Small | The estimate is at or below the limit (default 5 days) |
| Testable | At least one Gherkin scenario has Given, When and Then |

READY needs a score of at least 5 of 6, an estimate and a complete scenario. The check exits 1 when any graded item is not READY and 2 when the input is unreadable, an ID is missing or a requested ID does not exist. `--ids` grades only the named candidates. Report the counts it prints.

A READY verdict reports form, not substance. A well-formed item can still be the wrong work; that question belongs to prioritization and discovery.

`scripts/readiness_check_selftest.py` runs the check against its fixtures. Run it after any change.

## Failure modes

| What happens | Why it matters | What to do |
|---|---|---|
| Acceptance criteria list build steps | QA cannot observe them and the build is fixed early | Rewrite each as an outcome a user or tester can see |
| An item below the bar enters the sprint because capacity is free | Unrefined work blows up mid-sprint | Hold the definition of ready; sprint-planning fails the commit |
| The same item is discussed for three sessions | Discussion is standing in for discovery | Route it with the open question and an owner |
| Every box is ticked but the assumptions are untested | The check grades form | Test the assumptions in discovery before committing large items |
| The definition of ready grows into a specification checklist | Nothing is ever ready | Keep it to the items in the asset; move the rest to the definition of done |
| Estimates have no shared reference | Points drift between people | Re-estimate a few reference items each quarter |
| A spike is renewed indefinitely | Nothing is learned | Every spike has a written question and a two-to-three-day limit |
| Items split by team or layer | No slice ships alone | Split by user outcome |
| Two-hour tasks are recorded as features | The backlog is noise | Group them under the requirement they serve |

## Durable output

Each run leaves `refinement/readiness-YYYY-MM-DD.json`, the Markdown report beside it, and any proposed RAID entries, per `_shared/output-contract.md`. Workbook changes go to a new requirements version through requirements-capture. Deliver or link the files.

## Boundaries

- Does not write requirements, user stories or acceptance criteria from source documents. That is `requirements-capture`.
- Does not rank or set priority. That is `prioritization` and the Product Owner.
- Does not plan the sprint or decide commitments. That is `sprint-planning` and the team.
- Does not write the RAID log. That is `delivery-status`.
- Does not estimate. The team does.

## Files

- `references/splitting.md`: vertical splitting, the pattern table, worked splits and how to record a split in the workbook.
- `assets/definition-of-ready-and-done.md`: definition-of-ready and definition-of-done checklists by item type, the session agenda and a grading card.
- `scripts/readiness_check.py`: the check, which uses the standard library only.
- `scripts/readiness_check_selftest.py` and `scripts/fixtures/`: synthetic requirements, a RAID log and expected verdicts.
- `UPSTREAM.md` and `LICENSE-UPSTREAM`: the sources this skill adapts and their license.

## Release gate (required)

Before you deliver, run the gate. Full spec in [`release-gate.md`](_shared/release-gate.md).

1. Apply writing-integrity to the report prose.
2. Run quality-gate before you call it final.

Do not present the refinement as final until both checks have passed.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
