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
HOOK_DEFER_GATE=1   # the master gate fires in hook_read_input, once the target repo is known
. "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

hook_read_input
COMMAND=$(hook_command_text)

# Anchored at a command position (line start, or after a separator) so that prose
# ABOUT `git worktree add` — in a commit message, a doc, an echo — is not read as
# an instruction to run it.
# The -C value alternatives are QUOTED-FIRST. With only [^[:space:]]+ a spaced -C path
# ("git -C '/…/64 Org' worktree add …") matched neither branch, so this whole hook
# exited 0 before either judgement ran — the nesting guard was simply absent for any
# command that named its repo with a quoted path.
WT_ADD='(^|[;&|][[:space:]]*)git[[:space:]]+(-C[[:space:]]+("[^"]+"|'"'"'[^'"'"']+'"'"'|[^[:space:]]+)[[:space:]]+)?worktree[[:space:]]+add\b'

echo "$COMMAND" | grep -qE "$WT_ADD" || exit 0

if in_worktree "."; then
  WT=$(git rev-parse --show-toplevel 2>/dev/null)
  BR=$(current_branch ".")
  if is_devops_center; then
    block \
      "BLOCKED: you are already inside a worktree. Creating another nests them." \
      "" \
      "  here: $WT (branch: $BR)" \
      "" \
      "Stay in this worktree only if it is the exact branch for the current WI." \
      "For another WI, return to the main checkout, fetch the exact branch DevOps" \
      "Center created, and add that branch as a separate linked worktree."
  fi
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
#
# Tokenised with shlex, not awk. awk splits on whitespace, so a QUOTED target
# containing a space — which every worktree of a checkout named "64 Org" has — was
# split across fields and this printed the first fragment complete with its opening
# quote. That then failed the /* absolute test below, got $PWD prepended, matched no
# worktree, and the check silently passed. `--reason "spawned by agent"` broke it the
# same way: the flag's own value became the target.
#
# Do NOT pre-truncate at |;& — `cd /tmp && git worktree add ...` would lose its
# target and the guard would silently pass.
#
# python3's absence degrades THIS check only; the cwd check above still applies, and
# it is the one that catches the common case. Saying so beats pretending otherwise.
if command -v python3 >/dev/null 2>&1; then
  TARGET=$(printf '%s' "$COMMAND" | python3 -c '
import shlex, sys
try:
    toks = shlex.split(sys.stdin.read())
except ValueError:          # unbalanced quotes: nothing reliable to say
    sys.exit(0)
for i in range(len(toks) - 1):
    if toks[i] == "worktree" and toks[i + 1] == "add":
        skip = False
        for t in toks[i + 2:]:
            if skip:
                skip = False
                continue
            if t in ("-b", "-B", "--reason"):
                skip = True
                continue
            if t.startswith("-"):
                continue
            print(t)
            sys.exit(0)
        sys.exit(0)
' 2>/dev/null)
else
  TARGET=""
fi

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
# `sed 's/^worktree //'`, never `awk '{print $2}'` — awk truncates at the first space,
# so "…/64 Org-GH-1" became "…/64". That fails BOTH ways: a nested add into a spaced
# worktree passes, and an unrelated path under the truncated prefix gets blocked with a
# message naming a worktree that does not exist. Same bug this stack fixed in
# pipeline_environment_branches and source_tree_root.
done < <(git worktree list --porcelain 2>/dev/null | sed -n 's/^worktree //p')

exit 0
