# Scoring methods

Six of the methods below run through the scorer: ICE, ODI, Opportunity Score, RICE, the weighted decision matrix and WSJF. The Eisenhower matrix, the impact/effort 2x2, Kano, MoSCoW and risk versus reward are run as discussions. Sections follow alphabetical order. Field names and input rules for the scored methods are in [the candidate file contract](candidate-file.md).

## Eisenhower matrix

The Eisenhower matrix sorts a personal task list by urgency and importance:

- urgent and important: do it now;
- important but not urgent: put it in the calendar;
- urgent but not important: hand it to someone else;
- neither: drop it.

The scorer has no support for it.

## ICE

Score = impact × confidence × ease. Impact and ease are rated 1-10, where an ease of 10 means the work is trivial. Classic ICE rates confidence on the same scale. This scorer instead takes confidence as a fraction or a percent, exactly as RICE does: a classic confidence rating of 8 goes into the file as 0.8 or as 80.

ICE is fast but subjective. It handles a long backlog poorly and works best as a conversation opener.

## Impact/effort 2x2

This is the informal cousin of ICE, usually drawn on a whiteboard. Each item lands in one quadrant:

| Impact | Effort | Quadrant |
| --- | --- | --- |
| High | Low | Quick wins |
| High | High | Major projects |
| Low | Low | Fill-ins |
| Low | High | Money pits |

Most of its value comes from arguing over where each item goes. Exact placement matters far less.

## Kano model

The Kano model sorts features into five categories: must-be, performance, attractive, indifferent and reverse. Its categories should rest on user research no older than roughly a year. Kano describes features without ranking them, so follow it with a scoring method; use it before scoring, in discussion.

## MoSCoW

Must, Should, Could and Won't, with the definitions `capture-requirements` uses. Musts should claim no more than about 60% of what the release can absorb; a list where every item is a Must tells nobody anything. The scorer does not compute MoSCoW, whose values `capture-requirements` owns.

## ODI opportunity algorithm

Score = importance + max(importance - satisfaction, 0). Customers rate importance and satisfaction on 0-10 for each desired-outcome statement. Those statements come from `frame-jobs-to-be-done`. A score above 10 marks an under-served outcome. A score far below 10 marks one that is adequately served or over-served. When the team invented the ratings, the score is a hypothesis.

With importance 9 and satisfaction 3, the score is 9 + max(9 - 3, 0) = 15, an under-served outcome. With importance 7 and satisfaction 8, the satisfaction gap counts as 0 and the score is 7.

## Opportunity Score

Score = importance × (1 - satisfaction), with importance on 0-10 and satisfaction as a 0-1 fraction. Importance 8 and satisfaction 0.25 give 8 × 0.75 = 6. A sample of about 12 respondents cannot separate two scores that differ only slightly.

## RICE

Score = (reach × impact × confidence) / effort.

- Reach is a head count of the users the change will touch within a defined window, usually one quarter. The size of the whole market is never a substitute.
- Impact uses Intercom's scale: minimal 0.25, low 0.5, medium 1, high 2, massive 3.
- Confidence has three levels: low 50%, medium 80%, high 100%.
- Effort is measured in person-weeks or person-months, and engineering sizes it.

A feature reaching 2,400 riders a quarter, with impact 2, confidence 80% and 6 person-weeks of effort, scores (2400 × 2 × 0.8) / 6 = 640.

## Risk versus reward

Reward is the expected impact on success. Risk is the probability of failure multiplied by the cost of failure. Plotting one against the other gives safe bets (high reward, low risk), bold bets (high reward, high risk), incremental work (low reward, low risk) and items to avoid (low reward, high risk). It suits initiatives with high uncertainty and runs as a discussion.

## Weighted decision matrix

Agree on the criteria and their weights up front; the weights sum to 1. Score every option against each criterion on 1-5 or 1-10, multiply each score by its weight and add the products. The matrix is transparent and slow. It suits about 5-10 decisions at a time; a long backlog needs a faster method.

## WSJF

Score = (business value + time criticality + risk reduction or opportunity enablement) / job size. All four inputs use a relative scale such as modified Fibonacci. With uncalibrated sizes the denominator dominates every score, so anchor the sizes to a few reference items before scoring.

## Evidence rules

The scorer enforces four rules on its own ([the input reference](candidate-file.md) gives the exact behavior):

- importance with no customer source (ODI, Opportunity Score) is flagged as a hypothesis;
- more than 30% of scored items sharing the top impact value triggers a note asking for recalibration;
- effort or job size with no engineering source is flagged as unpublishable until engineering sizes it;
- an unsourced confidence above 50% is scored as exactly 50%.

The session lead enforces three more:

- Kano inputs rest on research from roughly the past year;
- the scorer lists ties without breaking them; the decision meeting breaks each one with a stated tiebreaker, for instance the closer strategic fit or the lighter build;
- reach is counted per period and never as the total market.

## Originators

| Method | Credit |
| --- | --- |
| Eisenhower matrix | Named for Dwight Eisenhower and popularized by Stephen Covey |
| ICE | Sean Ellis |
| Kano model | Noriaki Kano |
| MoSCoW | Dai Clegg, as part of DSDM |
| ODI | Tony Ulwick of Strategyn |
| Opportunity Score | Dan Olsen, in *The Lean Product Playbook* |
| RICE | Sean McBride at Intercom |
| WSJF | Builds on Don Reinertsen's cost of delay; popularized by SAFe |
