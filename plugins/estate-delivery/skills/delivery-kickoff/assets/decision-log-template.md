# Decision log: {{ENGAGEMENT_NAME}} ({{SOW_ID}})

Opened at Mobilize by delivery-kickoff, as of {{SEED_DATE}}.
Stewarded from here by delivery-status. IDs are permanent: never renumber, never reuse.

ID convention: DEC-### in creation order, zero-padded to three digits. DEC, not D, so decision IDs
never collide with the RAID log's dependency IDs.

A decision is logged when a human makes it, with the human named in Made by. This log records
decisions; it never contains a decision an agent made on the humans' behalf. A pending decision is
an open question in the RAID log (usually an A or D item), not a pre-filled row here.

Status values: Proposed, Decided, Superseded. A superseded decision keeps its row; the new row
names the old ID in Supersedes.

| ID | Decision | Date | Made by | Rationale | Options considered | Source | Status | Supersedes |
|---|---|---|---|---|---|---|---|---|
| DEC-001 | {{DECISION}} | {{DATE}} | {{NAMED_HUMAN}} | {{RATIONALE}} | {{OPTIONS}} | {{MEETING_OR_DOC}} | Decided | |
