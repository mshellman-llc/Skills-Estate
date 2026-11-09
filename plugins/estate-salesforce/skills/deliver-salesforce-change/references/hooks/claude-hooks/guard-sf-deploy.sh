#!/bin/bash
# PreToolUse (Bash) — deploy hygiene. Check the source checkout before a deployment; this does not prove org parity.
#
# Test-level policy is checked by the workflow against the actual target org.
#   3. --source-dir force-app -> whole-tree deploys
#   4. Real deploy off main   -> orphaned deploy if the branch never merges
#   5. Real deploy from a dirty main   -> org receives code that is not in git
#   6. Real deploy from an unsynced main -> org receives code that is not on origin
#
# Dry runs are exempt from 4-6: validating from a worktree IS the merge gate.

set -u
. "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

hook_read_input
COMMAND=$(hook_command_text)

echo "$COMMAND" | grep -qE '\b(sf|sfdx)\b.*\bdeploy\b' || exit 0

# Test level follows the target org and project policy. Broad test runs and
# production validation are supported; this guard must not prohibit them.

# ── 3. whole-tree deploys ────────────────────────────────────
# Blocks bare `force-app`; the documented fresh-scratch-org bootstrap
# (--source-dir force-app/main/default) stays available on purpose.
if echo "$COMMAND" | grep -qE -- '(--source-dir[= ]force-app($|[[:space:]])|-d[[:space:]]+force-app($|[[:space:]]))'; then
  block \
    "BLOCKED: deploying the entire force-app/ tree." \
    "" \
    "Pass one --source-dir per changed file:" \
    "  --source-dir force-app/main/default/classes/MyClass.cls \\" \
    "  --source-dir force-app/main/default/classes/MyClassTest.cls" \
    "" \
    "Whole-tree deploys are slow, surface unrelated failures, and make it impossible" \
    "to tell what the org actually received for this ticket."
fi

# Everything below concerns REAL deploys only.
echo "$COMMAND" | grep -qE -- '--dry-run' && exit 0
echo "$COMMAND" | grep -qE '\bdeploy[[:space:]]+(report|cancel|resume|preview|validate)\b' && exit 0
echo "$COMMAND" | grep -qE '\bdeploy[[:space:]]+(start|quick)\b' || exit 0

BRANCH=$(current_branch ".")
[ -z "$BRANCH" ] && block "BLOCKED: cannot verify the Git checkout for a real deployment."

# ── 4. deploys come from the main checkout, on main ──────────
if [ "$BRANCH" != "main" ] || in_worktree "."; then
  WHERE="branch '$BRANCH'"
  in_worktree "." && WHERE="a worktree (branch '$BRANCH')"
  block \
    "BLOCKED: real deploys run from the main checkout on main — this is $WHERE." \
    "" \
    "The org only ever receives merged code. Deploying a branch creates an" \
    "orphaned deploy the moment that branch changes or never merges." \
    "" \
    "From a worktree, validate (this is the merge gate):" \
    "  sf project deploy start --dry-run --source-dir <changed files> \\" \
    "    --test-level RunSpecifiedTests --tests <TestClasses>" \
    "" \
    "Then squash-merge, and deploy from main:" \
    "  git checkout main && git pull && sf project deploy start ..."
fi

# ── 5. main must be clean where it matters ───────────────────
DIRTY=$(git status --porcelain -- force-app/ 2>/dev/null)
if [ -n "$DIRTY" ]; then
  block \
    "BLOCKED: main has uncommitted force-app/ changes. Deploying now would put" \
    "code in the org that exists nowhere in git." \
    "" \
    "$DIRTY" \
    "" \
    "Commit them through a worktree + PR, or discard them, then deploy."
fi

# ── 6. main must match origin ────────────────────────────────
if ! git rev-parse --verify --quiet origin/main >/dev/null 2>&1; then
  block "BLOCKED: origin/main is unavailable; verify the remote release commit before deploying."
fi
if git rev-parse --verify --quiet origin/main >/dev/null 2>&1; then
  LOCAL=$(git rev-parse main 2>/dev/null)
  REMOTE=$(git rev-parse origin/main 2>/dev/null)
  if [ -n "$LOCAL" ] && [ -n "$REMOTE" ] && [ "$LOCAL" != "$REMOTE" ]; then
    if git merge-base --is-ancestor "$LOCAL" "$REMOTE" 2>/dev/null; then
      block \
        "BLOCKED: local main is BEHIND origin/main. The squash merge is not checked out yet," \
        "so this deploy would send the org an older tree than the one you merged." \
        "" \
        "  git checkout main && git pull" \
        "" \
        "then re-run the deploy."
    else
      block \
        "BLOCKED: local main is AHEAD of origin/main (or has diverged)." \
        "" \
        "Deploying unpushed commits puts code in the org that is not on GitHub —" \
        "the same untraceable-change problem this platform exists to eliminate." \
        "" \
        "  git push        # if these commits are legitimate (e.g. a revert)" \
        "  git log origin/main..main --oneline    # to see what is unpushed"
    fi
  fi
fi

exit 0
