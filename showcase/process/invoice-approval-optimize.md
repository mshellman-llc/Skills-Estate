---
skill: process
title: Speeding up a supplier invoice approval process
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: b0876f55eab1b43642897b2ff9bb019bfc4e063805612555ebcdb9add823addf
---

## Request

Our supplier invoice approval process takes far too long and suppliers keep chasing us for payment. I've pasted how it works today plus some timings from last month's invoices; can you work out what to fix first and how the process should look instead?

## Inputs

Run of the built `process-design` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### current-process.md

#### Supplier invoice approval: how it works today (Finance team notes)

1. Suppliers email invoices to invoices@example.com. A shared inbox is checked by the AP clerk (Dana) each morning.
2. Dana prints or saves each invoice, then keys the supplier, amount, date and PO number into the accounting system by hand.
3. Dana looks for the matching purchase order in a shared spreadsheet kept by Procurement. If she cannot find the PO number, she emails Procurement and waits for a reply.
4. Dana emails the invoice to the budget holder (the manager who raised the PO) for approval. Budget holders reply "approved" by email, or sometimes by chat.
5. Dana chases budget holders who have not replied. There is no fixed chase schedule; she does it when she remembers.
6. Invoices over 5,000 also need sign-off from the Finance Manager (Priya). Dana forwards the approved email to her.
7. Dana records the approval in the accounting system and adds the invoice to the weekly payment run, which the Finance Manager releases on Thursdays.
8. Invoices that miss the Thursday cut-off (approval recorded after Wednesday 5pm) wait for the next week's run.

Known problems from the team: invoices with no PO number on them are common; budget holders on leave leave invoices sitting; nobody is named as backup for approvals; some approvals are given in chat and cannot be found later.

Supplier payment terms: 30 days from invoice date.

#### october-timings.md

#### October timings (from Dana's tracking sheet)

Invoices processed in October: 120
Invoices over 5,000: 18
Invoices with missing or unmatched PO: 31 (of the 120)

Average working time per invoice for data entry (step 2): 6 minutes
Average time to find PO when it matches first time (step 3): 2 minutes
Average calendar days from receipt to data entry complete: 1.0
Average calendar days waiting for Procurement reply on unmatched POs: 3.5
Average calendar days from approval request to budget holder approval: 6.2
Average additional calendar days waiting for Finance Manager sign-off (over-5,000 only): 2.1
Average calendar days from approval recorded to payment run: 3.4
Average calendar days from receipt to payment, all invoices: 13.9

Invoices paid after the 30-day terms: 9 of 120
Invoices where the approval email or chat could not be located during the audit sample: 6 of 25 sampled

Not tracked: how many invoices needed more than one chase; budget-holder time spent per approval; cost of late payment.

## Output

#### Supplier invoice approval: what to fix first

**The biggest constraint is the wait for budget-holder approval.** It averages 6.2 calendar days, about 45% of the 13.9 days from receipt to payment (6.2 ÷ 13.9). Nothing in the process makes that wait end: there is no chase schedule, no named backup when a budget holder is away, and approvals arrive by email or chat. Fix this step first.

**Top recommendation:** send every approval request from one place with a fixed reminder schedule and a named delegate for each budget holder. The second fix is at intake: stop invoices with no PO number entering the process (31 of 120 in October).

Everything below the "Current state" heading is traced to your October timings. Where the timings don't give a figure, I mark it `not captured` instead of estimating it.

##### Current state (as you described it)

| # | Step | Owner | Type | Time (October) |
|---|------|-------|------|----------------|
| 1 | Invoice arrives in the shared inbox | AP clerk (Dana) | Manual | 1.0 day to reach end of step 2 |
| 2 | Key supplier, amount, date, PO into accounting system | Dana | Manual | 6 min per invoice |
| 3 | Match PO in Procurement's spreadsheet | Dana | Manual | 2 min when it matches first time |
| 3a | If no PO found: email Procurement and wait | Dana, Procurement | Manual, wait | 3.5 days average, 31 invoices |
| 4 | Email invoice to budget holder for approval | Dana, budget holder | Approval, wait | 6.2 days average |
| 5 | Chase non-responders | Dana | Manual | Chase count `not captured` |
| 6 | Over 5,000: forward to Finance Manager (Priya) for sign-off | Dana, Priya | Approval, wait | 2.1 days extra, 18 invoices |
| 7 | Record approval, add to weekly payment run | Dana | Manual | Part of the 3.4 days below |
| 8 | Priya releases the run on Thursdays; approvals after Wednesday 5pm wait a week | Priya | Approval, wait | 3.4 days from approval to run |

**Hand-offs:** 4 on every invoice (inbox to Dana, Dana to budget holder, budget holder back to Dana, Dana to the payment run). Procurement adds 2 for unmatched POs and Priya's sign-off adds 2 for invoices over 5,000, so up to 8.

**Work time versus wait time.** Data entry is 6 minutes × 120 invoices = 12 hours in the month. Calendar waits are measured in days. Typing is not what slows payment.

##### Where the 13.9 days go

| Segment | Average | Share of invoices affected | Weighted contribution to the 13.9 days |
|---------|---------|---------------------------|-----------------------------------------|
| Receipt to data entry done | 1.0 days | 120 of 120 | 1.0 |
| Budget-holder approval | 6.2 days | 120 of 120 | 6.2 |
| Approval recorded to payment run | 3.4 days | 120 of 120 | 3.4 |
| Waiting for Procurement on unmatched POs | 3.5 days | 31 of 120 | about 0.9 |
| Finance Manager sign-off | 2.1 days | 18 of 120 | about 0.3 |

The segments sum to about 11.8 days. The remaining 2.1 days of the 13.9 average is not explained by your timings. It may be time before the budget-holder request is sent or overlap between segments: `open: where do the other 2.1 days sit?`

*Assumption:* the Procurement and sign-off averages cover only the invoices that needed those steps, so I weighted them by 31/120 and 18/120.

##### Waste found

- **Waiting (largest):** 6.2 days for approval, 3.4 days for the payment run, 3.5 days on unmatched POs.
- **Rework:** 31 of 120 invoices (26%) arrive without a matching PO and loop back through Procurement. The cause on the supplier side is `not captured`.
- **Hand-offs:** every approval goes through Dana as relay. The Finance Manager sign-off is a second relay.
- **Manual work:** keying invoice data by hand and looking up POs in a spreadsheet.
- **Control gap:** in the audit sample, 6 of 25 approvals (24%) could not be found, because some were given in chat.
- **Outcome:** 9 of 120 invoices (7.5%) were paid after the 30-day terms.

##### Recommendations

Impact figures come only from your October data. Effort is my judgment and has no source in your notes.

| Priority | Change | Expected impact | Effort |
|----------|--------|-----------------|--------|
| 1 | **One approval channel with a fixed reminder schedule and a named delegate per budget holder.** Record the approval where the invoice lives, not in email or chat. | Targets the 6.2-day segment (45% of total). Size of reduction `not captured`. Also closes the 6-of-25 missing-approval gap. | Medium |
| 2 | **Require a PO number on every supplier invoice.** Send suppliers a notice, and auto-reply to invoices without one asking for a corrected copy. | Removes the Procurement loop for the 31 invoices (about 0.9 days of the average, 3.5 days on each affected invoice) once suppliers comply. Compliance rate `not captured`. | Low |
| 3 | **Change the payment-run cadence or cut-off.** For example, run twice a week, or release approved invoices on a rolling basis. | Targets the 3.4-day segment (24% of total). Direction is shorter; magnitude `not captured`. | Low to medium |
| 4 | **Request Priya's sign-off at the same time as the budget holder** for invoices over 5,000, instead of after. | Up to 2.1 days on 18 invoices (15% of volume). Only valid if sign-off doesn't depend on seeing the budget holder's decision: `open: does it?` | Low |
| 5 | **Give Procurement a live PO list** that Dana can search, replacing emails for lookups. | Reduces the 2-minute lookups and some of the 3.5-day waits. Magnitude `not captured`. | Medium |
| 6 | **Capture invoice data automatically** from the email or PDF, if the accounting system supports it. | Up to 12 hours of keying per month, minus time spent checking captured data (`not captured`). Cost `not captured`. | Medium to high |

Recommendation 4 changes a control. Treat it as a checkpoint, not a gate: Priya sees the invoice early, and payment still requires both approvals.

##### Future state

1. Invoice arrives at the shared inbox. An automatic reply returns any invoice without a PO number to the supplier.
2. Dana (or automatic capture) enters the invoice; the PO is matched against a searchable PO list.
3. The approval request goes to the budget holder from one system. Reminders go on the agreed schedule, then escalate to the named delegate.
4. For invoices over 5,000, Priya's sign-off request goes out at the same time.
5. Both approvals are recorded against the invoice. The invoice joins the next payment run under the new cadence.

**Steps:** 8 today (plus conditional step 3a) become 5. **Hand-offs:** 4 on every invoice today (up to 8) become 2 on every invoice (inbox to Dana, system to payment run). The budget-holder request and reply happen inside one system, and the Procurement loop is removed once suppliers comply. Priya's sign-off stays a separate approval, but runs in parallel. That count assumes the system's approval step does not count as a hand-off through Dana; if you count it, the figure is 4.

*Assumption:* these counts are a design target. They depend on the accounting system supporting in-system approvals, which your notes don't say (`open`).

##### Open questions and figures not captured

- `open:` What reminder interval and escalation point should apply? Your notes give no current rule to base a number on.
- `open:` Who is the named delegate for each budget holder?
- `open:` Can the accounting system send approval requests and reminders, or will this need a separate tool?
- `open:` Can Priya's sign-off run in parallel, or must it follow the budget holder's decision?
- `open:` What payment-run cadence is acceptable to Priya?
- `open:` Where do the other 2.1 days of the 13.9 average go?
- `not captured:` chase counts, budget-holder time per approval, cost of late payment, supplier compliance rate on PO numbers, and the time saved by any recommendation.

##### Implementation order

1. **Week-one fixes:** agree a named delegate for each budget holder; stop approving in chat; send the PO-number notice to suppliers. Dana's own tracking sheet already holds the baseline.
2. **Next:** set the reminder schedule and escalation rule; decide the payment-run cadence with Priya.
3. **Then:** move approvals into one system; run Priya's sign-off in parallel if she agrees.
4. **Later:** a searchable PO list, then automatic invoice capture.

After a month, repeat the October measurements. The baselines to beat are 6.2 days for approval, 3.4 days to the payment run, 31 of 120 unmatched POs, 9 of 120 late payments, and 6 of 25 approvals missing from the audit sample.

##### Checks run before delivery

The bundled scripts (preflight, writing check, quality gate) can't run here, so I did the checks by hand: I recomputed every percentage and the weighted segments from the October figures, confirmed that every impact claim traces to a supplied number or is marked `not captured`, and read the text for filler. The brand renderer does not apply because there is no styled file. No formal receipt exists.

**Files:** none produced; the analysis above is the deliverable (this file, `out/answer.md`).
