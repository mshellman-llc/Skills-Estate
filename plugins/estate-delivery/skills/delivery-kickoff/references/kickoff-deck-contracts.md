# Kickoff deck content contracts

Two decks per engagement: internal kickoff (the team, before the client sees anything) and client
kickoff. Each has a waterfall and an agile variant; build the variant matching the SOW delivery
model, confirmed by a human, never assumed. This file is a content contract: what each slide must
carry. Deck mechanics belong elsewhere: deck-builder owns the stage-gated build process, pptx owns
the file format, estate-brand-renderer owns brand tokens and the visual and parity gates.
prose-pass gates every line of copy. Do not restate their rules here or anywhere.

Universal rules for both decks:

- Populated from the shared record and the handoff brief. A kickoff deck that could be reused on
  another client unchanged is the named failure mode: client name, scope language, stakeholders,
  and risks are this engagement's, not boilerplate.
- Any figure (fees, hours, dates) comes from the SOW; the deck renders, never authors.
- Headers carry the slide's point, not a label.
- Internal deck runs first, always. The team surfaces risks and gaps privately before the client
  sees any of them.

## Internal kickoff deck

Audience: the delivery team plus CSE. Job: the team walks out aligned on scope, roles, tools, and
the risks, before the client meeting. Required slides:

1. **The engagement in one slide.** Client, what was sold, why the client bought it, SOW id,
   delivery model, duration. From the handoff brief's company overview and sell-cycle context.
2. **Client context.** Who the client is, how they make money, who the stakeholders are, and the
   deal-cycle versus delivery mismatches the handoff flagged. Sourced; no unsourced claims.
3. **What was promised.** Sell-cycle commitments from the handoff brief, verbatim where possible.
   The team must know what the client heard, not only what the SOW says.
4. **Scope baseline.** In and out, from the charter's scope section. Same source stamp.
5. **Roles and RACI.** Who owns what, from the charter. Every team member sees their own name.
6. **Risk and gap review.** The seeded RAID items by ID, led by the Program Lead as a working
   conversation, not a read-through. This slide is why the internal kickoff exists: problems get
   surfaced here or they get surfaced by the client.
7. **Flagged deltas.** The F-### items: where client expectation and SOW differ, and who is
   resolving each before client kickoff.
8. **Tools and working agreements.** Where requirements, notes, and documents live (must be agreed
   in this meeting if not already), sandbox and access status (tracked truthfully: provisioned,
   requested, blocked), meeting cadence, definition of done for Sprint 0 or Mobilize tasks.
9. **The next two weeks.** Sprint 0 plan or mobilization plan, owner per item.

## Client kickoff deck

Audience: client sponsor, client team, Estate team. Job: shared understanding of scope,
plan, governance, and what Estate needs from the client, ending with explicit agreement on
cadence and the charter path to signature. Required slides:

1. **Why we are here.** The business outcome the client bought, in their language, from the
   sell-cycle context. Not Estate's methodology.
2. **Introductions and roles.** Both teams, with the RACI's accountable owners visible. The client
   sees who to call.
3. **Scope: what is in.** The SOW baseline, restated. Source-stamped internally even if the stamp
   is not rendered on the slide.
4. **Scope: what is out, and how change works.** Out-of-scope named plainly, plus the change
   control path. Framing rule: boundaries are the conditions under which the plan holds, not fine
   print. This slide makes the future Change Order conversation survivable.
5. **The plan.** Variant-specific, see below.
6. **Governance and cadence.** The ceremony table from the charter, presented as a proposal to
   agree in the room. Status reporting day, steering rhythm, escalation path, decision logging.
7. **What we need from you.** Client-side asks with dates: access grants, sandbox prerequisites,
   named decision-makers, data sources, resolve-by dates on the client-owned RAID items. Every ask
   traces to a RAID ID or a charter open item.
8. **Risks we are watching.** The client-safe subset of the RAID log. Honest but curated: items
   the client owns or must know, not the internal roster.
9. **Next steps.** Charter to signature (who signs, by when), Sprint 0 or Analyze start, first
   status report date.

## Variant differences (slide 5, The plan, plus rhythm slides)

**Waterfall variant.** The plan slide is the phase timeline: six stages, week ranges, exit gates,
and which gates the client co-signs. Emphasize gate criteria: the client should leave knowing that
Requirements and Design each end in a co-signature and what that commits them to. Demos appear at
stage boundaries.

**Agile variant.** The plan slide is the sprint structure: Sprint 0 scope, sprint length, demo
every two weeks, how the backlog is ordered and re-ordered, and what the client's product-owner
role is in each sprint. Keep the stage gates visible: agile here is adaptive scope inside a
phase-gated engagement, not the absence of gates. Add a backlog slide showing the seeded epics
from the scope baseline and how items move.

Do not mix variants to hedge. If the SOW is ambiguous about the model, that ambiguity is a flagged
delta and a human decision, not a hybrid deck.
