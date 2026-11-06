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
HOOK_DEFER_GATE=1   # the master gate fires in hook_read_input, once the target repo is known
. "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

hook_read_input
COMMAND=$(hook_command_text)

# Only sf commands care about target-org; only node tooling cares about
# node_modules. Anything else, stay out of the way.
NEEDS_ORG=0
NEEDS_NODE=0
echo "$COMMAND" | grep -qE '(^|[[:space:]"'"'"'(])(sf|sfdx)[[:space:]]' && NEEDS_ORG=1
echo "$COMMAND" | grep -qE '(^|[[:space:]])(npm|npx|node|eslint|prettier|jest)([[:space:]]|$)' && NEEDS_NODE=1
[ "$NEEDS_ORG" = "0" ] && [ "$NEEDS_NODE" = "0" ] && exit 0

in_worktree "." || exit 0          # the main clone configures itself
TREE=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
MAIN=$(main_repo_root ".") || exit 0
[ -z "$MAIN" ] || [ "$MAIN" = "$TREE" ] && exit 0

FIXED=""

# ── target-org ───────────────────────────────────────────────
# .sf/ is gitignored, so a fresh worktree has none and every sf command falls
# through to the machine's GLOBAL default org. A deploy or validate against the
# wrong org is the most expensive mistake available in this workflow.
if [ "$NEEDS_ORG" = "1" ]; then
  HAVE=""
  [ -f "$TREE/.sf/config.json" ] && command -v jq >/dev/null 2>&1 && \
    HAVE=$(jq -r '."target-org" // empty' "$TREE/.sf/config.json" 2>/dev/null)
  if [ -z "$HAVE" ]; then
    ALIAS=""
    [ -f "$MAIN/.sf/config.json" ] && command -v jq >/dev/null 2>&1 && \
      ALIAS=$(jq -r '."target-org" // empty' "$MAIN/.sf/config.json" 2>/dev/null)
    ALIAS="${ALIAS:-$(org_alias)}"
    if [ -n "$ALIAS" ] && command -v sf >/dev/null 2>&1 \
       && (cd "$TREE" && sf config set "target-org=$ALIAS" >/dev/null 2>&1); then
      FIXED="${FIXED}set target-org=$ALIAS in this worktree (it had none; sf would have used the machine's global default org). "
    elif [ -z "$ALIAS" ]; then
      # `note` here, and NOTHING else — this used to `exit 0`, which abandoned the
      # whole hook over one unset config value. The stealth CLAUDE.md/.forceignore
      # symlinks and the node_modules link below never ran, so a stealth worktree
      # ended up with no contract in context: precisely the failure this hook's own
      # header cites as the reason it exists, triggered by something unrelated to it.
      #
      # Nothing downstream needs the org, so there is nothing to skip. One repair
      # failing must not cancel the others.
      note "This worktree has no target-org and the main clone ($MAIN) does not define one." \
           "Set it there first, then here:  sf config set target-org=<alias>" \
           "Until then every sf command targets the machine's GLOBAL default org, not this project."
    fi
  fi
fi

# ── CLAUDE.md, in stealth mode ───────────────────────────────
#
# In native mode CLAUDE.md is committed, so a worktree materializes it like any
# tracked file and there is nothing to do. In stealth mode it is untracked (it is
# ours, not the client's), which means a worktree gets NO CLAUDE.md at all — and a
# worktree agent with no contract in context is exactly the failure this whole
# stack exists to prevent. Symlink it, the same way node_modules is handled.
#
# .forceignore gets the same treatment for the same reason: an absent .forceignore
# in a worktree changes what a deploy includes.
if is_stealth; then
  for F in CLAUDE.md AGENTS.md .forceignore; do
    if [ ! -e "$TREE/$F" ] && [ -f "$MAIN/$F" ]; then
      ln -s "$MAIN/$F" "$TREE/$F" 2>/dev/null \
        && FIXED="${FIXED}linked $F from the main clone (untracked in stealth mode, so a worktree has none). "
    fi
  done
fi

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
