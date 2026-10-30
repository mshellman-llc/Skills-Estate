# RAID and decision log stewardship

The two governance logs are the memory of the engagement. The status report is a projection of them; the logs are the record. These rules keep them trustworthy enough that a decision is written down once and never re-litigated.

## The stable ID convention

Seeded by `delivery-kickoff` at Mobilize. IDs are permanent for the life of the engagement.

| Prefix | Log | Meaning |
|--------|-----|---------|
| R-001 | RAID log | Risk |
| A-001 | RAID log | Assumption |
| I-001 | RAID log | Issue |
| D-001 | RAID log | Dependency |
| DEC-001 | Decision log | Decision |

- Three digits, zero-padded, sequential per prefix. The next risk after R-017 is R-018 even if R-005 was closed long ago.
- Never renumber, never reuse, never delete. A closed entry stays in the log with status Closed. An ID that once meant something must always mean that thing, because status reports, transcripts, and emails reference IDs and those references must never dangle.
- Decisions use DEC, not D, so decision references never collide with dependencies. This matches the log templates seeded by delivery-kickoff; the templates are the authority for the convention.

## RAID entry format

One entry per row or block, always carrying:

```
ID | Type | Item | Owner | Status | Resolve-by | Gate blocked | Source | History
```

- **Item**: one sentence, specific. "Client SSO team has not confirmed IdP metadata delivery" not "SSO risk".
- **Owner**: a role or named person. An unowned entry is not written; it goes back to the user as a question.
- **Status**: Open, Mitigating, Closed (risks/issues); Open, Validated, Invalidated (assumptions); Open, Delivered (dependencies).
- **Gate blocked**: which phase gate this blocks, or "none". This is what makes the log a planning tool instead of a worry list.
- **Source**: where the entry came from. A transcript quote with speaker and date (synthetic example: "Test coordinator, 2030-02-12 fixture meeting: 'the test environment is unavailable until the sample checklist is approved'"), an SOW clause, or a named person's statement. Every entry sourced, no exceptions.
- **History**: dated status lines appended over time. Corrections are new history lines, never edits to the original item text.

## Decision entry format

```
ID | Decision | Date | Made by | Rationale | Source | Status
```

- **Made by**: the human who decided. Agents and skills never appear here; they draft, humans decide.
- **Rationale**: one or two sentences on why, captured at the time. This is the field that prevents the decision from being reopened by someone who was not in the room.
- **Status**: Standing, or Superseded by DEC-0NN. A superseded decision is never deleted; the chain shows how thinking moved.

## Append-only discipline

- New information is a new entry or a new history line. Never rewrite an existing item to say something different from what it said when it was sourced.
- Closing needs a sourced basis: a quote, a delivered artifact, a signed gate. "It has not come up lately" is not closure. No source, stays open.
- When a meeting produces candidate entries, propose the batch to the user with sources before appending, when running interactively. On an unattended run, append with a clearly marked `proposed` status only if this destination and update are already authorized; otherwise return the proposed batch without writing. Say which occurred in the status report.

## What to extract from each transcript

Read the transcript verbatim and pull, with quotes and speakers:

1. Decisions made in the room (someone with authority chose between options).
2. New risks (a stated threat to scope, timeline, or budget).
3. New issues (a risk that has materialized).
4. New dependencies (the delivery team is waiting on someone, or someone on the delivery team).
5. Assumptions stated as fact ("we assume the data is clean" is A-0NN, not silence).
6. Action items with owners and dates. Unowned actions evaporate; push for an owner before logging.
7. Anything that smells like scope drift: route those to the scope-drift protocol, not just the logs.

A meeting that produced no entries is itself a finding: say so in the status report rather than leaving the reader to wonder whether the meeting was processed.
