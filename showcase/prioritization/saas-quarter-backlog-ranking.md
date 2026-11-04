---
skill: prioritization
title: Ranking a SaaS quarter backlog and choosing cuts
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 1c83aff26fc94e0e6687382b897a3d133f23992d0f1fac399b66f80661e2fc0e
---

## Request

Prioritize the Packwise backlog for next quarter with a scoring framework and tell me what to cut. We have 6 engineers for a 12-week quarter. Backlog and context are in ./inputs/.

## Inputs

Run of the built `prioritization` task package. All inputs below are invented. The run had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so. Files it also produced, not shown here: `candidates.json`.

#### backlog.md

#### Packwise — candidate features for next quarter (fictional SaaS for small moving companies)

Context: ~420 paying companies; $1.9M ARR; 6 engineers. Quarter goal: reduce churn (currently 3.1% monthly logo churn) and grow seats in existing accounts.

| Feature | Notes from team |
|---|---|
| Online quote form customers can embed | Sales says 60+ prospects asked; mostly helps acquisition. ~5 eng-weeks. |
| Crew mobile app offline mode | Support: 140 tickets last quarter from crews losing signal in basements/elevators; 3 churned accounts cited it. ~8 eng-weeks. |
| QuickBooks Online two-way sync | Today one-way export. 35% of accounts use QBO; CS says it's a top-3 renewal complaint. ~6 eng-weeks. |
| Damage claim photos attached to job | Requested by 22 accounts. ~2 eng-weeks. |
| Multi-branch dashboards | 18 accounts have 2+ branches; these are the biggest accounts (avg 3x seats). ~6 eng-weeks. |
| SMS arrival notifications to end customers | Competitor parity; 50 requests. Twilio costs pass-through. ~3 eng-weeks. |
| Dark mode | 9 requests. ~2 eng-weeks. |

## Output

### Packwise next-quarter backlog: ICE ranking and cut proposal

**Proposal:** build QuickBooks sync, offline mode, multi-branch dashboards, SMS notifications and damage photos (25 eng-weeks). Cut dark mode and the embeddable quote form (7 eng-weeks). This is a proposal; the person who owns next quarter's roadmap decides. The inputs don't name them.

**Capacity doesn't force the cut.** Six engineers over 12 weeks is 72 eng-weeks. The seven items add up to 32 eng-weeks on the team's own numbers, which is 44% of capacity. I cut the two items that don't serve the quarter goal (reduce 3.1% monthly logo churn and grow seats in existing accounts). The inputs don't give maintenance or support load, so I can't say how much of the 72 weeks is really free.

#### Ranking (ICE: impact x confidence x ease)

I used ICE because there are 7 items, which the skill treats as a quick-sort case. Reach is not comparable across the notes: they mix tickets, requests, accounts and prospects. Impact is scored 1 to 10 against the quarter goal. Ease is 10 for trivial work and is mapped from the team's eng-week figures: 2 weeks is 9, 3 is 8, 5 is 6, 6 is 5, 8 is 3.

| Rank | ID | Feature | Impact | Confidence | Ease | Score | Eng-weeks | Proposal |
|---:|---|---|---:|---:|---:|---:|---:|---|
| 1 | QBO | QuickBooks Online two-way sync | 8 | 0.5 | 5 | 20 | 6 | Build |
| 2 | OFFLINE | Crew mobile app offline mode | 8 | 0.8 | 3 | 19.2 | 8 | Build |
| 3 | MULTIBR | Multi-branch dashboards | 7 | 0.5 | 5 | 17.5 | 6 | Build |
| 4 | SMS | SMS arrival notifications | 4 | 0.5 | 8 | 16 | 3 | Build |
| 5 | PHOTOS | Damage claim photos | 3 | 0.5 | 9 | 13.5 | 2 | Build |
| 6 | QUOTE | Embeddable quote form | 2 | 0.5 | 6 | 6 | 5 | Cut |
| 7 | DARK | Dark mode | 1 | 0.5 | 9 | 4.5 | 2 | Cut |

Formulas: QBO 8 x 0.5 x 5; OFFLINE 8 x 0.8 x 3; MULTIBR 7 x 0.5 x 5; SMS 4 x 0.5 x 8; PHOTOS 3 x 0.5 x 9; QUOTE 2 x 0.5 x 6; DARK 1 x 0.5 x 9.

#### Why each call

- **Offline mode** has the strongest evidence: 140 support tickets last quarter, and 3 churned accounts cited it. At 3.1% monthly churn on about 420 accounts, roughly 39 logos leave per quarter, so those 3 are about 8% of churn. That is my arithmetic from the inputs, not a figure the team gave. It is the only item whose confidence (0.8) rests on a written source. It is also the largest item, which is why it ranks second.
- **QuickBooks sync** is a top-3 renewal complaint per CS, and 35% of accounts (about 147) use QBO. There is no complaint count, so confidence stays at 0.5. A ticket or renewal-note count could lift it above offline mode.
- **Multi-branch dashboards** serve 18 accounts, but those accounts average 3x seats. By my arithmetic that is about 12% of seats, with seats counted as 402 single-seat accounts plus 18 at 3x. Nothing in the inputs shows these accounts are at risk or asking for it, so confidence is 0.5. This is the best seat-growth bet.
- **SMS and damage photos** are cheap and have demand (50 requests; 22 accounts), but neither is linked to churn or seats. SMS also carries Twilio pass-through cost, which needs a pricing decision before launch.
- **Quote form** helps acquisition, not the quarter goal. Sales reports 60+ prospects asking, so it is a candidate for next quarter if the goal shifts to growth.
- **Dark mode** has 9 requests and no link to the goal.

#### Flags

- **Near-tie at the top:** QBO (20) and offline (19.2) are not separable at this evidence level. Treat them as equal and commit both.
- **Effort is unconfirmed.** Every eng-week figure is a team note ("~"), and no engineer sized them. The skill says effort comes from engineering. Get sign-off before publishing. If the estimates run 2x, the five committed items need 50 eng-weeks.
- **Ease is derived** from those unconfirmed figures through my mapping, so it carries the same caveat.
- **Impact scores are my judgment** against the quarter goal. Only the offline score has behavioural evidence behind it. Two of seven items share the top impact value (29%), under the 30% recalibration threshold.
- **No source supports confidence above 0.5** except offline mode, so the rest are held at 0.5, as the tool would cap them.

#### If estimates slip

Drop in this order: damage photos, SMS, then multi-branch. Protect QBO and offline mode, which are the two items with a stated retention link.

#### Decisions needed

1. The roadmap owner confirms the five-item scope and the two cuts. If it is a scope change to committed work, route it through delivery-status to log a DEC entry.
2. An engineer sizes the five committed items.
3. Someone supplies maintenance and support load, so the real capacity is known.
4. A pricing owner decides how to pass through Twilio cost on SMS.

#### How this was produced

The scoring script was not run in this session. I scored by hand using its documented ICE formula and evidence rules, and I applied the writing review by reading, with no checker run. The candidate file is in the format the script reads.

#### Files

- `out/candidates.json`: candidate file with problems, scores and sources for each item.
- `out/answer.md`: this ranking and proposal.
