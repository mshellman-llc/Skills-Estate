# Cutover runbook: {CLIENT} {ENGAGEMENT}

- Client: {CLIENT}
- Engagement: {ENGAGEMENT_NAME} (SOW {SOW_ID})
- Cutover window: {START_DATETIME_TZ} to {END_DATETIME_TZ}
- Go / no-go: signed {DATE} by {ROLES} (source: {GATE_RECORD_OR_MINUTES})
- War room: {CHANNEL_AND_BRIDGE}
- Sources: cutover plan {DOC_VERSION}, readiness pack {DOC_VERSION}, Solution Design Document {DOC_VERSION}
- As of: {DATE}, built from {STATE_SOURCE}

## Roles on the day

| Role | Aleysian | Client counterpart | Reachable via |
|------|----------|--------------------|---------------|
| Program Lead | {NAME} | {NAME} | {CHANNEL} |
| Solution Lead | {NAME} | {NAME} | {CHANNEL} |
| TA / deploy | {NAME} | {NAME} | {CHANNEL} |

Escalation path: first {ROLE_NAME}, then {ROLE_NAME}, then CSE {NAME}.

## Go / no-go entry conditions

State each condition that was true at sign-off so drift is visible on the day.

- Open defects at sign-off: {LIST_WITH_IDS_AND_DISPOSITIONS}
- Environment freeze: {IN_PLACE_SINCE, EVIDENCE}
- Pre-cutover backup: {TAKEN_WHEN, WHERE, VERIFIED_HOW}

## Step table

Every row needs an owner, a verification a second person could run, and a
rollback point or `No rollback: <reason and remedy>`. Gate:
`python3 scripts/closeout_gate.py <this file> --type runbook`

| # | Step | Owner | Verification | Rollback point |
|---|------|-------|--------------|----------------|
| 1 | {ACTION} | {ROLE/NAME} | {OBSERVABLE_RESULT} | {ROLLBACK_OR_RB_REF} |
| 2 | {ACTION} | {ROLE/NAME} | {OBSERVABLE_RESULT} | RB-1 |
| 3 | {ACTION} | {ROLE/NAME} | {OBSERVABLE_RESULT} | No rollback: {REASON_AND_REMEDY} |

## Rollback procedures

### RB-1: {NAME}

- Trigger: {WHAT_FAILURE_INVOKES_THIS}
- Owner: {ROLE/NAME}
- Steps: {NUMBERED_STEPS}
- Duration: {ESTIMATE_WITH_SOURCE}
- End state: {SYSTEM_STATE_AFTERWARD}

## Rollback decision rule

- Who can call it: {ROLE}
- Point of no return: after step {N} ({WHY})
- Client communication on rollback: {WHO_SAYS_WHAT_TO_WHOM}

## Post-cutover monitoring

| What | Watched by | Through | Threshold that opens a hypercare issue |
|------|------------|---------|----------------------------------------|
| {SIGNAL} | {ROLE} | {DATE} | {THRESHOLD} |
