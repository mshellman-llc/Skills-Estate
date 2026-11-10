# Choosing a scoring method

Pick the method for a ranking here, once step 1 of the procedure has settled whether the list holds problems or solutions.

## Rank problems before solutions

Scoring solutions first is a premature commitment: the team settles on one answer before anyone has checked what the underlying problem is worth. Work in this order:

1. Rank the problems, jobs or desired outcomes.
2. Shortlist the strongest of them.
3. Generate several solution ideas for each shortlisted problem.
4. Score those ideas against one another.

When a list holds only solutions, ask its owner which problem each item addresses. If nobody can say, detour through `frame-jobs-to-be-done`, which has a reference on prioritizing by job.

## Match the method to the situation

| Situation | Method | Scorer support |
| --- | --- | --- |
| A personal task list | Eisenhower matrix | Discussion only |
| A short feature or initiative list (under about 15 items) needing a quick first pass | ICE, or its informal cousin, an impact/effort 2x2 sketched on a whiteboard | `ice` |
| Telling expected features apart from delighting ones, before any scoring | Kano model | Discussion only |
| Requirements competing for a fixed release | MoSCoW | Not computed; `capture-requirements` owns the values |
| Problems, jobs or outcomes with customer ratings of importance and satisfaction on 0-10 | ODI opportunity algorithm | `odi` |
| A list of that same kind, rated by a quick team estimate | Opportunity Score | `opportunity` |
| A longer list (about 15 items or more) with reach data | RICE | `rice` |
| Initiatives carrying high uncertainty | Risk versus reward | Discussion only |
| A few high-stakes options whose criteria the stakeholders must agree on | Weighted decision matrix | `weighted` |
| Portfolio-level work sharing one team's capacity across several periods | WSJF | `wsjf` |

[Scoring methods](scoring-methods.md) has the formula, scales and caveats for every row.

## One method per ranking

Name the method in the proposal and say why it fits. A ranking never combines scores produced by two different methods. When a session does use more than one (Kano to sort features, then RICE on the shortlist, for instance), record the reason for each in the proposal.

## Failure patterns and remedies

| Failure pattern | Remedy |
| --- | --- |
| The ranking is presented as if it were the decision | Label it a proposal from the title down. Only the owner's choice sets the order; on an engagement, `track-delivery` logs that choice |
| Confidence creeps upward to clear a cutoff although no new evidence has arrived | Require a written source for every confidence value; the scorer caps unsourced confidence at 50% |
| MoSCoW with no ceiling on Musts | Hold the Musts near 60% of the release effort |
| Reach equals the total addressable market | Count only the people the change touches within the current quarter |
| A product manager sizes effort alone | Have engineering approve the sizes before the ranking is published |
| Each sponsor gives their own item maximum impact | Allow the top impact value only where behavior data or revenue data backs it |
