#!/bin/bash
# Regression tests for claude-hooks/guard-worktree-nesting.sh.
#
# WHY THIS GUARD IS WORTH TESTING HARD: a worktree created inside another
# worktree is unrecoverable. Removing the outer one deletes the inner one's cwd
# and every subsequent Bash call fails, `cd /` included. The session is gone.
# There is no recovery path, so the only defence is the guard — and a guard that
# fails OPEN is not a defence at all.
#
# The hook makes two independent judgements, and this suite separates them:
#
#   1. AM I in a worktree?      in_worktree "." after retargeting on `cd`/`git -C`
#   2. Is the TARGET in one?    the resolved target vs `git worktree list`
#
# Judgement 1 is sound. Judgement 2 is not: it is defeated by a quoted target and
# by any worktree path containing a space, and it can also produce a FALSE block.
# Five cases below fail on purpose. See "SUSPECTED HOOK BUGS" at the bottom of
# this header; do not "fix" them by loosening the expectations.
#
# FIXTURE NOTES, each load-bearing:
#
#   spaces          The real checkout is "64 Org", so every worktree path has a
#                   space and every such path in a command is quoted. That is the
#                   condition the guard is broken under, so it must be the
#                   condition the fixture reproduces.
#   an UNSPACED     $PLAIN holds a second worktree of the same repo at a path with
#   control         no space in it, so a failing spaced case can be attributed to
#                   space handling rather than to the comparison logic in general.
#   pwd -P          macOS $TMPDIR is under /var -> /private/var. in_worktree()
#                   compares a physical git dir against a resolved common dir; an
#                   unresolved root makes the main checkout read as a worktree and
#                   the whole guard fail open.
#   estate.mode   The master gate: every hook exits 0 at once in a repo with no
#                   `estate.mode`. Without it every case here "passes" as allow
#                   while testing nothing.
#
# Topology, never path patterns: a worktree is --git-dir != --git-common-dir. An
# earlier version matched "/worktrees/" in the command text and so blocked
# `git worktree add .claude/worktrees/<name>` — the standard location Claude Code
# itself uses. Both of those are pinned as ALLOW below.
#
# Self-contained: builds its own throwaway repos, touches nothing else.
#
# Run: bash references/hooks/tests/guard-worktree-nesting.test.sh
#
# ── SUSPECTED HOOK BUGS pinned by the failing cases ──────────────────────────
#
#   B1  TARGET is never dequoted (guard-worktree-nesting.sh:69-72). awk yields the
#       token WITH its quote characters, so `"$W/nested"` becomes `"/private/...`,
#       fails the `/*` absolute test, gets $PWD prepended, and matches no
#       worktree. Every quoted target is therefore unchecked — and a path with a
#       space is always quoted.
#   B2  `awk '/^worktree /{print $2}'` (:92) truncates at the first space, so a
#       worktree whose path contains one can never be matched (fail open), and the
#       truncated prefix can match an unrelated path (false block).
#   B3  WT_ADD (:22) allows only an UNQUOTED value after -C
#       (`-C[[:space:]]+[^[:space:]]+`), so `git -C "<path with space>" worktree
#       add ...` is not recognised as a worktree-add at all and the hook exits 0
#       before either judgement runs.

set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
HOOK="$HERE/../claude-hooks/guard-worktree-nesting.sh"
[ -f "$HOOK" ] || { echo "missing hook: $HOOK"; exit 1; }

command -v python3 >/dev/null 2>&1 || { echo "python3 required; skipping"; exit 0; }

TMP=$(mktemp -d "${TMPDIR:-/tmp}/guard nest.XXXXXX")   || exit 1
TMP=$(cd "$TMP" && pwd -P)
PLAIN=$(mktemp -d "${TMPDIR:-/tmp}/nestplain.XXXXXX")  || exit 1
PLAIN=$(cd "$PLAIN" && pwd -P)                          # deliberately NO space

M="$TMP/main repo"        # the managed clone
W="$TMP/wt GH-1"          # worktree of M, spaced path (the realistic one)
W2="$PLAIN/wt2"           # worktree of M, unspaced path (the control)
U="$TMP/plain repo"       # unmanaged repo
UW="$TMP/plain wt"        # ... and its worktree
OUT="$TMP/hook.out"

# What `awk '/^worktree /{print $2}'` actually yields for anything under $TMP:
# everything from the first space onward is lost.
TRUNC="${TMP%% *}"

cleanup() { rm -rf "$TMP" "$PLAIN"; }
trap cleanup EXIT

mkdir -p "$M" && cd "$M" || exit 1
git init -q -b main .                                     >/dev/null 2>&1
git config user.email t@t.test; git config user.name t
git config estate.mode native
git config estate.trunk main
echo x > f.txt
git add -A >/dev/null 2>&1 && git commit -qm init >/dev/null 2>&1

git worktree add --detach "$W"  HEAD >/dev/null 2>&1 \
  || { echo "could not create spaced worktree; skipping"; exit 0; }
git worktree add --detach "$W2" HEAD >/dev/null 2>&1 \
  || { echo "could not create unspaced worktree; skipping"; exit 0; }

mkdir -p "$U" && ( cd "$U" \
  && git init -q -b main . >/dev/null 2>&1 \
  && git config user.email t@t.test && git config user.name t \
  && echo x > f.txt && git add -A >/dev/null 2>&1 && git commit -qm init >/dev/null 2>&1 \
  && git worktree add --detach "$UW" HEAD >/dev/null 2>&1 )

PASS=0; FAIL=0

# run <expect allow|block> <cwd> <label> <command text>
#
# cwd is the session's project directory — it is what decides "am I in a
# worktree?" for any command that does not redirect with `cd` or `git -C`.
run() {
  local want="$1" cwd="$2" label="$3" cmd="$4" got rc
  printf '%s' "$cmd" \
    | python3 -c 'import json,sys; print(json.dumps({"tool_name":"Bash","tool_input":{"command":sys.stdin.read()}}))' \
    | ( cd "$cwd" && bash "$HOOK" ) >"$OUT" 2>&1
  rc=$?
  got=allow; [ $rc -ne 0 ] && got=block
  if [ "$got" = "$want" ]; then
    PASS=$((PASS+1)); echo "  PASS [$got] $label"
  else
    FAIL=$((FAIL+1)); echo "  FAIL expected=$want got=$got :: $label"; sed -n '2,3p' "$OUT"
  fi
}

echo "== not a worktree-add at a command position: must ALLOW =="
run allow "$W" "git worktree list"                  "git worktree list --porcelain"
run allow "$W" "prose inside an echo"               "echo \"next step: git worktree add foo\""
run allow "$W" "a shell comment"                    "# git worktree add foo"
# A heredoc body is data. Commit messages routinely quote the very commands these
# guards look for, and strip_heredocs() exists so that quoting one is not treated
# as running one.
run allow "$W" "heredoc body (a commit message)"    "$(printf 'git commit -F - <<EOF\ngit worktree add somewhere\nEOF\n')"

echo "== already inside a worktree: must BLOCK, wherever it is aimed =="
run block "$W" "plain add from inside a worktree"   "git worktree add \"$TMP/other wt\""
run block "$W" "anchored after && (cd out first)"   "cd /tmp && git worktree add other"
run block "$M" "cd \"<spaced worktree>\" && add"      "cd \"$W\" && git worktree add \"$TMP/other wt\""
run block "$M" "git -C <unspaced worktree> add"     "git -C $W2 worktree add $PLAIN/other"

echo "== from the main checkout, to a legitimate place: must ALLOW =="
# The regression this pins: an earlier version pattern-matched "/worktrees/" and
# blocked the standard Claude Code location outright.
run allow "$M" "the standard .claude/worktrees spot" "git worktree add \".claude/worktrees/wt GH-9\""
run allow "$M" "a sibling of the repo, with -b"      "git worktree add -b feat/9-x \"$TMP/sibling wt\""

echo "== target lands INSIDE an existing worktree: must BLOCK =="
run block "$M" "unquoted, unspaced (the control)"    "git worktree add $W2/nested"
run block "$M" "-b value skipped, then the target"   "git worktree add -b feat/1-x $W2/nested"
# B1 — the only difference from the control above is a pair of double quotes.
run block "$M" "DOUBLE-QUOTED, unspaced  [B1]"       "git worktree add \"$W2/nested\""
# B1 + B2 — and this is the shape every real command in this repo has, because
# every real worktree path contains a space.
run block "$M" "quoted AND spaced        [B1+B2]"    "git worktree add \"$W/nested\""
# B1 again, via a flag VALUE this time: --reason's quoted value is split on the
# space, so the token after it is mistaken for the target.
run block "$M" "--reason \"two words\" then target  [B1]" "git worktree add --reason \"spawned by agent\" $W2/nested"
# B3 — not recognised as a worktree-add at all, so neither judgement runs.
run block "$M" "git -C \"<spaced worktree>\" add     [B3]" "git -C \"$W\" worktree add \"$TMP/other wt\""

echo "== the truncated root must not block an unrelated path =="
# B2, the over-block direction. Nothing exists at this path and it is inside no
# worktree, but it starts with the truncated prefix awk produced, so the guard
# blocks it and names a worktree ($TRUNC) that does not exist. A false block costs
# as much trust as a false pass.
run allow "$M" "unrelated path under the prefix  [B2]" "git worktree add $TRUNC/unrelated-9f3"

echo "== what does it do when it CANNOT tell? =="
# No target token at all: TARGET is empty and the hook exits 0. Acceptable here
# only because git itself rejects the command — pinned so the fail-open stays
# visible and deliberate.
run allow "$M" "no target argument"                 "git worktree add --detach"

echo "== the master gate: an unmanaged repo must be untouched =="
# Same nesting mistake, in a repo that never ran init. These hooks are installed
# at user level and fire everywhere, so staying inert here is the requirement.
run allow "$UW" "nesting inside an unmanaged worktree" "git worktree add \"$TMP/other wt\""

echo
echo "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
