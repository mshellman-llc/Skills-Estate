#!/bin/bash
# PostToolUse / TaskCompleted (Bash) — record a real deploy to the deploy-log.
#
#   1. Append "<sha> <job-id> <utc stamp>" to the state dir's deploy-log — the
#      proof-of-deploy the merge gate reads, and what the DoD nag checks against.
#      Only genuine successes go in; the job id is recorded so any entry can be
#      re-checked against the org.
#   2. Report what is left in the Definition of Done.
#
# It does NOT touch the tracker. A hook cannot reach the session's MCP, and the
# one ticket write this loop does — a comment recording the deployed SHA + job id —
# is the AGENT's job via the tracker (Jira: the Rovo MCP addCommentToJiraIssue;
# GitHub: gh issue comment). See references/ticket-adapters.md. It never labels,
# transitions, or closes a ticket: closure is out of this loop's scope.
#
# Fires on `deploy start` and on `deploy report` / `deploy resume`, since the
# documented pattern for a long deploy is `--async` + `report --job-id`.
#
# Registered under BOTH PostToolUse and TaskCompleted. When the harness
# auto-backgrounds a long-running deploy, PostToolUse fires with an incomplete
# result. TaskCompleted fires when the background command actually finishes,
# carrying the real output, so the recording happens then instead.
#
# Deploy vs dry run is decided by the ORG, not the console text — see
# sf_deploy_verdict(). Never blocks.

set -u
HOOK_EVENT="PostToolUse"
HOOK_DEFER_GATE=1   # the master gate fires in hook_read_input, once the target repo is known
. "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

hook_read_input
is_devops_center && exit 0
# Derive the actual event from the JSON input so the same script works under both
# PostToolUse and TaskCompleted without a wrapper. note() uses HOOK_EVENT to route
# its message through the correct hookEventName channel.
_ev=$(hook_field '.hook_event_name')
[ -n "$_ev" ] && HOOK_EVENT="$_ev"
COMMAND=$(hook_command_text)

# Anchored to a COMMAND POSITION — see SFDS_DEPLOY_RE / SFDS_CMDPOS in _lib.sh.
# Unanchored, `grep -rn "sf project deploy start" docs/` counted as a deploy, and if
# the doc it found quoted a sample transcript the grep OUTPUT carried "Status:
# Succeeded" — writing a PROOF-OF-DEPLOY entry for a commit no org had ever seen,
# which the merge gate then reads as a shipped commit and the DoD nag as "trunk is in
# the org". This hook forges the evidence rather than merely missing it, so prose must
# not reach it.
echo "$COMMAND" | grep -qE "${SFDS_DEPLOY_RE}(start|report|resume)\b" || exit 0

# A dry run is a validate. record-validate.sh owns those.
if echo "$COMMAND" | grep -qE "${SFDS_DEPLOY_RE}start\b" && echo "$COMMAND" | grep -qE -- '--dry-run'; then
  exit 0
fi

IS_START=0
echo "$COMMAND" | grep -qE "${SFDS_DEPLOY_RE}start\b" && IS_START=1

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

# Only trunk deploys to the org. Anything else is not proof of the invariant
# (and guard-sf-deploy.sh should have blocked it before it ran).
#
# Checked for `start` only. A `report` carries its own provenance: the pending
# record above exists precisely because we watched a start on trunk, so which
# branch the shell happens to sit on when the result is collected is irrelevant.
TRUNK=$(trunk)
if [ "$IS_START" = "1" ] && [ "$BRANCH" != "$TRUNK" ]; then
  note "Deploy ran from '$BRANCH', not '$TRUNK'. NOT recorded as proof-of-deploy." \
       "The org may now hold code that is not on '$TRUNK' — restore the invariant:" \
       "deploy the same files from '$TRUNK', or revert what this pushed."
  exit 0
fi

OUTPUT=$(hook_tool_output)
VERDICT=$(sf_deploy_verdict "$OUTPUT" "$COMMAND")
JOB=$(sf_job_id "$COMMAND"); [ -z "$JOB" ] && JOB=$(sf_job_id "$OUTPUT")

case "$VERDICT" in
  DEPLOY)
    # The org confirmed the job id — but on a `start`, that id was scraped from this
    # command's COMBINED output. A foreign id echoed after a deploy that actually
    # failed is confirmed by the org just the same, and crediting HEAD for it forges
    # the proof-of-deploy the merge gate reads. Require this command's own output to show the
    # deploy succeeded before recording. The report/resume path is already bound by
    # pending_lookup and needs no such check — hence IS_START only.  (FORGE 1)
    if [ "$IS_START" = "1" ] && ! deploy_start_self_confirmed "$OUTPUT"; then
      note "A deploy id in the output was confirmed by the org, but this command's own" \
           "output shows no successful deploy — the id may have come from elsewhere in a" \
           "chained command (e.g. a trailing echo). NOTHING was recorded as proof-of-deploy." \
           "If this was a real --async deploy, collect it explicitly and it records then:" \
           "  sf project deploy report --job-id ${JOB:-<id>}"
      exit 0
    fi
    ;;
  VALIDATE)
    exit 0 ;;   # check-only; record-validate.sh handles it
  FAILED)
    [ -n "$JOB" ] && pending_remove "$JOB"
    note "Deploy FAILED, so nothing was recorded. '$TRUNK' may now be ahead of the org." \
         "Fix forward (new worktree, <5 min) or revert:" \
         "  git revert HEAD --no-edit && git push && sf project deploy start --source-dir <same files> ..."
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
  note "Deployed ${SHORT_SHA} from '$TRUNK', recorded as proof-of-deploy." \
       "The commit message carries no ticket ref, so no ticket is associated with it."
  exit 0
fi

# ── The one ticket write this loop does — and the AGENT does it ──────────────
#
# A hook cannot reach the session's MCP, so it cannot write to a Jira ticket, and
# it deliberately does not shell out to a tracker CLI to do it either. Recording
# the deploy on the ticket is a COMMENT (never a label, transition, or closure),
# and the agent posts it: Jira via the Rovo MCP addCommentToJiraIssue, GitHub via
# `gh issue comment`. The client-tracker policy (do not write to a client's
# tickets without agreement) is the agent's to honour — it is named in the note
# so the decision is visible rather than assumed.
LIST=$(for N in $ISSUES; do printf '%s ' "$(ticket_label "$N")"; done)

if [ "$(ticket_system)" = "jira" ]; then
  CMT="the Rovo MCP: mcp__*__addCommentToJiraIssue"
else
  CMT="gh issue comment <ticket>"
fi

if [ "$(ticket_remote)" = "client" ]; then
  note "Deployed ${SHORT_SHA} from '$TRUNK', recorded as proof-of-deploy." \
       "Tracker is the CLIENT's (estate.ticket.remote=client) — do NOT write to ${LIST}" \
       "automatically. Update them through their process if that has been agreed." \
       "Remaining Definition of Done: acceptance criteria, user green light. The ticket" \
       "stays open (closure is production delivery scope) unless the user asks to close it."
  exit 0
fi

note "Deployed ${SHORT_SHA} from '$TRUNK', recorded as proof-of-deploy." \
     "Record it on the ticket(s) ${LIST}with a COMMENT (not a transition or closure), via" \
     "  $CMT" \
     "  body: Deployed to the org from \`$TRUNK\` at \`${SHORT_SHA}\` (deploy \`${JOB:-unknown}\`)." \
     "" \
     "Remaining Definition of Done: acceptance criteria verified, user green light, worktree" \
     "removed. Leave the ticket OPEN; closing it is production delivery scope, not this loop's." \
     "close it only if the user explicitly asks."

exit 0
