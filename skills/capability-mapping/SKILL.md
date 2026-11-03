---
name: capability-mapping
description: "Build a business capability map and map-and-gap assessment from interviews, workshop notes, strategy documents and reference catalogs. Produces a Level 1 to 3 capability hierarchy placed on customer lifecycle stages and linked to strategy goals such as V2MOM methods or OKRs, scored for current and target maturity and business impact, and ranked into a prioritized gap list. One JSON model renders an HTML dashboard, an Excel tracker with live formulas and a decision readout. Also prepares the customer lifecycle workshop kit and capture workbook. Triggers on business capability, capability map, capability model, capability heatmap, map and gap, capability gap analysis, capability maturity assessment, business architecture, capability-based planning, lifecycle analysis workshop, and on consolidating two companies' capabilities after an acquisition. Step-by-step process work belongs to process; one actor's experience belongs to journey-mapping; the solution design belongs to solution-brief or system-design."
---

# Capability mapping

Build one capability map for a business, assess it, and rank the gaps worth closing. The sponsor decides from the ranked gap list; the map, the lifecycle view and the strategy coverage show how each gap was scored.

Before modeling, read the complete [capability mapping method](references/method.md). It contains the scoping rules, the capability-versus-process test, decomposition levels, derivation approaches, lifecycle and strategy alignment, the maturity scale with its five dimensions, impact rating, the gap and priority formula, and the release checks. Read it in bounded parts if the tool would clip its output; a partial read cannot establish coverage. Resolve the skill directory first and run the method's relative commands from that directory.

Confirm the business, the state being mapped, the decision and the audience. Keep one occurrence of each capability and record who performs it. Name capabilities by what the business can do, never by system or team. Every score carries an evidence basis; an unknown value stays `null` and shows as OPEN.

Keep the JSON model as the editable source, following [the model schema](references/model-schema.md), and build every output from it:

```sh
python3 scripts/build_capability_map.py build model.json --output-dir out/
```

For a lifecycle workshop, use [the workshop kit](references/workshop-kit.md) and its `workshop` and `ingest` commands. The output layout is in [rendered outputs](references/rendered-outputs.md). A Markdown-only request still receives the ranked gaps, goal coverage, findings and open items.

Review the outputs against the sources: compare the readout figures with the computed model, open the HTML and the workbook, and check that stakeholder overrides keep their reasons. Hand top gaps to their next owner as the method describes; this skill does not price work or design the solution. Run the method's applicable release checks and report a missing check instead of claiming a pass.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
