# Cutover runbook format

The runbook is the sequenced, owned script for the production cutover. Its job is that nobody in the war room ever has to invent a decision under pressure: every step already knows who does it, how you know it worked, and where you land if it does not.

The gate (`scripts/closeout_gate.py --type runbook`) parses the step table, so the table shape below is load-bearing, not a style preference.

## Document skeleton

1. Header block: client, engagement, SOW ID, cutover window (start and end, with timezone), go / no-go sign-off reference (who signed, when, source), war-room channel and bridge.
2. Roles on the day: each role from the engagement team with the named person covering it during the window, plus the client-side counterparts. Include an explicit escalation path (first call, second call, CSE).
3. Go / no-go entry conditions: the conditions that were true when go was signed, restated so a drift is visible on the day (open defect list as of sign-off, environment freeze in place, backup taken).
4. The step table (below).
5. Rollback decision rule: who can call a rollback, by when the call must be made (the point of no return, named as a step number), and what the client is told in each case.
6. Post-cutover monitoring: what is watched, by whom, for how long, and the threshold that turns an observation into a hypercare issue.

## The step table

One markdown table, these columns, in this order:

| # | Step | Owner | Verification | Rollback point |
|---|------|-------|--------------|----------------|

Rules per row:

- **Step** is one action with a start and an end, in imperative voice. If a step needs the word "and" twice, it is two steps.
- **Owner** is a role from the engagement team, and during the cutover window a named person. "Team" is not an owner; the gate treats it as filled but a reviewer should not.
- **Verification** is how you know the step worked, stated so a second person could run it: a status value, a count that reconciles, a test transaction that round-trips, a confirmation received in writing. "Confirm it worked" is not a verification.
- **Rollback point** is one of exactly two things:
  - a rollback action or a reference to a numbered rollback procedure (RB-1, RB-2) defined below the table, or
  - the literal words `No rollback:` followed by the reason there is none and what the remedy is instead. A one-way step is acceptable; an undeclared one-way step is not.
- Order the steps by execution sequence. Where steps run in parallel, give them the same number with a letter suffix (4a, 4b) and say in the step text what they must both precede.

## Rollback procedures

Each RB-n referenced in the table gets a short block below it: trigger, steps, owner, how long it takes, and the state the system is in afterward. A rollback that has never been written down is a hope, not a procedure.

## Sourcing

The runbook is assembled, not authored: steps come from the cutover plan and the readiness pack out of stage 05 Validate, the deployment mechanics from the Solution Design Document, and the freeze and communication steps from the Program Lead's plan. Cite the source document and version in the header block. A step you cannot trace to a plan is a step to raise with the Solution Lead before the window, not to invent.
