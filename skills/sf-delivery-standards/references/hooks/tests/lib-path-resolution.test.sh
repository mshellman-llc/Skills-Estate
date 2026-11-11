#!/bin/bash
# Regression tests for the two path-resolution helpers in claude-hooks/_lib.sh.
#
# Both bugs these cover were FAIL-OPEN or MIS-RECORD, not visible breakage, which
# is why neither was caught by using the stack — only by instrumenting it.
#
#   in_worktree()      compared a PHYSICAL path against a LOGICAL one. Under any
#                      symlinked path the main checkout read as a worktree, so the
#                      force-app guards exited 0 and allowed every write.
#
#   source_tree_root() tokenized --source-dir on whitespace with no quoted
#                      alternative, so a quoted path containing a space truncated
#                      and the function fell through to $PWD — recording the WRONG
#                      branch's HEAD as validated, which makes the merge gate
#                      block a PR that was in fact validated.
#
# macOS $TMPDIR lives under /var, a symlink to /private/var, so mktemp gives us
# the symlinked-path case for free. Do not "tidy" that by resolving the temp root.
#
# Run: bash references/hooks/tests/lib-path-resolution.test.sh

set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
LIB="$HERE/../claude-hooks/_lib.sh"
[ -f "$LIB" ] || { echo "missing lib: $LIB"; exit 1; }

TMP=$(mktemp -d "${TMPDIR:-/tmp}/lib path test.XXXXXX") || exit 1   # space on purpose
M="$TMP/main repo"
W="$TMP/wt ORG64-1"

cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

mkdir -p "$M" && cd "$M" || exit 1
git init -q -b main .                                     >/dev/null 2>&1
git config user.email t@t.test; git config user.name t
git config estate.mode native
mkdir -p force-app/main/default && echo x > force-app/main/default/x.xml
git add -A >/dev/null 2>&1 && git commit -qm init >/dev/null 2>&1
git worktree add --detach "$W" HEAD >/dev/null 2>&1 \
  || { echo "could not create temp worktree; skipping"; exit 0; }

PASS=0; FAIL=0
check() { # $1=label  $2=expected  $3=actual
  if [ "$2" = "$3" ]; then PASS=$((PASS+1)); echo "  PASS $1"
  else FAIL=$((FAIL+1)); echo "  FAIL $1 — expected [$2] got [$3]"; fi
}

# in_worktree, probed from four cwds: the main checkout and a real worktree, each
# reached by both its symlinked and its resolved path. The symlinked main-checkout
# case is the fail-open.
probe_in_worktree() { ( cd "$1" && . "$LIB" 2>/dev/null && { in_worktree "." && echo yes || echo no; } ) }

echo "== in_worktree: the main checkout is NOT a worktree, by either path =="
check "main checkout, symlinked path" no  "$(probe_in_worktree "$M")"
check "main checkout, resolved path"  no  "$(probe_in_worktree "$(cd "$M" && pwd -P)")"

echo "== in_worktree: a real worktree IS one, by either path =="
check "worktree, symlinked path"      yes "$(probe_in_worktree "$W")"
check "worktree, resolved path"       yes "$(probe_in_worktree "$(cd "$W" && pwd -P)")"

# source_tree_root must pick the tree named by --source-dir, not the cwd, and must
# survive quoting. Probed from the MAIN checkout while pointing at the WORKTREE:
# if the token is mishandled the function falls back to $PWD and answers with the
# main checkout, which is precisely the mis-record.
WP=$(cd "$W" && pwd -P)
probe_root() { ( cd "$M" && . "$LIB" 2>/dev/null && source_tree_root "$1" ) }

echo "== source_tree_root: resolves the tree the command names, quoting and all =="
check "double-quoted path with spaces" "$WP" \
  "$(probe_root "sf project deploy start --dry-run --source-dir \"$W/force-app/main/default/x.xml\"")"
check "single-quoted path with spaces" "$WP" \
  "$(probe_root "sf project deploy start --dry-run --source-dir '$W/force-app/main/default/x.xml'")"
check "-d short flag, quoted"          "$WP" \
  "$(probe_root "sf project deploy start -d \"$W/force-app/main/default/x.xml\"")"

echo
echo "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
