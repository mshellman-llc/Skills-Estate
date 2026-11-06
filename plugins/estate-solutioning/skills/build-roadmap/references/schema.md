# Plan schema (kit v1)

A roadmap is one JSON object, saved as `plan.json` beside the kit files. The renderer in `assets/rk.js` draws it with `assets/rk.css` and the org theme (`theme.css`). Write data only. Do not add CSS, change colors or write new markup. Colors and fonts come from the mode defaults or the org theme. See `branding.md`.

## Top level

```json
{
  "kit": 1,
  "id": "acme-roadmap-h1-2027",
  "template": "product-now-next-later",
  "meta": { },
  "legend": { },
  "blocks": [ ]
}
```

| Key | Required | Notes |
|---|---|---|
| `kit` | yes | Always `1`. |
| `id` | yes | Stable slug. The board remembers card moves in the viewer's browser under this id. |
| `template` | no | Catalog id from `catalog.md`. Lets a later session know which template made the plan. |
| `persist` | no | `false` stops the board from remembering moves. |
| `live` | no | Connector bindings that refresh blocks with live data. See `connectors.md`. |

## meta (header strip)

| Key | Type | Notes |
|---|---|---|
| `title` | string | Required. A name, such as "Tallyroom H1 2027 roadmap". |
| `eyebrow` | string[] | Short mono labels above the title: roadmap type, period, stage. |
| `subtitle` | string | One or two sentences: scope, team, the hard constraint. |
| `northStar` | `{label, value}` | Accent pill. Use for the north-star metric, launch promise or end-state. |
| `stats` | `[{label, value, target?, tone?}]` | Header tiles. `target` renders as `value → target` (current vs target SLOs, metrics). |
| `source` | string | Footer, left. Say "Example data" when inputs were invented. |
| `sources` | `[{name, detail?, retrieved?}]` | Where the data came from, such as `{"name": "Linear", "detail": "Team Payments", "retrieved": "2026-10-29"}`. Shown in the footer. |
| `mode` | `"relaxed"` (default), `"compact"` or `"editorial"` | The roadmap's format, fixed at build time. Viewers cannot switch it. |
| `corners` | `"rounded"` (default), `"square"` or `"brand"` | Rounded uses 4, 8 and 12px corners in every mode. Square removes them. Brand uses the profile's radius. |
| `logo` | `{file, alt}` | The org's real logo file, relative to the plan. `build.py` copies it and sets `src`. Omit when there is no file. |
| `updated` | string | Footer, right. ISO date. |
| `citeHref` | string | Prefix for evidence links, default `#ev-`. `cite: [3]` links to `#ev-3`. Set it to the host page's evidence-list anchor when the host owns the list. |

## legend

```json
{ "title": "Theme", "items": [{ "key": "onb", "label": "Onboarding", "c": 1 }],
  "symbols": [{ "label": "Milestone", "shape": "diamond" }, { "label": "Buffer", "shape": "hatch" }] }
```

`items` are the categorical groups: theme, team, channel, function, consumer type, epic, phase. `c` is a palette slot from 1 to 6. Use at most 6 groups. Clicking a legend item filters the page to that group. `symbols` explain shapes and are not filters.

Semantic tones are separate from groups: `good`, `warn`, `crit`, `info`, `muted`. Use tones for status, risk, confidence, severity and capacity. Never use a group color to mean risk.

## Shared: card

Used by `board` and `matrix`.

| Key | Notes |
|---|---|
| `id` | Required on movable boards. |
| `col` | Column id. `row` is also required in a matrix. |
| `group` | Legend key. Shows the colored group label. |
| `kicker` | Short text after the group label, such as `L-14`, `T-3` or `Q2`. |
| `title` | Specific, named initiative. Never "Blog post" or "Refactor". |
| `body` | The problem or why. One sentence. |
| `fields` | `{ "Outcome": "...", "Depends on": "..." }` or `[["k","v"]]`. Label/value rows. |
| `tags` | `"M"` or `{ "t": "Conf: Low", "tone": "crit" }`. Size, confidence, risk, format, funnel stage. |
| `owner` | Name, or `"TBD"` for a placeholder slot. `false` hides the slot. |
| `points` | Number. Summed against column `capacity`. |
| `ref` | Space-separated ids this card links to. Hovering highlights them. |
| `cite` | Evidence numbers, such as `[2]` or `[1, 4]`. Each renders as a small superscript link to that entry in the evidence list. Callouts, table rows and timeline rows take `cite` too. |

## Blocks

Each block takes optional `title`, `kicker` (small mono text after the title) and `note` (one line of help).

### `board`: columns of cards

`columns: [{id, title, subtitle?, capacity?, tags?}]`, `cards: [card]`, `movable` (default true), `stack` (default true: columns stack on phones; `false` keeps a swipeable row), `unit` (capacity unit such as "pts"), `capacityLabel`.

A column with `capacity` shows a meter of summed `points`. It turns red when over. Meters recount when cards move.

Use for: now/next/later, maturity stages, migration phases, GTM stages, sprints, quarterly themes.

### `timeline`: Gantt, swimlanes, countdown

| Key | Notes |
|---|---|
| `start`, `end` | ISO dates. `end` is inclusive. Every bar must fall inside. |
| `scale` | `day`, `week`, `month` or `quarter`. |
| `countdown` | `{date, unit: "week" or "day"}`. The axis reads T-n … T-0, with the event at the right edge. |
| `rows` | See below. |
| `markers` | `[{date, label, tone?, dashed?}]`. Vertical lines across all rows: launch, freeze, event. |
| `today` | ISO date. Dashed "Today" line. |
| `critical` | Bar ids on the critical path. Dependency arrows between them draw in red. |
| `relative` | `week` or `day`. Labels the axis 1, 2, 3 from `start` for plans with durations but no calendar dates. Bar dates then only position bars. |
| `labelHeader`, `labelWidth`, `unitWidth` | Optional layout overrides. |

Row: `{id, label, group?, lane?, laneGroup?, owner?, heat?, bars?, milestones?}`.

- Single-bar row: put `start`, `end`, `deps`, `kind` on the row itself. Its `id` is the bar id.
- Multi-bar row (a swimlane): `bars: [{id, start, end, label, group?, kind?, deps?}]`. Overlapping bars stack into sub-tracks automatically.
- `lane`: rows that share a lane name sit under a lane header.
- `kind`: `buffer` (hatched) or `tentative` (dashed outline).
- `deps`: ids of bars that must finish first. Draws an arrow.
- `milestones: [{date, label, id?}]`: diamonds with date labels.
- `heat: {n: 1-3, tone?, title?}`: risk heat next to the row label.

### `matrix`: phases × lanes

`columns: [{id, title, subtitle?, tone?, meter?, split?, tags?}]`, `rows: [{id, label, group?}]`, `cards: [card with col and row]`. Empty cells say "No work planned". On phones each column becomes a section with its lanes inside.

`split` on a column: `{label, unit, parts: [{label, value, group or tone}]}`. Shows a brand-vs-demand or effort split bar.

Use for: GTM phases by function, brand/demand tracks by quarter, reliability lanes by effort tier, content pillars by week.

### `callouts`

`items: [{title, body?, meta?, tone?, ref?}]`, `numbered` (default true). Use for fire-now items, riskiest handoffs, must-not-slip activities and watch lists. `ref` links to bar or card ids.

### `meters`

`items: [{label, value, max, unit?, tone?, group?, note?}]` for single meters, or `{title, label, unit, parts: [...]}` for split bars. Use for budget weight per channel, capacity per team and SLO current vs target.

### `table`

`columns: [{key, label, swatch?}]`, `rows: [{...cells, ref?, group?}]`. A cell may be `{t, tone}` to render a tag. A column keyed `owner` renders owner slots. `swatch: true` shows the row's group color in that cell. Use for RAID registers, dependency lists and kill criteria.

### `checklist`

`items: ["text" or {t, owner?, done?}]`. Use for a day-of checklist at T-0 or a launch-day runbook.

### `evidence`

`items: ["basis · source", ...]`, optional `intro`. One numbered list; item n gets the id that `cite: [n]` links to. Write each basis once here instead of labeling every card. A plan has at most one evidence block, and every cite number must have an entry. Leave it out when the host page already owns the evidence list.

### `text`

`body: "..."` or `["para", "para"]`. Use sparingly, for a short framing note.

## Embedding

- `<rk-roadmap src="plan.json" mode="relaxed|compact|editorial" live="off"></rk-roadmap>` loads and renders a plan. An inline `<script type="application/json">` child works instead of `src`.
- `RoadmapKit.mount(plan, element, {mode, live, embed, parts})` renders into any element and returns the instance. `modeSwitch: true` adds a Relaxed / Compact / Editorial switch; use it only on design review pages.
- A page with `<main id="rk-root">` and `<script type="application/json" id="rk-data">` renders on load.

## Rules the checker enforces

`scripts/build.py --check` fails when: `kit`, `id` or `meta.title` is missing; a card points at an unknown column or row; a card uses a group missing from the legend; a movable card has no id; a cite number has no evidence entry; a bar ends before it starts or falls outside the timeline range; a dependency names an unknown bar.
