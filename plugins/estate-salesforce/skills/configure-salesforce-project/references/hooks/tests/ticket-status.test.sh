#!/bin/bash
# Regression tests for the existing-ticket intake helper.

set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
STATUS="$HERE/../bin/estate-ticket-status"
[ -f "$STATUS" ] || { echo "missing helper: $STATUS"; exit 1; }

TMP=$(mktemp -d "${TMPDIR:-/tmp}/ticket status.XXXXXX") || exit 1
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

R="$TMP/repo"
OUT="$TMP/status.out"
PASS=0; FAIL=0
mkdir -p "$R" && cd "$R" || exit 1
git init -q -b sandbox-a .
git config user.email t@t.test
git config user.name t
git config estate.mode native
git config estate.trunk sandbox-a

printf 'base\n' > README.md
git add README.md && git commit -qm 'base'
git checkout -qb feat/EXAMPLE-190
printf 'change\n' >> README.md
git add README.md && git commit -qm 'feat: existing implementation (EXAMPLE-190)'
FEATURE=$(git rev-parse HEAD)
mkdir -p .git/estate
printf '%s feat/EXAMPLE-190 2026-08-25T00:00:00Z\n' "$FEATURE" > .git/estate/validate-log
git checkout -q sandbox-a
git merge -q --no-ff feat/EXAMPLE-190 -m 'Merge EXAMPLE-190'
LANDED=$(git rev-parse HEAD)
printf '%s 0Afake 2026-08-25T00:01:00Z\n' "$LANDED" > .git/estate/deploy-log

run_status() { bash "$STATUS" EXAMPLE-190 > "$OUT" 2>&1; }
expect() {
  local want="$1" pattern="$2" label="$3" got=no
  grep -qE "$pattern" "$OUT" && got=yes
  if [ "$got" = "$want" ]; then PASS=$((PASS+1)); echo "  PASS $label"
  else
    FAIL=$((FAIL+1)); echo "  FAIL $label (expected $want, got $got)"
    sed 's/^/    | /' "$OUT"
  fi
}

echo "== landed ticket with local receipts =="
run_status
expect yes '^state[[:space:]]+delivered \(local ancestry evidence\)' "reports delivered from ancestry"
expect yes '^validated[[:space:]]+historical ' "does not apply an old receipt to the newer merge commit"
expect yes '^deployed[[:space:]]+yes ' "finds the trunk deployment receipt"
expect yes '^landed[[:space:]]+' "reports the landed trunk commit"

echo "== cleanup can remove the validated feature ref =="
git branch -D feat/EXAMPLE-190 >/dev/null
run_status
expect yes '^validated[[:space:]]+historical ' "keeps the old receipt explicitly historical"

echo "== ticket identifiers match as complete tokens =="
bash "$STATUS" EXAMPLE-19 > "$OUT" 2>&1
expect yes '^state[[:space:]]+not found in local Git evidence' "does not confuse EXAMPLE-19 with EXAMPLE-190"
expect no 'EXAMPLE-190' "does not leak the longer ticket into results"

echo "== absent clone-local receipts stay unknown =="
rm -f .git/estate/validate-log .git/estate/deploy-log
run_status
expect yes '^state[[:space:]]+landed; deployment unknown in this clone' "does not claim undeployed"
expect yes '^validated[[:space:]]+unknown ' "does not claim unvalidated"
expect yes '^deployed[[:space:]]+unknown ' "does not claim undeployed"
expect no 'not validated|not deployed' "avoids false negative status language"

echo
echo "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
