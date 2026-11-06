# {{SPRINT_NAME}} plan

Dates: {{START_DATE}} to {{END_DATE}}
Team: {{TEAM}}
Status: proposed until the team commits at sprint planning

## Goal

{{ONE_SENTENCE_OUTCOME}}

## Capacity

| Person | Hours | Basis |
|---|---:|---|
| {{NAME}} | {{HOURS}} | {{PTO_ON_CALL_AND_OTHER_DEDUCTIONS}} |

Capacity: {{CAPACITY_HOURS}} h. Commit target: {{COMMIT_PCT}}% ({{COMMIT_TARGET_HOURS}} h). Stretch target: {{STRETCH_PCT}}%, with {{RESERVE_HOURS}} h held in reserve.
Recent velocity: {{VELOCITY_HISTORY}} (average {{AVERAGE_VELOCITY}}), or "not available".

## Committed work

| ID | Item | Owner | Hours | Points | Dependencies (RAID) | Main risk and mitigation |
|---|---|---|---:|---:|---|---|
| {{REQ_ID}} | {{TITLE}} | {{ASSIGNEE}} | {{HOURS}} | {{POINTS}} | {{D_IDS}} | {{RISK}} |

Committed total: {{COMMIT_HOURS}} h ({{UTILIZATION}}% of capacity).

## Stretch work

Pull these only after the committed work is done.

| ID | Item | Hours |
|---|---|---:|
| {{REQ_ID}} | {{TITLE}} | {{HOURS}} |

## Dependencies to confirm before day one

| RAID ID | Needed from | Owner | Needed by | Confirmed |
|---|---|---|---|---|
| {{D_ID}} | {{TEAM_OR_VENDOR}} | {{OWNER}} | {{DATE}} | {{YES_OR_NO}} |

## Definition of done

{{TEAM_DOD_LIST}}

## Checkpoints

- Mid-sprint check-in: {{DATE}}
- Dependency confirmations: {{DATE}}
- Sprint review and retrospective: {{DATE}}

## Gate

{{SPRINT_CHECK_COUNTS_AND_DISPOSITION}}

Proposed RAID entries for track-delivery: {{PROPOSED_RAID_ENTRIES_OR_NONE}}
