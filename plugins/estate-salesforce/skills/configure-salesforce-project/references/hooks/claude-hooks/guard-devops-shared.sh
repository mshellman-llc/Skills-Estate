#!/bin/bash
# PreToolUse (Bash) - guard the shared development-org branch boundary.
#
# GitHub's successful Deployment record is the cross-clone receipt. Any action
# that starts or rebases development work, or validates it against the shared
# org, stops when that receipt differs from origin/<integration branch>.

set -u
HOOK_EVENT="PreToolUse"
HOOK_DEFER_GATE=1
. "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

hook_read_input
is_devops_shared || exit 0
COMMAND=$(hook_command_text)
INTEGRATION=$(devops_integration_branch)
DEV_PATTERN=$(devops_development_branch_pattern)
BRANCH=$(current_branch ".")
STATUS_BIN="$(cd "$(dirname "${BASH_SOURCE[0]}")/../bin" 2>/dev/null && pwd)/estate-devops-shared-status"

require_synced_receipt() {
  local verdict rc
  verdict=$("$STATUS_BIN" 2>&1); rc=$?
  [ "$rc" -eq 0 ] && return 0
  block \
    "BLOCKED: the shared development branch is not proven deployed." \
    "" \
    "$verdict" \
    "" \
    "origin/$INTEGRATION must equal the latest successful GitHub Deployment" \
    "receipt for '$(devops_environment)'. A mismatch can mean queued, failed, stale," \
    "or bypassed delivery. The centralized landing coordinator must repair it before" \
    "another WI branches, rebases, merges, or validates against the shared org."
}

# New development branches are cut from the deployed integration ref, never from
# the DevOps-generated packaging branch and never from a stale local branch.
if echo "$COMMAND" | grep -qE "${SFDS_CMDPOS}git[[:space:]]+worktree[[:space:]]+add\b" \
   && echo "$COMMAND" | grep -qE -- "-b[[:space:]]+dev/WI-[0-9]+"; then
  echo "$COMMAND" | grep -qE "origin/${INTEGRATION}([[:space:]]|$)" || block \
    "BLOCKED: shared-sandbox development worktrees must start at origin/$INTEGRATION." \
    "" \
    "Use: git worktree add <path> -b dev/WI-###### origin/$INTEGRATION"
  require_synced_receipt
  exit 0
fi

if echo "$COMMAND" | grep -qE "${SFDS_CMDPOS}git[[:space:]]+(switch[[:space:]]+-c|checkout[[:space:]]+-b)[[:space:]]+dev/WI-[0-9]+"; then
  echo "$COMMAND" | grep -qE "origin/${INTEGRATION}([[:space:]]|$)" || block \
    "BLOCKED: shared-sandbox development branches must start at origin/$INTEGRATION." \
    "" \
    "Name the base explicitly so the branch cannot inherit a stale checkout."
  require_synced_receipt
  exit 0
fi

# A packaging branch may receive the recorded WI patch, never the accumulated
# integration branch. This check is intentionally narrow: cherry-picking a named
# commit can be legitimate for non-source files, while merging the whole branch is
# the specific smuggling path the topology forbids.
if printf '%s\n' "$BRANCH" | grep -qE "$(devops_branch_pattern)" \
   && echo "$COMMAND" | grep -qE "${SFDS_CMDPOS}git[[:space:]]+([^|;&]*[[:space:]])?merge\b" \
   && echo "$COMMAND" | grep -qE "(^|[[:space:]])(origin/)?${INTEGRATION}([[:space:]]|$)"; then
  block \
    "BLOCKED: do not merge '$INTEGRATION' into the DevOps Center packaging branch." \
    "" \
    "That branch contains other accepted but unpromoted WIs. Use" \
    "estate-devops-package to apply and verify only this WI's recorded patch."
fi

if printf '%s\n' "$BRANCH" | grep -qE "$DEV_PATTERN"; then
  if echo "$COMMAND" | grep -qE "${SFDS_CMDPOS}git[[:space:]]+([^|;&]*[[:space:]])?(rebase|merge)\b" \
     || echo "$COMMAND" | grep -qE '\bsf[[:space:]]+project[[:space:]]+deploy[[:space:]]+start\b'; then
    require_synced_receipt
  fi
fi

exit 0
