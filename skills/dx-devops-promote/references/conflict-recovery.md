# DevOps Center stale-branch recovery

Use this workflow when a target stage advanced after the WI branch was created, validation reports
a VCS conflict, or the existing PR is not mergeable.

1. Confirm the linked WI worktree is clean. Fetch the remote and resolve the exact current target
   stage tip. Do not check out or mutate the target stage locally.
2. Inspect before mutation where possible:
   ```bash
   git fetch origin <target-stage-branch>
   BASE=$(git merge-base HEAD origin/<target-stage-branch>)
   git merge-tree "$BASE" HEAD origin/<target-stage-branch>
   git diff --name-status "$BASE"..origin/<target-stage-branch>
   ```
3. In the existing WI worktree, merge the target stage into the WI branch:
   ```bash
   git merge --no-ff origin/<target-stage-branch>
   ```
   Never reverse this direction. Never merge the WI branch locally into `staging`, `main`, or any
   other pipeline stage.
4. Resolve conflicts from the current stage baseline. Preserve comprehensive shared tests and
   configuration already promoted to the stage, then fold the WI-specific behavior into that
   baseline. Do not restore the stale WI copy wholesale. Inspect `git diff --name-only
   --diff-filter=U` while resolving and `git diff --cached MERGE_HEAD` before committing.
5. Run focused checks for the reconciled behavior and the full repository quality suite. Commit
   the merge, then run a scoped Salesforce deployment dry run from the clean worktree so the
   evidence identifies that exact commit.
6. Push the same WI branch. Keep the existing PR. Verify its head SHA, base branch, clean merge
   state, and mergeability. For GitHub, inspect `gh pr view --json
   headRefOid,baseRefName,mergeStateStatus,mergeable,url`; require the expected head/base,
   `mergeStateStatus` of `CLEAN`, and `mergeable` of `MERGEABLE`.
7. Run `sf devops promotion validate` again for the exact work-item set and target stage. Promotion
   may use `--skip-validation` only if that validation passed in this session and no relevant Git,
   PR, or DevOps Center state changed afterward.

The delivery-standards pre-commit hook scopes a recognized stage-sync merge to the net WI delta
relative to `MERGE_HEAD`. If a complex chained repository hook cannot consume the same base, use
the recorded `git commit --no-verify` escape only with independent evidence: the net file list,
focused gates, full suite, and exact-commit Salesforce dry run.
