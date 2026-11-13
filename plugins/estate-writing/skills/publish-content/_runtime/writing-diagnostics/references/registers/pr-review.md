# Register: pull requests and code review

This register covers PR descriptions, review comments and commit messages, which stay terse, active and factual.

## Rules

- Active voice throughout. "Adds the retry path", not "The retry path is added".
- Commit subjects in the imperative: "Add retry path", "Fix the merge gate".
- Describe what tests cover, not how many. Never "12 tests pass" or "all green"; write "covers the empty-quote and multi-org cases".
- No CI status narration. The pipeline reports itself.
- State the positive. Not "handles X, not Y", just "handles X".
- Cut hedge adverbs such as regardless and nonetheless from the end of a sentence.
- Give each change its own sentence. Reviewers scan, and compound sentences hide the diff.

## What good looks like

> Adds the org-id preflight to every write path. Covers the sandbox-vs-prod
> case and the missing-config case. The guard fails closed when the org cannot
> be confirmed.

## What to avoid

> This PR is added to ensure that the system seamlessly handles a robust set of
> cases. It's worth noting that all 14 tests are passing. The result? Safer
> deploys, not riskier ones.
