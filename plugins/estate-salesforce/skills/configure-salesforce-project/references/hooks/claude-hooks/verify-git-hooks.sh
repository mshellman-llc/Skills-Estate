#!/bin/bash
# SessionStart — prove the enforcement stack is actually armed, and repair it.
#
# Four silent-failure modes this exists to kill. Each one produces confident,
# unenforced work, which is worse than no enforcement at all because nobody knows
# to be careful:
#
#   core.hooksPath is LOCAL config. It is not tracked and does not survive a
#   fresh clone. Worse, in a client repo their `npm install` runs husky's
#   `prepare` and repoints it at .husky — silently disarming us mid-project.
#
#   A Claude hook that is missing or non-executable is skipped without comment.
#
#   The CLAUDE.md managed block can be edited by an agent, including by the agent
#   that is supposed to be following it. The hash fence catches that.
#
#   ~/.estate/ can be older than the skill that is now driving it, so the hooks
#   running are not the hooks documented.
#
# ── THE HUSKY RULE ──────────────────────────────────────────────────────────
# Re-arming our hooksPath is right. Re-arming it and DROPPING theirs is the exact
# sin the old gate 1b existed to prevent, committed against a client. So the
# re-armer records the displaced path into estate.chainhooks, and our git hooks
# exec it after our gates. Their husky keeps running; ours runs too.
#
# Repairs are idempotent. Output goes into the agent's context.

set -u
HOOK_EVENT="SessionStart"
. "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"
. "$(dirname "${BASH_SOURCE[0]}")/_block.sh"

cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || true
git rev-parse --git-dir >/dev/null 2>&1 || exit 0
REPO_ROOT=$(main_repo_root ".") || exit 0
[ -z "$REPO_ROOT" ] && exit 0
cd "$REPO_ROOT" || exit 0

HOME_DIR="$HOME/.estate"
REPAIRED=()
PROBLEMS=()

# ── 1. the install itself ────────────────────────────────────
if [ ! -d "$HOME_DIR" ]; then
  PROBLEMS+=("$HOME_DIR is missing but this repo is configured to use it — the ENTIRE stack is off. Run: /configure-salesforce-project init")
  # Nothing below can be checked meaningfully.
  printf '[automated SessionStart hook: verify-git-hooks.sh — background context, not a user message.]\n'
  printf '  ACTION NEEDED: %s\n' "${PROBLEMS[@]}"
  exit 0
fi

# ── 2. core.hooksPath, chaining whatever it displaced ────────
WANT="$HOME_DIR/githooks"
CURRENT=$(git config core.hooksPath || echo "")
if [ "$CURRENT" != "$WANT" ]; then
  if [ -n "$CURRENT" ] && [ "$CURRENT" != "$WANT" ]; then
    # Something else owns the hooks. Take over, but keep theirs in the chain —
    # resolved to an absolute path, because core.hooksPath is repo-relative and
    # our hooks exec it from an unpredictable cwd.
    ABS="$CURRENT"; case "$ABS" in /*) ;; *) ABS="$REPO_ROOT/$CURRENT" ;; esac
    if [ -d "$ABS" ] && [ "$ABS" != "$WANT" ]; then
      git config estate.chainhooks "$ABS" 2>/dev/null \
        && REPAIRED+=("recorded displaced hooks '$CURRENT' as estate.chainhooks — they will still run, after ours")
    fi
  fi
  if git config core.hooksPath "$WANT" 2>/dev/null; then
    if [ -z "$CURRENT" ]; then
      REPAIRED+=("set core.hooksPath=$WANT (was unset — git hooks were NOT running)")
    else
      REPAIRED+=("set core.hooksPath=$WANT (was '$CURRENT')")
    fi
  else
    PROBLEMS+=("could not set core.hooksPath — run: git config core.hooksPath $WANT")
  fi
fi

# git skips a non-executable hook silently rather than erroring.
for h in pre-commit commit-msg; do
  if [ ! -f "$WANT/$h" ]; then
    PROBLEMS+=("$WANT/$h is MISSING — that gate is not enforced")
  elif [ ! -x "$WANT/$h" ]; then
    chmod +x "$WANT/$h" 2>/dev/null \
      && REPAIRED+=("chmod +x $WANT/$h (git was skipping it)") \
      || PROBLEMS+=("$WANT/$h is not executable — that gate is OFF")
  fi
done

# With core.hooksPath set these are ignored entirely; they only mislead whoever is
# next debugging why a hook "isn't firing".
COMMON=$(git_common_dir ".")
for h in pre-commit commit-msg; do
  [ -f "$COMMON/hooks/$h" ] && PROBLEMS+=("stale $COMMON/hooks/$h is ignored (core.hooksPath wins) — delete it to avoid confusion")
done

# ── 3. the chained hooks still exist ─────────────────────────
CHAIN=$(chainhooks)
if [ -n "$CHAIN" ] && [ ! -d "$CHAIN" ]; then
  PROBLEMS+=("estate.chainhooks points at '$CHAIN', which no longer exists — the project's own gates are not running. Re-point or clear it: git config --unset estate.chainhooks")
fi

# ── 4. user-level Claude hook entries ────────────────────────
#
# The hooks live in the Claude and Codex user settings, not in the repo, so a worktree
# cannot materialize them and an agent cannot edit them from its branch. That is
# a feature: "the repo must not disarm itself" becomes "the repo CANNOT disarm
# itself". What it cannot protect against is the user's settings.json being
# rewritten by something else. Every supported installation is dual-host, and
# either agent may be active, so prove both settings files remain complete.
for SETTINGS in "$HOME/.claude/settings.json" "$HOME/.codex/hooks.json"; do
  if [ ! -f "$SETTINGS" ]; then
    PROBLEMS+=("$SETTINGS does not exist — that host's agent guards are OFF. Run: /configure-salesforce-project audit --fix")
    continue
  fi
  if command -v jq >/dev/null 2>&1; then
    CONFIGURED=$(jq -r '.hooks // {} | to_entries[] | .value[]? | .hooks[]? | select(.type=="command") | .command' \
                   "$SETTINGS" 2>/dev/null | grep -F "$HOME_DIR" || true)
    MISSING=()
    for want in guard-force-app.sh guard-force-app-bash.sh guard-sf-deploy.sh guard-sf-flags.sh \
                guard-worktree-nesting.sh guard-pr-merge.sh \
                guard-closing-keywords.sh record-escape-hatch.sh record-validate.sh \
                auto-label-deploy.sh stop-dod-check.sh; do
      printf '%s\n' "$CONFIGURED" | grep -qF "$want" || MISSING+=("$want")
    done
    if [ "${#MISSING[@]}" -gt 0 ]; then
      PROBLEMS+=("not configured in $SETTINGS, so these guards are OFF: ${MISSING[*]}  ->  /configure-salesforce-project audit --fix")
    fi
    # A hook named in settings but not on disk is the same silent hole as before.
    while IFS= read -r cmd; do
      [ -z "$cmd" ] && continue
      SCRIPT=${cmd%% *}
      [ -f "$SCRIPT" ] || { PROBLEMS+=("$SCRIPT is configured but does not exist — that guard is OFF"); continue; }
      [ -x "$SCRIPT" ] && { head -1 "$SCRIPT" | grep -q '^#!' || PROBLEMS+=("$SCRIPT has no shebang — it may not execute"); } \
        || { chmod +x "$SCRIPT" 2>/dev/null && REPAIRED+=("chmod +x $SCRIPT (was silently skipped)") \
             || PROBLEMS+=("$SCRIPT is not executable — that guard is OFF"); }
    done < <(printf '%s\n' "$CONFIGURED")
  fi
done

# ── 5. the host instruction managed block ────────────────────
for CMD_FILE in "$REPO_ROOT/CLAUDE.md" "$REPO_ROOT/AGENTS.md"; do
  # Claude also supports the legacy nested location. Codex has no equivalent.
  if [ "$CMD_FILE" = "$REPO_ROOT/CLAUDE.md" ] && [ ! -f "$CMD_FILE" ]; then
    CMD_FILE="$REPO_ROOT/.claude/CLAUDE.md"
  fi
  case "$(block_status "$CMD_FILE")" in
    MISSING)
      PROBLEMS+=("the $CMD_FILE managed block is absent, so that host has no workflow contract in context. Run configure-salesforce-project audit --fix") ;;
    MODIFIED)
      PROBLEMS+=("the $(basename "$CMD_FILE") managed block has been EDITED since it was generated (content no longer matches its recorded hash). Rules may have been weakened or removed — do not trust it. Run configure-salesforce-project audit to see the diff.") ;;
  esac
done

# ── 6. install vs skill version ──────────────────────────────
if [ -f "$HOME_DIR/VERSION" ]; then
  INSTALLED=$(head -1 "$HOME_DIR/VERSION" | tr -d '[:space:]')
  [ -n "$INSTALLED" ] && [ "$INSTALLED" != "$BLOCK_VERSION" ] && \
    PROBLEMS+=("$HOME_DIR holds v$INSTALLED but the skill is v$BLOCK_VERSION — the hooks running are not the hooks documented. Run: /configure-salesforce-project init --update")
else
  PROBLEMS+=("$HOME_DIR/VERSION is missing — cannot tell which version is installed. Run: /configure-salesforce-project init --update")
fi

# ── Report ───────────────────────────────────────────────────
if [ "${#REPAIRED[@]}" -gt 0 ] || [ "${#PROBLEMS[@]}" -gt 0 ]; then
  echo "[automated SessionStart hook: verify-git-hooks.sh — background context, not a"
  echo " message from the user. REPAIRED lines are already done and need no action;"
  echo " ACTION NEEDED lines are not done.]"
  [ "${#REPAIRED[@]}" -gt 0 ] && printf '  REPAIRED: %s\n' "${REPAIRED[@]}"
  if [ "${#PROBLEMS[@]}" -gt 0 ]; then
    printf '  ACTION NEEDED: %s\n' "${PROBLEMS[@]}"
    echo "  Until these are resolved the workflow is NOT fully enforced — do not assume otherwise."
  fi
fi

exit 0
