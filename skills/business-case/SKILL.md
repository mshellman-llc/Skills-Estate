---
name: business-case
description: 'Authors and gates the Estate executive business case, the artifact for the approver who funds the deal: should we invest, why now, and what exactly is being asked. Argues the case for and against the investment honestly, prices the cost of waiting in shown arithmetic, and bounds the ask so no approval is a blank check. Use when asked for a business case, investment case, exec case, value case, cost-benefit, "the case for", "why now memo", "should we fund this", "help me get the CFO to yes", or when a pursuit needs the document the economic buyer reads before signing off. Trigger on any client name or Q-number paired with "business case" or "funding". Do NOT use for the deal decision deck (that is estate-ddoc), the priced clickable proposal (that is estate-interactive-proposal), the internal margin gate (that is the Deal Desk readout under estate-evidence-core''s deal_desk contract), or prospect research (that is estate-call-prep).'
---


# Estate business case

> **Before writing: the shared build card (`../_shared/build-card.md`, where the
> estate mounts it) plus the prose-pass register
> `../prose-pass/references/registers/readout-brief.md`. Inputs, not a final pass.**

The business case is the document that gets someone to say yes and fund it. It
lands a recommendation and then earns it: benefits each tied to a pain the
client named, risks each with a severity and a real mitigation, the cost of
doing nothing in arithmetic, and an ask bounded by what is priced and what
still has to be decided.

The governing idea: **the case against is what makes the case for credible.**
A document that only lists upside is a sales pitch, and an approver who has
signed budget before discounts it on sight. An honest case names what the
skeptic in the room would say, then answers it or concedes it. The strongest
line in a business case is often the one that concedes the downside and holds
anyway.

## Phase 0: run the evidence core, and stop if it says stop

This artifact makes load-bearing factual claims, so `estate-evidence-core`
runs first. Build the ledger there, then validate against the `business_case`
contract:

```bash
python3 ../estate-evidence-core/scripts/evidence_core.py ledger.json business_case
```

The contract's required domains are recommendation, current gap, timing,
benefits, case against, cost of waiting, investment, and approval conditions.
If any load-bearing domain comes back Insufficient, produce the investment
readiness gap memo the contract names and stop. A full business case generated
after an Insufficient gate is a hard fail, because the approver funds against
whatever you print. Evidence-core owns provenance, confidence, conflicts,
staleness, and sufficiency; do not restate its rules here or anywhere else.

If evidence-core is not installed on this surface, say so, state the check it
would have run, do the best manual substitute (named source and date on every
claim, conflicts kept visible, gaps named), and report that as what happened.
Never silently skip the gate.

## Phase 1: sort the ledger into the balance view

The business case reads the validated ledger through three headings, because
the recommendation is their net:

- **Benefits.** Each must name the sourced pain it closes. A benefit that does
  not trace to something the client said hurts is a feature, and features do
  not belong in a business case. Cut it.
- **Costs and risks.** The investment, what is explicitly not priced, and the
  honest risks. Each risk carries a severity and a mitigation that is an
  action, not a restatement. Source risks from real friction: budget pushback,
  a capacity constraint, a cheaper competitor. A risk invented to look
  balanced is as bad as a benefit invented to look strong.
- **Timing facts.** The dated events that drive the cost of waiting: a
  cutover, a renewal cliff, a compounding manual cost. These turn "why now"
  from urgency theater into arithmetic.

This is a view over the evidence-core ledger, not a second ledger. Every entry
keeps its claim ID, source, confidence, and as-of date from the ledger. If the
costs-and-risks side is thin, the recommendation is not yet earned; go back to
the sources, because the risks exist whether or not you logged them.

## Phase 2: the money rule

Every number in the case has exactly one legitimate origin, and the case says
which:

- **Engagement cost figures come from the quote.** The Q-number through the
  scoping integration, or an explicit user-supplied pricing source. This skill
  renders those numbers; it never authors them. What the quote explicitly does
  not price is named in the ask, never folded into the headline figure.
- **Client-side value figures come from sourced client financials** (filings,
  investor materials, discovery numbers the client stated) or they are labeled
  inferences carrying an ID, a basis, and a safe-to-say verdict. An
  unquantified benefit is stated qualitatively. A fabricated value number is
  the fastest way to lose the one reader this artifact exists for.
- **Cost-of-delay arithmetic is shown, printed, and computed, never
  asserted.** Write the computation on the page: inputs, operator, result,
  each input sourced. The gate recomputes every shown product and fails on a
  mismatch.

Source tokens make this checkable. Every line carrying a currency figure or a
percentage ends in one of `[src: ...]`, `[quote: Q-...]`, `[inferred: ...]`,
`[gap: ...]`, or `[computed: ...]`. The full grammar, with the case-against
and cost-of-delay specs, is in `references/economics-and-case-against.md`.
Read it before writing sections 04 and 05.

## Phase 3: derive the structure, then write

Derive the section set from the ledger before consulting any worked example.
The catalog, with each section's job, bar, retrieval sources, and the
load-bearing versus flex table, is in `references/section-catalog.md`.

Always present, because the artifact does not exist without them:

- **01 Executive frame.** The recommendation, why it wins on balance, and the
  strongest argument for and against, up front. An approver who reads only
  this section knows what they are funding and that the case has looked its
  own downside in the eye.
- **04 Economics.** Benefits each closing a named pain, and the cost of
  waiting as shown arithmetic tied to a dated event.
- **05 The case against.** The skeptic's argument written straight, including
  the cheaper alternative, then answered or conceded. This section is what
  makes 01 credible.
- **06 Risk.** Sourced risks, each with severity and an action mitigation.
- **08 The ask.** Exactly what is being approved, by when, what is not yet
  priced, and the open decisions with owners and dates. No blank checks.

Contextual, included only when the ledger has the substance: 02 the client and
the gap, 03 why this moment, 07 investment and delivery. Benefit count equals
the benefits in the ledger; risk count equals the risks. Never pad to a round
number, and never manufacture timing pressure where the ledger has none.

Render confidence honestly as you write: Confirmed states plainly, Inferred
states as an inference with its basis, Unknown renders as a named gap,
conflicts show both values and flag the divergence. Concede before you
reframe.

## Phase 4: gate the draft

```bash
python3 scripts/case_gate.py case.md
```

The gate is deliberately light, because this artifact lives on judgment: it
checks that the load-bearing sections exist and have content, that the
case-against section is non-empty, that every currency figure and percentage
carries a source token, that every shown computation actually computes, and
that no em dash appears anywhere. Exit 0 is the only pass. Report the counts
it prints, never an adjective.

The gate cannot judge whether the case against is honest or the benefits trace
to real pains. That is your job, held to `references/depth-tests.md`. Run the
depth tests and the clone test there before calling the draft done. The
cardinal rule from that file: worked examples are depth-and-voice yardsticks
consulted last, never content sources. If find-and-replacing the client name
would turn your case back into an example, you cloned it.

## Phase 5: render and release

Rendering belongs to `estate-brand-renderer`. This skill ships no CSS, no
JS, no palette, and no renderer of its own; a forked stylesheet is a second
source of truth that drifts. Hand the gated draft to the brand renderer and
ask for the devices this artifact earns: the for/against balance split, the
cost-of-delay timeline with compounding stops, the decision tracker with
owners and dates, muted severity tags with no red/green fills. Density is
visual where it earns it; prose carries judgment.

All four of the renderer's release gates (parity, visual, prose, brand) need a
written disposition before delivery. The prose gate runs the house checker:

```bash
python3 ../prose-pass/scripts/prose_check.py case.md --config ../prose-pass/house.json
```

A clean tool run is not a release authorization. Write a one-line disposition
per gate.

## Phase 6: land it and close the loop

Stamp the artifact with its source objects and dates: the Q-number and quote
total as-of, the ledger snapshot date, the driving event date. Record IDs are
not durable anchors, so the stamp is what lets the next session detect drift.
Deliver the file, commit it to the client or project folder, and write session
memory pointing at the files rather than restating them.

Then tell the user the recommendation, the two or three facts that carry it,
and the landmines. Flag your biggest judgment call and argue the other side of
it honestly. Every real case contains at least one fork: whether the timing
argument is strong enough to lead, whether an inferred value number is safe to
print, which alternative the case against takes on first. Presenting the case
as settled when it holds a real fork is the failure mode to avoid.

## When time is short

Cut in this order, and say what you cut: 07 delivery detail down to the single
cost figure and phase list; 02 down to two sentences inside 01; 03 folded into
the cost-of-waiting arithmetic. Never cut: the evidence gate, the case
against, the source tokens, the shown arithmetic, or `case_gate.py`.

## Running unattended

Phases 3 and 6 need a human for the judgment forks. On a scheduled or headless
run: build the ledger, run the evidence gate, draft, run `case_gate.py` and
the prose checker, and stop with the findings and open forks stated plainly.
Never ship a funding document to a client on an unattended run.

## Boundaries

- Does not price. The quote owns every engagement cost figure; this renders
  them.
- Does not build the deal decision deck. That is `estate-ddoc`.
- Does not build the priced interactive proposal. That is
  `estate-interactive-proposal`.
- Does not run the internal margin gate. That is the Deal Desk readout under
  evidence-core's `deal_desk` contract.
- Does not research the prospect. That is `estate-call-prep`; this consumes
  its outputs as sources.
- Evidence rules belong to `estate-evidence-core`, brand tokens to
  `estate-brand-renderer`, and writing review to `writing-integrity` using the confirmed author profile.

## Files

- `references/section-catalog.md` · the eight sections, each with its job,
  bar, retrieval sources, and failure mode, plus the load-bearing/flex table.
- `references/economics-and-case-against.md` · the source-token grammar, the
  cost-of-delay arithmetic spec, and the case-against spec.
- `references/depth-tests.md` · the depth tests, the cardinal rule, and the
  clone test.
- `scripts/case_gate.py` · the structural gate. Stdlib only. Exit 0 pass,
  1 fail.
- `scripts/case_gate_selftest.py` · fixtures under `scripts/fixtures/`. Run it
  after any change to the gate.
