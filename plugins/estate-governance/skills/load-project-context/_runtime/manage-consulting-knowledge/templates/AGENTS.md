---
client: "{{client}}"
client_id: "{{client_id}}"
sf_opportunity_ids: []
status: active
as_of: "{{today}}"
created_from: "knowledge-hub init"
---

# {{client}}: AI Knowledge Hub index

This file is the map. Any agent or person landing in this folder reads it first.
An unindexed file does not exist. `CLAUDE.md` is a one-line pointer here so
Claude Code auto-loads the same content that ChatGPT, Codex, and Cursor read
natively.

## Session start

1. Run the knowledge-hub skill's `hub_workspace.py audit --hub .` before touching
   any work. It reports sync conflict copies and any commit that a Drive sync race
   dropped off the branch. A human would never notice a clobbered ref; your agent
   notices for you. If it reports a blocking finding, run `doctor` and read what
   it repaired before continuing.
2. Read `STANDARDS.md` (claim tags, IDs, frontmatter, commit rules) and, for a
   pursuit, `METHODOLOGY.md` (the seven-phase pipeline).
3. Read `00-CLIENT.md`, then the one front door for the opportunity or engagement
   you are working, then at most four task-relevant records.

## Current direction

State the working thesis in three lines and date it. When a pivot lands, rewrite
this block and move the superseded thesis to the archive table below.

- Direction: (not yet stated)
- Since: {{today}}
- Decided by: (owner)

## Start here, in order

1. `00-CLIENT.md`
2. `account/` records that exist
3. `opportunities/<id>/00-OPPORTUNITY.md` or `engagements/<id>/00-ENGAGEMENT.md`
4. `TODO.md` for who owns what

## File index

| Path | What it is | Owner | Status |
|---|---|---|---|
| `STANDARDS.md` | Rules for every file in this hub | knowledge-hub skill | final |
| `METHODOLOGY.md` | Pursuit research and scoping pipeline | knowledge-hub skill | final |
| `TODO.md` | Human and agent assignments, updated on handoff | deal owner | live |

## Archive: do not build from these

| Path | Why archived | Superseded by | Date |
|---|---|---|---|

## Dormancy

A hub untouched for 60 days gets a line here naming the outcome (won, lost,
paused) so a dead folder is distinguishable from a live one without checking
file dates. `audit` warns when this is due.
