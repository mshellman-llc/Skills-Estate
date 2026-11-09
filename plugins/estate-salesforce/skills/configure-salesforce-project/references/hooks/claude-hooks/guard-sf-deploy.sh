#!/bin/bash
# PreToolUse (Bash) — deploy hygiene. Everything here protects main === org.
#
#   1. `deploy validate`      -> use `deploy start --dry-run` (validate rejects NoTestRun)
#   2. RunLocalTests / RunAllTestsInOrg -> 20+ minute org-wide runs
#   3. --source-dir force-app -> whole-tree deploys
#   4. Real deploy off trunk  -> orphaned deploy if the branch never merges
#   5. Real deploy from a dirty trunk   -> org receives code that is not in git
#   6. Real deploy from an unsynced trunk -> org receives code not on the remote
#
# Dry runs are exempt from 4-6: validating from a worktree IS the merge gate.
#
# "trunk" is estate.trunk, not the literal string main. On a shared client repo
# where each consultant owns a sandbox, trunk is sandbox/<alias> and the invariant
# is `my sandbox branch === my sandbox org` — the same rule, a different branch.
# Check 6 is skipped when estate.host=none: there is no remote to be behind, and
# blocking on a missing origin would make local-only mode unusable.

set -u
HOOK_DEFER_GATE=1   # the master gate fires in hook_read_input, once the target repo is known
. "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

hook_read_input
COMMAND=$(hook_command_text)

echo "$COMMAND" | grep -qE '\b(sf|sfdx)\b.*\bdeploy\b' || exit 0

# ── 1. validate vs dry-run ───────────────────────────────────
if echo "$COMMAND" | grep -qE '\bdeploy[[:space:]]+validate\b'; then
  block \
    "BLOCKED: 'deploy validate' is the production quick-deploy path and rejects NoTestRun." \
    "" \
    "Use the dry run instead — it accepts every test level:" \
    "  sf project deploy start --dry-run --source-dir <changed files> \\" \
    "    --test-level RunSpecifiedTests --tests <TestClasses>" \
    "" \
    "See https://github.com/forcedotcom/cli/issues/2470"
fi

# ── 2. org-wide test levels ──────────────────────────────────
for LEVEL in RunLocalTests RunAllTestsInOrg; do
  if echo "$COMMAND" | grep -qi "$LEVEL"; then
    block \
      "BLOCKED: --test-level $LEVEL runs every test in the org (20+ min)." \
      "" \
      "Name the tests that cover the changed classes:" \
      "  --test-level RunSpecifiedTests --tests FooServiceTest BarServiceTest" \
      "" \
      "Not sure which:  grep -rl \"FooService\" force-app --include=\"*Test.cls\"" \
      "Nothing in the change can affect Apex results (metadata, CSS/HTML, labels)?" \
      "  --test-level NoTestRun"
  fi
done

# ── 3. whole-tree deploys ────────────────────────────────────
# Blocks bare `force-app`; the documented fresh-scratch-org bootstrap
# (--source-dir force-app/main/default) stays available on purpose.
#
# Three things the token must tolerate, each of which used to walk straight
# through this check and deploy the entire tree:
#
#   a QUOTE around the path      --source-dir "force-app"   (quoted paths are the
#                               norm in this stack — see command_repo_dir() and
#                               source_tree_root() in _lib.sh for why)
#   a TRAILING SLASH            --source-dir force-app/
#   both                        --source-dir "force-app/"
#
# `force-app/?` followed by (quote|space|end) is what distinguishes those from the
# bootstrap: in force-app/main/default the character after the slash is `m`, which
# closes no alternative, so that path still passes.
if echo "$COMMAND" | grep -qE -- '(--source-dir[= ]|-d[[:space:]]+)("|'"'"')?force-app/?("|'"'"'|$|[[:space:]])'; then
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
echo "$COMMAND" | grep -qE '\bdeploy[[:space:]]+(report|cancel|resume|preview|quick)\b' && exit 0
echo "$COMMAND" | grep -qE '\bdeploy[[:space:]]+start\b' || exit 0

BRANCH=$(current_branch ".")
[ -z "$BRANCH" ] && exit 0
TRUNK=$(trunk)

# DevOps Center owns the stage branches. A real local deploy is useful only as a
# WI feedback loop against the configured development org, from the same worktree
# and committed WI branch that will be pushed for review.
if is_devops_center; then
  if is_devops_shared; then
    block \
      "BLOCKED: local real deploys are disabled for a shared DevOps Center development org." \
      "" \
      "Open the validated dev/WI pull request to '$(devops_integration_branch)'. The" \
      "centralized landing coordinator serializes the merge and deployment, then" \
      "publishes the successful '$(devops_environment)' GitHub Deployment receipt." \
      "" \
      "A local deploy cannot hold the cross-clone lease or publish authoritative state."
  fi
  if ! printf '%s\n' "$BRANCH" | grep -qE "$(devops_branch_pattern)"; then
    block \
      "BLOCKED: a real local deploy in DevOps Center mode must come from a WI branch." \
      "" \
      "Current branch: $BRANCH" \
      "Move the DevOps Center work item to In Progress, fetch the exact WI-######" \
      "branch it creates, and work from a linked worktree on that branch."
  fi
  in_worktree "." || block \
    "BLOCKED: a real local deploy in DevOps Center mode must run from the WI worktree." \
    "" \
    "The main checkout holds pipeline branches and is inspection-only for force-app/."
  DIRTY=$(git status --porcelain -- force-app/ 2>/dev/null)
  [ -z "$DIRTY" ] || block \
    "BLOCKED: commit the WI source before the real development-org deploy." \
    "" \
    "$DIRTY" \
    "" \
    "Validation and deployment evidence must identify an immutable WI commit."
  exit 0
fi

# ── 4. deploys come from the main checkout, on trunk ─────────
if [ "$BRANCH" != "$TRUNK" ] || in_worktree "."; then
  WHERE="branch '$BRANCH'"
  in_worktree "." && WHERE="a worktree (branch '$BRANCH')"
  block \
    "BLOCKED: real deploys run from the main checkout on '$TRUNK' — this is $WHERE." \
    "" \
    "The org only ever receives merged code. Deploying a branch creates an" \
    "orphaned deploy the moment that branch changes or never merges." \
    "" \
    "From a worktree, validate (this is the merge gate):" \
    "  sf project deploy start --dry-run --source-dir <changed files> \\" \
    "    --test-level RunSpecifiedTests --tests <TestClasses>" \
    "" \
    "Then land it on '$TRUNK' and deploy from there:" \
    "  git checkout $TRUNK && git pull && sf project deploy start ..."
fi

# ── 5. main must be clean where it matters ───────────────────
DIRTY=$(git status --porcelain -- force-app/ 2>/dev/null)
if [ -n "$DIRTY" ]; then
  block \
    "BLOCKED: '$TRUNK' has uncommitted force-app/ changes. Deploying now would put" \
    "code in the org that exists nowhere in git." \
    "" \
    "$DIRTY" \
    "" \
    "Commit them through a worktree + PR, or discard them, then deploy."
fi

# ── 6. trunk must match the remote (skipped when there is no remote) ──
[ "$(host)" = "none" ] && exit 0

# Refresh origin/<trunk> FIRST, best-effort. Without this the comparison below
# reads a cached ref, so a deploy passes against a teammate's push it never saw —
# exactly the stale-deploy this check exists to stop on a shared org + branch. The
# fetch is timed and non-fatal: if it cannot reach the remote, we fall back to the
# cached ref (same behaviour as before this line) rather than block on a blip.
fetch_trunk 8 || true

if git rev-parse --verify --quiet "origin/$TRUNK" >/dev/null 2>&1; then
  LOCAL=$(git rev-parse "$TRUNK" 2>/dev/null)
  REMOTE=$(git rev-parse "origin/$TRUNK" 2>/dev/null)
  if [ -n "$LOCAL" ] && [ -n "$REMOTE" ] && [ "$LOCAL" != "$REMOTE" ]; then
    if git merge-base --is-ancestor "$LOCAL" "$REMOTE" 2>/dev/null; then
      block \
        "BLOCKED: local $TRUNK is BEHIND origin/$TRUNK. The merge is not checked out yet," \
        "so this deploy would send the org an older tree than the one you merged." \
        "" \
        "  git checkout $TRUNK && git pull" \
        "" \
        "then re-run the deploy."
    else
      block \
        "BLOCKED: local $TRUNK is AHEAD of origin/$TRUNK (or has diverged)." \
        "" \
        "Deploying unpushed commits puts code in the org that is not on GitHub —" \
        "the same untraceable-change problem this platform exists to eliminate." \
        "" \
        "  git push        # if these commits are legitimate (e.g. a revert)" \
        "  git log origin/$TRUNK..$TRUNK --oneline    # to see what is unpushed"
    fi
  fi
fi

exit 0
