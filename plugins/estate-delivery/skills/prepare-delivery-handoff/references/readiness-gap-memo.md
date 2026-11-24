# Handoff readiness gap memo

The memo is the output when the evidence check returns Insufficient, including an unsigned
deal. It tells the reader what blocks delivery, what already holds, and what closes each
blocker. It is written for the delivery lead and the seller, who may be one person.

## File type

Write the memo as Markdown, `handoff-readiness-gap-memo.md`. A branded HTML page is allowed
when the audience needs one; it goes through brand-renderer and keeps the same sections in
the same order. The run record (`run-record.md`, per `_shared/output-contract.md`) sits
beside the memo and carries the commands, gate results and outstanding human actions. The
memo does not replace it.

## Sections, in order

Each section is a level-two heading with the text shown here, so a reviewer can hold two runs
to one shape. `scripts/check_gap_memo.py` checks them.

1. `What stops the handoff`: one or two sentences that name the blocker first.
2. `What already holds`: the settled ground delivery can count on, each line sourced.
3. `Blockers`: a table with the blocker, its owner, its closing condition and the work it
   holds back. Take the owner, closing condition and stop rule from the ledger.
4. `Ownership gaps`: blockers with no owner, or an explicit line saying there are none.
5. `Promises made before signature`: each promise, where it was said, and whether the
   agreement or draft carries it.
6. `Evidence`: the plain names of the sources read and the sources nobody searched. Record
   IDs stay in the source index.
7. `Next gate`: what has to be true before this skill runs again, and what that run builds.

## Rules

- State the money rule's limit: figures come from the executed agreement and its quote only.
  Before signature, say that the figures shown belong to the draft and quote revision named.
- Record no warm transfer and no acceptance that did not happen.
- Never fill a gap from an example or from memory. Name it as a blocker.
- Fixture: `scripts/fixtures/gap_memo_example.md`, an invented bakery deal.
