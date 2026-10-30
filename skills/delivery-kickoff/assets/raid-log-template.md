# RAID log: {{ENGAGEMENT_NAME}} ({{SOW_ID}})

Seeded at Mobilize by delivery-kickoff from the accepted handoff brief, as of {{SEED_DATE}}.
Stewarded from here by delivery-status. IDs are permanent: never renumber, never reuse.

ID conventions: R-### risks, A-### assumptions, I-### issues, D-### dependencies. Numbers are
zero-padded to three digits and assigned in creation order within each type. A closed item keeps
its row and its ID; set Status to Closed and fill Resolution. New items append at the bottom of
their table.

Status values: Open, Mitigating, Closed. Every Open item has a named owner and a resolve-by date.
An unowned item is a seeding failure, not a backlog.

## Risks

| ID | Risk | Impact | Likelihood | Owner | Status | Resolve by | Gate blocked | Source | Resolution |
|---|---|---|---|---|---|---|---|---|---|
| R-001 | {{RISK}} | {{H_M_L}} | {{H_M_L}} | {{OWNER}} | Open | {{DATE}} | {{GATE_OR_NONE}} | {{HANDOFF_SECTION_OR_TRANSCRIPT}} | |

## Assumptions

| ID | Assumption | Basis | Owner | Status | Validate by | Gate blocked | Source | Resolution |
|---|---|---|---|---|---|---|---|---|
| A-001 | {{ASSUMPTION}} | {{BASIS}} | {{OWNER}} | Open | {{DATE}} | {{GATE_OR_NONE}} | {{SOURCE}} | |

## Issues

| ID | Issue | Impact | Owner | Status | Resolve by | Gate blocked | Source | Resolution |
|---|---|---|---|---|---|---|---|---|
| I-001 | {{ISSUE}} | {{IMPACT}} | {{OWNER}} | Open | {{DATE}} | {{GATE_OR_NONE}} | {{SOURCE}} | |

## Dependencies

| ID | Dependency | Depends on | Owner | Status | Needed by | Gate blocked | Source | Resolution |
|---|---|---|---|---|---|---|---|---|
| D-001 | {{DEPENDENCY}} | {{EXTERNAL_PARTY_OR_SYSTEM}} | {{OWNER}} | Open | {{DATE}} | {{GATE_OR_NONE}} | {{SOURCE}} | |
