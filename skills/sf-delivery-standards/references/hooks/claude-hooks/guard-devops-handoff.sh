#!/bin/bash
# PreToolUse (Bash) - gate the point where a WI is handed to DevOps Center.

set -u
HOOK_EVENT="PreToolUse"
HOOK_DEFER_GATE=1
. "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

hook_read_input
is_devops_center || exit 0
COMMAND=$(hook_command_text)

IS_GH=0; IS_SF=0
echo "$COMMAND" | grep -qE '\bgh[[:space:]]+pr[[:space:]]+create\b' && IS_GH=1
echo "$COMMAND" | grep -qE '\bsf[[:space:]]+devops[[:space:]]+review[[:space:]]+create\b' && IS_SF=1
[ "$IS_GH" = "1" ] || [ "$IS_SF" = "1" ] || exit 0

BRANCH=$(current_branch ".")

IS_SHARED_DEV=0
if is_devops_shared && printf '%s\n' "$BRANCH" | grep -qE "$(devops_development_branch_pattern)"; then
  IS_SHARED_DEV=1
fi

require_persistent_branch() { # branch
  local branch="$1" status_bin status rc
  status_bin="$(cd "$(dirname "${BASH_SOURCE[0]}")/../bin" 2>/dev/null && pwd)/estate-devops-branch-status"
  status=$("$status_bin" --branch "$branch" 2>&1); rc=$?
  [ "$rc" -eq 0 ] || block \
    "BLOCKED: pipeline branch '$branch' is not proven persistent on GitHub." \
    "" \
    "$status" \
    "" \
    "A missing or deletable stage branch can turn a later DevOps Center promotion" \
    "into an empty or broken transition. Protect it with deletion disabled first."
}

if [ "$IS_SHARED_DEV" = "0" ]; then
  printf '%s\n' "$BRANCH" | grep -qE "$(devops_branch_pattern)" || block \
    "BLOCKED: DevOps Center review creation must run from its WI packaging branch." \
    "" \
    "Current branch: ${BRANCH:-unknown}" \
    "Expected pattern: $(devops_branch_pattern)"
fi

in_worktree "." || block \
  "BLOCKED: create the DevOps Center review from the linked WI worktree." \
  "" \
  "The worktree is the boundary that keeps WI source separate from pipeline branches."

DIRTY=$(git status --porcelain -- force-app/ 2>/dev/null)
[ -z "$DIRTY" ] || block \
  "BLOCKED: commit all WI source before creating its DevOps Center review." \
  "" \
  "$DIRTY"

HEAD_SHA=$(git rev-parse HEAD 2>/dev/null || echo "")
VLOG=$(validate_log ".")
[ -n "$HEAD_SHA" ] && grep -q "^${HEAD_SHA}[[:space:]]" "$VLOG" 2>/dev/null || block \
  "BLOCKED: validate the current WI commit before creating its review." \
  "" \
  "Current HEAD: ${HEAD_SHA:-unknown}" \
  "Run the scoped sf project deploy start --dry-run from this worktree first."

if [ "$IS_SHARED_DEV" = "1" ]; then
  [ "$IS_GH" = "1" ] || block \
    "BLOCKED: the dev/WI branch first needs a GitHub PR to the shared integration branch." \
    "" \
    "DevOps Center review creation belongs to the generated WI-###### packaging branch."
  INTEGRATION=$(devops_integration_branch)
  echo "$COMMAND" | grep -qE -- "--base(=|[[:space:]]+)${INTEGRATION}([[:space:]]|$)" || block \
    "BLOCKED: the shared-sandbox development PR must explicitly target '$INTEGRATION'." \
    "" \
    "Use: gh pr create --base $INTEGRATION ..."
  require_persistent_branch "$INTEGRATION"
  STATUS_BIN="$(cd "$(dirname "${BASH_SOURCE[0]}")/../bin" 2>/dev/null && pwd)/estate-devops-shared-status"
  STATUS=$("$STATUS_BIN" 2>&1); STATUS_RC=$?
  [ "$STATUS_RC" -eq 0 ] || block \
    "BLOCKED: the shared development branch is not proven deployed." \
    "" \
    "$STATUS" \
    "" \
    "Repair the centralized deployment receipt before opening another landing PR."
  exit 0
fi

if is_devops_shared; then
  require_persistent_branch "$(trunk)"
  LEDGER=".estate/work-items/$BRANCH.json"
  [ -f "$LEDGER" ] || block \
    "BLOCKED: the WI packaging branch has no scope ledger." \
    "" \
    "Run: estate-devops-package --development-branch dev/$BRANCH" \
    "Then review, commit, and validate the exact packaged delta."
  jq -e --arg wi "$BRANCH" --arg landing "$(trunk)" \
    '.schemaVersion == 1 and .workItem == $wi and .packagingBranch == $wi and .landingBranch == $landing and (.files|type == "array") and (.metadataMembers|type == "array")' \
    "$LEDGER" >/dev/null 2>&1 || block \
      "BLOCKED: $LEDGER does not describe this packaging branch and landing branch."

  PACKAGE_BASE=$(jq -r '.packagingBase // empty' "$LEDGER")
  git cat-file -e "${PACKAGE_BASE}^{commit}" 2>/dev/null || block \
    "BLOCKED: the scope ledger's packaging base does not resolve: ${PACKAGE_BASE:-missing}."
  ACTUAL=$(git diff --name-only "$PACKAGE_BASE" HEAD -- . ':(exclude).estate/work-items/**' | LC_ALL=C sort)
  EXPECTED=$(jq -r '.files[].path' "$LEDGER" | LC_ALL=C sort)
  [ "$ACTUAL" = "$EXPECTED" ] || block \
    "BLOCKED: the packaging branch file set differs from the recorded WI scope." \
    "" \
    "Recorded:" \
    "$EXPECTED" \
    "" \
    "Actual:" \
    "$ACTUAL" \
    "" \
    "Re-run estate-devops-package from a clean generated WI branch."

  while IFS=$'\t' read -r PATH_NAME SOURCE_BLOB; do
    [ -n "$PATH_NAME" ] || continue
    if [ "$SOURCE_BLOB" = "null" ]; then
      [ ! -e "$PATH_NAME" ] || block "BLOCKED: '$PATH_NAME' was recorded as deleted but exists in the package."
    else
      CURRENT_BLOB=$(git rev-parse "HEAD:$PATH_NAME" 2>/dev/null || echo "")
      [ "$CURRENT_BLOB" = "$SOURCE_BLOB" ] || block \
        "BLOCKED: packaged '$PATH_NAME' is not byte-identical to the accepted development file."
    fi
  done <<EOF
$(jq -r '.files[] | [.path, (.sourceBlob // "null")] | @tsv' "$LEDGER")
EOF

  STATUS_BIN="$(cd "$(dirname "${BASH_SOURCE[0]}")/../bin" 2>/dev/null && pwd)/estate-devops-shared-status"
  STATUS_JSON=$("$STATUS_BIN" --json 2>/dev/null); STATUS_RC=$?
  [ "$STATUS_RC" -eq 0 ] || block \
    "BLOCKED: the shared development branch no longer has a current successful deployment receipt."
  DEPLOYED_SHA=$(printf '%s' "$STATUS_JSON" | jq -r '.deployedSha // empty')
  while IFS=$'\t' read -r PATH_NAME SOURCE_BLOB; do
    [ -n "$PATH_NAME" ] || continue
    DEPLOYED_BLOB=$(git rev-parse "$DEPLOYED_SHA:$PATH_NAME" 2>/dev/null || echo "null")
    [ "$DEPLOYED_BLOB" = "$SOURCE_BLOB" ] || block \
      "BLOCKED: shared component overlap changed '$PATH_NAME' after this WI was accepted." \
      "" \
      "Promote the predecessor first, preserve dependency order, or explicitly combine" \
      "the WIs. Do not copy the current sandbox file into this package."
  done <<EOF
$(jq -r '.files[] | [.path, (.sourceBlob // "null")] | @tsv' "$LEDGER")
EOF
fi

if [ "$IS_GH" = "1" ]; then
  TRUNK=$(trunk)
  echo "$COMMAND" | grep -qE -- "--base(=|[[:space:]]+)${TRUNK}([[:space:]]|$)" || block \
    "BLOCKED: the WI pull request must explicitly target '$TRUNK'." \
    "" \
    "Use: gh pr create --base $TRUNK ..." \
    "Do not rely on the repository default branch for a DevOps Center handoff."
fi

exit 0
