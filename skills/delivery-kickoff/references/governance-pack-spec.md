# Governance pack spec

Three artifacts, created once at Mobilize, stewarded for the rest of the engagement by
aleysian-delivery-status. This skill seeds them; it does not run them. Everything here exists so
that downstream stewardship is mechanical: stable IDs, fixed columns, append-only history.

Templates: `assets/raid-log-template.md`, `assets/decision-log-template.md`,
`assets/status-report-template.md`. Fill them; do not restructure them. A steward skill parsing
these files depends on the column sets staying put.

## Stable ID conventions (shared contract with aleysian-delivery-status)

- RAID log: `R-###` risks, `A-###` assumptions, `I-###` issues, `D-###` dependencies.
- Decision log: `DEC-###`. DEC rather than D, so decisions never collide with dependencies.
- Charter flagged deltas: `F-###`.
- Zero-padded to three digits, assigned in creation order within each type, starting at 001.
- IDs are permanent. Never renumber, never reuse, never delete a row. Closed items keep their row
  with Status set to Closed and Resolution filled. New items append at the bottom of their table.
- Cross-references use the bare ID (write "blocks R-003", not "risk number 3").

These conventions are load-bearing: the status skill diffs the tables week over week by ID. A
renumbered log breaks every downstream report.

## RAID log seeding rules

The RAID log starts populated, not empty. Seed from, in order:

1. **Handoff open questions.** Every open question in the accepted handoff brief becomes a RAID
   item. Classify honestly: a question about something that might hurt the project is a risk (R);
   a thing being treated as true without proof is an assumption (A); a problem already live is an
   issue (I); a thing waiting on someone else is a dependency (D). Carry over the owner and
   resolve-by date from the brief; where the brief left them blank, assign the owner now (default
   owner for unclassifiable items is the Program Lead) and set a resolve-by date, defaulting to
   before client kickoff. A handoff open question that vanishes instead of becoming an owned RAID
   item is the named failure mode of this stage.
2. **Handoff risks and gaps.** The brief's scope, risks, and gaps section maps to R items.
3. **SOW assumptions.** Volumetric and dependency assumptions in the SOW (Exhibit A, basis of
   estimate) become A items so their invalidation is noticed, not discovered.
4. **Charter flagged deltas.** Each F-### delta gets a companion R item if unresolved at seeding.
5. **Maturity-gap capabilities.** If the engagement touches a maturity-gap capability (CPQ and
   Billing amendments, ERP integrations, RCA migrations, DRO, UBB, CLM), seed an R item raising
   the oversight level, per the confidence tiers.

Every seeded item cites its source (handoff section, SOW clause, transcript id). Do not invent
risks to make the log look thorough; a padded RAID log trains the client to skim it.

## Decision log rules

Opened at Mobilize, usually near-empty. Log only decisions humans actually made, with the human
named. Legitimate day-one entries: the confirmed delivery model variant (made by whoever confirmed
it), the agreed note-keeping and document location, the cadence once the client accepts it at
kickoff. A decision nobody made yet is an open question in the RAID log, not a Proposed row here.

## Status report template rules

The template is a contract for the weekly report the status skill will produce. What matters at
creation time:

- Status colors always carry a one-line reason.
- Attention items reference RAID IDs; the report never restates the log, it points into it.
- Budget and burn figures come from the SOW and tracked actuals, never authored.
- Agree the reporting day and audience with the Program Lead and record both in the charter's
  cadence table.

## Where the pack lives

Before client kickoff the team must agree where requirements, notes, and these artifacts live
(the client folder, a Drive location, whatever the account uses). Record the location in the
charter's governance section and as a DEC entry once agreed. A governance pack nobody can find is
a governance pack that does not exist.
