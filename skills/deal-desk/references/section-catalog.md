# Deal Desk readout: section catalog

Built from the Deal Desk Readout Template (artifact 10 of the playbook suite,
read 2026-08-11). Every section below is always present in the packet. A
section the evidence cannot fill is not dropped; it is filled with a named
unknown carrying an owner, a resolve-by date, and the gate it blocks.

Field source tags, from the template, used throughout:

- **DS**, deal specific: AE or SSL enters it for this deal.
- **SE**, scoping engine: auto-populated from the quote via the scoping MCP.
  Never retyped from memory, never reconstructed.
- **CA**, calculated: computed by this skill and printed with the computation.
  Never entered manually.
- **PS**, playbook static: pre-filled from the playbook; do not change.

## Header and snapshot

| Element | Source | The bar |
|---|---|---|
| Deal / opportunity, stage, submitted by, date | DS | A reviewer knows in five seconds what they are approving |
| Six snap cards: total program value, phase price (this desk), margin %, phase count, confidence level, competitor | SE + DS | Margin % is one of the six cards and the visually dominant figure. Competitor blank means uncontested, say so |
| Tagline | DS | Two to three sentences: what the client needs, why this deal, what is at stake. No AI vocabulary |

## Sales context

One table, ten rows, all DS: stage, source, first conversation, scoping call
(date plus summary), ROMs shown (investment figure plus client reaction for
each), buying signal (observed, not interpreted), trigger event, decision
criteria stated, decision criteria inferred (labeled as the AE/SSL read),
hard deadline, last touch. Stated and inferred criteria are separate rows on
purpose; never merge them.

## Stakeholders

Two tables, client side and Aleysian side: name, role or title, maturity tag,
notes. Follow with one or two DS sentences on client-side dynamics and
decision-making context. Postures come from transcripts or CRM, cited; a
posture with no source is an inference and is labeled as one.

## Win strategy

Four DS rows: our wedge (specific, not generic), risk to winning, competitive
posture against the named competitor, exec presence needed at proposal or
close.

## Scope and solution

- **Scope summary table**: phase, workstream (DS) against duration, hours,
  price (SE), with a program total row (SE).
- **In scope / out of scope bullets** (DS): specific to the confirmed DDOC
  option; out-of-scope names what was explicitly excluded in the DDOC session.
- **Assumptions table**, minimum five rows: area, present-tense assumption,
  "if broken" consequence. Every "if broken" cell names a number or a named
  change order trigger. Vague language is a defect.
- **Risks and mitigation**: severity, risk with a specific failure mode,
  mitigation (what Aleysian has already done or committed to, not
  aspiration), owner as a named individual, not a role.
- **Methodology**: approach, sprint length, cadence, deployments, why this
  approach, change order mechanism, reference engagements, risk to
  methodology. Mostly PS with DS deviations noted.

## Economics

- **Pricing and staffing table**: role, allocation, weeks, hours, rate,
  subtotal, with totals. Hours and rates are SE from the quote's pricing
  sheet; subtotals and totals are CA. Six standard rows (AE, PM, SA, TA, BA,
  DEV); add rate-card roles as the deal needs. All figures monospace.
- **Pricing model rationale** (DS): why T&M or fixed fee, never both.
- **Sensitivity analysis**: three to four scenarios, each with a quantified
  dollar impact. "Scope grows" is not a scenario; "a fourth integration adds
  roughly 120 DEV hours, $27,000 at rate" is.
- **Staffing plan**: allocation per role across engagement weeks (a Gantt in
  the HTML rendering), plus a continuity note on whether the team rolls into
  the next phase.
- **Margin analysis**: revenue, internal cost, gross margin, all recomputed
  and printed, rendered against the margin floor (gauge in HTML, table in
  print). See `margin-approval-routing.md` for the floor and the ladder.
- **Levers**: real options only, each with a dollar or percent impact,
  followed by a one-sentence recommendation: hold pricing or pull a named
  lever, position stated directly.

## Approval

See `asks-and-decisions-log.md` for the full formats.

- **Asks**: two to six, every ask carries a recommendation.
- **Decisions log**: filled live during the meeting.
- **Action items**: action, named owner, due date.
- **Sign-off**: Deal Desk reviewer (approved / not approved), AE
  (acknowledged), delivery lead (deliverable confirmed). The delivery lead
  row is the cosign; it is human input, never inferred.

## The figures block

Every packet embeds the machine-readable `deal-desk-figures` block the gate
script verifies (schema in `margin-approval-routing.md`). In markdown it is a
fenced code block tagged `deal-desk-figures`; in HTML it is a comment opening
with `deal-desk-figures`. The block duplicates no prose; it is the checkable
spine the prose is rendered from.

## What is out of this catalog

Post-Deal-Desk change detection (a material scope or margin change after
approval requiring re-alignment before the SOW is final) belongs to deal
governance, not this packet. Flag it as a known gap in the packet's risks
when relevant; do not build it here.
