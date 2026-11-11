---
name: journey-mapping
description: 'Build customer journey maps and service blueprints the Aleysian way for AI advisory and consulting work: end-to-end experience across touchpoints, emotions, friction, and the systems underneath, every claim sourced and confidence-labeled. Stack-agnostic, with optional Salesforce prompts. Two jobs: a client-facing consulting deliverable mapping a client customer journey, or an internal map of the Aleysian prospect-to-client lifecycle. Triggers on customer journey, journey map, service blueprint, user journey, experience map, touchpoint analysis, friction map, CX blueprint, and when teams hold different mental models of an experience and need one shared, evidence-grounded view.'
---

# Aleysian Journey Mapping

> **Before writing: [`build-card.md`](../_shared/build-card.md) plus
> [`readout-brief.md`](../prose-pass/references/registers/readout-brief.md). Inputs, not a final pass.**

Build journey maps and service blueprints that surface friction, align stakeholders, and produce a prioritized set of decisions. This is the Aleysian cut of the discipline: platform-neutral back-stage layers, AI-touchpoint awareness, discovery-transcript inputs, and a source-and-confidence rule on every claim.

Stack-agnostic by default. The method does not assume any particular platform. Where an engagement runs on Salesforce, the back-stage and touchpoint sections carry optional Salesforce-specific prompts so you can name real components. On a non-Salesforce engagement, ignore those and name whatever stack is actually in play (HubSpot, a homegrown app, ServiceNow, Zendesk, a data warehouse, spreadsheets, whatever is true).

Two jobs, one method:

1. **Client deliverable.** Map a client's customer journey as a consulting artifact. The back-stage is whatever the client actually runs: CRM, data model, integrations, and any AI in the loop. This is client-facing, so brand canon applies before it ships (see "House rules" and "Shipping a client deliverable").
2. **Internal map.** Map Aleysian's own prospect-to-client lifecycle, the sell-to-deliver path from first touch through delivery and growth. Ties to the pipeline and the engagement stages Aleysian already runs.

This skill maps the whole experience and turns friction into a decision list. It is self-contained: it needs no other skill, script, or external file to run. Related work sits outside it, and if you happen to have those tools you can hand off to them, but none is required here: testing a single touchpoint is a usability test, upstream discovery is generative research, and conversion math on one funnel step is CRO.

---

## House rules (apply throughout, not as a post-pass)

- **Source every claim.** Each pain point, emotion, drop-off, and behavior traces to a named transcript, interview, ticket set, analytics query, or record. Carry the source inline. An unsourced claim is a defect.
- **Confidence, not confidence theater.** Facts (what a user did, what a system does, what a client said) degrade honestly. If the input does not capture it, write "not captured" rather than a plausible fill. Judgment (what the friction means, where the opportunity is) reasons forward like a principal, leads with the answer, states the basis once, and does not open with a disclaimer.
- **Plain language leads.** No jargon walls. Method labels, stage codes, and internal IDs never reach a client-facing surface.
- **No em dashes. Never use the section sign.** House voice throughout. Before anything ships, read it back and strip AI tells: buzzwords, filler, hedging openers, repetition-as-thoroughness. (If your house de-slop tooling is installed, run it; if not, the rule is right here and you do it by hand.)
- **One map per segment.** Merging the mid-market buyer and the enterprise buyer into one map produces a lie that helps no one. Split them.

---

## When to use

- Departments or workstreams hold different mental models of the same experience
- A client's CX feels disjointed across their systems and channels
- A specific friction or drop-off point needs a diagnosis, not a guess
- Strategic planning needs a shared, evidence-grounded view of the user
- Service design needs front-stage and back-stage aligned, including the CRM and integration layer
- A new feature, workflow, or AI agent needs to be designed in the context of the whole journey

## When NOT to use

- Testing one page or screen (that is a usability test)
- Generative discovery before any map exists (do that research first)
- Pure operational process mapping with no user in it
- Single-step funnel optimization (that is conversion analysis)

---

## Required inputs

- One named persona or segment to map. One map per segment.
- Evidence about that segment: discovery transcripts (Granola or equivalent), interviews, support tickets, survey data, product analytics, CRM records.
- Cross-functional access. You cannot map the back-stage without input from the people who run sales, service, ops, and the platform.
- Stakeholder time. A real journey map is an engagement, not an afternoon.

For an Aleysian internal map, the inputs are the pipeline, deal records, discovery and delivery transcripts, and the people who run each stage.

---

## The three deliverables

**1. Journey map, the user-facing view.** Eight lanes per step: phase, step, touchpoint, goal,
thoughts, emotion, pain point, opportunity. Let phases emerge from the real experience rather
than forcing a preset onto it. Name the real channel at each touchpoint. Thoughts should be a
real quote from a transcript where one exists, and every pain point carries its source.

**2. Service blueprint, the back-stage that makes it work.** Adds front-stage actions, back-stage
actions, supporting systems, and the two visibility lines. Platform-neutral: name whatever the
client actually runs. On a Salesforce engagement that means the specific cloud, flow, or agent; on
any other stack, name that stack.

The blueprint's whole point is to trace a front-stage symptom ("my case took a week") to its
back-stage cause ("no routing rule, so it sat unassigned"). Back-stage failures cluster at the
line of internal visibility: a broken automation, a stale integration, a data-quality gap that
surfaces as a customer-facing symptom.

**3. Opportunity map, the output that drives decisions.** The map and blueprint are inputs. This
is the deliverable that produces action: critical friction with evidence, quick wins (often
config rather than build), strategic bets, front-stage to back-stage disconnects, and the gaps
that need more than one team.

Effort and impact are labels here, not prices. Anything that becomes a scoped, priced
recommendation goes to the pricing and scoping path. This map does not invent numbers.

The fillable version of all three, with the lane tables, blueprint layers, source-and-confidence
ledger, and opportunity tables, is in `references/journey-map-template.md`.

---

## Phase presets

Five presets, for most products, SaaS, a service business, a CX engagement on the client's
customers, and Aleysian's own prospect-to-client lifecycle, are in
`references/journey-map-template.md`.

They are a starting point, not a mandate. Start from the real experience and let the phases
emerge. A preset forced onto an experience it does not fit produces a map that reads well and
describes nothing.

---

## Gathering the inputs

A credible map triangulates three views that usually disagree. The disagreements are findings.

**From users / clients**
- Discovery and interview transcripts. Walk them through a real, recent instance, not a hypothetical.
- Diary or over-time logs where the journey spans weeks.
- Surveys for scale, with the understanding that they trade depth for reach.

**From the business / platform**
- Internal interviews with sales, service, success, and ops. They each see a different slice.
- Operational data: funnel drop-off, ticket categories, NPS verbatims, churn reasons.
- System inventory: which touchpoints exist, which systems support them, where data flows and where it stalls.

**Cross-validate**
- What the user says happens
- What the data says happened
- What the internal team believes happens

Where they diverge, record the gap. It is often the most valuable thing on the map.

---

## Workflow

1. **Scope.** One persona, one journey, one timeframe. Write it down before mapping.
2. **Gather.** Transcripts, interviews, operational data, system inventory. Plan real time for this.
3. **Draft the spine.** Phases, steps, touchpoints. Get to a rough working draft fast, then iterate.
4. **Add the human layers.** Goals, thoughts, emotions, pain points, each with a source.
5. **Blueprint the back-stage.** Front-stage, back-stage, supporting systems, the two visibility lines. Name the real systems, whatever the stack.
6. **Find the opportunities.** Work from friction and disconnects, not from a wishlist.
7. **Validate with users.** Does this match their lived experience? Correct it.
8. **Workshop with stakeholders.** Walk the map. Build shared understanding and agree the top opportunities.
9. **Translate to action.** Named projects, owners, sequence. Scoped or priced items route to the pricing path.
10. **Maintain.** A journey map decays. Revisit on major change or on a set cadence.

---

## Failure patterns

- **Mapped from assumptions.** A map built without research reflects the team, not the user.
- **One map for every user.** Different buyers, different journeys. Do not merge.
- **No back-stage.** Symptoms with no causes. The common miss: the map never reaches the workflow or integration that actually broke.
- **Beautiful, inert.** Production value spent, no decision produced.
- **Filed, never reopened.** A map is a tool, not an artifact.
- **Emotion dropped.** The "what" with no "how it felt" misses the point.
- **Vague pain.** "Onboarding is frustrating" is not a finding. Which step, when, why, and where is the source.
- **Fabricated fill.** A plausible-sounding detail with no source is worse than "not captured."
- **Quick wins found, never shipped.** Same failure as research that never reaches production.

---

## Output format

Default outputs:

1. **Journey map** (a visual in the client's or team's tool, plus a markdown narrative version)
2. **Service blueprint** (same tool, or its own document when the back-stage is deep)
3. **Opportunity map** (markdown, prioritized)

The fillable markdown for all three, per-phase step blocks, blueprint layers, the source and
confidence ledger, and the opportunity tables, is in `references/journey-map-template.md`. Copy
it and fill it rather than rebuilding the structure each time.

---

## Shipping a client deliverable

When the map is client-facing, before it ships: confirm every substantive claim survived the render (parity), have a human or model inspect the rendered visual, do the de-slop read-back above, and apply the client's or Aleysian's brand (palette, type, logo, footers). Brand assets and pricing live outside this skill by design; if the engagement is priced, that stays with whoever owns the numbers, and the map carries labeled effort and impact, not dollar figures. None of this requires another skill to be installed.

---

## Reference files

- `references/journey-map-template.md`: the fillable journey map, service blueprint, source-and-confidence ledger, and opportunity map. Platform-neutral, with optional Salesforce prompts and both phase presets.

## Release gate (required)

Before you deliver, run the gate. This is a required step, not a suggestion, and
not something a reviewer does later. Full spec in
[`release-gate.md`](../_shared/release-gate.md).

1. Run prose-pass on the prose. It rewrites AI patterns and gates the result. For
   a final artifact it emits a receipt the quality gate requires.
2. Run brand-renderer on the branded artifact: palette, borders, radii, logo,
   footer.
3. Run quality-gate before you call it final.

Do not call the artifact finished until every applicable check passes.
