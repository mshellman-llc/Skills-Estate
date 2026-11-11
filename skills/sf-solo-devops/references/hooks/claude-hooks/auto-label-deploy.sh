#!/bin/bash
# PostToolUse (Bash) — record a real deploy and update the ticket.
#
#   1. Append "<sha> <job-id> <utc stamp>" to .claude/.deploy-log — the
#      proof-of-deploy guard-issue-close.sh requires. Only genuine successes go
#      in; the job id is recorded so any entry can be re-checked against the org.
#   2. Label + comment every issue the deployed commit references.
#   3. Report what is left in the Definition of Done.
#
# Fires on `deploy start` and on `deploy report` / `deploy resume`, since the
# documented pattern for a long deploy is `--async` + `report --job-id`.
#
# Deploy vs dry run is read from a complete CLI JSON result — see
# sf_deploy_verdict(). Never blocks.

set -u
HOOK_EVENT="PostToolUse"
. "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

hook_read_input
COMMAND=$(hook_command_text)

echo "$COMMAND" | grep -qE '\b(sf|sfdx)\b.*\bdeploy[[:space:]]+(start|report|resume)\b' || exit 0

# A dry run is a validate. record-validate.sh owns those.
if echo "$COMMAND" | grep -qE '\bdeploy[[:space:]]+start\b' && echo "$COMMAND" | grep -qE -- '--dry-run'; then
  exit 0
fi

IS_START=0
echo "$COMMAND" | grep -qE '\bdeploy[[:space:]]+start\b' && IS_START=1

BRANCH=$(current_branch ".")
SHA=$(git rev-parse HEAD 2>/dev/null)
[ -z "$SHA" ] && exit 0

# A `report`/`resume` only counts as a deploy result if we watched the matching
# `start`. Otherwise this is somebody inspecting an old job, and recording HEAD
# against it invents a deploy that never happened. See pending_add() in _lib.sh.
PENDING_SHA=""
if [ "$IS_START" = "0" ]; then
  RJOB=$(sf_job_id "$COMMAND")
  [ -z "$RJOB" ] && exit 0
  PEND=$(pending_lookup "$RJOB") || exit 0
  [ -z "$PEND" ] && exit 0
  PENDING_SHA=${PEND%% *}
  [ "${PEND##* }" = "deploy" ] || exit 0
  # main may have moved while the deploy was in flight; credit the commit that
  # was actually sent, not whatever HEAD is now.
  SHA="$PENDING_SHA"
fi

# Only main deploys to the org. Anything else is not proof of the invariant
# (and guard-sf-deploy.sh should have blocked it before it ran).
#
# Checked for `start` only. A `report` carries its own provenance: the pending
# record above exists precisely because we watched a start on main, so which
# branch the shell happens to sit on when the result is collected is irrelevant.
if [ "$IS_START" = "1" ] && [ "$BRANCH" != "main" ]; then
  note "Deploy ran from '$BRANCH', not main. NOT recorded as proof-of-deploy." \
       "The org may now hold code that is not on main — restore the invariant:" \
       "deploy the same files from main, or revert what this pushed."
  exit 0
fi

OUTPUT=$(hook_tool_output)
VERDICT=$(sf_deploy_verdict "$OUTPUT" "$COMMAND")
JOB=$(sf_job_id "$COMMAND"); [ -z "$JOB" ] && JOB=$(sf_job_id "$OUTPUT")

case "$VERDICT" in
  DEPLOY) ;;
  VALIDATE)
    exit 0 ;;   # check-only; record-validate.sh handles it
  FAILED)
    [ -n "$JOB" ] && pending_remove "$JOB"
    note "Deploy FAILED, so nothing was recorded. main may now be ahead of the org." \
         "Preserve the failed result and inspect the org state before choosing fix-forward or rollback."
    exit 0 ;;
  *)
    # Almost always an --async deploy still in flight, so do not report it as a
    # failure. Remember the job so the eventual `deploy report` is recognised as
    # our deploy rather than a lookup.
    if [ "$IS_START" = "1" ]; then
      [ -n "$JOB" ] && pending_add "$JOB" "$SHA" deploy
      note "Deploy not finished (or its result could not be read), so nothing was recorded yet." \
           "If this was --async, report on the job id and the result will be recorded then:" \
           "  sf project deploy report --job-id ${JOB:-<id>}"
    fi
    exit 0 ;;
esac

[ -n "$JOB" ] && pending_remove "$JOB"
DLOG=$(deploy_log ".")
mkdir -p "$(dirname "$DLOG")" 2>/dev/null

# Already recorded? Then this is a re-report of a deploy we have seen, and the
# ticket already carries its comment. Recording is idempotent by sha; the GitHub
# comment is not, so this check has to gate BOTH — otherwise every follow-up
# `deploy report` posts another identical "Deployed at <sha>" to the ticket.
if deploy_log_shas "$DLOG" | grep -qx "$SHA"; then
  exit 0
fi

echo "$SHA ${JOB:-unknown} $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$DLOG"

ISSUES=$(issue_refs "$SHA")
SHORT_SHA=${SHA:0:8}

if [ -z "$ISSUES" ]; then
  note "Deployed ${SHORT_SHA} from main, recorded as proof-of-deploy." \
       "The commit message carries no 'refs #N' / 'fixes #N', so no ticket was updated —" \
       "and guard-issue-close.sh will refuse to close anything against this deploy."
  exit 0
fi

if [ "${SOLO_GITHUB_UPDATES:-0}" != "1" ]; then
  note "Deployment recorded locally. GitHub issue updates require explicit project opt-in (SOLO_GITHUB_UPDATES=1)."
  exit 0
fi

command -v gh >/dev/null 2>&1 || {
  note "Deployed ${SHORT_SHA} from main, recorded. gh is unavailable, so issues" \
       "$(echo "$ISSUES" | tr '\n' ' ')were not labelled — update them by hand."
  exit 0
}

EXPRESS=""
for N in $ISSUES; do
  gh issue edit "$N" --add-label "deployed" >/dev/null 2>&1
  gh issue comment "$N" --body "Deployed to the org from \`main\` at \`${SHORT_SHA}\` (deploy \`${JOB:-unknown}\`)." >/dev/null 2>&1
  LABELS=$(gh issue view "$N" --json labels -q '[.labels[].name] | join(",")' 2>/dev/null || echo "")
  case ",$LABELS," in
    *,express,*) EXPRESS="$EXPRESS #$N" ;;
  esac
done

LIST=$(echo "$ISSUES" | sed 's/^/#/' | tr '\n' ' ')

if [ -n "$EXPRESS" ]; then
  note "Deployed ${SHORT_SHA}. Labelled 'deployed' + commented on: ${LIST}" \
       "EXPRESS:${EXPRESS} — no separate user-testing round. Verify the acceptance" \
       "criteria now, then close the ticket(s) and remove the worktree."
else
  note "Deployed ${SHORT_SHA}. Labelled 'deployed' + commented on: ${LIST}" \
       "Remaining Definition of Done: acceptance criteria verified, user green light," \
       "close the ticket(s), remove the worktree."
fi

exit 0
