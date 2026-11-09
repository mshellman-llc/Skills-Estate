#!/bin/bash
# PreToolUse (Bash) — record use of an escape hatch. NEVER blocks.
#
# Most hatches self-report from inside the guard they disable. `git commit
# --no-verify` cannot: it stops every git hook from running, so no git hook can
# log its own bypass. The only place left to see it is the command, before it
# executes.
#
# SCOPE: this sees commands issued through Claude Code's Bash tool. A
# --no-verify typed in a terminal or clicked in an IDE is invisible here, so the
# claim is "hatches used through the agent are recorded", not "all commits are
# accounted for".
#
# Env-var hatches are matched here too, as a second layer. Shell state does not
# persist between Bash calls, so a hatch var must be set inline on the command.

set -u
HOOK_EVENT="PreToolUse"
HOOK_DEFER_GATE=1   # the master gate fires in hook_read_input, once the target repo is known
. "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

hook_read_input
COMMAND=$(hook_command_text)

[ -z "$COMMAND" ] && exit 0

USED=""

# Anchor to a COMMAND POSITION: start of a line, or after a separator, allowing
# any number of leading VAR=value assignments. Without this, writing *about* a
# hatch uses one:
#
#   echo "never use git commit --no-verify" >> notes.md
#
# ...logged a bypass that never happened. A log that cries wolf is discarded, and
# false entries in an audit trail are worse than a thin one. Same rule the guards
# already follow — prose is not a command.
#
# The pattern now lives in _lib.sh as SFDS_CMDPOS, because the two deploy recorders
# needed the same anchor for the same reason and one definition beats three. The
# local name is kept so the patterns below read unchanged.
CMDPOS="$SFDS_CMDPOS"

# --no-verify / -n on a commit. The hooks it skips cannot report themselves.
if echo "$COMMAND" | grep -qE "${CMDPOS}git[[:space:]]+([^|;&]*[[:space:]])?commit\b[^|;&]*(--no-verify|[[:space:]]-n\b)"; then
  record_hatch NO_VERIFY "$COMMAND"
  USED="$USED
  - git commit --no-verify — prettier, ESLint, PMD, Jest and the issue-ref check
    were all skipped for this commit. None of them can report their own bypass."
fi

# Inline env-var hatches. The guards they disable log too; this catches the case
# where the guard never runs at all.
if echo "$COMMAND" | grep -qE "${CMDPOS}(ESTATE|SOLO)_ALLOW_UNVALIDATED_MERGE=1([[:space:]]|\$)"; then
  record_hatch ALLOW_UNVALIDATED_MERGE_INLINE "$COMMAND"
  USED="$USED
  - the validate-before-merge gate was disabled for this command."
fi

if echo "$COMMAND" | grep -qE "${CMDPOS}ESTATE_ALLOW_LOCAL_MERGE=1([[:space:]]|\$)"; then
  record_hatch ALLOW_LOCAL_MERGE_INLINE "$COMMAND"
  USED="$USED
  - the local-merge-into-trunk gate was disabled for this command."
fi

if echo "$COMMAND" | grep -qE "${CMDPOS}(ESTATE|SOLO)_SKIP_DOD=1([[:space:]]|\$)"; then
  record_hatch SKIP_DOD_INLINE "$COMMAND"
  USED="$USED
  - the Definition-of-Done Stop check was disabled for this command."
fi

[ -z "$USED" ] && exit 0

note "ESCAPE HATCH USED — recorded to the hatch-log:${USED}" \
     "" \
     "This is allowed and is not an error. It is recorded so the decision survives" \
     "the conversation. If it was deliberate, say why on the ticket."

exit 0
