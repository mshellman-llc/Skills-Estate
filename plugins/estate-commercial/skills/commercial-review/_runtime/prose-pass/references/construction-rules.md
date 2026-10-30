# Construction rules, C1 to C18

Full reference. `SKILL.md` carries the six highest-frequency rules; this file carries all eighteen with reasoning and replacements.

Each rule states the ban, then what replaces it. The replacement is the part that matters. A rule that says only what to avoid relocates the construction instead of removing it, which is how a successful em-dash ban produces a `, and` epidemic.

## Contents

| | | | |
|---|---|---|---|
| [C1](#c1-balanced-two-clause-sentence) Balanced two-clause sentence | [C2](#c2-antithesis-payoff) Antithesis payoff | [C3](#c3-aphorism-as-closer) Aphorism as closer | [C4](#c4-number-forward-headline) Number-forward headline |
| [C5](#c5-colon-drumroll) Colon drumroll | [C6](#c6-fragment-stacking) Fragment stacking | [C7](#c7-triads) Triads | [C8](#c8-trailing-restatement) Trailing restatement |
| [C9](#c9-self-narration) Self-narration | [C10](#c10-deference-signalling) Deference signalling | [C11](#c11-agentless-construction) Agentless construction | [C12](#c12-verbatim-recycling) Verbatim recycling |
| [C13](#c13-forced-template-symmetry) Forced template symmetry | [C14](#c14-undefined-idiom-as-a-scored-value) Undefined idiom as scored value | [C15](#c15-unsourced-quantifier) Unsourced quantifier | [C16](#c16-notation-drift) Notation drift |
| [C17](#c17-fear-framing) Fear framing | [C18](#c18-defensive-attribution) Defensive attribution | | |

Examples are drawn from two real documents, anonymized: an interactive lifecycle panel and a consulting assessment deck.

---

## C1. Balanced two-clause sentence

**Ban.** Two independent clauses of similar weight joined by `, and`, `, but`, or `, so`.

**Why.** This is the em dash in disguise. In a house that bans the em dash it becomes the highest-frequency structural tell, because the ban removed the punctuation without addressing the construction underneath it.

**Replace with.** Split into two sentences of deliberately unequal length. Or subordinate the weaker clause. Or cut it.

Do not substitute a semicolon, a colon, or a dash of any width. Those preserve the rhythm and only change the paint.

> Before: Costs not yet negotiated, and the first numbers were too high.
> After: Costs are not negotiated. The first numbers came back too high.

The unequal-length part is not decoration. Two short sentences of matching length reproduce the same metronomic feel. Let one run long and the other land short.

---

## C2. Antithesis payoff

**Ban.** `X, not Y`. `X does but Y blocks`. `The most A is the most B`. Any sentence whose payload is the contrast rather than the fact.

**Why.** Antithesis is the default shape a model reaches for when a line needs to feel conclusive. It produces the *sensation* of insight without necessarily carrying any.

**Replace with.** The operative fact, stated flat. Keep at most one antithesis per document, and only where the contrast is the actual finding.

> Before: The product does it and the implementation blocks it.
> After: Every capability was present at go-live. None was configured.

---

## C3. Aphorism as closer

**Ban.** Ending a section, card, or slide on an epigram.

**Why.** This is the hardest rule to self-diagnose, because each line passes inspection alone. Uniformity is the tell. Human documents contain flat, unmemorable closers. A document where every unit lands a zinger reads as generated regardless of how good the zingers are.

**Replace with.** End on the last substantive fact. Budget one epigrammatic closer per document, placed where it earns the emphasis.

A useful test: read only the final sentence of every section in sequence. If it sounds like a collection of pull quotes, you have this problem.

---

## C4. Number-forward headline

**Ban.** Headlines built on a count. `Nine stages, three verdicts`. `Your four examples`. `Two figures`. `The three questions`.

**Why.** Quantifying the headline performs rigor. One is fine. When every headline does it, the reader feels the template before reading the content.

**Replace with.** A headline that names the content. The count belongs in the body or in the visual, where the reader can verify it.

---

## C5. Colon drumroll

**Ban.** Setup, colon, payoff, where the right side is a question or a reveal.

> One question at each: is the system holding up?

**Why.** The colon is doing suspense work. The question is not answered by the sentence and often not by the section either.

**Replace with.** State the thing. If the question genuinely structures the section, make it the heading and answer it in the first sentence.

---

## C6. Fragment stacking

**Ban.** Consecutive verbless sentences. Terse trailing beats used for punch: `Credit memos follow.` `In acceptance testing.` `Phase 1B.`

**Why.** One fragment is a choice. Three in sequence is a cadence tic, currently the most recognizable one in circulation. It reads as manufactured punch.

**Replace with.** One verbless sentence per section at most, never two in a row. Give the fragment a verb, or fold it into the sentence before it.

Headings and table cells are legitimately verbless. This rule is about body prose.

---

## C7. Triads

**Ban.** Extends the familiar rule-of-three ban to three further forms:

- **Asyndetic triads.** `Defective code, rules from 2021, bad records from grouped deals.` Three noun phrases, no conjunction, terminal. A distinctive generated rhythm.
- **Lists padded to three.** If the third item exists to complete the pattern, it will usually break the grammar of the list. `Each one answers who works there, what the business needs, and one of three verdicts` fails because a verdict cannot be answered. That grammatical break is diagnostic: it means the list was extended for shape, not content.
- **Structural triads.** Three parallel cards, three columns, three phases, chosen for symmetry rather than because there are three.

**Replace with.** The true count. Two items get two. Four get four. Check that every item in a list is governed by the same verb.

---

## C8. Trailing restatement

**Ban.** Eyebrow, headline, and kicker where the kicker restates the headline.

> LEAD TO CASH / Who carries the work at each stage / What was bought, and what actually does the work.

**Why.** Three lines, one piece of information. Generated header stacks fill every available slot whether or not there is something to put in it.

**Replace with.** Each line carries information the others do not. The kicker adds a constraint or a source. If it has nothing to add, delete it.

---

## C9. Self-narration

**Ban.** Prose that describes the document instead of being the document:

- Section labels naming the rhetorical move: `THE STORY`, `WHAT IT MEANS`, `WHAT WAS SKIPPED`
- Prose describing the artifact's own construction: `Retellable without system vocabulary`
- Reading instructions inside the content: `Click any stage`, `Each question opens only if the answer before it is yes`
- Completion claims: `The July 15 question, answered`

**Why.** A section that contains the meaning does not need a label announcing that meaning follows. This is the written equivalent of explaining a joke.

**Replace with.** The content.

---

## C10. Deference signalling

**Ban.** `Your four examples`. `The cascades you asked to see`. `In your order`. `As requested`. `You said`.

**Why.** This is assistant voice proving it listened. Of everything here, it is the tell most specific to model-authored work. It appears because the model is optimizing to demonstrate responsiveness. A senior colleague does not label a slide with whose question it answers; they answer it.

**Replace with.** Nothing. Deliver the answer. Attribution of the question belongs in a cover note if it belongs anywhere.

---

## C11. Agentless construction

**Ban.** Extends the passive-voice rule to cover agentless *active* constructions, where systems act and people are absent.

> the code books it as new business, failing overnight silently
> 550+ automations sit on the quoting engine, so changes stopped shipping
> BUILT, IN ACCEPTANCE TESTING

**Why.** These are not passive by grammar. A passive-voice checker clears them. They achieve the same evasion. In the source document, a reader could not tell which of two organizations had built the work under review, which was load-bearing in a document about who should pay for it.

**Replace with.** Name the actor on every state change. Status labels take an owner.

---

## C12. Verbatim recycling

**Ban.** The same phrase of four or more words appearing twice in one document.

**Why.** Recurrence happens because each section was generated from the same brief and independently re-derived the same wording. A human editor consolidates without being told to. The source deck repeated `owned by finance operations` and `3 or 4 redundant apps` word for word across slides, and restated three statistics on a later slide that had already carried them.

**Replace with.** One authoritative home per fact, referenced from elsewhere.

Canonical strings that must match across documents by contract (product names, defined terms, legal language) are exempt. Note them as deliberate.

---

## C13. Forced template symmetry

**Ban.** N parallel items compressed or padded to identical length.

**Why.** In the source deck, all four case studies ran exactly five beats, each beat one short sentence, the fifth always root cause plus status. Four unrelated failure modes do not have the same shape. The uniformity is the tell, visible before a word is read.

**Replace with.** Let each item run its natural length. If a template forces a fixed beat count, the template is wrong.

---

## C14. Undefined idiom as a scored value

**Ban.** Rubric or verdict values that are idioms.

> Verdicts: holding up / set up wrong / broken

**Why.** Two of those three are specific. `Holding up` is an unmeasurable hedge. It is also the value carrying the good news, which is the worst place for imprecision.

**Replace with.** Define every rubric value where it first appears, in the same terms as its peers.

---

## C15. Unsourced quantifier

**Ban.** `Thousands of`. `Most`. `Many`. `The majority of`. `Countless`.

**Why.** These borrow the authority of measurement without doing any. `Runs the same product as thousands of companies` is doing reassurance work, not evidence work.

**Replace with.** A number with a source, or nothing. An unknown count is marked unknown; that is more credible than a vague one, not less.

---

## C16. Notation drift

**Ban.** More than one notation per quantity class in a document.

The source deck expressed ranges four ways (`$200K–$300K`, `70-80%`, `5-10`, `5 to 10`) and approximation three ways (tilde, plus-suffix, rounding). Two of those range instances were the same underlying quantity.

**Replace with.** One notation, declared once. Keep precision consistent across comparable figures: do not place `$49,676` beside `$0.9M–$1.8M` without explaining why one is exact.

---

## C17. Fear framing

**Ban.** The recurring-loss frame. `Exposure`. `Recurs every year the failures stand`. `Invests in a depreciating asset`.

**Why.** Urgency register substitutes emotional pressure for the figure itself, and readers discount it.

**Replace with.** The figure and its period. `$0.9M to $1.8M annually, until pricing and approvals deploy.`

---

## C18. Defensive attribution

**Ban.** Blame allocation presented as neutral fact.

> The 18-month figure is [another party]'s program design, and we were asked to fill in the blanks on it.
> You said no one inside the company can state that yet.

**Why.** Both sentences are true and both are doing something other than informing. They pre-position responsibility for a number the author expects to be challenged. Readers notice. It costs more credibility than the disclaimed number would have.

**Replace with.** The position. If a number is wrong, give the right number and the basis for it.

---

## Applying these to your own writing

These shapes are what fluent generation produces by default. Knowing the rule does not exempt you from it, and documents *about* the rules are not exempt either. The first draft of this file failed C1 ten times and C7 five times.

Run the checker on your own output, including output about writing quality.
