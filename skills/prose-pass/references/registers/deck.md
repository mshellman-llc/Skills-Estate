# Register: slide decks and presentation copy

Decks carry different generated-writing patterns than prose. The trap is the opposite of wordiness: over-correcting into clipped fragments and gimmick labels that read *more* artificial, not less. These rules were learned on a real Aleysian deck where a prose pass produced "$87,900, firm. This is the SOW." and headers like "Wear math, automated" — both rejected as obvious AI slop. The 2025-26 deck literature confirms the diagnosis: AI-deck tells are *sameness* (fixed grids, identical card structures, "statistical average of all presentations" content) and label-headers that say nothing ("Overview," "Key Takeaways") — never wordiness.

## Writing rules

**Full sentences, not label fragments.** Every support line is a complete, declarative sentence in the consultant voice. "$87,900, detailed in the attached Statement of Work." — not "$87,900, firm. This is the SOW." Punchy is good; choppy is a tell. Staccato fragmentation ("Period." energy) reads as a machine trying to sound human. A slide deck is not an excuse to drop verbs.

**No gimmick headers, no label headers.** Two failure modes, one fix. Gimmick: "Wear math, automated," "Open the door" — taglines and winks. Label: "Overview," "Key Takeaways," "Our Approach" — headers that tell the audience nothing. Write headers that carry the slide's actual point: "Automated wear projections," "Provide access and data," "Approvals average 5-7 days."

**Watch the colon tic.** Avoiding em dashes breeds "X: Y" constructions on every line. The scanner reports colon density. A label ("Version 1: Foundation") earns one; body lines rarely do.

**Break symmetry with words, not truncation.** Repeated stock lines (a card opening "Everything in Version 1" three times) and identical noun-phrase headers across blocks signal templating — the documented "AI deck uncanny valley." Fix by writing each one specifically, not by chopping into fragments.

**Respect the box.** Slide text frames have hard vertical limits. On the Aleysian template the vertical-step support box holds about two lines; a card support box a few short lines. The line budget is a writing constraint — cut words to fit, keeping whole sentences.

## QA — not done until rendered

1. Convert to PDF or images and inspect every slide: text overflow, header-over-body overlap, leftover placeholder copy, missing A-mark or footer. Text that scans clean in source can still collide on the slide.
2. Extract the deck text and run the scanner (same gate as contract docs): section-sign 0, em-dash 0 in authored copy (verbatim source values like a client's opportunity name exempt).
3. Run `--tie-out` against the pricing/scoping source. Deck figures drift from SOW figures more than any other artifact pair — every number on a slide must tie.

## Worked example

Input (slide): Header "The number" / Support "$87,900, firm. This is the SOW. 12 weeks. Done."

Rewrite: Header "Fixed-fee investment" / Support "$87,900 fixed fee, delivered over 12 weeks and detailed in the attached Statement of Work."

Why it works: the header states the point plainly; the support line is one complete sentence carrying all three specifics; nothing was truncated to fake punchiness.
