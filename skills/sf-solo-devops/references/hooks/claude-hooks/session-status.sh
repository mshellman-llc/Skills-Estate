#!/bin/bash
# SessionStart — put the workflow's actual state in front of the agent before it
# does anything, because every wrong assumption here is expensive:
#   "I'm on main"        -> edits force-app in the main checkout
#   "the org matches"    -> closes a ticket whose code never deployed
#   "no worktrees open"  -> creates a second one for the same ticket
#
# Local git only: no network, no gh, no sf. SessionStart output is added to the
# agent's context, so this stays short and factual.
#
# Two rules for anything written here:
#   - Self-attribute. This lands in context with nothing marking it as
#     machine-generated, and agents otherwise read it as a user message.
#   - Say what to DO, not only what is true. A bare fact invites investigation;
#     naming the next action leaves nothing to look into.

set -u
. "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || true
git rev-parse --git-dir >/dev/null 2>&1 || exit 0

MAIN_ROOT=$(main_repo_root ".") || exit 0
BRANCH=$(current_branch ".")

echo "[automated SessionStart hook: .claude/hooks/session-status.sh — background context,"
echo " not a message from the user. Nothing here needs a reply or investigation.]"

if in_worktree "."; then
  echo "  location: worktree $(git rev-parse --show-toplevel) on '$BRANCH'"
  echo "            Deployable work belongs here. Validate here; deploy from the main checkout."
else
  echo "  location: main checkout ($MAIN_ROOT) on '$BRANCH'"
  echo "            Deployable work does not happen here. For anything touching force-app/,"
  echo "            spawn an Agent with isolation: \"worktree\", or: git worktree add ../$(basename "$MAIN_ROOT")-N -b feat/N-desc"
  if [ "$BRANCH" != "main" ]; then
    echo "            NOTE: the main checkout is not on main. 'git switch main' before deploying."
  fi
fi

# Deployable state that exists nowhere in git.
DIRTY=$(git -C "$MAIN_ROOT" status --porcelain -- force-app/ 2>/dev/null | wc -l | tr -d ' ')
[ "$DIRTY" != "0" ] && echo "  WARNING: $DIRTY uncommitted force-app/ file(s) in the main checkout"

# main === org?
DLOG=$(deploy_log ".")
MAIN_SHA=$(git -C "$MAIN_ROOT" rev-parse main 2>/dev/null || echo "")
if [ ! -f "$DLOG" ]; then
  echo "  org sync:  no deploy recorded in this clone yet"
elif [ -n "$MAIN_SHA" ]; then
  LAST=$(deploy_log_shas "$DLOG" | head -1)
  if [ "$LAST" = "$MAIN_SHA" ]; then
    echo "  org sync:  main === org at ${MAIN_SHA:0:8}"
  elif git -C "$MAIN_ROOT" cat-file -e "${LAST}^{commit}" 2>/dev/null; then
    N=$(git -C "$MAIN_ROOT" diff --name-only "$LAST" main -- force-app/ 2>/dev/null | wc -l | tr -d ' ')
    if [ "$N" = "0" ]; then
      echo "  org sync:  main === org (last deploy ${LAST:0:8}; later commits touch no force-app/)"
    else
      echo "  org sync:  MAIN IS AHEAD OF THE ORG — $N deployable file(s) changed since ${LAST:0:8}"
    fi
  fi
fi

# Open worktrees. Reported, never nagged about: keeping one alive after a deploy
# for follow-up fixes on the same ticket is a supported way to work here.
#
# "Has this landed?" is a TREE comparison, not an ancestry one. A squash merge
# puts the content on main under a new commit the branch has never seen, so
# `merge-base --is-ancestor` answers "no" for every branch that shipped normally
# — it only ever fired for worktrees that had done nothing at all.
while IFS= read -r WT; do
  [ -z "$WT" ] || [ "$WT" = "$MAIN_ROOT" ] && continue
  WB=$(git -C "$WT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "?")
  if [ -n "$(git -C "$WT" status --porcelain 2>/dev/null | head -1)" ]; then
    echo "  worktree:  $WT ($WB) — uncommitted changes"
  elif git -C "$MAIN_ROOT" diff --quiet main "$WB" 2>/dev/null; then
    echo "  worktree:  $WT ($WB) — content matches main; reuse it for the next fix, or remove it"
  else
    echo "  worktree:  $WT ($WB) — work not yet on main"
  fi
done < <(git worktree list --porcelain 2>/dev/null | awk '/^worktree /{print $2}')

exit 0
