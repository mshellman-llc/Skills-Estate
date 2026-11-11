#!/bin/bash
# Shared helpers for this repo's Claude Code hooks. SOURCED, never executed.
#
#   . "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"
#
# EXIT CODE CONTRACT:
#   0  = allow. stdout is surfaced in the transcript.
#   2  = BLOCK. stderr is fed back to Claude. This is the only blocking code.
#   1  = non-blocking error. The tool RUNS ANYWAY.
# Always block via block(); a guard that exits 1 is decorative.
#
# ── THIS FILE ARMS THE MASTER GATE ───────────────────────────
# Sourcing _lib.sh sources _config.sh and calls sfds_gate(), which EXITS 0
# immediately in any repo that has no `aleysian.mode` set. That is why the tiny
# guards in this directory need no mode-gating prologue of their own: they are
# inert everywhere until `/sf-delivery-standards init` configures a clone.
#
# Set HOOK_NO_GATE=1 before sourcing to run anyway (install.sh, audit.sh).

_SFDS_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$_SFDS_LIB_DIR/_config.sh"
. "$_SFDS_LIB_DIR/_ticket.sh"
sfds_gate

# ── Event input ──────────────────────────────────────────────

HOOK_INPUT=""

# Read the event, then STAND WHERE THE COMMAND STANDS before any config is read.
#
# A hook's cwd is the session's project directory, which is not necessarily the
# repo the tool call will act on. sfds_retarget() chdir's to the target and
# re-runs the master gate there, so a command aimed at an unmanaged repo is inert
# and a command aimed at a managed one is judged by ITS config. See the long note
# above sfds_retarget() in _config.sh.
#
# This is also where a deferred gate finally fires, so every hook that sets
# HOOK_DEFER_GATE=1 must call this, and must call it first.
hook_read_input() {
  HOOK_INPUT=$(cat)
  # Fast inert path, for the case that dominates a machine-wide install: an
  # UNRELATED project. When cwd is unmanaged, the call is Bash, and the payload
  # carries no `-C`/`cd`, the command acts on cwd and there is nothing to judge —
  # so skip the jq payload-parse entirely and exit exactly as the full path below
  # would (retarget on an unmanaged cwd already ends in `sfds_gate` -> exit 0).
  #
  # This is safe against a guard bypass because command_repo_dir() recognises a
  # redirection ONLY through `-C` or `cd`; a payload containing neither cannot
  # name another repo, so matching those two substrings has ZERO false negatives.
  # Every other shape (managed cwd, any redirection marker, Edit/Write, MCP)
  # falls through to the full, unchanged path. stdin is already drained above, so
  # this exit does not break the caller's pipe. See sfds_retarget() in _config.sh.
  if [ -z "$(mode)" ]; then
    case "$HOOK_INPUT" in
      *'"tool_name":"Bash"'*|*'"tool_name": "Bash"'*)
        case "$HOOK_INPUT" in
          *-C*|*cd*) : ;;                 # a possible redirection — take the full path
          *)         exit 0 ;;            # no redirection — inert, no jq needed
        esac ;;
    esac
  fi
  sfds_retarget "$(hook_target_dir)"
}

# The directory a tool call will act on, or empty when it names none.
#
# Bash: an explicit repo redirection in the command — `git -C <dir>` or a
# `cd <dir> &&` prefix. Everything else acts on cwd, which is already correct.
# Edit/Write/NotebookEdit/apply_patch: the directory holding the first file being
# written. Codex sends an apply_patch program in tool_input.command rather than a
# file_path, so hook_file_paths normalizes both host payloads.
hook_target_dir() {
  local tool file
  tool=$(hook_tool_name)
  if [ "$tool" = "Bash" ]; then
    command_repo_dir "$(hook_command_text)"
    return 0
  fi
  file=$(hook_file_paths | head -1)
  [ -n "$file" ] && printf '%s' "$(dirname "$file")"
}

# Emit every file touched by a Claude Write/Edit payload or a Codex apply_patch
# payload, one absolute path per line. Delete paths are included; callers that
# need the post-write file can ignore paths that no longer exist.
hook_file_paths() {
  printf '%s' "$HOOK_INPUT" | python3 -c '
import json, sys
from pathlib import Path
try:
    d = json.load(sys.stdin)
except Exception:
    raise SystemExit(0)
ti = d.get("tool_input") or {}
cwd = Path(d.get("cwd") or ".").resolve()
paths = []
for key in ("file_path", "notebook_path"):
    if ti.get(key):
        paths.append(ti[key])
for line in (ti.get("command") or "").splitlines():
    for marker in ("*** Add File: ", "*** Update File: ", "*** Delete File: "):
        if line.startswith(marker):
            paths.append(line[len(marker):].strip())
for raw in dict.fromkeys(paths):
    path = Path(raw)
    print(path if path.is_absolute() else cwd / path)
' 2>/dev/null
}

# An explicit repo redirection in a shell command, or empty.
#
# `git -C` is read BEFORE `cd`, because for a git command it is the one that
# wins: in `cd A && git -C B commit`, the commit lands in B.
#
# Quoted alternatives come FIRST in both patterns. A bare [^[:space:]]+ alone
# truncates a quoted path at its first space, and every worktree of a checkout
# named "64 Org" has a space in its path — so the token would resolve to a
# nonexistent directory, this would silently return nothing, and the retarget
# would not happen. Same bug class as source_tree_root() and
# guard-force-app-bash.sh. Do not "simplify" it.
command_repo_dir() {
  local cmd="$1" tok=""

  tok=$(printf '%s' "$cmd" \
    | grep -oE -- "-C[[:space:]]+(\"[^\"]+\"|'[^']+'|[^[:space:]|&;]+)" \
    | head -1 | sed -E 's/^-C[[:space:]]+//')

  if [ -z "$tok" ]; then
    tok=$(printf '%s' "$cmd" \
      | grep -oE "(^|[;&|][[:space:]]*)cd[[:space:]]+(\"[^\"]+\"|'[^']+'|[^[:space:]|&;]+)" \
      | head -1 | sed -E 's/.*cd[[:space:]]+//')
  fi

  [ -z "$tok" ] && return 0
  tok=${tok%\"}; tok=${tok#\"}; tok=${tok%\'}; tok=${tok#\'}
  printf '%s' "$tok"
}

# hook_field '.tool_input.command' — empty string when absent.
hook_field() {
  local path="$1"
  if command -v jq >/dev/null 2>&1; then
    printf '%s' "$HOOK_INPUT" | jq -r "${path} // empty" 2>/dev/null
  else
    printf '%s' "$HOOK_INPUT" | python3 -c '
import sys, json
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
for k in sys.argv[1].lstrip(".").split("."):
    if isinstance(d, dict) and k in d:
        d = d[k]
    else:
        sys.exit(0)
if d is None or d is False:
    sys.exit(0)
print("true" if d is True else d)
' "$path" 2>/dev/null
  fi
}

hook_command() { hook_field '.tool_input.command'; }

# The tool that fired this hook. For Bash it is "Bash"; for an MCP tool it is
# mcp__<server>__<tool>. A guard that only ever reads .tool_input.command is blind to
# every MCP tool call. No hook in this stack matches on MCP tools anymore — Jira is
# handled agent-side via the Rovo MCP, and a hook cannot reach MCP to gate it — but
# the accessor stays because reading the tool name is generically useful.
hook_tool_name() { hook_field '.tool_name'; }

# The command with heredoc BODIES removed. Use this for any pattern scan: a
# heredoc body is data, not instructions, and commit messages routinely quote
# the commands these guards look for. Redirect targets and flags stay on the
# command line, so real writes are still seen.
strip_heredocs() {
  local line trimmed tag term="" inhd=0
  while IFS= read -r line; do
    if [ "$inhd" = 1 ]; then
      trimmed=$(printf '%s' "$line" | tr -d '[:space:]')
      [ "$trimmed" = "$term" ] && inhd=0
      continue
    fi
    printf '%s\n' "$line"
    tag=$(printf '%s' "$line" \
      | grep -oE "<<-?[[:space:]]*(\"[A-Za-z_][A-Za-z0-9_]*\"|'[A-Za-z_][A-Za-z0-9_]*'|[A-Za-z_][A-Za-z0-9_]*)" \
      | tail -1)
    if [ -n "$tag" ]; then
      term=$(printf '%s' "$tag" | sed -E 's/^<<-?[[:space:]]*//; s/["'"'"']//g')
      inhd=1
    fi
  done
}

hook_command_text() { hook_command | strip_heredocs; }

# ── Command POSITION ─────────────────────────────────────────
#
# Prefix for any pattern that must match a command being RUN rather than a command
# being TALKED ABOUT. It anchors to the start of a line or to just after a
# separator, allowing any number of leading VAR=value assignments:
#
#   ALEY_SKIP_DOD=1 git commit --no-verify         <- using a hatch
#   echo "never git commit --no-verify" >> x.md    <- writing about one
#   grep -rn "sf project deploy start" docs/       <- looking one up
#
# Without this, writing about a thing counts as doing it — and that is not
# hypothetical in either direction. Unanchored, record-escape-hatch.sh logged
# bypasses that never happened; unanchored, the two recorders wrote a validate and
# a PROOF-OF-DEPLOY for a `grep` of the project's own runbook, because the grep
# output quoted a sample transcript containing "Status: Succeeded". The second is
# the worse half: it does not disable a gate, it FORGES the evidence the merge gate
# requires, and a phantom deploy-log line is indistinguishable from a real one
# afterwards.
#
# Defined here and only here so all three hooks anchor identically. Use it as a
# prefix inside a DOUBLE-quoted ERE:
#
#   grep -qE "${SFDS_CMDPOS}git[[:space:]]+([^|;&]*[[:space:]])?commit\b"
SFDS_CMDPOS='(^|[;&|(`])[[:space:]]*([A-Za-z_][A-Za-z0-9_]*=[^[:space:]]*[[:space:]]+)*'

# `sf project deploy start|report|resume`, as a command actually being run. Both
# recorders key off it, so it is one definition with the subcommand appended by the
# caller:
#
#   grep -qE "${SFDS_DEPLOY_RE}(start|report|resume)\b"   any of the three
#   grep -qE "${SFDS_DEPLOY_RE}start\b"                   a start specifically
#
# The gap between the binary and `deploy` is bounded to [^|;&] rather than left as
# `.*`. An unbounded gap matches an `sf` in one pipeline stage against a `deploy` in
# the next — two different commands — which is the same reason the commit guards
# bound theirs the same way.
SFDS_DEPLOY_RE="${SFDS_CMDPOS}(sf|sfdx)[[:space:]]+([^|;&]*[[:space:]])?deploy[[:space:]]+"

# Combined stdout+stderr of the tool that just ran (PostToolUse only).
# tool_response is an object for Bash, but may be a bare string.
hook_tool_output() {
  if command -v jq >/dev/null 2>&1; then
    printf '%s' "$HOOK_INPUT" | jq -r '
      .tool_response
      | if type == "string" then .
        elif type == "object" then ((.stdout // "") + "\n" + (.stderr // ""))
        else "" end' 2>/dev/null
  else
    printf '%s' "$HOOK_INPUT" | python3 -c '
import sys, json
try:
    r = json.load(sys.stdin).get("tool_response")
except Exception:
    sys.exit(0)
if isinstance(r, str):
    print(r)
elif isinstance(r, dict):
    print((r.get("stdout") or "") + "\n" + (r.get("stderr") or ""))
' 2>/dev/null
  fi
}

# ── Talking to Claude ────────────────────────────────────────

# Block the tool call. Every argument is one line of explanation.
block() {
  {
    echo ""
    printf '%s\n' "$@"
  } >&2
  exit 2
}

# Feed guidance back to Claude without failing anything. Plain stderr on exit 0
# reaches only the user's transcript; additionalContext is the channel that
# reaches the model. Set HOOK_EVENT to the firing event — a mismatched event
# name is dropped. The self-attributing tag keeps agents from reading hook
# output as a user instruction.
note() {
  local msg
  msg="[automated hook: $(basename "${0:-hook}")]
$(printf '%s\n' "$@")"
  if command -v jq >/dev/null 2>&1; then
    jq -nc --arg m "$msg" --arg e "${HOOK_EVENT:-PostToolUse}" \
      '{hookSpecificOutput: {hookEventName: $e, additionalContext: $m}}'
  else
    printf '%s\n' "$msg" >&2
  fi
}

# ── Git topology ─────────────────────────────────────────────
#
# A linked worktree's --git-dir is <main>/.git/worktrees/<name>; its
# --git-common-dir is <main>/.git. In the main checkout they are the same.
# That comparison is the worktree test — never pattern-match on a path like
# ".claude/worktrees/", which misses a worktree created anywhere else.

git_common_dir() {
  local d
  d=$(git -C "${1:-.}" rev-parse --git-common-dir 2>/dev/null) || return 1
  case "$d" in /*) ;; *) d="$(cd "${1:-.}" && pwd)/$d" ;; esac
  (cd "$d" 2>/dev/null && pwd)
}

# The original clone's working tree, even when called from inside a worktree.
# All machine-local state lives there and only there.
main_repo_root() {
  local common
  common=$(git_common_dir "${1:-.}") || return 1
  # <root>/.git -> <root>;  a bare repo has no parent working tree
  case "$common" in
    */.git) dirname "$common" ;;
    *) git -C "${1:-.}" rev-parse --show-toplevel 2>/dev/null ;;
  esac
}

# Both sides must be resolved the SAME way or this fails OPEN — the worst
# direction for a guard, because the main checkout then reads as a worktree and
# every force-app write is allowed with no warning.
#
# `--absolute-git-dir` returns a PHYSICAL path; git_common_dir ends in a bare
# `pwd`, which is LOGICAL. Under any symlinked path — macOS /var -> /private/var,
# a symlinked home or work directory, some network mounts — those two strings can
# never be equal, so the comparison below is always true. `pwd -P` on both sides
# is what keeps that from happening.
in_worktree() {
  local dir="${1:-.}" gitdir common
  gitdir=$(git -C "$dir" rev-parse --absolute-git-dir 2>/dev/null) || return 1
  common=$(git_common_dir "$dir") || return 1
  gitdir=$(cd "$gitdir" 2>/dev/null && pwd -P) || return 1
  common=$(cd "$common" 2>/dev/null && pwd -P) || return 1
  [ "$gitdir" != "$common" ]
}

current_branch() { git -C "${1:-.}" rev-parse --abbrev-ref HEAD 2>/dev/null; }

# The working tree a deploy/validate command is operating on, derived from its
# first resolvable --source-dir / -d; falls back to cwd.
#
# A dry run validates FILES, not the directory you are standing in. Reading
# `git rev-parse HEAD` from cwd records the wrong commit whenever the two
# differ — judge the target, not the shell.
# Quoted alternatives MUST come first in the token pattern below. An unquoted
# pattern alone truncates a quoted path at its first space — "/…/64 Org-GH-431/…"
# becomes "/…/64" — which is not a directory, so this falls through to $PWD and
# records the WRONG tree's HEAD as validated. guard-pr-merge.sh then blocks the
# PR as unvalidated, or worse, credits a different branch's commit.
# Same bug class as GH-436 in guard-force-app-bash.sh. Do not "simplify" this.
source_tree_root() {
  local cmd="$1" tok dir
  while IFS= read -r tok; do
    [ -z "$tok" ] && continue
    tok=${tok%\"}; tok=${tok#\"}; tok=${tok%\'}; tok=${tok#\'}
    case "$tok" in /*) dir="$tok" ;; *) dir="$PWD/$tok" ;; esac
    [ -d "$dir" ] || dir=$(dirname "$dir")
    while [ ! -d "$dir" ] && [ "$dir" != "/" ] && [ "$dir" != "." ]; do dir=$(dirname "$dir"); done
    if git -C "$dir" rev-parse --git-dir >/dev/null 2>&1; then
      git -C "$dir" rev-parse --show-toplevel 2>/dev/null && return 0
    fi
  done < <(printf '%s' "$cmd" \
    | grep -oE -- "(--source-dir|-d)[[:space:]]+(\"[^\"]+\"|'[^']+'|[^[:space:]|&;]+)" \
    | sed -E 's/^(--source-dir|-d)[[:space:]]+//')
  printf '%s' "$PWD"
}

# All machine-local state lives in $(git-common-dir)/aleysian/ — see state_dir()
# in _config.sh for why it moved out of the working tree. One helper per log so a
# caller never builds the path itself.
deploy_log()   { echo "$(state_dir "${1:-.}")/deploy-log"; }
validate_log() { echo "$(state_dir "${1:-.}")/validate-log"; }
pending_log()  { echo "$(state_dir "${1:-.}")/pending-jobs"; }
hatch_log()    { echo "$(state_dir "${1:-.}")/hatch-log"; }
approve_log()  { echo "$(state_dir "${1:-.}")/approve-log"; }
drift_log()    { echo "$(state_dir "${1:-.}")/drift-log"; }
ship_log()     { echo "$(state_dir "${1:-.}")/ship-log"; }
dod_state()    { echo "$(state_dir "${1:-.}")/dod-state"; }
checklist()    { echo "$(state_dir "${1:-.}")/client-checklist"; }

# ── Escape-hatch accounting ──────────────────────────────────
#
# record_hatch <kind> <detail...> appends one line and returns 0, so a caller
# can write:  record_hatch SKIP_DOD "..." ; exit 0
#
# Never blocks. Hatches exist because a gate is occasionally wrong; the log
# makes using one a decision on record rather than a silent one.
record_hatch() {
  local kind="$1"; shift
  local f; f=$(hatch_log ".") || return 0
  mkdir -p "$(dirname "$f")" 2>/dev/null
  printf '%s %s %s %s\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    "$kind" \
    "$(git rev-parse --short HEAD 2>/dev/null || echo '-')" \
    "$*" >> "$f" 2>/dev/null
  return 0
}

# ── Async job correlation ────────────────────────────────────
#
# `deploy report --job-id X` serves two purposes that look identical from the
# command: collecting the result of an --async job this clone started, and
# looking up some older job. Only the first is a result.
#
# A `deploy start` that returns in flight registers <job-id, sha, kind> here.
# The later report matches on job id, or is ignored as a lookup. It credits the
# SHA from the start, since main can move while a deploy is in flight.
pending_add() {   # <job> <sha> <deploy|validate>
  local f; f=$(pending_log ".") || return 1
  mkdir -p "$(dirname "$f")" 2>/dev/null
  grep -q "^${1}[[:space:]]" "$f" 2>/dev/null && return 0
  echo "$1 $2 $3" >> "$f"
}

pending_lookup() { # <job> -> "<sha> <kind>" when we started it, else nothing
  local f; f=$(pending_log ".") || return 1
  [ -f "$f" ] || return 1
  awk -v j="$1" '$1 == j {print $2, $3; exit}' "$f"
}

pending_remove() {
  local f tmp; f=$(pending_log ".") || return 1
  [ -f "$f" ] || return 0
  tmp="${f}.tmp$$"
  awk -v j="$1" '$1 != j' "$f" > "$tmp" 2>/dev/null && mv "$tmp" "$f"
}

# Newest-first read of a log file (macOS has no tac).
read_log_reverse() {
  [ -f "$1" ] || return 0
  if command -v tac >/dev/null 2>&1; then tac "$1"; else tail -r "$1"; fi
}

# Deployed SHAs, newest first. Lines are "<sha> <job-id> <utc stamp>", so field
# 1 is the only safe read. Every consumer must go through this rather than
# treating a whole line as a SHA.
deploy_log_shas() {
  read_log_reverse "$1" | awk 'NF {print $1}'
}

# ── Ticket references ────────────────────────────────────────
#
# The pattern is per ticket system and comes from config — see ref_pattern() in
# _config.sh. GitHub stays keyword-anchored ('refs #12', never a bare '#12')
# because a bare-#N scan reads issue numbers out of ordinary prose, which is
# enough to label and unlock tickets nobody touched. Jira keys need no keyword:
# SFO-123 is already a distinctive token.
#
# Kept as a variable for hooks that grep a message directly.
ISSUE_REF_RE_LEGACY='(refs?|fix(es|ed)?|close[sd]?|resolve[sd]?)[[:space:]]+#'

# Ticket refs this commit claims to act on, one per line. Bare numbers under
# GitHub, whole keys (SFO-12) otherwise — see extract_refs().
issue_refs() {
  git log -1 --pretty=%B "$1" 2>/dev/null | extract_refs
}

# Does any commit in $1's history reference ticket $2? Prints the match if so.
#
# git's ERE has no \b, so "([^0-9]|$)" is the portable trailing boundary — it is
# what keeps #9 from matching #99, and SFO-1 from matching SFO-12.
history_references_issue() {
  local needle
  case "$(ticket_system)" in
    github) needle="${ISSUE_REF_RE_LEGACY}${2}([^0-9]|\$)" ;;
    *)      needle="${2}([^0-9]|\$)" ;;
  esac
  git log --extended-regexp --regexp-ignore-case \
    --grep="$needle" --oneline "$1" 2>/dev/null | head -1
}

# ── sf output interpretation ─────────────────────────────────

# The deploy id in some sf output, if there is one.
sf_job_id() { printf '%s' "$1" | grep -oE '0Af[a-zA-Z0-9]{12,15}' | head -1; }

# Ask the org about one job. Prints "<status> <checkOnly>", or nothing when the
# job cannot be resolved. Never --use-most-recent: in a multi-agent org that
# resolves to somebody else's deploy.
#
# The `.result.id == $id` guard is load-bearing — `deploy report` answers from a
# local cache when it can, so a mismatched id is no answer, not a verdict.
sf_job_info() {
  command -v sf >/dev/null 2>&1 || return 1
  command -v jq >/dev/null 2>&1 || return 1
  sf project deploy report --job-id "$1" --json 2>/dev/null \
    | jq -r --arg id "$1" '
        select(.result.id == $id)
        | "\(.result.status // "") \(.result.checkOnly // false)"' 2>/dev/null \
    | head -1
}

# Poll one job until the org reports a TERMINAL status (Succeeded/Failed/Canceled),
# or the bound is reached. Same "<status> <checkOnly>" output shape as sf_job_info.
#
# For the caller that already KNOWS the underlying operation finished and only needs
# the org's status API to catch up — a SYNCHRONOUS `deploy start`, which blocked on
# the job before this hook ever ran. See the poll note in sf_deploy_verdict(); this
# is not for an --async job, which really is still running and must not be waited on
# inside a hook.
#
# Bounded so a hook can never hang: SFDS_JOB_POLL_TRIES readings, SFDS_JOB_POLL_SLEEP
# seconds apart (tests set the sleep to 0). Returns the last reading, terminal or not
# — a non-terminal result after the bound falls through to UNKNOWN upstream, which is
# recoverable, exactly as a genuine timeout should be.
sf_job_info_wait() {
  local job="$1"
  local tries="${SFDS_JOB_POLL_TRIES:-10}" nap="${SFDS_JOB_POLL_SLEEP:-3}"
  local info st i=1
  while :; do
    info=$(sf_job_info "$job")
    st=${info%% *}
    case "$st" in Succeeded|Failed|Canceled) break ;; esac
    [ "$i" -ge "$tries" ] && break
    i=$((i+1))
    sleep "$nap"
  done
  printf '%s' "$info"
}

# sf_deploy_verdict <tool output> <command text> -> one of:
#
#   DEPLOY    a real deploy succeeded — the org now holds this code
#   VALIDATE  a check-only deploy succeeded — the org is unchanged
#   FAILED    it demonstrably did not succeed
#   UNKNOWN   still running, or nothing conclusive to read
#
# UNKNOWN is not FAILED. FAILED means main may be ahead of the org and needs a
# fix-forward or revert; UNKNOWN usually means an --async deploy is in flight.
#
# The org is the authority whenever a job id is available. "Status: Succeeded"
# is a string, and a string cannot tell a real deploy from a dry run — which is
# the distinction the whole proof-of-deploy gate rests on.
sf_deploy_verdict() {
  local out="${1:-}" cmd="${2:-}" job info st check

  # The command first: `deploy report --job-id X` names the job explicitly and
  # does not always echo it back in the output.
  job=$(sf_job_id "$cmd")
  [ -z "$job" ] && job=$(sf_job_id "$out")

  if [ -n "$job" ]; then
    info=$(sf_job_info "$job")
    st=${info%% *}

    # A SYNCHRONOUS `deploy start` (no --async) has, by definition, already run to
    # completion by the time this hook reads its output — the command BLOCKED on the
    # job. So a NON-TERMINAL org status here (InProgress/Pending/Queued) is not "in
    # flight", it is the org's status API lagging a job it just finished — an
    # eventual-consistency window that widens the longer the test/coverage run takes.
    # Left as UNKNOWN, that verdict drops the run to a pending entry that nothing ever
    # finalises, so record-validate.sh writes no pass and guard-pr-merge.sh blocks a
    # genuinely green commit. Poll the org to a terminal status first.  (ORG64-161)
    #
    #   --async     the OPPOSITE case — the job really is still running, and the
    #               command returned early on purpose. Never poll it here; that would
    #               hang the hook for the length of the deploy. It is left to the
    #               later `deploy report`/`deploy resume` via the pending mechanism.
    #   empty info  the org cannot resolve the id at all (cache miss / transient).
    #               Polling cannot fix that, so fall straight through to the
    #               output-text/JSON scan below — the fast, unchanged path.
    if [ -n "$info" ] \
       && printf '%s' "$cmd" | grep -qE "${SFDS_DEPLOY_RE}start\b" \
       && ! printf '%s' "$cmd" | grep -qE -- '--async'; then
      case "$st" in
        Succeeded|Failed|Canceled) : ;;
        *) info=$(sf_job_info_wait "$job"); st=${info%% *} ;;
      esac
    fi

    if [ -n "$info" ]; then
      check=${info##* }
      case "$st" in
        Succeeded)          [ "$check" = "true" ] && echo "VALIDATE" || echo "DEPLOY" ;;
        Failed|Canceled)    echo "FAILED" ;;
        *)                  echo "UNKNOWN" ;;   # InProgress / Pending / Queued
      esac
      return 0
    fi
  fi

  # No id, or the org could not resolve it. The text can still prove two things,
  # and it must not be allowed to "prove" a third:
  #
  #   FAILED    an explicit failure is an explicit failure.
  #   VALIDATE  a success plus `--dry-run` IN THE COMMAND. check-only is read off
  #             the command there, not guessed from the output, so it stands.
  #   DEPLOY    NOT AVAILABLE. "Status: Succeeded" is a string, and this function
  #             exists precisely because a string cannot tell a real deploy from a
  #             validation. Treating an unconfirmed success as a deploy is how a
  #             `grep` of the runbook wrote a proof-of-deploy for a commit nothing
  #             had ever sent to an org.
  #
  # So an unconfirmed success is UNKNOWN. Downstream that is already the right
  # shape: it is remembered as a pending job and is never reported as FAILED, and
  # the note tells the agent to collect the result with `deploy report --job-id`.
  # A real deploy always emits its 0Af id, so the cost is a missing record in the
  # cases where the org could not be asked at all — recoverable in one command,
  # which is the correct direction for a gate to fail.
  local kind="UNKNOWN"
  printf '%s' "$cmd" | grep -qE -- '--dry-run' && kind="VALIDATE"

  # STRUCTURED JSON is sf's own machine-readable self-report and is PREFERRED
  # whenever it is present. When the output carries a JSON envelope we decide from
  # it ALONE and do not fall through to the plain-text scan below: a "Status:" line
  # appended to a --json run (e.g. `sf ... --json; echo "Status: Succeeded"`) must
  # never override the structured result the CLI actually returned.  (FORGE 2)
  if command -v jq >/dev/null 2>&1 && printf '%s' "$out" | grep -q '"status"'; then
    st=$(printf '%s' "$out" | jq -r '.result.status // empty' 2>/dev/null | head -1)
    case "$st" in
      Succeeded)       echo "$kind";  return 0 ;;
      Failed|Canceled) echo "FAILED"; return 0 ;;
      *)               echo "UNKNOWN"; return 0 ;;
    esac
  fi

  # No JSON envelope at all — the genuine "dry run with no queryable job" case the
  # comment above is about. Plain text can still prove a FAILED outright. It can
  # prove a VALIDATE too, but ONLY when the run actually reached the org, which a
  # real dry run evidences by emitting a job id (in $job here even when the org
  # could not later resolve it). A bare "Status: Succeeded" with NO id anywhere is
  # exactly what `echo "Status: Succeeded"` produces, and on its own it must not
  # unlock the merge gate.  (FORGE 2)
  #
  # Residual, non-JSON only: a caller who also fabricates a job id — echoing a real
  # foreign dry-run's 0Af alongside the success line — can still get here, the same
  # tradeoff a string channel always carries. Using --json removes it: the branch
  # above then decides from the structured envelope, which an echo cannot forge.
  printf '%s' "$out" | grep -qE 'Status:[[:space:]]+(Failed|Canceled)' && { echo "FAILED"; return 0; }
  if [ -n "$job" ] && printf '%s' "$out" | grep -qE 'Status:[[:space:]]+Succeeded'; then
    echo "$kind"; return 0
  fi

  echo "UNKNOWN"
}

# On a `deploy start`, sf_deploy_verdict() scrapes the job id from the COMBINED
# output of what may be a chained command, and the org will confirm ANY real
# Succeeded non-checkOnly id — including a foreign one echoed after a deploy that
# actually failed:
#
#   sf project deploy start --source-dir force-app 2>/dev/null; echo "Deploy 0Af<foreign>"
#
# The org says "yes, 0Af<foreign> succeeded", HEAD is credited, and proof-of-deploy is
# recorded for a commit the org never received. Before crediting a START, require this
# command's OWN output to show THIS deploy succeeded: a structured JSON success, or
# a plain-text "Status: Succeeded". The forge above carries neither (the real deploy
# failed and its stderr was suppressed), so it is refused.  (FORGE 1)
#
# JSON is authoritative when present, so a "Status: Succeeded" echoed after a --json
# run whose envelope reports Failed cannot rescue it. The report/resume path needs no
# such check: it is bound harder still, by pending_lookup — it credits only a job THIS
# clone registered from a start it watched, and credits that start's sha, not HEAD.
#
# Residual, non-JSON only: a caller who ALSO echoes "Status: Succeeded" defeats this,
# the same string-channel tradeoff sf_deploy_verdict() documents for VALIDATE. Deploy
# with --json to close it — the CLI's structured self-report cannot be echo-forged.
deploy_start_self_confirmed() {
  local out="${1:-}" st
  if command -v jq >/dev/null 2>&1 && printf '%s' "$out" | grep -q '"status"'; then
    st=$(printf '%s' "$out" | jq -r '.result.status // empty' 2>/dev/null | head -1)
    [ "$st" = "Succeeded" ]
    return
  fi
  printf '%s' "$out" | grep -qE 'Status:[[:space:]]+Succeeded'
}
