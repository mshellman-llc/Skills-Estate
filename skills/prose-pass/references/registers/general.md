# Register: general human-facing prose

Use this register when no narrower one fits. It covers conversation, status updates, tickets,
issue bodies, UI copy, code comments, and human-facing runbooks or internal notes.

## Rules

- Lead with the answer, decision, action, or observed fact. Put background after it only when the reader needs that background to act.
- Carry one subject-specific detail in every sentence: a name, number, system, owner, consequence, constraint, or clear judgment. Cut sentences that could move unchanged to another task.
- Match the surface. A validation message names the failed field and the recovery action. A code comment explains a non-obvious constraint. A status update names the completed work and blocker.
- Preserve uncertainty at its actual level. Write `unknown`, name the missing evidence, or state the condition that would change the conclusion.
- Use bullets only when the content is a list. Do not turn prose into symmetrical cards or bullets whose bold opening repeats the sentence that follows.
- Vary sentence and paragraph length. Avoid manufactured fragments, rhetorical questions, triads, and one-line drama written to sound informal.
- End when the substance ends. Cut generic offers to help, recap paragraphs, and closers that add no next action.

## Surface checks

- Conversation and status: answer the current request directly; do not narrate compliance with the request or praise the method.
- Tickets and issues: state the observed behavior, expected behavior, evidence, and acceptance condition only when each is known.
- UI copy: name the object and next action within the available space; never trade accuracy for a slogan.
- Code comments: explain the decision or invariant. Do not restate the code.
