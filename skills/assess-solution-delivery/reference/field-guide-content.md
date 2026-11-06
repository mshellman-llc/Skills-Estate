# Content structure and discipline

A field guide is an internal, single-file, interactive brief that arms the pursuit
team to hold a room. It is never client-facing.

It is `field_guide` mode of this skill, built off the same governed graph as the
brief. Approval mode judges deliverability for a decision; field guide mode
prepares the seller: what the solution is, how it works, and how to answer the
person across the table who thinks they can build it themselves. Same evidence
gate, same claim governance, different reader.

## What makes one good (the bar)

The difference between a field guide that lands and one that reads like filler is
not polish. It is four things, learned the hard way:

1. **Derived from raw source, not summaries.** Mine the actual scope documents,
   estimators, transcripts, and records. Depth comes from committing to specific
   named mechanics (objects, native-vs-custom, real numbers), not generic
   diagrams. A spreadsheet of the client's own rate card is worth more than any
   restatement of it.
2. **An honest ledger.** State plainly where the platform does the work and where
   the team builds. Naming the custom rows before the client's builder finds them
   is what makes the native rows credible.
3. **Built for a named skeptic.** Write the objection section for a specific
   person (usually the client's in-house admin or architect). Prepared answers,
   each ending in a question that hands a dependency back to them.
4. **Contradictions surfaced, not smoothed.** When the scope says 90 days and the
   sponsor said 60, both go in the open-decisions register with the source. Gaps
   are flagged, never filled with a plausible guess.

## Section order (reference outline)

The reference build runs ten sections. Adapt to the pursuit, but keep the spine:
orient, ground in the business, show the mechanics, be honest about the build,
prepare for the skeptic, list what is unresolved, cite everything.

1. **Orientation** — who is in the room, who plans to build this, what the ask
   actually maps to (name the record/project). Frame the in-house build as the
   real competition if it is.
2. **The business model** — what the client sells and how they price it, grounded
   in a source. This usually reframes the whole engagement.
3. **The flow / deliverables** — the staged process, ideally as the clickable flow
   widget. What happens at each stage, in plain language.
4. **The build ledger** — native / configured / custom / dependency, as the
   filterable ledger widget. The honest accounting.
5. **The mechanics, concretely** — how the hard part actually gets built. Name
   objects and patterns. Use the flat/structured toggle if there is a before/after.
6. **A key decision** — a real fork the team must carry a recommendation into
   (a tool choice, a boundary). Give the option table and the recommendation.
7. **Systems and dependencies** — the integration surface and what the client must
   provide. Correct any "customer responsibilities: none" fiction.
8. **The skeptic brief** — the in-house-build objections, prepared answers, and the
   dependency ask after each. Use the pricing resolver here if pricing is a fault
   line.
9. **Open decisions** — every unresolved delta, sourced, with a named decider.
10. **Sources** — where every claim comes from. Mark proposed architecture as the
    team's recommendation, not client statements.

## Voice

Apply `review-writing` to the prose before shipping; it is a hard gate. In practice:

- Do not photocopy another guide's headings or rhetorical moves. Borrowed cadence
  is itself the machine tell. Write the headings for *this* pursuit.
- Vary sentence length. Break balanced "X, and Y" two-clause sentences into uneven
  lengths. Cut antithesis ("not X, but Y"), negation openers, and strings of
  aphoristic one-line closers.
- Lead with the finding. No windup, no meta-signposting ("in this section we").
- Zero em dashes, always. Verify with grep after every edit.

## Money and gaps

Nothing in the guide is priced by the guide. Pricing authority is the confirmed scoping
system or supplied quote source. The pricing resolver demonstrates the client's own model against
their own rate card; it is a teaching tool, not a quote. Do not invent list
prices, dates, owners, or volumes. If a number is unknown, it goes in the
open-decisions register as unknown, never as a placeholder.

Do not print gap-flags or "[TBD]" markers in the artifact itself. Surface gaps to
the seller in chat; the shipped guide reads clean.
