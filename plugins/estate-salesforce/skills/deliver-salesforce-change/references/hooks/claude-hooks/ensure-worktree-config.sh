#!/bin/bash
# PreToolUse (Bash) — make a worktree usable, just before it matters.
#
# WHY NOT WorktreeCreate
# ---------------------
# Do NOT move this into a WorktreeCreate hook. That event is a misreading of the
# event. WorktreeCreate does not notify you that a worktree was made — it is
# expected to MAKE it and print the path:
#
#   "WorktreeCreate hook failed: hook succeeded but returned no worktree path
#    (command: echo the path to stdout; ...)"
#
# So a hook that printed status lines handed Claude Code a status line as the
# worktree path, and every `isolation: "worktree"` agent died at spawn. Sending
# that output to stderr would not have helped either — then stdout is empty and
# the spawn fails with "returned no worktree path". The event exists so non-git
# VCS users can supply worktrees; in a git repo the native implementation is
# already correct, and configuring the hook only overrides something that works.
#
# Doing it here instead covers strictly more cases: agent-created worktrees,
# `git worktree add` by hand, and a clone that was never set up at all.
#
# Never blocks. Never prints to stdout unless it changed something.

set -u
HOOK_EVENT="PreToolUse"
. "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

hook_read_input
COMMAND=$(hook_command_text)

# Only node tooling needs shared local dependencies. Never infer, copy, or set
# a Salesforce connection; org operations require an explicit confirmed target.
NEEDS_NODE=0
echo "$COMMAND" | grep -qE '(^|[[:space:]])(npm|npx|node|eslint|prettier|jest)([[:space:]]|$)' && NEEDS_NODE=1
[ "$NEEDS_NODE" = "0" ] && exit 0

in_worktree "." || exit 0          # the main clone configures itself
TREE=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
MAIN=$(main_repo_root ".") || exit 0
[ -z "$MAIN" ] || [ "$MAIN" = "$TREE" ] && exit 0

FIXED=""

# ── node_modules ─────────────────────────────────────────────
# Gitignored, so a worktree has none, and eslint/jest/prettier resolve plugins
# relative to the working tree. pre-commit links it too; doing it here means the
# tools also work when run by hand, before the first commit.
if [ "$NEEDS_NODE" = "1" ] && [ ! -e "$TREE/node_modules" ] && [ -d "$MAIN/node_modules" ]; then
  ln -s "$MAIN/node_modules" "$TREE/node_modules" 2>/dev/null \
    && FIXED="${FIXED}linked node_modules from the main clone. "
fi

[ -n "$FIXED" ] && note "$FIXED"
exit 0
