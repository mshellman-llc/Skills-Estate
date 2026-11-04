# Prioritization frameworks

Rank problems before solutions. A feature is one answer to a problem; scoring features first locks in an answer before anyone checks whether the problem is worth solving. Rank the problems or jobs, choose the few worth solving, generate more than one solution for each, then rank the solutions.

## Choosing a framework

| What is being ranked | Framework | Tool support |
|---|---|---|
| Customer problems or jobs, with importance and satisfaction ratings | ODI when the ratings come from customers on 0 to 10 scales; Opportunity Score for a quick team estimate | `odi`, `opportunity` |
| Features or initiatives, fewer than about 15, quick sort | ICE, or impact against effort on a whiteboard | `ice` |
| Features or initiatives, 15 or more, with reach data | RICE | `rice` |
| Portfolio items competing for one team's capacity over time | WSJF | `wsjf` |
| A few high-stakes options that need stakeholder agreement on criteria | Weighted decision matrix | `weighted` |
| Requirements inside a fixed release scope | MoSCoW, recorded in requirements-capture | none; requirements-capture owns the values |
| Initiatives with large uncertainty | Risk against reward | discussion only |
| Understanding which features customers expect versus enjoy | Kano, before ranking | discussion only |
| A PM's own task list | Eisenhower matrix | discussion only |

Use one framework per ranking and say which one. When a session combines frameworks, record why.

## Formulas and scales

**ODI (Ulwick).** `importance + max(importance - satisfaction, 0)`, both rated 0 to 10 by customers for a desired-outcome statement from jtbd-framing. Scores above 10 indicate under-served outcomes; scores well below 10 indicate outcomes already served or over-served. Internal ratings make the result a hypothesis.

**Opportunity Score (Olsen).** `importance x (1 - satisfaction)`, importance 0 to 10 and satisfaction 0 to 1. Example: finding products quickly, importance 9 and satisfaction 0.3, scores 6.3; comparing prices, 7 and 0.8, scores 1.4. A survey of a dozen people is too small to separate close scores.

**RICE.** `(reach x impact x confidence) / effort`. Reach is the number of people affected in a stated period, such as a quarter; the total market is too broad. Impact uses the fixed scale 3 massive, 2 high, 1 medium, 0.5 low, 0.25 minimal. Confidence is 100% high, 80% medium, 50% low. Effort is person-months or person-weeks, sized by engineering.

**ICE.** `impact x confidence x ease`, each 1 to 10, where ease 10 is trivial. Fast and subjective; use it to start a discussion, and not for backlogs of 80 items.

**WSJF.** `(business value + time criticality + risk reduction or opportunity enablement) / job size`, each on a relative scale such as modified Fibonacci. Calibrate job size against a few reference items, or the denominator decides the ranking.

**Weighted decision matrix.** Agree the criteria and weights first (weights sum to 1), then score each option 1 to 5 or 1 to 10 per criterion. It is transparent and slow, so it suits 5 to 10 decisions; a long backlog needs a faster framework.

**MoSCoW.** Must Have, Should Have, Could Have, Won't Have, with requirements-capture's definitions. Keep Must Have to about 60% of the release effort; when everything is a Must Have, the category ranks nothing.

**Impact against effort.** Quick wins (high impact, low effort), major projects (high, high), fill-ins (low, low), money pits (low, high). The discussion matters more than exact placement.

**Risk against reward.** Reward is the expected impact if it works; risk is the probability of failure times its cost. Safe bets, bold bets, incremental work, and work to avoid.

**Kano.** Must-be, performance, attractive, indifferent and reverse features, from recent user research. It explains expectations; rank afterwards with another framework.

**Eisenhower.** Urgent and important work first, important but not urgent work scheduled, urgent but unimportant work delegated, the rest dropped.

## Where the numbers come from

Each score input names its source in the candidate file's `sources` object. The tool enforces three rules and the facilitator enforces the rest.

| Rule | Enforced by |
|---|---|
| Confidence above 50% needs a written source; without one it is capped at 50% | `priority_score.py` |
| Effort or job size needs an engineering source before the score is published | `priority_score.py` flags it |
| Customer importance needs a customer source, or the rank is a hypothesis | `priority_score.py` flags it |
| When more than 30% of items share the top impact value, recalibrate | `priority_score.py` notes it |
| Reach is counted per period, not as the total market | facilitator |
| Ties are broken in the decision meeting, by a named rule such as strategic fit or lower effort | facilitator; the tool lists ties |
| Kano categories come from research less than about a year old | facilitator |

## Common failures

| What happens | Fix |
|---|---|
| Every champion's item gets top impact | Keep the top value only where behavioural or revenue evidence exists |
| Confidence rises to clear the cut line without new evidence | Require a source; the tool caps unsourced confidence |
| The PM sizes effort alone | Engineering signs off on effort before publication |
| Reach uses the total addressable market | Count people affected this quarter |
| MoSCoW with no limit on Must Have | Cap Must Have near 60% of effort |
| The ranking is announced as the decision | Present it as a proposal; the decision owner decides and delivery-status records it as a DEC entry |
