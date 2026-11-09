#!/bin/bash
# Regression tests for claude-hooks/guard-force-app-bash.sh.
#
# The bug these pin down (first found as GH-436 in Example Project-Estate, whose
# checkout is literally named "64 Org"): when the clone's path contains a
# SPACE, every worktree path contains one too, so those paths are always
# quoted. Both the `cd` resolver and the force-app token extractor used to
# truncate at the space, so the guard could not recognize its own worktrees and
# false-positive-blocked the authoring it exists to permit.
#
# The temp repo and worktree below deliberately have spaces in their names.
# Do not "tidy" that away — the space is the test.
#
# Self-contained: builds its own throwaway repo, touches nothing else.
#
# Run: bash references/hooks/tests/guard-force-app-bash.test.sh

set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
HOOK="$HERE/../claude-hooks/guard-force-app-bash.sh"
[ -f "$HOOK" ] || { echo "missing hook: $HOOK"; exit 1; }

command -v python3 >/dev/null 2>&1 || { echo "python3 required; skipping"; exit 0; }

# ── throwaway repo, space in the name on purpose ─────────────
# Resolve symlinks in the temp root. On macOS $TMPDIR lives under /var, which is
# a symlink to /private/var — and in_worktree() compares an UNRESOLVED
# `--absolute-git-dir` against a RESOLVED git_common_dir(). Under a symlinked
# path those never match, the main checkout reads as a worktree, and the guard
# silently allows everything. That is a real fail-open worth fixing in _lib.sh,
# but this test must not depend on it either way.
TMP=$(mktemp -d "${TMPDIR:-/tmp}/guard fa test.XXXXXX") || exit 1
TMP=$(cd "$TMP" && pwd -P)
M="$TMP/main repo"
W="$TMP/wt GH-1"                       # space is load-bearing
FA="force-app/main/default"
OUT="$TMP/hook.out"

cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

mkdir -p "$M" && cd "$M" || exit 1
git init -q -b main .                                     >/dev/null 2>&1
git config user.email t@t.test; git config user.name t
# Every hook exits 0 immediately in a repo with no estate.mode — the master
# gate. Without this the guard never runs and every case would "pass" as allow.
git config estate.mode native
git config estate.trunk main
mkdir -p "$FA/reports"
echo x > "$FA/x.xml"
git add -A >/dev/null 2>&1 && git commit -qm init >/dev/null 2>&1
git worktree add --detach "$W" HEAD >/dev/null 2>&1 \
  || { echo "could not create temp worktree; skipping"; exit 0; }
W=$(cd "$W" && pwd)
mkdir -p "$W/$FA/reports"

PASS=0; FAIL=0

run() { # $1=expect(allow|block)  $2=label  $3=command text
  local got rc
  printf '%s' "$3" \
    | python3 -c 'import json,sys; print(json.dumps({"tool_name":"Bash","tool_input":{"command":sys.stdin.read()}}))' \
    | bash "$HOOK" >"$OUT" 2>&1
  rc=$?
  got=allow; [ $rc -ne 0 ] && got=block
  if [ "$got" = "$1" ]; then
    PASS=$((PASS+1)); echo "  PASS [$got] $2"
  else
    FAIL=$((FAIL+1)); echo "  FAIL expected=$1 got=$got :: $2"; sed -n '1,3p' "$OUT"
  fi
}

echo "== writes INTO a worktree: must ALLOW =="
run allow "quoted spaced absolute path"        "cd \"$W\" && git checkout -- \"$W/$FA/reports/\""
run allow "cd worktree + relative sed -i"      "cd \"$W\" && sed -i '' 's/a/b/' $FA/x.xml"
run allow "single-quoted spaced absolute path" "cp /tmp/x '$W/$FA/x.xml'"

echo "== writes to the MAIN CHECKOUT: must BLOCK =="
run block "relative git checkout"              "git checkout -- $FA/reports/"
run block "quoted spaced absolute cp"          "cp /tmp/x \"$M/$FA/x.xml\""
run block "relative sed -i"                    "sed -i '' 's/a/b/' $FA/x.xml"
run block "cd main checkout then write"        "cd \"$M\" && cp /tmp/x $FA/x.xml"

echo "== read-only: must ALLOW =="
run allow "grep"                               "grep -r foo $FA/reports"
run allow "git diff"                           "git --no-pager diff -- $FA/reports"

echo
echo "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
