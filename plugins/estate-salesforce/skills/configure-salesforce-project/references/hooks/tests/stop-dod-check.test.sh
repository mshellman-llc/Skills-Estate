#!/bin/bash
# Regression tests for claude-hooks/stop-dod-check.sh — the Stop hook that refuses
# to end a turn while the Definition of Done is visibly incomplete.
#
# This one DOES block, so the exit code is half the contract (2 = block, and only 2;
# an exit 1 is a decorative error the harness ignores). The other half is STATE, and
# it is the half that breaks quietly:
#
#   dod-state   the fingerprint of the findings. Written on a block, and read back to
#               make an identical set of findings block ONCE. If it stops being
#               written the hook nags forever; if it is written on a path that did
#               not block, the next real finding is swallowed. Both are asserted.
#
#   hatch-log   ESTATE_SKIP_DOD=1 must be RECORDED, not merely honoured — a hatch that
#               leaves no trace is a silent gate removal. And it must NOT write
#               dod-state, or skipping once would suppress the finding for good.
#
# ONE finding: trunk ahead of the org. Ticket closure is out of this loop's scope —
# the local Definition of Done tops out at "deployed to the sandbox", so a deployed
# ticket that is still open is NOT a finding. The removed-behaviour case below pins
# that: it blocked before this change and must not now. Everything the hook reads is
# local git state (the deploy-log and the commit graph); there is no tracker call.
#
# The master gate applies here too — every hook exits 0 in a repo with no
# `estate.mode`, so the fixture sets it and the first pair of cases proves the gate
# is the only difference between blocking and not.
#
# Self-contained: builds its own throwaway repo (plus a worktree), touches nothing
# else. The path has a SPACE in it on purpose.
#
# Run: bash references/hooks/tests/stop-dod-check.test.sh

set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
HOOK="$HERE/../claude-hooks/stop-dod-check.sh"
[ -f "$HOOK" ] || { echo "missing hook: $HOOK"; exit 1; }

command -v python3 >/dev/null 2>&1 || { echo "python3 required; skipping"; exit 0; }
command -v jq      >/dev/null 2>&1 || { echo "jq required by the hook; skipping"; exit 0; }

TMP=$(mktemp -d "${TMPDIR:-/tmp}/stop dod.XXXXXX") || exit 1
TMP=$(cd "$TMP" && pwd -P)
R="$TMP/main repo"
W="$TMP/wt GH-431"
BIN="$TMP/bin"
ERR="$TMP/hook.err"
OUT="$TMP/hook.out"

cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

mkdir -p "$R" "$BIN" && cd "$R" || exit 1
git init -q -b main . >/dev/null 2>&1
git config user.email t@t.test; git config user.name t
# Without this the hook exits 0 at source time and nothing below is under test.
git config estate.mode native
git config estate.trunk main
git config estate.host github
git config estate.ticket.system github
mkdir -p force-app/main/default docs
echo x > force-app/main/default/x.xml
echo d > docs/notes.md
git add -A >/dev/null 2>&1 && git commit -qm "init refs #7" >/dev/null 2>&1
C1=$(git rev-parse HEAD)
# A second force-app commit, so trunk can be AHEAD of a deploy-log pointing at C1.
echo more >> force-app/main/default/x.xml
git commit -qam "second refs #7" >/dev/null 2>&1
C2=$(git rev-parse HEAD)

# ── gh stub ──────────────────────────────────────────────────
# The current hook makes NO tracker call, so this stub is inert for it. It exists so
# the removed-behaviour case can be replayed against the PRE-CHANGE hook (req 14):
# that version called ticket_is_open(), and GH_STATE=OPEN is what made it block on a
# deployed-but-open ticket. Keeping the stub lets that same case prove the nag is now
# gone without a second fixture.
cat > "$BIN/gh" <<'STUB'
#!/bin/bash
if [ "${1:-}" = "issue" ] && [ "${2:-}" = "view" ]; then
  for A in "$@"; do [ "$A" = "state" ] && { printf '%s\n' "${GH_STATE:-CLOSED}"; exit 0; }; done
fi
exit 0
STUB
chmod +x "$BIN/gh"
PATH="$BIN:$PATH"; export PATH
GH_STATE=CLOSED; export GH_STATE

DLOG="$R/.git/estate/deploy-log"
DODS="$R/.git/estate/dod-state"
HLOG="$R/.git/estate/hatch-log"
mkdir -p "$R/.git/estate"

PASS=0; FAIL=0
check() { # <label> <expected> <actual>
  if [ "$2" = "$3" ]; then PASS=$((PASS+1)); echo "  PASS $2 :: $1"
  else FAIL=$((FAIL+1)); echo "  FAIL $1"; echo "       expected [$2]"; echo "       got      [$3]"; fi
}
# Plain ASCII substrings: the block message carries em dashes, and grep -E is
# byte-oriented, so '.' will not match one.
says() { if grep -q "$2" "$ERR"; then PASS=$((PASS+1)); echo "  PASS says '$2' :: $1"
         else FAIL=$((FAIL+1)); echo "  FAIL $1 — stderr does not say '$2'"; sed -n '1,6p' "$ERR"; fi; }

dod() { [ -f "$DODS" ] || { printf 'NONE'; return; }; cat "$DODS"; }
verdict() { [ "$RC" -eq 2 ] && printf 'block' || printf "allow($RC)"; }

RC=0
# stop <cwd> [stop_hook_active]  — the Stop event carries no tool_input at all.
stop() {
  ( cd "$1" && python3 -c 'import json,sys
print(json.dumps({"session_id":"s1","transcript_path":"/dev/null",
                  "stop_hook_active": sys.argv[1] == "true"}))' "${2:-false}" \
    | bash "$HOOK" ) >"$OUT" 2>"$ERR"
  RC=$?
}
# One deploy-log line per argument, in the order given (oldest first).
seed_deploys() { : > "$DLOG"; for S in "$@"; do
    printf '%s 0AfAA000000001AAA 2026-01-01T00:00:00Z\n' "$S" >> "$DLOG"; done; }

echo "== the master gate: no estate.mode means the check does not run =="
seed_deploys "$C1"; rm -f "$DODS"       # trunk is C2, ahead of the recorded C1
git config --unset estate.mode
stop "$R"
check "unconfigured repo does not block" "allow(0)" "$(verdict)"
check "...and writes no state"           "NONE"     "$(dod)"
git config estate.mode native
stop "$R"
check "the same state blocks once mode is set" "block" "$(verdict)"
check "...and fingerprints what it blocked on" "yes" \
      "$([ "$(dod)" = "NONE" ] && echo no || echo yes)"

echo
echo "== the same findings block ONCE =="
FP_AHEAD=$(dod)
stop "$R"
check "stopping again does not re-block" "allow(0)" "$(verdict)"
check "...and the fingerprint is unchanged" "$FP_AHEAD" "$(dod)"

echo
echo "== nothing has ever deployed here: nothing to be done about =="
rm -f "$DLOG" "$DODS"
stop "$R"
check "no deploy-log at all" "allow(0)" "$(verdict)"
check "...and no state written" "NONE" "$(dod)"

echo
echo "== deploy-log at trunk HEAD: nothing outstanding =="
seed_deploys "$C2"; rm -f "$DODS"
stop "$R"
check "does not block" "allow(0)" "$(verdict)"
check "and writes no state" "NONE" "$(dod)"

echo
echo "== REMOVED behaviour: a deployed ticket left OPEN no longer nags =="
# Before this change the hook read ticket_is_open() and blocked here; closure is now
# out of the loop's scope, so a deployed-but-open ticket is not a finding. GH_STATE
# is OPEN to prove the point (and to make the PRE-CHANGE hook block, per req 14).
seed_deploys "$C2"; rm -f "$DODS"; GH_STATE=OPEN
stop "$R"
check "an open ticket at trunk HEAD does not block" "allow(0)" "$(verdict)"
check "and writes no state" "NONE" "$(dod)"
GH_STATE=CLOSED

echo
echo "== trunk ahead of the org =="
seed_deploys "$C1"; rm -f "$DODS"
stop "$R"
check "deployable files changed since the last deploy -> blocks" "block" "$(verdict)"
says "says which branch is ahead"     "is AHEAD OF THE ORG"
says "names the undeployed file"      "force-app/main/default/x.xml"
says "and gives the deploy command"   "sf project deploy start"

echo "== only force-app/ counts: hook, doc and config commits never reach the org =="
seed_deploys "$C2"; rm -f "$DODS"
echo more >> docs/notes.md
git commit -qam "docs: notes refs #7" >/dev/null 2>&1
C3=$(git rev-parse HEAD)
stop "$R"
check "a docs-only commit is not the org being behind" "allow(0)" "$(verdict)"
check "and writes no state" "NONE" "$(dod)"

echo "== a deploy-log sha this clone does not have =="
seed_deploys "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"; rm -f "$DODS"
stop "$R"
check "an unresolvable sha is not a finding" "allow(0)" "$(verdict)"

echo "== the NEWEST recorded deploy is the one that counts =="
# deploy_log_shas() reads newest-first and takes field 1 only; the lines are
# "<sha> <job-id> <stamp>", so a consumer treating a whole line as a sha breaks here.
seed_deploys "$C1" "$C3"; rm -f "$DODS"
stop "$R"
check "stale line first, newest at trunk -> nothing outstanding" "allow(0)" "$(verdict)"
seed_deploys "$C3" "$C1"; rm -f "$DODS"
stop "$R"
check "newest line is the stale one -> blocks" "block" "$(verdict)"

echo
echo "== the escape hatch is honoured AND recorded =="
seed_deploys "$C1"; rm -f "$DODS" "$HLOG"
ESTATE_SKIP_DOD=1 stop "$R"
check "does not block" "allow(0)" "$(verdict)"
check "recorded to the hatch-log" "SKIP_DOD;" \
      "$(awk 'NF{printf "%s;", $2}' "$HLOG" 2>/dev/null)"
# Not fingerprinting is the point: skipping the check once must not suppress the
# finding permanently, which is exactly what writing dod-state here would do.
check "no fingerprint written" "NONE" "$(dod)"
stop "$R"
check "so the finding still blocks on the next stop" "block" "$(verdict)"

rm -f "$DODS" "$HLOG"
SOLO_SKIP_DOD=1 stop "$R"
check "SOLO_ prefix still honoured" "allow(0)" "$(verdict)"
rm -f "$DODS" "$HLOG"
SOLO_SKIP_DOD=1 stop "$R"
check "SOLO_ prefix still honoured" "allow(0)" "$(verdict)"
check "and recorded too" "SKIP_DOD;" \
      "$(awk 'NF{printf "%s;", $2}' "$HLOG" 2>/dev/null)"

echo
echo "== stop_hook_active: it cannot loop =="
seed_deploys "$C1"; rm -f "$DODS"
stop "$R" true
check "does not block when already re-prompted" "allow(0)" "$(verdict)"
check "and writes no state" "NONE" "$(dod)"

echo
echo "== from inside a worktree: judged against the MAIN checkout =="
# A Stop event fires wherever the session is standing, which is routinely a worktree.
# main_repo_root() must take it to the original clone, because that is where trunk and
# all the state live — a worktree has its own HEAD and its own branch, and neither is
# the invariant being checked.
git worktree add -q "$W" -b wt/GH-431 >/dev/null 2>&1 \
  || { echo "  (could not create temp worktree; skipping this section)"; W=""; }
if [ -n "$W" ]; then
  seed_deploys "$C1"; rm -f "$DODS"
  stop "$W"
  check "blocks on main being ahead of the org" "block" "$(verdict)"
  says "and reports the TRUNK branch, not the worktree's" "'main' is AHEAD OF THE ORG"
  check "state landed in the shared common dir" "yes" \
        "$([ -f "$DODS" ] && echo yes || echo no)"
fi

echo
printf '%d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
