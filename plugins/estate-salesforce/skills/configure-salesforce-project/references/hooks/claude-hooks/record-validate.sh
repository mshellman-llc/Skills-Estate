#!/bin/bash
# PostToolUse / TaskCompleted (Bash) — record every SUCCESSFUL dry-run validate.
#
# Writes "<sha> <branch> <utc timestamp>" to the state dir's validate-log, where
# guard-pr-merge.sh (and estate-merge, and guard-push.sh) read it. The state dir
# is inside .git/, common to every worktree — so a worktree's dry run is visible
# to the orchestrator standing on trunk. That is the whole point of putting it there.
#
# Only genuine successes are recorded, and check-only status is decided by the
# ORG rather than the console text — see sf_deploy_verdict().
#
# Fires on `deploy report` / `deploy resume` too, so an --async dry run that
# finishes after the command returns is still recorded.
#
# Registered under BOTH PostToolUse and TaskCompleted. The harness auto-backgrounds
# Bash commands that exceed its timeout; when that happens, PostToolUse fires with
# an incomplete result (the command is still running), so the validate cannot be
# recorded. TaskCompleted fires when the backgrounded command actually finishes,
# carrying the real output — so the recording happens then instead.
#
# Never blocks. A recording failure costs a re-validate, nothing more.

set -u
HOOK_EVENT="PostToolUse"
HOOK_DEFER_GATE=1   # the master gate fires in hook_read_input, once the target repo is known
. "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

hook_read_input
# Derive the actual event from the JSON input so the same script works under both
# PostToolUse and TaskCompleted without a wrapper. note() uses HOOK_EVENT to route
# its message through the correct hookEventName channel.
_ev=$(hook_field '.hook_event_name')
[ -n "$_ev" ] && HOOK_EVENT="$_ev"
COMMAND=$(hook_command_text)

# Anchored to a COMMAND POSITION — see SFDS_DEPLOY_RE / SFDS_CMDPOS in _lib.sh.
# Unanchored, `grep -rn "sf project deploy start --dry-run" docs/` counted as a dry
# run, and if the doc it found quoted a sample transcript the grep OUTPUT carried
# "Status: Succeeded" — recording HEAD as validated and unlocking the merge gate for
# a commit nothing was ever run against. Prose is not a command.
echo "$COMMAND" | grep -qE "${SFDS_DEPLOY_RE}(start|report|resume)\b" || exit 0

IS_START=0
echo "$COMMAND" | grep -qE "${SFDS_DEPLOY_RE}start\b" && IS_START=1

# A non-dry-run `deploy start` is a real deploy; auto-label-deploy.sh owns it.
if [ "$IS_START" = "1" ] && ! echo "$COMMAND" | grep -qE -- '--dry-run'; then
  exit 0
fi

# Record the SHA of the tree whose FILES were validated, which is not
# necessarily the tree this hook is standing in — see source_tree_root().
SRC_ROOT=$(source_tree_root "$COMMAND")
SHA=$(git -C "$SRC_ROOT" rev-parse HEAD 2>/dev/null) || exit 0
[ -z "$SHA" ] && exit 0

# A report only counts as OUR validate if we watched the matching start. Reading
# an unrelated job id here would record the current HEAD as validated and unlock
# a merge gate for a commit nothing was ever run against. See pending_add().
if [ "$IS_START" = "0" ]; then
  RJOB=$(sf_job_id "$COMMAND")
  [ -z "$RJOB" ] && exit 0
  PEND=$(pending_lookup "$RJOB") || exit 0
  [ -z "$PEND" ] && exit 0
  [ "${PEND##* }" = "validate" ] || exit 0
  SHA=${PEND%% *}
fi

VERDICT=$(sf_deploy_verdict "$(hook_tool_output)" "$COMMAND")
JOB=$(sf_job_id "$COMMAND"); [ -z "$JOB" ] && JOB=$(sf_job_id "$(hook_tool_output)")

if [ "$VERDICT" != "VALIDATE" ]; then
  # In flight: remember it, so the eventual report is recognised as ours.
  [ "$VERDICT" = "UNKNOWN" ] && [ "$IS_START" = "1" ] && [ -n "$JOB" ] && \
    pending_add "$JOB" "$SHA" validate
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

# Uncommitted changes mean the validated tree is not the tree that will merge.
# Checked in the SOURCE tree for the same reason the SHA is read from there.
if [ -n "$(git -C "$SRC_ROOT" status --porcelain -- force-app/ 2>/dev/null)" ]; then
  note "Validate recorded against ${SHA:0:8}, but force-app/ has uncommitted changes." \
       "The merge gate is per-commit: commit these and re-validate, or the PR will be" \
       "blocked as unvalidated."
fi

exit 0
