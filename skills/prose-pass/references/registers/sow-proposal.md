# Register: SOW / proposal / RFP response / change order

Contract-class documents. The reader is an evaluator scoring against criteria, or a client signing against scope. Both read dozens of these and pattern-match fast.

## What evaluators actually punish

From bid/proposal evaluator commentary (Lohfeld and others, 2025): experienced reviewers "can spot AI Speak from a mile away" and "if the evaluator feels like they are reading AI Speak, your proposal score is toast." Their named tells, in priority order:

1. **Buzz clusters** — innovative / cutting-edge / seamless / robust stacked in one sentence or paragraph. One is a word choice; three together is a fingerprint.
2. **Oddly uniform sentence and paragraph rhythm** — flawless grammar, every paragraph the same shape. Vary it.
3. **Shallow customization** — boilerplate where only the client name was swapped in. Every section should contain something that could only be written about *this* client: their org names, their volumes, their systems, their stated constraints.
4. **Overexplaining the obvious** — clause-justification, restating what a section does. (This overlaps `sow-quality` structural de-slop; that skill owns repetition-as-thoroughness and cross-reference discipline. Don't duplicate its work — run it after this pass on contract-class docs.)

## The hallucinated-capability rule

The highest-stakes failure in this register is not style. An LLM-drafted sentence that implies a capability, accelerator, or staffing depth Aleysian doesn't have makes the document misleading and the project undeliverable. When a rewrite tightens a sentence, check it didn't *strengthen a claim*: "we can support X" and "our proven X practice" are different promises. It is better to raise a price than to present something Aleysian resources can't deliver; it is never acceptable to fill a gap with a plausible-sounding projection.

## Voice calibration

Confident, outcome-led, precise scope language, "we" voice. No filler, no stakes inflation — name the business impact in numbers (deals lost, cycle time, margin leakage), never "fundamental breakdown" or "inability to compete." Volumetric assumptions belong in the Basis of Estimate / Exhibit A, not scattered in prose (sow-quality owns that mechanic).

## Tie-out is mandatory here

Run `--tie-out` and reconcile to the pricing source (the quote, Q-number, or scoping output), not just to the input draft. Pricing, durations, resource counts, and assumption volumes must match the authoritative system exactly. Section signs: zero. Em dashes in authored prose: zero (verbatim source values exempt).

## Worked example

Input: "Our comprehensive assessment has delved into the intricacies of your Salesforce environment, revealing pivotal insights that underscore the transformative potential of your platform. By leveraging our robust methodology, we have navigated the complex landscape of your current architecture."

Rewrite: "We reviewed your Salesforce environment across five domains: data model, automation, integrations, security, and reporting. Three findings need attention before any new build work starts. First, 44 active workflow rules and process builders on Case alone — the root cause of the performance issues your team flagged."

Why it works: every sentence carries a specific (five named domains, a count, a named object, a client-reported symptom). The buzzwords didn't get synonyms; they got replaced by facts.
