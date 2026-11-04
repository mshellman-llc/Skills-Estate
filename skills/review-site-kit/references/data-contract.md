# Data contract

Every skill in the series reads and writes these files. The JSON Schemas in `schema/` are the authority; this page explains who writes each field and when it changes.

## Ownership

| File | Written by | Changes when |
|---|---|---|
| `tracker/tickets.json` | `tracker-intake` adapter | Each new export. Never edited by hand. |
| `tracker/delta.json` | `tracker-intake` | Each new export, against the previous one. |
| `tracker/intake-log.json` | `tracker-intake` | One record appended per export. |
| `tracker/review-queue.json` and `.md` | `moscow-story-map queue` | Each refresh. |
| `config/site.json` | The agent, from the user's decisions | Engagement setup, page or brand changes. |
| `content/stories.json` | The agent; computed fields never stored | A ticket is mapped, a class changes, or story text is revised. |
| `content/questions.json` | The agent | New questions from refinement notes, or a status or answer recorded outside the page. |
| `content/journeys.json` | `journey-mapping` or `sales-process-mapping` output, reshaped | Workflow research changes. |
| `content/processes.json` | The agent, from tickets and design records | A process step or design decision changes. |
| `dist/` | `review-site build` | Every build. Hand edits are lost at the next build. |

## Canonical tickets

An adapter keeps the fields the pages need and drops the rest. Comment text, assignees and reporters are dropped. A description survives only as its acceptance-criteria and background extracts plus a hash. The hash shows a changed description in the delta without storing the text.

`category` is one of `todo`, `wip`, `done`, `canceled` and `blocked`. The adapter maps each status through `tracker.status_map` first, then a default list. An unknown status maps to `todo`. The intake record lists it as a conflict; add it to the map.

`blocked_by` lists the tickets that block this one. In a Jira export those are the `Inward issue link (Blocks)` columns. `blocks` lists the `Outward issue link (Blocks)` columns.

## Stories

Authored fields: `id`, `label`, `step`, `class`, `tickets`, `planned_in`, `roles`, `what`, `interim`, `acceptance`, `depends_on`. The first ticket in `tickets` is the primary ticket; its status, sprint and estimate represent the story. A story with no tickets is not in the tracker yet; set `planned_in` to the epic that plans it.

The renderer adds computed fields under `computed` and never writes them back to `content/stories.json`:

- `status`: the primary ticket's status.
- `sprint` and `points`: from the primary ticket.
- `acceptance`: taken from the tickets unless the story lists its own.
- `questions` and `open_questions`.
- `blockers`: open blocking tickets, plus dependencies on stories that have no ticket.
- `checks` and `ready`: the configured readiness rules. A done story is always ready.

Must share is open Must points divided by open Must, Should and Could points. Stories without an estimate are counted separately in `unestimated_must_should`.

## Questions

`status` is one of Open, Proposed, Partly answered, Answered, Deferred, Blocked and Sandbox check. `answer.label` is `Proposed answer` for the team's proposal or `Answer` for a recorded client decision. The page's shared store can override the status and answer; `decision-register export` merges the store into the authored file's view.

## Shared store

A published page with the `db` capability keeps:

- `answers/<question id>`: `{status, state, answer, conditions, at, by}`.
- `moscow/<story id>`: `{class, note, at, by}`.
- `comments/<question id>/items`: `{text, at, by}`.

The collection names come from `config.store` and default to these. Read the records with the artifact data tool and save them as JSON for `export`.
