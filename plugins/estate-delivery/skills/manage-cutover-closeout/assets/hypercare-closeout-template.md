# Hypercare Closeout Report: {CLIENT} {ENGAGEMENT}

Record document; nobody countersigns it. Every section stays present: fill it
or state why it is empty with an owner and a resolve-by date.
Gate: `python3 scripts/closeout_gate.py <this file> --type closeout`

- Client: {CLIENT}
- Engagement: {ENGAGEMENT_NAME} (SOW {SOW_ID})
- Hypercare window: {START_DATE} to {END_DATE} (per SOW section {N}: "{CLAUSE_EXCERPT}")
- Go-Live Acceptance status: {STATUS_FROM_TRACKER, WITH_DATES_AND_REFERENCE}
- As of: {DATE}, built from {TRIAGE_LOG_VERSION} and {TRACKER_VERSION}

## Window summary

Counts computed from the log below, not estimated.

- Issues raised: {N} (Sev 1: {N}, Sev 2: {N}, Sev 3: {N}, Sev 4: {N})
- Closed with verified resolution: {N}
- Open, transferred: {N}
- Change-order candidates routed: {N}
- Withdrawn: {N}

## Hypercare issue log

| ID | Severity | Issue | Disposition |
|----|----------|-------|-------------|
| HC-001 | Sev {N} | {ISSUE, WITH_UPSTREAM_DEFECT_ID_IF_CARRIED_IN} | Closed: {FIX} verified by {WHO} on {DATE} |
| HC-002 | Sev {N} | {ISSUE} | Change-order candidate: routed to track-delivery {DATE} |

## Open transfers

| ID | Now owned by | Reference given to client |
|----|--------------|---------------------------|
| {HC_ID} | {SUPPORT_ARRANGEMENT} | {TICKET_OR_DOC} |

## Change-order candidates

Routed, not priced. Pricing and sizing belong to the change-order machinery.

| ID | Request | Routed to | Date |
|----|---------|-----------|------|
| {HC_ID} | {WHAT_WAS_ASKED} | track-delivery | {DATE} |

## Actuals vs estimate

Estimates from the quote ({Q_NUMBER}), actuals from {TIMESHEET_SOURCE} as of
{DATE}. Hours only; no rates, fees, or margin here. Unsourceable cells read
`GAP: <what is missing, who owns it, by when>`. This table feeds future deal
comparables; that is why the sourcing matters.

| Workstream | Estimated hours | Actual hours | Variance | Source |
|------------|-----------------|--------------|----------|--------|
| {WORKSTREAM} | {N} | {N} | {+/-N} | {Q_NUMBER field; timesheet export DATE} |

{ONE_PARAGRAPH_PER_WORKSTREAM_OVER_ABOUT_15_PERCENT_VARIANCE}

## What broke and why

{PER_SEV1_AND_SEV2: what happened, the cause chain, the earliest lifecycle
point it could have been caught, what would catch it next time. Causes, not
blame.}

## Transition

- Transition documentation: {LOCATION}
- Support arrangement taking over: {WHO, FROM_WHEN, CONTACT_MODEL}
- Known issues and accepted limitations handed over: {HC_IDS}
