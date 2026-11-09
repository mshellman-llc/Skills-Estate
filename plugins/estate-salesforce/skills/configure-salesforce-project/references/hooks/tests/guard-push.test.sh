#!/bin/bash
# Regression tests for claude-hooks/guard-push.sh — the push gate, active ONLY on
# Bitbucket, where it is the SOLE interception point before a web-UI merge. A
# fail-open here has no backstop.
#
# REQUIREMENT 8 (fail CLOSED on an indeterminate answer) is the focus. The bug:
#
#   BASE=$(git merge-base "$TRUNK" HEAD 2>/dev/null) || exit 0
#
# When the base cannot be computed — an unresolvable trunk, or orphan / unrelated
# history — the guard exited 0, so an unvalidated force-app branch could be pushed
# and then merged in the browser. "I can't compute the base" is NOT "there is
# nothing to validate". The fix falls back to HEAD's own tree: force-app present
# (or a HEAD whose tree cannot be read) falls through to the validate gate and
# BLOCKS; a genuinely clean tree is still allowed.
#
# The determinable paths are covered too, so a fix that made everything block by
# way of the fallback would not pass: a normal force-app branch with no validate
# still blocks, a docs-only branch still allows, a recorded validate still opens
# the gate, and a non-Bitbucket host / a trunk push are still inert.
#
# Point SFDS_PUSH_HOOK at a sibling copy of an older guard-push.sh (extract one
# with `git show <sha>:...` into the claude-hooks/ dir so it still finds _lib.sh)
# to run these against a pre-fix baseline and watch the req-8 case fail — that is
# how a check earns trust (REQUIREMENTS.md §14).
#
# Self-contained: builds its own throwaway repos, touches nothing else.
#
# Run: bash references/hooks/tests/guard-push.test.sh

set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
HOOK="${SFDS_PUSH_HOOK:-$HERE/../claude-hooks/guard-push.sh}"
[ -f "$HOOK" ] || { echo "missing hook: $HOOK"; exit 1; }

command -v python3 >/dev/null 2>&1 || { echo "python3 required; skipping"; exit 0; }
command -v git     >/dev/null 2>&1 || { echo "git required"; exit 1; }

TMP=$(mktemp -d "${TMPDIR:-/tmp}/guard-push.XXXXXX") || exit 1
TMP=$(cd "$TMP" && pwd -P)
OUT="$TMP/hook.out"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

# A base repo: one commit on main (a doc), Bitbucket host, native mode. Without
# estate.mode the master gate exits 0 and every case "passes" as allow.
mkbase() { # $1=dir
  local d="$1"
  mkdir -p "$d"
  ( cd "$d" \
    && git init -q -b main . >/dev/null 2>&1 \
    && git config user.email t@t.test && git config user.name t \
    && git config estate.mode native \
    && git config estate.trunk main \
    && git config estate.host bitbucket \
    && echo x > readme.md && git add -A >/dev/null 2>&1 \
    && git commit -qm init >/dev/null 2>&1 )
}

add_forceapp() { # $1=dir -> commit a force-app file on the current branch
  ( cd "$1" \
    && mkdir -p force-app/main/default/classes \
    && echo 'public class Acme {}' > force-app/main/default/classes/Acme.cls \
    && git add -A >/dev/null 2>&1 && git commit -qm "add Acme" >/dev/null 2>&1 )
}

record_validate() { # $1=dir -> mark HEAD as validated
  local vl; vl="$1/.git/estate/validate-log"
  mkdir -p "$(dirname "$vl")"
  printf '%s validated\n' "$(cd "$1" && git rev-parse HEAD)" >> "$vl"
}

PASS=0; FAIL=0

run() { # $1=expect(allow|block) $2=cwd $3=label $4=command text
  local want="$1" cwd="$2" label="$3" cmd="$4" got rc
  printf '%s' "$cmd" \
    | python3 -c 'import json,sys; print(json.dumps({"tool_name":"Bash","tool_input":{"command":sys.stdin.read()}}))' \
    | ( cd "$cwd" && bash "$HOOK" ) >"$OUT" 2>&1
  rc=$?
  got=allow; [ $rc -ne 0 ] && got=block
  if [ "$got" = "$want" ]; then
    PASS=$((PASS+1)); printf '  PASS [%s] %s\n' "$got" "$label"
  else
    FAIL=$((FAIL+1)); printf '  FAIL expected=%s got=%s :: %s\n' "$want" "$got" "$label"; sed -n '2,4p' "$OUT"
  fi
}

# ── the fix: base indeterminable (orphan / unrelated history) ────────────────
echo "== req 8: merge-base fails + force-app on HEAD -> FAILS CLOSED =="
# An orphan branch shares no ancestor with main, so `git merge-base main HEAD`
# fails. Pre-fix that took `|| exit 0` and the unvalidated force-app branch was
# waved through. This case reports FAIL (got=allow) against the pre-fix hook.
ORFA="$TMP/orphan-fa"; mkbase "$ORFA"
( cd "$ORFA" && git checkout -q --orphan feature/orphan && git rm -rf -q . >/dev/null 2>&1 )
add_forceapp "$ORFA"
run block "$ORFA" "orphan branch, force-app, no validate" "git push -u origin feature/orphan"

echo "== base indeterminable but HEAD carries no force-app -> a clean push is still allowed =="
ORDOCS="$TMP/orphan-docs"; mkbase "$ORDOCS"
( cd "$ORDOCS" && git checkout -q --orphan feature/od && git rm -rf -q . >/dev/null 2>&1 \
  && echo notes > notes.md && git add -A >/dev/null 2>&1 && git commit -qm "docs" >/dev/null 2>&1 )
run allow "$ORDOCS" "orphan branch, docs only"            "git push -u origin feature/od"

echo "== base indeterminable, force-app on HEAD, but a validate is on record -> allowed =="
ORVAL="$TMP/orphan-validated"; mkbase "$ORVAL"
( cd "$ORVAL" && git checkout -q --orphan feature/ov && git rm -rf -q . >/dev/null 2>&1 )
add_forceapp "$ORVAL"; record_validate "$ORVAL"
run allow "$ORVAL" "orphan branch, force-app, validated"  "git push -u origin feature/ov"

# ── controls: the determinable paths are unchanged ──────────────────────────
echo "== determinable: normal force-app branch with no validate still blocks =="
FA="$TMP/normal-fa"; mkbase "$FA"
( cd "$FA" && git checkout -q -b feature/fa )
add_forceapp "$FA"
run block "$FA" "force-app change vs trunk, no validate"  "git push -u origin feature/fa"

echo "== determinable: force-app branch WITH a recorded validate is allowed =="
FAV="$TMP/normal-fa-validated"; mkbase "$FAV"
( cd "$FAV" && git checkout -q -b feature/fav )
add_forceapp "$FAV"; record_validate "$FAV"
run allow "$FAV" "force-app change vs trunk, validated"   "git push -u origin feature/fav"

echo "== determinable: a docs-only branch has nothing to validate =="
DOCS="$TMP/normal-docs"; mkbase "$DOCS"
( cd "$DOCS" && git checkout -q -b feature/docs \
  && echo more >> readme.md && git add -A >/dev/null 2>&1 && git commit -qm "doc" >/dev/null 2>&1 )
run allow "$DOCS" "no force-app change vs trunk"          "git push -u origin feature/docs"

# ── scope: only Bitbucket, only branch pushes ───────────────────────────────
echo "== inert off Bitbucket, and for a trunk push =="
NONBB="$TMP/github-host"; mkbase "$NONBB"
( cd "$NONBB" && git config estate.host github \
  && git checkout -q --orphan feature/gh && git rm -rf -q . >/dev/null 2>&1 )
add_forceapp "$NONBB"
run allow "$NONBB" "host=github: not this hook's surface"  "git push -u origin feature/gh"
# The hook reads the repo's ACTUAL current branch, not the command text — so this
# repo must genuinely be on trunk. mkbase leaves it on main.
TRUNKP="$TMP/on-trunk"; mkbase "$TRUNKP"
run allow "$TRUNKP" "pushing trunk itself (post-merge sync)" "git push origin main"

echo "== the escape hatch is honoured =="
run allow "$ORFA" "ESTATE_ALLOW_UNVALIDATED_PUSH=1"          "ESTATE_ALLOW_UNVALIDATED_PUSH=1 git push -u origin feature/orphan"

echo "== non-push commands are not this hook's business =="
run allow "$FA" "git status is not a push"                 "git status"

echo
echo "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
