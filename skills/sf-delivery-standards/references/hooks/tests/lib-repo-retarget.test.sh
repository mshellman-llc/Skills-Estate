#!/bin/bash
# Regression tests for sfds_retarget() / command_repo_dir() — "judge the target
# repo, not the shell".
#
# The bug these pin down: every `aleysian.*` read goes through `git config`, which
# answers for the repo containing the hook process's cwd. A hook's cwd is the
# SESSION's project directory, not necessarily the repo the command acts on. So a
# `git commit` in the skills repo was blocked by 64-Org's Jira ref rules — in a
# repo with no `aleysian.mode` at all, where every guard should have been inert.
#
# It has TWO directions, and only one of them is visible in normal use:
#
#   over-block   configured cwd, unmanaged target -> the wrong project's rules
#                are applied. Loud. This is the one that was found.
#   under-block  unmanaged cwd, configured target -> the source-time gate exits 0
#                before any command is read, so NO rule is applied. Silent, and
#                strictly worse. Closed by deferring the gate (HOOK_DEFER_GATE).
#
# Both are covered below. A fix for only the first would leave the more dangerous
# half in place and look complete.
#
# Both throwaway repos have SPACES in their names on purpose: worktree and repo
# paths here routinely contain one ("64 Org"), so they are always quoted, and a
# token pattern without a quoted alternative truncates them at the first space —
# which makes command_repo_dir() return nothing and the retarget silently not
# happen. Do not "tidy" the spaces away; they are the test.
#
# Self-contained: builds its own throwaway repos, touches nothing else.
#
# Run: bash references/hooks/tests/lib-repo-retarget.test.sh

set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
HOOK="$HERE/../claude-hooks/guard-closing-keywords.sh"
[ -f "$HOOK" ] || { echo "missing hook: $HOOK"; exit 1; }

command -v python3 >/dev/null 2>&1 || { echo "python3 required; skipping"; exit 0; }

TMP=$(mktemp -d "${TMPDIR:-/tmp}/retarget test.XXXXXX") || exit 1
TMP=$(cd "$TMP" && pwd -P)
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

# CONFIGURED: a managed project, Jira-tracked. Its rule 2 blocks any '#N' ref.
# PLAIN:      an ordinary git repo with no aleysian.* config at all. Every guard
#             must be inert here — that is what the master gate is for.
CONF="$TMP/configured repo"
PLAIN="$TMP/plain repo"
OUT="$TMP/hook.out"

for D in "$CONF" "$PLAIN"; do
  mkdir -p "$D" && ( cd "$D" && git init -q -b main . >/dev/null 2>&1 \
    && git config user.email t@t.test && git config user.name t \
    && echo x > f.txt && git add -A >/dev/null 2>&1 \
    && git commit -qm init >/dev/null 2>&1 )
done

( cd "$CONF" \
  && git config aleysian.mode native \
  && git config aleysian.trunk main \
  && git config aleysian.ticket.system jira \
  && git config aleysian.ticket.project ORG64 )

PASS=0; FAIL=0

# run <expect allow|block> <cwd> <label> <command text>
run() {
  local want="$1" cwd="$2" label="$3" cmd="$4" got rc
  printf '%s' "$cmd" \
    | python3 -c 'import json,sys; print(json.dumps({"tool_name":"Bash","tool_input":{"command":sys.stdin.read()}}))' \
    | ( cd "$cwd" && bash "$HOOK" ) >"$OUT" 2>&1
  rc=$?
  got=allow; [ $rc -ne 0 ] && got=block
  if [ "$got" = "$want" ]; then
    PASS=$((PASS+1)); echo "  PASS [$got] $label"
  else
    FAIL=$((FAIL+1)); echo "  FAIL expected=$want got=$got :: $label"; sed -n '2,4p' "$OUT"
  fi
}

# 'wip #12' carries no closing keyword, so ONLY the Jira '#N' rule can fire —
# which isolates the question this suite is asking (whose config was read?) from
# every other rule in the hook.
MSG='git commit -m "wip #12"'

echo "== the control: no redirection, so cwd IS the target =="
run block "$CONF"  "configured cwd, no redirect"    "$MSG"
run allow "$PLAIN" "unmanaged cwd, no redirect"     "$MSG"

echo "== over-block: configured cwd, command aimed at an unmanaged repo =="
run allow "$CONF" "cd <plain> && git commit"        "cd \"$PLAIN\" && $MSG"
run allow "$CONF" "git -C <plain> commit"           "git -C \"$PLAIN\" commit -m \"wip #12\""
run allow "$CONF" "single-quoted cd target"         "cd '$PLAIN' && $MSG"

echo "== under-block: unmanaged cwd, command aimed at the configured repo =="
run block "$PLAIN" "cd <configured> && git commit"  "cd \"$CONF\" && $MSG"
run block "$PLAIN" "git -C <configured> commit"     "git -C \"$CONF\" commit -m \"wip #12\""

echo "== -C wins over cd, because that is what git does =="
run block "$PLAIN" "cd <plain> && git -C <conf>"    "cd \"$PLAIN\" && git -C \"$CONF\" commit -m \"wip #12\""
run allow "$CONF"  "cd <conf> && git -C <plain>"    "cd \"$CONF\" && git -C \"$PLAIN\" commit -m \"wip #12\""

echo "== a target that resolves to no repo leaves cwd's answer standing =="
run block "$CONF" "cd /nonexistent-xyz"             "cd /nonexistent-xyz-9f3 && $MSG"
run block "$CONF" "cd a non-repo directory"         "cd \"$TMP\" && $MSG"

echo "== a 'cd' inside a commit MESSAGE is not a redirection =="
run block "$CONF" "message mentioning cd"           "git commit -m \"wip #12; cd $PLAIN\""

echo
echo "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
