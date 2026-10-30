# Pursuit research and scoping methodology

How a pursuit goes from thin sales inputs to a defensible ROM inside an AI
Knowledge Hub. `init` copies this file into the hub root as `METHODOLOGY.md`.
The mechanical rules (frontmatter, claim tags, IDs, the ledger, commit rules)
live in `STANDARDS.md` and are assumed throughout. Use the hub's client, opportunity, and engagement records to keep account facts
separate from individual pursuits and delivery work.

## Why this shape

Partner-sourced enterprise deals arrive information-poor, sometimes on purpose.
Three consequences drive everything below:

1. Traceability is the product. With thin inputs a number defends itself only by
   the chain behind it: stated requirement, scope driver, assumption, price.
2. The bid is an audition. In a bakeoff the quality of the questions is scored
   alongside the number, so research artifacts double as proposal material.
3. Human attention is the scarce resource. Everything gatherable is delegated;
   everything decidable by evidence is decided by evidence.

## Roles

**Orchestrator.** One accountable agent or operator per pursuit. Plans the work, briefs
and gates the subagents, maintains `AGENTS.md` and `TODO.md`, owns all
synthesis, and is the only thing that commits. It never delegates synthesis,
gating, or anything touching bid strategy.

**Research subagents, when available and authorized.** One bounded topic
each. A single agent can perform the same research passes sequentially. Every brief names the exact output path, tells the agent to read
`STANDARDS.md` and the relevant inputs first, fixes the required structure, and
caps the return summary. Subagents write files directly; the orchestrator
verifies the file exists on disk and gates its content. A "done" report is not
evidence that work landed.

**Deal owner.** Provides the raw context and the strategic frame, edits the
standards at will (human edits are authoritative), sits the review gates, and
owns every client-facing decision.

## Where things live

The hub's records are the spine, one home per fact type. The working areas are
the layer where analysis happens; their content becomes canonical only through a
hub record.

| Pipeline artifact | Working area | Canonical hub record |
|---|---|---|
| Stated requirements, REQ ids, verbatim | `inputs/stated-requirements.md` | `opportunity.discovery` summarizes and points back |
| Deal origin, competitive frame, owner instructions | `inputs/deal-context.md` | `opportunity.qualification` |
| Raw call material | `inputs/transcripts/` | `transcripts.index` |
| Current-state systems, SYS ids | `research/current-state-architecture.md` | `client.technology` (account level, stored once) |
| Business model | `research/business-model.md` | `client.business_strategy` |
| Scope-driver universe, SD ids | `research/<domain>-scope-drivers.md` | `opportunity.solution_scope` carries the narrowed set |
| Our own assets, honestly | `research/our-assets.md` | `opportunity.solution_scope` |
| Requirements theory, fit-gap, seams analysis | `synthesis/` | `opportunity.solution_scope` carries the conclusions by id |
| Sources and claims, SRC and CLM ids | `evidence/` | `evidence.sources`, `evidence.claims` |
| Assumptions and decisions, ASM and DEC ids | ledger `register` events | readable rows in `opportunity.solution_scope`; for delivery, `engagement.control` |
| Run records, generated outputs | `deliverables/` | `deliverables.register` |

## The pipeline

### Phase 0: workspace before work

Run `init` for the client and the opportunity. It creates the hub root, the
index and pointer files, the standards, `TODO.md`, the opportunity front door
and working areas, and commits the skeleton. Minutes of cost; every later
artifact lands catalogued instead of needing cleanup.

### Phase 1: freeze the given context

Capture verbatim what was provided before generating anything: stated
requirements under REQ ids, deal origin, competitive dynamics, owner
instructions. Research contaminates memory; two weeks in nobody remembers whether
"they need SAP integration" was stated or inferred. Append a `source` event for
each input and a `claim` event for each load-bearing stated claim. Record what
the inputs conspicuously do not say; the silence list is where estimate risk
concentrates.

### Phase 2: bounded research passes

Research one topic per pass; delegate independent passes when authorized. The standing quartet: business
model, current-state architecture (the SYS inventory, unknowns included),
possible-universe scope drivers, and an honest inventory of our own assets. The
orchestrator gates each output on landing (claims tagged, citations live,
assumptions surfaced), appends ledger events for the load-bearing claims, runs
`check`, and commits per gated file.

### Phase 3: universe, then narrow

Enumerate the full universe of what the work might entail before deciding what
it does entail. Every candidate gets an SD id and a citation. Then narrow, in
writing, against the stated requirements, the business model, and the
assumption register. The universe list is never deleted; "here is everything we
evaluated and why these fifteen did not make the cut" is proof of rigour.

### Phase 4: seams, then assumptions

Place the solution in the client's architecture (SYS). Find every boundary where
it touches something we do not control: data masters, integration boundaries,
ownership boundaries, organizational boundaries. Scope risk concentrates at
seams. At each seam, write the assumption we are pricing against as an ASM
register event citing its SYS and CLM ids, with the if-false consequence, and
mark whether it must be communicated. An assumption held but not communicated is
a free option written to the client.

### Phase 5: synthesis at the top

The orchestrator, not a delegate, writes the requirements theory and the
fit-gap. Synthesis is where judgment concentrates and errors are most expensive.
The synthesis files cite ids and own no facts.

### Phase 6: human review gate

Deal owner and orchestrator walk the research, the synthesis, and the ASM rows
together before any pricing. Every ASM row is communicate or hold-back with a
reason. Nothing enters the pricing system until this gate passes.

### Phase 7: price the range, not the point

Scoping uses the confirmed pricing system or a versioned local estimate with
explicit formulas and source inputs. It produces a range whose
width is justified by named SD and ASM ids. The bid package includes the
clarifying questions the research surfaced. `evidence-core`'s finalization gate
runs on the projected ledger before any artifact ships.

### Pivot

When a late fact reframes the deal: append `supersede` events for the stale
claims, put section-precise supersession banners on the affected synthesis
files, rewrite them under the new frame, move the old thesis to the archive
table in `AGENTS.md`, and review the whole pivot as one git diff.

## Failure modes this exists to prevent

- The confident guess with no chain behind it (ids and tags everywhere).
- Research contaminating the record of what the client said (Phase 1 freeze).
- Scope drawn only from the list the partner chose to send (Phase 3 universe).
- Assumptions held in heads and discovered at delivery (Phase 4 register).
- Subagent output trusted without verification (gate on landing, verify on disk).
- The accelerator's demo assumptions priced as production-ready (honest asset
  inventory).
- The late reframe with no undo (git from Phase 0, commit at gates).
- Prior-generation vendor documentation priced as current capability (pin the
  product generation the bid targets; audit citations whose naming betrays an
  older era).
- A fabricated claim compounding through synthesis (ledger check at every gate
  commit, not only at finalization).
