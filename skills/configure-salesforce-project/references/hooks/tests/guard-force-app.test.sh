#!/bin/bash
# Regression tests for claude-hooks/guard-force-app.sh.
#
# THE CLAIM UNDER TEST: deployable source is authored in a worktree and nowhere
# else. So this guard has to be right in BOTH directions — a missed block puts
# force-app changes on main before any deploy (breaking main === org), and a
# false block stops the authoring the whole workflow depends on. Every section
# below therefore pairs an expected block with the expected allow beside it.
#
# Payload shape is NOT the Bash one. This hook reads `.tool_input.file_path`:
#   {"tool_name":"Write","tool_input":{"file_path":"/abs/path"}}
# Exit 2 = block, exit 0 = allow.
#
# Three things the fixture must get right, each learned the hard way:
#
#   space in the path   The real checkout is named "64 Org", so every worktree
#                       path contains a space and is therefore always quoted.
#                       Quoted-path truncation is the recurring defect in this
#                       directory (GH-436 and friends). The spaces below are the
#                       test — do not tidy them away.
#   pwd -P on the root  macOS $TMPDIR sits under /var, a symlink to /private/var.
#                       in_worktree() compares a PHYSICAL --absolute-git-dir
#                       against git_common_dir(); if the two sides are resolved
#                       differently the main checkout reads as a worktree and the
#                       guard fails OPEN, silently allowing everything.
#   estate.mode set   Every hook exits 0 immediately in a repo with no
#                       `estate.mode` — the master gate. Without the config
#                       below, every case here would "pass" as allow while
#                       testing absolutely nothing.
#
# Worktrees are detected by git topology (--git-dir != --git-common-dir), never
# by path pattern. Both a worktree in an ARBITRARY location and one in the
# standard .claude/worktrees/ location are covered, and the standard one lives
# INSIDE the main checkout — a path-prefix implementation would call it main.
#
# Self-contained: builds its own throwaway repos, touches nothing else.
#
# Run: bash references/hooks/tests/guard-force-app.test.sh

set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
HOOK="$HERE/../claude-hooks/guard-force-app.sh"
[ -f "$HOOK" ] || { echo "missing hook: $HOOK"; exit 1; }

command -v python3 >/dev/null 2>&1 || { echo "python3 required; skipping"; exit 0; }

TMP=$(mktemp -d "${TMPDIR:-/tmp}/guard fa edit.XXXXXX") || exit 1
TMP=$(cd "$TMP" && pwd -P)

M="$TMP/main repo"                  # the managed clone
W="$TMP/wt GH-1"                    # worktree in an ARBITRARY location
WSTD="$M/.claude/worktrees/wt GH-2" # worktree in the standard location, INSIDE M
U="$TMP/plain repo"                 # ordinary git repo, no estate.* at all
SL="$TMP/link"                      # symlink to TMP, to re-enter via a symlinked path
FA="force-app/main/default"
OUT="$TMP/hook.out"

cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

mkdir -p "$M/$FA" && cd "$M" || exit 1
git init -q -b main .                                     >/dev/null 2>&1
git config user.email t@t.test; git config user.name t
git config estate.mode native
git config estate.trunk main
echo x > "$FA/x.xml"
mkdir -p scripts/apex && echo x > scripts/apex/s.apex
git add -A >/dev/null 2>&1 && git commit -qm init >/dev/null 2>&1

git worktree add --detach "$W"    HEAD >/dev/null 2>&1 \
  || { echo "could not create temp worktree; skipping"; exit 0; }
git worktree add --detach "$WSTD" HEAD >/dev/null 2>&1 \
  || { echo "could not create standard-location worktree; skipping"; exit 0; }

# The unmanaged neighbour. It HAS a force-app, and no estate.mode: a write here
# must be allowed, because the master gate makes these hooks inert in repos that
# were never initialised. Installed at user level, they fire in every repo on the
# machine, so this is the common case, not an edge case.
mkdir -p "$U/$FA" && ( cd "$U" \
  && git init -q -b main . >/dev/null 2>&1 \
  && git config user.email t@t.test && git config user.name t \
  && echo x > "$FA/x.xml" \
  && git add -A >/dev/null 2>&1 && git commit -qm init >/dev/null 2>&1 )

ln -sfn "$TMP" "$SL"

PASS=0; FAIL=0

# run <expect allow|block> <cwd> <label> <file_path> [tool_name]
#
# cwd matters: a hook's cwd is the session's project directory, and it is what
# resolves a RELATIVE file_path and what the master gate falls back to when the
# target cannot be resolved.
run() {
  local want="$1" cwd="$2" label="$3" path="$4" tool="${5:-Write}" got rc
  printf '%s' "$path" \
    | python3 -c 'import json,sys; print(json.dumps({"tool_name":sys.argv[1],"tool_input":{"file_path":sys.stdin.read()}}))' "$tool" \
    | ( cd "$cwd" && bash "$HOOK" ) >"$OUT" 2>&1
  rc=$?
  got=allow; [ $rc -ne 0 ] && got=block
  if [ "$got" = "$want" ]; then
    PASS=$((PASS+1)); echo "  PASS [$got] $label"
  else
    FAIL=$((FAIL+1)); echo "  FAIL expected=$want got=$got :: $label"; sed -n '2,4p' "$OUT"
  fi
}

# Codex represents file edits as apply_patch with the patch program in
# tool_input.command. Keep this separate from run() so both wire formats remain
# explicit regression fixtures.
run_patch() {
  local want="$1" cwd="$2" label="$3" path="$4" got rc
  python3 -c 'import json,sys; print(json.dumps({"cwd":sys.argv[1],"tool_name":"apply_patch","tool_input":{"command":"*** Begin Patch\n*** Update File: "+sys.argv[2]+"\n@@\n-x\n+y\n*** End Patch"}}))' "$cwd" "$path" \
    | ( cd "$cwd" && bash "$HOOK" ) >"$OUT" 2>&1
  rc=$?
  got=allow; [ $rc -ne 0 ] && got=block
  if [ "$got" = "$want" ]; then
    PASS=$((PASS+1)); echo "  PASS [$got] $label"
  else
    FAIL=$((FAIL+1)); echo "  FAIL expected=$want got=$got :: $label"; sed -n '2,4p' "$OUT"
  fi
}

echo "== force-app in the MAIN CHECKOUT: must BLOCK =="
run block "$M" "absolute path, space in repo name"  "$M/$FA/Foo.cls"
run block "$M" "relative path"                      "$FA/Foo.cls"
run block "$M" "NEW file, dirs do not exist yet"    "$M/$FA/lwc/brandNew/brandNew.js"
run block "$M" "NotebookEdit is guarded too"        "$M/$FA/nb.ipynb" NotebookEdit
run_patch block "$M" "Codex apply_patch payload"     "$FA/Foo.cls"
# The symlink case is the fail-open from _lib.sh's in_worktree() comment. Entering
# via /link/... instead of the physical path must not change the verdict; if it
# does, every force-app write on a machine with a symlinked TMPDIR/home is allowed.
run block "$M" "re-entered via a SYMLINKED path"    "$SL/main repo/$FA/Foo.cls"

echo "== force-app in a WORKTREE: must ALLOW =="
run allow "$M" "worktree in an arbitrary location"  "$W/$FA/Foo.cls"
run allow "$M" "standard .claude/worktrees, inside M" "$WSTD/$FA/Foo.cls"
run allow "$M" "NEW file, dirs do not exist yet"    "$W/$FA/lwc/brandNew/brandNew.js"
run allow "$W" "relative path, cwd is the worktree" "$FA/Foo.cls"
run allow "$M" "NotebookEdit into a worktree"       "$W/$FA/nb.ipynb" NotebookEdit
run_patch allow "$W" "Codex apply_patch in worktree" "$FA/Foo.cls"
run allow "$M" "worktree re-entered via a symlink"  "$SL/wt GH-1/$FA/Foo.cls"

echo "== paths this guard has no opinion about: must ALLOW =="
run allow "$M" "README in the main checkout"        "$M/README.md"
run allow "$M" "scripts/apex in the main checkout"  "$M/scripts/apex/s.apex"
run allow "$M" "'force-app-notes' is not force-app" "$M/force-app-notes/x.md"
run allow "$M" "no file_path in the payload"        ""

echo "== the master gate: an unmanaged repo must be untouched =="
# Judge the target, not the shell — in BOTH directions. The gate re-runs after
# retargeting to the file's repo, so a configured session must not export its
# rules, and an unconfigured session must not disarm them.
run allow "$M" "target is an unmanaged repo"        "$U/$FA/Foo.cls"
run allow "$U" "cwd unmanaged, target unmanaged"    "$U/$FA/Foo.cls"
run block "$U" "cwd unmanaged, target IS managed"   "$M/$FA/Foo.cls"

echo "== what does it do when it CANNOT tell? =="
# A force-app path in no git repo at all. in_worktree() returns non-zero, so this
# BLOCKS: uncertainty resolves toward refusing, which is the correct direction for
# a guard. Pinned so a future "tidy up" cannot quietly flip it to allow.
run block "$M" "force-app path outside any repo"    "/nowhere-9f3/force-app/x.cls"

echo
echo "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
