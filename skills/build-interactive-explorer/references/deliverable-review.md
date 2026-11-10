# Review a material visual or interactive deliverable

Use these focused assessments for a material deliverable built with this workflow. Keep simple prose answers and small static edits proportionate. The user's approved visual direction remains the starting point; reviewers identify concrete defects, not permission to redesign by preference.

## Writing integrity

Use the current `review-writing` skill, which owns writing-integrity review. Review the rendered or generated file through its `scripts/extract_review_text.py` procedure. Read all extracted text, including dynamic labels, revealed details and rehearsal answers. If extraction misses reader-visible strings, add them to the review coverage explicitly. Check claims, ownership, unresolved choices and instructions against the controlling sources.

Fix findings in the generator or other owning source, rebuild, extract again, review changed text and retain the coverage receipt. Report files and lines read and changed. A scanner supplements the review; record justified retained warnings without calling the scan clean.

## Visual inspector

Use a separate reviewer to inspect the running deliverable at desktop and narrow widths. Give the reviewer the reader's task, supplied examples, approved direction and relevant constraints. Inspect hierarchy, density, typography, relationships, diagram labels, control placement and meaningful selected or revealed states. Keep context legible as details change. Report observed defects with the view, size and state that reproduces them; distinguish evidence from taste.

## Web-app interaction expert

Use a separate reviewer for task completion in the running deliverable. Give the reviewer the controlling facts and expected outcomes. Exercise relevant flows, exception states, selections, cross-view links, keyboard focus and narrow-screen use. Check where each link lands, whether its target is visible below sticky navigation, and where focus moves when content changes. In rehearsal, verify reveal, next question, progress and return-to-context behavior where implemented.

Coordinate reviewers that share a browser so one does not change the other's state. Their roles may assess in parallel when surfaces are independent.

## Resolve and finish

Verify each finding against the source and running behavior. Repair the owning implementation and retest affected paths. Repeat a review only when a change, failure or unresolved concern warrants it. Keep content, behavior, visual assessment and the user's acceptance separate. State tested sizes and states, unresolved findings and material limits. Do not add unrelated estate-wide review gates to this deliverable check.
