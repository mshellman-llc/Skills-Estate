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
| Confirmation action | For derived or unknown values, name the actual confirming action and phase when one exists. |

Use a phase from the project timeline when it exists. Without a timeline,
identify the discovery action needed or retain the confirmation step as
unresolved. A rough estimate does not require inventing an approved phase.

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

Basis rows can inform the selected contract's estimating assumptions. Preserve
the dimension and proposed value, with the effect of a change. Use the actual
contract profile for exhibit names and change-order rules. A rough estimate
does not create an obligation or establish when a change order is mandatory.
