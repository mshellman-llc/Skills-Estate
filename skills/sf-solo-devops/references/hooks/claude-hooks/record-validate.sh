#!/bin/bash
# PostToolUse (Bash) — record every SUCCESSFUL dry-run validate.
#
# Writes "<sha> <branch> <utc timestamp>" to .claude/.validate-log in the MAIN
# clone, where guard-pr-merge.sh reads it.
#
# Only genuine successes are recorded, and check-only status is decided by the
# structured JSON result, never a status string — see sf_deploy_verdict().
#
# Fires on `deploy report` / `deploy resume` too, so an --async dry run that
# finishes after the command returns is still recorded.
#
# Never blocks. A recording failure costs a re-validate, nothing more.

set -u
HOOK_EVENT="PostToolUse"
. "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

hook_read_input
COMMAND=$(hook_command_text)
TARGET_KEY=$(sf_target_key "$COMMAND")
[ -n "$TARGET_KEY" ] || exit 0

echo "$COMMAND" | grep -qE '\b(sf|sfdx)\b.*\bdeploy[[:space:]]+(start|validate|report|resume)\b' || exit 0

IS_START=0
echo "$COMMAND" | grep -qE '\bdeploy[[:space:]]+(start|validate)\b' && IS_START=1

# A non-dry-run `deploy start` is a real deploy; auto-label-deploy.sh owns it.
if [ "$IS_START" = "1" ] && ! echo "$COMMAND" | grep -qE -- '--dry-run|deploy[[:space:]]+validate'; then
  exit 0
fi

# Record the SHA of the tree whose FILES were validated, which is not
# necessarily the tree this hook is standing in — see source_tree_root().
SRC_ROOT=$(source_tree_root "$COMMAND") || exit 0
SHA=$(git -C "$SRC_ROOT" rev-parse HEAD 2>/dev/null) || exit 0
[ -z "$SHA" ] && exit 0
if [ "$IS_START" = "1" ] && [ -n "$(git -C "$SRC_ROOT" status --porcelain 2>/dev/null)" ]; then
  note "Validation was not credited to a commit: source metadata has uncommitted changes."
  exit 0
fi

# A report only counts as OUR validate if we watched the matching start. Reading
# an unrelated job id here would record the current HEAD as validated and unlock
# a merge gate for a commit nothing was ever run against. See pending_add().
if [ "$IS_START" = "0" ]; then
  RJOB=$(sf_job_id "$COMMAND")
  [ -z "$RJOB" ] && exit 0
  PEND=$(pending_lookup "$RJOB" "$TARGET_KEY") || exit 0
  [ -z "$PEND" ] && exit 0
  [ "${PEND##* }" = "validate" ] || exit 0
  SHA=${PEND%% *}
fi

VERDICT=$(sf_deploy_verdict "$(hook_tool_stdout)" "$COMMAND")
JOB=$(sf_job_id "$COMMAND"); [ -z "$JOB" ] && JOB=$(sf_job_id "$(hook_tool_stdout)")

if [ "$VERDICT" != "VALIDATE" ]; then
  # In flight: remember it, so the eventual report is recognised as ours.
  if [ "$VERDICT" = "UNKNOWN" ] && [ "$IS_START" = "1" ]; then
    ASYNC_JOB=$(sf_pending_job "$(hook_tool_stdout)" "$COMMAND")
    [ -n "$ASYNC_JOB" ] && pending_add "$ASYNC_JOB" "$SHA" validate "$TARGET_KEY"
  fi
  [ "$VERDICT" = "FAILED" ] && [ -n "$JOB" ] && pending_remove "$JOB"
  exit 0
fi

[ -n "$JOB" ] && pending_remove "$JOB"
BRANCH=$(current_branch "$SRC_ROOT")
STAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

VLOG=$(validate_log ".")
mkdir -p "$(dirname "$VLOG")" 2>/dev/null

grep -q "^${SHA}[[:space:]]" "$VLOG" 2>/dev/null || \
  echo "$SHA ${BRANCH:-unknown} $STAMP" >> "$VLOG"

exit 0
