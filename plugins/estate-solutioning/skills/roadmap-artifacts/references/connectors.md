# Connecting roadmaps to live data

A roadmap can take its work items from the tools a team already uses. There are two modes, and a plan can use both.

| Mode | Who reads the data | When | What viewers see |
|---|---|---|---|
| **Snapshot** | Claude, in the conversation, through its connector tools | At build time | Fixed data with its source and date in the footer (`meta.sources`) |
| **Live** | The published page, through the viewer's own claude.ai connectors (`mcp` capability) | Every view, refreshed on a schedule | Current data, a "Live · Linear · 3 min ago" status, and the snapshot as fallback |

Always build the snapshot first. It is the first paint, the fallback when a viewer has no access, and the version that works outside claude.ai.

## Snapshot mode

1. Find the connector tools for the source (ToolSearch with the tool's name, such as "linear issues" or "jira search"). If the connector failed to connect, tell the user. Do not treat it as missing.
2. Read only what the roadmap needs: one project, team, cycle, board, epic or sheet range. Never sweep a whole workspace.
3. Map the items into the plan's blocks yourself, using the field intents below.
4. Add a `meta.sources` entry for each source: `{"name": "Linear", "detail": "Team Payments, Cycle 12", "retrieved": "2026-10-29"}`.

## Live mode

Add a `live` array to the plan. Each binding watches one read-only tool and fills one block.

```json
"live": [{
  "block": 0,
  "server": "Google Sheets",
  "tool": "get_values",
  "input": { "spreadsheetId": "1AbC…", "range": "Planning!A1:H60" },
  "items": "values",
  "format": "rows",
  "map": { "id": "ID", "title": "Workstream", "group": "Team", "owner": "Owner", "start": "Start", "end": "End", "deps": "Depends on" },
  "values": { "group": { "Payments": "pay", "Core": "core", "*": "core" } },
  "refetch": 300000,
  "verified": "2026-10-29: get_values returns {range, values: [[row], …]}; first row is the header."
}]
```

| Key | Notes |
|---|---|
| `block` | Index of the block to fill: `board`, `matrix`, `timeline` or `table`. |
| `server` | The connector's display name in claude.ai, such as "Google Sheets", "Linear" or "Atlassian". |
| `tool`, `input` | The read tool and its arguments, exactly as the tool's input schema names them. |
| `items` | Dot path to the list in the tool's payload. Empty when the payload is the list. |
| `format` | `"objects"` (default) or `"rows"` (first row is the header; map by header name). |
| `map` | Item field → path or header. Fields: `id`, `title`, `body`, `col`, `row`, `group`, `lane`, `owner`, `points`, `start`, `end`, `deps`, `kicker`, plus `fields: {"Label": path}` and `tags: [{path, prefix?, tone?, tones?}]`. `{"const": "now"}` sets a fixed value. |
| `values` | Lookup tables that turn source values into kit ids: `col` (status → column id), `row`, `group` (→ legend key), `lane`. `"*"` is the catch-all. Lookups ignore case. |
| `defaults` | `{col, row, group}` used when a lookup has no match and no `"*"`. |
| `limit` | Maximum items (default 200). Extra items are counted in "N not shown". |
| `autoRange` | Timelines only. Default true: the axis stretches to fit the data. |
| `refetch` | Poll interval in ms. Minimum 30000, default 300000. |
| `verified` | **Required.** The date you observed a real result from this tool and matched the paths to it. |

### Rules for live bindings

- **Never guess a payload shape.** Before writing `items` and `map`, read the tool's input schema in this session, make one real read call on the user's data, and take the paths from that result. If you cannot make the call, ship snapshot mode only and say why. `build.py --check` refuses a binding without `verified`.
- Never put observed values into the page as sample data. Snapshot data is fine only when the user asked for a roadmap of that data.
- Read tools only. The kit never writes back to a source. Card moves on the board stay a proposal in the viewer's browser.
- Each viewer sees what their own connector can see. A viewer without access gets the snapshot and a short message telling them how to fix it.
- Publish with the `capabilities` that `build.py` prints: `{"mcp": {"servers": [{"server", "tools"}]}}`, listing only the tools the bindings use.

### What viewers see when something fails

`rk-live.js` handles each connector error code separately:

| Code | Behaviour |
|---|---|
| `needs_reauth` | Snapshot restored. "Reconnect {server} in claude.ai Settings → Connectors." |
| `server_not_connected` | Snapshot restored. "Add {server} in claude.ai Settings → Connectors to see live data." |
| `selection_required` | Snapshot restored. Asks the viewer to choose a connector when claude.ai prompts. |
| `approval_required` | Snapshot restored. An "Allow {server}" button that makes one call. |
| `not_in_manifest`, `blocked_by_policy`, `server_not_found` | Snapshot restored with the reason. |
| `server_unavailable`, retryable `upstream_error` | Last good data kept. One retry after the stated delay. |
| `tool_error` | Last good data kept, with the tool's message. |
| `not_granted`, `capability_disabled`, page outside claude.ai | Snapshot, labelled with its date. |

## Field intents by source

These say which source field feeds which roadmap field. They are not payload paths. Confirm the paths against a real result as described above.

| Source | Board column (`col`) | Group (`group`) | Owner | Points / size | Dates | Dependencies |
|---|---|---|---|---|---|---|
| Google Sheets | a Status or Horizon column | Team / Theme column | Owner column | Points column | Start, End columns | "Depends on" column of ids |
| Linear | issue state, or project status | team, project or label | assignee | estimate | project start and target dates; cycle dates | blocking relations |
| Jira (Atlassian) | status category or fix version | component, epic or label | assignee | story points field | start date and due date; sprint dates | "is blocked by" links |
| Asana | section, or a custom Status field | project or tag | assignee | custom number field | start on and due on | dependencies |
| Notion database | a Status or Select property | a Select property | a Person property | a Number property | a Date property (start and end) | a Relation property |
| GitHub Projects | Status field | label or repository | assignees | custom number field | iteration or date fields | linked issues |
| Monday, ClickUp | status column | group or list | people column | number column | timeline or date columns | dependency column |

Only Google Sheets has been verified against a real result (2026-10-29: `get_values` returns `{range, values: [[…]]}`). Every other row is a starting point to check.

## Metrics in the header

Header stats (`meta.stats`) can come from an analytics connector in snapshot mode. Examples: activation rate from Amplitude, or uptime from a monitoring tool. Record the query and date in `meta.sources`. Live header stats are not supported yet.
