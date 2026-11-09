#!/bin/bash
# PreToolUse (Bash) — the merge gate. A PR touching force-app/ may not be merged
# until that exact commit has passed a dry-run validate against the org.
#
# Step 4 orders validate BEFORE merge for one reason: once the squash lands on
# main, main claims to describe the org. If the code then fails to deploy, main
# is ahead of the org and the invariant is already broken — the only repairs are
# fix-forward or revert. Validating first makes that state unreachable.
#
# Proof comes from record-validate.sh, which logs the commit SHA of every
# successful `deploy start --dry-run`.
#
# Fails OPEN when GitHub cannot be reached: an offline gh should not stop work,
# and the deploy-side guards still protect the org.
# Escape hatch (deliberate, visible, auditable): ESTATE_ALLOW_UNVALIDATED_MERGE=1.

set -u
HOOK_EVENT="PreToolUse"
. "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

hook_read_input
COMMAND=$(hook_command_text)

echo "$COMMAND" | grep -qE '\bgh[[:space:]]+pr[[:space:]]+merge\b' || exit 0

if [ "${ESTATE_ALLOW_UNVALIDATED_MERGE:-}" = "1" ]; then
  record_hatch ALLOW_UNVALIDATED_MERGE "$COMMAND"
  note "ESCAPE HATCH USED: the validate-before-merge gate was skipped for this merge." \
       "Recorded to .claude/.hatch-log. Say so on the ticket — a merge with no recorded" \
       "dry run is the one case where main can end up ahead of the org unnoticed."
  exit 0
fi

# ── Squash-only ──────────────────────────────────────────────
# One ticket, one commit on main. Merge commits and rebases scatter the issue
# refs that auto-label-deploy.sh and guard-issue-close.sh read.
if ! echo "$COMMAND" | grep -qE -- '(--squash|(^|[[:space:]])-s([[:space:]]|$))'; then
  block \
    "BLOCKED: merge with --squash." \
    "" \
    "  gh pr merge --squash --delete-branch" \
    "" \
    "main carries one commit per ticket. A merge or rebase spreads the '#N' reference" \
    "across commits, and proof-of-deploy is tracked per squashed commit."
fi

command -v gh >/dev/null 2>&1 || exit 0

# ── Which PR? ────────────────────────────────────────────────
PR_ARG=$(echo "$COMMAND" | sed -E 's/.*\bgh[[:space:]]+pr[[:space:]]+merge[[:space:]]*//' \
  | awk '{print $1}' | grep -oE '^[0-9]+$' || true)

PR_JSON=$(gh pr view $PR_ARG --json number,headRefOid,files 2>/dev/null) || exit 0
[ -z "$PR_JSON" ] && exit 0

PR_NUM=$(echo "$PR_JSON" | jq -r '.number // empty')
HEAD_SHA=$(echo "$PR_JSON" | jq -r '.headRefOid // empty')
TOUCHES_FORCE_APP=$(echo "$PR_JSON" | jq -r '[.files[]?.path | select(startswith("force-app/"))] | length')

[ -z "$HEAD_SHA" ] && exit 0
# Nothing deployable in the PR — no org validate is meaningful.
[ "${TOUCHES_FORCE_APP:-0}" = "0" ] && exit 0

VLOG=$(validate_log ".")
if [ -f "$VLOG" ] && grep -q "^${HEAD_SHA}[[:space:]]" "$VLOG"; then
  exit 0
fi

VALIDATED_HINT=""
if [ -f "$VLOG" ]; then
  LAST=$(read_log_reverse "$VLOG" | head -1)
  [ -n "$LAST" ] && VALIDATED_HINT="Most recent recorded validate: $LAST"
fi

block \
  "BLOCKED: PR #${PR_NUM} touches force-app/ but commit ${HEAD_SHA:0:8} has no recorded validate." \
  "" \
  "Run the merge gate from the worktree first:" \
  "  sf project deploy start --dry-run \\" \
  "    --source-dir <each changed file> \\" \
  "    --test-level RunSpecifiedTests --tests <TestClasses>" \
  "" \
  "${VALIDATED_HINT:-No validates have been recorded for this clone yet.}" \
  "" \
  "Validated an earlier commit and then pushed another? Re-validate — the gate is" \
  "per-commit on purpose. Also confirm the branch is pushed: gh reads the remote tip." \
  "" \
  "Genuinely not validatable (org down, etc.)? ESTATE_ALLOW_UNVALIDATED_MERGE=1 gh pr merge ..." \
  "and say so on the ticket."
