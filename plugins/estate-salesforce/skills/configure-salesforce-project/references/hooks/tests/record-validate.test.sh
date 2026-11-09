#!/bin/bash
# Regression tests for claude-hooks/record-validate.sh — the recorder that decides
# whether guard-pr-merge.sh will let a PR land.
#
# THIS IS NOT A BLOCKER, SO THE EXIT CODE PROVES NOTHING. record-validate.sh exits
# 0 on every path there is: when it records, when it deliberately declines to, and
# when it silently does nothing because a path token was mishandled. A recorder
# that writes nothing is indistinguishable from a working one by return code
# alone, and a recorder that writes the WRONG SHA looks healthiest of all. So
# every case below asserts the SIDE EFFECT — exactly what landed in
# .git/estate/validate-log and pending-jobs, and what did not.
#
# The four things this pins down, each one a shipped bug:
#
#   the master gate      every hook exits 0 in a repo with no `estate.mode`. The
#                        fixture sets it, and one case unsets it again to prove the
#                        gate is the only difference — otherwise a suite can be
#                        entirely green against a hook that never ran.
#
#   the org, not stdout  "Status: Succeeded" cannot tell a dry run from a real
#                        deploy, and that distinction is the whole proof-of-deploy
#                        gate. sf_deploy_verdict() asks the org via `deploy report
#                        --job-id`. Cases below contradict the console text in both
#                        directions and assert the ORG wins.
#
#   the named tree       a dry run validates FILES. source_tree_root() must credit
#                        the tree named by --source-dir, not the shell's cwd —
#                        recording the wrong tree's HEAD blocks a PR that was in
#                        fact validated. Tested with a QUOTED path containing a
#                        SPACE, because that truncation has shipped here twice.
#
#   async correlation    a `deploy report` on a job we never started is a lookup,
#                        not a result. Recording HEAD against one would unlock the
#                        merge gate for a commit nothing ran against.
#
# `sf` is stubbed on PATH rather than mocked inside the hook, so the hook's own
# argument handling is under test. THE STUB REQUIRES --job-id AND FAILS WITHOUT IT:
# a stub that answers regardless of its arguments hid a real bug in this repo for
# months (see guard-pr-merge.test.sh's gh stub for the same lesson). One case reads
# the stub's invocation log back to prove the id was actually passed.
#
# Self-contained: builds its own throwaway repo + worktree, touches nothing else.
# The temp root has a SPACE in it on purpose. Do not "tidy" that away; it is the test.
#
# Run: bash references/hooks/tests/record-validate.test.sh

set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
HOOK="$HERE/../claude-hooks/record-validate.sh"
[ -f "$HOOK" ] || { echo "missing hook: $HOOK"; exit 1; }

command -v python3 >/dev/null 2>&1 || { echo "python3 required; skipping"; exit 0; }
command -v jq      >/dev/null 2>&1 || { echo "jq required by the hook; skipping"; exit 0; }

TMP=$(mktemp -d "${TMPDIR:-/tmp}/record validate.XXXXXX") || exit 1   # space on purpose
TMP=$(cd "$TMP" && pwd -P)
M="$TMP/main repo"
W="$TMP/wt GH-431"
BIN="$TMP/bin"
OUT="$TMP/hook.out"
SF_LOG="$TMP/sf.invocations"

cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

mkdir -p "$M" "$BIN" && cd "$M" || exit 1
git init -q -b main . >/dev/null 2>&1
git config user.email t@t.test; git config user.name t
# Without this every hook exits 0 at source time and nothing below is under test.
git config estate.mode native
git config estate.trunk main
git config estate.ticket.system github
mkdir -p force-app/main/default && echo x > force-app/main/default/x.xml
mkdir -p docs && printf 'nothing\n' > docs/runbook.md
git add -A >/dev/null 2>&1 && git commit -qm "init refs #7" >/dev/null 2>&1
git branch -q feature/x
git worktree add -q "$W" feature/x >/dev/null 2>&1 \
  || { echo "could not create temp worktree; skipping"; exit 0; }
( cd "$W" && echo y > force-app/main/default/y.xml \
  && git add -A >/dev/null 2>&1 && git commit -qm "wt refs #9" >/dev/null 2>&1 )

MSHA=$(git -C "$M" rev-parse HEAD)
WSHA=$(git -C "$W" rev-parse HEAD)

# State lives in the COMMON git dir, so the worktree's dry run is visible to the
# orchestrator standing on trunk. Asserting the literal path is part of the point.
VLOG="$M/.git/estate/validate-log"
PLOG="$M/.git/estate/pending-jobs"

# ── sf stub ──────────────────────────────────────────────────
# Answers the one shape the hook issues: `sf project deploy report --job-id <ID> --json`.
#
# It REQUIRES the id. Real `sf` has --use-most-recent for the no-id case, which in a
# shared org resolves to somebody else's deploy — so "no id" is not a question with a
# safe answer, and the stub refuses it rather than guessing. That refusal is what makes
# the "the id reaches the org" case below meaningful: if the hook stopped passing it,
# the verdict would silently fall back to parsing console text and several cases here
# would flip.
#
# It also echoes back the id it was given, so the hook's own `.result.id == $id` guard
# is exercised; STUB_ID overrides it to simulate `deploy report` answering from its
# local cache about a DIFFERENT job, which is no answer at all.
cat > "$BIN/sf" <<'STUB'
#!/bin/bash
printf '%s\n' "$*" >> "${SF_LOG:-/dev/null}"
[ "${1:-}" = "project" ] && [ "${2:-}" = "deploy" ] && [ "${3:-}" = "report" ] || exit 1
ID=""; PREV=""
for A in "$@"; do [ "$PREV" = "--job-id" ] && ID="$A"; PREV="$A"; done
[ -z "$ID" ] && { echo "Error: --job-id or --use-most-recent is required" >&2; exit 1; }
[ "${STUB_UNRESOLVED:-0}" = "1" ] && { echo '{"status":1,"message":"job not found"}'; exit 1; }
# Eventual consistency: answer InProgress for the first STUB_INPROGRESS_UNTIL report
# calls, then the real STUB_STATUS. Opt-in (needs both vars), so every other case is
# untouched. This is the EXAMPLE-161 window — a finished synchronous run the org has
# not yet marked terminal — and it is what the verdict poll must ride out.
if [ -n "${STUB_INPROGRESS_UNTIL:-}" ] && [ -n "${STUB_COUNT_FILE:-}" ]; then
  n=$(cat "$STUB_COUNT_FILE" 2>/dev/null || echo 0); n=$((n+1)); echo "$n" > "$STUB_COUNT_FILE"
  if [ "$n" -le "$STUB_INPROGRESS_UNTIL" ]; then
    printf '{"status":0,"result":{"id":"%s","status":"InProgress","checkOnly":%s}}\n' \
      "${STUB_ID:-$ID}" "${STUB_CHECKONLY:-true}"; exit 0
  fi
fi
printf '{"status":0,"result":{"id":"%s","status":"%s","checkOnly":%s}}\n' \
  "${STUB_ID:-$ID}" "${STUB_STATUS:-Succeeded}" "${STUB_CHECKONLY:-true}"
STUB
chmod +x "$BIN/sf"
PATH="$BIN:$PATH"; export PATH
export SF_LOG
STUB_STATUS=Succeeded; STUB_CHECKONLY=true; STUB_UNRESOLVED=0; STUB_ID=""
export STUB_STATUS STUB_CHECKONLY STUB_UNRESOLVED STUB_ID

J1=0AfAA000000001AAA
J2=0AfBB000000002BBB
UNKNOWN_JOB=0AfZZ000000009ZZZ

# ── harness ──────────────────────────────────────────────────

PASS=0; FAIL=0
check() { # <label> <expected> <actual>
  if [ "$2" = "$3" ]; then PASS=$((PASS+1)); echo "  PASS $2 :: $1"
  else FAIL=$((FAIL+1)); echo "  FAIL $1"; echo "       expected [$2]"; echo "       got      [$3]"; fi
}

# The recorded state, rendered compactly so an expectation is readable inline.
#   validate-log -> "<sha8>@<branch>;" per line, oldest first
#   pending-jobs -> "<job>/<sha8>/<kind>;" per line
vlog() { [ -f "$VLOG" ] || { printf 'ABSENT'; return; }
         awk 'NF{printf "%s@%s;", substr($1,1,8), $2}' "$VLOG"; }
pend() { [ -f "$PLOG" ] || { printf 'ABSENT'; return; }
         awk 'NF{printf "%s/%s/%s;", $1, substr($2,1,8), $3}' "$PLOG"; }
s8()   { printf '%s' "${1:0:8}"; }

reset() { rm -f "$VLOG" "$PLOG"; : > "$SF_LOG"; }

# fire <cwd> <command text> <tool stdout>
# The PostToolUse payload carries the tool's OUTPUT, which is what the hook reads.
RC=0
fire() {
  ( cd "$1" && python3 -c 'import json,sys
print(json.dumps({"tool_name":"Bash",
                  "tool_input":{"command":sys.argv[1]},
                  "tool_response":{"stdout":sys.argv[2],"stderr":""}}))' "$2" "$3" \
    | bash "$HOOK" ) >"$OUT" 2>&1
  RC=$?
}

SUCCEEDED='Deploy ID: '"$J1"'
Status: Succeeded'

echo "== the master gate: no estate.mode means no recording at all =="
reset
git config --unset estate.mode
fire "$M" "sf project deploy start --dry-run --source-dir force-app --json" "$SUCCEEDED"
check "unconfigured repo records nothing" "ABSENT" "$(vlog)"
git config estate.mode native
fire "$M" "sf project deploy start --dry-run --source-dir force-app --json" "$SUCCEEDED"
check "the same input records once mode is set" "$(s8 "$MSHA")@main;" "$(vlog)"

echo
echo "== the ORG decides check-only, not the console text =="
reset
STUB_CHECKONLY=true
fire "$M" "sf project deploy start --dry-run --source-dir force-app" "$SUCCEEDED"
check "org says checkOnly -> recorded" "$(s8 "$MSHA")@main;" "$(vlog)"

reset
STUB_CHECKONLY=false
fire "$M" "sf project deploy start --dry-run --source-dir force-app" "$SUCCEEDED"
check "org says a REAL deploy -> not a validate, records nothing" "ABSENT" "$(vlog)"

reset
STUB_CHECKONLY=true
fire "$M" "sf project deploy start --dry-run --source-dir force-app" "Deploy ID: $J1
Status: Failed
Error: something looked wrong on the console"
check "console says Failed, org says check-only Succeeded -> recorded" \
      "$(s8 "$MSHA")@main;" "$(vlog)"

echo
echo "== the job id must actually reach the org =="
# If it stopped being passed, the stub would refuse, the verdict would fall back to
# console text, and the two contradiction cases above would quietly flip.
reset
STUB_CHECKONLY=true
fire "$M" "sf project deploy start --dry-run --source-dir force-app" "$SUCCEEDED"
check "the org was asked about this exact job" \
      "project deploy report --job-id $J1 --json" "$(head -1 "$SF_LOG")"

reset
STUB_CHECKONLY=true; STUB_ID="$J2"     # answers about a different job: no answer
fire "$M" "sf project deploy start --dry-run --source-dir force-app" "$SUCCEEDED"
check "org answers about another job -> text fallback, --dry-run reads as validate" \
      "$(s8 "$MSHA")@main;" "$(vlog)"
STUB_ID=""

reset
STUB_UNRESOLVED=1
fire "$M" "sf project deploy start --dry-run --source-dir force-app" "$SUCCEEDED"
check "org cannot resolve the job -> console text + --dry-run -> recorded" \
      "$(s8 "$MSHA")@main;" "$(vlog)"

reset
STUB_UNRESOLVED=1
fire "$M" "sf project deploy start --dry-run --async --source-dir force-app" "Deploy ID: $J1"
check "unresolvable and nothing conclusive to read -> UNKNOWN, not recorded" "ABSENT" "$(vlog)"
check "...but remembered as pending, so the eventual report is ours" \
      "$J1/$(s8 "$MSHA")/validate;" "$(pend)"
STUB_UNRESOLVED=0

echo
echo "== the tree the COMMAND NAMES is credited, not the shell's cwd =="
# Fired from the main checkout while pointing at the worktree. A mishandled token
# falls through to \$PWD and records main's HEAD on branch main — which reads as a
# success and blocks the worktree's PR as unvalidated.
STUB_CHECKONLY=true
reset
fire "$M" "sf project deploy start --dry-run --source-dir \"$W/force-app/main/default/y.xml\"" "$SUCCEEDED"
check "double-quoted --source-dir with spaces credits the worktree" \
      "$(s8 "$WSHA")@feature/x;" "$(vlog)"

reset
fire "$M" "sf project deploy start --dry-run --source-dir '$W/force-app'" "$SUCCEEDED"
check "single-quoted --source-dir with spaces credits the worktree" \
      "$(s8 "$WSHA")@feature/x;" "$(vlog)"

reset
fire "$M" "sf project deploy start --dry-run -d \"$W/force-app\" --json" "$SUCCEEDED"
check "-d short flag, quoted" "$(s8 "$WSHA")@feature/x;" "$(vlog)"

reset
fire "$M" "sf project deploy start --dry-run --manifest package.xml" "$SUCCEEDED"
check "no --source-dir at all falls back to cwd (the control)" \
      "$(s8 "$MSHA")@main;" "$(vlog)"

reset
fire "$W" "sf project deploy start --dry-run --source-dir force-app" "$SUCCEEDED"
check "run FROM the worktree: its HEAD lands in the shared common-dir log" \
      "$(s8 "$WSHA")@feature/x;" "$(vlog)"

echo
echo "== uncommitted force-app changes are recorded AND warned about =="
# Checked in the SOURCE tree, for the same reason the SHA is read from there.
reset
echo dirty >> "$W/force-app/main/default/y.xml"
fire "$M" "sf project deploy start --dry-run --source-dir \"$W/force-app\"" "$SUCCEEDED"
check "still recorded" "$(s8 "$WSHA")@feature/x;" "$(vlog)"
# Plain ASCII substring: grep -E is byte-oriented and the notes carry em dashes.
if grep -q 'has uncommitted changes' "$OUT"; then PASS=$((PASS+1)); echo "  PASS warned about the dirty source tree"
else FAIL=$((FAIL+1)); echo "  FAIL no warning about the dirty source tree"; fi
git -C "$W" checkout -- force-app >/dev/null 2>&1

echo
echo "== async correlation: a report is only ours if we watched the start =="
reset
STUB_STATUS=InProgress
fire "$M" "sf project deploy start --dry-run --async --source-dir force-app" "Deploy ID: $J1"
check "in flight: nothing recorded" "ABSENT" "$(vlog)"
check "in flight: remembered as a pending VALIDATE" "$J1/$(s8 "$MSHA")/validate;" "$(pend)"

# main moves while the dry run is in flight. The eventual report must credit the
# commit that was actually sent, not whatever HEAD became.
echo moved >> "$M/force-app/main/default/x.xml"
( cd "$M" && git commit -qam "moved on refs #7" >/dev/null 2>&1 )
MSHA2=$(git -C "$M" rev-parse HEAD)
STUB_STATUS=Succeeded; STUB_CHECKONLY=true
fire "$M" "sf project deploy report --job-id $J1" "Status: Succeeded"
check "the report credits the PENDING sha, not the new HEAD" \
      "$(s8 "$MSHA")@main;" "$(vlog)"
check "the pending entry is cleared" "" "$(pend)"

reset
fire "$M" "sf project deploy report --job-id $UNKNOWN_JOB" "Status: Succeeded"
check "a report on a job we never started records nothing" "ABSENT" "$(vlog)"

reset
echo "$J1 $MSHA2 deploy" > "$PLOG"
fire "$M" "sf project deploy report --job-id $J1" "Status: Succeeded"
check "a pending DEPLOY is not this hook's to record" "ABSENT" "$(vlog)"
check "...and its pending entry is left alone" "$J1/$(s8 "$MSHA2")/deploy;" "$(pend)"

reset
echo "$J1 $MSHA2 validate" > "$PLOG"
fire "$M" "sf project deploy resume --job-id $J1" "Status: Succeeded"
check "deploy resume is honoured the same way as report" "$(s8 "$MSHA2")@main;" "$(vlog)"

reset
echo "$J1 $MSHA2 validate" > "$PLOG"
STUB_STATUS=Failed
fire "$M" "sf project deploy report --job-id $J1" "Status: Failed"
check "a FAILED validate records nothing" "ABSENT" "$(vlog)"
check "...and stops being pending, so a later lookup is not mistaken for a result" \
      "" "$(pend)"
STUB_STATUS=Succeeded

echo
echo "== idempotency: one line per sha, however many times it is reported =="
reset
STUB_CHECKONLY=true
fire "$M" "sf project deploy start --dry-run --source-dir force-app" "$SUCCEEDED"
fire "$M" "sf project deploy start --dry-run --source-dir force-app" "$SUCCEEDED"
fire "$M" "sf project deploy start --dry-run --source-dir force-app" "$SUCCEEDED"
check "three identical validates, one entry" "$(s8 "$MSHA2")@main;" "$(vlog)"

echo
echo "== commands that are not this hook's business =="
reset
fire "$M" "sf project deploy start --source-dir force-app" "$SUCCEEDED"
check "a real deploy belongs to auto-label-deploy.sh" "ABSENT" "$(vlog)"
fire "$M" "sf org list --json" "$SUCCEEDED"
check "sf org list" "ABSENT" "$(vlog)"
fire "$M" "git status --porcelain" ""
check "git status" "ABSENT" "$(vlog)"
fire "$M" "sf project deploy start --dry-run --source-dir force-app" "Deploying...
still going"
check "no verdict to be had -> nothing recorded" "ABSENT" "$(vlog)"

echo
echo "== a command that only MENTIONS a validate must not record one =="
# The trigger is anchored to a COMMAND POSITION (SFDS_DEPLOY_RE / SFDS_CMDPOS in
# _lib.sh), the same anchor record-escape-hatch.sh has always used. Unanchored, these
# recorded a validate for a commit nothing was ever run against: searching the docs
# for the documented dry-run command is ordinary work, and when the doc quotes a
# sample transcript the grep OUTPUT carries 'Status: Succeeded'. That forges the
# evidence guard-pr-merge.sh reads, which is worse than missing it.
reset
STUB_UNRESOLVED=1     # prose carries no job id the org could resolve
fire "$M" 'grep -rn "sf project deploy start --dry-run" docs/' \
  'docs/runbook.md:12:  sf project deploy start --dry-run --source-dir force-app
docs/runbook.md:13:  Status: Succeeded'
check "grepping the docs for the command records nothing" "ABSENT" "$(vlog)"

reset
fire "$M" 'echo "always sf project deploy start --dry-run first" >> docs/runbook.md' \
  'always sf project deploy start --dry-run first
Status: Succeeded'
check "echoing the command into a doc records nothing" "ABSENT" "$(vlog)"

reset
fire "$M" 'git commit -m "docs: sf project deploy start --dry-run before every merge"' \
  '[main 1234567] docs
 Status: Succeeded'
check "a commit message quoting the command records nothing" "ABSENT" "$(vlog)"
STUB_UNRESOLVED=0

echo
echo "== ...while a real dry run still records, in every ordinary shape =="
# The other half of anchoring: over-anchor and the recorder goes silent, which is the
# same gate failure wearing a different hat. These are the shapes a dry run actually
# arrives in.
STUB_CHECKONLY=true
reset
fire "$M" "git pull --quiet && sf project deploy start --dry-run --source-dir force-app" "$SUCCEEDED"
check "after a && separator" "$(s8 "$MSHA2")@main;" "$(vlog)"
reset
fire "$M" "cd \"$M\" && sf project deploy start --dry-run -d force-app" "$SUCCEEDED"
check "after a cd into the repo" "$(s8 "$MSHA2")@main;" "$(vlog)"
reset
fire "$M" "SF_LOG_LEVEL=warn sf project deploy start --dry-run --source-dir force-app" "$SUCCEEDED"
check "behind an env assignment" "$(s8 "$MSHA2")@main;" "$(vlog)"
# A genuine dry run reaches the org and so emits a job id, even when the org later
# cannot resolve it (cache miss). That id (in "$SUCCEEDED") is what tells this
# fallback the run was real, so the text success is honoured.
reset
STUB_UNRESOLVED=1
fire "$M" "sf project deploy start --dry-run --source-dir force-app" "$SUCCEEDED"
check "unresolvable id + --dry-run + text success still records" \
      "$(s8 "$MSHA2")@main;" "$(vlog)"
STUB_UNRESOLVED=0

echo
echo "== FORGE 2: a bare echoed success line cannot alone unlock the merge gate =="
# sf_deploy_verdict returns VALIDATE from plain text only when the run actually
# reached the org (it emitted a job id). A dry run whose real result is suppressed,
# with "Status: Succeeded" echoed after it, carries NO id — so it is UNKNOWN, not a
# validate, and nothing is recorded. Before the fix this recorded HEAD as validated.
reset
fire "$M" "sf project deploy start --dry-run --source-dir force-app 2>/dev/null; echo \"Status: Succeeded\"" \
  "Status: Succeeded"
check "echoed 'Status: Succeeded' with no job id records nothing" "ABSENT" "$(vlog)"
check "...and is not remembered as pending either" "ABSENT" "$(pend)"

# Same forge, but the fabricated success arrives as a JSON blob echoed after a
# --json run whose real envelope is a failure. JSON is authoritative when present,
# so the echoed success does not override the structured Failed result.
reset
fire "$M" "sf project deploy start --dry-run --json --source-dir force-app 2>/dev/null; echo '{\"result\":{\"status\":\"Succeeded\"}}'" \
  '{"status":1,"result":{"status":"Failed"}}
{"result":{"status":"Succeeded"}}'
check "an echoed JSON success cannot override a real Failed envelope" "ABSENT" "$(vlog)"

echo
echo "== EXAMPLE-161: a synchronous dry run the org has not FINALISED yet =="
# A long dry run (full test suite) returns green, but a fresh `deploy report` fired
# by this hook a moment later can still say InProgress — the org's status API lags
# a job it just finished. The verdict must not stall at UNKNOWN and drop the run to a
# pending entry nothing finalises (that is the bug: no validate-log line, so
# guard-pr-merge blocks a genuinely green commit). It must poll to a terminal status
# and record the pass. Not an --async run: the command BLOCKED to completion here.
reset
: > "$TMP/poll.count"
STUB_COUNT_FILE="$TMP/poll.count"; export STUB_COUNT_FILE
STUB_INPROGRESS_UNTIL=2; export STUB_INPROGRESS_UNTIL   # two InProgress, then Succeeded
SFDS_JOB_POLL_SLEEP=0; export SFDS_JOB_POLL_SLEEP        # no real waiting in the test
STUB_CHECKONLY=true
fire "$M" "sf project deploy start --dry-run --source-dir force-app --json" "$SUCCEEDED"
check "org InProgress then Succeeded -> polled to a pass and recorded" \
      "$(s8 "$MSHA2")@main;" "$(vlog)"
check "...and not left dangling as a pending validate" "ABSENT" "$(pend)"
unset STUB_INPROGRESS_UNTIL STUB_COUNT_FILE SFDS_JOB_POLL_SLEEP

# The async counterpart is UNCHANGED: an --async start that the org reports InProgress
# is still remembered as pending, never polled (a poll would hang for the deploy's
# length). This pins the boundary the fix draws between the two.
reset
: > "$TMP/poll.count"
STUB_COUNT_FILE="$TMP/poll.count"; export STUB_COUNT_FILE
STUB_INPROGRESS_UNTIL=99; export STUB_INPROGRESS_UNTIL  # would never resolve if polled
SFDS_JOB_POLL_SLEEP=0; export SFDS_JOB_POLL_SLEEP
fire "$M" "sf project deploy start --dry-run --async --source-dir force-app" "Deploy ID: $J1"
check "async InProgress -> not polled, nothing recorded" "ABSENT" "$(vlog)"
check "async InProgress -> remembered as a pending VALIDATE" "$J1/$(s8 "$MSHA2")/validate;" "$(pend)"
unset STUB_INPROGRESS_UNTIL STUB_COUNT_FILE SFDS_JOB_POLL_SLEEP

echo
echo "== TaskCompleted: the same script records when fired as a completed background task =="
# When the harness auto-backgrounds a long-running validate, PostToolUse fires with
# an incomplete result (the command is still running). TaskCompleted fires when it
# actually finishes, carrying the real output. The hook is registered under both
# events. This tests that the hook records correctly when the input carries
# hook_event_name: "TaskCompleted".

# fire_tc: same as fire() but injects hook_event_name into the JSON payload.
fire_tc() {
  ( cd "$1" && python3 -c 'import json,sys
print(json.dumps({"hook_event_name":"TaskCompleted",
                  "tool_name":"Bash",
                  "tool_input":{"command":sys.argv[1]},
                  "tool_response":{"stdout":sys.argv[2],"stderr":""}}))' "$2" "$3" \
    | bash "$HOOK" ) >"$OUT" 2>&1
  RC=$?
}

STUB_CHECKONLY=true; STUB_UNRESOLVED=0; STUB_STATUS=Succeeded
reset
fire_tc "$M" "sf project deploy start --dry-run --source-dir force-app" "$SUCCEEDED"
check "TaskCompleted event records exactly like PostToolUse" \
      "$(s8 "$MSHA2")@main;" "$(vlog)"

reset
fire_tc "$M" "sf project deploy start --dry-run --source-dir \"$W/force-app\"" "$SUCCEEDED"
check "TaskCompleted: quoted source-dir with spaces credits the worktree" \
      "$(s8 "$WSHA")@feature/x;" "$(vlog)"

# Verify HOOK_EVENT is derived from the input. When the hook emits a note(), it stamps
# hookEventName. A PostToolUse hookEventName on a TaskCompleted event is dropped by the
# harness — so verify the output carries TaskCompleted when fired as one.
reset
echo dirty >> "$W/force-app/main/default/y.xml"
fire_tc "$M" "sf project deploy start --dry-run --source-dir \"$W/force-app\"" "$SUCCEEDED"
if grep -q '"TaskCompleted"' "$OUT"; then PASS=$((PASS+1)); echo "  PASS note() stamps TaskCompleted, not PostToolUse"
else FAIL=$((FAIL+1)); echo "  FAIL note() should stamp TaskCompleted when fired as TaskCompleted"; fi
git -C "$W" checkout -- force-app >/dev/null 2>&1

echo
printf '%d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
