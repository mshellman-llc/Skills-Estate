#!/bin/bash
# PreToolUse (Edit|Write) — block edits to force-app/ outside a git worktree.
#
# Deployable source is only ever authored in a worktree. Editing it in the main
# checkout leads to force-app changes committed on main, which breaks the
# main === org invariant before any deploy has happened.
#
# Worktree detection is by git topology, not by path, so a worktree created
# anywhere (git worktree add ../whatever) is honoured, not just .claude/worktrees/.

set -u
. "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

hook_read_input
FILE_PATH=$(hook_field '.tool_input.file_path')

[ -z "$FILE_PATH" ] && exit 0
case "$FILE_PATH" in
  */force-app/*|force-app/*) ;;
  *) exit 0 ;;
esac

# Walk up to the nearest directory that exists — the file itself may be new.
DIR=$(dirname "$FILE_PATH")
while [ ! -d "$DIR" ] && [ "$DIR" != "/" ] && [ "$DIR" != "." ]; do
  DIR=$(dirname "$DIR")
done

in_worktree "$DIR" && exit 0

block \
  "BLOCKED: force-app/ is worktree-only. This path is in the main checkout." \
  "" \
  "  $FILE_PATH" \
  "" \
  "The workflow:" \
  "  1. Ticket    gh issue create  (or find the existing one)" \
  "  2. Worktree  Agent tool with isolation: \"worktree\", branch feat/N-... or fix/N-..." \
  "  3. Quality   npm run pmd + /simplify before committing" \
  "  4. Ship      dry-run validate -> PR -> squash merge -> deploy from main" \
  "" \
  "Already have a worktree open for this ticket? Keep using it — follow-up PRs" \
  "from the same worktree are fine. Editing here is not."
