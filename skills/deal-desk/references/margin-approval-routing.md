# Margin governance and approval routing

## Where the numbers come from, and why this file is not canon

The figures below are transcribed from the Playbook Overview Template,
sections 13 (discount thresholds) and 14 (protective clauses summary), as
read on 2026-08-11. That template calls its own sections 13 and 14
"universal Estate canon, do not modify."

**This file is a pointer, not a home.** Canon can change, and a skill that
carries its own copy of the floor becomes a stale second authority the day
it does. Before building any packet, re-verify the current values against
the live Playbook Overview canon (the current template in Drive, or the
playbook's published overview). Write the values you verified, with the
verification date, into the packet's figures block fields `floor_source` and
`approval_ladder_source`. The gate script rejects an undated source, which
is deliberate: it forces the re-verification to actually happen.

## The margin floor and the approval ladder

As of 2026-08-11, per Playbook Overview Template section 13:

- The **48% margin floor** is canon. At or above it, standard AE authority
  holds (0 to 5% discount), rationale documented in the deal record.
- **45 to 48%** (5 to 10% discount): Deal Desk approval, requiring this
  packet with margin analysis and lever discussion.
- **42 to 45%** (10 to 15% discount): Deal Desk plus CEO approval. Surface
  the trade-offs.
- **Under 42%** (15%+ discount): ELT. Margin governance treats under 45% as
  an ERROR; scope cannot proceed without rebalancing or executive override.
- Margin math anchors on the AE list rate of $325 per the canonical pricing
  sheet; rate-card variance is flagged separately.

Routing rule for the packet: compute the real margin, find the band it lands
in, and name that band's approver as the `approval_route`. Every ask in the
packet that touches price or discount routes to that approver or higher,
never lower. The gate verifies the route against the ladder carried in the
figures block, so the packet cannot quietly under-route.

## Rendering margin against the floor

Margin is the headline. In the HTML rendering it is a gauge with the floor
marked; in print it is the revenue / internal cost / gross margin table with
the floor stated beside it. Three requirements:

1. The margin is computed and printed with its inputs (fee, internal cost,
   and the role rows they recompute from), never asserted.
2. The floor comparison is explicit prose: "52.8% against the 48% floor
   (above)", not a color.
3. If the real margin depends on an unconfirmed staffing assumption, the
   real margin is a range. Present the range with the pessimistic end
   against the floor. Hiding the real margin behind a point estimate is a
   registry hard fail.

## Protective clauses (SOW section 6)

Per Playbook Overview Template section 14, read 2026-08-11. Re-verify
against the live SOW master before citing clause text; the packet cites
coverage, the SOW owns the language.

| Clause | Purpose | Trigger condition |
|---|---|---|
| 6.1 Inventory gate | Protect against undisclosed scope: record, object, automation counts | Discovered inventory exceeds SOW section 7 thresholds |
| 6.2 ARM scope boundary | Limit ARM functionality to in-scope modules; protect against license changes | ARM module change, license downgrade, or scope expansion during delivery |
| 6.3 Integration discovery | Limit integration scope | Integration count or complexity exceeds section 7 assumptions |
| 6.4 Parallel run / validation | Cap validation hours | Client delay or out-of-scope defects extend validation past the contracted window |
| 6.5 Post-go-live stability | Define hypercare scope and duration | Feature, training, or client-side change requests during hypercare |
| 6.6 Client availability | Define client SME hours, response SLA, sponsor commitment | Client unavailability extends the timeline |

In the packet's risk section, every margin risk pairs with either the clause
that protects it (by number) or a flag saying no clause covers it. One or
the other, never both, never neither.

## The figures block schema

The gate script (`scripts/deal_desk_gate.py`) parses this block. All keys
required.

```deal-desk-figures
{
  "source_quote": "Q-000181",
  "as_of": "2026-08-11",
  "pricing_model": "t_and_m",
  "fee": 218000,
  "roles": [
    {"role": "SA", "hours": 320, "rate": 275, "cost_rate": 130}
  ],
  "internal_cost": 102800,
  "stated_margin_pct": 52.84,
  "margin_floor_pct": 48,
  "floor_source": "Playbook Overview canon section 13, re-verified 2026-08-11",
  "margin_vs_floor": "above",
  "approval_ladder": [
    {"min_margin_pct": 48, "approver": "AE"},
    {"min_margin_pct": 45, "approver": "Deal Desk"},
    {"min_margin_pct": 42, "approver": "Deal Desk + CEO"},
    {"min_margin_pct": 0, "approver": "ELT"}
  ],
  "approval_ladder_source": "Playbook Overview canon section 13, re-verified 2026-08-11",
  "approval_route": "AE",
  "delivery_cosign": {"status": "confirmed", "by": "R. Alvarez", "date": "2026-08-10"},
  "delivery_cosign_scope": "scope, hours, and assumptions",
  "approval_action": "approve"
}
```

Field notes:

- `pricing_model`: exactly `fixed_fee` or `t_and_m`. Never both.
- `roles`: hours and rates SE from the quote; `cost_rate` from the pricing
  sheet cost model. The gate recomputes `internal_cost` from these rows, and
  on T&M recomputes `fee` too.
- `stated_margin_pct`: must equal (fee minus internal_cost) / fee within
  0.5 points, or the gate fails.
- `margin_vs_floor`: `above` or `below`, and it must match the arithmetic.
- `approval_route`: must match the ladder band the recomputed margin lands in.
- `delivery_cosign.status`: one of `confirmed`, `conditional`, `pending`,
  `declined`. Blank, `assumed`, `inferred`, and `tbd` all fail. `confirmed`
  requires `by` (a named individual) and `date`. `pending` is an honest,
  passing status; the packet then names who signs and by when.
- `delivery_cosign_scope`: optional but recommended; "scope reviewed, hours
  under review" is a real status and belongs here verbatim.
- `approval_action`: exactly one of `approve`, `approve_with_conditions`,
  `reject`, `not_ready`. A list fails; more than one approval ask is a
  registry hard fail.
