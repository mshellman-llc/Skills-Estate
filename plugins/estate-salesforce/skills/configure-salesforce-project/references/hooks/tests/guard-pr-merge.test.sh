#!/bin/bash
# Regression tests for claude-hooks/guard-pr-merge.sh — specifically the two
# things that let this stack run on a repo it does not own the merge policy of:
#
#   estate.squash=merge   the INVERSE of the default. Merge commits required,
#                           --squash and --rebase refused. A repo whose promotion
#                           model cherry-picks merge commits (-m 1) and reverts
#                           them (-m 1) has no structure to run on without them.
#
#   estate.protected      branches this clone may never merge INTO, whoever
#                           owns them. Checked BEFORE the validate escape hatch,
#                           because "I accept the risk of skipping a dry run" is
#                           a different decision from "I may merge here at all".
#
# The default path (squash=require, protected unset) is tested too. A change that
# makes the new values work by breaking the old ones is not a fix.
#
# `gh` is stubbed on PATH rather than mocked inside the hook: the hook's own
# argument parsing and jq handling are part of what is under test, and a stub
# that answers the real command line exercises them.
#
# Self-contained: builds its own throwaway repo, touches nothing else.
#
# Run: bash references/hooks/tests/guard-pr-merge.test.sh

set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# Point SFDS_PRMERGE_HOOK at a sibling copy of an older guard-pr-merge.sh (extract
# one with `git show <sha>:...` into the claude-hooks/ dir so it still finds
# _lib.sh) to run these against a pre-fix baseline and watch the req-8 cases fail —
# that is how a check earns trust (REQUIREMENTS.md §14).
HOOK="${SFDS_PRMERGE_HOOK:-$HERE/../claude-hooks/guard-pr-merge.sh}"
[ -f "$HOOK" ] || { echo "missing hook: $HOOK"; exit 1; }

command -v python3 >/dev/null 2>&1 || { echo "python3 required; skipping"; exit 0; }
command -v jq      >/dev/null 2>&1 || { echo "jq required by the hook; skipping"; exit 0; }

TMP=$(mktemp -d "${TMPDIR:-/tmp}/guard-prmerge.XXXXXX") || exit 1
TMP=$(cd "$TMP" && pwd -P)
R="$TMP/repo"
OUT="$TMP/hook.out"
BIN="$TMP/bin"

cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

mkdir -p "$R" "$BIN" && cd "$R" || exit 1
git init -q -b main . >/dev/null 2>&1
git config user.email t@t.test; git config user.name t
# Every hook exits 0 immediately in a repo with no estate.mode — the master
# gate. Without this nothing runs and every case "passes" as allow.
git config estate.mode native
git config estate.trunk main
git config estate.host github
echo x > a.txt
git add -A >/dev/null 2>&1 && git commit -qm init >/dev/null 2>&1

# ── gh stub ──────────────────────────────────────────────────
# Answers the two shapes guard-pr-merge.sh actually issues. $STUB_BASE picks the
# PR's base branch; the file list deliberately contains NO force-app/ path, so a
# case that gets past the protected and squash gates exits clean on
# TOUCHES_FORCE_APP=0 and any block we do see is unambiguously from the gate
# under test rather than from the validate gate.
# The stub REQUIRES a numeric PR id, and that requirement is load-bearing.
#
# It used to answer `.baseRefName` whether or not an id was passed. That masked a
# real bug completely: the hook extracted the id with `sed -E 's/.*\bgh...'`, BSD sed
# has no \b, so on macOS the id was ALWAYS empty — and the stub cheerfully answered
# anyway. Twelve cases stayed green against a guard that was inert on every
# developer machine, and only went red when tested against real `gh`.
#
# Real `gh pr view` with no id resolves the CURRENT BRANCH's PR — which, for a bare
# `gh pr merge`, IS the PR being merged. The stub models that: it answers the
# $STUB_CURRENT_PR pr when no id is passed, and fails when the branch has none.
cat > "$BIN/gh" <<'STUB'
#!/bin/bash
if [ "${1:-}" = "pr" ] && [ "${2:-}" = "view" ]; then
  ID=""
  for a in "$@"; do
    case "$a" in ''|*[!0-9]*) ;; *) ID="$a" ;; esac
  done
  # No numeric id: real `gh pr view` resolves the CURRENT BRANCH's PR — the very PR
  # a bare `gh pr merge` merges — or fails if the branch has none. $STUB_CURRENT_PR
  # models that resolution; unset means "no PR for this branch" -> non-zero exit,
  # exactly as real gh behaves.
  if [ -z "$ID" ]; then
    [ -z "${STUB_CURRENT_PR:-}" ] && exit 1
    ID="$STUB_CURRENT_PR"
  fi
  for a in "$@"; do
    [ "$a" = ".baseRefName" ] && { printf '%s\n' "${STUB_BASE:-feature/x}"; exit 0; }
  done
  # $STUB_FILES selects the .files shape the API returns, which is the whole point
  # of the req-8 cases:
  #   (unset)   a readable list with NO force-app path  -> the gate stands aside
  #   forceapp  a readable list that DOES touch force-app -> validate required
  #   omit      the .files key is ABSENT (an API hiccup, or pagination truncating
  #             the file list on a very large PR) -> the "unknown" case; must fail
  #             CLOSED, not be read as "touches nothing".
  case "${STUB_FILES:-}" in
    forceapp) printf '{"number":%s,"headRefOid":"deadbeefdeadbeef","files":[{"path":"force-app/main/default/classes/Acme.cls"}]}\n' "$ID" ;;
    omit)     printf '{"number":%s,"headRefOid":"deadbeefdeadbeef"}\n' "$ID" ;;
    *)        printf '{"number":%s,"headRefOid":"deadbeefdeadbeef","files":[{"path":"docs/readme.md"}]}\n' "$ID" ;;
  esac
  exit 0
fi
exit 1
STUB
chmod +x "$BIN/gh"
PATH="$BIN:$PATH"; export PATH

PASS=0; FAIL=0

run() { # $1=expect(allow|block)  $2=label  $3=command text
  local got rc
  printf '%s' "$3" \
    | python3 -c 'import json,sys; print(json.dumps({"tool_name":"Bash","tool_input":{"command":sys.stdin.read()}}))' \
    | bash "$HOOK" >"$OUT" 2>&1
  rc=$?
  got=allow; [ $rc -ne 0 ] && got=block
  if [ "$got" = "$1" ]; then
    PASS=$((PASS+1)); printf '  PASS [%s] %s\n' "$got" "$2"
  else
    FAIL=$((FAIL+1)); printf '  FAIL expected=%s got=%s :: %s\n' "$1" "$got" "$2"; sed -n '1,4p' "$OUT"
  fi
}

echo "== default policy (squash=require, protected unset): unchanged =="
git config --unset estate.protected 2>/dev/null
git config --unset estate.squash 2>/dev/null
STUB_BASE=main; export STUB_BASE
run block "--merge is refused when squash is required" "gh pr merge 5 --merge --delete-branch"
run allow "--squash is the sanctioned landing"         "gh pr merge 5 --squash --delete-branch"

echo
echo "== estate.squash=merge: the rule inverts =="
git config estate.squash merge
run block "--squash refused"  "gh pr merge 5 --squash --delete-branch"
run block "--rebase refused"  "gh pr merge 5 --rebase --delete-branch"
run allow "--merge accepted"  "gh pr merge 5 --merge --delete-branch"

echo
echo "== estate.protected: merges INTO a listed branch are refused =="
git config estate.protected "preprod main"
STUB_BASE=main
run block "base=main is protected"    "gh pr merge 5 --merge --delete-branch"
STUB_BASE=preprod
run block "base=preprod is protected" "gh pr merge 5 --merge --delete-branch"
STUB_BASE=sandbox-a
run allow "base=sandbox-a is not"      "gh pr merge 5 --merge --delete-branch"

echo
echo "== the validate hatch does NOT unlock a protected branch =="
STUB_BASE=main
ESTATE_ALLOW_UNVALIDATED_MERGE=1 \
  run block "hatch set, base protected" "gh pr merge 5 --merge --delete-branch"

echo
echo "== protected unset: no protected-branch behaviour at all =="
git config --unset estate.protected
STUB_BASE=main
run allow "base=main, nothing protected" "gh pr merge 5 --merge --delete-branch"

echo
echo "== the PR id must actually be extracted from the command =="
# These are the cases the old stub could not express, because it answered whether or
# not an id was passed. With BSD sed's missing \b the id was always empty, so the
# protected check took its "could not read the base" path on every Mac — and that
# path allowed. The guard reported itself configured and protected nothing.
git config estate.protected "preprod main"
STUB_BASE=main
run block "id named plainly"                 "gh pr merge 5 --merge --delete-branch"
run block "flags before the id"              "gh pr merge --delete-branch 5 --merge"
run block "id in a longer pipeline"          "git fetch && gh pr merge 5 --merge"

echo "== an unresolvable base FAILS CLOSED when branches are protected =="
# No id in the command, and (STUB_CURRENT_PR unset here) the branch has no PR gh can
# resolve, so the base cannot be established. The hook always said "an unreadable
# base is not a pass"; it now behaves that way — protected blocks, unprotected
# stands aside because there is no PR to gate. (When a current-branch PR DOES
# resolve, the no-id command is gated on it — see the flagship section below.)
run block "no id, protected set"             "gh pr merge --merge --delete-branch"
git config --unset estate.protected
run allow "no id, nothing protected"         "gh pr merge --merge --delete-branch"

echo "== non-merge commands are not this hook's business =="
run allow "gh pr create"  "gh pr create --base main --title x"
run allow "gh pr view"    "gh pr view 5"

echo
echo "== req 8: an absent/unreadable .files list FAILS CLOSED (not 'touches nothing') =="
# THE FAIL-OPEN. Pre-fix, TOUCHES_FORCE_APP=$(... [.files[]?.path ...] | length)
# returns 0 for BOTH "readable list, no force-app path" AND ".files absent/null"
# (an API hiccup, or pagination truncating a very large PR's file list). The
# 0-shortcut then ALLOWED the merge in both cases. With no recorded validate, an
# unreadable file list must instead fall through to the validate gate and BLOCK —
# the header promises "When it cannot be read, the gate requires the validate
# anyway." This case reports FAIL (got=allow) against the pre-fix hook.
git config --unset estate.protected 2>/dev/null
git config --unset estate.squash 2>/dev/null
STUB_BASE=main; export STUB_BASE
STUB_FILES=omit; export STUB_FILES
run block ".files absent, no validate -> required"    "gh pr merge 5 --squash --delete-branch"

echo "== the two determinable outcomes are unchanged (the fix did not just block everything) =="
# A readable list with no force-app path is still the correct stand-aside...
STUB_FILES=; export STUB_FILES
run allow "files readable, no force-app path"          "gh pr merge 5 --squash --delete-branch"
# ...and a readable list that DOES touch force-app still requires a validate...
STUB_FILES=forceapp; export STUB_FILES
run block "force-app touched, no validate"            "gh pr merge 5 --squash --delete-branch"
# ...and passes once THAT commit (headRefOid) has a recorded validate.
VLOG="$R/.git/estate/validate-log"
mkdir -p "$(dirname "$VLOG")"
printf '%s validated\n' deadbeefdeadbeef >> "$VLOG"
run allow "force-app touched, validate on record"     "gh pr merge 5 --squash --delete-branch"
rm -f "$VLOG"
STUB_FILES=; export STUB_FILES

echo
echo "== flagship: the DOCUMENTED no-id merge command is gated via current-branch resolution =="
# `gh pr merge --squash --delete-branch` (no number) merges the CURRENT branch's PR,
# so `gh pr view` with no arg resolves the very PR being merged and the gate enforces
# validate on it. Pre-fix the hook bailed on the empty id (`[ -z "$PR_ARG" ] && exit
# 0`) and skipped the gate entirely — and on GitHub this is the ONLY interception
# point, so the blessed happy-path command landed force-app on trunk unvalidated. The
# first case reports FAIL (got=allow) against the pre-fix hook; the original
# The predecessor gate (sw-platform) enforced it exactly this way.
git config --unset estate.protected 2>/dev/null
STUB_BASE=main; export STUB_BASE
STUB_CURRENT_PR=7; export STUB_CURRENT_PR
STUB_FILES=forceapp; export STUB_FILES
run block "no-id merge, force-app, no validate"        "gh pr merge --squash --delete-branch"
STUB_FILES=; export STUB_FILES
run allow "no-id merge, no force-app path"             "gh pr merge --squash --delete-branch"
STUB_FILES=forceapp; export STUB_FILES
VLOG="$R/.git/estate/validate-log"
mkdir -p "$(dirname "$VLOG")"
printf '%s validated\n' deadbeefdeadbeef >> "$VLOG"
run allow "no-id merge, force-app, validate on record" "gh pr merge --squash --delete-branch"
rm -f "$VLOG"
STUB_CURRENT_PR=; export STUB_CURRENT_PR
STUB_FILES=; export STUB_FILES

echo
printf '%d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
