# Rendered map layout

A rendered journey map puts the journey map and the service blueprint on one board, so a reader can follow a phase from what the actor feels down to the system that causes it. The opportunity map sits below the board as the critical friction callouts. [The HTML starter](../assets/journey-map.html) implements this layout from one data object.

## Page order

The header names the actor and gives the scope sentence, for example "One pursuit, from a lead landing to a recorded win or loss." A one-line lead says where the journey dips. A legend follows with swatches for phase, pain point, and opportunity, plus the emotional curve and whether it is evidence or hypothesis.

The board comes next. It scrolls horizontally on narrow screens, and the row labels stay pinned on the left.

The evidence-basis note sits directly under the board. It says which layers come from the system or from participants and which are hypotheses, in the same words as the map metadata.

The critical friction section closes the page. Each trough in the emotional curve gets one card with the phase number, a one-line finding, and one or two sentences on the cause, including a number from the record where one exists (for example, "5 of 35 playbooks are published" or "outcomes sit at 0").

## Board rows

| Row | Content | Styling |
|---|---|---|
| Phase | Two-digit phase number and a short phase name, one column per phase | Dark header band |
| Emotion | One curve across all phases, intensity 1 to 5 | Solid line for evidence, dashed line and a "hypothesis" label for a hypothesis |
| Step and touchpoint | What happens and where, with the channel after a middle dot, e.g., "Handoff · chat" | Plain cell |
| Goal | What the actor wants at this phase, in the actor's terms | Plain cell |
| Thoughts | A sourced quote, or a hypothesized thought | Italic, muted; a hypothesis carries no attribution |
| Pain points | The specific friction | Warm tint |
| Opportunities | The intervention aimed at that friction, matched to the same column | Accent tint |
| Line of visibility | Full-width divider labeled "Line of visibility" | Dark band |
| Front-stage | What the actor sees the system or staff do, e.g., an abstain message or a routed-away list | Cool tint |
| Back-stage | Work out of view, e.g., an assessor or a fit judge, or a table that is never written | Cool tint |
| Supporting | Systems and records underneath, e.g., the catalog, the CRM, or a related role's view | Cool tint |

Leave a blueprint cell empty when nothing happens in that layer at that phase. An empty back-stage cell under a painful phase is a finding: it shows that nothing supports that step.

## Related roles

When two roles share a journey, such as a seller who hands off to a technical specialist, build a map for each role. Use the same phase numbers where their paths meet and name the other map in the supporting row of the handoff phase.

## Checks before sharing

Every phase column has a value or an intentional blank in each row. The emotional curve has one point per phase, and its lowest points match the critical friction cards. The opportunity in each column addresses the pain point in the same column. The evidence-basis note matches the ledger, and hypothesis styling appears on every hypothesis layer. Render at phone width and confirm the board scrolls without the page scrolling sideways.
