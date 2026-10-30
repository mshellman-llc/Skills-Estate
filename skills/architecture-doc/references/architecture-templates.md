# Architecture templates

Fillable skeletons for the two altitudes, the source-line convention, the systems-map and trade-offs patterns, the HTML build pattern, and the pre-ship checklist. Customize the sections to the real system. Every substantive factual claim carries a source locator. Raise missing evidence with the user. Retain an unresolved condition in the reference when readers need it for a decision; never invent a fact.

---

## Document metadata (both altitudes)

**Altitude:** [Architecture doc | System design]

**System or product:** [Name]

**Authoritative source:** [The decisions record, brief, or spec that governs. Name it. State precedence: what wins when sources disagree.]

**Fallback sources:** [Brief, stand-up plan, notes, for anything the authoritative source is silent on.]

**Status:** [Design for review | Proposal | Confirmed]

**Rev:** [YYYY-MM-DD]

**Owner / build lead:** [Person]

---

## Source-line convention

Carry a source line at the end of each section, or on each claim where sections mix sources.

- From a named document: `Source: executive brief, section 3.`
- From the authoritative decisions record: `Source: architecture decisions, section 2.`
- A design proposal you are making: `Source: design proposal, consistent with [named source].`

An unsourced fact is a defect. A design proposal is sourced to itself and carries its trade-off.

---

## Architecture doc skeleton (the what and why)

### Hero
- Kicker: `[System] · [one-line category]`
- Title: `[System] architecture`
- Lead: [One or two sentences. What it is, in plain terms.]
- Metadata row: Owner, Status, Stack, and one more that fits (Shape, Scope, Access).

### Overview
- What it is. [One paragraph.]
- The problem it closes. [What the status quo cannot do.] `Source: ...`
- How to read the set. [Which document carries the what/why, which carries the engineering, which is authoritative.]

### Product shape
- The core action. [The single thing a user does.]
- The surfaces or entry points. [Table: surface, what it does, identity.]
- Audience or access levels. [Table: level, who may act or view.] `Source: ...`

### Architecture at a glance
- Systems map. [A diagram. See the systems-map pattern below.]
- Two kinds of change. [A code change versus a data or content change, and why that split matters.]
- Point to the system design for the data model, the API, and the credential. `Source: ...`

### Security posture
- The controls as the shape of the system, at posture altitude. [List, one control per line.] `Source: ...`

### Cost and ownership
- Run-cost envelope. [Table: piece, first environment, fuller environment. Cite the rate sources.]
- People time. [Hours per period.]
- Ownership. [Named owner and backup, no lock-in, runbook.] `Source: ...`

### Stand-up or build
- The ordered steps. [Table: number, step, the check that proves it.]
- The long pole, if any. `Source: ...`

### Jobs to be done
- [One job per line: what the system is hired to do, plainly.]

### Growth
- The additive order. [Numbered: what comes next, in order.] `Source: ...`

### Risks
- [Table: risk, mitigation that is already in the design.]
- Roles. [The product roles, and the build roles if they differ.] `Source: ...`

### Footer
- Revision, sources and date. Add a mark or brandline only when the selected profile calls for one.

---

## System design skeleton (the engineering how)

### Hero
- Kicker: `[System] · [category]`
- Title: `[System] system design`
- Lead: [What this design is for.]
- Metadata row.

### Overview
- What governs it. [Name the authoritative source and the precedence.]
- How to read it. [Requirements are sourced; design choices are proposals with trade-offs.]

### Requirements
- Functional. [Table: requirement, what it means for the build, source.]
- Non-functional. [Table: dimension, target, source. Scale, latency, availability, cost, security.]
- Constraints. [Table: constraint, effect on the design, source.]

### High-level design
- Components and how they speak. [Systems-map diagram.]
- Data flows. [The main flows, for example publish and serve.]
- Storage split. [What lives in the database versus object storage.] `Source: ...`

### Identity and authorization
- Principal and authorization key. [Identity, tenant or isolation key where relevant.]
- Access matrix. [Who may perform each action, where authorization is enforced, and what denial returns.] `Source: ...`

### Data model
- Tables and an illustrative schema. [See the schema-block pattern below.]
- The enforcement model. [For example row-level security, and what its failure mode is.] `Source: ...`

### API
- The surface. [Table: endpoint, purpose, notes.]
- The main contract. [One request and response example.]
- Idempotency and retry. [How a repeated call resolves.] `Source: ...`

### Credential and serving
- The request path. [Ordered requests, responses and state changes for the actual interaction. Include credential handling and failure branches; do not assume one universal sequence.]
- The security order and the transaction boundary. [What is atomic, what fails closed.]
- Error behavior. [What a denied, expired, or unknown request returns, and why.] `Source: ...`

### Records and cascade
- The versioning and pointer model. [How a change propagates.]
- What it commits to. [State the architectural commitment plainly, and what it rules out.] `Source: ...`

### Governance and audit
- Attribution, retention, and export. [Table or list.] `Source: ...`

### Scale and reliability
- Load, scaling posture, failover, monitoring. [Table: concern, posture.] `Source: ...`

### Trade-offs
- [Table: decision, choice, why, and what it traded and when to revisit. One row per real decision.]
- What to revisit as it grows. [A short list.]

### Footer
- Revision and source references; profile-specific assets only when required.

---

## Systems-map pattern

Draw a directed systems map using the selected renderer and project profile. Label every relationship with its operation or data, identify trust and ownership boundaries, and distinguish proposed flows from confirmed behavior. A sequence shows ordered requests, responses, state changes and failure branches. Existing diagram classes (`.diagram`, `.drow`, `.dbox`, `.dseam`, `.dcap`) may be reused when available. One row per layer, seams for the connectors, a caption that carries the source. Keep boxes to a title and one line. Example layers for a hosted app:

```
row 1:  [source and deploy]  --deploy on push-->  [the app, dark box]
row 2:  [entry origin]  --one hard split-->  [serving origin, accent box]
row 3:  [datastore]   [render or compute]   [identity]
caption: the two-kinds-of-change note, plus the source line.
```

Use the selected profile’s borders and palette, and provide labels that remain understandable without color.

---

## Schema-block pattern

Present an illustrative schema in a readable monospace block using the selected profile. Check contrast for code and comments. Keep it illustrative, not exhaustive.

```
-- every table carries [the isolation key]. the enforcement keys on it.
table_a   (id pk, [isolation key] fk, ...)   -- one-line note
table_b   (id pk, [isolation key] fk, ...)   -- immutable, or append-only, note the invariant
```

State the enforcement model in prose after the block: what the database refuses, and what the failure mode of a bad deploy is.

---

## Trade-offs table pattern

| Decision | Choice | Why | Traded, and revisit when |
|---|---|---|---|
| [Axis] | [The call] | [The reason] | [What it gave up, and the trigger to revisit] |

Every real decision gets a row. The point is that each choice names what it gave up.

---

## HTML build pattern

1. Build the document with the selected profile's stylesheet and available assets. A neutral profile requires no logo placeholders.
2. If a template uses placeholders, inject only the selected profile's declared values and reject unresolved placeholders.
3. Run the configured brand and prose checks. Review findings in context and preserve required technical meaning.
4. Render and inspect the output. Compare every diagram, table, source locator and substantive claim with the editable source.

Supplemental styles for code blocks and labels use the selected profile. Inspect readable contrast and layout in the requested export format.

---

## Pre-ship checklist

- [ ] Every substantive claim has a source line.
- [ ] Missing evidence and decisions are reported to the user; the reference retains conditions its readers need.
- [ ] Superseded framing removed, not annotated. The authoritative source's precedence is honored.
- [ ] Design proposals are framed as proposals, each with its trade-off. Genuine forks defaulted in the doc and flagged in chat.
- [ ] Brand gate: `PASS: 0 failure(s)`.
- [ ] Prose and interface labels reviewed; applicable diagnostic findings resolved without changing the meaning.
- [ ] Parity: all substance survived the render. A human or model looked at it.
- [ ] The confirmed author voice and selected project profile apply; no unrelated brand or personal voice remains.
- [ ] Numbers cascaded to the rest of the set.
