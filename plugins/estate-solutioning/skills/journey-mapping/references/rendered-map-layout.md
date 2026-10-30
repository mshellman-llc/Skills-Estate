# Rendered map layout

A rendered journey map puts the journey map and the service blueprint on one board, so a reader can follow each phase from the actor’s experience to the staff and systems supporting it. Friction callouts sit below the board. The opportunity map follows as a board of cards that keep owners, dependencies, expected outcomes and measures. [The HTML starter](../assets/journey-map.html) implements this layout from one data object.

## Page order

The header names the actor and gives the scope sentence, for example "One pursuit, from a lead landing to a recorded win or loss." A one-line lead says where the journey dips. A legend follows with swatches for phase, pain point, and opportunity, plus the emotional curve and whether it is evidence or hypothesis.

The browser tab uses `MAP.title`. The starter uses body and label text of at least 16 pixels. The board comes next. It scrolls horizontally on narrow screens, and the row labels stay pinned on the left.

The evidence-basis note sits directly under the board. It says which layers come from the system or from participants and which are hypotheses, in the same words as the map metadata.

An evidence list follows the note. Row labels and feeling cells carry a small reference number; each number points to one entry giving the basis and source, or the reasoning for a hypothesis. Cells do not repeat "hypothesis", "reported" or source names, so the board stays readable.

The friction section closes the page. Critical friction includes the troughs in the emotional curve. Each supported trough in the emotional curve can have a card with the phase number, a one-line finding, and one or two sentences on the cause, including a number from the record where one exists (for example, "5 of 35 playbooks are published" or "outcomes sit at 0").

Operational friction outside a trough can also have a card; do not change an emotion score to fit a finding. The sample values are illustrative and are labeled as such.

## Opportunity map

`opportunityMap` is optional. When present, the page ends with the opportunity map drawn by the estate's roadmap components (`roadmap-artifacts`), in columns for quick wins, strategic bets, cross-team gaps and front-to-back disconnects. Only columns with an opportunity appear.

Each opportunity has `phase` (the phase number of the friction it addresses), `kind` (`quick win`, `strategic bet`, `cross-team gap` or `disconnect`), `title`, `outcome` and `measure`, plus `basis` (observed, reported or hypothesis) and `source`. `intervention`, `dependsOn`, `effort` and `owner` are optional; an owner of `"TBD"` shows an empty owner slot. The basis and source go into the evidence list once, and each card carries the reference number, the same way the board rows do. Effort is a label, never a price.

Keep the prioritized Markdown opportunity map in the narrative when the reader needs the full reasoning; the board shows the decision view.

## Board rows

| Row | Content | Styling |
|---|---|---|
| Phase | Two-digit phase number and a short phase name, one column per phase | Dark header band |
| Emotion | Optional curve across phases, scores 1 to 5 with the scale defined in the evidence-basis note | Solid line for evidence, dashed line for a hypothesis; the legend explains the dash once |
| Feelings | Optional qualitative description at each phase, even without scores | A reference number per description, pointing to its basis and source in the evidence list |
| Step and touchpoint | What happens and where, with the channel after a middle dot, e.g., "Handoff · chat" | Plain cell |
| Goal | What the actor wants at this phase, in the actor's terms | Plain cell |
| Thoughts | A sourced quote, or a hypothesized thought | Italic, muted; a hypothesis carries no attribution |
| Pain points | The specific friction | Neutral shaded cells |
| Opportunities | The intervention aimed at that friction, matched to the same column | Accent text; the legend uses the same accent |
| Visibility not captured | Optional system actions whose visibility to the actor is unknown | Separate row above the classified blueprint; these actions belong in neither front-stage nor back-stage |
| Front-stage | What the actor sees the system or staff do, e.g., an abstain message or a routed-away list | Plain cell |
| Line of visibility | Divider between Front-stage and Back-stage | Dark band |
| Back-stage | Work out of view, e.g., an assessor or a fit judge, or a table that is never written | Plain cell |
| Line of internal interaction | Divider between Back-stage and Supporting | Dark band |
| Supporting | Systems and records underneath, e.g., the catalog, the CRM, or a related role's view | Plain cell |

Use an empty string only when evidence confirms that nothing happens in that layer. Use null for missing evidence; the renderer displays "Not captured". In Opportunities, null means "None proposed". Supply `visibilityUnknown` as one text or null entry per phase for system actions whose visibility has not been established. Do not place those actions below the line of visibility. `Goal` and `Opportunities` may also set a row `basis`, which adds the row to the evidence list; a row marked `not captured` cannot contain known text. Missing evidence does not establish that support is absent. Thoughts and Pain points each carry their own basis: observed, reported, hypothesis, or not captured. Set emotion to null and emotionBasis to "not captured" when no defensible curve exists. This means scores are missing, not that reported feelings must be removed.

To retain qualitative feelings, supply `emotionLabels` with exactly one entry per phase. Use null for a phase with no captured feeling. Each other entry is an object with `text`, `basis` (observed, reported or hypothesis), and `source` (source reference or the reasoning for a hypothesis). For example, `{"text":"Anxious before boarding","basis":"reported","source":"Passenger interview, session 3"}`. Keep each description at the phase where that feeling occurred. Labels work with or without the curve; do not derive scores from them.

Wrong-length arrays, out-of-range scores and incomplete row structures stop rendering with a visible error; correct the source data instead of truncating or clamping it.

## Related roles

When two roles share a journey, such as a seller who hands off to a technical specialist, build a map for each role. Use the same phase numbers where their paths meet and name the other map in the supporting row of the handoff phase.

## Checks before sharing

Every phase column has a value or an intentional blank in each row. When scores exist, the emotional curve has one point per phase. Captured feelings appear in their phase columns even when scores do not exist. Friction cards follow the supported findings; do not invent a card to match a curve. The opportunity in each column addresses the pain point in the same column. The evidence-basis note matches the ledger, and every hypothesis layer appears in the evidence list. Render at phone width and confirm the board scrolls without the page scrolling sideways.

## Keep one editable map source

Author the map data as JSON, then embed that object in the HTML starter. Rebuild the HTML from the JSON after an edit. Do not maintain a JavaScript object and convert it back to JSON with regular expressions; that can change quotes or leave the two versions inconsistent.

Build the page with the packaged script. It replaces the starter's `MAP` object with the JSON, escapes HTML-opening characters so a quoted source cannot close the script element, and inlines the roadmap components so the page stays one file with no network requests. Run it from the skill directory; existing outputs are refused.

```bash
python3 scripts/build_journey_map.py map-data.json --output attempt-001/journey-map.html
```

The starter opened on its own renders the opportunity map as a numbered list, because the components are added only by the build.

Open the rebuilt HTML and check its visible errors, qualitative feelings, blueprint layers and opportunity text against the JSON and narrative. A source edit is not proof that the rendered output changed.
