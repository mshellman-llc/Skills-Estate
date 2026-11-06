# The 12-section catalog

One catalog for both moments. The package (moment 1, at signature) and the brief
(moment 2, at delivery acceptance) carry the same 12 sections in the same order;
the brief is the package at a later state of completion. Rename a section to the
deal's language if that helps the reader, but keep each section's job.

Every section is always present. It is either filled with sourced facts, or it
carries one or more named gaps, each with an owner, a resolve-by date, and the
gate it blocks. A section that does not apply says so in one sourced line, for
example "Greenfield build; no incumbent process to map (SOW section 2, exhibit A)."
A blank section fails the gate.

Open each section with the one-line standard it is held to. The bar column below
is that line.

| # | Section | Answers | The bar |
|---|---------|---------|---------|
| 01 | The engagement | What was sold, what is explicitly out, the one outcome it is judged on, and the contract baseline: fee model, figures, hard dates, signed assumptions | A reader new to the account gets it in two minutes; every figure traces to the executed SOW or the quote |
| 02 | What came before | What a prior assessment or discovery settled, and what was left deliberately open | The team can name what is closed versus open, and never reopens a settled call in front of the client |
| 03 | Process and current state | How it works today and where it breaks | The as-is view names real people and tools, marks every manual break, and ties each break to the fix that was sold |
| 04 | System landscape | What they run, labeled keep, replace, or connect, with owners, access status, integrations, and the migration and testing notes from the pursuit | Every system labeled, each owner named, every access dependency flagged before kickoff |
| 05 | Solution shape | The ownership boundaries at orientation depth | A reader sees what each system owns and what crosses the seam; implementation depth lives in the Solution Brief and is pointed to, not recreated |
| 06 | Decisions inherited | Each shaping decision: the call, the rationale, the owner, settled versus open; delivery-lens and maturity-gap flags carried forward from the pursuit | Every decision has status, owner, and rationale; the open ones are visible, not buried; no flag raised during selling is dropped at the seam |
| 07 | Sell-cycle promises | Everything said to the client, split into promises the SOW contains (with the clause) and promises it does not (flagged liabilities) | Every promise is sourced to where and when it was said; every off-contract promise carries a flag and an owner; "nothing off-contract was found" is itself a sourced claim naming what was searched |
| 08 | Risks, assumptions, gaps | Real risks with real mitigations; load-bearing assumptions with what breaks if false; the known gaps | Severity plus owner plus a mitigation that is not a restatement; every assumption names its failure consequence |
| 09 | The people | Who decides, who to win, who to protect; the deal-cycle roster against the delivery roster, mismatches flagged | The team knows whose metric the project protects and who holds each access dependency; postures are sourced, never asserted; every deal-versus-delivery mismatch is explicit |
| 10 | Relevant prior engagements | Comparable past builds and the specific artifact to reuse | Each names a schema, sequence, or template to reuse with a pointer to where it lives, not "we did something similar" |
| 11 | Discovery sessions | The validation sessions to run in week one, before any build commitment, ordered by risk | Every session has a named owner, the right attendees, and a concrete output that closes a ledger Unknown or Inferred |
| 12 | What good looks like | The readiness checklist and the definition of done | Every criterion is observable, carries a binary test, and ladders to the one outcome from section 01 |

## Section notes

**01 The engagement.** Lead with the success spine: the one outcome, ideally a
number with a before and after, or a small set of observable conditions. State it
here, return to it in 12. The contract baseline subsection is the only home for
money: fee model (fixed fee or T&M, never both), total, payment schedule, hard
dates, and the volumetric assumptions the price rests on, each cited to the SOW
clause or quote field.

**06 Decisions inherited.** The pursuit resolved options and made calls under
pressure. Delivery inherits those decisions, not the deliberation. Record each as:
decision, date, made by, rationale, source, settled or open. Carry every
delivery-lens flag from scope review and every maturity-gap tag (for example CPQ
amendments, ERP integrations, RCA migrations) forward verbatim; dropping a flag at
the boundary is a named failure mode.

**07 Sell-cycle promises.** The reason this section exists: the historical pattern
that pulls sales back into delivery is a client saying "but your team told us."
Harvest promises from transcripts, email, and Slack, not from the seller's memory
alone. For each: the promise text, where and when it was said, by whom, whether
the executed SOW contains it (cite the clause) or not (flag it, name an owner, and
route it: honor it, price it as a change order, or have the Pursuit Lead reset the
expectation before kickoff).

**09 The people.** Two rosters side by side: who was in the deal cycle, who is in
delivery. Flag every person who appears on one side only. An economic buyer absent
from delivery, or a delivery-side owner nobody met during the sale, is a top cause
of failed kickoffs and belongs in section 11 as a session or in section 08 as a
risk.

**11 and 12** have their own spec: `week-one-definition-of-done.md`. They are the
reason the brief exists and are never cut, thinned to placeholders, or satisfied
by gaps alone at moment 2.
