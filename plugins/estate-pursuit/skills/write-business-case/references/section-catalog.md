# Section catalog

The catalog does double duty: it is the retrieval checklist worked against the
evidence-core ledger, and the projection target the draft renders. Each entry
gives the question the section answers, the bar it is held to, where its
content is retrieved from, and the failure mode it exists to prevent.

Open each section of the case with one line stating the bar it is held to.
That device keeps the writer honest and tells the approver what the section is
for.

Titles flex to the deal's language ("The ask" can become "The decision";
"Why this moment" can become "The window"). Keep the section's job, change the
label. The gate matches headings by keyword, so keep the domain word in the
title.

## 01 Executive frame · LOAD-BEARING

- **Answers:** what we recommend, why it wins on balance, and the strongest
  argument for and against, stated up front.
- **Bar:** an approver who reads only this section knows what they are being
  asked to fund, why it beats the alternatives including doing nothing, and
  that the recommendation has looked its own downside in the eye. The decisive
  factor is named, not asserted.
- **Retrieve from:** the net of the whole ledger. The for/against pull from
  the benefits and costs-and-risks headings; the ask pulls from the quote and
  the proposal or SOW draft.
- **Prevents:** a case that buries the recommendation on page six, and one
  that reads as advocacy because it never concedes a downside.

## 02 The client and the gap · contextual

- **Answers:** who the client is, the strategic bet they are making, and the
  specific gap this investment closes.
- **Bar:** an approver who has never seen the account understands in two
  minutes who they are, where they are headed, and the one structural gap in
  the way, framed as a business problem rather than a tooling shortfall.
- **Retrieve from:** the client's public financials for the macro bet,
  Salesforce for the deal, discovery outputs for the gap in the client's own
  words.
- **Prevents:** arguing for a solution before establishing the problem is
  worth money.

## 03 Why this moment · contextual, drop only after looking hard

- **Answers:** why now and not next year: the forces, and the date that makes
  them urgent.
- **Bar:** "why now" rests on a real event with a real date (a migration
  cutover, a renewal cliff, a fiscal close), sourced. Not manufactured
  urgency.
- **Retrieve from:** the timing facts in the ledger. Gmail and Slack for the
  driving date, Salesforce for close pressure, discovery for the compounding
  pain.
- **Prevents:** an "act now" a CFO would not accept.

## 04 Economics · LOAD-BEARING

- **Answers:** what the investment delivers, each benefit closing a pain the
  client named, and what waiting costs in shown arithmetic.
- **Bar:** every benefit leads with an outcome and names the specific
  current-state break it closes. The cost of delay is a printed computation
  tied to a dated event: what compounds per month, what gets built twice, when
  the earliest value lands if the decision slips. Spec in
  `economics-and-case-against.md`.
- **Retrieve from:** the benefits heading crossed with the timing facts. Each
  benefit pulls from a discovery pain; each delay cost pulls from a sourced
  rate and a sourced date. Ground benefits in prior engagements where the
  value landed, when the portfolio record supports it.
- **Prevents:** the feature-list pitch, and a "why now" with no teeth.

## 05 The case against · LOAD-BEARING

- **Answers:** what the skeptic in the approval meeting would say, written
  straight, then answered or conceded.
- **Bar:** the cheaper alternative (a point tool, hire more people, do
  nothing) is taken on directly, not dodged. Each argument is sourced from
  real friction and gets one of two treatments: an answer with evidence, or a
  concession with its consequence. A downside rendered as a strawman reads as
  one. Spec in `economics-and-case-against.md`.
- **Retrieve from:** the costs-and-risks heading. Slack and pricing threads
  for budget pushback, competitor intel off the opportunity, SOW assumptions,
  prior engagements where a comparable build went wrong.
- **Prevents:** the sales pitch. A case with no credible downside is
  discounted on sight by anyone who has approved budget before.

## 06 Risk · LOAD-BEARING

- **Answers:** what could go wrong in delivery and adoption, how bad, and what
  keeps each from becoming a blocker.
- **Bar:** each risk carries a severity and a mitigation that is an action,
  not a restatement of the risk. Risks are sourced from actual friction, never
  invented to look balanced. Severity tags stay muted in the render; no
  red/green fills.
- **Retrieve from:** the costs-and-risks heading: capacity constraints,
  client-side staffing, change-management load, dependency dates.
- **Prevents:** a mitigation column that just repeats the risk in softer
  words, and a risk register that exists to look thorough.

## 07 Investment and delivery · contextual

- **Answers:** the investment, the phase plan, and what the client has to
  bring.
- **Bar:** the number is honest (the un-priced parts named, not hidden), the
  plan sequences around any hard date, and the client-side commitment is
  explicit so "we did not have the people" never surfaces mid-build.
- **Retrieve from:** the quote for the number and its edges, the SOW or
  proposal draft for phasing and assumptions, the staffing model for
  client-side hours. Every cost figure carries a `[quote: ...]` token.
- **Prevents:** an approval granted against a number that quietly excludes
  half the work.

## 08 The ask · LOAD-BEARING

- **Answers:** exactly what is being asked, by when, what is not yet priced,
  and the open decisions that gate approval.
- **Bar:** the ask is specific: approve what, by what date, at what figure.
  Every un-priced item is named so the budget conversation is honest. Every
  open decision has an owner and a resolve-by date. No blank checks.
- **Retrieve from:** the Unknown entries and un-priced quote lines (the gaps),
  plus the open decisions from Slack, Gmail, and the SOW draft.
- **Prevents:** an approval built on a number that grows later, and a yes that
  stalls because nobody knew what still had to be decided.

## Load-bearing versus flex

| Section | Status | Include when | Drop or fold when |
| --- | --- | --- | --- |
| 01 Executive frame | Load-bearing | Always | Never |
| 02 The client and the gap | Flex | The approver needs the situation set | An internal audience knows the account cold; fold two sentences into 01 |
| 03 Why this moment | Flex | Timing is a real driver, which is almost always | Genuinely no timing pressure; look hard before dropping, and fold any dates into 04 |
| 04 Economics | Load-bearing | Always | Never |
| 05 The case against | Load-bearing | Always | Never |
| 06 Risk | Load-bearing | Always | Never |
| 07 Investment and delivery | Flex | The cost, plan, and client effort are part of the ask | A pure go/no-go on direction; keep the single cost figure in 08 |
| 08 The ask | Load-bearing | Always | Never |

Scaling follows the ledger. A thin deal yields the load-bearing five, folded
tight. A rich one earns the situation, the timing section, the full
investment-and-delivery detail, and longer benefit and risk lists. Benefit
count equals the ledger's benefits; risk count equals the ledger's risks; no
padding to a round number.
