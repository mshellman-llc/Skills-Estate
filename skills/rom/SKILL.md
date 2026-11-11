---
name: rom
description: 'Build and gate the Estate ROM: a defensible cost and effort range around a scoping-app quote, plus the basis of estimate the client validates before deep scoping. Buyer-facing or deal-desk-facing. Use when asked for a ROM, rough order of magnitude, early pricing range, investment range, or ballpark for the quote, when a Q-number is paired with a range, sizing, or early-pricing request, or when a playbook tier needs its ROM artifact. Do NOT use for scoping or quote creation (that is scoping-agent), the SOW (sow), the firm proposal (interactive-proposal), or a standalone ballpark-LOE request untied to a quote or playbook (say so and stop).'
---

<!-- ESTATE-WRITING:BEGIN -->
Before writing, read the [writing standard](references/estate/writing.md). Apply it to every authored sentence. Review instructions and internal records too. Audience labels and file formats do not exempt prose from review.
<!-- ESTATE-WRITING:END -->


# Estate ROM

> **Before writing: [`build-card.md`](../_shared/build-card.md) plus the prose-pass register
> for briefs. Inputs, not a final pass.**

The ROM answers one question: what will this roughly cost and take, and what is that estimate
standing on? It is a range and a basis, never a quote. It gives the buyer a decision-grade
investment frame before deep scoping, and it surfaces the dimensions driving the estimate so
both sides know what to confirm. The moment a ROM implies precision the underlying data does
not support, it becomes a liability at the table. An honest wide range beats a false-precise
tight one.

Two audiences, one substrate. Buyer-facing: the range, the basis of estimate, what moves the
number. Deal-desk-facing: the same plus the reconciliation print and the confidence
composition. Pin the audience before building; it sets what renders, not what gets verified.

## The money rule is absolute

The scoping-app quote owns every number. Hours, rates, fees, phase allocations, and timelines
come from the quote (Q-number) through the scoping MCP, or from an explicit user-supplied
source named on the page. This skill renders a range around the quote total with a stated
basis. It never authors hours, rates, or fees. If a figure is missing from the quote, that is
a named gap routed to the SSL, not a number to invent. Trust the quote, not memory.

## Orient: pin the source before anything else

1. **Resolve the Q-number.** Call `scoping_get_sow_data` first; it returns the project
   context, scope items by capability, and the timeline with phases and resources in one
   call. Given a Q-number rather than a record Id, resolve it with a SOQL query on
   `Quote__c.Name`. Fill gaps with `scoping_get_quote` (resource grid and rates) only if
   needed.
2. **Detect the pricing model from the quote.** Fixed fee or time and materials. Never assume
   it, and never render both models' cards.
3. **Read the phases from the source.** The phase canon is whatever the quote timeline or the
   playbook definition states, in its order, with its names. Phases are read, never assumed.
   A ROM that renders a phase sequence the quote does not carry is fabrication.
4. **Pin the audience** (buyer or deal desk) and whether this is a draft or a client-ready
   range. Say plainly which depth you are building.

If there is no quote and no playbook definition, stop. A ROM without a source is a ballpark,
and ballparks are out of scope by name.

## Evidence first

Run **evidence-core** before drafting. The registry entry for `rom` requires these
load-bearing domains: scope basis, workstream effort, role assumptions, rates or cost basis,
confidence, range reopeners, commercial posture. If any is Insufficient, produce the
**estimate readiness gap memo** and stop. A full ROM after an Insufficient gate is a hard
fail. Generated artifacts and worked examples are never evidence.

Every figure the ROM shows is a ledger entry: figure, source, confidence, as-of. Confidence
uses the evidence-core register, nothing else:

- **Confirmed**: stated in the quote and cross-checked by computation, traceable to a scope
  input.
- **Inferred**: derived from a comparable engagement or current-knowledge scoping, with its
  derivation stated. (Older ROM drafts called this "Estimated"; that term is retired.)
- **Unknown**: depends on a footprint dimension the client has not confirmed. These are
  flagged assumptions. They live in the basis-of-estimate table, each tagged with the
  source-named phase in which it gets confirmed, and each appears in the assumptions register
  with an owner and the gate it blocks.

Map confidence to presentation: Confirmed renders as fact, Inferred renders with its
derivation, Unknown renders as a flagged assumption, never as a settled figure. Conflicts
between sources render as both values with a recommendation, never a silent pick.

## The sections

Derive the set from the ledger, not from an example. Read
`references/basis-of-estimate.md` before writing the BOE table and
`references/range-discipline.md` before stating the range.

| Section | What it answers | The bar |
|---|---|---|
| Header | What engagement, which tier or option, what pricing model, which Q-number | A reader knows in five seconds what governs the page |
| Metric strip | The range, hours, duration, and the model-specific card | Every figure traces to a quote field; fixed-price and T&M cards never coexist |
| Phase distribution | Hours across the source-stated phases | Phases come from the quote timeline; a heavy phase has a named reason |
| Basis of estimate | The footprint dimensions the estimate rests on | Every row is countable and specific to this client; Unknowns are flagged with their confirming phase |
| What moves the number | The range reopeners: scope conditions that are Change Orders regardless of size | Read from this deal's scope, never a generic list |
| Reconciliation (deal-desk view) | The printed tie-out | Present verbatim from the gate output |
| Footer | Confidentiality and status | Clear whether this is an internal draft or a client-ready range |

## The reasoning tests

1. **The math holds.** Hours times blended rate reconciles to the fee. Surface any
   discrepancy before rendering; never bury a rounding gap inside a polished number.
2. **The three-way tie holds.** Phase hour totals equal role hour totals equal work-package
   hour totals equal the quote grand total, or the variance is flagged with per-line deltas.
   This reconciliation is the artifact's spine.
3. **Phase distribution tells a story.** If one phase carries 40 percent of hours, that phase
   is doing something specific. Name it, from the source.
4. **BOE dimensions are real and specific.** "Custom objects" is not a BOE dimension.
   "Custom objects in CPQ requiring migration of pricing rules" is. The specificity bar is in
   `references/basis-of-estimate.md`.
5. **The model-specific card is correct.** Fixed fee: the fixed price and milestone basis.
   T&M: the envelope and upfront. The model determines which appears; never both.
6. **Range reopeners are this deal's reopeners.** "Additional integrations beyond the scoped
   four" is real. "Scope changes" is not.
7. **The range is honest about its precision.** A ROM standing on Unknown dimensions is wider
   than one standing on Confirmed ones, and the BOE table makes that visible.

## Verify by computation, then print it

Never assert a total you did not recompute. Build the figures block (schema in
`references/reconciliation-format.md`), then run the gate:

```bash
python3 scripts/rom_gate.py figures.json
```

The gate recomputes the three-way tie, checks hours times rate against the fee, checks that
the range bounds bracket the quote total, and checks the model card matches the pricing
model. It prints the full reconciliation and exits nonzero on any failure. The printed
reconciliation goes on the deal-desk view verbatim; for the buyer view it stays in the build
notes. Report the gate's counts, never an adjective. "Clean" is not a finding; "PASS, 0
failures" is.

**Discrepancy handling.** If a source figure fails to reconcile, render the internally
consistent value so the artifact ties out, and flag the discrepancy on the page with the
source values and per-line deltas, framed as a decision for the SSL. Never silently smooth,
and never silently override the quote. Cascade: if any figure changes, regenerate from the
figures block so numbers cannot drift between the model and the markup.

## Rendering and voice

Hand rendering to **brand-renderer**: it owns the palette, type, logo, layout
tokens, and the parity, visual, and brand release gates. Do not inline hex values here or in
the artifact build notes. Brand applies during the build, not after.

Run the **prose-pass** checker on every prose surface of the artifact and on this skill's own
output. No em dashes anywhere, sentence-case headings, no hedging, all figures as digits.
Report the scanner's counts.

Fallback: if a governor is not installed on the current surface, state the check it would
have run, perform the best manual substitute, and say that is what you did. Never silently
skip.

## Boundaries

- Does not scope and does not create or edit quotes. That is **scoping-agent**.
- Does not build the SOW. That is **sow**.
- Does not build the firm proposal. That is **interactive-proposal**.
- Does not price and does not set the range's midpoint. The quote owns the number; the SSL
  and deal desk own the decision. This skill informs, renders, and reconciles.
- Does not answer standalone ballpark-LOE requests untied to a quote or playbook. Say so.

## State discipline

Q-numbers and quote totals are not durable anchors; sandbox refreshes destroy them. Stamp the
artifact with its Q-number, quote total, timeline snapshot, and as-of date. Where a playbook
is involved, live-read its 00-STATE file at open; truth hierarchy: live quote, then
definition file, then state file, then memory, then chat context. Never hand-patch the
rendered output; fix the figures block and regenerate.

## Degradation ladder

When time is short, cut in this order and say what you cut:

1. The deal-desk confidence-composition view (keep the buyer view).
2. Phase-distribution commentary (keep the distribution itself).
3. Comparable-engagement derivation notes on Inferred figures (keep the Inferred label).

Never cut: the evidence-core run, the gate run and its printed reconciliation, the BOE table
with its flagged Unknowns, or the assumptions register.

## Files

- `scripts/rom_gate.py`: the deterministic figure gate. `--selftest` runs the fixtures.
- `scripts/rom_selftest.py`: standalone selftest wrapper for estate sync.
- `scripts/fixtures/`: one passing and one failing figures block.
- `references/basis-of-estimate.md`: BOE row spec, specificity bar, confidence mapping.
- `references/range-discipline.md`: how the range is stated, band width, model handling.
- `references/reconciliation-format.md`: the figures-block schema and the printed tie-out
  format.

## Release gate (required)

Before you deliver, run the gate. This is a required step, not a suggestion, and
not something a reviewer does later. Full spec in
[`release-gate.md`](../_shared/release-gate.md).

1. Apply writing-integrity to the prose. Use the bundled diagnostic tools to check saved writing. For
   a final artifact it emits a receipt the quality gate requires.
2. Run brand-renderer on the branded artifact: palette, borders, radii, logo,
   footer.
3. Run quality-gate before you call it final.

Do not present the artifact as finished until every check that applies has passed.
