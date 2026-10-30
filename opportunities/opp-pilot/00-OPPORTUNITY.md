---
title: "opp-pilot"
status: draft
owner: deal owner
updated: "2026-10-30"
sources:
  - knowledge-hub init
---

# opp-pilot

Front door for this pursuit. Short map, not the history. Current answer first.

## Identity

- Client: Example Manufacturing
- Opportunity id: `opp-pilot`
- Salesforce Opportunity: (record id)
- Deal Drive folder: (link to the opportunity's own Drive folder)

## Current state

(one paragraph: stage, next milestone, the number range if priced, dated)

## Active work

- (item, owner, date)

## Unresolved

- (open question or contested claim, with its CLM or ASM id)

## Working areas

| Folder | Holds | Rule |
|---|---|---|
| `inputs/` | Frozen given context: `stated-requirements.md` (REQ ids), `deal-context.md`, `transcripts/` | Frozen before research starts |
| `research/` | Subagent research files, claims tagged, SD ids minted | Gated on landing by the orchestrator |
| `synthesis/` | Requirements theory, fit-gap, seams analysis | Cites ids, owns no facts |
| `evidence/` | `source-register.md` (SRC rows), `evidence-ledger.jsonl` (CLM events) | Append-only ledger under git |
| `deliverables/` | Run records and generated outputs | Authority zero as evidence |

## Records

- `qualification.md`, `discovery.md`, `solution-and-scope.md`, `commercial.md`,
  `pursuit-history.md`: create each when it has durable content, never before.
