# DDOC copy examples, before and after

Worked pairs for the failure modes listed in `ddoc-patterns.md`. The table there names each failure; this file shows one in full so the fix is legible rather than abstract.

The "after" examples are the accepted rewrites and reflect current canon: options carry names rather than version numbers, and exactly one option is marked recommended.

---

## Fragment over-correction

The most common failure, and it is caused by the fix for a different problem. An editor cutting "AI wordiness" truncates sentences into fragments. The result reads more artificial, not less.

**Before (rejected):**
> Header: The number
> Body: $87,900, firm. This is the scope. 12 weeks. Done.

**After (accepted):**
> Header: Fixed-fee investment
> Body: $87,900 fixed fee, delivered over 12 weeks.

**Why it works:** one complete sentence carries the specifics. Nothing was chopped to fake punchiness, because punchiness comes from specificity, not truncation.

**Diagnostic signal:** body sentences under five words are a fragment indicator. Period-stacked constructions ("X. Y. Done.") are a near-certain tell. The builder warns on any bullet that does not end in terminal punctuation.

---

## Gimmick header

The opposite failure. The editor tries to make the deck interesting and produces a header that sounds like a billboard rather than a consultant.

**Before (rejected):**
> Header: Wear math, automated

**After (accepted):**
> Header: Automated wear projections replace the spreadsheet

**Why it works:** a reader who sees only the header knows the topic. The rejected header needs the body to decode it. A header that needs decoding is doing no work.

**Rule:** if you have to read the body to understand the header, rewrite the header.

---

## Label header, the "nothing" header

Common on slides presenting a problem or an approach.

**Before (flagged):**
> Header: Current state
> Header: Our approach
> Header: Key takeaways

**After (accepted):**
> Header: Pewag cannot see when its chains are wearing out
> Header: A six-week path from spreadsheet to Salesforce alerts
> Header: Three things to confirm before we start

**Rule:** after reading the header alone, can the audience state the slide's point? If not, rewrite it.

---

## Slot-fill symmetry on option cards

Option cards fail when each one opens with the same construction and fills in a slot. The client reads the repetition as padding.

**Before (rejected):**
> Lift and shift: Everything in the base scope.
> Remediate and migrate: Everything in lift and shift, plus history migration.
> Re-architect and migrate: Everything in remediate and migrate, plus Salesforce Maps.

**After (accepted):**
> **Lift and shift.** Full asset lifecycle tracking. Chain sets are recorded by customer and site, wear state updates from field logs, alerts fire when a set approaches end of life, and Salesforce creates the replacement opportunity.
>
> **Remediate and migrate.** Everything above, plus a one-time migration of five years of spreadsheet history. Every chain Pewag has ever installed arrives in Salesforce with its install date, service records, and prior wear readings.
>
> **Re-architect and migrate.** Everything above, plus Salesforce Maps. Field reps see account and asset locations on a map and plan service routes without switching tools.

**Why it works:** each card reads as a standalone statement, and the added scope is described by what it produces for the client, not just named ("history migration").

**Rule:** cover the other cards and read one alone. If it makes sense, it passes. If it needs the others to decode, rewrite it.

**Note on parity:** the builder measures word count across option blocks and warns past a 1.4x spread. A card that runs long reads as effort rather than scope, which quietly biases the choice.

---

## Colon tic on body lines

Avoiding em dashes breeds "X: Y" on every line. A label earns a colon. A body line rarely does.

**Before (flagged):**
> Outcome: Pewag sees every chain set's wear state without opening a spreadsheet.
> Impact: Field reps receive an alert before the chain reaches end of life.
> Benefit: Salesforce creates the replacement opportunity automatically.

**After (accepted):**
> Pewag sees every chain set's wear state without opening a spreadsheet.
> Field reps receive an alert before a chain reaches end of life.
> Salesforce creates the replacement opportunity automatically.

**Why it works:** the predicate was already in each sentence. The labels added category noise, not meaning.

**Density rule:** one colon in a body block is usually fine. Three or more is a rewrite signal.

---

## Missing recommendation

A decision deck that presents options as equals has not made a decision. The client is left to arbitrate between three things they are not equipped to compare, and the safest choice becomes doing nothing.

**Before (rejected):**
> Header: Three paths forward
> Body: Each option delivers value depending on your priorities and appetite for change.

**After (accepted):**
> Header: We recommend remediate and migrate
> Body: Lift and shift is cheaper now and costs more later, because the data problems move with you. Re-architect is the right end state but not the right first step, since it delays value by a quarter. Remediate and migrate fixes the data on the way across and gets you live this quarter.

**Why it works:** the recommendation is stated, the alternatives are characterised honestly rather than strawmanned, and the reasoning is visible so the client can disagree with the logic rather than the conclusion.

**Builder behaviour:** decision mode refuses to render with no option marked recommended, or with more than one. This is a hard failure, not a warning.

---

## Unattributed heard slide

The fastest way to lose a room is telling the client they said something they did not say. Every item on the heard slide carries an evidence class, and only `client_stated` renders.

**Before (rejected):**
> They are frustrated with the manual quoting process.
> Leadership wants to modernise before the next fiscal year.
> The current system cannot scale.

**After (accepted):**
> "We are quoting off a spreadsheet and it takes three days." (Operations Director, discovery call, 14 May)
> "I need this live before our fiscal year starts in October." (CFO, discovery call, 14 May)

The third item was an inference, not a statement, so it moved to the "what we need from you" slide as a question: "What is the current quote volume, and where does the system slow down?"

**Why it works:** two attributed statements outrank three confident paraphrases. The inference became a question, which is both honest and a better discovery prompt.

**Builder behaviour:** every heard item must be `{text, evidence, source}`. A bare string fails. Any item whose evidence class is `seller_asserted` or `inferred` fails, with a message telling you to move it or drop it. Classes and sources go into speaker notes, never onto the slide.

---

## Investment slide, over-explained

The investment slide fails when it becomes a scope restatement.

**Before (rejected):**
> $87,900, firm fixed-fee
>
> Includes:
> - Asset object configuration
> - Wear tracking automation
> - Opportunity creation workflow
> - Data migration (current year only)
> - User training (up to 10 users)
> - Project management and QA
>
> Payment terms: 25% at signing, 50% at milestone 2, 25% at go-live.

**After (accepted):**
> $87,900 firm fixed fee, covering the recommended option over approximately six weeks.
>
> The proposal that follows this conversation carries the full scope, payment schedule, and change order terms.

**Why it works:** a bullet list of deliverables on a pricing slide creates two homes for scope, and two homes drift. The slide confirms the number and points at where the detail will live.

**Sequencing note:** the DDOC runs before the proposal, so it cannot point at an attached Statement of Work. The SOW does not exist yet. Point forward to the proposal, never sideways to an attachment.

---

## Contract voice where partnership voice belongs

**Before (flagged):**
> Client shall provide Salesforce admin access with object-level permissions.
> Client must deliver historical chain data in CSV format within 10 business days.
> Client is responsible for user acceptance testing sign-off.

**After (accepted):**
> Designate a Salesforce admin with object-level field access, and bring them to the kickoff meeting.
> Export your chain history to CSV and share it within two weeks of kickoff. We map and load it from there.
> Plan a two-day UAT window at the end of week 5. Your team confirms the system meets your requirements, and we fix what does not.

**Why it works:** these are asks, not obligations. They say what to do and why, from the client's side of the table. Contract voice belongs in the contract.

---

## Line budget overflow, vertical-step support box

**Before (overflows the two-line budget):**
> Step header: Wear tracking automation
> Support: Salesforce evaluates the wear percentage on each chain set against the threshold configured for its product type, and when a set crosses 80% of expected life, an automated alert is sent to the owning account executive along with a task to initiate the replacement conversation with the customer.

**After (fits):**
> Support: When a chain set crosses 80% of expected life, Salesforce alerts the owning rep and creates the replacement task.

**Why it works:** same outcome, fewer words. The mechanism (wear percentage, product-type threshold) is scope detail and belongs in the scope documentation, not on the slide.

**Rule:** cut modifiers, preserve the complete sentence. A support line wrapping to a third line collides with the next step header. The builder enforces the budgets in `slide-layouts.md` as hard failures.
