#!/usr/bin/env bash
# PreToolUse (Bash) — two refusals about merges, both of which only make sense
# once a pipeline.yml exists:
#
#   1. Never merge INTO an engine-managed environment branch. Promotion into one
#      is the engine's, through a release or an express promotion, so that the
#      promotion is recorded, attributed to tickets, and revertible. A hand merge
#      is none of those.
#
#   2. Never squash or rebase in an engine repo. Selective promotion is
#      `cherry-pick -m 1` and rollback is `revert -m 1`; both need a real merge
#      commit with two parents. Squashing removes the structure they run on, and
#      nothing notices until the day someone needs a rollback.
#
# WHY THIS LIVES HERE AND NOT IN sf-delivery-standards
# ----------------------------------------------------
# Both rules are statements about a pipeline. That skill is deliberately
# topology-agnostic and governs the loop against one org and one trunk; teaching
# it what an environment branch is would be exactly the coupling it avoids. So
# this layer brings its own guard, reads pipeline.yml itself, and requires no
# configuration over there and no awareness from anyone working the local loop.
#
# ONE INTERACTION, AND IT IS A PROJECT CONFIG, NOT A CODE CHANGE
# --------------------------------------------------------------
# sf-delivery-standards' own merge gate has a squash policy, and its default
# (`require`) blocks `--merge`. On an engine repo that would deadlock against
# rule 2 above. The fix uses that skill's EXISTING documented value:
# `git config aleysian.squash prefer` makes its policy advisory, and this hook
# then enforces the stricter, correct rule for a pipeline. scripts/init.sh sets
# it. Nothing in their skill changes.

set -u
. "$(dirname "${BASH_SOURCE[0]}")/_engine-lib.sh"

# Master gate first — see the note in guard-engine-deploy.sh.
gate_or_exit

COMMAND=$(hook_command)
[ -z "$COMMAND" ] && exit 0

# Only PR-merge surfaces. A plain `git merge` on a feature branch is ordinary
# work, and a `git merge` into an environment branch cannot reach the org
# without a push, which the engine's own webhook path then governs.
echo "$COMMAND" | grep -qE '\b(gh[[:space:]]+pr[[:space:]]+merge|glab[[:space:]]+mr[[:space:]]+merge)\b' || exit 0

ENVS=$(pipeline_envs "$PIPELINE")
[ -z "$ENVS" ] && exit 0

# ── rule 2: merge commits only ───────────────────────────────
# Checked first because it needs no network: a wrong merge METHOD is refused
# before we spend a round trip finding out which branch it targets.
if echo "$COMMAND" | grep -qE -- '(--squash|--rebase)'; then
  block \
    "BLOCKED: this repo promotes by cherry-picking merge commits, so squash and" \
    "rebase merges are not available here." \
    "" \
    "  gh pr merge <N> --merge --delete-branch" \
    "" \
    "Selective promotion is 'git cherry-pick -m 1' and rollback is 'git revert -m 1'." \
    "Both need a real merge commit with two parents. A squash produces one commit" \
    "with one parent, so the work becomes neither selectively promotable nor" \
    "cleanly revertible — and nothing surfaces that until someone needs a rollback." \
    "" \
    "Close it at the repo level too, so the web UI button agrees:" \
    "  gh api repos/<owner>/<repo> -X PATCH -f allow_squash_merge=false -f allow_rebase_merge=false"
fi

# ── rule 1: not into an environment branch ───────────────────
BASE=""
if echo "$COMMAND" | grep -qE '\bgh[[:space:]]+pr[[:space:]]+merge\b'; then
  command -v gh >/dev/null 2>&1 || exit 0
  # NO \b HERE. BSD sed (macOS) does not support it: the substitution silently
  # never matches, PR comes back empty, the base lookup returns nothing, and this
  # rule falls open on every merge while the --squash rule keeps working — so the
  # guard looks alive. BSD *grep* does support \b, which is why the detection
  # above is fine and only the extraction was dead. Take the first bare integer
  # after the verb instead; with none, `gh pr view` resolves the current branch's
  # PR, which is the right fallback.
  PR=$(printf '%s' "$COMMAND" | sed -E 's/.*gh[[:space:]]+pr[[:space:]]+merge//' \
    | grep -oE '[0-9]+' | head -1 || true)
  BASE=$(gh pr view $PR --json baseRefName -q .baseRefName 2>/dev/null || true)
elif echo "$COMMAND" | grep -qE '\bglab[[:space:]]+mr[[:space:]]+merge\b'; then
  command -v glab >/dev/null 2>&1 || exit 0
  # Same BSD sed caveat as above — no \b.
  MR=$(printf '%s' "$COMMAND" | sed -E 's/.*glab[[:space:]]+mr[[:space:]]+merge//' \
    | grep -oE '[0-9]+' | head -1 || true)
  BASE=$(glab mr view $MR -F json 2>/dev/null | python3 -c '
import json,sys
try: print(json.load(sys.stdin).get("target_branch","") or "")
except Exception: print("")' || true)
fi

# Fails OPEN on an unreadable base, unlike the deploy guard. The asymmetry is
# deliberate: a merge cannot reach an org on its own — the engine still validates
# the resulting push and can refuse it — whereas a deploy reaches the org
# immediately. Blocking every merge whenever the host CLI is offline would make
# this hook the thing people uninstall.
if [ -z "$BASE" ]; then
  note "note: could not read this merge's target branch, so the engine's" \
       "      environment-branch check did not run."
  exit 0
fi

while IFS=$'\t' read -r br un on; do
  [ -z "$br" ] && continue
  if [ "$BASE" = "$br" ]; then
    block \
      "BLOCKED: '$BASE' is an engine-managed environment branch." \
      "" \
      "Promotion into it belongs to the engine, so that what lands is recorded," \
      "attributed to its tickets, and revertible as a unit. A hand merge is none" \
      "of those: the release ledger never learns the work shipped, and a later" \
      "rollback has no single commit to revert." \
      "" \
      "Promote it properly:" \
      "  scripts/engine.sh release --from <source-env> GH-123 [GH-124 ...]" \
      "" \
      "Shipping everything on the upstream branch instead? That is a normal PR" \
      "from the upstream environment branch, which the engine recognises as a bulk" \
      "promotion and lets through."
  fi
done <<<"$ENVS"

exit 0
