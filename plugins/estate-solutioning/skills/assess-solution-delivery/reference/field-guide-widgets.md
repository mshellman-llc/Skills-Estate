# Field guide widgets and disposition vocabulary

`assets/field-guide.body.html` is the worked reference. It carries four interactive
widgets, the disposition pills, and two callout styles, all vanilla CSS and JS with
no dependencies. Copy a block into a section and edit its data. The script at the
bottom drives all four by class and `data-` attribute, so edit the data arrays
rather than the wiring.

Every widget uses the caller-selected brand profile, or the documented neutral
profile when none is selected. `scripts/build_field_guide.py` applies the bundled
brand runtime's font, color and shape variables. Keep fonts and colors in the
selected profile. Numbers use `font-variant-numeric: tabular-nums` for
alignment; retain accessible labels and sufficient contrast with any profile.

## When an interaction earns its place

A widget earns its place when it lets the reader do something a table cannot:
resolve a value, trace a path, filter to a subset, or compare two states.
Decoration is not a reason. Where a static diagram is the right call, hand-author
the SVG and keep the diagram-as-code conventions: a shared marker and palette
helper, one dedup rule for shared `<defs>` marker IDs across a multi-diagram file,
and a viewBox-overflow check on every `<text>`.

## 1. Rate resolver (`.pr`)

Resolves a live value from the client's own rate table: a category toggle, a row,
a range, then the result and a comparison against the other toggle state. Built
for `A x B x C` models where trying values teaches the reader something. In the
reference build uses a newly invented review tier, review step and day range.

Edit the `rates` object and `order` array in the script:

```js
var rates = {"Sample intake":[12,18], "Technical review":[24,36]}; // synthetic [stateA, stateB]
var order = ["Sample intake","Technical review"];                 // display order
```

Toggle labels live in the two `.pr-tb[data-status]` buttons. The compare line names
the opposite state automatically. If the client's model is not a rate lookup, do
not force it into this widget.

For real work, use the caller's confirmed model and source its figures. The
synthetic example is a teaching tool, not a rate card or an authorized price.

## 2. Clickable flow (`.ifl-steps` + `.ifl-detail`)

Numbered step chips; clicking one fills a detail panel with the step's layer,
disposition pill, description, and source. Use it for any staged process. It
replaces a static flow diagram and its walk-through table together, so ship one
rather than both.

```js
{n:1, title:"...", layer:"Scheduler", disp:"config",
 what:"one or two sentences, plain voice", src:"where this claim comes from"}
```

`disp` is `native | config | custom | dep` and sets the pill colour.

## 3. Filterable ledger (`.ldf` + a table)

A disposition table with filter chips and a proportional build-load bar, so the
reader sees where the platform ends and the build begins, then filters to one
class. Two parts to keep in step:

- the filter block `.ldf` (chip counts and `.ldf-bar` segment widths as
  percentages summing to 100)
- the table, with `data-disp="native|config|custom|dep"` on every `<tr>`

The ledger is a projection of scope items. Every row is a `scopeItem` carrying
`buildDisposition`, so the ledger cannot drift from scope. The validator rejects an
included scope item with no `buildDisposition`.

## 4. Flat / structured toggle (`.ctw`)

One dataset in two representations, switched by a toggle: the messy current state
and the target. Built for greenfield and migration stories. Two `.ct-view[data-view]`
panels, `current` and `target`. Keep the same underlying items in both so the
transform stays honest.

## Disposition pills (`.disp`)

Four labelled categories with consistent meaning. Reuse the vocabulary across
every guide, and keep it aligned with `buildDisposition` on the scope item.

- `d-native`: the platform supports it out of the box
- `d-config`: declarative configuration; assess its actual risk
- `d-custom`: a build, such as code, an integration, or a custom object
- `d-dep`: a dependency with a confirmed owner

## Callouts (`.call`, `.call.warn`)

- `.call`: a point to land, or a recommendation
- `.call.warn`: a correction or a risk to raise

Use the selected profile's semantic colors and include a text label so color is
not the only signal. Label each callout with a short `.lbl` and keep it to one point.

## Class-name hygiene

The chip title class inside `.ifl-chip` is `.ct`; the catalog container is `.ctw`.
A bare `.ct` container rule collides with the first and makes flow chips inherit
card styling. When adding a widget, give its container a class that is not a prefix
collision with an existing one.
