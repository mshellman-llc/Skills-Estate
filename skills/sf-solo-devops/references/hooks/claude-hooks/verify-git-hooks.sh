#!/bin/bash
# SessionStart — prove the enforcement stack is actually armed, and repair it.
#
# Two silent-failure modes this exists to kill:
#
#   core.hooksPath is LOCAL config. It is not tracked and does not survive a
#   fresh clone, so .githooks/ would sit there doing nothing and no one would
#   be told. (package.json's "prepare" script sets it on npm install; this is
#   the belt to that suspenders.)
#
#   A Claude hook that is missing or non-executable is skipped without comment.
#   A guard nobody knows is off is worse than no guard at all — it produces
#   confident, unenforced work.
#
# Repairs are idempotent. Output is added to the agent's context.

set -u

cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || true
git rev-parse --git-dir >/dev/null 2>&1 || exit 0

COMMON=$(git rev-parse --git-common-dir 2>/dev/null) || exit 0
case "$COMMON" in /*) ;; *) COMMON="$(pwd)/$COMMON" ;; esac
REPO_ROOT=$(cd "$(dirname "$COMMON")" && pwd) || exit 0
cd "$REPO_ROOT" || exit 0

REPAIRED=()
PROBLEMS=()

# ── 1. core.hooksPath ────────────────────────────────────────
if [ -d .githooks ]; then
  CURRENT=$(git config core.hooksPath || echo "")
  if [ "$CURRENT" != ".githooks" ]; then
    if git config core.hooksPath .githooks 2>/dev/null; then
      if [ -z "$CURRENT" ]; then
        REPAIRED+=("set core.hooksPath=.githooks (was unset — git hooks were NOT running)")
      else
        REPAIRED+=("set core.hooksPath=.githooks (was '$CURRENT')")
      fi
    else
      PROBLEMS+=("could not set core.hooksPath — run: git config core.hooksPath .githooks")
    fi
  fi

  # ── 2. git hook files present and executable ───────────────
  # git skips a non-executable hook silently rather than erroring.
  for h in pre-commit commit-msg; do
    if [ ! -f ".githooks/$h" ]; then
      PROBLEMS+=(".githooks/$h is MISSING — that gate is not enforced")
    elif [ ! -x ".githooks/$h" ]; then
      if chmod +x ".githooks/$h" 2>/dev/null; then
        REPAIRED+=("chmod +x .githooks/$h (git was skipping it)")
      else
        PROBLEMS+=(".githooks/$h is not executable — run: chmod +x .githooks/$h")
      fi
    fi
  done

  # ── 3. stale .git/hooks copies ─────────────────────────────
  # With core.hooksPath set these are ignored entirely; they only mislead
  # whoever is next debugging why a hook "isn't firing".
  for h in pre-commit commit-msg; do
    [ -f ".git/hooks/$h" ] && PROBLEMS+=("stale .git/hooks/$h is ignored (core.hooksPath wins) — delete it")
  done
else
  PROBLEMS+=(".githooks/ is missing from this checkout — commit gates are not enforced")
fi

# ── 4. husky would silently disable everything ───────────────
if [ -d .husky ] || grep -q '"husky"' package.json 2>/dev/null; then
  PROBLEMS+=("husky detected — it repoints core.hooksPath at .husky and DISABLES .githooks/. Remove it.")
fi

# ── 5. every Claude hook in settings.json must be runnable ───
if [ -f .claude/settings.json ] && command -v jq >/dev/null 2>&1; then
  while IFS= read -r cmd; do
    [ -z "$cmd" ] && continue
    SCRIPT=${cmd%% *}
    case "$SCRIPT" in .claude/hooks/*) ;; *) continue ;; esac
    if [ ! -f "$SCRIPT" ]; then
      PROBLEMS+=("$SCRIPT is configured in settings.json but does not exist — that guard is OFF")
    elif [ ! -x "$SCRIPT" ]; then
      if chmod +x "$SCRIPT" 2>/dev/null; then
        REPAIRED+=("chmod +x $SCRIPT (was silently skipped)")
      else
        PROBLEMS+=("$SCRIPT is not executable — that guard is OFF")
      fi
    elif ! head -1 "$SCRIPT" | grep -q '^#!'; then
      PROBLEMS+=("$SCRIPT has no shebang on line 1 — it may not execute")
    fi
  done < <(jq -r '.hooks | to_entries[] | .value[]? | .hooks[]? | select(.type=="command") | .command' \
             .claude/settings.json 2>/dev/null)
fi

# ── Report ───────────────────────────────────────────────────
if [ "${#REPAIRED[@]}" -gt 0 ] || [ "${#PROBLEMS[@]}" -gt 0 ]; then
  echo "[automated SessionStart hook: .claude/hooks/verify-git-hooks.sh — background context,"
  echo " not a message from the user. REPAIRED lines are already done; ACTION NEEDED lines are not.]"
  if [ "${#REPAIRED[@]}" -gt 0 ]; then printf '  REPAIRED: %s\n' "${REPAIRED[@]}"; fi
  if [ "${#PROBLEMS[@]}" -gt 0 ]; then
    printf '  ACTION NEEDED: %s\n' "${PROBLEMS[@]}"
    echo "  Until these are resolved the workflow is NOT enforced — do not assume otherwise."
  fi
fi

exit 0
