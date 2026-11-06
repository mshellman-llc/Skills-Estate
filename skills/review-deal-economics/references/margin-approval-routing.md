# Margin policy and commercial review

Read the current project's confirmed commercial policy before applying a
margin threshold or approval ladder. Keep its source and verification date
in the review record. This estate supplies no default margin floor, role
rate or discount authority.

Without that policy, prepare the sourced economics and identify the missing
approval rule. Do not claim commercial approval. A missing policy does not
prevent comparing known costs or recording a financial discrepancy.

## Calculate and route

Calculate internal cost from each role's hours and cost rate. For time and
materials, reconcile the fee from hours and billing rates. For fixed fee,
use the confirmed quote value. Calculate gross margin as the fee less
internal cost, divided by the fee. Retain the inputs with the result.

Compare the calculated margin to the confirmed floor. Select the approver
from the supplied ladder and report the approval status actually recorded.
An approver's title in a template does not establish authority in this
project. Check explicit discounts separately from cost changes.

If staffing is unconfirmed, model the supported scenarios and show their
effect on margin. Compare the lower supported result with the floor when
the project policy requires it. Do not hide a range behind a point estimate.
Do not invent a probability for a scenario.

The review can display a gauge or a fee/cost/margin table. State the figures
in readable text too; color alone cannot communicate a policy exception.

## Connect risks to actual terms

For each material commercial risk, identify its coverage in the selected
contract or record the missing protection. Use the contract's actual clause
number and wording. These are patterns to inspect, not default legal terms:

| Pattern | Condition to inspect |
| --- | --- |
| Inventory assumptions | Discovered volume or complexity exceeds the agreed estimate basis. |
| Module boundary | A new module or license change alters the supported work. |
| Integration discovery | An interface differs from the confirmed integration assumptions. |
| Validation effort | Client delay or additional defects extend testing beyond the agreed work. |
| Post-launch support | A feature or training request falls outside agreed hypercare. |
| Client availability | Missing access or delayed client decisions affect the delivery plan. |

Keep a proposed protective term separate from one already accepted. This
workflow can recommend a scope or pricing decision; it cannot approve one.

## Figures block

`scripts/deal_desk_gate.py` validates the existing `deal-desk-figures` format.
Its names are compatibility identifiers for the review-deal-economics module.
The example below is fictional test data. Its floor and approval titles
have no authority for another engagement.

```deal-desk-figures
{
  "source_quote": "Q-EXAMPLE-001",
  "as_of": "2026-10-22",
  "pricing_model": "t_and_m",
  "fee": 10000,
  "roles": [
    {"role": "Consultant", "hours": 100, "rate": 100, "cost_rate": 60}
  ],
  "internal_cost": 6000,
  "stated_margin_pct": 40,
  "margin_floor_pct": 30,
  "floor_source": "Fictional policy example, verified 2026-10-22",
  "margin_vs_floor": "above",
  "approval_ladder": [
    {"min_margin_pct": 30, "approver": "Commercial owner"},
    {"min_margin_pct": 0, "approver": "Exception reviewer"}
  ],
  "approval_ladder_source": "Fictional policy example, verified 2026-10-22",
  "approval_route": "Commercial owner",
  "delivery_cosign": {"status": "pending"},
  "delivery_cosign_scope": "Scope and staffing review pending",
  "approval_action": "not_ready"
}
```

Use `fixed_fee` or `t_and_m` as the pricing model. The validator recomputes
cost from the role rows and checks the stated margin within its documented
tolerance. It also checks whether the floor comparison and approval route
match the supplied policy values. A valid record cannot establish that
the policy itself was approved; inspect its source separately.

Delivery review can be confirmed or conditional. It can also remain pending
or be declined. Confirmed review needs a named reviewer and date. Preserve
partial review scope, such as hours remaining under review. The approval
action is one recorded decision: approve, approve with conditions, reject
or not ready. Do not infer a signature from a passing record.
