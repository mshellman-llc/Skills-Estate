# Project Charter section spec

The charter is the Mobilize exit artifact. The client signs it; that signature is the gate into
Analyze. Everything below exists so the signature means something: the client is signing a
restatement of what they already bought, plus the operating rules for how the team will run.

Work from `assets/charter-template.md`. Fill content, do not restructure. Every section below is
always present. A section the sources cannot fill is filled with a known unknown carrying an owner,
a resolve-by date, and the gate it blocks, per the provenance rule. Never drop a section because
the SOW was silent on it.

`scripts/charter_check.py` enforces the checkable parts of this spec. Run it before any human
reads the draft.

## Required sections, in order

1. Engagement summary
2. Scope baseline
3. Delivery model
4. Team and allocations
5. RACI
6. Governance and cadence
7. Phase plan and milestones
8. Assumptions and open items
9. Sign-off

## Section rules

### Engagement summary

One paragraph plus the meta table. Business outcome first, platform second. Client name,
engagement name, SOW id, delivery model, start date, duration, commercial structure. Each row of
the meta table names its source. Commercial structure is fixed fee or T&M, exactly as the SOW
states it, never both.

### Scope baseline

The load-bearing section, and the one with the hardest rule: **scope is the SOW scope restated,
verbatim where the SOW language is usable, faithfully condensed where it is not. It is never
renegotiated, extended, softened, or "clarified" here.** The charter is where the client re-accepts
the boundary they signed; changing the boundary during restatement is how scope drift starts on
day one.

- The section opens with a source stamp on its own line: `Source: SOW <id>, as of <YYYY-MM-DD>`.
  The as-of date is the SOW signature date or the version date of the copy consulted. The gate
  script rejects a scope section without this stamp.
- In-scope items carry the SOW's own description and the acceptance method they are testable
  against (from the SOW or the handoff brief's `scope_baseline` with `testable_against`).
- The out-of-scope table restates the SOW's exclusions with clause references. An empty
  out-of-scope table on a real SOW is a red flag: go back and look.
- **Flagged deltas.** When the handoff brief, a transcript, or the client's own words show an
  expectation that differs from the SOW, that delta goes in the flagged-deltas table with F-###
  IDs: what was heard, what the SOW says, where it was heard, an owner (usually the Program Lead
  or Pursuit Lead), and a resolve-by date before client kickoff. A delta is never silently fixed
  in either direction: neither written into the baseline nor quietly dropped. If a delta implies
  paid work, the resolution path is a Change Order conversation owned by humans, not this skill.
- Any figures (fees, hours, rates) that appear anywhere in the charter come from the signed SOW or
  the quote it was rendered from. The charter authors no numbers.

### Delivery model

Names the variant, waterfall or agile, exactly as the SOW variant states it, plus who confirmed it
and when. Detection is from the SOW; confirmation is from a human. State what the model means
concretely for this engagement: acceptance rhythm, demo cadence, how scope change is handled.

### Team and allocations

Aleysian roles with named owners and allocations from the SOW estimate and the handoff brief, plus
client-side counterparts from the stakeholder map. A role with no named owner is an open item in
section 8, not a blank. Flag any deal-cycle versus delivery stakeholder mismatch the handoff brief
surfaced; a sponsor who was in the deal but is absent from delivery is a kickoff risk, not a detail.

### RACI

Activities as rows; Responsible, Accountable, Consulted, Informed as columns. Hard rules the gate
script enforces:

- Every cell filled. No blanks, no TBD.
- Exactly one Accountable per activity. Shared accountability is no accountability.
- Every role in the team table appears somewhere in the RACI. A role on the project that owns
  nothing in the RACI is either mis-staffed or the RACI is incomplete; both are findings.

Minimum activity set: project plan and schedule, requirements ownership, solution design,
build, testing, deployment and cutover, status reporting, decision escalation, change control.

### Governance and cadence

The ceremony table: what meets, how often, who owns it, who attends, what it produces. Cadence is
proposed by Aleysian and agreed at kickoff, never imposed; label it as proposed until the client
signs. Name where the governance artifacts live and the escalation path (Program Lead to CSE to
client sponsor).

### Phase plan and milestones

The six delivery stages with week ranges and exit gates, drawn from the SOW. Waterfall: phase
boundaries are gate dates. Agile: keep the stage gates and add the sprint cadence inside Build.
Dates derive from the SOW start date and duration; the charter does not invent a schedule the SOW
does not support.

### Assumptions and open items

The charter-level view of what the signature rests on. Every handoff open question that survives
to charter time appears here by its RAID ID (the RAID log is the working home; this section is the
snapshot the client signs against). Owner and resolve-by date on every row.

### Sign-off

Signature block for the client executive sponsor and the Aleysian CSE. The skill drafts the block
and leaves it empty. Securing the signature is the Program Lead's job. Never mark the charter
signed, and never record a signature that has not happened.

## Provenance

Every filled field ties to the SOW, the handoff brief, the shared record, or a named transcript.
Where aleysian-evidence-core is installed, run its ledger over the charter's load-bearing claims
before drafting; where it is not, state that and keep a manual source column, which the template
already carries.
