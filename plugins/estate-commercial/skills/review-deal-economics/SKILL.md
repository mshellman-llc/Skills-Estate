---
name: review-deal-economics
description: "Review provider economics, risks and commercial conditions, and reconcile figures across a quote, proposal or statement of work. Use current project policy; do not change pricing or infer approval."
---


# Review deal economics

The Deal Desk readout answers one question for people who were not in the
scoping room: should Estate ship this offer, and on what terms. It is the
last internal gate before the client sees numbers, so its job is to make the
commercial reality legible, not attractive.

The cardinal rule: **surface everything, smooth nothing.** A reviewer who
approves a clean-looking packet with hidden problems is not protected; one
who approves a packet with explicit flags made a considered decision. Every
unconfirmed staffing role, every load-bearing assumption, every risk to
margin appears as a labeled flag with a named resolution path. Presenting a
clean deal that is not clean is the exact failure this artifact exists to
catch, and it is why the artifact registry lists "risk smoothed over" and
"real margin hidden behind point estimate" as hard fails.

Margin is the headline. A reviewer should reach the margin number, and its
position against the floor, in the first ten seconds. If the margin is
tight or provisional, that is the lead, not a footnote.

## Governance, delegated

- **evidence-core** runs first. Sales context, stakeholder
  postures, risks, and assumptions are load-bearing claims; build the ledger
  before the packet. If a load-bearing domain is Insufficient, produce the
  "Not ready for Deal Desk approval" memo and stop. A full packet after
  insufficient evidence is a hard fail.
- **The quote owns every number.** Hours, rates, fees, and durations come
  from the Q-number through the scoping MCP (`scoping_get_quote` and
  friends), never from memory or chat. Margin is computed from those inputs
  and printed with the computation, never asserted. Fixed fee or T&M, never
  both. If the quote and any other document disagree, the quote wins and the
  disagreement becomes a flag.
- **brand-renderer** owns the rendering and the visual, parity, and
  brand release gates. Never inline hex values or rebuild the token set.
- **review-writing** owns writing review; a confirmed profile supplies voice. Run its checker on the packet's prose. No em
  dashes, sentence-case headings, no AI vocabulary in the tagline or
  anywhere else.

If a governor is not installed on this surface, state the check it would
have run, do the best manual substitute, and say that is what happened.
Never skip silently.

## One mandatory human input

The delivery leadership cosign is asked for, never inferred. Ask the
delivery lead (or the user relaying them) whether delivery has cosigned
scope, hours, and assumptions, and record the answer verbatim. The
figures block field `delivery_cosign.status` takes exactly one of
`confirmed`, `conditional`, `pending`, or `declined`; the gate rejects
blank, `assumed`, `inferred`, and `tbd`. "Delivery cosign missing" is a
registry hard fail, and it means missing from the record, not missing
approval: `pending` with a named signer and a date is an honest, passing
answer. `confirmed` without a name and date fails.

Everything else in the packet can be harvested. This one field cannot.

## Workflow

**1. Orient.** Pin the opportunity, the Q-number, the deal desk meeting if
one is scheduled, and who reviews. Confirm the quote total and pricing model
through the scoping MCP before writing anything. Stamp the packet with the
Q-number and an as-of date; record IDs do not survive sandbox refreshes, so
the stamp is what makes the packet auditable later.

**2. Read current commercial policy.** Confirm the project's margin floor and
approval ladder from its named source. Record the verification date and the
selected values in the figures block. Read [margin policy](references/margin-approval-routing.md)
for the input contract. If policy is unavailable, prepare the supported economics
and identify the approval decision still needed. Never inherit a threshold from
an example or treat a valid figures record as approval.

**3. Harvest.** Internal first: the quote, the DDOC and its confirmed
option, the solution brief, the SOW draft if one exists, Salesforce
opportunity and contacts, transcripts read verbatim, Slack. Evidence-core
governs provenance: every claim carries a source and date, every inference
is labeled with a confidence band, conflicts show both sides.

**4. Build two ledgers, then the packet.** The commercial ledger: per-role
hours, rates, cost rates, fee, computed margin, staffing basis, sensitivity
scenarios with dollar impacts, levers with quantified effects. The risk
ledger: margin risks each paired with a protective clause by number or a
no-coverage flag (one or the other, never both, never neither), scope risks,
staffing prerequisites, load-bearing assumptions with quantified "if broken"
consequences. Then project the packet from the ledgers using
`references/section-catalog.md`. Every catalog section is always present;
an unfillable section becomes a named unknown with an owner, a resolve-by
date, and the gate it blocks, never a plausible projection.

**5. Route the asks.** Two to six asks, each with a direct recommendation,
formatted per `references/asks-and-decisions-log.md`. Compute which ladder
band the real margin lands in and route price-touching asks to that band's
approver or higher. The packet requests exactly one overall approval action:
approve, approve with conditions, reject, or not ready. More than one is a
hard fail. The decisions log ships empty; it is filled live in the meeting,
and pre-filling it fabricates approvals.

**6. Embed the figures block and run the gate.**

```bash
python3 scripts/deal_desk_gate.py packet.md
```

The block schema is in `references/margin-approval-routing.md`. The gate
recomputes internal cost from role hours and cost rates (and the fee too on
T&M), checks the stated margin against the recomputed one, checks the floor
comparison against the arithmetic, checks the approval route against the
ladder carried in the block, and rejects a blank or non-committal cosign.
Exit 0 or the packet does not ship. Fix the ledger and regenerate; never
hand-patch the rendered output, because the next regenerate drops the patch.

**7. Tie out every figure across the reviewed artifacts.** Export the quote's
figures (fee, per-role hours and rates, phase totals, verified percentages,
assumptions, scope lines) to JSON per the schema in
`scripts/quote_tieout_check.py`, then reconcile the packet prose and every
sibling artifact under review (SOW draft, ROM, proposal) against it:

```bash
python3 scripts/quote_tieout_check.py quote.json packet.md sow-draft.md rom.md
```

Any figure that traces to nothing in the quote fails, whether it is fabricated
or contradicts a quote value; the check prints the offending line and the
nearest quote value and resolves nothing. A quote figure, assumption, or scope
line no artifact carries is a warning to confirm. Fix conflicts at their
source (the quote through scope-project, or the artifact through its owning
skill) and rerun; this skill never edits a figure to make the tie-out pass.

**8. Render and gate the rendering.** Hand to brand-renderer for
the HTML (or docx backup for email and print). Margin is the visually
dominant figure, rendered against the floor; all economics in monospace.
Verify by rendering, then apply review-writing to the prose. Report counts per
gate, not adjectives, and write a one-line disposition per gate.

**9. Land and close the loop.** Deliver the file, commit it to the deal's
folder, write session memory pointing at the files. Close with the margin
verdict, the flags a reviewer must not miss, and your biggest judgment call
argued honestly from the other side. If the packet contains a real fork,
say so; never present it as settled.

## Durable output

Every run leaves a Markdown record per `_shared/output-contract.md`: the
packet itself on a build, or a review record with the gate and tie-out
results, the exceptions, and the remediation list on an audit. The decision
record lands in the engagement hub's `04-decisions-assumptions.md`, which
this skill owns for Deal Desk outcomes: what was asked, what the humans
decided, and what supersedes what. Deliver or link the file; never just say
it was written.

## If the margin does not survive

When the recomputed margin lands below the floor, or becomes a range whose
pessimistic end does, that is the headline and the packet still ships, with
the route escalated per the ladder and the levers section carrying real
options with quantified impacts. What never happens: adjusting hours or
rates to rescue the number. Pricing changes belong to scope-project against
the quote; this skill renders what the quote says and routes the
consequences.

## Boundaries

- Internal only. Nothing in this packet is client-facing; it carries margin,
  cost rates, and candid risk the client never sees.
- Does not price and does not touch the quote. scope-project owns scope and
  pricing changes; this skill renders and routes.
- Not the DDOC. The client-facing decision deck is build-deck; "Deal Desk
  document" as a client deck is a retired name for that artifact, and this
  skill is the internal readout only.
- Not the business case; that is write-business-case. Not SOW terms;
  that is write-statement-of-work, and the protective clauses' text lives in the SOW
  master, cited here by number only.
- Reviews and verdicts only. It never authors or silently rewrites the
  solution, the SOW, or any source evidence; a failed check produces a
  remediation list for the owning skill, never an edit.
- Does not approve. Humans clear the gate; the packet prepares it. The
  decisions log and sign-off table record what humans decided.
- Post-approval change detection (a material scope or margin change after
  Deal Desk requiring re-alignment before SOW) is deal governance, not this
  skill. It is a known gap: when a packet is being rebuilt after approval,
  flag the delta explicitly and say re-alignment is required.

## Running unattended

The cosign and the live decisions log need humans. On a scheduled or
headless run: build the ledgers, embed the figures block with
`delivery_cosign.status` set to `pending` and a named owner, run the gate,
and stop with findings. Say plainly that the cosign is outstanding. Never
record an answer nobody gave.

## When time is short

Cut in this order, and say what was cut: methodology detail, the staffing
Gantt (keep the allocation table), sales-context depth below the ROM and
deadline rows. Never cut: the figures block and its gate, the cosign ask,
the floor comparison, the assumptions table, sourcing, or the flags. A thin
honest packet clears review; a full smooth one is the failure mode.

## Files

- `references/section-catalog.md`: every packet section, its field sources
  (DS, SE, CA, PS), and the bar each must clear.
- `references/margin-approval-routing.md`: floor, ladder, protective
  clauses, re-verification rule, and the figures block schema.
- `references/asks-and-decisions-log.md`: ask format, live decisions log,
  action items, sign-off, and the cosign protocol.
- `scripts/deal_desk_gate.py`: the blocking gate. Python 3 stdlib only.
- `scripts/deal_desk_gate_selftest.py`: run it after any gate change;
  fixtures in `scripts/fixtures/`.
- `scripts/quote_tieout_check.py`: the deterministic tie-out. Reconciles
  every figure, assumption, and scope line in the reviewed artifacts against
  the quote export. Stdlib only; the quote JSON schema is in its docstring.
- `scripts/quote_tieout_check_selftest.py`: run it after any tie-out change;
  fixtures `tieout_quote.json`, `tieout_pass.md`, and `tieout_fail.md` in
  `scripts/fixtures/`.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
