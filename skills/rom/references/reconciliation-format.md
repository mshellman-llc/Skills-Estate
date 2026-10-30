# Reconciliation print format

Verification is by computation, and the computation is printed. A tie-out that happened
silently did not happen. This file defines the figures block the gate consumes and the
reconciliation block it prints.

This gate applies to quote-anchored figures. For local or effort-only estimates,
use the primary project-scoping calculator and its incomplete-estimate contract.
Do not invent quote fields, rates or commercial approval to satisfy this schema.

## The figures block

One JSON object, either in a standalone `.json` file or inside the first fenced ```json
block of a markdown or HTML build file. Build it from the quote, never by hand-copying
rendered markup.

```json
{
  "q_number": "Q-000043",
  "as_of": "2026-08-11",
  "pricing_model": "fixed_fee",
  "model_card": "fixed_price",
  "quote_total_hours": 1200,
  "blended_rate": 250.0,
  "quote_total_fee": 300000.0,
  "fee_source": "Fictional quote Q-000043 revision 1",
  "fixed_fee_basis": "Independently agreed milestone fee",
  "range_low": 270000.0,
  "range_high": 345000.0,
  "phases": [
    {"name": "Analyze", "hours": 240},
    {"name": "Build", "hours": 720},
    {"name": "Deploy", "hours": 240}
  ],
  "roles": [
    {"name": "Solution Architect", "hours": 400},
    {"name": "Consultant", "hours": 800}
  ],
  "work_packages": [
    {"name": "Pricing rule migration", "hours": 700},
    {"name": "Integration build", "hours": 500}
  ]
}
```

Field rules:

- `pricing_model` is `fixed_fee` or `t_and_m`. `model_card` is `fixed_price` or
  `tm_envelope` and must match the model. Exactly one card, always.
- Phase names are whatever the quote timeline states, verbatim. The gate checks sums, not
  names, and imposes no phase count or sequence.
- `work_packages` is optional; when absent the tie is two-way and the gate says so. When the
  quote carries work packages, include them; omitting them to dodge a mismatch is smoothing.
- All hours and money must be finite, nonnegative JSON numbers, not strings or booleans.
- Fixed fees require nonempty `fee_source` and `fixed_fee_basis`, naming the actual authoritative commercial record and agreed basis. Their presence does not itself verify commercial authority.

## The gate's checks

1. **Three-way tie**: sum(phase hours) = sum(role hours) = sum(work-package hours) =
   `quote_total_hours`, exact to 0.01 hours.
2. **Fee reconciliation**: for T&M, `quote_total_hours` times `blended_rate` matches
   `quote_total_fee` within the retained 0.5 percent arithmetic tolerance. This
   diagnostic tolerance does not authorize changing quoted amounts. A fixed fee
   uses its separately sourced `fee_source` and `fixed_fee_basis`; hours times rate
   may differ and cannot replace that fee.
3. **Range brackets the quote**: `range_low` <= `quote_total_fee` <= `range_high`, with
   `range_low` < `range_high` and both positive.
4. **Model card**: exactly one card, and it matches the pricing model.

## The printed block

The gate prints this shape. On the deal-desk view it appears verbatim; on a buyer view it
stays in the build notes.

```
ROM figure gate: Q-000043 (fixed_fee), as of 2026-08-11
  phase hours total:        1200.00
  role hours total:         1200.00
  work package hours total: 1200.00
  quote total hours:        1200.00
  three-way tie: PASS
  fixed fee: check authoritative fee_source and stated fixed_fee_basis
  range: 270000.00 to 345000.00 brackets quote total 300000.00: PASS
  model card: fixed_price matches fixed_fee: PASS
RESULT: PASS (0 failures)
```

## Discrepancy handling

On any failure the gate prints a `FLAG:` line per finding with the source values and the
per-line delta, and exits nonzero. The response is never to smooth. Either fix the figures
block at its source (a transcription error) and rerun, or, when the quote itself is
internally inconsistent, preserve the quoted discrepancy, label it with the flag on the
artifact, and request a corrected authoritative source from the quote owner. A separately
labeled calculated scenario may accompany it, but a derived figure never silently
substitutes for the quoted one in a client-facing deliverable. Never silently carry a wrong
number, and never silently override the quote.
