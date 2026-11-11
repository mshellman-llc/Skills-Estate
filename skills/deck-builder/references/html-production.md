# HTML production

Use this route for a browser deck and PDF export. It preserves selectable text and embeds the selected profile's assets. Complete the pre-build stages in SKILL.md before generating the final file. Those stages establish the argument and slide structure, then the actual copy.

## Inputs

Save JSON with `title`, `context`, `sources` and `slides`. `context` identifies the engagement or marks a synthetic example. `sources` maps a stable key to its evidence description. Each slide has a `title`, an optional `lead` that adds information beyond the title, a nonempty list of source keys and `blocks`. Retain `question`, `reason` and `transition` in the input as the storyboard record. An optional `implication` gives a supported condition or consequence beneath the visual. These fields support review; their presence does not prove narrative quality.

Choose blocks for the relationship on the slide:

| Type | Required values | Use |
|---|---|---|
| `text` | `text` | An explanation or decision |
| `columns` | Two or three `items`, each with `title` and `text` | Distinct options or responsibilities |
| `flow` | Two to five `items` with the same fields | Ordered steps; numbering carries sequence |
| `table` | `headers` and equally sized `rows` | Scope, ownership, evidence or acceptance comparisons |
| `sequence` | `description`, two to four `actors`, `events` | Directed interaction and lost responses |
| `diagram` | `description`, `nodes`, labeled `edges`; optional `zones` | Branches, boundaries, dependencies and operating states |
| `specimen` | `description`, `title`, `fields` | A proposed or sourced record with field annotations |
| `bars` | `description`, `unit`, `maximum`, up to six `items` | Nonnegative measured values on one zero-based scale |

Keep full supporting detail in a subsequent slide when the first slide cannot hold it. A renderer accepting the data does not prove that the copy fits. Split dense content before reducing the profile's minimum type size.

A visual needs its accessible `description`. Use `caption` when a printed explanation adds something; set it to an empty string to omit a redundant caption.

The worked example at `examples/reconciliation-narrative.json` is synthetic. It traces a lost posting response through receipt recovery, a held match, an operator record, the service boundary and acceptance decisions. Its claims cannot supply evidence for a client deck. The older `examples/reconciliation.json` remains a regression fixture for text, columns, numbered flows and tables; it is not the explanatory-quality benchmark.

## Visual input contract

All visible strings become escaped text. Each visual requires a descriptive caption. SVG labels remain selectable. A complete relationship list accompanies the diagram on narrow screens; the diagram itself scrolls horizontally without changing the meaning of its connections.

- Sequence actors use `id` and `label`. Events use `from`, `to` and `label`; `lost: true` marks a failed return path. Split more than six events into successive views. A lost response does not establish that a write failed.
- Diagram nodes use `id`, `label`, `x`, `y`, `w`, `h` and an optional `kind`: `process`, `decision`, `external`, `note` or `emphasis`. Coordinates use a 1120-unit-wide canvas; `height` defaults to 400 and cannot exceed 490. Decision labels need enough room inside the diamond.
- Edges name existing `from` and `to` node IDs. Optional `from_side` and `to_side` select `left`, `right`, `top` or `bottom`; defaults are right to left. Use `via: [[x,y], ...]` for bends. Position the required label with `label_x`, `label_y` and `label_width` when the default midpoint would collide. Optional `style: "dashed"` changes the line, not its meaning; explain the distinction in the caption.
- Zones use `x`, `y`, `w`, `h` and `label`. Their boundaries must correspond to a stated responsibility or scope. The renderer does not infer which nodes belong in a zone.
- Specimen fields use `label`, `value` and `why`. Label a proposed record as a specimen; do not imply that it is a screenshot of an implemented product.
- Bar items use `label` and a finite numeric `value`. `maximum` is the shared scale limit and must include every value. The renderer rejects negative values; choose another renderer when negatives are meaningful. Preserve the underlying data and units. Never create measurements for visual variety.

Bounds and endpoint checks catch malformed input. They cannot prevent every visual collision or assess whether an edge means the right thing. Inspect the resulting SVG at delivery size. Use another renderer for unsupported forms rather than replacing the explanation with prose boxes.

## Build and inspect

```bash
python3 scripts/build_html.py INPUT.json OUTPUT.html
```

Add `--profile /project/brand.md` to select a project identity.

The command preserves existing outputs by refusing to overwrite them. It also rejects invalid source references and malformed blocks. Missing declared brand assets stop the build. Input strings become escaped text. The selected brand profile supplies all colors and typography; the renderer has no company palette.

Open the output in a browser. Read every slide at presentation size and on a narrow screen. Check that tables retain their column associations. Trace each flow in order and confirm which claims the footnotes support. Save a PDF through the browser's print function with CSS page size and background graphics enabled. The print layout uses one landscape page per slide.

For repeatable checks, the test environment needs Node.js with Playwright and a Chromium browser. Run `scripts/check_html.mjs` with the HTML file URL and a new output directory. `PW_MODULE` can identify the installed Playwright module; `PW_CHROMIUM` can select an available Chromium executable. The checker blocks remote requests. It measures clipping and edge-label collisions with node bounds. It also captures every slide, checks the narrow layout and exports a PDF. Keep failed attempts. Inspect the captured views and every exported page before recording visual acceptance. Independently trace each request and receipt in its stated direction. Follow the branch conditions and verify which interfaces cross the scope boundary. Geometry alone cannot establish those meanings.

Run the writing and brand checks using the runtime returned by brand-renderer preflight. Reconcile each slide to its source record. Keep the deck and input JSON with the stage files. Preserve source hashes and checker outputs alongside the completed polish record. A browser measurement cannot approve the argument or establish the truth of a claim.
