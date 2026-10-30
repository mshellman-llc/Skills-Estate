---
name: project-scoping
description: "Develop project scope, effort, staffing and timelines, including rough estimates and confirmed quote models. Use supplied exports, rate cards and comparables; use a CRM connector only when configured for the project."
---

## Choose the requested task

Use the primary workflow below unless the request matches a mode in this table. For a matching mode, read its complete linked workflow and required references, then produce that mode's output. Preserve its calculations, failure handling and acceptance checks. One request does not require every mode.

| Requested mode | Complete workflow |
| --- | --- |
| rough estimate | [rom](_runtime/rom/WORKFLOW.md) |


# Project scoping

Build the requested scope from current project evidence. Use a supplied export
or the local model below when no pricing integration is configured. A rough
estimate does not require an existing quote. Keep accepted commitments separate
from draft scope and estimate assumptions.

## Select the work

| Request | Output |
| --- | --- |
| Define scope | Work items with supported boundaries and acceptance conditions |
| Estimate effort | Sourced role-hour ranges and their basis |
| Estimate cost | The effort model with an explicit rate source and currency |
| Plan staffing | Role capacity and a schedule constrained by dependencies |
| Revise a quote | A comparison against the confirmed quote revision; authorized changes only |

Read the supplied brief and existing decisions before asking a question. Find
the constraints affecting scope or price. Preserve contradictory evidence as
an unresolved decision. Ask only when a missing choice materially changes the
work; continue the supported parts while it is pending.

## Define the deliverable scope

Organize items around the behavior or deliverable being supplied. An item can
carry its requirements work through validation and deployment. Avoid counting
the same lifecycle effort again in a separate overhead row. A standalone test
or assessment engagement may have its own deliverable; follow the actual brief.

Give each item a stable ID and descriptive name. Explain its behavior and the
condition that bounds it. Link it to its source and acceptance check. Keep
dependencies and exclusions where they affect that item. Use the project's
capability taxonomy if one exists; a local draft needs no custom CRM taxonomy.

Distinguish explicitly requested work from a necessary implication. Keep an
inferred addition proposed until its scope owner accepts it. Do not turn an
unanswered question into a statement that documentation or access is absent.
An assumption is a proposed estimating condition, with its consequence if it
changes. It is never a substitute for a fact.

Read [the estimation method](references/methodology.md) for calibration and
staffing decisions. Use meaningful item names in cross-references; retain IDs
for traceability rather than making the reader decode abbreviations.

## Estimate with available sources

Use current scope decomposition or relevant comparables. Describe differences
in volume and complexity when adapting another engagement. A user-supplied
anchor can support an estimate when its working hours and scope are explicit.
Do not assume a working week, a phase split or a staffing ratio.

Keep a low and high bound around the expected effort where the source supports
a range. Explain which condition moves each bound. Do not invent a confidence
percentage or treat the expected value as a statistical median without data.
If effort remains unknown, retain the item as unestimated and identify the
discovery needed. Do not present a priced subset as the complete project cost.

Use the supplied rate card or confirmed quote for rates. Preserve its revision
and distinguish cost rates from client billing rates. Without rates, deliver
the effort estimate and the missing pricing input. Do not import old rates
from this estate or another engagement.

## Run the local calculator

The calculator requires Python 3 and no external service:

```bash
python3 scripts/estimate.py scope.json --output attempts/001/estimate.json
```

It writes the exact decimal calculations and a readable Markdown estimate.
Existing outputs are preserved. Use another attempt path after a revision.
The [fictional input](fixtures/estimate.example.json) shows the full contract.
Its rates and effort are test data, with no authority for a real project.

| Input | Required content |
| --- | --- |
| `source` | Reference and revision of the scope model |
| `currency` | Currency supplied for this estimate |
| `rates` | Role and rate, with the source of that rate |
| `items` | Unique ID and name; description and source; estimated items also need a basis and role allocations |
| `items[].status`, when used | `estimated` (the default) or `unestimated`; other values are refused |
| `items[].discovery_needed` | Required for an unestimated item; explain what must be learned before estimating it |
| `allocations[].hours` | Nonnegative `low`, `expected` and `high` values in that order |
| `capacity`, when used | Role count and weekly hours per person, with availability from 0 to 1 |
| `assumptions` and `exclusions` | Conditions and work boundaries preserved in the result |

The result includes item calculations and role-hour totals. It also gives the
aggregate hours and fee for each scenario. Amounts retain their decimal value;
the calculator applies no implicit commercial rounding or contingency uplift.
It records the input hash and calculator hash.

For work with no effort basis, set `status` to `unestimated`, retain its source
and description, and supply `discovery_needed`. Omit allocations or use an empty
list. The calculator rejects allocations on an unestimated item so hours cannot
be silently discarded.

Output format 2 retains every item. When any item is unestimated, the status is
`incomplete-estimate`, `totals_complete` is false, and full-project `totals` is
null. `estimated_subtotal` contains only the estimated work; it is null when no
item has an estimate. For fully estimated scope, `totals` keeps the scenario
calculations. Fees remain null without rates. Consumers must check completeness
before using totals. The Markdown shows item calculations, role hours, supplied
rate sources, and all three capacity scenarios. Capacity covers estimated work
only, so unknown work cannot acquire an implied delivery date.

Capacity produces a workload lower bound in weeks. Dependencies and waiting
time can extend the schedule. A capacity bound cannot establish a delivery date.
For a schedule, place the actual work against dependencies and agreed resource
availability. Preserve phase names and staffing increments from the project.

Inspect the generated estimate against the input. Recompute a representative
item and reconcile the totals. Check the range drivers and the meaning of each
assumption. Apply writing-integrity to the generated prose, including text
carried from a draft input. Calculation success does not establish scope quality.

## Use a configured CRM adapter

Read [CRM scoping](references/crm-scoping.md) only when the project uses the
documented custom integration. Inspect the tools actually available and confirm
the org before a write. Read [payloads](references/payloads.md) before preparing
a supported mutation. Use the target's actual metadata and schema version.

Create or update a record only within the user's authorized request. Show the
affected quote and scope before a material change. Never add team membership,
replace a tag catalog or activate a timeline merely to make local estimation
possible. Read back changed records and report what the system accepted.

## Deliver the result

Return the usable scope and requested calculations. Retain assumptions with the
estimate and name the conditions that would reopen it. Save actual generated
files and failed attempts. A hub update is optional and needs an available,
authorized project destination; local work remains usable without it.

Use scope-options for a comparison or interactive proposal. Use the
statement-of-work workflow for the contract. A new estimate does not replace an
accepted quote, authorize a production operation or establish client approval.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
