#!/bin/bash
# PreToolUse (Bash) — block shell commands that WRITE to force-app/ from the
# main checkout. Companion to guard-force-app.sh, which covers Edit/Write.
#
# Read-only commands (cat, grep, find, git diff, ls) pass through untouched;
# blocking those would make the main checkout unusable for inspection.

set -u
HOOK_EVENT="PreToolUse"   # note() stamps the event name; a mismatch is dropped
HOOK_DEFER_GATE=1   # the master gate fires in hook_read_input, once the target repo is known
. "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

hook_read_input
COMMAND=$(hook_command_text)

# "force-app" must appear as a PATH, not as a substring of some other name.
# Without the token boundary this guard blocks commands that merely mention
# ~/.aleysian/claude-hooks/guard-force-app-bash.sh — including edits to itself.
FA='force-app(/|[[:space:]]|"|'"'"'|$)'

echo "$COMMAND" | grep -qE "$FA" || exit 0

# Judge the TARGET PATH, not the shell's cwd. The rule is about where the file
# lives: deployable source is authored in a worktree. Writing into a worktree
# from the main checkout is fine, including `cd <worktree> && write`.

in_worktree "." && exit 0     # cheap path: already standing in one

# A leading `cd <dir> &&` changes what relative paths mean.
#
# Quoted forms must be matched before the bare one: a checkout whose name
# contains a space (e.g. "64 Org") gives every worktree a space in its path, so
# it is always quoted. Tokenizing that on whitespace yields a nonexistent
# directory, BASE silently falls back to the main checkout, and the guard then
# blocks writes that were in fact headed INTO a worktree.
BASE="$PWD"
CD_TARGET=$(printf '%s' "$COMMAND" | sed -nE 's/^[[:space:]]*cd[[:space:]]+"([^"]+)".*/\1/p')
[ -z "$CD_TARGET" ] && CD_TARGET=$(printf '%s' "$COMMAND" | sed -nE "s/^[[:space:]]*cd[[:space:]]+'([^']+)'.*/\1/p")
[ -z "$CD_TARGET" ] && CD_TARGET=$(printf '%s' "$COMMAND" | sed -nE 's/^[[:space:]]*cd[[:space:]]+([^[:space:];&|]+).*/\1/p')
CD_TARGET=$(printf '%s' "$CD_TARGET" | head -1)
if [ -n "$CD_TARGET" ] && [ -d "$CD_TARGET" ]; then
  BASE=$(cd "$CD_TARGET" 2>/dev/null && pwd) || BASE="$PWD"
fi

# Emit every force-app path token in a command, one per line, spaces intact.
#
# A path containing a space is only usable when quoted, so quoted runs are
# taken whole and first; blanking them out before the whitespace pass is what
# keeps "…/64 Org-GH-433/force-app/x" from also surfacing as the bogus
# fragment "Org-GH-433/force-app/x", which would resolve against the main
# checkout and block a legitimate worktree write.
fa_path_tokens() {
  local cmd="$1"
  printf '%s' "$cmd" | grep -oE '"[^"]*force-app[^"]*"|'\''[^'\'']*force-app[^'\'']*'\'''
  printf '%s' "$cmd" | sed -E 's/"[^"]*"/ /g; s/'\''[^'\'']*'\''/ /g' \
    | grep -oE "[^[:space:]\"'<>|;&]*force-app[^[:space:]\"'<>|;&]*"
}

# Every path-ish token naming force-app, resolved and tested individually.
RESOLVED_ANY=0
OUTSIDE=""
TOKENS=()
while IFS= read -r TOK; do
  [ -z "$TOK" ] && continue
  TOK=${TOK%\"}; TOK=${TOK#\"}; TOK=${TOK%\'}; TOK=${TOK#\'}
  case "$TOK" in
    /*) ABS="$TOK" ;;
    *)  ABS="$BASE/$TOK" ;;
  esac
  DIR=$(dirname "$ABS")
  while [ ! -d "$DIR" ] && [ "$DIR" != "/" ] && [ "$DIR" != "." ]; do DIR=$(dirname "$DIR"); done
  RESOLVED_ANY=1
  TOKENS+=("$ABS")
  in_worktree "$DIR" || OUTSIDE="$OUTSIDE  $TOK"$'\n'
done < <(fa_path_tokens "$COMMAND")

# Every force-app target lives in a worktree — that is the workflow, allow it.
[ "$RESOLVED_ANY" = "1" ] && [ -z "$OUTSIDE" ] && exit 0

# ── Deleting UNTRACKED force-app files is cleanup, not authoring ─────────────
#
# A stray untracked file under force-app/ exists nowhere in git, yet a broad
# deploy picks it up. Removing it is cleanup. Tracked paths are never eligible,
# so this cannot destroy committed source or author anything.
if [ "${#TOKENS[@]}" -gt 0 ] && echo "$COMMAND" | grep -qE '\b(rm|git[[:space:]]+clean)\b'; then
  ALL_UNTRACKED=1
  for ABS in "${TOKENS[@]}"; do
    [ -n "$(git ls-files -- "$ABS" 2>/dev/null | head -1)" ] && ALL_UNTRACKED=0 && break
  done
  if [ "$ALL_UNTRACKED" = "1" ]; then
    note "Allowed: removing untracked force-app/ path(s) from the main checkout." \
         "Nothing tracked was touched."
    exit 0
  fi
fi

# Write-intent detection: a denylist of write verbs, not an allowlist of
# readers. A missed reader is a visible false block; a missed writer is a
# silent hole.
WRITES=0

# A redirect's target is the ONE token after `>`. Excluding whitespace, quotes
# and angle brackets from that token keeps `grep -rn "<fullName>" force-app/...`
# — ordinary work in an XML metadata repo — from reading as a write, while
# `> force-app/x.cls` and `>"force-app/x.cls"` still match.
REDIR=">{1,2}[[:space:]]*['\"]?[^[:space:]|&;<>'\"]*$FA"

if echo "$COMMAND" | grep -qE "$REDIR"; then WRITES=1
elif echo "$COMMAND" | grep -qE "sed[[:space:]]+[^|;]*-i[^|;]*$FA"; then WRITES=1
elif echo "$COMMAND" | grep -qE "\b(cp|mv|rm|tee|touch|mkdir|rmdir|chmod|chown|ln|install|rsync|truncate)\b[^|;]*$FA"; then WRITES=1
elif echo "$COMMAND" | grep -qE "\bgit[[:space:]]+(apply|checkout|restore|mv|rm|clean)\b[^|;]*$FA"; then WRITES=1
elif echo "$COMMAND" | grep -qE "\bpatch\b[^|;]*$FA"; then WRITES=1
elif echo "$COMMAND" | grep -qE "(python3?|node|perl|ruby)[[:space:]][^|;]*$FA"; then WRITES=1
elif echo "$COMMAND" | grep -qE "\b(sf|sfdx)\b[^|;]*(retrieve|convert)\b"; then WRITES=1
fi

[ "$WRITES" -eq 0 ] && exit 0

if is_devops_center; then
  block \
    "BLOCKED: this writes force-app/ source that is NOT inside a worktree:" \
    "${OUTSIDE:-  (resolved against $BASE)}" \
    "  $COMMAND" \
    "" \
    "Move the DevOps Center WI to In Progress and fetch the exact WI-###### branch" \
    "it created. Add that existing branch as a linked worktree, then aim this write" \
    "at that worktree. Do not create a feat/* or replacement WI branch." \
    "" \
    "Commit with the same WI id, validate, push, and create the DevOps review." \
    "DevOps Center owns protected-stage merges and promotions."
fi

block \
  "BLOCKED: this writes force-app/ source that is NOT inside a worktree:" \
  "${OUTSIDE:-  (resolved against $BASE)}" \
  "  $COMMAND" \
  "" \
  "You do not need a subagent or a directory change. Make a worktree and write" \
  "into it — from right here is fine:" \
  "  git worktree add ../$(basename "$(main_repo_root .)")-N -b feat/N-description" \
  "  cd ../$(basename "$(main_repo_root .)")-N        # optional; the guard checks the PATH" \
  "" \
  "Deployable source is authored in a worktree only:" \
  "  1. Ticket    gh issue create  (or find the existing one)" \
  "  2. Worktree  Agent tool with isolation: \"worktree\", branch feat/N-... or fix/N-..." \
  "  3. Quality   npm run pmd + /simplify before committing" \
  "  4. Ship      dry-run validate -> PR -> squash merge -> deploy from main" \
  "" \
  "If this is genuinely read-only and the match is wrong, restructure the command" \
  "(e.g. drop the redirect)."
