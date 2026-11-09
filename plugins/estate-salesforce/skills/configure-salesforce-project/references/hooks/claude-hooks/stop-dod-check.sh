#!/bin/bash
# Stop — refuse to end the turn while the Definition of Done is visibly incomplete.
#
# One check: trunk ahead of the org. The local Definition of Done tops out at
# "deployed to the sandbox" — ticket closure is out of this loop's scope (tickets
# stay open until production, the delivery system's domain), so nothing here nags
# about an open ticket.
#
# NOT checked: an open worktree. Reusing one across deploys for follow-up fixes
# on the same ticket is supported; cleanup belongs at the end of the TICKET.
# session-status.sh reports open worktrees at session start instead.
#
# Local git state plus at most one gh call, fingerprinted so an identical set of
# findings blocks once. With the stop_hook_active guard, it cannot loop.
#
# Escape hatch: ESTATE_SKIP_DOD=1 (SOLO_ prefixes still honoured).

set -u
HOOK_EVENT="Stop"
HOOK_DEFER_GATE=1   # the master gate fires in hook_read_input, once the target repo is known
. "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

hook_read_input

# DevOps Center, not a clone-local deploy receipt, decides whether stage branches
# are ahead of their orgs. Applying the direct-delivery invariant here would nag the
# agent to deploy staging manually, which is exactly the action this mode forbids.
is_devops_center && exit 0

if [ "${ESTATE_SKIP_DOD:-}" = "1" ] || [ "${SOLO_SKIP_DOD:-}" = "1" ] || [ "${SOLO_SKIP_DOD:-}" = "1" ]; then
  record_hatch SKIP_DOD "Stop-hook Definition-of-Done check disabled for this turn"
  note "ESCAPE HATCH USED: the Definition-of-Done check was skipped for this turn." \
       "Recorded to the hatch-log. Whatever is incomplete — trunk ahead of the org —" \
       "is still incomplete; it just was not checked."
  exit 0
fi
[ "$(hook_field '.stop_hook_active')" = "true" ] && exit 0

MAIN_ROOT=$(main_repo_root ".") || exit 0
[ -z "$MAIN_ROOT" ] && exit 0
cd "$MAIN_ROOT" 2>/dev/null || exit 0
TRUNK=$(trunk)

DLOG=$(deploy_log ".")
[ -f "$DLOG" ] || exit 0   # nothing has ever deployed here; nothing to be done about

FINDINGS=()

# ── trunk ahead of the org ───────────────────────────────────
# Only force-app/ matters: hook, doc and config commits never reach the org.
LAST_DEPLOYED=$(deploy_log_shas "$DLOG" | head -1)
MAIN_SHA=$(git rev-parse "$TRUNK" 2>/dev/null || echo "")
if [ -n "$LAST_DEPLOYED" ] && [ -n "$MAIN_SHA" ] && [ "$LAST_DEPLOYED" != "$MAIN_SHA" ] \
   && git cat-file -e "$LAST_DEPLOYED^{commit}" 2>/dev/null; then
  UNDEPLOYED=$(git diff --name-only "$LAST_DEPLOYED" "$TRUNK" -- force-app/ 2>/dev/null | head -10)
  if [ -n "$UNDEPLOYED" ]; then
    FINDINGS+=("- '$TRUNK' is AHEAD OF THE ORG. Deployable files changed since the last recorded deploy (${LAST_DEPLOYED:0:8}):")
    while IFS= read -r f; do FINDINGS+=("      $f"); done <<< "$UNDEPLOYED"
    PULL="git checkout $TRUNK && git pull"; [ "$(host)" = "none" ] && PULL="git checkout $TRUNK"
    FINDINGS+=("      -> $PULL && sf project deploy start --source-dir <those files> ...")
  fi
fi

[ "${#FINDINGS[@]}" -eq 0 ] && exit 0

# ── Fingerprint: block once per distinct state ───────────────
STATE_FILE=$(dod_state ".")
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
