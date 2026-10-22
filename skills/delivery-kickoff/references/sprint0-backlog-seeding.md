# Sprint 0 plan and backlog seeding rules

Sprint 0 is the mobilization sprint: the two weeks between charter drafting and real delivery
work. The economics of this stage are brutal: lost efficiency in weeks one and two costs roughly
110 percent effort to recover later, so Sprint 0 exists to make sure Analyze starts with nothing
missing. On a waterfall engagement the same content is the mobilization plan; the name changes,
the checklist does not.

## Sprint 0 plan contents

Every item has an owner and a date. Draw from this standard set, cut what the engagement does not
need, and add engagement-specific items from the RAID log:

1. Charter to signature (Program Lead secures; this skill only drafts).
2. Governance pack live and located where the team agreed documents live.
3. Sandbox and access setup **tracked to done**. Tracked, not performed: provisioning and access
   grants are human or system actions. This skill records status per environment and per person
   (provisioned, requested, blocked, verified) and flags blockers as RAID items. Never mark an
   environment ready that nobody verified; claiming unverified sandbox readiness is a named
   failure mode of this stage.
4. Handoff open questions resolved or converted to owned RAID items with dates.
5. Flagged deltas (F-###) dispositioned before client kickoff where possible.
6. Requirements sessions scheduled with the right client attendees (scheduling only; running them
   is estate-requirements-capture's job in Analyze).
7. Client research pack distributed to the team.
8. Both kickoffs held: internal first, then client.
9. Backlog seeded and, on agile engagements, ordered with the client product owner.

## Backlog seeding rules

The seed backlog is a projection of the scope baseline, nothing more. Rules:

- **One epic per SOW workstream**, carrying the workstream's SOW description and its
  `testable_against` acceptance method. Epic IDs: `E-###`, same conventions as the governance IDs
  (zero-padded, permanent, append-only).
- **First-level breakdown only.** Split an epic into stories only where the SOW or handoff brief
  gives real basis for the split (named integrations, named objects, named migrations, listed
  deliverables). Story IDs: `E-###-S-##` under their epic.
- **Never invent scope.** A story that does not trace to an SOW line or a handoff fact does not
  get seeded. Gaps the SOW leaves (unnamed integration counts, unspecified data volumes) become
  RAID assumptions or dependencies, not stories. Requirements capture in Analyze will grow the
  backlog; seeding is not requirements capture and must not preempt it, so no acceptance criteria
  authoring, no Gherkin, no sizing. Effort figures, if anyone asks, come from the SOW estimate;
  the backlog carries no hours this skill authored.
- **Every seeded item cites its source**: SOW clause or handoff section.
- **Order by dependency, then by gate.** Items blocking the Analyze gate float to the top.
  Migration and integration epics get an early discovery story, because those are where
  maturity-gap capabilities live.
- **Tag maturity-gap items.** Any epic touching CPQ and Billing amendments, ERP integrations, RCA
  migrations, DRO, UBB, or CLM is tagged for raised oversight, and gets a companion RAID risk.

Format: a markdown table per epic (ID, item, description, source, testable against, tags), so the
backlog can live beside the governance pack and be lifted into whatever tracker the team uses.
This skill does not own the tracker; it hands the team a correct seed.

## Client research pack

A short extension of the handoff brief's company overview for the delivery team: what the company
does, how it makes money, who the stakeholders are, what was promised, plus anything new since the
brief was written. Every claim sourced. Do not rebuild pursuit-grade research; if the team needs a
full prep pack for a specific meeting, that is estate-call-prep. This pack is a two-page read,
not a knowledge base.
