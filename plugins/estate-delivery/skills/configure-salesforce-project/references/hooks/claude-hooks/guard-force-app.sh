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
HOOK_DEFER_GATE=1   # the master gate fires in hook_read_input, once the target repo is known
. "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

hook_read_input
FILE_PATH=""
while IFS= read -r candidate; do
  case "$candidate" in
    */force-app/*|force-app/*) FILE_PATH="$candidate"; break ;;
  esac
done < <(hook_file_paths)
[ -z "$FILE_PATH" ] && exit 0

# Walk up to the nearest directory that exists — the file itself may be new.
DIR=$(dirname "$FILE_PATH")
while [ ! -d "$DIR" ] && [ "$DIR" != "/" ] && [ "$DIR" != "." ]; do
  DIR=$(dirname "$DIR")
done

in_worktree "$DIR" && exit 0

if is_devops_center; then
  block \
    "BLOCKED: force-app/ is worktree-only. This path is in the main checkout." \
    "" \
    "  $FILE_PATH" \
    "" \
    "DevOps Center workflow:" \
    "  1. Find or create the WI, then move it to In Progress." \
    "  2. Fetch the exact WI-###### branch DevOps Center created." \
    "  3. Add that existing branch as a linked worktree and make the change there." \
    "  4. Commit with the same WI id, validate, push, and create the DevOps review." \
    "" \
    "DevOps Center owns merges into protected stages and every promotion. Reuse a" \
    "worktree only for follow-up work on the same WI."
fi

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
