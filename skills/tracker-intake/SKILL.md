---
name: tracker-intake
description: Turn a tracker export (Jira CSV, another tracker's table export, or tickets pulled through a connector) into canonical tickets, an intake record and a delta against the previous export. Use when a new Jira or tracker export arrives, to see what changed since the last export, or before refreshing a review site, status report or backlog view. Do NOT use to change tickets in the tracker, to write requirements (requirements-backlog) or to grade readiness for a sprint (backlog-refinement).
---

# Tracker intake

Every refresh starts with intake. The adapter turns the export into `tickets.json`, records where it came from and writes the delta. Downstream skills read only `tickets.json`, so a client on another tracker needs one adapter and nothing else.

## Inputs

| Input | Source | If missing |
|---|---|---|
| The export | Jira "All fields" CSV, a table CSV from another tracker, or JSON tickets you pulled through a connector | Ask for the file. A connector pull needs the user's authorization for that project. |
| `config/site.json` | The engagement folder | Create it with `review-site init`, or write the `tracker` block yourself. |
| Origin and scope | Who supplied the export and what it covers, for example "Jira export from the client PM, project NW, all issues" | Ask; the intake record requires both. |

The `tracker` block in `site.json` selects the adapter:

- `jira-csv`: the default. It reads the repeated Sprint, Labels, link and Comment columns as lists and treats `Inward issue link (Blocks)` as the tickets that block this one.
- `table-csv`: any tracker's table export. Set `tracker.columns` to map `key`, `summary`, `status` and any of `type`, `epic`, `parent`, `sprint`, `points`, `labels`, `priority`, `created`, `updated`, `description`, `acceptance`, `blocked_by` and `blocks` to the export's column names.
- `json`: canonical tickets you wrote from a connector. Follow `schema/tickets.schema.json` in the kit.

Set `tracker.status_map` for statuses the default list does not know. Set `tracker.base_url` to the tracker's browse URL so pages can link each ticket.

## Run

```bash
python3 scripts/intake.py --config <project>/config/site.json --input <export> \
  --out <project>/tracker --origin "<who and how>" --scope "<what it covers>"
```

The script writes these files to `--out`:

- `tickets.json`.
- `delta.json`: added, removed and changed tickets, with field-level changes.
- `intake-log.json`: a record appended for this export, with the original name, SHA-256, received date, origin, scope, redactions and conflicts.

The previous `tickets.json` moves to `history/`. An export with the same hash as the current one changes nothing and reports `unchanged`.

The adapter drops comment text, assignees and reporters. It keeps descriptions only as acceptance-criteria and background extracts plus a hash. Keep the original export in the engagement's evidence folder; it never goes into the skill or the rendered site.

## Report

Report the ticket count and the added, removed and changed counts. List every conflict from the intake record, such as an unknown status or a duplicate key, and fix the `status_map` when a status is unknown. A newer export is not an approved scope change, and a ticket status does not prove deployment. Say what changed in the tracker and leave approval to its owner.

Then hand `tickets.json` and `delta.json` to `moscow-story-map queue` or `review-site refresh`.
