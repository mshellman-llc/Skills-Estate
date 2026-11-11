---
name: scope-reference
description: 'Build a static, print-ready, Aleysian-branded scope reference from live scoping-app quotes: option cards plus a side-by-side line-item matrix with hours and in, available, optional, or out states, every item, hour, and price validated 1:1 before rendering. Use for a scope reference, option summary, scope comparison, option matrix, what is included, tier comparison, or a flat client leave-behind that shows the full matrix at once. Do NOT use for a clickable or interactive proposal or a version switcher where the prospect moves through versions one at a time (that is interactive-proposal), the DDOC decision deck (ddoc), the SOW contract (sow), or creating and editing the quote itself (scoping-agent).'
---

# Aleysian scope reference

> **Before writing:** read [`build-card.md`](../_shared/build-card.md) and the
> [`sow-proposal.md`](../prose-pass/references/registers/sow-proposal.md)
> register. Inputs, not a final pass. Brand and prose are release gates, applied
> during the build, not after.

Produce a single self-contained HTML file a client can read, print, or be walked
through on a call. It answers one question cleanly: **what is in scope, and what
does it cost.** When the pursuit has more than one option, they sit side by side
as cards and a single matrix shows every line item, its hours, and its state per
option. When the pursuit is a single quote with no tiers, the same artifact
renders in single-option mode: one summary panel instead of a card row, and a
two-state matrix (in / optional) instead of a per-option comparison. Same brand,
same sourcing rules, same gates.

Pick the mode from the input, not from a guess:

| Signal | Mode |
|---|---|
| Two or more Q-numbers, or a client with tiered options | **Comparison** (cards + per-option matrix) |
| One Q-number, or a pursuit with a single agreed scope | **Single-option** (summary panel + in/optional matrix) |

State the mode in your first line back to the user, since it sets what the page
will look like.

This artifact is static and complete on the page. It is not the click-through
interactive proposal (that is `interactive-proposal`), not the decision
deck (`ddoc`), and not the contract (`sow`). If the user wants
a page that switches between one option at a time, route to interactive-proposal
instead.

## The non-negotiables, in order

1. **Live quote is the only source of truth for scope, hours, and state.** Pull
   every option's scope hierarchy from the scoping app immediately before
   building. Never carry figures forward from a prior doc, an upload, a memory
   summary, or a cached pull. Snapshots change between sessions.
2. **Validate 1:1 before rendering.** Every item name, hour value, and per-option
   state in the file must reconcile exactly against the live pull. Run the
   validation step (below) and report the result. Do not render an unreconciled
   table.
3. **Price by timeline snapshot, not by summing items.** Each option's headline
   price is its active timeline snapshot revenue. Per-item dollars are *not*
   authoritative — they are back-allocated from the timeline and drift between
   snapshots, so the same item shows different dollars in different quotes. The
   table therefore carries **hours** as its per-item anchor and shows no per-item
   price. One line under the table states that option price is set by the
   staffing timeline, not by adding lines.
4. **Absent facts are gaps, never filled.** Flag gaps to the user in chat. Never
   write a plausible number, description, or state into the artifact to cover a
   hole. (Descriptions are the one authored element — see "Descriptions" below —
   and even those are grounded, never invented from nothing.)
5. **Brand and prose gates are applied during the build.** State the design
   system before building. Run the prose gate before delivering. No AI
   tells, no internal language, no competitor language, no editorializing.

## Workflow

### 1. Resolve the option(s) and their quote(s)

Identify each option and its Q-number. If the user names a client but not the
quotes, find them (`scoping_get_quote`, or search by account).

- **Comparison mode:** confirm the option order — options usually build on one
  another (each is the prior plus a layer); present them in that ascending order.
- **Single-option mode:** there is one quote and no tier ordering. The page is a
  scope summary for that one quote, not a comparison.

State back to the user: the mode, the option(s), the Q-number(s), and (in
comparison mode) the build order. If any quote can't be resolved, stop and ask
rather than guessing.

### 2. Pull live scope for every option

For each quote, pull the scope hierarchy twice, in parallel where possible:

- `scoping_get_scope_hierarchy` with `activeOnly: false`, `includeHours: true`,
  `includeFinancials: false` — the full item list.
- `scoping_get_scope_hierarchy` with `activeOnly: true` — to distinguish
  **present-but-deselected** items (in the quote, inactive) from genuinely
  **absent** items.

The state of each item per option is then:

| State | Meaning | How to detect |
|---|---|---|
| **in** | actively selected in this quote | in active-only pull, not flagged optional |
| **available** | present in the quote, deselected | in full pull, drops out of active-only |
| **optional** | a line the quote marks optional / togg(`[Optional]`) | phase/flag marked optional |
| **out** | not present in this quote at all | absent from the full pull |

Getting `available` vs `out` right matters: an available item is a one-click
add, not a re-scope, and the artifact says so. Never collapse the two.

In **single-option mode** there is no `out` column and usually no `available`
(nothing to compare against). The matrix reduces to two states — **in** and
**optional** — for the one quote. Still run both pulls: the active-only pull is
what confirms which items are actually selected versus present-but-optional.

### 3. Pull the price and weeks per option

Two-step timeline read per quote:

1. `scoping_manage_timeline` `operation: list` — confirm the **active** snapshot
   ID (do not assume the newest is active).
2. `scoping_manage_timeline` `operation: get` with that `snapshotId` — read
   `totalRevenue` and `weekCount`.

If the client sees more than one staffing variant (e.g. onshore vs nearshore),
each variant is its **own** snapshot with its own hours, weeks, and revenue.
They are not one plan at two rates — read both, and do not assume hours or weeks
match across them. If a variant does not exist as its own snapshot, say so;
do not derive it silently.

Round headline prices to the nearest \$1,000 for the client surface unless the
user says otherwise. Keep the exact figures in your working notes for tie-out.

### 4. Validate 1:1

Before building, reconcile the assembled item set against the live pulls:
name-match every item, compare hours, compare each per-option state. Use the
bundled `scripts/scope_reference_validate.py` (`validate` and `present_counts`)
and the method in [`validation.md`](validation.md). Report
the result to the user in one line ("1:1 match" or the specific discrepancies).
Only build on a clean reconcile.

### 5. Build the HTML

Read [`build-guide.md`](build-guide.md) for the full
structure, the design tokens, the asset-embedding pattern, and the state-icon
system. In short: Aleysian brand (Deep Navy `#080F28`, Teal `#1A6B6B`, Sand
`#F7F5F0`, Plus Jakarta Sans), self-contained single file with base64-embedded
fonts and logo, option cards on top, one grouped line-item matrix below, a
four-state legend, and a short explanatory footer. If two staffing variants
exist, add the neutral toggle described in the build guide.

### 6. Descriptions

Each line item carries a one-sentence plain-language description under its name.
The scoping app's stored description field is **not exposed** by the hierarchy
tools, so these are authored, grounded in the item's effort-basis note or the
user's source material — never invented to sound good. Vary the sentence
openings (do not template every line the same way). If the user needs
descriptions verbatim-matched to the SOW, ask them to export the description
field and swap yours out.

### 7. Gate before delivering

- **Prose gate.** Run the `prose-pass` skill, or resolve its installed
  directory from the host's skills list and run `scripts/rewrite_scan.py` over the rendered text.
  Zero em dashes, zero banned vocabulary, zero bold-phrase tells. Then do the
  manual structural pass the scanner cannot do:
  no rule-of-three clusters, no significance inflation ("the core / the spine /
  the analytical heart" stacking), no templated parallel openers, no restating
  card-role lines.
- **Competitor / internal-language scrub.** Remove any competitor names or
  "vs competitor" framing, any internal register ("Jim's call", "needs sign-off",
  "required scope"), and any editorial framing. A record name in the quote that
  still contains such language (pending rename) does not license it in the
  artifact — reframe around what the client gets.
- **Brand gate.** Palette, font, logo placement, footer, radii per the build
  guide.
- **Tie-out.** Each headline price on the surface equals the snapshot revenue you
  read. Item counts per option match the live pull.

Deliver the file with `present_files` and a short summary. Flag any gaps or open
decisions in chat only — never in the artifact.

## Decisions to surface, not assume

- Which staffing variant(s) to show, and which is the default view.
- Whether an optional line (e.g. a historical-data migration marked optional on
  one quote but required on others) should display as optional or be forced to a
  single state — this is a real quote-state inconsistency worth raising.
- Whether descriptions need to be verbatim-matched to the SOW.
- Rounding convention if not the \$1,000 default.

## What good looks like

The reference doc is the kind of leave-behind a client can read alone and a
seller can present live. Nothing on it is guessed. Every hour and state ties to
a live quote. The price sits with each option, the hours anchor each line, and
no one can add up the lines and land somewhere the total does not.

## Release gate (required)

Before you deliver, run the gate. This is a required step, not a suggestion, and
not something a reviewer does later. Full spec in
[`release-gate.md`](../_shared/release-gate.md).

1. Run prose-pass on the prose. It rewrites AI patterns and gates the result. For
   a final artifact it emits a receipt the quality gate requires.
2. Run brand-renderer on the branded artifact: palette, borders, radii, logo,
   footer.
3. Run quality-gate before you call it final.

Do not present the artifact as finished until every check that applies has passed.
