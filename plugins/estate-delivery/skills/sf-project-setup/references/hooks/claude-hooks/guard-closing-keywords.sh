#!/bin/bash
# PreToolUse (Bash) — never write a GitHub closing keyword from an agent.
#
# WHAT THIS FIXES
# ---------------
# `fixes #42` in a commit message or PR title closes issue #42 in whatever repo
# the commit lands in. Two distinct failures, both live:
#
#   1. In a repo we own, it closes the ticket the MOMENT the PR merges — which is
#      BEFORE the deploy, and against the rule that this local loop leaves tickets
#      OPEN (closure is production delivery scope, and happens only if the user asks
#      for it). A ticket must never close as a side effect of a merge.
#
#   2. In a CLIENT's GitHub repo it closes THEIR #42. Under a Jira-tracked
#      project, an agent writing "#42" into a client's repo is referring to an
#      issue it has never seen, in a tracker it is not supposed to touch. There
#      is no reading of that which is correct.
#
# So: refs, never fixes. This loop does not close tickets; referencing one is all
# a commit or PR should ever do to it.
#
# commit-msg carries the same check as a backstop for terminal-authored commits.
# This hook covers what comes through the agent — including PR titles and bodies,
# which no git hook can ever see.
#
# There is deliberately NO escape hatch. Referencing a ticket without closing it is
# 'refs #N', which is what you want anyway.

set -u
HOOK_EVENT="PreToolUse"
HOOK_DEFER_GATE=1   # the master gate fires in hook_read_input, once the target repo is known
. "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

hook_read_input
COMMAND=$(hook_command_text)
[ -z "$COMMAND" ] && exit 0

# ── A heredoc that is PUBLISHED, not quoted ──────────────────
#
# hook_command_text() strips heredoc BODIES, and for almost every guard that is
# right: a heredoc body is data, and a commit message routinely quotes the very
# commands these guards look for. A doc explaining this rule must not trip it.
#
# There is exactly one shape where the body is not a quotation of a command but
# the ARTIFACT ITSELF: a PR or issue body piped in with `--body-file -` / `-F -`.
# That text goes straight to GitHub as the PR description, where a closing keyword
# closes the issue on merge — and unlike a commit message, NO git hook can back it
# up. commit-msg sees commit messages; it has never seen, and can never see, a PR
# body. `git commit -F - <<MSG` is deliberately NOT in this set for exactly that
# reason: commit-msg catches it, so stripping there costs nothing.
#
# So for these commands only, judge the raw text with the body left in. Narrow on
# purpose: the alternative (stop stripping generally) trades one bypass for a class
# of false blocks, and a guard that refuses correct work loses trust just as fast
# as one that misses.
RAW=$(hook_command)
if printf '%s' "$RAW" \
     | grep -qE 'gh[[:space:]]+(pr[[:space:]]+(create|edit|merge)|issue[[:space:]]+(create|edit))' \
   && printf '%s' "$RAW" \
     | grep -qE -- '(--body-file|-F)[[:space:]=]+-([[:space:]]|$)'; then
  COMMAND="$RAW"
fi

# Only the commands that can actually carry a keyword to GitHub. Prose, echo, and
# file writes are none of this hook's business — a doc that explains the rule
# must not trip it.
echo "$COMMAND" | grep -qE '(^|[;&|][[:space:]]*)([A-Za-z_][A-Za-z0-9_]*=[^[:space:]]*[[:space:]]+)*(git[[:space:]]+([^|;&]*[[:space:]])?commit\b|gh[[:space:]]+pr[[:space:]]+(create|edit|merge)\b|gh[[:space:]]+issue[[:space:]]+(create|edit)\b)' || exit 0

KEYWORDS='(close[sd]?|fix(e[sd])?|resolve[sd]?)'

# ── 1. Closing keyword + #N ──────────────────────────────────
if echo "$COMMAND" | grep -qiE "${KEYWORDS}[[:space:]]+#[0-9]+"; then
  MATCH=$(echo "$COMMAND" | grep -oiE "${KEYWORDS}[[:space:]]+#[0-9]+" | head -3 | tr '\n' ' ')
  block \
    "BLOCKED: a GitHub closing keyword ($MATCH) would auto-close an issue on merge." \
    "" \
    "Use 'refs #N' instead. This local loop never closes a ticket on merge:" \
    "" \
    "  1. merge      the squash lands on $(trunk)" \
    "  2. deploy     sf project deploy start ...   (this is what makes it real)" \
    "  3. verify     acceptance criteria + user green light" \
    "" \
    "The ticket then stays OPEN. Closure is production delivery scope, not this loop's," \
    "and happens only if the user asks. A closing keyword collapses all of this into the" \
    "merge and closes the ticket against a deploy that has not even happened yet."
fi

# ── 2. A #N ref at all, when GitHub is not the tracker ───────
#
# In a Jira-tracked project the number after '#' means nothing to us and
# something specific to whoever owns the repo. Blocking the bare ref as well is
# not pedantry: `#42` in a PR body still renders as a live cross-link.
if [ "$(ticket_system)" != "github" ] && [ "$(ticket_system)" != "none" ]; then
  if echo "$COMMAND" | grep -qE '#[0-9]+'; then
    block \
      "BLOCKED: a '#N' GitHub issue reference, in a project tracked in $(ticket_system)." \
      "" \
      "  $(echo "$COMMAND" | grep -oE '#[0-9]+' | head -3 | tr '\n' ' ')" \
      "" \
      "GitHub resolves '#N' against the repo this lands in — which is not this project's" \
      "tracker. At best it is a dead reference; in a repo we do not own it links to, and" \
      "can notify, somebody else's issue." \
      "" \
      "Reference the ticket the way this project does:  $(ticket_example)"
  fi
fi

exit 0
