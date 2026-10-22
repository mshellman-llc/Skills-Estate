# Architecture templates (Estate)

Fillable skeletons for the two altitudes, the source-line convention, the systems-map and trade-offs patterns, the HTML build pattern, and the pre-ship checklist. Customize the sections to the real system. Every substantive claim carries a source line. If a source does not cover something, it is a gap: raise it with the operator in chat, do not fill it here.

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
- Color mark, brandline, rev line naming the sources and the date.

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
- The authorization key. [What the system keys on.]
- Access or audience levels. [Table.] `Source: ...`

### Data model
- Tables and an illustrative schema. [See the schema-block pattern below.]
- The enforcement model. [For example row-level security, and what its failure mode is.] `Source: ...`

### API
- The surface. [Table: endpoint, purpose, notes.]
- The main contract. [One request and response example.]
- Idempotency and retry. [How a repeated call resolves.] `Source: ...`

### Credential and serving
- The request path. [The fixed order: decide, serve, log.]
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
- Color mark, brandline, rev line.

---

## Systems-map pattern

Draw the map inline with the Estate diagram classes (`.diagram`, `.drow`, `.dbox`, `.dseam`, `.dcap`). One row per layer, seams for the connectors, a caption that carries the source. Keep boxes to a title and one line. Example layers for a hosted app:

```
row 1:  [source and deploy]  --deploy on push-->  [the app, dark box]
row 2:  [entry origin]  --one hard split-->  [serving origin, accent box]
row 3:  [datastore]   [render or compute]   [identity]
caption: the two-kinds-of-change note, plus the source line.
```

Do not use color-coded left borders. Use full 1px borders and the token palette.

---

## Schema-block pattern

Present an illustrative schema in a monospace block styled with the token palette (frost background, 1px border, 8px radius, muted comments, teal table names). Keep it illustrative, not exhaustive.

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

1. Author the body HTML with three placeholders: `{{STYLE}}` in the head, `{{LOGO_WHITE_B64}}` in the hero, `{{MARK_COLOR_B64}}` in the footer.
2. Inject the Estate stylesheet (from `_shared/estate-brand`) into `{{STYLE}}`, and the two logos as `data:image/png;base64,<contents>` into the logo placeholders.
3. Assert no `{{` remains.
4. Run the gates. Fix a C1 balanced-clause fail by splitting the true two-clause sentences ("X, so Y") into sentences of unequal length. Leave the serial-comma lists, which also match the pattern but are correct.
5. Render and inspect. Confirm parity.

Supplemental styles (code blocks, pill labels) stay on the token palette: frost or white backgrounds, 1px token borders, radii of 4px or 8px, teal as the one accent.

---

## Pre-ship checklist

- [ ] Every substantive claim has a source line.
- [ ] No gap-flags, no "TBD", no "to confirm" in the document. Gaps raised with the operator in chat instead.
- [ ] Superseded framing removed, not annotated. The authoritative source's precedence is honored.
- [ ] Design proposals are framed as proposals, each with its trade-off. Genuine forks defaulted in the doc and flagged in chat.
- [ ] Brand gate: `PASS: 0 failure(s)`.
- [ ] Prose gate (documents only): exit 0. C1 balanced-clause sentences split where they were true two-clause joins.
- [ ] Parity: all substance survived the render. A human or model looked at it.
- [ ] House voice: no em dashes, no en-dash ranges, no section sign, no emoji, no forbidden words, sentence case, digits.
- [ ] Numbers cascaded to the rest of the set.
