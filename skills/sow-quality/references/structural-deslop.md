# Structural de-slop

Historical CPQ/T&M profile reference. Preserve these examples as examples. Apply
their terms, section numbers and role names only when the selected agreement
adopts that profile; the current contract and confirmed project policy control.
Never convert a fixed commitment or billing model merely to match this reference.

These are the AI tells a keyword scan misses. They live in how the document is organized, not in its vocabulary. Word-level patterns (buzzwords, hollow transitions, parallel gerunds) are checked by Writing Integrity’s internal diagnostic tools. This file owns the structural ones.

## Tell 1: Repetition-as-thoroughness

The model restates the same clause or mechanic in section after section, because each section "should" mention it. A human contract author states a mechanic once, in the section that owns it, and cross-references it elsewhere. The AI version reads as padded and, worse, creates contradiction risk: when the same rule is written five times in slightly different words, the versions drift and a client's counsel will find the gap.

**How to detect.** Grep for the distinctive verb phrase of each mechanic and count occurrences. In the Tier 1 CPQ SOW, "re-baselines the estimate and timeline through a Change Order before Build proceeds" appeared five times and the full Time-and-Materials billing explanation three times.

**How to fix.** Pick one authoritative home (see `section-ownership.md`). State the mechanic fully there. Everywhere else, either cut it or reduce it to a single pointer sentence: "the basis-of-estimate and Change Order mechanics are stated in Section 7.2." A preview in Section 1 or 2 is allowed, but it is one sentence, not a re-explanation.

**What is NOT this tell.** Defined terms repeating (Change Order, Basis of Estimate, RCA) is contract register and correct. Cross-references repeating is correct. The tell is the *full mechanic* being re-explained, not the *term* recurring.

## Tell 2: Clause-justification

The model states a rule, then adds a sentence explaining why the rule exists. "Provide record counts before execution, so the basis of estimate can be confirmed." "Defects are categorized before Estate commits to resolution." The why-tail reads as the model reassuring itself that the rule is reasonable. A contract states the obligation; it does not argue for it.

**How to fix.** Cut the why-tail. "Provide record counts before SOW execution." Done.

**The exception that matters.** Keep the justification when it defends an *exception* to a default or a *stricter-than-standard* term, because there the reason is what stops the term reading as arbitrary to the client. Two real examples from the Tier 1 SOW that were correctly kept:
- The acceptance window is 10 business days, but the data-migration reconciliation report carries a 3-business-day window "because cutover sequencing depends on it." Cut that reason and the shorter window looks arbitrary and a client pushes back.
- Exhibit A lists binary additions as "Change Orders regardless of size." The "regardless of size" defends a stricter term (no small-change grace) and earns its place.

The test: does the justification defend a deviation, or does it merely restate that the rule is sensible? Defend a deviation, keep it. Restate sensibility, cut it.

## Tell 3: Rule-of-three verb piles and meta-commentary

**Verb piles.** "The engagement does not remediate, re-architect, or add capability." Three verbs where the sentence then gets re-explained by a following sentence covering the same boundary. Collapse to the necessary verbs and delete the follow-on if it repeats.

**Meta-commentary.** Sentences that answer an internal question the client never asked, usually about Estate's own staffing or pricing logic. The clearest case from Tier 1: "Senior-architect oversight beyond the Solution Architect line is enabling and non-billable; there is no separate senior-architect line in the price." A client does not need to be told what is not in the price. Delete it. Same with "because senior roles bill at higher rates, a shift onto senior roles consumes the envelope faster than the hour total alone would suggest", which narrated rate-mix arithmetic the client did not ask for.

**How to detect meta-commentary.** Ask of each sentence: is this an obligation, a boundary, a deliverable, a term, or a definition? If it is none of those, and it is explaining Estate's internal reasoning, it is meta-commentary. Cut it.

## The discipline that makes this stick

Verify with counts, never with an adjective. Before claiming a SOW is clean, grep the repeated mechanics and report the before/after counts. "Clean" is not a feeling; it is "the T&M mechanic now appears once, down from three." If you cannot show the count dropped, you have not done the work.
