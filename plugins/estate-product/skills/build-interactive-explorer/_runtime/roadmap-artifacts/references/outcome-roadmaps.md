# Outcome roadmaps

Use this mode when a roadmap should say what will change for customers and the business, not only what will ship. It applies to the `product-now-next-later` template and to any board whose columns follow the now/next/later pattern. The kit renders the plan; this reference governs what goes on the cards, and `scripts/outcome_check.py` checks it.

An outcome roadmap does not decide priorities. Rank the candidates first with `prioritization`, and take the jobs and desired outcomes from `jtbd-framing` where that work exists. A roadmap built before that step tends to become a feature list rewritten in outcome language.

## From output to outcome

An output is the thing built: "advanced search". An outcome is the change it should cause: "power users find the right product in under 5 seconds, so browse-to-purchase conversion rises". Commit to the outcome and treat the feature as the team's current hypothesis about how to reach it. If the metric does not move, the team changes the solution and keeps the outcome.

Write each outcome as:

```text
Enable [specific segment] to [change the customer would recognise] so that [business metric moves]
```

The segment is precise: "agency owners in their first week", not "users". The middle part is something the customer would notice and value. The last part names a metric the business already tracks.

### The "so what?" chain

Start from the feature and ask "so what?" until the answer satisfies two readers. A customer would say the change matters to them, and a business leader would say it moves a metric they own. The upstream guidance expects about three steps.

```text
Add CSV export
  so what? Users can get their data out.
  so what? They can share reports with stakeholders who have no account.
  so what? Approvers see the numbers sooner, so deal approvals stop waiting on screenshots.
Outcome: Enable account owners to share live figures with outside approvers
         so that median approval time falls from 19 to 12 days.
```

"Users can find products faster" still describes an activity. Keep asking until the statement reaches a business metric.

## Horizons and how much detail each carries

| Horizon | Meaning | What the card holds |
|---|---|---|
| Now | In build, or starting within about two weeks | An Outcome with a baseline and a target. It also names an owner and its dependencies, and cites evidence |
| Next | Direction set, approach still open | An Outcome with a draft metric; owner may be a team rather than a person |
| Later | A problem or opportunity the team is watching | The problem and why it matters; no dates, priority labels, mockups or solution detail |

The horizon windows above (about six weeks for Now, up to three months for Next, three to six months for Later) come from upstream practitioner guidance and are no standard. Set the windows from the team's own cadence and state them in the column subtitles.

Cap Now at what the team can ship in its next cycle. The upstream guidance and the check both use three cards. A Now column with eight cards has no priorities in it; the column claims a commitment the team cannot keep. When a stakeholder pushes for a fourth Now item, move one card to Next and record the trade in a decision entry through `delivery-status` (DEC-###), or raise the cap with `--max-now` and say why.

## Writing the cards

Put the outcome in the card's `fields` so the kit shows it and the check can read it:

```json
{ "id": "c2", "col": "now", "group": "pay", "owner": "Payments squad",
  "title": "Card and ACH pay link on every invoice",
  "body": "34% of invoices are paid by check, 19 days slower.",
  "fields": { "Outcome": "Median days-to-paid 24 → 14", "Job": "Get paid without chasing", "Depends on": "D-004" },
  "cite": [2] }
```

- Title the card with the initiative; the Outcome field carries the change.
- Write the Outcome as baseline → target, with the unit. "Under 10 minutes" is a target; "42 → 10 minutes" also shows how far the team has to move.
- Record dependencies as RAID IDs (D-###) in `Depends on`. Only `delivery-status` writes the RAID log; the roadmap points at it.
- Cite the evidence for the problem and the baseline. A baseline that nobody has measured is a hypothesis; say so in the evidence list and plan the measurement as the first step.
- Pair each Now outcome with one counter-metric when the obvious way to hit the target could damage something else. If sign-ups are the target, watch activation.
- Leave `owner` as a name or team. "TBD" on a Now card means nobody has accepted the commitment.

## Showing the roadmap to different readers

One plan can serve several readers. Keep the plan fixed and change what each reader sees.

| Reader | Lead with | Leave out |
|---|---|---|
| Executives | Each outcome against the company goal it serves, with its baseline and target; then risks and dependencies | Task status and feature detail |
| Sales and customer-facing teams | Now items as commitments, described as what customers will be able to do; Next as direction | Later items, which change too often to promise |
| Engineering | The full "so what?" chain behind each outcome and its metric, so the team can propose the solution | Solution prescriptions the team has not agreed |
| Customers | Themes and the changes they will notice | Dates, unless the team is confident in them |

## Red flags

| Red flag | How to catch it |
|---|---|
| Outcome wording on top of a dated feature list | Standup notes and status reports mention only feature names |
| Now outcome without a measure | No baseline, target or date on the Now card (the check fails a Now Outcome with no number) |
| More than three Now cards | Count them; the check fails the plan |
| Later cards with scope | Dates, P0 to P3 labels, mockup links or feature counts in Later (the check warns) |
| The "so what?" chain stopped after one step | The Outcome describes user activity, not a metric the business tracks |
| Interchangeable outcome statements | Read three aloud; if they could swap cards unnoticed, push the chain further (the check warns on exact repeats) |
| "When exactly will it ship?" asked at every review | The horizons were never explained; walk through what each column commits to |
| Silent mid-quarter reshuffles | A Now card appeared or vanished with no decision entry |
| The roadmap has become a project plan | Engineer names, hour estimates or daily milestones on cards; those belong in `sprint-planning` |
| No link to company goals | Nobody can name the goal or key result a Now card serves |
| Hidden dependencies | Now or Next cards with an empty `Depends on` where the work plainly needs another team |
| Reviewed only at quarter boundaries | The board shows work nobody is doing, or omits work in progress |

## Review cadence

Check Now outcomes against their metrics weekly with product and engineering leads. Review horizon placement monthly with stakeholders, and record each move between columns as a decision. Revisit whether the outcomes still serve company strategy each quarter. Ask customer-facing teams continuously whether the assumptions behind the outcomes still hold.

## Running the check

```bash
python3 scripts/outcome_check.py plan.json
python3 scripts/outcome_check.py plan.json --max-now 4 --format json
```

The check exits 1 when Now holds more than the cap, when a Now card has no Outcome, or when a Now Outcome names no number. It warns when a Now Outcome has no baseline, a Now card has no named owner or no citation (unless `meta.source` marks the plan as example data), a Next card has no Outcome, a Later card carries dates or priority labels, or two cards share an Outcome. Run it before `build.py`; it does not replace `build.py --check`, which validates the plan's structure.
