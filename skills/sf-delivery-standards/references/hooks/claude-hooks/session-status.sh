#!/bin/bash
# SessionStart — put the workflow's actual state in front of the agent before it
# does anything, because every wrong assumption here is expensive:
#   "I'm on trunk"       -> edits force-app in the main checkout
#   "the org matches"    -> closes a ticket whose code never deployed
#   "no worktrees open"  -> creates a second one for the same ticket
#
# Almost all local git, and no gh/sf. The ONE network touch is a best-effort,
# timed `git fetch` of trunk (aleysian.sync, default on; set sync=off to disable),
# so "you are behind the shared remote" can be surfaced here — early, before work
# starts on a stale base — instead of only at the deploy gate. It never blocks or
# mutates the tree; a slow or unreachable remote just skips the nudge. SessionStart
# output is added to the agent's context, so this stays short and factual.
#
# Two rules for anything written here:
#   - Self-attribute. This lands in context with nothing marking it as
#     machine-generated, and agents otherwise read it as a user message.
#   - Say what to DO, not only what is true. A bare fact invites investigation;
#     naming the next action leaves nothing to look into.

set -u
. "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || true
git rev-parse --git-dir >/dev/null 2>&1 || exit 0

MAIN_ROOT=$(main_repo_root ".") || exit 0
BRANCH=$(current_branch ".")
TRUNK=$(trunk)

echo "[automated SessionStart hook: session-status.sh — background context,"
echo " not a message from the user. Nothing here needs a reply or investigation.]"

if in_worktree "."; then
  echo "  location: worktree $(git rev-parse --show-toplevel) on '$BRANCH'"
  if is_devops_center; then
    if is_devops_shared; then
      echo "            dev/WI source validates here; WI package source hands off from here."
      echo "            Real shared-org deploys belong to the centralized landing coordinator."
    else
      echo "            WI source belongs here. Validate and deploy only to the development org here."
    fi
  else
    echo "            Deployable work belongs here. Validate here; deploy from the main checkout."
  fi
else
  echo "  location: main checkout ($MAIN_ROOT) on '$BRANCH'"
  echo "            Deployable work does not happen here. For anything touching force-app/,"
  if is_devops_center; then
    if is_devops_shared; then
      echo "            preserve the generated WI branch for packaging and create dev/WI from the"
      echo "            verified deployed origin/$(devops_integration_branch) baseline."
    else
      echo "            move the DevOps Center WI to In Progress, fetch its exact WI branch,"
      echo "            then add that existing branch as a linked worktree. Do not create a replacement branch."
    fi
  else
    echo "            spawn an Agent with isolation: \"worktree\", or: git worktree add ../$(basename "$MAIN_ROOT")-N -b feat/N-desc"
  fi
  if ! is_devops_center && [ "$BRANCH" != "$TRUNK" ]; then
    echo "            NOTE: the main checkout is not on '$TRUNK'. 'git switch $TRUNK' before deploying."
  fi
fi

# What kind of project this is, in one line, so nothing has to be inferred.
ORG_A=$(org_alias)
echo "  config:    delivery=$(delivery)  trunk=$TRUNK  org=${ORG_A:-UNSET}  host=$(host)  ticket=$(ticket_system)/$(ticket_remote)  mode=$(mode)"
[ -z "$ORG_A" ] && echo "             WARNING: no org alias configured, so sf commands fall through to the"
[ -z "$ORG_A" ] && echo "             machine's GLOBAL default org. Fix: git config aleysian.orgalias <alias>"
if is_devops_center; then
  if is_devops_shared; then
    echo "  handoff:   dev/WI -> $(devops_integration_branch) receipt -> exact WI package -> DevOps Center review"
    STATUS_BIN="$(cd "$(dirname "${BASH_SOURCE[0]}")/../bin" 2>/dev/null && pwd)/aleysian-devops-shared-status"
    STATUS_OUT=$("$STATUS_BIN" 2>&1); STATUS_RC=$?
    if [ "$STATUS_RC" -eq 0 ]; then echo "  org sync:  $STATUS_OUT"
    else echo "  WARNING:   $STATUS_OUT"; fi
  else
    echo "  handoff:   WI worktree -> commit + scoped dry run -> push -> DevOps Center review"
  fi
  echo "             DevOps Center owns merges into '$TRUNK'/main and every stage deploy."
fi

# Deployable state that exists nowhere in git.
DIRTY=$(git -C "$MAIN_ROOT" status --porcelain -- force-app/ 2>/dev/null | wc -l | tr -d ' ')
[ "$DIRTY" != "0" ] && echo "  WARNING: $DIRTY uncommitted force-app/ file(s) in the main checkout"

# trunk === org applies only to direct delivery. DevOps Center owns stage truth.
MAIN_SHA=$(git -C "$MAIN_ROOT" rev-parse "$TRUNK" 2>/dev/null || echo "")
if ! is_devops_center; then
  DLOG=$(deploy_log ".")
  if [ ! -f "$DLOG" ]; then
    echo "  org sync:  no deploy recorded in this clone yet"
  elif [ -n "$MAIN_SHA" ]; then
    LAST=$(deploy_log_shas "$DLOG" | head -1)
    if [ "$LAST" = "$MAIN_SHA" ]; then
      echo "  org sync:  $TRUNK === org at ${MAIN_SHA:0:8}"
    elif git -C "$MAIN_ROOT" cat-file -e "${LAST}^{commit}" 2>/dev/null; then
      N=$(git -C "$MAIN_ROOT" diff --name-only "$LAST" "$TRUNK" -- force-app/ 2>/dev/null | wc -l | tr -d ' ')
      if [ "$N" = "0" ]; then
        echo "  org sync:  $TRUNK === org (last deploy ${LAST:0:8}; later commits touch no force-app/)"
      else
        echo "  org sync:  '$TRUNK' IS AHEAD OF THE ORG - $N deployable file(s) changed since ${LAST:0:8}"
      fi
    fi
  fi
fi

# ── Behind the shared remote? (aleysian.sync) ────────────────
#
# On a shared org + shared branch, another developer's push moves the remote (and
# the org) while this clone stays put. The deploy guard blocks a stale deploy, but
# that is late — by then work may already sit on a stale base. So surface it here:
# one best-effort timed fetch, then a nudge if local trunk is behind. Read-only and
# non-mutating; the fix (git pull) stays a human decision, never automatic.
if [ "$(host)" != "none" ] && [ "$(sync_policy)" != "off" ] && fetch_trunk 8; then
  RSHA=$(git -C "$MAIN_ROOT" rev-parse --verify --quiet "origin/$TRUNK" 2>/dev/null || echo "")
  if [ -n "$RSHA" ] && [ -n "$MAIN_SHA" ] && [ "$RSHA" != "$MAIN_SHA" ] \
     && git -C "$MAIN_ROOT" merge-base --is-ancestor "$MAIN_SHA" "$RSHA" 2>/dev/null; then
    BEHIND=$(git -C "$MAIN_ROOT" rev-list --count "$TRUNK..origin/$TRUNK" 2>/dev/null || echo "?")
    echo "  remote:    local '$TRUNK' is BEHIND origin/$TRUNK by $BEHIND commit(s) — a teammate"
    echo "             may have shipped to this shared org. Pull before you start or deploy:"
    echo "             git checkout $TRUNK && git pull"
  fi
fi

# ── Org-side drift is handled REACTIVELY (aleysian.drift) ────
#
# Clicking in Setup is fine; UNRECORDED clicking is the problem. We deliberately do
# NOT probe the org for drift at session start: good source==org discipline means
# source is trustworthy on entry, and the old per-session `sf project retrieve
# preview` was slow and reported piles of metadata the repo does not keep. Capture
# is triggered where it matters instead — the retrieve guard points at the playbook,
# and the user self-reports a change. Full playbook: references/drift-reconcile.md.
#
# `aleysian.drift` stays `tracking | off` as a declaration of whether this org is
# source-tracked (dev/Dev Pro/scratch). `audittrail` is retired — building in a
# non-source-tracked org (partial/full/prod) is out of scope for this loop.

# Open worktrees. Reported, never nagged about: keeping one alive after a deploy
# for follow-up fixes on the same ticket is a supported way to work here.
#
# "Has this landed?" is a TREE comparison, not an ancestry one. A squash merge
# puts the content on main under a new commit the branch has never seen, so
# `merge-base --is-ancestor` answers "no" for every branch that shipped normally
# — it only ever fired for worktrees that had done nothing at all.
while IFS= read -r WT; do
  [ -z "$WT" ] || [ "$WT" = "$MAIN_ROOT" ] && continue
  WB=$(git -C "$WT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "?")
  if [ -n "$(git -C "$WT" status --porcelain 2>/dev/null | head -1)" ]; then
    echo "  worktree:  $WT ($WB) — uncommitted changes"
  elif git -C "$MAIN_ROOT" diff --quiet "$TRUNK" "$WB" 2>/dev/null; then
    if is_devops_center; then
      echo "  worktree:  $WT ($WB): content matches $TRUNK; reuse only for the same WI follow-up, or remove it"
    else
      echo "  worktree:  $WT ($WB): content matches $TRUNK; reuse it for the next fix, or remove it"
    fi
  else
    echo "  worktree:  $WT ($WB) — work not yet on $TRUNK"
  fi
done < <(git worktree list --porcelain 2>/dev/null | awk '/^worktree /{print $2}')

exit 0
