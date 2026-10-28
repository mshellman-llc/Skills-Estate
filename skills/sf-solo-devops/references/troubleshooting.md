# Troubleshooting — Common Failure Modes and Recovery

## Validation Fails

**Symptom:** `sf project deploy start --dry-run` returns errors.

**Action:** Stay in the worktree. Fix the issue, re-commit, re-validate. Do not merge until validation passes. Common causes:
- Missing test coverage for new Apex
- Apex test failures (query changed data, missing test data setup)
- Metadata dependency not included in `force-app/` (e.g., referenced field doesn't exist yet)
- Permission set references a field that hasn't been created

## Deploy Fails After Merge (rare)

**Symptom:** Validation passed from the worktree, squash merge succeeded, but `sf project deploy start` from main fails.

**Why it's rare:** Validation runs the same checks as deploy. But it can happen if the org changed between validate and deploy, or if the squash merge introduced a subtle conflict.

**Priority:** Restore `main == org` immediately. Do not leave main ahead of the org while you debug.

**Decision: revert or fix forward?**

- **Fix forward** if you can identify and fix the issue in under 5 minutes (typo, missing field, obvious error). New worktree, fix, validate, merge, deploy.
- **Revert** if you need time to investigate:
  ```bash
  # 1. Revert the broken commit on main
  git revert HEAD --no-edit
  git push

  # 2. Deploy the reverted state — restores main == org
  sf project deploy start --source-dir <same files> \
    --test-level RunSpecifiedTests --tests <same list>

  # 3. Rebase the worktree off the reverted main and debug there
  cd <worktree-path>
  git fetch origin && git rebase origin/main
  # ... fix the issue, then go through normal validate → merge → deploy
  ```

**Either way:** Open a new GitHub issue for the deploy failure. Close it (and the original issue) once the fix is deployed.

## Worktree Doesn't Have the Right Org

**Symptom:** `sf project deploy start --dry-run` targets the wrong org or fails with "No default org set."

**Cause:** Worktrees don't inherit the parent repo's `.sf/config.json` (`.sf/` is gitignored).

**Normally self-healing.** `ensure-worktree-config.sh` sets `target-org` from the main clone the first time an `sf` command runs in a worktree, and says so when it does. If you see this symptom anyway, the main clone has no alias to copy:

```bash
sf config set target-org=<ORG_ALIAS>     # in the MAIN clone first
cd <worktree-path>
sf config set target-org=<ORG_ALIAS>     # then here, or just re-run your sf command
```

> Do **not** try to solve this with a `WorktreeCreate` hook. That event makes worktrees rather than reacting to them, and configuring one in a git repo breaks every `isolation: "worktree"` agent at spawn. See [hooks/README.md](hooks/README.md).

## `gh auth` on Wrong Account

**Symptom:** `gh pr create` fails with permission errors, or the PR is created under the wrong account.

**Fix:**
```bash
gh auth status                          # See which account is active
gh auth switch --user <CORRECT_ACCOUNT> # Switch
```

Remember to switch back to your default account after GitHub operations.

## Pre-commit Hook Blocks Commit on Main

**Symptom:** `git commit` on `main` fails with "Cannot commit force-app/ changes directly to main."

**This is working as intended.** The hook prevents direct commits to `main` for deployable code. Create a worktree:
```bash
git stash
git worktree add ../project-fix -b fix/N-description
cd ../project-fix
git stash pop
```

## Claude Hook Blocks Edit/Write on force-app/

**Symptom:** Edit or Write tool call fails with "BLOCKED: Cannot modify force-app/ files from the main project root."

**This is working as intended.** `guard-force-app.sh` prevents authoring deployable source outside a worktree.

It judges the **file path**, not your shell's cwd — so writing into a worktree from anywhere is fine, and a worktree created outside `.claude/worktrees/` counts just as much. Check which side of the line a directory is on with one plain command:

```bash
git rev-parse --absolute-git-dir
```

`…/<repo>/.git` is the main checkout; `…/<repo>/.git/worktrees/<name>` is a worktree.

**If you ARE in a worktree and still get blocked**, the path you are writing to is probably not the one you think — read the block message, which lists each offending path after resolving it.

The Bash companion (`guard-force-app-bash.sh`) also allows `rm` of **untracked** `force-app/` paths in the main checkout: a stray untracked file there is a deploy hazard, not something to protect. Tracked paths are never removable this way.

## Claude Hook Blocks Deploy Command

**Symptom:** a `sf project deploy` Bash call is blocked by `guard-sf-deploy.sh`.

**All of these are working as intended.** Each block message names the fix; the short version:

| Block | Fix |
|---|---|
| `RunLocalTests` / `RunAllTestsInOrg` | `--test-level RunSpecifiedTests --tests A B`, or `NoTestRun` if nothing can affect Apex results |
| whole `force-app/` tree | one `--source-dir` per changed file |
| `deploy validate` | `deploy start --dry-run` (validate rejects `NoTestRun`) |
| real deploy off `main` | dry-run from the worktree; deploy after the squash merge |
| `main` has uncommitted `force-app/` | commit through a worktree + PR, or discard, then deploy |
| local `main` behind `origin/main` | `git checkout main && git pull` |
| local `main` ahead of `origin/main` | `git push` first — unpushed code must not reach the org |

## Merge Blocked: No Recorded Validate

**Symptom:** `gh pr merge` is blocked with "commit `<sha>` has no recorded validate".

The merge gate is **per-commit**. `record-validate.sh` logs the SHA of each successful dry run, and `guard-pr-merge.sh` requires the PR's head commit to be in that log. Usual causes, in order of likelihood:

1. You validated, then committed again. Re-run the dry run.
2. The last commit is not pushed — `gh` reads the remote tip, not your local HEAD. Push, then re-validate if the SHA moved.
3. The dry run did not actually succeed. Check the output for `Status: Failed`; only successes are recorded.
4. You validated in a different clone. The log is machine-local by design.

If the org is genuinely unavailable, `SOLO_ALLOW_UNVALIDATED_MERGE=1 gh pr merge --squash ...` — and say so on the ticket.

## Close Blocked: "No Deploy Has Ever Been Recorded"

**Symptom:** `gh issue close N` is blocked because `.claude/.deploy-log` is missing or does not mention the ticket — but you *did* deploy.

**Do not hand-write an entry to get past it.** That gate is the only thing standing between a closed ticket and an org that never received the code; typing in a sha defeats it. Ask the org what it actually received:

```bash
sf data query --use-tooling-api -q \
  "SELECT Id, Status, CheckOnly, CreatedDate, NumberComponentsTotal FROM DeployRequest \
   WHERE CheckOnly = false AND Status = 'Succeeded' ORDER BY CreatedDate DESC LIMIT 20"
```

`CheckOnly = false` is the important filter — dry runs are `DeployRequest` rows too, and they are not proof of anything. Cross-reference each timestamp with `git reflog --date=format:'%H:%M:%S'` to find the sha that was `HEAD` when it ran, then rewrite `<sha> <job-id> <utc stamp>` lines in chronological order. Reconstructing a verified fact is fine; inventing one is not.

**Then find out why it went missing**, because the log does not delete itself:

1. **A test harness.** Far and away the most common cause — see the warning in [hooks/README.md](hooks/README.md). A suite that runs against the live repo and tidies up after itself will delete this file, and the resulting block looks exactly like a hook bug.
2. `git clean -fdx` — the `-x` also removes ignored files. `-fd` alone leaves them.
3. A fresh clone. The log is machine-local by design; a new clone has no history against the org.

## Ticket Has Duplicate or Phantom "Deployed" Comments

**Symptom:** a ticket carries several identical `Deployed to the org at <sha>` comments, or one naming a commit you never deployed.

**Check the org first** — `DeployRequest` (query above) is the record of what really happened. If no real deploy matches the timestamp, nothing was deployed and the comment is spurious.

Causes, in order of likelihood:

1. **A test harness ran `auto-label-deploy.sh` for real.** It does not merely inspect the ticket, it **executes** `gh issue edit` and `gh issue comment`. Feed it a synthetic success payload from a clone whose `origin` still resolves to the real GitHub project and it posts to real tickets. Stub `gh` on `PATH`.
2. **Re-reporting the same deploy.** The ticket comment is gated on the same idempotency check as the log write, so a repeated `deploy report` should not add one. If you see duplicates, that check is what to look at.

Spurious comments are worth deleting (`gh api -X DELETE repos/{owner}/{repo}/issues/comments/<id>`) — an audit trail nobody trusts is not one.

## Turn Won't End: Definition of Done

**Symptom:** the Stop hook reports incomplete DoD items and the turn continues.

It found one of two things: `main` ahead of the org, or a deployed ticket still open. Each comes with its command. It reports each distinct state only once, so finishing the work — or telling the user plainly what you are leaving open and why — both end the loop. "Deployed, waiting on your testing before I close #N" is a complete answer. `SOLO_SKIP_DOD=1` disables it.

It says nothing about open worktrees. Keeping one alive after a deploy for follow-up fixes on the same ticket is a supported way to work; `session-status.sh` reports open worktrees at session start instead.

## A Guard Blocked Something Harmless

**Symptom:** a guard fires on a command that only *mentions* a blocked pattern — a commit message, a doc, an echo.

Guards read the command with heredoc bodies stripped and match paths on token boundaries, so most prose is already safe. If one still misfires, that is a **bug in the guard, not a reason to route around it** — a guard people work around is a guard they eventually disable. Move the text into a heredoc or a file, and fix the pattern in the hook.

## `sf project retrieve` is Blocked

**Symptom:** Any `sf project retrieve start` command is denied.

**This is working as intended.** The deny rule in `.claude/settings.json` prevents accidental org-to-source pulls that could overwrite local changes. If you genuinely need to retrieve, ask the user to temporarily allow it.

## Jest Tests Fail

**Symptom:** `npm test` fails before you even get to org validation.

**Action:** Fix the tests first. Common causes:
- Import paths changed (LWC module resolution)
- Mock data doesn't match updated component expectations
- New `@wire` adapter not mocked

## Stale Worktree After Main Moves Ahead

**Symptom:** You've been working in a worktree for a while, and `main` has moved forward (other PRs merged).

**Action:** Rebase or merge main into your worktree branch:
```bash
cd <worktree-path>
git fetch origin
git rebase origin/main
```

If there are conflicts, resolve them. Then re-validate before merging.

## Squash Merge Overwrites Previous PR's Changes

**Symptom:** Two worktrees branched from the same main commit, both touched the same file. The second squash merge replaces the first PR's changes entirely.

**Prevention:** This is why the workflow mandates one active worktree per file. If you must have parallel worktrees, ensure they touch different files. After merging one, rebase the other before merging.

**Recovery:** If it already happened, the lost changes are in the git history. Cherry-pick or manually reapply from the first PR's commit.

## Concurrent Deploy Collision

**Symptom:** `sf project deploy report` shows results for a job you didn't start, or your deploy seems to have been cancelled/superseded.

**Cause:** You used `--use-most-recent` (or the CLI defaulted to it) and another agent's deploy was the latest.

**Fix:** Always capture and use the job ID:
```bash
DEPLOY_RESULT=$(sf project deploy start --source-dir <files> \
  --test-level RunSpecifiedTests --tests <tests> --json --async)
JOB_ID=$(echo "$DEPLOY_RESULT" | jq -r '.result.id')
sf project deploy report --job-id "$JOB_ID"
```

**Never use `--use-most-recent`.**

## Nested Worktree Catastrophe

**Symptom:** Every Bash command fails, even `cd /`. The session is unrecoverable.

**Cause:** A worktree was created inside another worktree. When the outer worktree was cleaned up, the inner one's path was deleted, and the Bash CWD now points to a non-existent directory.

**Recovery:** There is no in-session recovery. The user must:
1. Close the conversation
2. Manually clean up leftover worktrees: `git worktree list` then `git worktree remove <path>` for orphaned entries
3. Start a new conversation

**Bash inside a worktree-isolated agent is sandboxed by the harness.** It refuses anything it cannot prove stays inside the worktree — `&&`/`;` chains, `cd … && for …`, and `<<'EOF'` heredocs (read as redirects):

> `…is too complex to verify that it stays inside the worktree; break it into plain, separate commands`

That is **Claude Code, not this project's hooks** — there is nothing to find in `.claude/hooks/`, and it is **not** a stop-and-report condition. Split into plain commands, or write a script to the scratchpad and run it by path.

**Prevention:** Never create a worktree inside another worktree. `guard-worktree-nesting.sh` blocks it, and the same check works by hand — it is git topology, not a path pattern, so a worktree created anywhere counts:

```bash
git rev-parse --absolute-git-dir
```
Read the answer off the path: `…/<repo>/.git` is the main checkout, `…/<repo>/.git/worktrees/<name>` is a worktree. This is the same topology the hooks use, so it cannot disagree with them.


## Agent Skipped a Step

**Symptom:** Agent deployed without validating, merged without tests, or reported "done" without closing the ticket.

**Action:** This skill exists to prevent exactly this. If you're reviewing an agent's work and notice a skipped step:
1. Check if validation actually ran (look for `sf project deploy start --dry-run` in the conversation)
2. Check if tests passed
3. Check if the GitHub issue was closed
4. Check if the worktree was removed
5. If any step was skipped, do it now before considering the task complete

## Rollback Poisoning (Coverage Failure)

**Symptom:** Deploy fails on COVERAGE (tests pass but coverage < 75%). Next deploy fails with "Method does not exist" or "Dependent class needs recompilation."

**Cause:** Salesforce rolled back ALL deployed classes, leaving the org with stale versions that can't compile against each other.

**Fix:** Re-deploy all affected classes together with `--ignore-conflicts`:
```bash
sf project deploy start \
  --source-dir force-app/main/default/classes/AffectedClass.cls \
  --source-dir force-app/main/default/classes/AffectedClassDependency.cls \
  --test-level RunSpecifiedTests --tests AffectedClassTest \
  --ignore-conflicts
```

## CLAUDE.md Missing in a Worktree

**Symptom:** An agent in a worktree behaves as if it's never seen the project's workflow rules — no ticket-first discipline, no worktree awareness, no invariant mentioned.

**Cause:** `CLAUDE.md` is gitignored or otherwise untracked. `git worktree add` only materializes tracked content from the branch's tree — untracked/gitignored files never propagate into a new worktree, silently.

**Fix:** Confirm `CLAUDE.md` is committed (`git ls-files CLAUDE.md` should return it). If it's gitignored, remove that entry, commit the file, and push. If there's personal content mixed in that shouldn't be shared, split it into a separate untracked file — the workflow rules themselves aren't personal and need to be committed to function at all.
