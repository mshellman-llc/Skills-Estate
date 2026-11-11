# Source authority for the handoff

By the time this skill runs the deal is closed-won and the paper trail is rich.
The first job is to mine the connected sources, not interview anyone. If you are
about to assert something, you should be able to point at where it came from.

## Search anchors

Establish these first and reuse them across every connector: the client and
account name, the opportunity name and ID, the SOW or engagement number, the
Q-number, the project record ID, and the key people's names and emails (pulled
from Salesforce first, so the other searches use the right spellings).

## The authority order

1. **The executed SOW.** Contract truth and the most authoritative source. Read
   scope, named exclusions, deliverables, acceptance methods, fee model, timeline
   and hard dates, and the assumptions the firm signed up to, verbatim. Not the
   draft, not the proposal: the signed one.
2. **The quote (Q-number).** The estimate behind the contract: capabilities,
   hours by role, team mix, price, margin. With the SOW, the only permitted
   source for contract figures (the money rule).
3. **Salesforce.** The deal system of record: account (domain, size, industry),
   opportunity (amount, close date, stage history, products, competitors),
   contact roles, the delivery or project record.
4. **Google Drive.** The thinking behind the deal: proposal and discovery decks,
   current-state maps, system and integration inventories, prior assessments.
5. **Slack and Gmail.** The unwritten current state: late changes, verbal
   commitments, access-blocker status, what the team already worries about. The
   primary hunting ground for section 07 promises.
6. **Calendar and call notes or transcripts.** Who met whom and what was said.
   Read transcripts verbatim, never summaries; the promise you need to flag lives
   in the exact words, and so does the attribution.
7. **Prior-engagement records.** Comparable past builds and the specific artifact
   to reuse (section 10).
8. **The AE, SSL, and CSE debrief. Last and narrow.** Only the tacit context no
   system holds: room dynamics, inter-functional politics, verbal promises that
   never reached writing, disambiguation of source conflicts. This context
   expires fast, so hold the debrief promptly, but never let it substitute for
   reading the record, and treat what it yields as Inferred until corroborated.

## Corroboration and conflict

- Record the named source and date for every claim; evidence-core governs the
  ledger format and confidence bands.
- Corroborate load-bearing claims (the outcome, scope boundaries, settled
  decisions) across two sources or mark them Inferred.
- **Recency versus authority.** Authority ranks as above, but recency can
  override on current state: a Slack thread from last week reopening a "settled"
  clause outranks the SOW on where things stand now. It never silently overrides
  the contract; show both, flag the conflict, and route it to the Pursuit Lead.
  The gap between what was signed and what was last said is exactly what a
  handoff exists to catch.
- An un-searched source is an Unknown, not a confirmed absence. "No off-contract
  promises found" is only a claim if it names what was searched.
- Worked examples and previously generated artifacts have zero evidentiary
  authority. A prior handoff for another client is a voice yardstick, never a
  content source; run the clone test before shipping.

## What feeds what

| Source | Primarily feeds |
|--------|-----------------|
| Executed SOW | 01, 04 (integration and migration clauses), 06, 08, scope list, figures, 12 (acceptance methods) |
| Quote | 01 contract baseline, figures, team roles |
| Salesforce | 01, 09, source_snapshot |
| Drive | 02, 03, 04, 05, 10 |
| Slack and Gmail | 06 (late changes), 07, 08, 09 |
| Calendar and transcripts | 07, 09, 11 (who can settle what) |
| Prior engagements | 10 |
| AE/CSE debrief | 07, 09 postures, conflict disambiguation |
