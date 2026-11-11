# Build guide: the scope reference HTML

A single self-contained HTML file. Fonts and logo base64-embedded, all CSS
inline, no external requests, no build step. Opens from an email attachment and
prints clean.

## Design system (state it before building)

| Token | Value | Use |
|---|---|---|
| Deep Navy | `#080F28` | header, footer, table header, category rows |
| Teal | `#1A6B6B` | accents, eyebrows, highlighted card, active toggle, "in" icon |
| Teal light | `#4AA8A8` | header eyebrow/meta on navy |
| Sand | `#F7F5F0` | card headers, total-row backgrounds |
| Amber | `#D97706` / bg `#FEF3C7` | "available" state icon |
| Indigo | `#6366F1` / bg `#EEF2FF` | "optional" state icon |
| Grey | `#D1D5DB` on `#F3F4F6` | "out" state icon |
| Text | `#1A1F2E` primary, `#3D4460` mid, `#6B7280` muted | body copy |
| Font | Plus Jakarta Sans, weights 400/500/600/700 | everything |

Radii ~10px on cards/tables, 5px on state-icon chips. Body ~13.5px.

## Assets

Use the logo and font files vendored under `_shared/aleysian-brand/` in the
skill bundle. Resolve them relative to the skill directory. Encode binary
assets with Python because shell heredocs can corrupt base64 content.

Declare each weight with an `@font-face` block using
`src:url('data:font/ttf;base64,{...}') format('truetype')`.

## Single-option mode layout

When there is one quote and no tiers, keep the same brand, header, footer, gates,
and line-item matrix, but change three things:

1. **Replace the card row with one summary panel.** A single wide panel (sand or
   teal header) carrying the option name, `Q-number · N items · N weeks`, the
   headline price, and a two-to-three sentence plain summary of what the client
   gets. No comparison, no highlighted-card treatment.
2. **Collapse the matrix to two states.** Columns become **Scope item · Hours ·
   Status**, where Status is `in` or `optional` only. Drop the per-option
   columns and the `available` / `out` icons — there is nothing to compare
   against, so those states carry no meaning here. The legend shrinks to the two
   states in play.
3. **Drop the staffing toggle unless the single quote genuinely has two variant
   snapshots.** If it does (onshore/nearshore of the same single scope), keep the
   toggle exactly as in comparison mode; it flips the one price and week span. If
   it does not, omit the toggle entirely.

Everything else — the hours-anchor rule, the "price set by timeline not by
summing lines" note, the descriptions, the callouts, the prose and brand gates —
is identical. The single-option page is the same artifact with the comparison
scaffolding removed, not a different document.

## Comparison-mode layout

Page structure, top to bottom, when two or more options are compared:

1. **Header** (navy). White logo, eyebrow ("Asset implementation · scope
   reference" or the engagement's equivalent), title ("What each option
   delivers" / "Three options for X"), sub (client · date). Right side: "Prepared
   by Aleysian" — not named individuals, this is client-facing.
2. **Context strip** (teal). 2–3 short true facts that frame the read, dot-
   separated. Good ones: "Each option builds on the one before it";
   "[Product] base enablement is in all three". Keep them factual, not sales-y.
   Do **not** claim hours/weeks are identical across variants unless the live
   snapshots actually agree — they often do not.
3. **Toggle bar** (dark, only if >1 staffing variant). Two neutral buttons
   (e.g. "Onshore BA" / "Nearshore BA"). No cost-framing labels ("cheaper",
   "proposed savings"). Default to whichever the user specifies; otherwise the
   primary/onshore. JS flips price + weeks + note per option via `data-*`
   attributes. See toggle snippet below.
4. **Option cards** (one per option, grid). Each card:
   - header (sand; teal if it is the highlighted/recommended one): option name,
     `Q-number · N items · N weeks`, headline price with a small variant note.
   - body: a short capability label, the key differentiating items as icon+name+
     one-liner, a divider, and a one-sentence "In [product] terms:" summary.
   - Weeks and price carry `data-onshore` / `data-nearshore` for the toggle.
5. **Line-item matrix** (the core). One table, grouped by category with navy
   category rows. Columns: **Scope item** (name + one-line description) ·
   **Hours** · one column per option. Cells use the state icons. No per-item
   price column. Under the heading, one line: *"Hours per item, constant across
   options. The price of each option is shown above; it is set by the staffing
   timeline, not by summing line items."*
6. **Legend.** Four states: in / available / optional / out, each with its icon
   and a short gloss (available = "in the quote, deselected, can be switched on").
7. **Callouts** (2–4, two-column grid). Neutral explainers only: how the product
   is already licensed, how location/data works, what "available" means, why a
   heavy item carries its hours. No budget/negotiation/Phase-2-strategy framing
   on a client surface.
8. **Footer** (navy). "Aleysian · [client] · [date]" left, "Confidential" right.

## State icons

```
in        teal check on pale-teal chip
available amber filled dot on pale-amber chip
optional  indigo minus/dash on pale-indigo chip
out       grey cross on grey chip
```

For an `out` item, dim the name and show "Not included" (or the phase, e.g.
"Phase 2") rather than a full description.

## Toggle snippet

Each toggleable value gets `id` + `data-onshore` + `data-nearshore`. Prices,
week spans, and the variant note all participate.

```html
<div class="tc-pr" id="price-optA"
     data-onshore="$94,000" data-nearshore="$72,000">$94,000</div>
...
<span id="wk-optC" data-onshore="13 weeks" data-nearshore="12 weeks">13 weeks</span>
```

```html
<script>
function setVariant(v){
  ['price-optA','price-optB','price-optC',
   'note-optA','note-optB','note-optC','wk-optC'].forEach(function(id){
    var el=document.getElementById(id);
    if(el) el.textContent=el.getAttribute('data-'+v);
  });
  document.getElementById('btn-onshore').classList.toggle('active', v==='onshore');
  document.getElementById('btn-nearshore').classList.toggle('active', v==='nearshore');
}
</script>
```

No `localStorage`/`sessionStorage` — in-memory only.

## Item counts on cards

Card label count = active + optional (the lines that are "in the quote as
selected or a selectable optional"), matching how the scoping app presents the
option. Show `available` items inside the card but they are surfaced separately
("1 active, 2 available"), not folded into the headline item count. Confirm the
count ties to the live pull during validation.

## Writing the file

Build the whole document as one Python string (`.format` conflicts with CSS
braces — use `%`-style or plain concatenation / f-strings with doubled `{{ }}`
in the CSS, whichever you keep consistent). Write to
`/mnt/user-data/outputs/<client>-scope-reference.html`, run the prose gate over
the extracted text, then `present_files`.

## Gate extraction

To scan only the visible prose (not CSS/JS/base64), strip `<style>`/`<script>`
blocks and tags before running the prose scanner:

```python
import re
h = re.sub(r'<style[^>]*>.*?</style>','',html,flags=re.DOTALL)
h = re.sub(r'<script[^>]*>.*?</script>','',h,flags=re.DOTALL)
text = re.sub(r'<[^>]+>',' ',h)
text = (text.replace('&middot;','·').replace('&amp;','&')
            .replace('&nbsp;',' ').replace('&mdash;','—'))
text = re.sub(r'\s+',' ',text).strip()
```

Watch for em dashes hiding in button labels and headings, not just body copy —
the scanner reads the extracted text, so a `—` anywhere in visible content is a
hit.
