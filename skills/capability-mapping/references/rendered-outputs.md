# Rendered outputs

All four outputs come from one model build. Their figures match by construction. Rebuild after any change to the model; do not edit an output by hand.

## HTML dashboard

[The starter](../assets/capability-map.html) is built on the Baseline design system from `client-brand`. The build inlines Baseline's palette F tokens unchanged, the Baseline components the page uses and the Stockholm icons it needs. It also swaps the `const MODEL = {...};` block for the computed model, which keeps the page to one file. The Inter font is its only network request. When the page is offline, the system font stands in.

The page leads with the decision and keeps the full record behind it:

1. Page header with the organization, state, score date and title. A Draft badge stays on the title until `meta.status` is `validated`.
2. The lede gives the count of Invest now capabilities as its headline, then the scope sentence and basis note. Beside it, the Invest now and Plan capabilities are listed in rank order.
3. Capability map: Baseline tonal tiles in domain columns, Level 3 children grouped under their parent. A segmented control colors the tiles by priority band or by current maturity, and each tile opens a hover card with its scores, KPIs and reasons.
4. Gap to target: a dumbbell chart in rank order, from today's maturity to the target, with the score at the end of each row.
5. Strategy coverage lists each goal with its measure and the capabilities that deliver it, and flags a goal that has none.
6. Across the customer lifecycle repeats the tiles on the stages they serve, plus an Enabling column.
7. Why these come first gives the reasons for each capability in that ranked list; open items and findings sit beside it.
8. The full ranked table and the evidence list sit in collapsed sections at the end. An overridden row shows the decided band beside the computed one.

Priority tiles use the Baseline sequential ramp: Invest now `--bl-seq-600`, Plan `--bl-seq-500`, Monitor `--bl-seq-200`, Hold `--bl-seq-50`, Retire review a dashed outline and OPEN a solid outline. The maturity view runs from an outlined 0 through `--bl-seq-100`, `-200`, `-300`, `-500` and `-600`, skipping `-400`, where neither dark nor light text reaches 4.5:1. For a confirmed project profile, override the `--bl-*` tokens and keep their names.

The layout fits a 390-pixel phone screen without horizontal page scroll. The lifecycle strip and the table scroll inside their own containers.

## Excel tracker

`capability-assessment.xlsx` has these sheets:

| Sheet | Contents |
| --- | --- |
| Capabilities | One row per scored capability. Gap, impact weight, score and band are formulas over the current, target, impact and status cells, so editing a score in Excel recomputes the row. Header row frozen, filters on. |
| Lifecycle | Capabilities by stage with a marker in each stage column they serve. |
| Strategy trace | Goals with their measures, linked capabilities and the best band among them. |
| Rubric | The maturity scale, dimension questions, impact weights and band thresholds used for this build. |
| Evidence | The evidence list. |
| Open items | Open questions and every OPEN value. |

Edits made in the workbook do not flow back into the model. Bring agreed changes back through the model JSON (or `ingest` for the workshop sheet) and rebuild so the HTML and readout match.

## Markdown readout

`capability-readout.md` is the decision narrative for the sponsor: the scope and basis, the two top bands with their reasons, goal coverage findings, redundant capabilities under review, overrides, open items with owners, and validation questions for anything scored as a hypothesis. It does not repeat the full map; it links the HTML and workbook by file name.

## Computed model

`model.computed.json` carries the computed fields described in [the model schema](model-schema.md). When a hub is configured, store it with the engagement records. A later rescore is compared with this baseline.
