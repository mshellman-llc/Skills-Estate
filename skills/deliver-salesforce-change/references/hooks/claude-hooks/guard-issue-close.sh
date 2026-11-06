#!/bin/bash
# PreToolUse (Bash) — a ticket cannot be closed until its code is in the org.
#
# Definition of Done step 1 is "deployed", not "validated": closing after a
# green dry run leaves main ahead of the org.
#
# Proof is .claude/.deploy-log. A close is allowed when one of those commits'
# histories references #N.
#
# Escape hatch: label the issue 'docs-only' or 'no-deploy'.

set -u
HOOK_EVENT="PreToolUse"
. "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

hook_read_input
COMMAND=$(hook_command_text)

echo "$COMMAND" | grep -qE '\bgh[[:space:]]+issue[[:space:]]+close\b' || exit 0

ISSUE=$(echo "$COMMAND" \
  | grep -oE '\bgh[[:space:]]+issue[[:space:]]+close[[:space:]]+#?[0-9]+' \
  | grep -oE '[0-9]+$')

# URL form or a variable — don't guess at what is being closed.
[ -z "$ISSUE" ] && exit 0

# Explicitly exempted on the ticket itself.
if command -v gh >/dev/null 2>&1; then
  LABELS=$(gh issue view "$ISSUE" --json labels -q '[.labels[].name] | join(",")' 2>/dev/null || echo "")
  case ",$LABELS," in
    *,docs-only,*|*,no-deploy,*)
      record_hatch CLOSE_EXEMPT_LABEL "#$ISSUE labels=[$LABELS]"
      note "ESCAPE HATCH USED: #$ISSUE closed under a 'docs-only'/'no-deploy' label," \
           "so no proof of deploy was required. Recorded to .claude/.hatch-log." \
           "If this ticket did ship metadata, the label is wrong and the audit trail now" \
           "says it shipped nothing."
      exit 0 ;;
  esac
fi

DLOG=$(deploy_log ".")

if [ ! -f "$DLOG" ]; then
  block \
    "BLOCKED: cannot close #$ISSUE — no deploy has ever been recorded in this clone." \
    "" \
    "Definition of Done needs a real deploy, not a dry run:" \
    "  git checkout main && git pull" \
    "  sf project deploy start --source-dir <changed files> \\" \
    "    --test-level RunSpecifiedTests --tests <TestClasses>" \
    "" \
    "Ticket genuinely has no deployable output? Label it and close:" \
    "  gh issue edit $ISSUE --add-label docs-only"
fi

while read -r SHA; do
  [ -z "$SHA" ] && continue
  [ -n "$(history_references_issue "$SHA" "$ISSUE")" ] && exit 0
done < <(deploy_log_shas "$DLOG")

LAST_DEPLOY=$(deploy_log_shas "$DLOG" | head -1)

block \
  "BLOCKED: cannot close #$ISSUE — no deployed commit references it." \
  "" \
  "Deploys are on record (most recent: ${LAST_DEPLOY:0:8}) but no commit in their" \
  "histories says 'refs #$ISSUE' / 'fixes #$ISSUE'. Either this ticket's code is merged" \
  "but not yet deployed, or the squash-merge commit dropped the issue reference." \
  "" \
  "Restore main === org first:" \
  "  git checkout main && git pull" \
  "  sf project deploy start --source-dir <changed files> \\" \
  "    --test-level RunSpecifiedTests --tests <TestClasses>" \
  "" \
  "Then close. If the merge commit simply omitted '#$ISSUE', say so in a comment on the" \
  "ticket with the SHA before closing — the audit trail is the point of the gate."
