#!/bin/bash
# PreToolUse (Bash) — never create a worktree inside a worktree.
#
# When the outer worktree is cleaned up, every shell in the nested one has its
# cwd deleted underneath it and the Bash tool fails permanently — even `cd /`.
# The session cannot recover. This is the single most destructive mistake in
# this workflow, and it is entirely mechanical to prevent.
#
# An agent spawned with isolation: "worktree" is ALREADY isolated. It branches
# and commits where it stands.

set -u
. "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

hook_read_input
COMMAND=$(hook_command_text)

# Anchored at a command position (line start, or after a separator) so that prose
# ABOUT `git worktree add` — in a commit message, a doc, an echo — is not read as
# an instruction to run it.
WT_ADD='(^|[;&|][[:space:]]*)git[[:space:]]+(-C[[:space:]]+[^[:space:]]+[[:space:]]+)?worktree[[:space:]]+add\b'

echo "$COMMAND" | grep -qE "$WT_ADD" || exit 0

if in_worktree "."; then
  WT=$(git rev-parse --show-toplevel 2>/dev/null)
  BR=$(current_branch ".")
  block \
    "BLOCKED: you are already inside a worktree — creating another nests them." \
    "" \
    "  here: $WT (branch: $BR)" \
    "" \
    "Nested worktrees are unrecoverable: when the outer one is removed, this shell's" \
    "cwd stops existing and every subsequent Bash call fails, including 'cd /'." \
    "" \
    "Work right here instead:" \
    "  git switch -c feat/N-short-description   # if you still need a branch" \
    "  ...edit, commit, validate, PR from this directory..."
fi

# Also refuse a target path that lands inside an existing LINKED worktree.
#
# This must compare the resolved target against the real worktree list. An
# earlier version pattern-matched "/worktrees/" in the command and so blocked
# `git worktree add .claude/worktrees/<name>` from the main checkout — which is
# the standard location Claude Code itself uses and the one .gitignore exists
# for. "Contains the word worktrees" is not the same claim as "is inside a
# worktree", and conflating them broke the normal path while catching nothing.

# First non-flag argument after `worktree add` (-b/-B/--reason take a value).
# Do NOT pre-truncate at |;& — `cd /tmp && git worktree add ...` would lose its
# target and the guard would silently pass. awk finds the token pair itself, and
# stops at the first non-flag argument, so a trailing pipe is harmless.
TARGET=$(printf '%s' "$COMMAND" | awk '
  { for (i = 1; i < NF; i++) if ($i == "worktree" && $(i+1) == "add") { start = i + 2; break } }
  start {
    skip = 0
    for (i = start; i <= NF; i++) {
      if (skip) { skip = 0; continue }
      if ($i == "-b" || $i == "-B" || $i == "--reason") { skip = 1; continue }
      if (substr($i, 1, 1) == "-") continue
      print $i; exit
    }
  }')

[ -z "$TARGET" ] && exit 0

case "$TARGET" in
  /*) ABS="$TARGET" ;;
  *)  ABS="$PWD/$TARGET" ;;
esac

MAINROOT=$(main_repo_root ".")
while IFS= read -r WTROOT; do
  [ -z "$WTROOT" ] && continue
  [ "$WTROOT" = "$MAINROOT" ] && continue      # the main checkout is not a worktree
  case "$ABS/" in
    "$WTROOT"/*)
      block \
        "BLOCKED: that path is inside the existing worktree $WTROOT." \
        "" \
        "  $COMMAND" \
        "" \
        "Nesting one worktree inside another is unrecoverable: removing the outer one" \
        "deletes the inner one's cwd and every later Bash call fails, including 'cd /'." \
        "" \
        "Put it somewhere else — .claude/worktrees/<name> in the main checkout is the" \
        "normal location, and a sibling of the repo works too."
      ;;
  esac
done < <(git worktree list --porcelain 2>/dev/null | awk '/^worktree /{print $2}')

exit 0
