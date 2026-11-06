#!/bin/bash
# Regression tests for REQUIREMENT 1 — "running the skill affects exactly one
# project": no interference, and no cost, in a repo that never went through init.
#
# These hooks are registered user-level and fire in EVERY repo on the machine, so
# their inert path is the single most-executed code in the stack. Three ways it
# was, or could again be, wrong — each failing SILENTLY toward "carry on":
#
#   EPIPE        a hook that exits before reading its payload leaves the harness's
#                write to it failing with a broken pipe. Measured live: the two
#                SessionStart hooks did this on every session start in every
#                unrelated project. Pinned below by feeding a >64KB payload (larger
#                than the pipe buffer) and asserting the writer never breaks.
#   cost         the inert path used to spawn 3-4 subprocesses per hook (git twice,
#                jq twice) just to discover "not my project". Pinned below by
#                counting git+jq calls with PATH shims: <=1 git, 0 jq.
#   bypass       the cost fix skips the jq payload-parse only when the command
#                cannot name another repo. If that shortcut ever skips a command
#                that DID redirect into a managed repo, it is a guard bypass. Pinned
#                below: from an unmanaged cwd, `git -C <managed>` / `cd <managed>`
#                must still be judged.
#
# And the control: the optimization must not disable the guards in a repo that IS
# managed.
#
# Point SFDS_HOOKS_DIR at another claude-hooks tree to run these against a pre-fix
# baseline and watch them fail (that is how a check earns trust — see the header of
# REQUIREMENTS.md §14). E.g.:
#   SFDS_HOOKS_DIR=~/.estate/claude-hooks bash <thisfile>     # armed, pre-drain
#   (or extract an older SHA with `git show <sha>:...` into a temp tree)
#
# Both throwaway repos have SPACES in their names on purpose — every worktree of a
# checkout named "64 Org" does. Self-contained: touches nothing else.
#
# Run: bash references/hooks/tests/req1-noninterference.test.sh

set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
HOOKS="${SFDS_HOOKS_DIR:-$HERE/../claude-hooks}"
[ -d "$HOOKS" ] || { echo "missing hooks dir: $HOOKS"; exit 1; }

command -v git >/dev/null 2>&1 || { echo "git required"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "python3 required; skipping"; exit 0; }
REALGIT=$(command -v git); REALJQ=$(command -v jq || true)

TMP=$(mktemp -d "${TMPDIR:-/tmp}/req1 noninterference.XXXXXX") || exit 1
TMP=$(cd "$TMP" && pwd -P)
trap 'rm -rf "$TMP"' EXIT

# UN: unmanaged git repo.  NOGIT: not a repo at all.  MG: a managed, Jira-tracked
# repo whose guard-closing-keywords rule 2 blocks any '#N' ref.
UN="$TMP/plain repo";   mkdir -p "$UN"    && ( cd "$UN"  && "$REALGIT" init -q -b main )
NOGIT="$TMP/not a repo"; mkdir -p "$NOGIT"
MG="$TMP/managed repo"; mkdir -p "$MG"    && ( cd "$MG"  && "$REALGIT" init -q -b main \
  && "$REALGIT" config estate.mode native \
  && "$REALGIT" config estate.trunk main \
  && "$REALGIT" config estate.ticket.system jira \
  && "$REALGIT" config estate.ticket.project EXAMPLE )

# call-counting shims: each records itself, then execs the real tool.
BIN="$TMP/bin"; mkdir -p "$BIN"
printf '#!/bin/bash\necho git >> "%s/calls"\nexec "%s" "$@"\n' "$TMP" "$REALGIT" > "$BIN/git"; chmod +x "$BIN/git"
[ -n "$REALJQ" ] && { printf '#!/bin/bash\necho jq >> "%s/calls"\nexec "%s" "$@"\n' "$TMP" "$REALJQ" > "$BIN/jq"; chmod +x "$BIN/jq"; }

PASS=0; FAIL=0
ok() { PASS=$((PASS+1)); echo "  PASS $1"; }
no() { FAIL=$((FAIL+1)); echo "  FAIL $1"; }

# a JSON PreToolUse payload for command $1
payload() { printf '%s' "$1" | python3 -c 'import json,sys; print(json.dumps({"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":sys.stdin.read()}}))'; }

# ── 1. EPIPE: no hook breaks the caller's pipe in an unrelated project ──────────
# >64KB payload: a hook that exits without draining makes the writer take SIGPIPE.
PAD=$(head -c 200000 </dev/zero | tr '\0' x)
BIG='{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"'"$PAD"'"}}'
echo "== EPIPE: every hook drains stdin and exits cleanly in an unmanaged repo and a non-git dir =="
for f in "$HOOKS"/*.sh; do
  b=$(basename "$f"); case "$b" in _*) continue;; esac
  for ctx in "$UN" "$NOGIT"; do
    werr="$TMP/werr"; : > "$werr"
    { printf '%s' "$BIG" 2>"$werr"; } | ( cd "$ctx" && CLAUDE_PROJECT_DIR="$ctx" bash "$f" >/dev/null 2>&1 )
    ps=${PIPESTATUS[0]}
    if grep -qi 'broken pipe' "$werr" || [ "$ps" != 0 ]; then
      no "$b broke the pipe in '$(basename "$ctx")'"
    else
      ok "$b drained in '$(basename "$ctx")'"
    fi
  done
done

# ── 2. cost: the inert Bash path is <=1 git call and 0 jq calls ─────────────────
echo "== cost: an unmanaged Bash call with no redirection costs <=1 git and 0 jq =="
SMALL=$(payload 'echo hi')
for b in guard-sf-flags guard-force-app-bash guard-sf-deploy guard-worktree-nesting \
         guard-pr-merge guard-closing-keywords guard-push \
         ensure-worktree-config record-escape-hatch; do
  f="$HOOKS/$b.sh"; [ -f "$f" ] || continue
  : > "$TMP/calls"
  printf '%s' "$SMALL" | ( cd "$UN" && PATH="$BIN:$PATH" CLAUDE_PROJECT_DIR="$UN" bash "$f" >/dev/null 2>&1 )
  g=$(grep -c '^git$' "$TMP/calls"); j=$(grep -c '^jq$' "$TMP/calls")
  if [ "$g" -le 1 ] && [ "$j" -eq 0 ]; then ok "$b: ${g} git, ${j} jq"
  else no "$b: ${g} git, ${j} jq (want <=1 git, 0 jq)"; fi
done

# ── 3. bypass: an unmanaged cwd redirecting into a MANAGED repo is still judged ──
# guard-closing-keywords blocks a Jira '#N' ref; 'wip #12' isolates that one rule.
blocks() { # cwd, command  -> true if the hook blocks (exit != 0)
  payload "$2" | ( cd "$1" && CLAUDE_PROJECT_DIR="$1" bash "$HOOKS/guard-closing-keywords.sh" ) >/dev/null 2>&1
  [ $? -ne 0 ]
}
echo "== bypass: from an unmanaged cwd, a command aimed at a managed repo is still judged =="
blocks "$UN" "git -C \"$MG\" commit -m \"wip #12\"" && ok "git -C <managed> from unmanaged cwd still blocks" \
  || no "git -C <managed> was NOT judged — the inert-path shortcut opened a bypass"
blocks "$UN" "cd \"$MG\" && git commit -m \"wip #12\"" && ok "cd <managed> from unmanaged cwd still blocks" \
  || no "cd <managed> was NOT judged — the inert-path shortcut opened a bypass"

# ── 4. control: the optimization does not disable guards where they must run ─────
echo "== control: guards still fire in a managed repo, and stay inert in an unmanaged one =="
blocks "$MG" "git commit -m \"wip #12\"" && ok "managed cwd: '#12' ref blocks" \
  || no "managed cwd: guard did NOT fire — the optimization disabled it"
blocks "$MG" "git commit -m \"all clean\"" && no "managed cwd: clean message was wrongly blocked" \
  || ok "managed cwd: clean message allowed"
blocks "$UN" "git commit -m \"wip #12\"" && no "unmanaged cwd: '#12' ref wrongly blocked (not inert)" \
  || ok "unmanaged cwd: '#12' ref inert (allowed)"

echo
echo "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
