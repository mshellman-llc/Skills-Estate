#!/bin/bash
# Regression tests for audit.sh section 1: the trunk ref it trusts, and the org pin.
#
# Two bugs, both of which reported the wrong thing about a correctly configured repo.
#
# 1. trunk_ref — the on-trunk contract check read the LOCAL trunk branch. Worktrees
#    are cut from origin/<trunk> (64-Org's scripts/new-ticket does exactly that), so
#    on a clone whose local branch merely lagged origin, the block was present in
#    every worktree and audit said no CLAUDE.md was committed on trunk. A false alarm
#    costs the same trust as a false clean — people stop reading the output either way.
#
# 2. the org pin — aleysian.orgalias records INTENT, while .sf/config.json is what a
#    deploy actually resolves, and guard-sf-flags.sh hard-blocks --target-org. So that
#    file alone decides where a deploy lands, and a disagreement between the two was
#    invisible to audit. It is also the exact condition that dead-ended a real deploy
#    step with NoDefaultEnvError while every other check reported clean.
#
# The asymmetry in case 5 is the point: a MISSING target-org is mechanical and gets
# fixed, a CONTRADICTING one never is — one of the two values is wrong and this script
# cannot tell which, so repointing it silently would redirect every deploy from here.
#
# Self-contained: builds its own throwaway repos (including a bare "remote"), touches
# nothing else. Uses --no-probe so no network call is made.
#
# Run: bash references/hooks/tests/audit-config-checks.test.sh

set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
AUDIT="$HERE/../../../scripts/audit.sh"
[ -f "$AUDIT" ] || { echo "missing audit.sh: $AUDIT"; exit 1; }
command -v jq >/dev/null 2>&1 || { echo "jq required; skipping"; exit 0; }

TMP=$(mktemp -d "${TMPDIR:-/tmp}/audit cfg.XXXXXX") || exit 1
TMP=$(cd "$TMP" && pwd -P)
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

BARE="$TMP/remote.git"
R="$TMP/clone"
OUT="$TMP/audit.out"
PASS=0; FAIL=0

git init -q --bare -b main "$BARE" >/dev/null 2>&1

# A REAL hash, not a placeholder. With a fake one block_status is MODIFIED, section 6
# reports corruption, and the assertions below can no longer tell "found the block on
# the right ref" from "found a broken block" — which is how the first version of this
# suite passed without pinning anything.
HOOK_NO_GATE=1
# shellcheck source=/dev/null
. "$HERE/../claude-hooks/_block.sh"
BODY="Invariant: this is a test block, long enough to look like one."
HASH=$(printf '%s\n' "$BODY" | block_hash)

mkdir -p "$R" && cd "$R" || exit 1
git init -q -b main . >/dev/null 2>&1
git config user.email t@t.test; git config user.name t
git config aleysian.mode native
git config aleysian.trunk main
git config aleysian.ticket.system none
git remote add origin "$BARE"

# ── the fixture that reproduces the false alarm ──────────────────────────────
#
# The local branch must NOT carry the contract while origin DOES. That is the state
# the bug was found in: the block was committed and pushed, every worktree cut from
# origin/<trunk> had it, and audit — reading the local branch — announced that no
# CLAUDE.md was committed on trunk.
#
# Getting this wrong makes the whole suite vacuous. A fixture where the local branch
# also has the file cannot distinguish the fix from the bug, because neither version
# alarms.
echo "placeholder" > README.md
git add -A >/dev/null 2>&1 && git commit -qm "no contract yet" >/dev/null 2>&1
git push -q -u origin main >/dev/null 2>&1
BASE_SHA=$(git rev-parse HEAD)

printf '# Notes\n\n<!-- BEGIN aleysian-delivery-standards v1.0 hash:%s -->\n%s\n<!-- END aleysian-delivery-standards -->\n' \
  "$HASH" "$BODY" > CLAUDE.md
git add -A >/dev/null 2>&1 && git commit -qm "add the managed block" >/dev/null 2>&1
git push -q origin main >/dev/null 2>&1

# Local main goes back to before the block; origin/main keeps it.
git reset -q --hard "$BASE_SHA" >/dev/null 2>&1

run_audit() { ( cd "$R" && bash "$AUDIT" --no-probe ) > "$OUT" 2>&1; }

# expect <yes|no> <pattern> <label>
expect() {
  local want="$1" pat="$2" label="$3" got=no
  grep -qE "$pat" "$OUT" && got=yes
  if [ "$got" = "$want" ]; then PASS=$((PASS+1)); echo "  PASS $label"
  else FAIL=$((FAIL+1)); echo "  FAIL $label (expected $want, got $got)"; fi
}

echo "== pipeline repos require merge commits =="
touch pipeline.yml
git config aleysian.squash prefer
run_audit
expect yes 'pipeline.yml is present but aleysian.squash=prefer' "pipeline policy mismatch fails"
git config aleysian.squash merge
run_audit
expect no 'pipeline.yml is present but aleysian.squash=' "merge policy satisfies the engine"
rm -f pipeline.yml

echo "== trunk ref: origin is the authority, and local lagging is not a failure =="
run_audit
expect yes 'trunk ref: refs/remotes/origin/main' "resolves to the remote-tracking ref"
expect yes 'present on trunk .refs/remotes/origin/main:CLAUDE.md' "finds the block on the remote ref"
# THE case. The local branch genuinely has no CLAUDE.md; reading it produces a false
# alarm about a contract that is in fact present in every worktree.
expect no  'no CLAUDE.md is committed on trunk' "no false alarm while local lags origin"

echo "== trunk that resolves nowhere is a failure =="
git config aleysian.trunk nonexistent-branch
run_audit
expect yes 'resolves to no branch here' "unresolvable trunk fails"
git config aleysian.trunk main

echo "== the org pin: agreement, absence, contradiction =="
git config aleysian.orgalias RealOrg

run_audit
expect yes 'no .*\.sf/config\.json' "a missing project-local target-org fails"

mkdir -p .sf && printf '{"target-org":"RealOrg"}\n' > .sf/config.json
run_audit
expect yes 'target-org=RealOrg agrees with aleysian.orgalias' "agreement reports ok"

printf '{"target-org":"SomeOtherOrg"}\n' > .sf/config.json
run_audit
expect yes "target-org='SomeOtherOrg' but aleysian.orgalias='RealOrg'" "contradiction fails"

echo "== a contradiction is NEVER auto-fixed, even with --fix =="
( cd "$R" && bash "$AUDIT" --no-probe --fix ) > "$OUT" 2>&1
AFTER=$(jq -r '."target-org"' .sf/config.json)
if [ "$AFTER" = "SomeOtherOrg" ]; then
  PASS=$((PASS+1)); echo "  PASS --fix left the contradicting target-org alone"
else
  FAIL=$((FAIL+1)); echo "  FAIL --fix rewrote target-org to '$AFTER' — it must not guess"
fi

printf '{}\n' > .sf/config.json
run_audit
expect yes 'has no target-org' "an empty target-org fails"

echo "== DevOps Center configuration is coherent as a unit =="
git branch staging "$BASE_SHA"
git config aleysian.delivery devops-center
git config aleysian.trunk staging
git config aleysian.protected main
git config aleysian.squash merge
git config aleysian.ticket.system none
run_audit
expect yes "requires 'staging' in aleysian.protected" "first stage must be protected"
expect yes 'requires aleysian.squash=require' "squash policy is fixed"
expect yes 'requires aleysian.devops.orgalias' "control org alias is required"
expect yes 'requires aleysian.devops.projectid' "project id is required"
expect yes 'requires ticket.system=pattern' "WI ticket mode is required"
expect yes 'has only a provisional landing branch' "pipeline id is required for authoritative topology"

git config aleysian.protected 'staging main'
git config aleysian.squash require
git config aleysian.ticket.system pattern
git config aleysian.ticket.pattern '(^|[^[:alnum:]])WI-[0-9]+([^[:alnum:]]|$)'
git config aleysian.devops.orgalias control64
git config aleysian.devops.projectid 0DB000000000001
git config aleysian.devops.pipelineid 0DB000000000002
run_audit
expect no 'requires aleysian.squash=require' "coherent squash passes"
expect no "requires 'staging' in aleysian.protected" "coherent stage protection passes"
expect no 'requires aleysian.devops.orgalias' "configured control org passes"
expect no 'requires aleysian.devops.projectid' "configured project id passes"
expect no 'has only a provisional landing branch' "configured pipeline id passes"

echo "== shared DevOps Center configuration fails closed =="
git config aleysian.devops.workmodel shared
run_audit
expect yes 'requires aleysian.devops.integrationbranch' "integration branch is required"
expect yes 'requires aleysian.devops.environment' "deployment environment is required"

git config aleysian.devops.integrationbranch stevenc
git config aleysian.devops.environment StevenC
git config aleysian.devops.developmentbranchpattern '^dev/WI-[0-9]+$'
run_audit
expect yes "integration branch 'stevenc' does not resolve" "missing integration branch fails"
expect yes "requires 'stevenc' in aleysian.protected" "integration branch must be protected"

git branch stevenc "$BASE_SHA"
git config aleysian.protected 'staging main stevenc'
run_audit
expect no "integration branch 'stevenc' does not resolve" "configured integration branch passes"
expect no "requires 'stevenc' in aleysian.protected" "protected integration branch passes"

git config aleysian.delivery direct
git config aleysian.trunk main
git config aleysian.ticket.system none
git config aleysian.squash merge
git config --unset aleysian.protected

echo "== native worktrees must carry each selected host contract =="
printf '# Codex contract\n' > AGENTS.md
WT="$TMP/native-ticket"
git worktree add -q --detach "$WT" "$BASE_SHA"
run_audit
expect yes 'native-ticket has NO AGENTS.md' "missing native Codex contract fails"
( cd "$WT" && printf '# Codex contract\n' > AGENTS.md )
run_audit
expect no 'native-ticket has NO AGENTS.md' "present native Codex contract passes"

echo
echo "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
