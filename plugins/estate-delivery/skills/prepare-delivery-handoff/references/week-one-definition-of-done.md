# Sections 11 and 12: week one and the definition of done

These two sections are why the handoff exists. A handoff that transfers facts but
not a plan for the first week leaves the incoming team to do the synthesis in the
kickoff room. Never cut them, never thin them to placeholders, and at moment
`brief` never satisfy them with gaps alone.

The economics behind the rule: a weak start compounds. Inefficiency in the first
two weeks of a project is the most expensive inefficiency there is, and a project
typically has about 30 contractual days of runway but only about two usable weeks
before the drift begins.

## Section 11: the week-one discovery agenda

Built directly from the ledger, not brainstormed. The construction rule:

1. Take every Unknown and every load-bearing Inferred claim from the evidence
   ledger, plus every gap entry in sections 01 through 10.
2. Cluster them into sessions. A session is the unit of work: one room, one
   owner, one concrete output.
3. Order the sessions by risk: what, if wrong, invalidates the most downstream
   work goes first.
4. Anything that cannot be a week-one session stays a gap with its owner and
   resolve-by date, and says why it waits.

Each session card carries:

- **Name**: what is being validated, not a meeting title. "Confirm the material
  master schema against the migration assumption" beats "Data workshop".
- **Owner**: one named person or role accountable for the output existing.
- **Attendees**: the people who can actually settle the question, client side
  included. If the needed person is not in the delivery stakeholder list, that is
  a section 09 mismatch and gets flagged there too.
- **Output**: the concrete thing that closes the question. A confirmed schema, a
  signed-off inventory, an access grant verified by login. "Alignment" is not an
  output.
- **Closes**: the gap or claim ID it resolves, so the manifest can be updated
  mechanically after the session.

The depth test: read section 11 against the ledger. Every Unknown either maps to
a session or is a named gap explaining why it waits. A session that closes
nothing is padding; an Unknown that maps to nothing is a dropped liability.

## Section 12: what good looks like

Two parts: the readiness checklist (can we start) and the definition of done
(how we will know we succeeded).

### The readiness checklist

Binary items, each with a status of ready, blocked, or unknown, and an owner who
clears it. The standing set; extend per deal, do not shrink:

- Executed SOW and quote in hand, figures reconciled against section 01.
- Delivery team named and allocated (roles, not just names).
- Client-side owner identified for every system delivery must touch (from
  section 04).
- Sandbox or environment access requested, with grant status per system.
- Every off-contract promise from section 07 dispositioned: honored, priced, or
  reset with the client.
- Deal-versus-delivery stakeholder mismatches from section 09 each have a
  resolution path.
- Kickoff scheduled with the people section 09 says must be in the room.
- All maturity-gap flags acknowledged by the delivery leads.

An item that is blocked or unknown does not fail the handoff; hiding it does. The
gate requires the checklist to exist and every item to carry a status and an
owner; the humans decide whether to start anyway.

### The definition of done

Every criterion:

- **Is observable.** A behavior or state someone can watch happen. "The team is
  confident" is not observable; "a quote for a configured bundle reaches an
  approved state without a spreadsheet touch" is.
- **Carries a binary test.** The sentence a reviewer uses to answer yes or no.
- **Ladders to the success spine.** Each criterion supports the one outcome
  stated in section 01. A criterion that supports nothing is scope creep wearing
  a checklist costume.

Group criteria by workstream when the engagement has more than one. Where the SOW
defines acceptance methods per deliverable, the criteria quote them rather than
inventing parallel ones; a definition of done that diverges from the contract's
acceptance language is a conflict to surface, not an improvement to make
silently.
