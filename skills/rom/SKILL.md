---
name: rom
description: Rough-estimate method within project-scoping. Build a sourced effort or cost range from a supplied scope, comparables or quote, and preserve its basis and reopening conditions.
---

<!-- ESTATE-WRITING:BEGIN -->
Before writing, read the [writing standard](references/estate/writing.md). Apply it to every authored sentence. Review instructions and internal records too. Audience labels and file formats do not exempt prose from review.
<!-- ESTATE-WRITING:END -->


# Rough project estimate

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

Use the supplied scope and current rate card or relevant comparables as the
basis. Preserve each source revision and state how effort was derived. An
existing quote supplies confirmed commercial values when one is available;
it is not a prerequisite for a rough estimate. Never invent a rate or silently
turn a modeled range into a commitment.

## Orient on the available source

Read the brief and existing work breakdown. Use a local export when supplied.
A configured pricing connector can retrieve a quote, but its absence does not
block local scoping. Separate a fixed fee from time-and-materials assumptions.
Use phases from the project source; identify proposed phases as proposals.

Read the primary project-scoping workflow for the local calculator. From that
package root, `python3 scripts/estimate.py scope.json --output attempt/estimate.json`
creates a sourced working estimate and readable explanation. Its capacity
calculation is a lower bound, not a committed schedule.

Pin the audience and the requested level of detail before rendering the range.
For effort-only work without rates, deliver the hours and its basis. Identify
the missing pricing input rather than refusing the request.

## Evidence first

Run **evidence-core** before drafting. The registry entry for `rom` requires these
load-bearing domains: scope basis, workstream effort, role assumptions, rates or cost basis,
confidence, range reopeners, commercial posture. If a domain lacks support, retain the supported scope or effort work and name
the input needed for the missing calculation. Do not invent a full cost range.
Generated examples cannot supply evidence for a real engagement.

Every figure the ROM shows is a ledger entry: figure, source, confidence, as-of. Confidence
uses the evidence-core register, nothing else:

- **Confirmed**: stated in the quote and cross-checked by computation, traceable to a scope
  input.
- **Inferred**: derived from a comparable engagement or current-knowledge scoping, with its
  derivation stated. Keep derived effort labeled as estimated.
- **Unknown**: depends on a footprint dimension the client has not confirmed. These are
  flagged assumptions. They live in the basis-of-estimate table, each with a confirmation
  action (and the source-named phase in which it gets confirmed, when the source timeline has
  one), and each appears in the assumptions register with an owner and the gate it blocks.

Map confidence to presentation: Confirmed renders as fact, Inferred renders with its
derivation, Unknown renders as a flagged assumption, never as a settled figure. Conflicts
between sources render as both values with a recommendation, never a silent pick.

## The sections

Derive the set from the ledger, not from an example. Read
`references/basis-of-estimate.md` before writing the BOE table and
`references/range-discipline.md` before stating the range.

| Section | What it answers | The bar |
|---|---|---|
| Header | What engagement, which tier or option, what pricing model, which source revision or quote | A reader knows in five seconds what governs the page |
| Metric strip | The range, hours, duration, and the model-specific card | Every figure traces to its estimate input or quote field; fixed-price and T&M cards never coexist |
| Phase distribution | Hours across the source-stated phases | Phases come from the quote timeline; a heavy phase has a named reason |
| Basis of estimate | The footprint dimensions the estimate rests on | Every row is countable and specific to this client; Unknowns are flagged with a confirmation action, and a confirming phase when the source timeline evidences one |
| What moves the number | The range reopeners: scope conditions that would require a revised estimating basis. Contractual consequences come from the actual agreement | Read from this deal's scope, never a generic list |
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

Never assert a total you did not recompute. For a quote-anchored range using the
figures-block schema in `references/reconciliation-format.md`, run this module's gate from its own directory:

```bash
python3 scripts/rom_gate.py figures.json
```

The gate recomputes the three-way tie, checks hours times rate against the fee, checks that
the range bounds bracket the quote total, and checks the model card matches the pricing
model. It prints the full reconciliation and exits nonzero on any failure. The printed
reconciliation goes on the deal-desk view verbatim; for the buyer view it stays in the build
notes. Report the gate's counts, never an adjective. "Clean" is not a finding; "PASS, 0
failures" is.

**Discrepancy handling.** If a quoted figure fails to reconcile, preserve the quoted
discrepancy, label it, and request a corrected authoritative source. Do not present it as an
approved quote. A separately labeled calculated scenario may support the decision; it cannot
replace the source value, and a derived figure never silently substitutes for a quoted one in
a client-facing deliverable. Never silently smooth, and never silently override the quote. Cascade: if any figure changes, regenerate from the
figures block so numbers cannot drift between the model and the markup.

## Rendering and voice

Hand rendering to **brand-renderer**: it owns the palette, type, logo, layout
tokens, and the parity, visual, and brand release gates. Do not inline hex values here or in
the artifact build notes. Brand applies during the build, not after.

Run the **prose-pass** checker on every prose surface of the artifact and on this skill's own
output. Apply writing-integrity and the confirmed author profile. Preserve material
uncertainty in the claim. Review the rendered result after the diagnostic checks.

Fallback: if a governor is not installed on the current surface, state the check it would
have run, perform the best manual substitute, and say that is what you did. Never silently
skip.

## Boundaries

- Does not scope and does not create or edit quotes. That is the primary **project-scoping** workflow.
- Does not build the SOW. That is **sow**.
- Does not build the firm proposal. That is **interactive-proposal**.
- Derives prospective effort or cost only from the supplied basis. Commercial approval remains a separate project decision; an estimate cannot overwrite an accepted quote.
- Supports standalone effort ranges when their scope and estimating basis are supplied. An unavailable rate leaves pricing unresolved.

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
