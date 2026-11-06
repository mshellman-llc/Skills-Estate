# Economics and case-against spec

The two sections that decide whether the case is believed. Read this before
writing sections 04 and 05, and again before running the gate.

The numerical examples below are fictional library-catalogue illustrations, not client evidence.

## The source-token grammar

Every line of the draft that carries a currency figure or a percentage ends in
exactly one source token. The gate enforces this mechanically; the grammar is
what makes the money rule checkable rather than aspirational.

| Token | Means | Example |
| --- | --- | --- |
| `[src: <source>, <date>]` | A sourced client-side or market figure | `Catalogue administration costs $1,440 [src: synthetic time ledger, 2030-02-01]` |
| `[quote: <Q-number>]` | An engagement cost figure from the quote | `Catalogue pilot investment of $600 [quote: Q-SYNTH01]` |
| `[inferred: <ID>, <band>, <basis>]` | A labeled inference with its register entry | `Roughly 8% of cards need correction [inferred: A1, low, synthetic volunteer estimate]` |
| `[gap: <name>]` | A searched-for figure that does not exist yet | `Hosting not yet priced [gap: hosting quote needed, owner committee, due 2030-02-10]` |
| `[computed: <inputs>]` | The result of a shown computation | `$120/mo x 5 mo = $600 [computed: inputs C7, C9]` |

Rules that ride on the grammar:

- Engagement cost figures take `[quote: ...]` only. If the figure did not come
  from the quote or an explicit user-supplied pricing source, it does not go
  in the document. This skill renders numbers; it never authors them.
- Client-side value figures take `[src: ...]` when the client or a filing
  stated them, `[inferred: ...]` otherwise. Every inference in the document
  also appears in the assumptions register with its ID, confidence band,
  basis, and a safe-to-say verdict. An unquantified benefit is stated
  qualitatively; a fabricated number is a hard fail.
- `[gap: ...]` figures render as named gaps in section 08, never folded into
  the headline number.
- Fixed-fee versus time-and-materials: the case states one, never both.

## Cost-of-delay arithmetic

The cost of waiting is arithmetic, not adjective. Three shapes cover nearly
every deal; use whichever the timing facts support, and show the work on the
page:

1. **The compounding monthly cost.** A sourced per-month figure times the
   months of deferral. `$120/mo x 5 mo = $600 [computed: inputs C7, C9]`
   where C7 is the sourced monthly cost and C9 is the sourced decision-to-start
   interval.
2. **The built-twice cost.** Work that must be redone if the decision slips
   past a dated event: an integration built against the old system, a catalog
   loaded twice. Source the rework estimate; never invent it.
3. **The value-slip cost.** When the earliest value lands if the decision is
   made now versus after the driving date, and what each month of slip
   forgoes.

Requirements the gate enforces:

- At least one printed computation (inputs, operator, result) in the
  economics or cost-of-waiting content.
- Every shown product recomputes correctly. The gate multiplies the inputs and
  fails on a mismatch beyond one percent.
- Every input and every result line carries a source token.

Requirements only you can enforce:

- Every input traces to a ledger claim, not to a plausible-sounding rate.
- The deferral interval ties to a real dated event, not to a round number.
- If the ledger has no timing facts, say so and drop the device honestly. A
  cost-of-delay computation on invented inputs is worse than none.

## The case against

An honest case names what the skeptic would say and answers or concedes it.
Write section 05 as that skeptic, then respond. The discipline:

1. **Name the cheapest alternative first.** There is always one: a point
   tool, a build-it-internally, hire more people, do nothing. Take it on
   directly, on its own strongest ground (usually price or simplicity), not
   on a weakness you chose for it.
2. **Write each argument straight before responding.** The skeptic's line
   appears in full, at full strength, sourced from real friction: the budget
   pushback in the pricing thread, the competitor off the opportunity, the
   capacity worry the delivery lead raised. If you cannot source a
   case-against argument, you have not looked; the objections exist whether
   or not you logged them.
3. **Respond with exactly one of two moves.** Answer it with evidence (a
   TCO reframe with sourced figures, a prior engagement where the risk was
   managed), or concede it and state the consequence the recommendation
   absorbs ("this costs more than the point tool, and the case holds
   because..."). Concede before you reframe. Softening an objection into a
   non-risk reads as evasion to anyone who has heard the objection live.
4. **Let it carry real weight in section 01.** The executive frame's
   for/against split gives the against side its genuine best points, not
   filler. If the against side is thin, the recommendation is not yet earned.

Failure modes this spec exists to prevent: the strawman (an objection nobody
would raise, answered triumphantly), the dodge (the cheaper alternative never
mentioned), and the laundering (a real objection paraphrased into something
easier to answer). An approver who has heard the real objection recognizes
all three, and each one costs the whole document its credibility.
