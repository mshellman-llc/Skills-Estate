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
HOOK_DEFER_GATE=1   # the master gate fires in hook_read_input, once the target repo is known
. "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

hook_read_input
is_devops_center && exit 0
COMMAND=$(hook_command_text)

# Every host's merge surface, plus the local review gate. Each prints something
# different on success, so match the command AND accept that host's phrasing.
echo "$COMMAND" | grep -qE '(\bgh[[:space:]]+pr[[:space:]]+merge\b|\bglab[[:space:]]+mr[[:space:]]+merge\b|\baz[[:space:]]+repos[[:space:]]+pr[[:space:]]+update\b|\baleysian-merge\b)' || exit 0

OUT=$(hook_tool_output)
echo "$OUT" | grep -qiE '(merged pull request|merged!|"status": ?"completed"|MERGED to )' || exit 0

MAIN_ROOT=$(main_repo_root ".")
[ -z "$MAIN_ROOT" ] && exit 0
TRUNK=$(trunk)

# Where trunk's tip actually is. With a remote the merge happened server-side and
# origin/<trunk> is the authority; with host=none the squash landed locally and
# there is no origin to fetch.
if [ "$(host)" = "none" ]; then
  TIP="$TRUNK"
else
  git -C "$MAIN_ROOT" fetch --quiet origin "$TRUNK" 2>/dev/null
  TIP="origin/$TRUNK"
fi

# What the squash actually put on trunk, so the deploy can name those files.
FILES=$(git -C "$MAIN_ROOT" show --name-only --pretty=format: "$TIP" 2>/dev/null \
  | grep '^force-app/' | sort -u)

if [ -z "$FILES" ]; then
  note "Merged. No force-app/ files in the squashed commit — nothing to deploy." \
       "Definition of Done left: confirm acceptance criteria, remove the worktree" \
       "(git worktree remove <path>). Leave the ticket open — closure is out of this loop."
  exit 0
fi

COUNT=$(echo "$FILES" | wc -l | tr -d ' ')
SRC=$(echo "$FILES" | head -25 | sed 's|^|    --source-dir |; s|$| \\|')
[ "$COUNT" -gt 25 ] && SRC="$SRC
    # ...and $((COUNT - 25)) more — see: git show --name-only $TIP"

PULL="git checkout $TRUNK && git pull"
[ "$(host)" = "none" ] && PULL="git checkout $TRUNK"

note "Merged — '$TRUNK' is now AHEAD OF THE ORG. Close the gap before anything else:" \
     "" \
     "  $PULL" \
     "  sf project deploy start \\" \
     "$SRC" \
     "    --test-level RunSpecifiedTests --tests <TestClasses>   # or NoTestRun if nothing can affect Apex results" \
     "" \
     "Then: verify acceptance criteria, record the deploy on the ticket (a comment, via" \
     "the tracker), git worktree remove <path>. Leave the ticket open — closure is out of" \
     "this loop's scope; close it only if the user asks."

exit 0
