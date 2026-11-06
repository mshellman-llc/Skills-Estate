# Asks, decisions log, and sign-off formats

From the Deal Desk Readout Template approval section, read 2026-08-11.

## Asks

Two to six asks. Every ask carries a recommendation. Deal Desk does not
encounter an ask without a position; a list of open questions is a packet
that is not ready for review.

Format per ask:

| # | Ask |
|---|---|
| 1 | **Headline**, one sentence: what decision is being requested. **Context:** one to three sentences of relevant background, sourced. **Recommend:** one sentence, the AE/SSL position stated directly. |

Rules:

- The headline is a decision, not a topic. "Approve the 7% discount to hold
  the June start date" not "Discount discussion".
- Context cites its sources like everything else in the packet. An ask built
  on an inference says so.
- The recommendation takes a side. "Either could work" is not a position.
- Asks that touch price or discount route to the ladder approver computed in
  `margin-approval-routing.md`, or higher. Note the required approver in the
  ask when it is above the room.
- The asks are distinct from the single `approval_action`. The packet
  requests exactly one overall approval action (approve, approve with
  conditions, reject, or not ready); the asks are the specific decisions
  that action decomposes into. More than one overall approval ask is a
  registry hard fail.

## Decisions log

Filled live during the Deal Desk meeting, not before, not reconstructed
after. Empty rows in the pre-meeting packet are correct; a pre-filled
decision is a fabricated approval.

| Time | Decision | Decided by | Status |
|---|---|---|---|
| meeting timestamp | what was decided, in the words used | named individual | Approved / Rejected / Tabled |

Rules:

- Decided by is a named individual, never a role and never "the room".
- Status vocabulary is closed: Approved, Rejected, Tabled. Tabled entries
  get a matching action item with an owner and a due date.
- The log is append-only during the meeting. A reversed decision is a new
  row, not an edit.

## Action items

| Action | Owner | Due |
|---|---|---|
| specific action | named individual | date |

Every Tabled decision, every conditional approval, and every unresolved flag
that survived the meeting lands here. An action without an owner and a date
is a wish.

## Sign-off

| Role | Name | Decision |
|---|---|---|
| Deal Desk reviewer | name | Approved / Not approved |
| AE | name | Acknowledged |
| Delivery lead | name | Deliverable confirmed |

The delivery lead row is the cosign. It is the one mandatory human input in
the whole packet: ask the delivery lead (or the user relaying them)
directly, record exactly what they said, and set `delivery_cosign` in the
figures block to match. Never infer it from a calendar invite, a Slack
emoji, or the absence of objection. If the answer is partial ("scope
reviewed, hours under review"), record the partial answer verbatim with
status `conditional` or `pending` and name who completes it and by when.
