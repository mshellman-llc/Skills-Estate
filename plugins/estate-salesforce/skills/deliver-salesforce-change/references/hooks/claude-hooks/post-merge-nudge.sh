#!/bin/bash
# PostToolUse (Bash) — the moment after a squash merge is the riskiest point in
# the workflow: main now claims to describe the org, and does not yet.
#
# Hand the agent the exact next commands, with the changed files already listed
# so "deploy only what changed" is the path of least resistance.
#
# Never blocks.

set -u
HOOK_EVENT="PostToolUse"
. "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

hook_read_input
COMMAND=$(hook_command_text)

echo "$COMMAND" | grep -qE '\bgh[[:space:]]+pr[[:space:]]+merge\b' || exit 0

OUT=$(hook_tool_output)
# gh prints "Merged pull request #N" / "Squashed and merged pull request #N".
echo "$OUT" | grep -qiE 'merged pull request' || exit 0

MAIN_ROOT=$(main_repo_root ".")
[ -z "$MAIN_ROOT" ] && exit 0

git -C "$MAIN_ROOT" fetch --quiet origin main 2>/dev/null

# What the squash actually put on main, so the deploy can name those files.
FILES=$(git -C "$MAIN_ROOT" show --name-only --pretty=format: origin/main 2>/dev/null \
  | grep '^force-app/' | sort -u)

if [ -z "$FILES" ]; then
  note "PR merged. No force-app/ files in the squashed commit — nothing to deploy." \
       "Definition of Done left: confirm acceptance criteria, close the ticket," \
       "remove the worktree (git worktree remove <path>)."
  exit 0
fi

COUNT=$(echo "$FILES" | wc -l | tr -d ' ')
SRC=$(echo "$FILES" | head -25 | sed 's|^|    --source-dir |; s|$| \\|')
[ "$COUNT" -gt 25 ] && SRC="$SRC
    # ...and $((COUNT - 25)) more — see: git show --name-only origin/main"

note "PR merged — main is now AHEAD OF THE ORG. Close the gap before anything else:" \
     "" \
     "  git checkout main && git pull" \
     "  sf project deploy start \\" \
     "$SRC" \
     "    --test-level RunSpecifiedTests --tests <TestClasses>   # or NoTestRun if nothing can affect Apex results" \
     "" \
     "Then: verify acceptance criteria, close the ticket, git worktree remove <path>."

exit 0
