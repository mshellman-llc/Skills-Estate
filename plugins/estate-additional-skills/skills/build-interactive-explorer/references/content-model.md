# Content model

Start with `assets/site/content.example.json`. Supply UTF-8 JSON with these top-level fields. IDs are local linking keys, not UI copy.

| Field | Contents |
| --- | --- |
| `meta` | Required `title`, `brand`, `headline`, `intro`. Optional `eyebrow`, `accent` (a phrase shown after the headline, so leave it out of `headline`), `evidenceDate`, `evidenceBoundary`, `scopeNote`, `accessLabel`, `labels`. |
| `paths` | Required nonempty array. Each path has `id`, `title`, `summary`, `roleLabel`, and nonempty `stages`. |
| `people` | Optional roles/audiences, each with `id`, `name`, `mission`, context, jobs and steps. |
| `modules` | Optional capabilities, findings or design areas. |
| `priorities` | Optional scope categories: `id`, `title`, `description`, `items`. |
| `decisions` | Optional unresolved questions and working direction. |
| `roadmaps` | Optional planned work: `id`, `title`, `plan`; optional `summary`, `sourceIds`. |
| `sources` | Source entries: `id`, `title`, `group`, `kind`, `note`; optional `url`, `reviewed`, `locator`. |

## Detail objects

- Stage: `id`, `title`, `summary`, `goal`, `action`, `decision`, `handoff`, `finding`, `openQuestion`; optional `details` (`title`/`body` pairs), `moduleIds`, `sourceIds`.
- Person: `id`, `name`, `roleLabel`, `group`, `mission`, `context`, `trigger`, `scope`, `home`; string arrays `needs`, `questions`; `jobs` (`title`, `statement`, `implication`); `steps`; `sourceIds`.
- Journey step: `title`, `touchpoint`, `current`, `friction`, `action`, `decision`, `proposed`, `handoff`, `check`, `openQuestion`, `sourceIds`.
- Module: `id`, `title`, `fit`, `goal`; string arrays `experience`, `records`, `build`, `questions`, `checks`; optional `capabilityNote`, `planningNote`, `roleIds`, `sourceIds`.
- Priority item: `title`, `description`; optional `fallback`, `dependency`, `sourceIds`.
- Roadmap: `plan` is a complete `roadmap-artifacts` plan (`kit`, `id`, `meta`, `legend`, `blocks`). The generator checks it with the roadmap validator and refuses `live` bindings.
- Decision: `id`, `title`, `question`, `direction`, `gap`, `participants`, `sourceIds`.

Every `sourceIds` entry must resolve. Use `moduleIds`/`roleIds` only for present entries. Use real, safe URLs; omit unavailable links. `reviewed` records an actual review date, not an assumed current state.

Override section labels with `meta.labels`: `people`, `journeys`, `solution`, `roadmap`, `scope`, `decisions`, `sources`. Override module tabs with `experience`, `design`, `checks`.

| Topic | Possible paths | Optional views |
| --- | --- | --- |
| Solution design | Site seller / Enterprise account | People & jobs, Journeys, Solution, Rollout scope |
| Research | Understand / Compare / Apply | Perspectives, Research paths, Findings, Next questions |
| Service launch | Customer / Operations | Audiences, Journeys, Capabilities, Launch priorities |
| Learning | Beginner / Practitioner | Learning paths, Concepts, Practice, Open questions |

Translate decisions and handoffs into meaningful domain choices or next actions. Omit unsupported optional fields; retain a clear stage goal and action.

Store original evidence outside the skill. Task-specific outputs can summarize it under the authorized audience. Keep source IDs in source notes. Label fictional examples, proposals, hypotheses, date boundaries and unresolved questions. Verify current product capabilities through official sources rather than carrying over sample claims.
