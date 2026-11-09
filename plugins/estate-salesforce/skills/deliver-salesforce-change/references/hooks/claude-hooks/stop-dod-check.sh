#!/bin/bash
# Stop — refuse to end the turn while the Definition of Done is visibly incomplete.
#
# Two checks: main ahead of the org, and a deployed ticket still open.
#
# NOT checked: an open worktree. Reusing one across deploys for follow-up fixes
# on the same ticket is supported; cleanup belongs at the end of the TICKET.
# session-status.sh reports open worktrees at session start instead.
#
# Local git state plus at most one gh call, fingerprinted so an identical set of
# findings blocks once. With the stop_hook_active guard, it cannot loop.
#
# Escape hatch: SOLO_SKIP_DOD=1 or SOLO_SKIP_DOD=1.

set -u
HOOK_EVENT="Stop"
. "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

hook_read_input

if [ "${SOLO_SKIP_DOD:-}" = "1" ] || [ "${SOLO_SKIP_DOD:-}" = "1" ]; then
  record_hatch SKIP_DOD "Stop-hook Definition-of-Done check disabled for this turn"
  note "ESCAPE HATCH USED: the Definition-of-Done check was skipped for this turn." \
       "Recorded to .claude/.hatch-log. Whatever is incomplete — main ahead of the org," \
       "a deployed ticket still open — is still incomplete; it just was not checked."
  exit 0
fi
[ "$(hook_field '.stop_hook_active')" = "true" ] && exit 0

MAIN_ROOT=$(main_repo_root ".") || exit 0
[ -z "$MAIN_ROOT" ] && exit 0
cd "$MAIN_ROOT" 2>/dev/null || exit 0

DLOG=$(deploy_log ".")
[ -f "$DLOG" ] || exit 0   # nothing has ever deployed here; nothing to be done about

FINDINGS=()

# ── 1. main ahead of the org ─────────────────────────────────
# Only force-app/ matters: hook, doc and config commits never reach the org.
LAST_DEPLOYED=$(deploy_log_shas "$DLOG" | head -1)
MAIN_SHA=$(git rev-parse main 2>/dev/null || echo "")
if [ -n "$LAST_DEPLOYED" ] && [ -n "$MAIN_SHA" ] && [ "$LAST_DEPLOYED" != "$MAIN_SHA" ] \
   && git cat-file -e "$LAST_DEPLOYED^{commit}" 2>/dev/null; then
  UNDEPLOYED=$(git diff --name-only "$LAST_DEPLOYED" main -- force-app/ 2>/dev/null | head -10)
  if [ -n "$UNDEPLOYED" ]; then
    FINDINGS+=("- main is AHEAD OF THE ORG. Deployable files changed since the last recorded deploy (${LAST_DEPLOYED:0:8}):")
    while IFS= read -r f; do FINDINGS+=("      $f"); done <<< "$UNDEPLOYED"
    FINDINGS+=("      -> git checkout main && git pull && sf project deploy start --source-dir <those files> ...")
  fi
fi

# ── 2. deployed tickets still open ───────────────────────────
if command -v gh >/dev/null 2>&1 && [ -n "$LAST_DEPLOYED" ] && git cat-file -e "$LAST_DEPLOYED^{commit}" 2>/dev/null; then
  ISSUES=$(issue_refs "$LAST_DEPLOYED")
  for N in $ISSUES; do
    STATE=$(gh issue view "$N" --json state -q '.state' 2>/dev/null || echo "")
    if [ "$STATE" = "OPEN" ]; then
      FINDINGS+=("- issue #$N is deployed (${LAST_DEPLOYED:0:8}) but still OPEN.")
      FINDINGS+=("      -> if the acceptance criteria are met and the user has signed off:")
      FINDINGS+=("         comment the SHA, then gh issue close $N, then remove the worktree.")
      FINDINGS+=("      -> if you are waiting on user testing, say so explicitly and stop. That is a")
      FINDINGS+=("         complete answer; keeping the tree open for follow-up fixes is expected.")
    fi
  done
fi

[ "${#FINDINGS[@]}" -eq 0 ] && exit 0

# ── Fingerprint: block once per distinct state ───────────────
STATE_FILE="$MAIN_ROOT/.claude/.dod-state"
FP=$(printf '%s\n' "${FINDINGS[@]}" | shasum 2>/dev/null | awk '{print $1}')
[ -f "$STATE_FILE" ] && [ "$(cat "$STATE_FILE" 2>/dev/null)" = "$FP" ] && exit 0
mkdir -p "$(dirname "$STATE_FILE")" 2>/dev/null
echo "$FP" > "$STATE_FILE"

{
  echo "Definition of Done is not met yet:"
  echo ""
  printf '  %s\n' "${FINDINGS[@]}"
  echo ""
  echo "Finish these, or tell the user explicitly what you are leaving open and why."
  echo "(This check reports each distinct state once — stopping again will not re-block.)"
} >&2
exit 2
