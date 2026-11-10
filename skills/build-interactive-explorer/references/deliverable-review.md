# Review a material visual or interactive deliverable

Use these focused assessments for a material deliverable built with this workflow. Keep simple prose answers and small static edits proportionate. Preserve the user's approved direction. A first draft has no approval merely because it exists: challenge weak composition, content selection and explanatory structure when the user has not accepted them.

## Writing integrity

Use the current `review-writing` skill, which owns writing-integrity review. Review the rendered or generated file through its `scripts/extract_review_text.py` procedure. Read all extracted text, including dynamic labels, revealed details and rehearsal answers. If extraction misses reader-visible strings, add them to the review coverage explicitly. Check claims, ownership, unresolved choices and instructions against the controlling sources.

Fix findings in the generator or other owning source, rebuild, extract again, review changed text and retain the coverage receipt. Report files and lines read and changed. A scanner supplements the review; record justified retained warnings without calling the scan clean.

## Judge explanatory value before defect checks

Name the reader's question and demonstrate the answer using the finished output. Explain the mechanism with its actual records, values, owners, handoffs and consequences. A stage list, vendor inventory or collection of generic next questions is insufficient when the task requires understanding how a system or business process works.

Compare the finished explanation with at least one named supplied reference. Record the useful method in that reference, where the new output applies it, and where it remains weaker. Inspect the initial view, a meaningful change and return to context. State whether the main explanation is visible before introductory framing consumes the viewport. Describe what a reader can now understand or decide, with a concrete case. A component count or broad assertion that the design fits the benchmark is not comparison evidence. State whether references were inspected in source or rendered form and disclose access limits.

Distinguish a working discussion from rehearsal. In a working briefing, keep the relevant rule, consequence and open choice visible together. Hide an answer only when rehearsal serves the reader's task; remove the quiz pattern when the user rejects it. Keep a focused explanation connected to the requested wider business process, scope and ownership.

## Visual inspector

Use a separate reviewer to inspect the running deliverable at desktop and narrow widths. Give the reviewer the reader's task, supplied examples, approved direction and relevant constraints. Inspect hierarchy, density, typography, relationships, diagram labels, control placement and meaningful selected or revealed states. Keep context legible as details change. Report observed defects with the view, size and state that reproduces them; distinguish evidence from taste. Give an independent judgment of hierarchy and explanatory value against the named reference, in addition to defects. Challenge empty framing, prose disguised as a diagram, disconnected context and a weak initial composition. If an arrow implies the wrong causal relationship, treat it as a content defect even when it is well aligned.

## Web-app interaction expert

Use a separate reviewer for task completion in the running deliverable. Give the reviewer the controlling facts and expected outcomes. Exercise relevant flows, exception states, selections, cross-view links, keyboard focus and narrow-screen use. Use a case to judge whether the interaction teaches the mechanism: a changed input or exception should affect the represented relationship, value or consequence, while keeping its context. Working controls alone are insufficient. Check that displayed inputs and calculated results agree, including invalid input and rounding. Check where each link lands, whether its target is visible below sticky navigation, and where focus moves when content changes. In rehearsal, verify reveal, next question, progress and return-to-context behavior where implemented.

Coordinate reviewers that share a browser so one does not change the other's state. Their roles may assess in parallel when surfaces are independent.

## Resolve and finish

Verify each finding against the source and running behavior. Repair the owning implementation and retest affected paths. Repeat a review only when a change, failure or unresolved concern warrants it. Keep content, behavior, visual assessment and the user's acceptance separate. Report three distinct outcomes: explanatory quality against the named reference, functional defects and their repairs, and the user's acceptance. "No blockers" is a defect disposition, not a quality verdict. A user rejection makes the deliverable unsuccessful even when routing, reviewer invocation and browser checks pass. State tested sizes and states, unresolved findings and material limits. Do not add unrelated estate-wide review gates to this deliverable check.
