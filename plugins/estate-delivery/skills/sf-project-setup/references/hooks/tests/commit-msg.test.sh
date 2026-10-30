#!/bin/bash
# Regression tests for githooks/commit-msg — the ticket-reference gate.
#
# This hook is the backstop for commits typed in a terminal, which no Claude Code
# hook can see. It has two jobs on any commit touching force-app/: require a ticket
# reference, and reject anything that would close or transition a ticket at merge
# time.
#
# The case worth naming, because it is a documented trap rather than a bug: the hook
# enforces ONLY on commits that stage force-app/ paths. A chore or docs commit is
# waved through WITHOUT its ticket reference being validated. So a passing chore
# commit is not evidence the gate works — the gate did not run. That has misled at
# least one session into believing the ticket pattern was verified when nothing had
# checked it.
#
# Self-contained: builds its own throwaway repo, touches nothing else.
#
# Run: bash references/hooks/tests/commit-msg.test.sh

set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
HOOK="$HERE/../githooks/commit-msg"
[ -f "$HOOK" ] || { echo "missing hook: $HOOK"; exit 1; }

TMP=$(mktemp -d "${TMPDIR:-/tmp}/commit msg.XXXXXX") || exit 1
TMP=$(cd "$TMP" && pwd -P)
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

R="$TMP/repo"
MSG="$TMP/msg"
OUT="$TMP/out"
mkdir -p "$R/force-app/main/default" "$R/docs" && cd "$R" || exit 1
git init -q -b main . >/dev/null 2>&1
git config user.email t@t.test; git config user.name t
git config estate.mode native
git config estate.trunk main
git config estate.ticket.system jira
git config estate.ticket.project ORG64

PASS=0; FAIL=0

stage_force() { echo "x$RANDOM" > force-app/main/default/f.xml; git add force-app >/dev/null 2>&1; }
stage_docs()  { git reset -q >/dev/null 2>&1; echo "y$RANDOM" > docs/d.md; git add docs >/dev/null 2>&1; }

# run <expect allow|block> <label> <message text>
run() {
  local want="$1" label="$2" got rc
  printf '%s\n' "$3" > "$MSG"
  bash "$HOOK" "$MSG" >"$OUT" 2>&1
  rc=$?
  got=allow; [ $rc -ne 0 ] && got=block
  if [ "$got" = "$want" ]; then
    PASS=$((PASS+1)); echo "  PASS [$got] $label"
  else
    FAIL=$((FAIL+1)); echo "  FAIL expected=$want got=$got :: $label"; sed -n '2,4p' "$OUT"
  fi
}

echo "== force-app commits require the project's ticket key =="
stage_force
run block "no reference at all"          "feat: add the hail matrix"
run allow "bare ORG64 key"               "feat: add the hail matrix (ORG64-42)"
run allow "key in a conventional prefix" "feat(ORG64-42): add the hail matrix"
run block "another project's key"        "feat: add the hail matrix (SFO-42)"
run block "the key without its number"   "feat: add the hail matrix (ORG64-)"

echo "== a ticket key is NOT required off force-app/ — and is NOT validated there =="
stage_docs
run allow "docs commit, no reference"    "docs: rewrite the readme"
# The trap: this looks like the gate passing on a well-formed commit. It is the gate
# not running at all. A chore commit proves nothing about the ticket pattern.
run allow "docs commit, malformed key"   "docs: rewrite the readme (ORG64-)"

echo "== closing keywords are rejected outright =="
stage_force
run block "fixes #42"                    "feat: add the matrix (ORG64-42)

fixes #42"
run block "Closes #7, any case"          "feat: add the matrix (ORG64-42)

Closes #7"
run block "resolved #9"                  "feat: add the matrix (ORG64-42)

resolved #9"

echo "== Jira smart commits are rejected =="
run block "#done"                        "feat: add the matrix ORG64-42 #done"
run block "#comment"                     "feat: add the matrix ORG64-42 #comment looks good"
run block "#time"                        "feat: add the matrix ORG64-42 #time 2h"

echo "== git's commented template lines are not message content =="
# A '#123' inside the commented block git appends must never satisfy or trip anything.
run block "commented text cannot supply the key" "feat: add the matrix
# ORG64-42 is mentioned only in a comment"
run allow "commented closing keyword is inert"   "feat: add the matrix (ORG64-42)
# fixes #42 written in a comment"

echo "== ticket.system=none disables the requirement =="
git config estate.ticket.system none
run allow "no tracker configured"        "feat: add the matrix"
git config estate.ticket.system jira

echo "== DevOps Center requires the current WI branch in the message =="
git commit -qm 'test baseline'
git checkout -qb WI-000001
git config estate.delivery devops-center
git config estate.ticket.system pattern
git config estate.ticket.pattern '(^|[^[:alnum:]])WI-[0-9]+([^[:alnum:]]|$)'
stage_force
run allow "same WI branch and message"    "feat: add the matrix (WI-000001)"
run block "another WI cannot be credited" "feat: add the matrix (WI-000002)"
git branch -m feature/not-a-wi
run block "non-WI branch cannot commit source" "feat: add the matrix (WI-000001)"
git config estate.devops.workmodel shared
git config estate.devops.developmentbranchpattern '^dev/WI-[0-9]+$'
git branch -m dev/WI-000001
run allow "shared development branch references its WI" "feat: add the matrix (WI-000001)"
run block "shared development branch cannot credit another WI" "feat: add the matrix (WI-000002)"
git config estate.delivery direct

echo "== an uninitialised repo is inert =="
git config --unset estate.mode
run allow "no estate.mode set"         "feat: add the matrix"
git config estate.mode native

echo
echo "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
