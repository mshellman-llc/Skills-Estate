---
name: code-simplify
description: 'Review and refine the current code change for reuse, clarity, maintainability, and efficiency without changing behavior. Use when a delivery workflow requires a simplify pass, when the user asks to simplify or clean up a diff, or before committing a non-trivial implementation. Scope work to the current branch diff or an explicit target, preserve public behavior and project conventions, apply only high-confidence edits, and verify the result with focused tests. This is the Codex-native equivalent of Claude Code review with fixes, not a prose-style pass.'
---

# Code Simplify

Make the current change easier to understand and maintain without changing what it does. This is
a judgment pass over code, not a formatter, prose rewrite, or license to redesign the feature.

## Scope

Use the explicit target when the caller supplies one. Otherwise inspect:

1. commits ahead of the branch's upstream or merge base;
2. staged and unstaged changes;
3. untracked source files that belong to the change.

Read the repository's `AGENTS.md`, nearby tests, and the surrounding implementation before editing.
Generated output, vendored code, lockfiles, snapshots, and unrelated pre-existing changes stay out
of scope unless the caller explicitly includes them.

## Review lenses

- **Reuse:** replace new duplication with an established local helper or pattern when the fit is
  exact and the result is clearer.
- **Clarity:** reduce needless nesting, indirection, branching, and naming ambiguity.
- **Maintainability:** keep responsibilities narrow, make invariants visible, and remove dead code
  introduced by the current change.
- **Efficiency:** remove repeated or unnecessary work when the improvement is evident and does not
  trade away readability or correctness.

Do not chase cleverness, minimum line count, or speculative abstraction. A slightly longer direct
implementation is better than a compressed one that hides behavior.

## Behavior boundary

Preserve public APIs, data shapes, permissions, ordering, error behavior, logging semantics,
user-facing strings, prompts, test expectations, and integration contracts. Do not weaken checks
or delete apparently redundant safeguards without proving why they are redundant. If a proposed
cleanup would change any of these, report it as a separate recommendation instead of applying it.

## Workflow

1. Establish the diff base and list the files in scope. Stop if the base is ambiguous or the
   repository has overlapping changes that cannot be separated safely.
2. Inspect the diff with enough surrounding code and tests to understand its behavior.
3. Record candidate improvements under the four review lenses. Reject speculative, cosmetic-only,
   or behavior-changing candidates.
4. Apply the smallest coherent set of high-confidence edits.
5. Run the narrowest relevant formatter, static checks, and focused tests. Run broader repository
   gates when its contract requires them.
6. Re-read the final diff against the original intent. Confirm that no unrelated file or protected
   behavior changed.
7. Report applied refinements, verification evidence, and worthwhile candidates deliberately left
   unapplied.

For a review-only request, stop after step 3 and return findings without editing.

## Host routing

OpenAI Codex agents run this skill directly. Current Claude Code can use
`/code-review medium --fix` for the corresponding review-and-apply step, then inspect its resulting
diff and run the repository's required tests. The delivery contract names both routes so it does
not depend on one vendor's built-in command vocabulary.
