# Rendering JTBD work with roadmap components

A JTBD readout is usually Markdown. When the user asks for a page, an artifact or a section inside another estate page, build it from the roadmap components in `roadmap-artifacts` instead of writing HTML. The components give every readout the same layout, the selected brand profile's colors and fonts, and one evidence list that every claim points to.

## Build a page

Write a plan in the kit's JSON schema (`roadmap-artifacts/references/schema.md`) and build a single file from the skill directory:

```bash
python3 ../roadmap-artifacts/scripts/rk_embed.py page jtbd-plan.json --output attempt-001/jtbd-readout.html
```

In an installed package the script is at `_runtime/roadmap-artifacts/scripts/rk_embed.py`. Add `--profile /path/to/brand.md` for a confirmed project profile; without one the estate neutral profile applies. The page embeds its data, styles and script, loads nothing from the network, and passes `brand-renderer`'s palette check only when every color comes from the profile. Inspect the rendered page before delivery; a successful build proves only that the plan validated.

Pick one format for the page with `meta.mode`: `relaxed` (the default), `compact` for a dense working readout, or `editorial` for a strategy readout. Viewers cannot switch it.

## Which component carries which output

| JTBD output | Block | How to fill it |
|---|---|---|
| Job statements | `table` | Columns for situation, motivation and outcome. Put the dimensions (functional, emotional, social) in a tag column. One row per job, with `cite` on the row. |
| Struggling moments | `callouts` | One numbered callout per moment, in the order they occur. Title is the moment in the person's words; body names what they did next. Set `tone: "muted"`; the kit's red default implies a severity the research may not support. |
| Hire and fire criteria | `table` | Columns for criterion, hire or fire, and the switch it came from. Hire and fire are categories, not states, so do not give them status tones. |
| Candidates prioritized by job | `board` | One column per job, ordered by how much the job's struggle costs. Cards are candidate features or bets with fields for the moment addressed and the expected outcome. Set `movable: false` unless the team will reorder them live. |
| Jobs across segments | `matrix` | Columns are segments, rows are jobs, cards are the moments or criteria that differ. Empty cells read "No work planned", so only use this when every cell has evidence or an intentional gap. |
| Evidence | `evidence` | The last block. Item n is the basis and source for every `cite: [n]`. |

Keep group colors for categories that the reader filters on, such as segment or job. Status tones (`good`, `warn`, `crit`) mean state: confirmed, at risk, blocked. A candidate job is not "at risk" because it is a hypothesis.

## Show evidence as numbers

Follow the skill's evidence rule in the rendered page too. Each job, moment, criterion or candidate carries `cite` with one or more numbers. The kit renders them as small superscript links to the evidence block. Write the basis once per evidence item: "Reported · Interviews 3, 5 and 9, recent switchers" or "Hypothesis · reasoned from the support ticket themes, no interviews yet". When every job on the page is a candidate, say so once in the evidence block's `intro` and once in `meta.subtitle`. Do not add "hypothesis" tags to cards or rows.

The builder fails when a cite number has no evidence entry, when a standalone page uses cite numbers without an evidence block, and when a plan has more than one evidence list.

## Worked plan

The values are a synthetic example for testing the layout. Replace every value with sourced material.

```json
{
  "kit": 1,
  "id": "jtbd-example-invoicing",
  "persist": false,
  "meta": {
    "title": "Why agencies switch invoicing tools",
    "eyebrow": ["Jobs to be done", "Synthetic example"],
    "subtitle": "Candidate jobs from a synthetic interview set. Validate them before they drive the roadmap.",
    "source": "Synthetic example for layout testing"
  },
  "legend": {"title": "Job", "items": [
    {"key": "paid", "label": "Get paid on time", "c": 1},
    {"key": "bill", "label": "Bill without rework", "c": 2}
  ]},
  "blocks": [
    {"type": "table", "title": "Job statements", "columns": [
      {"key": "situation", "label": "When", "swatch": true},
      {"key": "motivation", "label": "I want to"},
      {"key": "outcome", "label": "So I can"}],
     "rows": [
      {"group": "paid", "situation": "A client invoice passes 30 days", "motivation": "chase it without an awkward call", "outcome": "keep cash flow predictable", "cite": [1]},
      {"group": "bill", "situation": "A month of timesheets closes", "motivation": "turn hours into line items once", "outcome": "send invoices the same day", "cite": [2]}]},
    {"type": "callouts", "title": "Struggling moments", "items": [
      {"title": "Retyping hours from the timesheet export", "body": "Two owners stopped invoicing weekly and moved to monthly batches.", "tone": "muted", "cite": [2]},
      {"title": "Writing the third reminder by hand", "body": "One owner left the invoice unpaid rather than send another email.", "tone": "muted", "cite": [1]}]},
    {"type": "board", "title": "Candidates by job", "movable": false,
     "columns": [{"id": "paid", "title": "Get paid on time"}, {"id": "bill", "title": "Bill without rework"}],
     "cards": [
      {"col": "paid", "group": "paid", "title": "Automatic reminders at 3, 7 and 14 days", "owner": false, "fields": {"Moment": "Writing the third reminder", "Outcome": "Fewer invoices past 30 days"}, "cite": [1]},
      {"col": "bill", "group": "bill", "title": "Import timesheet CSV into line items", "owner": false, "fields": {"Moment": "Retyping hours", "Outcome": "Same-day invoicing"}, "cite": [2]}]},
    {"type": "evidence", "title": "Evidence", "intro": "Every job on this page is a candidate until interviews confirm it.",
     "items": [
      "Hypothesis · reasoned from synthetic reminder-email logs; no interviews yet",
      "Hypothesis · reasoned from synthetic timesheet export volumes; no interviews yet"]}
  ]
}
```

## Inside another estate page

`interactive-proposal` and `journey-mapping` already inline the components through their builders. To add a JTBD section to one of them, give the host page a container with `class="rk rk-embed"`, include the CSS and JS that `rk_embed.assets()` returns, and call `RoadmapKit.mount(plan, element, {embed: true, live: false, parts: ["blocks"]})`. When the host page owns the evidence list, leave the `evidence` block out and set `meta.citeHref` to the host list's anchor prefix, such as `#ev-` in a journey map, so the numbers continue that list.
