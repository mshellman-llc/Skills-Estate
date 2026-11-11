# Journey Map Template (Aleysian)

Fillable journey map, service blueprint, source ledger, and opportunity map. Customize phases to the real experience. Every substantive claim carries a source. If an input does not capture something, write "not captured" rather than filling it.

---

## Map metadata

**Orientation:** [Client deliverable | Aleysian internal lifecycle]

**Persona / segment mapped:** [Specific. Not "users." Example: "Mid-market service managers renewing an existing support contract." Or for internal: "Enterprise prospect referred by partner, first AI advisory engagement."]

**Time horizon:** [Pre-purchase to first 90 days? Full lifetime? A single flow?]

**Map version:** [X.Y]

**Last updated:** [YYYY-MM-DD]

**Owner:** [Person or team]

**Source data:** [Transcripts, interviews, tickets, analytics, CRM records. List with counts, e.g., "9 discovery transcripts, 42 support tickets, Q3 funnel export."]

---

## Map structure (at a glance)

| Phase | Step | Touchpoint | Goal | Thoughts | Emotion | Pain points | Opportunities |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

---

## Phase 1: [Phase name]

### Step 1.1: [Step name]

**Touchpoint:** [Where. Name the real system / channel / agent: web or portal, email or marketing automation, sales rep, support case, chatbot or AI agent, offline conversation. Salesforce prompt if it applies: Experience Cloud portal, Marketing Cloud email, Sales Cloud rep, Service Cloud case, Agentforce agent.]

**Goal:** [What the user is trying to accomplish here]

**Thoughts:**
- "[Quote from a transcript where possible]" (source: [named source])
- "[Thought]" (source: [named source])

**Emotion:** [confused | hopeful | frustrated | curious | anxious | confident | ...]

**Emotional intensity:** [1 to 5, for the curve]

**Pain points:**
- [Specific pain] (source: [named source]; confidence: [high | medium | low | not captured])
- [Specific pain] (source: [named source])

**Opportunities:**
- [Specific improvement, config or build noted where known]

**Time at this step:** [Average and range, or "not captured"]

---

### Step 1.2: [Step name]
[Repeat structure]

---

## Phase 2: [Phase name]
[Repeat structure]

---

## [Continue with the phases that actually appear in the experience]

Phase presets to pull from. They are a starting point, not a mandate. Start from the real
experience and let the phases emerge; a preset that does not match the experience is a lie that
helps no one.

- **Most products:** Awareness -> Consideration -> Decision -> Onboarding -> Active use -> Renewal -> Advocacy
- **SaaS:** Trigger -> Discovery -> Evaluation -> Trial -> Onboarding -> Activation -> Habit -> Expansion -> Renewal -> Advocacy
- **Service business:** Awareness -> Inquiry -> Quote -> Decision -> Delivery -> Resolution -> Follow-up -> Repeat
- **CX engagement (client's customers):** Need -> Search -> Evaluate -> Buy -> Onboard -> Use / self-serve -> Get help -> Renew / expand -> Advocate  (name the real system or agent per touchpoint; on Salesforce, e.g., Sales Cloud at Buy, Service Cloud plus Agentforce at self-serve)
- **Aleysian internal lifecycle:** First touch -> Discovery -> Qualification / fit -> Scoping -> Proposal / SOW -> Kickoff -> Delivery -> Value shown -> Grow / expand -> Advocacy  (the "user" is the prospect and then the client; the back-stage is Aleysian's own method, artifacts, and the people who run each stage)

---

## Emotional curve

Plot intensity across the journey. The peaks (highest joy) and troughs (highest frustration) are the most strategic points.

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

Note the peaks and troughs and what causes each. These are where a fix or a delight moment pays off most.

---

## Service blueprint layers

For each phase, document the back-stage. Name real systems where known.

### Phase 1: [Phase name]

**Front-stage actions** (staff, in user view):
- [Action]

**Back-stage actions** (staff, out of view):
- [Action, e.g., manual case reassignment, approval, data cleanup]

**Supporting systems** (platform underneath):
- System of record / CRM: [what the client actually runs]
- Automation: [workflow / routing / validation rules]
- AI: [agents, models, or assistants in the loop]
- Data model: [key entities and relationships involved]
- Integrations: [middleware, external systems: billing, ERP, fulfillment]
- Salesforce prompt (only if it applies): clouds [Sales | Service | Marketing | Experience | Data]; Flows, assignment / validation rules; Agentforce / Einstein; MuleSoft

**Line-of-visibility issues** (back-stage failure surfacing as front-stage symptom):
- [Symptom the user feels] <- [Back-stage cause, e.g., no routing rule, stale integration, data-quality gap]

---

### Phase 2: [Phase name]
[Repeat]

---

## Source and confidence ledger

Every load-bearing claim on the map lands here. Builds traceability and lets a reviewer challenge any point.

| Claim | Phase / step | Source | Evidence | Confidence |
|---|---|---|---|---|
| [Pain at 2.1] | 2.1 | [9 of 9 discovery transcripts] | [Quote samples] | High |
| [Drop-off at 1.2] | 1.2 | [Funnel export] | [73% exit] | High |
| [Emotion at 3.1] | 3.1 | [Survey, 42 responses] | [Verbatims] | Medium |
| [Behavior at 4.1] | 4.1 | [not captured] | [none] | Not captured |

---

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

---

## Persona context (for reference)

**Persona:** [Name and one line]

**Context:**
- Role / job:
- Company size or segment:
- Platform maturity / estate (client maps): [systems in use, integrations, known debt; on Salesforce, orgs and clouds in use]
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

---

## Opportunity map (the output that drives decisions)

Effort and impact are labels, not prices. Anything that becomes a scoped, priced recommendation routes to the pricing / scoping path.

### Critical friction (fix soon)

| Friction | Phase / step | Evidence (source) | Recommended action | Effort | Owner |
|---|---|---|---|---|---|
| | | | | S/M/L | |

### Quick wins (low effort, real impact)

Often config, not build: routing rule, validation rule, workflow tweak, copy or layout fix.

| Opportunity | Phase / step | Recommended action | Effort | Impact |
|---|---|---|---|---|
| | | | S | M |

### Strategic bets (high effort, transformative)

| Opportunity | Phase / step | Recommended action | Effort | Impact |
|---|---|---|---|---|
| | | | L | H |

### Cross-team alignment opportunities

- [Issue, teams involved, recommended approach]

---

## Action plan

### Immediate (next 30 days)
- [ ] [Action] - [Owner]

### Near-term (60 to 90 days)
- [ ] [Action] - [Owner]

### Strategic (next 2 to 4 quarters)
- [ ] [Action] - [Owner]

---

## Re-mapping schedule

Maps decay. Re-map on:

- **Triggering events:** major product or platform launch, new segment, business-model change, drop in NPS or retention, a re-platform or large release.
- **Default cadence:** annual review, light quarterly updates.

---

## Workshop outputs

**Workshop 1: Validation**
- Date / attendees:
- Findings validated / disputed / newly surfaced:

**Workshop 2: Prioritization**
- Date / attendees:
- Top opportunities agreed / decisions made / open questions:

---

## Pre-ship checklist (client-facing maps)

- [ ] Every substantive claim has a source in the ledger
- [ ] "Not captured" used wherever an input is silent (no fabricated fill)
- [ ] Parity: all substance survived the render into the visual
- [ ] Visual inspected by a human or model
- [ ] Prose and voice pass run; no em dashes; plain language leads
- [ ] Aleysian brand applied (palette, type, logo, footers)
- [ ] No internal IDs, stage codes, or method jargon on the client surface
- [ ] Pricing left to the pricing path; map carries labeled effort and impact only

---

## Companion artifacts

- **Persona document.** The detailed persona this map represents.
- **Quote library.** Direct quotes organized by phase, sourced. Powerful in stakeholder readouts.
- **Service blueprint (full).** When the back-stage is deep, it earns its own document.
- **Opportunity backlog.** Every opportunity, labeled and queued for the delivery or scoping path.
