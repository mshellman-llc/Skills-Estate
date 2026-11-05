---
skill: tracker-intake
title: Weekly tracker export delta from a non-Jira board
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: ad155d56dd3ba52562f7e462af4e145db73e621812205a2933adac24c6d21fba
---

## Request

Priya Nair, the project manager at Larkfield Council, sent two exports from their Tasklane board for the online permits project: last week's and today's (see inputs/). Please run intake on the new one and tell me what changed since last week, ready to hand to the review site refresh.

## Inputs

Run of the built `tracker-intake` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### export-2026-10-28.csv

ID,Title,State,Kind,Parent,Cycle,Estimate,Tags,Priority,Created,Updated,Blocked by
LP-1,Online permit applications,In Progress,Epic,,,,,High,2026-09-01,2026-10-20,
LP-2,Applicant account sign-up,Done,Story,LP-1,Cycle 3,3,portal,High,2026-09-02,2026-10-14,
LP-3,Upload supporting documents,In Progress,Story,LP-1,Cycle 4,5,portal,High,2026-09-02,2026-10-27,
LP-4,Fee payment,Ready,Story,LP-1,Cycle 4,8,payments,High,2026-09-03,2026-10-22,LP-3
LP-5,Case officer queue,Backlog,Story,LP-1,,,staff,Medium,2026-09-10,2026-10-10,
LP-6,SMS reminders,Backlog,Story,LP-1,,2,,Low,2026-09-12,2026-10-10,

#### export-2026-11-03.csv

ID,Title,State,Kind,Parent,Cycle,Estimate,Tags,Priority,Created,Updated,Blocked by
LP-1,Online permit applications,In Progress,Epic,,,,,High,2026-09-01,2026-11-02,
LP-2,Applicant account sign-up,Done,Story,LP-1,Cycle 3,3,portal,High,2026-09-02,2026-10-14,
LP-3,Upload supporting documents,In Review,Story,LP-1,Cycle 4,5,portal,High,2026-09-02,2026-11-02,
LP-4,Fee payment,Awaiting Council,Story,LP-1,Cycle 5,13,payments,High,2026-09-03,2026-10-31,LP-3
LP-5,Case officer queue,In Progress,Story,LP-1,Cycle 5,3,staff,Medium,2026-09-10,2026-11-01,
LP-7,Refund requests,Backlog,Story,LP-1,,,payments,Medium,2026-10-30,2026-10-30,
LP-7,Refund requests (duplicate row),Backlog,Story,LP-1,,,payments,Medium,2026-10-30,2026-10-30,

#### priya-email.txt

From: Priya Nair <priya.nair@example.com>
Date: 3 November 2026
Subject: Permits board exports

Hi,

Attached are two exports from our Tasklane board for the online permits project (key prefix LP). Both are the full board, all items, using the "Table CSV" export.

- export-2026-10-28.csv is last week's.
- export-2026-11-03.csv is today's.

Column names in Tasklane differ from Jira: ID is the ticket key, Title is the summary, State is the status, Kind is the type, Parent is the epic, Cycle is the sprint, Estimate is story points, Tags are labels.

"Awaiting Council" is a state we added this week. It means the work is finished on our side and we need a council decision before it can move, so please treat it as blocked.

The board links are https://tasklane.example.com/items/LP-1 and so on.

Thanks,
Priya

## Output

Today's Tasklane export has 6 tickets. Compared with last week's, 1 was added, 1 was removed and 3 changed. I ran the intake steps by hand because I can't execute `scripts/intake.py` here, so the SHA-256 values are placeholders until the script is run on the original files.

#### What changed since 28 October

| Ticket | Change |
|---|---|
| LP-7 Refund requests | Added. Story under LP-1, Backlog, tagged payments, no estimate or cycle. |
| LP-6 SMS reminders | Removed from the export. It was a Backlog story estimated at 2 points. The export doesn't say whether it was deleted, archived or moved to another board. |
| LP-3 Upload supporting documents | State changed from In Progress to In Review. Still Cycle 4, 5 points. |
| LP-4 Fee payment | State changed from Ready to Awaiting Council, now category `blocked`. Moved from Cycle 4 to Cycle 5, and the estimate rose from 8 to 13. It is still blocked by LP-3. |
| LP-5 Case officer queue | State changed from Backlog to In Progress. Now in Cycle 5 with a 3-point estimate; it had neither last week. |

LP-1 and LP-2 have no tracked field changes. LP-1's updated date moved to 2 November, but the delta compares only summary, status, category, sprint, points, epic, type, description hash and blocked-by.

#### Conflicts

- **Duplicate key LP-7.** The new export has two LP-7 rows: "Refund requests" and "Refund requests (duplicate row)". The adapter keeps the first and skips the second. Priya Nair should confirm whether the second row is a stray copy or a different ticket with a mistyped ID.
- **Unknown state "Awaiting Council".** The default status list doesn't know it, so the adapter would have mapped it to `todo` and flagged it. Priya's email says it means a council decision is needed, so I added `"Awaiting Council": "blocked"` to `tracker.status_map`. With that in place there is no status conflict.

#### Read these with care

- LP-4's estimate rose from 8 to 13 points and it slipped a cycle. The export records the change but not the reason, and it isn't an approved scope change. Priya or the product owner would need to confirm it.
- The blocked category comes from Priya's description of the state. The export doesn't say what decision is outstanding or who at the council owns it.
- LP-3 being In Review doesn't mean it is deployed.
- Neither export has a Description column, so every ticket has empty acceptance and background extracts. Readiness checks downstream will show no acceptance criteria.

#### Setup and assumptions

- **Adapter:** `table-csv`, because Tasklane isn't Jira. Column mapping, taken from Priya's email: ID to key, Title to summary, State to status, Kind to type, Parent to epic, Cycle to sprint, Estimate to points, Tags to labels, and Priority, Created, Updated and Blocked by to the matching fields.
- **Base URL:** `https://tasklane.example.com/items/`, so pages can link each ticket.
- **Origin:** Tasklane table CSV export sent by Priya Nair, Larkfield Council project manager, by email on 3 November 2026.
- **Scope:** online permits project (prefix LP), full board, all items. I took this from her email.
- **Baseline:** the 28 October export was processed first, giving 6 tickets and no delta. The 3 November export was then processed against it.
- **Dropped fields:** the export has no comment, assignee or reporter columns, so nothing needed redacting. The intake record still carries the standard redaction notes.
- **Dates:** the 3 November export's latest update (2 November) is newer than last week's (27 October), so `--allow-older` isn't needed.
- **Links:** the LP-4 blocked-by LP-3 link appears on one side only. The adapter copies it across, so LP-3 now lists LP-4 under `blocks`.

To run it for real, use this command with the files saved to the engagement folder:

```bash
python3 scripts/intake.py --config config/site.json --input export-2026-11-03.csv \
  --out tracker --origin "Tasklane table CSV export from Priya Nair, Larkfield Council PM, email of 3 November 2026" \
  --scope "Online permits project (LP), full board, all items"
```

Run the same command on `export-2026-10-28.csv` first so the delta has a baseline. Keep both original files in the evidence folder, not in the site.

#### Next step

Hand `tickets.json` and `delta.json` to `review-site refresh` or `moscow-story-map queue`. The queue should list LP-7 as a new ticket to map or class, and LP-6 as no longer in the export. If the story map has a story tied to LP-6, someone needs to decide whether it leaves scope. The tracker can't make that decision.

#### Files

All in `./out/`. These are hand-built stand-ins for the script's output.

- `config/site.json`: the `tracker` block described above.
- `tracker/tickets.json`: 6 canonical tickets from the 3 November export.
- `tracker/delta.json`: added `LP-7`; removed `LP-6`; changed `LP-3`, `LP-4` and `LP-5` with the field-level changes in the table above.
- `tracker/intake-log.json`: one record for each export, with origin, scope, adapter, ticket count and latest update. The second record carries the LP-7 duplicate-key conflict.
