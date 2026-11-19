# Review a material visual or interactive deliverable

Use these focused assessments for a material deliverable built with this workflow. Keep simple prose answers and small static edits proportionate. Preserve the user's approved direction. A first draft has no approval merely because it exists: challenge weak composition, content selection and explanatory structure when the user has not accepted them.

Read [scope, depth and usefulness review](depth-usefulness-review.md) for substantial guides, adaptations and rebuilds. The builder and both reviewers assess the requested work as a whole, not only the best section or the functioning page.

## Writing integrity

Use the current `writing` skill, which owns writing-integrity review. Review the rendered or generated file through its `scripts/extract_review_text.py` procedure. Read all extracted text, including dynamic labels, revealed details and rehearsal answers. If extraction misses reader-visible strings, add them to the review coverage explicitly. Check claims, ownership, unresolved choices and instructions against the controlling sources. Preserve the depth of the explanation: remove filler and repetition without replacing designs, mechanisms, evidence, examples or exceptions with shorter generic prose.

Fix findings in the generator or other owning source, rebuild, extract again, review changed text and retain the coverage receipt. Report files and lines read and changed. A scanner supplements the review; record justified retained warnings without calling the scan clean.

## Judge explanatory value before defect checks

Name the reader's question and demonstrate the answer using the finished output. Explain the mechanism with its actual records, values, owners, handoffs and consequences. A stage list, vendor inventory or collection of generic next questions is insufficient when the task requires understanding how a system or business process works.

Compare the finished explanation with the relevant substantive methods in all supplied references. State why a reference method is inapplicable rather than ignoring it. Use the depth comparison in the linked review procedure; a single strong calculator, diagram or interaction cannot establish completeness of a broader guide. Record the useful method in that reference, where the new output applies it, and where it remains weaker. Inspect the initial view, a meaningful change and return to context. State whether the main explanation is visible before introductory framing consumes the viewport. Describe what a reader can now understand or decide, with a concrete case. A component count or broad assertion that the design fits the benchmark is not comparison evidence. State whether references were inspected in source or rendered form and disclose access limits.

Distinguish a working discussion from rehearsal. In a working briefing, keep the relevant rule, consequence and open choice visible together. Hide an answer only when rehearsal serves the reader's task; remove the quiz pattern when the user rejects it. Keep a focused explanation connected to the requested wider business process, scope and ownership.

## Visual inspector

Judge whether the whole deliverable has comparable explanatory depth and practical value to the supplied examples. Report omitted or superficial systems, designs, assumptions, examples and failure behavior as substantive findings. Inspect important revealed material as well as the first view. A polished presentation of a narrowed scope is insufficient.

Ask a second reviewer to inspect the running deliverable at desktop and narrow widths through its DOM and extracted text: brand-renderer's layout check for overflow, clipping and contrast, and the extracted text and element geometry of each meaningful state. The reviewer takes no screenshots and saves no image files. Supply the reader's task, examples, approved direction and relevant constraints. Inspect hierarchy, density, typography, relationships, diagram labels, control placement and meaningful selected or revealed states. Keep context legible as details change. Report observed defects with the view, size and state that reproduces them; distinguish evidence from taste. Besides defects, judge hierarchy and explanatory value independently, compared with the reference the user named. Challenge empty framing, prose disguised as a diagram, disconnected context and a weak initial composition. If an arrow implies the wrong causal relationship, treat it as a content defect even when it is well aligned.

## Web-app interaction expert

Use a realistic working question that crosses the relevant records, rules, systems and exception paths. Establish whether a reader can answer it using the artifact's actual detail, and identify what remains impossible or requires guessing. A click-through or one successful numerical example is insufficient evidence of a full guide's usefulness.

Assign task completion in the running deliverable to its own reviewer, with the controlling facts and expected outcomes. Exercise relevant flows, exception states, selections, cross-view links, keyboard focus and narrow-screen use. Use a case to judge whether the interaction teaches the mechanism: a changed input or exception should affect the represented relationship, value or consequence, while keeping its context. Working controls alone are insufficient. Check that displayed inputs and calculated results agree, including invalid input and rounding. Check where each link lands, whether its target is visible below sticky navigation, and where focus moves when content changes. In rehearsal, verify reveal, next question, progress and return-to-context behavior where implemented.

Coordinate reviewers that share a browser so one does not change the other's state. Their roles may assess in parallel when surfaces are independent.

## When the host cannot start a separate reviewer

Some hosts have no tool for starting another agent. There the builder runs a recorded single-agent review in place of the two separate reviewers and marks the independent-review gate pending. It does not count its own pass as independent.

Run the review by DOM, extracted text and keyboard. Cover both reviewer scopes above: the layout check at both widths, each state a reader can open, and the realistic working question with its flows, exception states, links and focus order. Open each revealed state and compare its text with the controlling sources: the values, owners, rules and consequences it states. A mechanical DOM check confirms that a state opens; it cannot show that the revealed content is true. Take no screenshots.

Write the review record before delivery. It names the host limit, the states and sizes checked, each finding and its repair, and the revealed states compared with which sources. Queue the independent review as an open item for a host that can start reviewers, with the brief, supplied examples and sources the reviewers will need. Report the gate as pending, never as passed, until that review runs. The user can still accept the deliverable in the meantime; keep that acceptance separate from the pending gate.

## Resolve and finish

Verify each finding against the source and running behavior. Repair the owning implementation and retest affected paths. Repeat a review only when a change, failure or unresolved concern warrants it. Keep content, behavior, visual assessment and the user's acceptance separate. Begin with a whole-deliverable depth/usefulness verdict: sufficient, partial or insufficient, supported by exact locations and missing content. Then report three distinct outcomes: explanatory quality against the named reference, functional defects and their repairs, and the user's acceptance. "No blockers" is a defect disposition, not a quality verdict. A user rejection makes the deliverable unsuccessful even when routing, reviewer invocation and browser checks pass. State tested sizes and states, unresolved findings and material limits. Do not add unrelated estate-wide review gates to this deliverable check.
