# Meridian Logistics business case

Source stamp: quote Q-000118 as of 2026-08-01, ledger snapshot 2026-08-04.

## 01 Executive frame

Bar: an approver who reads only this section knows what they are funding.
We recommend approving Phase 1 of the billing consolidation at $186,000 [quote: Q-000118].
The decisive factor is the ERP cutover date of 2026-12-15 [src: IT steering minutes, 2026-07-22].
The strongest argument against is that a point tool costs less in year one; we concede the year-one delta and hold on the rework cost below.

## 02 The client and the gap

Meridian Logistics runs regional freight brokerage on a fifteen-year-old billing stack.
Annual revenue of $412M.
Every carrier renewal is rebuilt from scratch in a spreadsheet owned by one analyst [src: discovery notes, 2026-06-30].

## 03 Why this moment

The ERP cutover lands 2026-12-15 and any integration built before approval gets built twice [src: IT steering minutes, 2026-07-22].
Budget for this fiscal year closes at the November board meeting [src: sponsor email, 2026-07-28].

## 04 Economics

Bar: every benefit closes a named pain, and the cost of waiting is shown arithmetic.
Benefit: renewals stop being rebuilt from scratch, closing the single-analyst spreadsheet dependency [src: discovery notes, 2026-06-30].
Benefit: unbilled renewal leakage of roughly 6% is recovered [inferred: A3, medium, ops lead estimate on the 2026-06-30 call].
Cost of waiting: $46,500/mo x 4 = $186,000 [computed: inputs C7, C9].
C7 is the monthly manual reconciliation cost [src: ops time study, 2026-07-10] and C9 is the decision-to-start interval [src: sponsor email, 2026-07-28].

## 05 The case against

Bar: the skeptic's argument written straight, then answered or conceded.
The skeptic says a point billing tool costs less in year one, and that is true; we concede the year-one delta [quote: Q-000118].
The answer is rework: a point tool integrated before the cutover gets rebuilt against the new ERP, and the rebuild estimate exceeds the delta [src: solution brief v2, 2026-07-18].
Doing nothing keeps the single-analyst dependency, which the client named as their largest operational fear [src: discovery notes, 2026-06-30].

## 06 Risk

Risk: the client-side data owner is 40% allocated elsewhere; severity medium; mitigation is naming a backup owner before kickoff [src: staffing thread, 2026-07-25].
Risk: cutover slip would compress stabilization; severity high; mitigation is phasing integration work after the cutover gate [src: solution brief v2, 2026-07-18].

## 07 Investment and delivery

Phase 1 investment is $186,000 fixed fee [quote: Q-000118].
Data migration is scoped but not yet priced [gap: migration scoping open, owner J. Ruiz, due 2026-08-29].
The plan sequences integration work after the 2026-12-15 cutover [src: solution brief v2, 2026-07-18].

## 08 The ask

Bar: the ask is specific and bounded.
Approve Phase 1 at $186,000 by the November board meeting [quote: Q-000118].
Not yet priced: data migration [gap: migration scoping open, owner J. Ruiz, due 2026-08-29].
Open decision: backup data owner, owner K. Patel, resolve by 2026-09-05 [src: staffing thread, 2026-07-25].
