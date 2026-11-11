#!/bin/bash
# Regression tests for scripts/install.sh --machine-only: a RE-ARM must reflect a
# hook that the skill has since DELETED, in both places the arm writes.
#
# The bug this pins (found live): install.sh copied hooks with a plain `cp` and
# merged settings by APPENDING, so re-arming an already-armed machine after a hook
# was removed left the dead hook (a) still on disk in ~/.aleysian/claude-hooks/ and
# (b) still registered in ~/.claude/settings.json — as a second matcher group whose
# command set no longer matched the fragment's, so the de-dup kept both. The removed
# guard kept firing, and nothing said so.
#
# So this arms a machine that looks like an OLDER install (a stale guard file, plus
# stale settings entries — a bare close-gate MCP matcher group and the guard inside
# the Bash group), re-arms from the CURRENT source, and asserts the stale footprint
# is gone while a THIRD-PARTY hook (a different path) survives untouched.
#
# HOME is redirected to a throwaway dir; the real install.sh runs against it. Path
# has a SPACE in it on purpose. Touches nothing outside the temp dir.
#
# Run: bash references/hooks/tests/rearm-prune.test.sh

set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
INSTALL="${SFDS_INSTALL_SH:-$HERE/../../../scripts/install.sh}"
[ -f "$INSTALL" ] || { echo "missing install.sh: $INSTALL"; exit 1; }

command -v jq >/dev/null 2>&1 || { echo "jq required; skipping"; exit 0; }

TMP=$(mktemp -d "${TMPDIR:-/tmp}/rearm prune.XXXXXX") || exit 1
TMP=$(cd "$TMP" && pwd -P)
export HOME="$TMP/home"
mkdir -p "$HOME/.claude" "$HOME/.aleysian/claude-hooks"
SET="$HOME/.claude/settings.json"

cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

PASS=0; FAIL=0
ok()  { PASS=$((PASS+1)); echo "  PASS $1"; }
no()  { FAIL=$((FAIL+1)); echo "  FAIL $1"; }
check(){ if [ "$2" = "$3" ]; then ok "$1 ($2)"; else no "$1 — expected [$2] got [$3]"; fi; }

# ── Simulate an OLDER arm: a since-deleted guard, on disk and in settings ─────
# A stale hook file that the current skill no longer ships.
cat > "$HOME/.aleysian/claude-hooks/guard-issue-close.sh" <<'STUB'
#!/bin/bash
exit 0
STUB
chmod +x "$HOME/.aleysian/claude-hooks/guard-issue-close.sh"

# Settings as an older install left them: a bare close-gate MCP matcher group, the
# guard inside the Bash PreToolUse group, and — crucially — a THIRD-PARTY hook the
# user owns, at a path that is NOT ours, which must survive verbatim.
cat > "$SET" <<JSON
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "mcp__.*__(transitionJiraIssue|editJiraIssue)",
        "hooks": [ { "type": "command", "command": "$HOME/.aleysian/claude-hooks/guard-issue-close.sh" } ] },
      { "matcher": "Bash",
        "hooks": [ { "type": "command", "command": "$HOME/.aleysian/claude-hooks/guard-issue-close.sh" },
                   { "type": "command", "command": "$HOME/.aleysian/claude-hooks/guard-push.sh" } ] },
      { "matcher": "Edit",
        "hooks": [ { "type": "command", "command": "/opt/other-skill/hooks/my-formatter.sh" } ] }
    ]
  }
}
JSON
jq -e . "$SET" >/dev/null 2>&1 || { echo "fixture settings.json is malformed"; exit 1; }

# ── Re-arm from the CURRENT source ────────────────────────────────────────────
bash "$INSTALL" --machine-only >/dev/null 2>&1

echo "== the deleted guard is pruned from ~/.aleysian/claude-hooks/ =="
check "guard-issue-close.sh removed from disk" "gone" \
      "$([ -e "$HOME/.aleysian/claude-hooks/guard-issue-close.sh" ] && echo present || echo gone)"
check "detect-ticket-close.sh not (re)created"  "gone" \
      "$([ -e "$HOME/.aleysian/claude-hooks/detect-ticket-close.sh" ] && echo present || echo gone)"
check "a current guard IS present"              "present" \
      "$([ -e "$HOME/.aleysian/claude-hooks/guard-closing-keywords.sh" ] && echo present || echo gone)"

echo "== settings.json no longer references the removed guard or its matcher =="
CMDS=$(jq -r '.hooks | to_entries[] | .value[]? | .hooks[]? | .command' "$SET" 2>/dev/null)
MATCHERS=$(jq -r '.hooks | to_entries[] | .value[]? | .matcher // ""' "$SET" 2>/dev/null)
check "no guard-issue-close command"   "0" "$(printf '%s\n' "$CMDS" | grep -c 'guard-issue-close.sh')"
check "no detect-ticket-close command" "0" "$(printf '%s\n' "$CMDS" | grep -c 'detect-ticket-close.sh')"
check "no transition/edit MCP matcher" "0" "$(printf '%s\n' "$MATCHERS" | grep -cE 'transitionJiraIssue|editJiraIssue')"

echo "== our footprint is exactly the 19 current hooks =="
ARMED=$(printf '%s\n' "$CMDS" | grep '/.aleysian/claude-hooks/' | sed 's|.*/||' | sort -u | grep -c .)
check "19 aleysian hooks registered" "19" "$ARMED"

echo "== the third-party hook is preserved verbatim =="
check "the user's own Edit hook survives" "1" \
      "$(printf '%s\n' "$CMDS" | grep -c '/opt/other-skill/hooks/my-formatter.sh')"

echo
printf '%d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
