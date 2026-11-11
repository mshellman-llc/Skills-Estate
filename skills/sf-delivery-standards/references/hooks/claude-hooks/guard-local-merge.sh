#!/bin/bash
# PreToolUse (Bash) — block local git merge into trunk on hosted repos.
#
# WHAT THIS FIXES
# ---------------
# On a repo hosted on GitHub/GitLab/Azure, feature branches land on trunk through
# the host's PR mechanism (gh pr create + gh pr merge, etc.). An agent that does
# `git merge feature-branch` locally and then `git push` bypasses the PR entirely:
# no review artifact, no merge record on the host, and the auto-label and
# closing-keyword guards cannot find a PR to track. The result is untraceable
# commits on trunk that look like they appeared from nowhere.
#
# guard-pr-merge.sh gates the HOST's merge command (validate before merge).
# This hook gates the WRONG merge command (local merge instead of a PR).
# They are separate concerns:
#   - guard-pr-merge.sh: "you are using the right mechanism, but haven't validated"
#   - guard-local-merge.sh: "you are using the wrong mechanism entirely"
#
# ALLOWED
# -------
#   - git merge on a non-trunk branch (syncing trunk down into a feature branch)
#   - git merge of a remote-tracking ref (origin/main, upstream/main — syncing
#     with the remote, which is what `git pull` does)
#   - host=none — local merge IS the merge mechanism (see bin/aleysian-merge)
#   - host=bitbucket — no CLI merge exists; guard-push.sh is the gate instead
#
# Escape hatch: ALEY_ALLOW_LOCAL_MERGE=1, recorded like every other.

set -u
HOOK_EVENT="PreToolUse"
HOOK_DEFER_GATE=1   # the master gate fires in hook_read_input, once the target repo is known
. "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

hook_read_input
COMMAND=$(hook_command_text)

# Only hosts with a CLI merge surface that SHOULD be used instead.
HOST=$(host)
case "$HOST" in
  github|gitlab|azure) ;;
  *) exit 0 ;;
esac

# Is this a git merge command?
echo "$COMMAND" | grep -qE "${SFDS_CMDPOS}git[[:space:]]+([^|;&]*[[:space:]])?merge\b" || exit 0

TRUNK=$(trunk)
BRANCH=$(current_branch ".")
[ -z "$BRANCH" ] && exit 0

# Only merges into the local landing branch or another protected pipeline branch
# matter. In DevOps Center mode both staging and main are service-owned.
IS_PIPELINE_BASE=0
[ "$BRANCH" = "$TRUNK" ] && IS_PIPELINE_BASE=1
for p in $(protected); do [ "$BRANCH" = "$p" ] && IS_PIPELINE_BASE=1; done
[ "$IS_PIPELINE_BASE" = "1" ] || exit 0

# What is being merged? Extract the positional argument after `git merge` and any
# flags. This is a best-effort parse: it strips --flag and --flag=value tokens and
# takes the first remaining argument. An unparseable merge (pipes, subshells) falls
# through and blocks — failing closed is correct here, because the merge is into
# trunk on a hosted repo and the agent should be using a PR regardless.
MERGE_TARGET=""
MERGE_ARGS=$(printf '%s' "$COMMAND" \
  | sed -nE 's/.*git[[:space:]]+([^|;&]*[[:space:]])?merge[[:space:]]+(.*)/\2/p' \
  | head -1)
if [ -n "$MERGE_ARGS" ]; then
  # Walk the tokens, skip flags.
  for tok in $MERGE_ARGS; do
    case "$tok" in
      --*=*) continue ;;      # --option=value
      --*)   continue ;;      # --flag (git-merge flags that take a value are rare
                              #  and none look like a branch name, so skipping the
                              #  flag token alone is safe enough for this purpose)
      -*)    continue ;;      # short flag
      *)     MERGE_TARGET="$tok"; break ;;
    esac
  done
fi

# Merging a remote-tracking ref (origin/main, upstream/main) is syncing with the
# remote — what `git pull` does internally. Allow it.
if [ -n "$MERGE_TARGET" ]; then
  case "$MERGE_TARGET" in
    origin/*|upstream/*) exit 0 ;;
  esac
  # Also allow any ref that git resolves to a remote-tracking branch, so
  # `git merge remotes/origin/main` or a custom remote name are not false-blocked.
  if git rev-parse --verify --quiet "refs/remotes/$MERGE_TARGET" >/dev/null 2>&1; then
    exit 0
  fi
fi

if is_devops_center; then
  for p in $(protected); do
    if [ "$BRANCH" = "$p" ]; then
      block \
        "BLOCKED: '$BRANCH' is a DevOps Center-owned pipeline branch." \
        "" \
        "Local feature merges and escape hatches do not apply here. Push the WI branch," \
        "create its DevOps Center review, and let promotion perform the merge and deploy."
    fi
  done
fi

# Escape hatch.
if [ "${ALEY_ALLOW_LOCAL_MERGE:-}" = "1" ]; then
  record_hatch ALLOW_LOCAL_MERGE "$COMMAND"
  note "ESCAPE HATCH USED: local merge into '$TRUNK' on a $HOST-hosted repo." \
       "Recorded to the hatch-log. This bypasses the PR flow — document why on the ticket."
  exit 0
fi

# Build the host-specific example. These match workflow-steps.md step 4c exactly.
case "$HOST" in
  github) EXAMPLE=$(printf '  gh pr create --base %s --title "feat: description (<TICKET>)" --body "..."\n  gh pr merge --squash --delete-branch' "$TRUNK") ;;
  gitlab) EXAMPLE=$(printf '  glab mr create --target-branch %s --title "feat: description (<TICKET>)" --description "..."\n  glab mr merge --squash --remove-source-branch' "$TRUNK") ;;
  azure)  EXAMPLE=$(printf '  az repos pr create --target-branch %s --title "feat: description (<TICKET>)"\n  az repos pr update --id <N> --squash true --status completed' "$TRUNK") ;;
esac

TARGET_LABEL=""
[ -n "$MERGE_TARGET" ] && TARGET_LABEL=" ('$MERGE_TARGET')"

block \
  "BLOCKED: local 'git merge'${TARGET_LABEL} into '$TRUNK' on a $HOST-hosted repo." \
  "" \
  "This repo uses $HOST for code review and merge tracking. Landing a change with" \
  "a local 'git merge' + 'git push' bypasses the PR entirely: no review artifact," \
  "no merge record on $HOST, and the auto-label and closing-keyword guards lose the" \
  "PR they expect to find." \
  "" \
  "Use the PR flow instead (workflow-steps.md, step 4c):" \
  "" \
  "$EXAMPLE" \
  "" \
  "The PR is where the validate proof, the review, and the ticket reference all" \
  "live. A local merge discards that traceability even when you push it to the" \
  "remote afterwards." \
  "" \
  "Genuinely need to bypass? ALEY_ALLOW_LOCAL_MERGE=1 git merge ... and document" \
  "why on the ticket."
