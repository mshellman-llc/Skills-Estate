#!/bin/bash
# PreToolUse (Bash) — the merge gate. A change touching force-app/ may not land
# on trunk until that exact commit has passed a dry-run validate against the org.
#
# WHY THE ORDER IS VALIDATE-THEN-MERGE
# ------------------------------------
# Once the squash lands on trunk, trunk claims to describe the org. If the code
# then fails to deploy, trunk is ahead of the org and the invariant is already
# broken — the only repairs are fix-forward or revert. Validating first makes
# that state unreachable rather than recoverable.
#
# Proof comes from record-validate.sh, which logs the commit SHA of every
# successful `deploy start --dry-run`.
#
# HOST ADAPTERS (aleysian.host)
# -----------------------------
#   github     gh pr merge            — full gate: head SHA + files, both read
#   gitlab     glab mr merge          — full gate on the head SHA
#   azure      az repos pr update     — full gate on the head SHA
#   bitbucket  (no CLI merge surface)  — the gate CANNOT live here. guard-push.sh
#              enforces a green validate before the branch is pushed instead, so
#              whatever gets merged in their web UI was validated. This is a real
#              reduction in coverage, not an equivalent — say so, do not paper it.
#   none       git merge into trunk   — full gate: validate + a recorded human
#              approval from aleysian-merge (see bin/aleysian-merge)
#
# For the hosted flows the file list is a nice-to-have: when it can be read and
# shows no force-app/ paths, the gate stands aside. When it cannot be read, the
# gate requires the validate anyway. Failing closed on an unknown file list is
# the right default — the cost is one dry run, and the alternative is a silent
# unvalidated merge.
#
# Fails OPEN when the host CLI is absent or the remote is unreachable: an offline
# tool should not stop work, and the deploy-side guards still protect the org.
#
# Escape hatch (deliberate, visible, recorded): ALEY_ALLOW_UNVALIDATED_MERGE=1
# (SW_/SOLO_ prefixes still work — a documented override that silently does
# nothing looks like a broken gate, and gates that look broken get removed).

set -u
HOOK_EVENT="PreToolUse"
HOOK_DEFER_GATE=1   # the master gate fires in hook_read_input, once the target repo is known
. "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

# ── The PR/MR number this command names ──────────────────────
#
# ONE implementation, because there were four copies of the extraction and the same
# bug in all of them:
#
#   sed -E 's/.*\bgh[[:space:]]+pr[[:space:]]+merge[[:space:]]*//'
#
# BSD sed — the macOS default — has no \b. The substitution never matched, so the
# command came through unchanged, `awk '{print $1}'` yielded "gh", and the trailing
# numeric grep produced nothing. Every caller then ran `gh pr view` with NO id, which
# resolves the CURRENT BRANCH's PR — a different PR than the one being merged — or
# fails and takes an `exit 0` fall-through.
#
# It worked under GNU sed, which is what hid it: correct in Linux CI, inert on every
# developer machine. Nothing reported it, because "could not read the base" and
# "gated a different PR" both look like success.
#
# if/elif rather than `case`: this is called from $(), and bash 3.2 cannot parse a
# case inside a command substitution — see the note in scripts/audit.sh.
merge_target_id() {
  if [ "${1:-}" = "glab" ]; then
    printf '%s' "$COMMAND" \
      | grep -oE 'glab[[:space:]]+mr[[:space:]]+merge[[:space:]]+[0-9]+' \
      | grep -oE '[0-9]+$' | head -1
  else
    printf '%s' "$COMMAND" \
      | grep -oE 'gh[[:space:]]+pr[[:space:]]+merge[[:space:]]+[0-9]+' \
      | grep -oE '[0-9]+$' | head -1
  fi
}

squash_example() {
  case "$(host)" in
    github) printf 'gh pr merge --squash --delete-branch' ;;
    gitlab) printf 'glab mr merge --squash --remove-source-branch' ;;
    azure)  printf 'az repos pr update --id <N> --squash true --status completed' ;;
    none)   printf 'aleysian-merge <branch>   # does the squash for you' ;;
    *)      printf 'merge with --squash' ;;
  esac
}

hook_read_input
COMMAND=$(hook_command_text)
HOST=$(host)
TRUNK=$(trunk)

# ── Is this a merge, on this host's surface? ──────────────────
IS_MERGE=0
case "$HOST" in
  github) echo "$COMMAND" | grep -qE '\bgh[[:space:]]+pr[[:space:]]+merge\b' && IS_MERGE=1 ;;
  gitlab) echo "$COMMAND" | grep -qE '\bglab[[:space:]]+mr[[:space:]]+merge\b' && IS_MERGE=1 ;;
  azure)  echo "$COMMAND" | grep -qE '\baz[[:space:]]+repos[[:space:]]+pr[[:space:]]+(update|complete)\b' && IS_MERGE=1 ;;
  bitbucket)
    # Nothing to intercept. But an agent reaching for `gh pr merge` in a
    # Bitbucket repo has the wrong model of this project, so say so once.
    if echo "$COMMAND" | grep -qE '\bgh[[:space:]]+pr[[:space:]]+merge\b'; then
      block \
        "BLOCKED: this repo's host is Bitbucket (aleysian.host=bitbucket) — there is no" \
        "gh PR to merge, and no CLI merge surface at all." \
        "" \
        "The merge happens in Bitbucket's web UI, by a human. What this stack enforces" \
        "instead is that nothing reaches the remote unvalidated: guard-push.sh requires a" \
        "recorded green dry run before 'git push' of a branch that touches force-app/." \
        "" \
        "So: validate -> push -> open and merge the PR in the browser -> deploy from" \
        "'$TRUNK'. The deploy guard still refuses a dirty or unsynced trunk."
    fi
    exit 0 ;;
  none)
    # The landing step is a local squash merge INTO trunk. Merges into anything
    # else (syncing trunk down into a feature branch) are ordinary work.
    if echo "$COMMAND" | grep -qE '(^|[;&|][[:space:]]*)git[[:space:]]+([^|;&]*[[:space:]])?merge\b'; then
      [ "$(current_branch ".")" = "$TRUNK" ] && IS_MERGE=1
    fi ;;
esac
[ "$IS_MERGE" = "0" ] && exit 0

# ── Protected branches (aleysian.protected) ──────────────────
#
# Checked BEFORE the validate hatch, deliberately. ALEY_ALLOW_UNVALIDATED_MERGE
# says "I accept the risk of merging without a dry run"; it does not say "I may
# merge into a branch this clone was told to stay out of". Those are different
# decisions and one must not silently grant the other.
#
# Empty by default, so a repo that never sets the key reaches none of this.
PROTECTED=$(protected)
if [ -n "$PROTECTED" ]; then
  BASE=""
  case "$HOST" in
    github)
      if command -v gh >/dev/null 2>&1; then
        PR_ARG=$(merge_target_id gh)
        [ -n "$PR_ARG" ] && BASE=$(gh pr view "$PR_ARG" --json baseRefName -q .baseRefName 2>/dev/null || true)
      fi ;;
    gitlab)
      if command -v glab >/dev/null 2>&1; then
        MR_ARG=$(merge_target_id glab)
        [ -n "$MR_ARG" ] && BASE=$(glab mr view "$MR_ARG" -F json 2>/dev/null | jq -r '.target_branch // empty' || true)
      fi ;;
    azure)
      if command -v az >/dev/null 2>&1; then
        AZ_ID=$(echo "$COMMAND" | grep -oE -- '--id[[:space:]=]+[0-9]+' | grep -oE '[0-9]+$' | head -1)
        [ -n "$AZ_ID" ] && BASE=$(az repos pr show --id "$AZ_ID" 2>/dev/null \
          | jq -r '.targetRefName // empty' | sed 's#^refs/heads/##' || true)
      fi ;;
    none)
      # `git merge` only reached IS_MERGE=1 while standing on trunk, so trunk is
      # the base by construction.
      BASE="$TRUNK" ;;
  esac

  # An unreadable base is not a pass — and until now this said so in a comment while
  # doing the opposite. It emitted a note and fell through to allow, which is the
  # definition of failing open, in the one check whose whole purpose is that the
  # branches on the list are the expensive ones to get wrong.
  #
  # That is doubly bad in combination with the sed bug above: BASE was empty on every
  # Mac, so this branch was not an edge case, it was the ONLY path. `aleysian.protected`
  # was inert while reporting itself configured.
  #
  # So it blocks. The cost of a false block here is one conversation; the cost of a
  # false pass is an agent merging into production.
  #
  # Deliberately NOT covered by ALEY_ALLOW_UNVALIDATED_MERGE — see the note above.
  # That hatch says "I accept merging without a dry run", not "I may merge into a
  # branch this clone was told to stay out of".
  if [ -z "$BASE" ]; then
    block \
      "BLOCKED: cannot determine this merge's target branch, and this clone has" \
      "protected branches: $PROTECTED" \
      "" \
      "The check that keeps merges out of those branches could not evaluate, so this" \
      "is refused rather than assumed safe. Nothing here says the merge IS wrong —" \
      "only that it could not be shown to be right." \
      "" \
      "Usually one of:" \
      "  - the merge names its PR indirectly (a URL, a variable, a branch name)." \
      "    Name the number instead:  gh pr merge <N> --merge" \
      "  - the host CLI is unauthenticated or the remote is unreachable." \
      "    Check with:  gh pr view <N> --json baseRefName" \
      "" \
      "If the target is genuinely not one of [$PROTECTED], re-run naming the PR number" \
      "and this will pass."
  else
    for p in $PROTECTED; do
      if [ "$BASE" = "$p" ]; then
        if is_devops_center; then
          block \
            "BLOCKED: '$BASE' is a DevOps Center stage branch." \
            "" \
            "Merges into it are not this session's to make. Push the validated WI" \
            "branch, create the DevOps Center review, and use dx-devops-promote." \
            "DevOps Center owns the merge, deployment, and promotion record." \
            "" \
            "Protected in this clone: $PROTECTED"
        fi
        block \
          "BLOCKED: '$BASE' is a protected branch (aleysian.protected)." \
          "" \
          "Merges into it are not this session's to make. Something else owns what" \
          "lands there — a deploy pipeline, a release process, or a human with the" \
          "context to decide. Protected in this clone: $PROTECTED" \
          "" \
          "If this repo has a deploy engine, promotion is its job: build a release" \
          "instead of merging by hand, so the promotion is recorded and revertible." \
          "" \
          "Genuinely need to merge here yourself? That is a decision to make out loud," \
          "with whoever owns the branch — not one to route around with a hatch."
      fi
    done
  fi
fi

if [ "${ALEY_ALLOW_UNVALIDATED_MERGE:-}" = "1" ] || [ "${SW_ALLOW_UNVALIDATED_MERGE:-}" = "1" ] \
   || [ "${SOLO_ALLOW_UNVALIDATED_MERGE:-}" = "1" ]; then
  record_hatch ALLOW_UNVALIDATED_MERGE "$COMMAND"
  note "ESCAPE HATCH USED: the validate-before-merge gate was skipped for this merge." \
       "Recorded to the hatch-log. Say so on the ticket — a merge with no recorded dry" \
       "run is the one case where '$TRUNK' can end up ahead of the org unnoticed."
  exit 0
fi

# ── Squash policy ────────────────────────────────────────────
#
# One ticket, one commit on trunk: a merge commit or a rebase scatters the ticket
# refs that auto-label-deploy.sh reads back out of history, and proof-of-deploy is
# tracked per squashed commit.
#
# HARD in native mode. In stealth mode it is advisory by default, because merge
# strategy in a client's repo is THEIR policy and a vendor tool overriding it is
# out of line — init asks, and aleysian.squash records the answer.
HAS_SQUASH=1
case "$HOST" in
  github|gitlab) echo "$COMMAND" | grep -qE -- '(--squash|(^|[[:space:]])-s([[:space:]]|$))' || HAS_SQUASH=0 ;;
  azure)         echo "$COMMAND" | grep -qE -- '--squash' || HAS_SQUASH=0 ;;
  none)          echo "$COMMAND" | grep -qE -- '--squash' || HAS_SQUASH=0 ;;
esac

# `merge` inverts the rule rather than relaxing it. A repo whose promotion model
# cherry-picks merge commits (-m 1) and reverts them (-m 1) needs the merge commit
# to exist; squashing there is not a style difference, it removes the structure
# both operations run on, and it does so silently — the damage is only visible
# later, when a rollback or a selective promotion turns out to be impossible.
if [ "$(squash_policy)" = "merge" ]; then
  if [ "$HAS_SQUASH" = "1" ]; then
    block \
      "BLOCKED: this repo lands MERGE COMMITS, not squashes (aleysian.squash=merge)." \
      "" \
      "  gh pr merge <N> --merge --delete-branch" \
      "" \
      "Selective promotion cherry-picks merge commits (git cherry-pick -m 1) and" \
      "rollback reverts them (git revert -m 1). Both need a real merge commit with" \
      "two parents. A squashed merge is neither selectively promotable nor cleanly" \
      "revertible, and nothing detects that until the day you need one of them." \
      "" \
      "Disable it at the repo level too, so the web UI button agrees:" \
      "  gh api repos/<owner>/<repo> -X PATCH -f allow_squash_merge=false -f allow_rebase_merge=false"
  fi
  # Rebase merges destroy the merge commit just as thoroughly.
  if echo "$COMMAND" | grep -qE -- '--rebase'; then
    block \
      "BLOCKED: --rebase produces no merge commit (aleysian.squash=merge)." \
      "" \
      "  gh pr merge <N> --merge --delete-branch" \
      "" \
      "See above: cherry-pick -m 1 and revert -m 1 both need the merge commit."
  fi
  SQUASH_OK=1
else
  SQUASH_OK=$HAS_SQUASH
fi

if [ "$SQUASH_OK" = "0" ]; then
  if [ "$(squash_policy)" = "require" ]; then
    block \
      "BLOCKED: merge with --squash." \
      "" \
      "  $(squash_example)" \
      "" \
      "'$TRUNK' carries one commit per ticket. A merge or rebase spreads the ticket" \
      "reference across commits, and proof-of-deploy is tracked per squashed commit." \
      "" \
      "The client's repo policy forbids squash? That is a config answer, not a bypass:" \
      "  git config aleysian.squash prefer"
  else
    note "Merging without --squash (aleysian.squash=prefer, so this is allowed)." \
         "One consequence to know about: the ticket reference will be spread across" \
         "several commits on '$TRUNK', so auto-label-deploy.sh may associate the deploy" \
         "with fewer tickets than you expect."
  fi
fi

# ── host=none: a human must have approved this diff ──────────
#
# Replicates the PR's FUNCTION (someone looked at the diff before it counted)
# without a remote. bin/aleysian-merge is the green button: a person runs it, it
# shows the diff, checks the validate, does the squash, and records the approval.
# Reaching `git merge` directly means that never happened.
if [ "$HOST" = "none" ]; then
  ALOG=$(approve_log ".")
  HEAD_SHA=""
  BR=$(printf '%s' "$COMMAND" | sed -nE 's/.*git[[:space:]]+([^|;&]*[[:space:]])?merge[[:space:]]+(--squash[[:space:]]+)?([^[:space:]-][^[:space:]]*).*/\3/p' | head -1)
  [ -n "$BR" ] && HEAD_SHA=$(git rev-parse --verify --quiet "$BR" 2>/dev/null || echo "")

  if [ -z "$HEAD_SHA" ]; then
    note "Could not tell which branch is being merged, so the approval check was skipped." \
         "If this is the landing step for a ticket, use: aleysian-merge <branch>"
    exit 0
  fi
  if ! grep -q "^${HEAD_SHA}[[:space:]]" "$ALOG" 2>/dev/null; then
    block \
      "BLOCKED: no recorded human approval for ${HEAD_SHA:0:8} (branch '$BR')." \
      "" \
      "This repo has no remote (aleysian.host=none), so there is no PR to review." \
      "The local review gate stands in for it — run it instead of git merge:" \
      "" \
      "  aleysian-merge $BR" \
      "" \
      "It shows you the diff, verifies the dry run, performs the squash with the right" \
      "ticket reference, and records who approved what. Without that record there is no" \
      "evidence any human ever read this diff, which is the one thing a PR guarantees." \
      "" \
      "Worth saying out loud: local-only mode gives up a second reviewer, off-machine" \
      "backup, and a durable review artifact. If the client will allow a private remote," \
      "that is strictly better than this."
  fi
fi

# ── Which commit is landing? ─────────────────────────────────
HEAD_SHA=""
TOUCHES_FORCE_APP="unknown"

case "$HOST" in
  github)
    command -v gh >/dev/null 2>&1 || exit 0
    PR_ARG=$(merge_target_id gh)
    # `gh pr merge` with no PR id merges the CURRENT branch's PR — so `gh pr view`
    # with no id resolves the very PR being merged, not a different one. $PR_ARG is
    # left UNQUOTED on purpose: an empty value collapses to `gh pr view` (current
    # branch) and a present id gates that id. This is how the original gate enforced
    # the documented `gh pr merge --squash --delete-branch` (no number); bailing on
    # an empty id instead skipped the validate gate on the entire happy path, which
    # on GitHub — where this is the only interception point — is unenforced merges.
    # A branch with genuinely no PR makes gh error, and we stand aside at || exit 0.
    # shellcheck disable=SC2086
    PR_JSON=$(gh pr view $PR_ARG --json number,headRefOid,files 2>/dev/null) || exit 0
    [ -z "$PR_JSON" ] && exit 0
    PR_ID=$(echo "$PR_JSON" | jq -r '.number // empty')
    HEAD_SHA=$(echo "$PR_JSON" | jq -r '.headRefOid // empty')
    # `[.files[]?.path | ... ] | length` returns 0 for BOTH "no force-app path"
    # AND ".files absent/null/unreadable" (an API hiccup, or pagination truncating
    # the file list on a very large PR) — because `.files[]?` swallows the missing
    # array. Those are opposite verdicts. Establish the file list is a present array
    # FIRST; only then is a length of 0 the real "touches nothing deployable" that
    # earns the exit-0 shortcut below. When it is not an array the count stays
    # "unknown", and the validate gate is required — the header promises exactly
    # this: "When it cannot be read, the gate requires the validate anyway."
    HAS_FILES=$(echo "$PR_JSON" | jq -r 'if (.files|type)=="array" then "yes" else "no" end')
    if [ "$HAS_FILES" = "yes" ]; then
      TOUCHES_FORCE_APP=$(echo "$PR_JSON" | jq -r '[.files[]?.path | select(startswith("force-app/"))] | length')
    else
      TOUCHES_FORCE_APP="unknown"
    fi
    ;;
  gitlab)
    command -v glab >/dev/null 2>&1 || exit 0
    MR_ARG=$(merge_target_id glab)
    [ -z "$MR_ARG" ] && exit 0
    MR_JSON=$(glab mr view "$MR_ARG" -F json 2>/dev/null) || exit 0
    [ -z "$MR_JSON" ] && exit 0
    PR_ID=$(echo "$MR_JSON" | jq -r '.iid // empty')
    HEAD_SHA=$(echo "$MR_JSON" | jq -r '.diff_refs.head_sha // .sha // empty')
    ;;
  azure)
    command -v az >/dev/null 2>&1 || exit 0
    PR_ID=$(echo "$COMMAND" | grep -oE -- '--id[[:space:]=]+[0-9]+' | grep -oE '[0-9]+$' | head -1)
    [ -z "$PR_ID" ] && exit 0
    HEAD_SHA=$(az repos pr show --id "$PR_ID" 2>/dev/null \
      | jq -r '.lastMergeSourceCommit.commitId // empty')
    ;;
  none)
    PR_ID="local"
    ;;
esac

[ -z "$HEAD_SHA" ] && exit 0
# The file list was readable AND held nothing deployable: no org validate is
# meaningful. "unknown" is not zero — see the header.
[ "$TOUCHES_FORCE_APP" = "0" ] && exit 0

VLOG=$(validate_log ".")
grep -q "^${HEAD_SHA}[[:space:]]" "$VLOG" 2>/dev/null && exit 0

VALIDATED_HINT="No validates have been recorded for this clone yet."
if [ -f "$VLOG" ]; then
  LAST=$(read_log_reverse "$VLOG" | head -1)
  [ -n "$LAST" ] && VALIDATED_HINT="Most recent recorded validate: $LAST"
fi

PUSHED_NOTE="Also confirm the branch is pushed: the host reads the remote tip, not your disk."
[ "$HOST" = "none" ] && PUSHED_NOTE="There is no remote here, so the SHA is read straight from the branch."

block \
  "BLOCKED: ${PR_ID:-this change} touches force-app/ but commit ${HEAD_SHA:0:8} has no" \
  "recorded validate." \
  "" \
  "Run the merge gate from the worktree first:" \
  "  sf project deploy start --dry-run \\" \
  "    --source-dir <each changed file> \\" \
  "    --test-level RunSpecifiedTests --tests <TestClasses>" \
  "" \
  "$VALIDATED_HINT" \
  "" \
  "Validated an earlier commit and then pushed another? Re-validate — the gate is" \
  "per-commit on purpose. $PUSHED_NOTE" \
  "" \
  "Genuinely not validatable (org down, etc.)? Prefix the merge with" \
  "ALEY_ALLOW_UNVALIDATED_MERGE=1 and say so on the ticket."
