# Deal Desk readout: Northwind Systems, CPQ to Revenue Cloud phase 1 (broken fixture)

This fixture carries a stated margin that does not recompute, a floor verdict
that contradicts the arithmetic, an undated floor source, a blank cosign, and
an approval route that skips the ladder. Every one of these must fail.

```deal-desk-figures
{
  "source_quote": "Q-000181",
  "as_of": "2026-08-11",
  "pricing_model": "t_and_m",
  "fee": 218000,
  "roles": [
    {"role": "SA", "hours": 320, "rate": 275, "cost_rate": 190},
    {"role": "PM", "hours": 160, "rate": 250, "cost_rate": 180},
    {"role": "DEV", "hours": 400, "rate": 225, "cost_rate": 170}
  ],
  "internal_cost": 102800,
  "stated_margin_pct": 55.0,
  "margin_floor_pct": 48,
  "floor_source": "the usual floor",
  "margin_vs_floor": "above",
  "approval_ladder": [
    {"min_margin_pct": 48, "approver": "AE"},
    {"min_margin_pct": 45, "approver": "Deal Desk"},
    {"min_margin_pct": 42, "approver": "Deal Desk + CEO"},
    {"min_margin_pct": 0, "approver": "ELT"}
  ],
  "approval_ladder_source": "Playbook Overview Template section 13",
  "approval_route": "AE",
  "delivery_cosign": {"status": "", "by": "", "date": ""},
  "approval_action": "approve"
}
```
