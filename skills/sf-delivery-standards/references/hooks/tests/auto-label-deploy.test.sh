#!/bin/bash
# Regression tests for claude-hooks/auto-label-deploy.sh — the recorder that writes
# the proof-of-deploy the MERGE gate reads and the DoD nag checks against.
#
# THIS IS NOT A BLOCKER, SO THE EXIT CODE PROVES NOTHING. Every path exits 0: the
# recording path, the paths that deliberately record nothing, and the failure modes
# where it records nothing by accident. Both directions matter and they are opposite
# bugs — a missing entry disables the merge gate, an invented entry opens it for a
# deploy that never happened. So every case asserts the SIDE EFFECT:
# .git/aleysian/deploy-log and pending-jobs.
#
# THE HOOK DOES NOT TOUCH THE TRACKER. A hook cannot reach the session's MCP, and it
# deliberately does not shell out to a tracker CLI either. Recording the deploy ON the
# ticket is a COMMENT the AGENT posts (Jira: the Rovo MCP addCommentToJiraIssue;
# GitHub: gh issue comment). So the tracker cases here assert the NOTE that delegates
# that to the agent, and assert the hook issues NO tracker call of its own. It never
# labels, transitions, or closes a ticket — closure is out of this loop's scope.
#
# What this pins down, each learned the hard way:
#
#   the master gate    every hook exits 0 in a repo with no `aleysian.mode`. The
#                      fixture sets it, and one case unsets it again — without that
#                      the whole suite can be green against a hook that never ran.
#
#   the org decides    "Status: Succeeded" cannot distinguish a real deploy from a
#                      validation, and that distinction IS the proof-of-deploy gate.
#                      sf_deploy_verdict() asks the org via `deploy report --job-id`.
#                      Cases below contradict the console text and assert the org wins.
#
#   trunk only         a deploy from a non-trunk branch is not proof of the
#                      invariant, and must record NOTHING — not the log, not a
#                      pending job.
#
#   UNKNOWN != FAILED  an --async deploy still in flight must be remembered as
#                      pending, not recorded and not reported as a failure. Calling
#                      it FAILED tells the agent to revert a deploy that is working.
#
#   recording is       the deploy-log entry is what the merge gate reads. It lands
#   independent of     before, and regardless of, anything to do with the tracker.
#   the tracker
#
# `sf` is stubbed on PATH rather than mocked inside the hook, so the hook's own
# argument handling is under test. THE sf STUB REQUIRES --job-id AND FAILS WITHOUT IT:
# a stub that answers regardless of its arguments hid a real bug in this repo for
# months (see the gh stub in guard-pr-merge.test.sh). One case reads the stub's
# invocation log back to prove the id was passed. A `gh` stub is present only to prove
# the hook NEVER calls it.
#
# Self-contained: builds its own throwaway repo, touches nothing else.
#
# Run: bash references/hooks/tests/auto-label-deploy.test.sh

set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
HOOK="$HERE/../claude-hooks/auto-label-deploy.sh"
[ -f "$HOOK" ] || { echo "missing hook: $HOOK"; exit 1; }

command -v python3 >/dev/null 2>&1 || { echo "python3 required; skipping"; exit 0; }
command -v jq      >/dev/null 2>&1 || { echo "jq required by the hook; skipping"; exit 0; }

TMP=$(mktemp -d "${TMPDIR:-/tmp}/auto label deploy.XXXXXX") || exit 1
TMP=$(cd "$TMP" && pwd -P)
R="$TMP/main repo"
BIN="$TMP/bin"
OUT="$TMP/hook.out"
SF_LOG="$TMP/sf.invocations"
GH_LOG="$TMP/gh.invocations"

cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

mkdir -p "$R" "$BIN" && cd "$R" || exit 1
git init -q -b main . >/dev/null 2>&1
git config user.email t@t.test; git config user.name t
# Without this every hook exits 0 at source time and nothing below is under test.
git config aleysian.mode native
git config aleysian.trunk main
git config aleysian.host github
git config aleysian.ticket.system github
# The bulk of this suite is about RECORDING, so writes are suppressed by policy —
# recording happens before the tracker is touched. The tracker section flips this.
git config aleysian.ticket.remote client
mkdir -p force-app/main/default && echo x > force-app/main/default/x.xml
mkdir -p docs && printf 'nothing\n' > docs/runbook.md
git add -A >/dev/null 2>&1 && git commit -qm "init refs #7" >/dev/null 2>&1

DLOG="$R/.git/aleysian/deploy-log"
PLOG="$R/.git/aleysian/pending-jobs"

# ── sf stub ──────────────────────────────────────────────────
# The one shape the hook issues: `sf project deploy report --job-id <ID> --json`.
# It REQUIRES the id. Real `sf` would need --use-most-recent instead, which in a
# shared org resolves to somebody else's deploy — there is no safe answer to "no
# id", so the stub refuses rather than guessing. That refusal is what makes the
# "the id reaches the org" case meaningful: stop passing it and the verdict quietly
# degrades to parsing console text, which cannot tell a deploy from a validation.
cat > "$BIN/sf" <<'STUB'
#!/bin/bash
printf '%s\n' "$*" >> "${SF_LOG:-/dev/null}"
[ "${1:-}" = "project" ] && [ "${2:-}" = "deploy" ] && [ "${3:-}" = "report" ] || exit 1
ID=""; PREV=""
for A in "$@"; do [ "$PREV" = "--job-id" ] && ID="$A"; PREV="$A"; done
[ -z "$ID" ] && { echo "Error: --job-id or --use-most-recent is required" >&2; exit 1; }
[ "${STUB_UNRESOLVED:-0}" = "1" ] && { echo '{"status":1,"message":"job not found"}'; exit 1; }
printf '{"status":0,"result":{"id":"%s","status":"%s","checkOnly":%s}}\n' \
  "$ID" "${STUB_STATUS:-Succeeded}" "${STUB_CHECKONLY:-false}"
STUB

# ── gh stub ──────────────────────────────────────────────────
# Reads always answer; WRITES fail when GH_WRITE_FAIL=1, which is what an expired
# browser OAuth session looks like — binary present, every call refused.
cat > "$BIN/gh" <<'STUB'
#!/bin/bash
printf '%s\n' "$*" >> "${GH_LOG:-/dev/null}"
if [ "${1:-}" = "issue" ] && [ "${2:-}" = "view" ]; then
  for A in "$@"; do
    [ "$A" = "state" ] && { printf '%s\n' "${GH_STATE:-OPEN}"; exit 0; }
    [ "$A" = "labels" ] && { printf '%s\n' "${GH_LABELS:-}"; exit 0; }
  done
  exit 0
fi
case "${2:-}" in
  edit|comment) [ "${GH_WRITE_FAIL:-0}" = "1" ] && exit 1; exit 0 ;;
esac
exit 0
STUB
chmod +x "$BIN/sf" "$BIN/gh"
PATH="$BIN:$PATH"; export PATH
export SF_LOG GH_LOG
STUB_STATUS=Succeeded; STUB_CHECKONLY=false; STUB_UNRESOLVED=0
GH_WRITE_FAIL=0; GH_LABELS=""; GH_STATE=OPEN
export STUB_STATUS STUB_CHECKONLY STUB_UNRESOLVED GH_WRITE_FAIL GH_LABELS GH_STATE

J1=0AfAA000000001AAA
UNKNOWN_JOB=0AfZZ000000009ZZZ

# ── harness ──────────────────────────────────────────────────

PASS=0; FAIL=0
check() { # <label> <expected> <actual>
  if [ "$2" = "$3" ]; then PASS=$((PASS+1)); echo "  PASS $2 :: $1"
  else FAIL=$((FAIL+1)); echo "  FAIL $1"; echo "       expected [$2]"; echo "       got      [$3]"; fi
}
# Plain ASCII substrings only: grep -E is byte-oriented and the hook's notes carry
# em dashes, which no '.' will match.
says()    { if grep -q "$2" "$OUT"; then PASS=$((PASS+1)); echo "  PASS says '$2' :: $1"
            else FAIL=$((FAIL+1)); echo "  FAIL $1 — output does not say '$2'"; sed -n '1,3p' "$OUT"; fi; }
says_not(){ if grep -q "$2" "$OUT"; then FAIL=$((FAIL+1)); echo "  FAIL $1 — output wrongly says '$2'"
            else PASS=$((PASS+1)); echo "  PASS never says '$2' :: $1"; fi; }

dlog() { [ -f "$DLOG" ] || { printf 'ABSENT'; return; }
         awk 'NF{printf "%s/%s;", substr($1,1,8), $2}' "$DLOG"; }
pend() { [ -f "$PLOG" ] || { printf 'ABSENT'; return; }
         awk 'NF{printf "%s/%s/%s;", $1, substr($2,1,8), $3}' "$PLOG"; }
ghlog(){ [ -s "$GH_LOG" ] || { printf 'NONE'; return; }
         awk 'NF{printf "%s;", $0}' "$GH_LOG"; }
s8()   { printf '%s' "${1:0:8}"; }
head_sha() { git -C "$R" rev-parse HEAD; }

reset() { rm -f "$DLOG" "$PLOG"; : > "$SF_LOG"; : > "$GH_LOG"; }

RC=0
fire() { # <command text> <tool stdout>
  ( cd "$R" && python3 -c 'import json,sys
print(json.dumps({"tool_name":"Bash",
                  "tool_input":{"command":sys.argv[1]},
                  "tool_response":{"stdout":sys.argv[2],"stderr":""}}))' "$1" "$2" \
    | bash "$HOOK" ) >"$OUT" 2>&1
  RC=$?
}

DEPLOY_CMD="sf project deploy start --source-dir force-app --json"
SUCCEEDED='Deploy ID: '"$J1"'
Status: Succeeded'

echo "== the master gate: no aleysian.mode means no recording at all =="
reset
git config --unset aleysian.mode
fire "$DEPLOY_CMD" "$SUCCEEDED"
check "unconfigured repo records nothing" "ABSENT" "$(dlog)"
git config aleysian.mode native
fire "$DEPLOY_CMD" "$SUCCEEDED"
check "the same input records once mode is set" "$(s8 "$(head_sha)")/$J1;" "$(dlog)"

echo
echo "== the ORG decides deploy vs validation, not the console text =="
reset
STUB_CHECKONLY=true
fire "$DEPLOY_CMD" "$SUCCEEDED"
check "org says check-only -> record-validate.sh owns it, nothing recorded here" \
      "ABSENT" "$(dlog)"
STUB_CHECKONLY=false

reset
fire "sf project deploy start --dry-run --source-dir force-app" "$SUCCEEDED"
check "an explicit --dry-run is not this hook's business" "ABSENT" "$(dlog)"

reset
STUB_STATUS=Failed
echo "$J1 $(head_sha) deploy" > "$PLOG"
fire "$DEPLOY_CMD" "Deploy ID: $J1
Status: Failed"
check "a FAILED deploy records nothing" "ABSENT" "$(dlog)"
check "...and stops being pending" "" "$(pend)"
says "the agent is told to fix forward or revert" "Deploy FAILED"
STUB_STATUS=Succeeded

echo
echo "== the job id must actually reach the org =="
reset
fire "$DEPLOY_CMD" "$SUCCEEDED"
check "the org was asked about this exact job" \
      "project deploy report --job-id $J1 --json" "$(head -1 "$SF_LOG")"

echo
echo "== UNKNOWN is not FAILED: an --async deploy in flight is remembered =="
reset
STUB_STATUS=InProgress
fire "sf project deploy start --source-dir force-app --async" "Deploy ID: $J1"
check "in flight: nothing recorded as proof-of-deploy" "ABSENT" "$(dlog)"
check "in flight: remembered as a pending DEPLOY" "$J1/$(s8 "$(head_sha)")/deploy;" "$(pend)"
says     "the agent is told how to collect the result" "deploy report --job-id $J1"
says_not "in flight is not reported as a failure"      "FAILED"
STUB_STATUS=Succeeded

echo "== ...and the eventual report credits the commit that was SENT =="
SENT_SHA=$(head_sha)
echo moved >> "$R/force-app/main/default/x.xml"
( cd "$R" && git commit -qam "moved on refs #7" >/dev/null 2>&1 )
# Deliberately collected from a non-trunk branch: the pending record exists because
# we watched a start on trunk, so where the shell sits now is irrelevant provenance.
( cd "$R" && git checkout -qb collect/elsewhere >/dev/null 2>&1 )
fire "sf project deploy report --job-id $J1" "Status: Succeeded"
check "the report credits the PENDING sha, not the new HEAD" "$(s8 "$SENT_SHA")/$J1;" "$(dlog)"
check "the pending entry is cleared" "" "$(pend)"
( cd "$R" && git checkout -q main >/dev/null 2>&1 )

echo
echo "== only a deploy from trunk is proof of the invariant =="
reset
( cd "$R" && git checkout -qb feature/y >/dev/null 2>&1 )
fire "$DEPLOY_CMD" "$SUCCEEDED"
check "a deploy from a non-trunk branch records NOTHING" "ABSENT" "$(dlog)"
check "...and no pending job either" "ABSENT" "$(pend)"
check "...and the tracker is not touched" "NONE" "$(ghlog)"
says "the agent is told the invariant may be broken" "NOT recorded as proof-of-deploy"

reset
STUB_STATUS=InProgress
fire "sf project deploy start --source-dir force-app --async" "Deploy ID: $J1"
check "an async deploy from a non-trunk branch is not even remembered" "ABSENT" "$(pend)"
STUB_STATUS=Succeeded
( cd "$R" && git checkout -q main >/dev/null 2>&1 )

echo
echo "== a report is only a result if we watched the start =="
reset
fire "sf project deploy report --job-id $UNKNOWN_JOB" "Status: Succeeded"
check "a report on a job we never started records nothing" "ABSENT" "$(dlog)"

reset
echo "$J1 $(head_sha) validate" > "$PLOG"
fire "sf project deploy report --job-id $J1" "Status: Succeeded"
check "a pending VALIDATE is not a deploy" "ABSENT" "$(dlog)"
check "...and its pending entry is left for record-validate.sh" \
      "$J1/$(s8 "$(head_sha)")/validate;" "$(pend)"

echo
echo "== idempotency: one deploy-log entry per sha =="
git config aleysian.ticket.remote ours
reset
fire "$DEPLOY_CMD" "$SUCCEEDED"
check "recorded once" "$(s8 "$(head_sha)")/$J1;" "$(dlog)"
says "the agent is asked to record it on the ticket" "Record it on the ticket"
fire "$DEPLOY_CMD" "$SUCCEEDED"
check "re-reporting the same deploy adds no second entry" "$(s8 "$(head_sha)")/$J1;" "$(dlog)"

echo
echo "== the tracker write is the AGENT's job, delegated in a note — the hook issues none =="
# The hook cannot reach the session's MCP, so it does not write to the tracker. It
# names the comment tool for the project's tracker and asks the agent to post it.
reset
fire "$DEPLOY_CMD" "$SUCCEEDED"
check "the hook issues NO tracker call of its own" "NONE" "$(ghlog)"
says     "it delegates the comment (GitHub tracker -> gh issue comment)" "gh issue comment"
says     "as a COMMENT, explicitly not a transition/closure"             "not a transition or closure"
says     "and says the ticket stays open"                                "Leave the ticket OPEN"
says_not "it never speaks of closing the ticket in this loop"            "then close"

echo "== a Jira project is told to comment via the Rovo MCP, never a CLI =="
# req 14 case: the pre-change hook shelled out to `acli jira workitem …` here; the
# loop's only ticket write is now an agent MCP comment. (The pre-change hook, given
# this same input, said "writing to the tracker FAILED" instead — demonstrated
# out-of-band during development.) Needs a commit that carries a Jira key, since
# issue_refs() matches SFO-N under a Jira tracker, not the fixture's "refs #7".
git config aleysian.ticket.system jira
git config aleysian.ticket.project SFO
( cd "$R" && echo j >> force-app/main/default/x.xml \
  && git commit -qam "SFO-42 wire it up" >/dev/null 2>&1 )
reset
fire "$DEPLOY_CMD" "$SUCCEEDED"
says     "the note names the Rovo MCP comment tool"  "addCommentToJiraIssue"
says     "as a COMMENT, not a transition/closure"    "not a transition or closure"
check    "still no tracker call from the hook"       "NONE" "$(ghlog)"
git config aleysian.ticket.system github
git config --unset aleysian.ticket.project

echo "== ticket.remote=client: the hook writes nothing and says so =="
# Needs a GitHub-ref commit: the client-policy note only fires when a ticket is
# referenced (the prior Jira case left HEAD on an SFO-key commit).
( cd "$R" && echo c >> force-app/main/default/x.xml \
  && git commit -qam "client policy refs #7" >/dev/null 2>&1 )
reset
git config aleysian.ticket.remote client
fire "$DEPLOY_CMD" "$SUCCEEDED"
check "recorded" "$(s8 "$(head_sha)")/$J1;" "$(dlog)"
check "nothing written to the client's tracker" "NONE" "$(ghlog)"
says "and it flags the client-tracker policy" "the CLIENT's"
git config aleysian.ticket.remote ours

echo "== a commit with no ticket ref =="
reset
( cd "$R" && echo untracked > force-app/main/default/z.xml \
  && git add -A >/dev/null 2>&1 && git commit -qm "chore: tidy up, no ticket" >/dev/null 2>&1 )
fire "$DEPLOY_CMD" "$SUCCEEDED"
check "still recorded" "$(s8 "$(head_sha)")/$J1;" "$(dlog)"
check "no ticket to annotate" "NONE" "$(ghlog)"
says "it says there is no ticket to associate" "no ticket is associated"

echo
echo "== commands that are not this hook's business =="
reset
fire "sf org list --json" "$SUCCEEDED"
check "sf org list" "ABSENT" "$(dlog)"
fire "git push origin main" "Everything up-to-date"
check "git push" "ABSENT" "$(dlog)"
fire "sf project deploy start --source-dir force-app" "Deploying... 12/40"
check "no verdict to be had -> nothing recorded" "ABSENT" "$(dlog)"

echo
echo "== a command that only MENTIONS a deploy must not record one =="
# LAYER 1 of the phantom-record fix: the trigger is anchored to a COMMAND POSITION
# (SFDS_DEPLOY_RE / SFDS_CMDPOS in _lib.sh), the same anchor record-escape-hatch.sh
# has always used. Unanchored, searching the docs for the documented deploy command —
# ordinary work — wrote a PROOF-OF-DEPLOY entry whenever the doc quoted a sample
# transcript containing 'Status: Succeeded'. That does not disable a gate, it forges
# the proof-of-deploy the merge gate reads, and the forged entry is indistinguishable
# from a real one afterwards.
reset
STUB_UNRESOLVED=1     # prose carries no job id the org could resolve
fire 'grep -rn "sf project deploy start" docs/' \
  'docs/runbook.md:12:  sf project deploy start --source-dir force-app
docs/runbook.md:13:  Status: Succeeded'
check "grepping the docs for the command records nothing" "ABSENT" "$(dlog)"

reset
fire 'echo "then sf project deploy start --source-dir force-app" >> docs/runbook.md' \
  'then sf project deploy start --source-dir force-app
Status: Succeeded'
check "echoing the command into a doc records nothing" "ABSENT" "$(dlog)"

reset
fire 'git commit -m "docs: sf project deploy start is the last step refs #7"' \
  '[main 1234567] docs
 Status: Succeeded'
check "a commit message quoting the command records nothing" "ABSENT" "$(dlog)"
STUB_UNRESOLVED=0

echo "== layer 2: a success the org did not confirm is UNKNOWN, not a deploy =="
# "Status: Succeeded" is a string, and this whole gate rests on a distinction a string
# cannot make. With no job id there is nothing to ask the org about, so the verdict is
# UNKNOWN — which downstream means "remembered, not recorded, and not a failure".
reset
STUB_UNRESOLVED=1
fire "$DEPLOY_CMD" "Status: Succeeded"
check "no job id anywhere -> nothing recorded" "ABSENT" "$(dlog)"
says     "the agent is told how to collect the real result" "deploy report --job-id"
says_not "and it is not called a failure"                   "FAILED"
STUB_UNRESOLVED=0

echo "== ...and a REAL deploy still records, in every ordinary shape =="
# The risk of layer 2 is over-correcting into silence. A genuine `deploy start` emits
# its 0Af id, which is what keeps these recording.
reset
fire "$DEPLOY_CMD" "$SUCCEEDED"
check "job id in the OUTPUT only, org confirms" "$(s8 "$(head_sha)")/$J1;" "$(dlog)"
reset
echo "$J1 $(head_sha) deploy" > "$PLOG"
fire "sf project deploy resume --job-id $J1" "Status: Succeeded"
check "job id in the COMMAND, matched to a start we watched" "$(s8 "$(head_sha)")/$J1;" "$(dlog)"
reset
fire "git pull --quiet && sf project deploy start --source-dir force-app --json" "$SUCCEEDED"
check "after a && separator" "$(s8 "$(head_sha)")/$J1;" "$(dlog)"
reset
fire "SF_USE_PROGRESS_BAR=false sf project deploy start --source-dir force-app" "$SUCCEEDED"
check "behind an env assignment" "$(s8 "$(head_sha)")/$J1;" "$(dlog)"

echo
echo "== FORGE 1: a foreign job id echoed after a failed start cannot credit HEAD =="
# The org confirms ANY real Succeeded non-checkOnly id, so a start whose real deploy
# fails (stderr suppressed) followed by `echo "Deploy 0Af<foreign>"` gets the foreign
# id confirmed and HEAD credited — forging the proof the CLOSE gate reads. The fix
# requires THIS command's own output to show a successful deploy, which the forge's
# output (only the echoed id) does not. Before the fix this recorded HEAD/foreign.
FOREIGN=0AfFF000000006FFF
reset
fire "sf project deploy start --source-dir force-app 2>/dev/null; echo \"Deploy $FOREIGN\"" \
  "Deploy $FOREIGN"
check "an echoed foreign id with no self-reported success records nothing" "ABSENT" "$(dlog)"
check "...and it is not left as a pending deploy either" "ABSENT" "$(pend)"
says "the agent is told nothing was recorded" "NOTHING was recorded as proof-of-deploy"

# Same forge with --json: the real envelope reports Failed, the foreign id is echoed
# after it. JSON is authoritative when present, so the echo cannot rescue it.
reset
fire "sf project deploy start --json --source-dir force-app 2>/dev/null; echo \"Deploy $FOREIGN\"" \
  '{"status":1,"result":{"status":"Failed"}}
Deploy '"$FOREIGN"
check "a foreign id echoed after a Failed --json envelope records nothing" "ABSENT" "$(dlog)"

# Positive control: the fix must not silence a genuine deploy that DOES self-report
# success, even if some other 0Af happens to appear later in the output. sf prints its
# own id first, so head -1 still credits the real one.
reset
fire "$DEPLOY_CMD" "$SUCCEEDED
(later log line mentioning $FOREIGN)"
check "a real deploy that self-reports success still records" "$(s8 "$(head_sha)")/$J1;" "$(dlog)"

echo
printf '%d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
