# Journey map template

This template has four parts to fill: the journey map, the service blueprint, the source ledger, and the opportunity map. Customize phases to the real experience. Every substantive claim carries a source or a hypothesis label. If an input does not capture something, write "not captured" rather than filling it.

## Map metadata

**Orientation:** [Client deliverable | Product role journey | Internal lifecycle]

**Actor / segment mapped:** [Specific. Not "users." Example: "Mid-market service managers renewing an existing support contract." For a product role: "Account executive working one pursuit." For an internal lifecycle: "Enterprise prospect referred by a partner, first advisory engagement."]

**Scope sentence:** [One actor, one journey, from a starting event to an ending event. Example: "One pursuit, from a lead landing to a recorded win or loss."]

**Time horizon:** [Pre-purchase to first 90 days? Full lifetime? A single flow?]

**State:** [Current state | Proposed future state]

**Evidence basis:** [Which layers are observed, reported, or hypothesis, in one or two sentences. Example: "Front-stage and back-stage are grounded in the built system. Thoughts, emotions, and pain are reasoned from the role and the system's failure modes, not from interviews. First map, to validate with real users."]

**Map version:** [X.Y]

**Last updated:** [YYYY-MM-DD]

**Owner:** [Person or team]

**Source data:** [Transcripts, interviews, tickets, analytics, CRM records, built-system review. List with counts, e.g., "9 discovery transcripts, 42 support tickets, Q3 funnel export."]

**Related maps:** [Other roles whose journeys share phases with this one, e.g., the specialist who receives a handoff at phase 07.]

## Map structure (at a glance)

| Phase | Step | Touchpoint | Goal | Thoughts | Emotion | Pain points | Opportunities |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

## Phase 1: [Phase name]

### Step 1.1: [Step name]

**Touchpoint:** [Where. Name the real system, channel, or agent: web or portal, email or marketing automation, chat workspace, sales rep, support case, chatbot or AI agent, offline conversation. Salesforce prompt if it applies: Experience Cloud portal, Marketing Cloud email, Sales Cloud rep, Service Cloud case, Agentforce agent.]

**Goal:** [What the actor is trying to accomplish here]

**Thoughts:**
- "[Quote from a transcript where possible]" (source: [named source])
- [Hypothesized thought, written as the likely thought and not attributed to anyone] (hypothesis; basis: [role constraint, system behavior, or failure mode])

**Emotion:** [confused | hopeful | frustrated | curious | anxious | confident | ...]

**Emotional intensity:** [Source-supplied score and scale, an explained hypothesis score, or "not captured". Preserve the qualitative emotion above even when no score exists.]

**Emotion evidence basis:** [observed | reported (source) | hypothesis (basis)]

**Pain points:**
- [Specific pain] (source: [named source]; confidence: [high | medium | low | hypothesis | not captured])
- [Specific pain] (source: [named source])

**Opportunities:**
- [Specific improvement, configuration or build noted where known]

**Time at this step:** [Average and range, or "not captured"]

### Step 1.2: [Step name]
[Repeat structure]

## Phase 2: [Phase name]
[Repeat structure]

## [Continue with the phases that actually appear in the experience]

Phase presets to pull from. They are a starting point, not a mandate. Start from the real experience and let the phases emerge; a preset that does not match the experience produces a map that describes nothing.

| Preset | Phases | Notes |
|---|---|---|
| Most products | Awareness -> Consideration -> Decision -> Onboarding -> Active use -> Renewal -> Advocacy | |
| SaaS | Trigger -> Discovery -> Evaluation -> Trial -> Onboarding -> Activation -> Habit -> Expansion -> Renewal -> Advocacy | |
| Service business | Awareness -> Inquiry -> Quote -> Decision -> Delivery -> Resolution -> Follow-up -> Repeat | |
| CX engagement (client's customers) | Need -> Search -> Evaluate -> Buy -> Onboard -> Use / self-serve -> Get help -> Renew / expand -> Advocate | Name the real system or agent per touchpoint. On Salesforce, that might be Sales Cloud at Buy and Service Cloud plus Agentforce at self-serve. |
| Consulting prospect-to-client lifecycle | First touch -> Discovery -> Qualification / fit -> Scoping -> Proposal / SOW -> Kickoff -> Delivery -> Value shown -> Grow / expand -> Advocacy | The actor is the prospect and then the client. The back-stage is the firm's own method and artifacts, plus the people who run each stage. |
| Product role journey (one unit of work through a tool) | Work arrives -> Frame quickly -> Assess -> Interpret -> Qualify or route -> Act -> Hand off -> Record the outcome -> Return for the next one | Example: a seller working one lead through a recommendation tool. The Return phase shows whether the tool earns trust for the next unit of work. |

## Emotional curve

Use a curve only when scores and their scale are supported or explicitly hypothesized. Define which end of the scale means a better experience; emotional intensity alone does not distinguish strong relief from strong frustration. Keep qualitative feelings at their steps when scores are not captured. Draw a hypothesized curve with a dashed line or a "hypothesis" label. The illustration below shows layout only, not participant data.

```
Emotion
intensity
   5 |
   4 |     *
   3 |   *   *     *
   2 | *       * *   *
   1 |           *     *
     +------------------------
       1.1  2.1  3.1  4.1
        Phase / Step
```

Describe changes in feelings with their sources. Do not infer a cause from the shape of a curve.

## Service blueprint layers

For each phase, document the back-stage. Name real systems where known. Front-stage and back-stage claims grounded in the built system are observed, even when the human layers are hypotheses.

Classify visibility from the mapped actor's perspective. The mapped actor's own actions belong in front-stage. Do not also list the same action as back-stage work. If the source does not establish visibility, keep the action and state that visibility is not captured; do not call it hidden.

Place the line of visibility between front-stage and back-stage actions, and the line of internal interaction between back-stage actions and supporting systems. Mark unknown support as "not captured"; do not infer absence from a blank.

### Phase 1: [Phase name]

**Front-stage actions** (staff or system, in the actor's view):
- [Action or visible output, e.g., an abstain message, a recommended play with its fit band]

**Back-stage actions** (staff or system, out of view):
- [Action, e.g., manual case reassignment, approval, data cleanup, a model or rules engine judging fit]

**Supporting systems** (platform underneath):
- System of record / CRM: [what the business actually runs]
- Automation: [workflow, routing, or validation rules]
- AI: [agents, models, or assistants in the loop]
- Data model: [key entities and relationships involved, including tables that should hold outcomes and do not]
- Integrations: [middleware, external systems: billing, ERP, fulfillment, chat]
- Salesforce prompt (only if it applies): which clouds [Sales | Service | Marketing | Experience | Data]; which Flows and rules; whether Agentforce or Einstein is in the loop; whether MuleSoft carries the integration

**Line-of-visibility issues** (back-stage failure surfacing as a front-stage symptom):
- [Symptom the actor feels] <- [Back-stage cause, e.g., no routing rule, stale integration, data-quality gap, outcome never written]

### Phase 2: [Phase name]
[Repeat]

## Source and confidence ledger

Every load-bearing claim on the map lands here. It builds traceability and lets a reviewer challenge any point.

| Claim | Phase / step | Source | Evidence | Confidence |
|---|---|---|---|---|
| [Pain at 2.1] | 2.1 | [9 of 9 discovery transcripts] | [Quote samples] | High |
| [Drop-off at 1.2] | 1.2 | [Funnel export] | [73% exit] | High |
| [Emotion at 3.1] | 3.1 | [Survey, 42 responses] | [Verbatims] | Medium |
| [Emotion at 4.1] | 4.1 | [Reasoned from the role and a system fact] | [e.g., 5 of 35 items published, from the catalog record] | Hypothesis |
| [Behavior at 5.1] | 5.1 | [not captured] | [none] | Not captured |

## Validation questions (required for hypothesis layers)

| Hypothesis | Phase / step | Question to ask | Whom to ask | Confirms or overturns |
|---|---|---|---|---|
| | | | | |

## Disconnects and gaps

The most valuable findings come from comparing the layers.

### Front-stage / back-stage disconnects

| Issue | Front-stage symptom | Back-stage cause (system) |
|---|---|---|
| | | |

### Internal belief vs user reality

| Internal belief | User reality | Gap |
|---|---|---|
| | | |

### Touchpoint / message inconsistencies

| Touchpoint A says | Touchpoint B says | Confusion result |
|---|---|---|
| | | |

## Persona context (for reference)

**Persona:** [Name and one line]

**Context:**
- Role / job:
- Company size or segment:
- Platform maturity / estate (client maps): [systems in use, integrations, known debt; on Salesforce, the orgs and clouds in use]
- Tech savviness:

**Goals:**
- [Primary]
- [Secondary]

**Frustrations:**
- [Frustration] (source: [named source])

**Behavior patterns:**
- [Pattern] (source: [named source])

**Quote that captures them:**
> "[Quote from a transcript]" (source: [named source])

## Opportunity map (the output that drives decisions)

Effort and impact are labels, not prices. Anything that becomes a scoped, priced recommendation routes to the scoping and pricing path.

### Critical friction (fix soon)

Use the captured feelings and operational evidence to identify friction. A curve is not required. Omit categories with no supported entries.

| Friction | Phase / step | Evidence (source) | Recommended action and timing | Expected outcome | Measure | Effort basis | Owner |
|---|---|---|---|---|---|---|---|
| | | | | | | S/M/L | |

For each action, explain how it changes the step and when it acts. Match the measure to that change. An acknowledgement sent after receipt can be tested for time to account confirmation; it cannot change whether the original request contained an account ID. Mark proposed owners, effort and outcomes as proposals.

### Quick wins (low effort, real impact)

Often configuration, not build: a routing rule, validation rule, workflow change, copy or layout fix.

| Opportunity | Phase / step | Recommended action | Dependencies | Effort | Impact |
|---|---|---|---|---|---|
| | | | | S | M |

### Strategic bets (high effort, high impact)

| Opportunity | Phase / step | Recommended action | Dependencies | Effort | Impact |
|---|---|---|---|---|---|
| | | | | L | H |

### Cross-team alignment opportunities

- [Issue, teams involved, recommended approach]

## Action plan

### Immediate (next 30 days)
- [ ] [Action] - [Owner]

### Near-term (60 to 90 days)
- [ ] [Action] - [Owner]

### Strategic (next 2 to 4 quarters)
- [ ] [Action] - [Owner]

## Re-mapping schedule

Maps decay. Re-map after a major product or platform launch, a new segment, a business-model change, a drop in NPS or retention, a re-platform or large release, or the first interviews that test a hypothesis map. Without a triggering event, review the map annually and update it lightly each quarter.

## Workshop outputs

**Workshop 1: Validation**
- Date / attendees:
- Findings validated / disputed / newly surfaced:
- Hypotheses confirmed / overturned:

**Workshop 2: Prioritization**
- Date / attendees:
- Top opportunities agreed / decisions made / open questions:

## Pre-ship checklist (client-facing maps)

- [ ] Every substantive claim has a source or a hypothesis label in the ledger
- [ ] "Not captured" used wherever an input is silent (no fabricated fill)
- [ ] Hypothesis layers are marked on the visual and the basis note is present
- [ ] Validation questions exist for every hypothesis
- [ ] Every captured feeling appears at the relevant step, including relief or other improvements
- [ ] Blueprint visibility uses the mapped actor's perspective
- [ ] Each proposed action can affect its measure at the point where it operates
- [ ] Parity: all substance survived the render into the visual
- [ ] Visual inspected by a person or a model
- [ ] Prose review run; plain language leads
- [ ] Confirmed brand profile applied, or the neutral profile with the substitution recorded
- [ ] No internal IDs, stage codes, or method jargon on the client surface
- [ ] Pricing left to the scoping and pricing path; the map carries labeled effort and impact only

## Companion artifacts

A persona document holds the detailed persona this map represents. A quote library organizes sourced quotes by phase for stakeholder readouts. A full service blueprint gets its own document when the back-stage is deep. Related role maps cover the roles that receive a handoff from this one and share phase IDs where the paths meet. An opportunity backlog holds every opportunity, labeled and queued for the delivery or scoping path.
