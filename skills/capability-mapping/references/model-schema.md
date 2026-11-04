# Capability model schema

The model is one JSON file. Every output is built from it, so edit the model and rebuild rather than editing an output. Each `id` is a short stable identifier, unique within its list, that stays fixed once the map is shared. [The synthetic fixture](../fixtures/synthetic-model.json) is a complete example; copy it as a starting point and replace every value.

## Top level

| Key | Required | Contents |
| --- | --- | --- |
| `meta` | yes | Title, organization, scope, state, date and basis note. |
| `stages` | yes | Ordered lifecycle stages, each `{"id", "name"}`. |
| `domains` | yes | Level 1 domains, each `{"id", "name"}`. |
| `goals` | yes; `[]` allowed | Strategy goals the map serves. |
| `capabilities` | yes | Level 2 and Level 3 capabilities. |
| `evidence` | yes; `[]` allowed | Sources cited by capabilities and goals. |
| `open_items` | no | Decisions and questions still to answer, each `{"id", "question", "owner", "affects"}`. Leave `owner` `null` when nobody owns it; the outputs flag it. |

## `meta`

| Key | Required | Contents |
| --- | --- | --- |
| `title` | yes | Page and workbook title. |
| `organization` | yes | The business the map describes. Use a real name only in that client's own workspace. |
| `scope` | yes | One sentence: business, state and decision. |
| `state` | yes | `current`, `target` or `current-and-target`. |
| `date` | yes | ISO date of the scores. |
| `basis_note` | yes | A short plain statement of where the scores came from, shown beside the map. |
| `status` | no | `draft` (default) or `validated`. A draft is labeled on every output. |
| `priority_bands` | no | Agreed thresholds replacing the defaults: `{"invest_now": 6, "plan": 3, "monitor": 1}`. |
| `release` | no | `{"name"}` for the planned release the map is traced against, such as `{"name": "the January release"}`. The name is used mid-sentence, so include its article. Required when any capability has `after_release`. |

## `goals[]`

| Key | Required | Contents |
| --- | --- | --- |
| `id` | yes | For example `G1`. |
| `statement` | yes | The goal in the client's words. |
| `measure` | no | How success is measured, such as a V2MOM measure or a key result. |
| `framework` | no | Where the goal came from: `V2MOM method`, `OKR`, `stated goal` or the client's own term. |
| `sources` | no | Evidence IDs. |

## `capabilities[]`

| Key | Required | Contents |
| --- | --- | --- |
| `id` | yes | For example `C-SVC-03`. |
| `name` | yes | Noun phrase naming what the business can do. Unique within the model, ignoring case. |
| `domain` | yes | A `domains[].id`. |
| `level` | yes | `2` or `3`. |
| `parent` | Level 3 only | The Level 2 capability ID. |
| `definition` | yes | One or two sentences in the client's terms. |
| `aliases` | no | Other names participants used. |
| `status` | yes | `existing`, `partial`, `new` or `redundant`. |
| `stages` | no | Stage IDs. Empty means an enabling capability. |
| `goals` | no | Goal IDs this capability enables. |
| `holders` | no | Business units or companies that perform it today. |
| `systems` | no | Supporting systems, including spreadsheets. |
| `owner` | no | Accountable role or person, when known. |
| `functions` | no | The business functions the capability groups, as short noun phrases. A reference catalog card usually lists them. |
| `kpis` | no | Measures that show the capability improving, each with its direction, such as "First-time fix rate, up". |
| `current`, `target` | scored entries | Whole numbers on the 0 to 5 maturity scale, or `null` for OPEN. `current` must be 0 when `status` is `new`. |
| `after_release` | no | The maturity the named release leaves the capability at, on the same scale. Set it to `current` when the release does not touch the capability. When a release is named, a high-impact capability without it counts as short of target. |
| `delivered_by` | no | The stories or epics that move this capability, each `{"name", "priority", "status", "ref"}`. `priority` is `must`, `should`, `could` or `wont`; `status` is `done`, `in-progress`, `not-started`, `not-ticketed` or `blocked`; `ref` is an optional ticket key. |
| `impact` | scored entries | `high`, `medium`, `low` or `null`. |
| `dimensions` | no | `{"people", "process", "data", "technology", "organization"}`, each `red`, `amber`, `green` or `open`. |
| `score_reason` | scored entries | The reason behind the current score. |
| `impact_reason` | scored entries | Why the capability matters this much. |
| `votes` | no | Stakeholder votes, a whole number of 0 or more. |
| `basis` | yes | `observed`, `reported` or `hypothesis`. |
| `sources` | observed or reported | Evidence IDs. At least one is required unless `basis` is `hypothesis`. |
| `priority_override` | no | `{"band", "reason", "source"}` recording a stakeholder decision that differs from the computed band. |

A Level 2 capability with Level 3 children carries no `current`, `target` or `impact`; its children are scored instead. Every other capability is a scored entry.

## `evidence[]`

| Key | Required | Contents |
| --- | --- | --- |
| `id` | yes | For example `E3`. |
| `label` | yes | What the source is, such as "Service leads interview, 2026-03-04". |
| `type` | yes | `interview`, `workshop`, `transcript`, `document`, `system`, `catalog` or `analysis`. |
| `locator` | no | Path, link or record reference. Leave out private locators from client-facing copies. |

## Validation

`build` and `ingest` refuse a model with any of these errors and name each one:

- missing required keys, or values outside the allowed sets;
- duplicate capability IDs, or two capabilities with the same name ignoring case (rationalize into one and use `holders`);
- references to an unknown domain, stage, goal, parent or evidence ID;
- a Level 3 capability whose parent is missing or is not Level 2, or a parent that carries its own score;
- `status: new` with `current` above 0;
- `basis: observed` or `reported` with no `sources`;
- a `delivered_by` entry without a name, a known priority or a known status, or `after_release` with no `meta.release`.

These conditions are reported as findings rather than errors: goals with no linked capability, Invest now capabilities with no linked goal, scored entries with OPEN values, stages with no capability, overrides that change the computed band, and open items with no owner. With a named release, the outputs also report each goal the release leaves short (a linked high-impact capability below target or without `after_release`), each capability the release leaves lower than today, and each capability whose Must or Should stories are blocked or not yet ticketed.

## Computed fields

`model.computed.json` adds, per scored capability: `rag` (the display color from current maturity, or `open`), `gap`, `impact_weight`, `priority_score`, `band`, `final_band` (the override when present), `rank`, `remaining_gap` and `remaining_score` (target minus `after_release`, and that times the impact weight), and `delivery` (counts of Must and Should stories by status). It adds `findings` and `summary` at the top level. Treat computed fields as outputs; `build` recomputes them and ignores any values already present.
