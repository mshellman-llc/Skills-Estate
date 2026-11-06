---
skill: compare-scope-options
title: Scope comparison of two repairs portal quotes with staffing variants
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 5ce4f83358b1c63d3abedd2a09d4258a3642c8d5b6fcba42e525cb313e45c6fc
---

## Request

Please build the scope reference for Fernhill Housing Association comparing quotes Q-4101 and Q-4102 for the tenant repairs portal, Q-4101 first. The export is in inputs/ and I want both staffing variants shown with exact prices.

## Inputs

Run of the built `compare-scope-options` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so. Other files it produced, not shown here: `plan.json`, `scope.html`, `scope.reconciliation.json`, `source.json`.

#### quote-export.md

#### Quote export: tenant repairs portal

Source system: Quote desk export (CSV converted to Markdown by the account manager)
Revision: 14
Captured: 2026-10-28 09:40 +00:00
Client: Fernhill Housing Association

##### Q-4101 (Core)

Active snapshot: Q-4101-A

| ID | Item | Category | Hours | Optional | Active | Description |
|---|---|---|---|---|---|---|
| repair-form | Repair request form | Intake | 40 | no | yes | Tenants report a repair with address, category and up to five photos. |
| triage-rules | Triage rules | Intake | 32 | no | yes | Sort each request as emergency, urgent or routine using Fernhill's approved rules. |
| contractor-sync | Contractor scheduling sync | Integration | 56 | no | yes | Send accepted jobs to the contractor scheduling system and read back appointment dates. |
| status-tracking | Tenant status tracking | Tenant experience | 24 | no | no | Let tenants see where a repair stands and its booked appointment. |
| sms | SMS notifications | Tenant experience | 16 | yes | no | Text tenants when a job is booked or rescheduled. |
| staff-training | Staff training | Handoff | 12 | no | yes | Train the repairs team to review and reassign triaged requests. |

| Snapshot | Label | Price | Weeks | Staffing hours |
|---|---|---|---|---|
| Q-4101-A | Standard team | GBP 48,600.00 | 7 | 300 |
| Q-4101-B | Lower-rate team | GBP 44,250.00 | 8 | 330 |

##### Q-4102 (Extended)

Active snapshot: Q-4102-A

| ID | Item | Category | Hours | Optional | Active | Description |
|---|---|---|---|---|---|---|
| repair-form | Repair request form | Intake | 40 | no | yes | Tenants report a repair with address, category and up to five photos. |
| triage-rules | Triage rules | Intake | 40 | no | yes | Sort each request as emergency, urgent or routine using Fernhill's approved rules. |
| contractor-sync | Contractor scheduling sync | Integration | 56 | no | yes | Send accepted jobs to the contractor scheduling system and read back appointment dates. |
| open-job-import | Open-job import | Integration | 36 | yes | no | Load repairs already open in the legacy system once its field mapping is approved. |
| status-tracking | Tenant status tracking | Tenant experience | 28 | no | yes | Let tenants see where a repair stands and its booked appointment. |
| sms | SMS notifications | Tenant experience | 16 | no | yes | Text tenants when a job is booked or rescheduled. |
| audit-accessibility | Accessibility audit | Handoff | 20 | no | yes | Check the tenant pages against WCAG 2.2 AA and list defects found. |
| staff-training | Staff training | Handoff | 16 | no | yes | Train the repairs team to review and reassign triaged requests. |

| Snapshot | Label | Price | Weeks | Staffing hours |
|---|---|---|---|---|
| Q-4102-A | Standard team | GBP 71,900.00 | 10 | 440 |
| Q-4102-B | Lower-rate team | GBP 66,300.00 | 11 | 470 |
| Q-4102-C | Draft v3 (not active) | GBP 74,500.00 | 10 | 450 |

#### scope-notes.txt

Scope notes from the quote desk, applying to both quotes

- Tenant and repair records stay in Fernhill's housing management system. The portal reads and writes them through the existing interface.
- A native mobile app is outside both quotes.
- SMS message charges are paid by Fernhill to its messaging provider and are not in either price.
- Open-job import (Q-4102 only, optional) depends on Fernhill approving the legacy field mapping before work starts.
- Staffing hours cover delivery activities such as project management and testing. Item hours are estimates for each item.

## Output

I've built the scope reference for Fernhill Housing Association as one self-contained HTML page. It compares Q-4101 (Core) and Q-4102 (Extended) in that order. The mode is a two-quote static comparison with both staffing variants and exact prices. The quotes are as of the export captured 2026-10-28 09:40 (+00:00), revision 14, from the quote desk. A local export doesn't show live state, so ask for a fresh export if either quote has changed since then.

**I couldn't run the scripts or a browser, so the checks below were done by hand.** The validator, the builder, the brand preflight, the prose and brand checkers, the browser and print checks and the PDF export all need Python, Node or Chromium. I applied the reconcile rules from `validation.md` myself and wrote the HTML following the builder's structure and stylesheet. The reconciliation file is marked as hand-written and has no hashes. Please run the two scripts on `out/source.json` and `out/plan.json` before sending this to the client. You didn't ask for a PDF, so I didn't make one.

#### Prices and plans

Each price is exact and comes from the staffing snapshot. The matrix has no per-item prices.

| Option | Plan | Price | Duration | Staffing hours |
|---|---|---|---|---|
| Core (Q-4101) | Standard team (active) | GBP 48,600.00 | 7 weeks | 300 |
| Core (Q-4101) | Lower-rate team | GBP 44,250.00 | 8 weeks | 330 |
| Extended (Q-4102) | Standard team (active) | GBP 71,900.00 | 10 weeks | 440 |
| Extended (Q-4102) | Lower-rate team | GBP 66,300.00 | 11 weeks | 470 |

The export also holds a third Q-4102 snapshot, "Draft v3 (not active)", at GBP 74,500.00 over 10 weeks and 450 hours. It isn't the active snapshot and you didn't ask for it, so it's left out. It stays in the source file.

#### What differs between the options

Counts are given per state. Available items aren't counted as included.

| Item | Core | Extended |
|---|---|---|
| Repair request form | Included, 40 h | Included, 40 h |
| Triage rules | Included, 32 h | Included, 40 h |
| Contractor scheduling sync | Included, 56 h | Included, 56 h |
| Open-job import | Not included | Optional, 36 h |
| Tenant status tracking | Available, 24 h | Included, 28 h |
| SMS notifications | Optional, 16 h | Included, 16 h |
| Accessibility audit | Not included | Included, 20 h |
| Staff training | Included, 12 h | Included, 16 h |

- **Core (Q-4101):** 4 included, 1 optional, 1 available, 2 not included.
- **Extended (Q-4102):** 7 included, 1 optional, 0 available, 0 not included.

Three points in the matrix are easy to misread:

- Tenant status tracking is present in Core but not selected. It is shown as Available, and adding it may change the price or schedule.
- Open-job import and the accessibility audit are absent from Core, so their cells show no hours.
- Hours differ by option for triage rules, tenant status tracking and staff training. Each cell shows its own quote's figure.

#### Scope conditions shown on the page

- Tenant and repair records stay in Fernhill's housing management system. The portal reads and writes them through the existing interface.
- A native mobile app is outside both quotes.
- SMS message charges are paid by Fernhill to its messaging provider and are not in either price.
- Open-job import depends on Fernhill approving the legacy field mapping before work starts.
- Staffing hours cover delivery activities such as project management and testing. Item hours are estimates for each item.

#### Checks and gaps

- **Reconciliation, by hand:** The 8 matrix items are the union of both quotes' items, with unique IDs. Every active ID is in its full list, and the active snapshots match the export. Snapshot figures were copied exactly. Absent items have null hours.
- **Descriptions:** Every description is the export's own wording, so I added no claims. There was no `effort_basis` field to cite.
- **Brand:** No project `brand.md` was supplied, so the page uses the neutral Baseline profile, with no logo. Its colours, type and 1px borders are inlined. I did not check contrast or the page's appearance, because I could not render it.
- **Not done:** No desktop, narrow-width or print inspection, and no scripted prose or brand check. I read the authored sentences. The option summaries (Core and Extended) follow the item states in the matrix. They give no recommendation, because you supplied no decision criteria.
- **Not published:** Creating this file doesn't change either quote or update any knowledge hub.

#### Files

- `out/scope.html`: the reference page, with the option panels, the staffing-plan tables, the grouped scope matrix, the state legend and the scope conditions.
- `out/source.json`: the normalized capture of the export, including the inactive draft snapshot.
- `out/plan.json`: the presentation record that the page was built from.
- `out/scope.reconciliation.json`: the hand-written reconciliation record, described above.
- `out/answer.md`: this reply.
