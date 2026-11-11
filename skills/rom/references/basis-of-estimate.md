# Basis of estimate spec

The basis of estimate (BOE) is the table of footprint dimensions the estimate stands on. It
is what the client validates before deep scoping, and it is what protects the fee when the
footprint turns out bigger than assumed. Every row must survive a hostile read at the table.

## Row anatomy

Each BOE row carries five fields:

| Field | Rule |
|---|---|
| Dimension | A countable, confirmable aspect of the client's environment, specific to this deal |
| Current value | The number or state the estimate assumes, exactly as the source states it |
| Source | The quote field, scope item, transcript, or comparable engagement it came from, with a date |
| Confidence | Confirmed, Inferred, or Unknown, per the evidence-core register |
| Confirming phase | For Inferred and Unknown rows: the source-named phase in which the client confirms it |

The confirming phase is read from the quote timeline or playbook definition, never assumed.
If the source names its first validation phase "Analyze", the flag reads "confirm in
Analyze". If it names it "Discovery" or "Assess", use that. A ROM must never carry a phase
name its own source does not.

## The specificity bar

A BOE dimension names something a client stakeholder can count or confirm in a meeting.

| Fails the bar | Passes the bar |
|---|---|
| Number of integrations | Custom REST integrations from CPQ to the ERP requiring field mapping, currently 4 |
| Custom objects | Custom objects in CPQ carrying pricing rules that must migrate, currently 12 |
| Data volume | Active contract records to migrate with amendment history, currently ~18,000 |
| Users | Quote-creating users across two business units, currently 45 |

The test: could the client answer "is that number right?" without asking what you mean? If
not, the row is too vague to protect anything.

## Confidence mapping

Use the evidence-core register only: Confirmed, Inferred, Unknown. Older ROM drafts used
Confirmed, Estimated, Assumed. Translate on sight:

- Estimated maps to **Inferred**: a value derived from a comparable engagement or
  current-knowledge scoping. State the derivation in the row's source field.
- Assumed maps to **Unknown, flagged as an assumption**: the value depends on something the
  client has not confirmed. It gets the confirming-phase flag, and it also appears in the
  assumptions register with an ID, an owner, and the gate it blocks.

Never present an Unknown row as if it carried Confirmed weight. The confidence column is
what makes the range's width defensible.

## Volumetrics feed the SOW

BOE rows are the seed of the SOW's Exhibit A volumetric assumptions (owned by
sow-quality's Basis of Estimate framework). Write rows so they can be lifted into
Exhibit A without rework: dimension, assumed value, and what exceeding it triggers. Binary
scope additions that are Change Orders regardless of size do not belong in the BOE table;
they belong in the range reopeners section.
