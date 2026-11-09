#!/bin/bash
# PreToolUse (Bash) — the push gate. Only active on hosts with no CLI merge
# surface, which today means Bitbucket.
#
# WHY THIS EXISTS, AND WHAT IT IS NOT
# -----------------------------------
# The merge gate works by intercepting the merge command. Bitbucket has no
# official CLI, so merges happen in the web browser and there is nothing for a
# PreToolUse hook to see. Rather than pretend the gate still applies, it moves one
# step earlier: a branch that touches force-app/ may not reach the remote without
# a recorded green dry run. Then whatever a human merges in the UI was validated.
#
# This is WEAKER than the merge gate, in two ways worth naming:
#   - It cannot tell a merge from a browse. Someone can merge an old unvalidated
#     branch that was pushed before this stack was installed.
#   - It gates the branch head at push time. Push, then merge something else, and
#     the proof does not follow.
# The deploy-side guards are unaffected and still protect the org — a real deploy
# still requires a clean, synced trunk. Do not describe this as equivalent
# coverage; describe it as the best available interception point on this host.
#
# Escape hatch: ALEY_ALLOW_UNVALIDATED_PUSH=1, recorded like every other.

set -u
HOOK_EVENT="PreToolUse"
HOOK_DEFER_GATE=1   # the master gate fires in hook_read_input, once the target repo is known
. "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

# Input FIRST, config second. hook_read_input() retargets to the repo the command
# acts on, and host is a per-repo answer — reading it before the retarget reads
# whichever project the session happens to be sitting in.
hook_read_input
COMMAND=$(hook_command_text)

# Only hosts where the merge cannot be intercepted.
case "$(host)" in
  bitbucket) ;;
  *) exit 0 ;;
esac

echo "$COMMAND" | grep -qE '(^|[;&|][[:space:]]*)git[[:space:]]+([^|;&]*[[:space:]])?push\b' || exit 0

TRUNK=$(trunk)
BRANCH=$(current_branch ".")
[ -z "$BRANCH" ] && exit 0

# Pushing trunk itself is the post-merge sync, or a revert. Both must go through,
# and both are already covered: the revert is the invariant repair, and the deploy
# guard checks trunk against the remote separately.
[ "$BRANCH" = "$TRUNK" ] && exit 0

if [ "${ALEY_ALLOW_UNVALIDATED_PUSH:-}" = "1" ]; then
  record_hatch ALLOW_UNVALIDATED_PUSH "$COMMAND"
  note "ESCAPE HATCH USED: pushed '$BRANCH' without a recorded validate." \
       "Recorded to the hatch-log. On this host the push gate is the only interception" \
       "point before a browser merge, so nothing else will catch this branch."
  exit 0
fi

# Does this branch carry deployable changes relative to trunk? A docs or config
# branch has nothing to validate.
#
# When the base CANNOT be computed — an unresolvable trunk, or orphan / unrelated
# history — "I can't compute the base" is NOT "there is nothing to validate", so
# this must not exit 0. It falls back to HEAD's own tree: a HEAD that carries no
# force-app/ at all is a genuinely clean push and is allowed; any force-app/
# present (or a HEAD whose tree cannot even be read) falls through to the validate
# gate below, which blocks unless a green dry run is on record. On Bitbucket this
# hook is the SOLE interception point before a web-UI merge, so a fail-open here
# has no backstop — hence force-app-present-or-indeterminable must not slip past.
if BASE=$(git merge-base "$TRUNK" HEAD 2>/dev/null); then
  DEPLOYABLE=$(git diff --name-only "$BASE" HEAD -- force-app/ 2>/dev/null | head -1)
elif HEAD_FA=$(git ls-tree -r --name-only HEAD -- force-app/ 2>/dev/null); then
  DEPLOYABLE=$(printf '%s\n' "$HEAD_FA" | head -1)
else
  DEPLOYABLE="force-app/"   # HEAD's tree unreadable — indeterminable, not clean
fi
[ -z "$DEPLOYABLE" ] && exit 0

HEAD_SHA=$(git rev-parse HEAD 2>/dev/null) || exit 0
VLOG=$(validate_log ".")
grep -q "^${HEAD_SHA}[[:space:]]" "$VLOG" 2>/dev/null && exit 0

block \
  "BLOCKED: '$BRANCH' touches force-app/ and commit ${HEAD_SHA:0:8} has no recorded validate." \
  "" \
  "This repo's host is Bitbucket, which has no CLI to merge through — so the merge" \
  "itself cannot be gated. The push is the last point anything can be checked, which" \
  "is why the gate lives here:" \
  "" \
  "  sf project deploy start --dry-run \\" \
  "    --source-dir <each changed file> \\" \
  "    --test-level RunSpecifiedTests --tests <TestClasses>" \
  "" \
  "then push, then open and merge the PR in the browser, then deploy from '$TRUNK'." \
  "" \
  "Committed again after validating? Re-validate — the record is per-commit." \
  "Genuinely cannot validate? ALEY_ALLOW_UNVALIDATED_PUSH=1 git push ... and say so" \
  "on the ticket."
