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

# ── Event input ──────────────────────────────────────────────

HOOK_INPUT=""

hook_read_input() { HOOK_INPUT=$(cat); }

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

# Deployment JSON is stdout. CLI update notices on stderr do not belong in it.
# The full hook event remains available to the host transcript.
hook_tool_stdout() {
  printf '%s' "$HOOK_INPUT" | python3 -c '
import json,sys
try:
    response=json.load(sys.stdin).get("tool_response")
    value=response if isinstance(response,str) else response.get("stdout","")
    if isinstance(value,str): print(value)
except (ValueError,AttributeError,TypeError): pass
' 2>/dev/null
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
  elif command -v python3 >/dev/null 2>&1; then
    python3 -c 'import json,sys; print(json.dumps({"hookSpecificOutput": {"hookEventName": sys.argv[1], "additionalContext": sys.argv[2]}}))' "${HOOK_EVENT:-PostToolUse}" "$msg"
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

in_worktree() {
  local dir="${1:-.}" gitdir common
  gitdir=$(git -C "$dir" rev-parse --absolute-git-dir 2>/dev/null) || return 1
  common=$(git_common_dir "$dir") || return 1
  [ "$gitdir" != "$common" ]
}

current_branch() { git -C "${1:-.}" rev-parse --abbrev-ref HEAD 2>/dev/null; }

# All explicit source paths must resolve to one worktree. Missing paths or
# mixed worktrees cannot be credited to a single commit.
source_tree_root() {
  python3 "$SF_HOOK_DIRECTORY/deploy-verdict.py" --source-root "$1"
}

deploy_log() { echo "$(main_repo_root "${1:-.}")/.claude/.deploy-log"; }
validate_log() { echo "$(main_repo_root "${1:-.}")/.claude/.validate-log"; }
pending_log() { echo "$(main_repo_root "${1:-.}")/.claude/.pending-jobs"; }
hatch_log() { echo "$(main_repo_root "${1:-.}")/.claude/.hatch-log"; }

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
# A valid async start registers <job-id, sha, kind, target-key> here.
# The later report matches on job id and exact target, or is ignored. It credits the
# SHA from the start, since main can move while a deploy is in flight.
pending_add() {   # <job> <sha> <deploy|validate> <target-key>
  [ -n "${4:-}" ] || return 1
  local f; f=$(pending_log ".") || return 1
  mkdir -p "$(dirname "$f")" 2>/dev/null
  grep -q "^${1}[[:space:]]" "$f" 2>/dev/null && return 0
  echo "$1 $2 $3 $4" >> "$f"
}

pending_lookup() { # <job> <target-key> -> "<sha> <kind>"; old targetless records cannot qualify
  [ -n "${2:-}" ] || return 1
  local f; f=$(pending_log ".") || return 1
  [ -f "$f" ] || return 1
  awk -v j="$1" -v t="$2" 'NF == 4 && $1 == j && $4 == t {print $2, $3; exit}' "$f"
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

# ── Issue references ─────────────────────────────────────────
#
# Keyword-anchored: a bare '#N' scan reads issue numbers out of ordinary prose.
# The commit convention is 'refs #N' in progress, 'fixes #N' on the squash, and
# commit-msg enforces it.
ISSUE_REF_RE='(refs?|fix(es|ed)?|close[sd]?|resolve[sd]?)[[:space:]]+#'

# Issue numbers this commit claims to act on, one per line.
issue_refs() {
  git log -1 --pretty=%B "$1" 2>/dev/null \
    | grep -oiE "${ISSUE_REF_RE}[0-9]+" \
    | grep -oE '[0-9]+$' | sort -u
}

# Does any commit in $1's history reference issue $2? Prints the match if so.
# git's ERE has no \b; "([^0-9]|$)" is the portable word boundary and keeps #9
# from matching #99.
history_references_issue() {
  git log --extended-regexp --regexp-ignore-case \
    --grep="${ISSUE_REF_RE}${2}([^0-9]|\$)" --oneline "$1" 2>/dev/null | head -1
}

# ── sf output interpretation ─────────────────────────────────

# The deploy id in some sf output, if there is one.
sf_job_id() { printf '%s' "$1" | grep -oE '0Af[a-zA-Z0-9]{12,15}' | head -1; }

# Interpret the supplied CLI JSON only. No implicit connection or background
# Salesforce query is permitted. Preserve the raw result in the project evidence.
SF_HOOK_DIRECTORY="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
sf_deploy_verdict() {
  command -v python3 >/dev/null 2>&1 || { echo UNKNOWN; return 0; }
  printf '%s' "${1:-}" | python3 "$SF_HOOK_DIRECTORY/deploy-verdict.py" "${2:-}"
}

sf_target_key() {
  python3 "$SF_HOOK_DIRECTORY/deploy-verdict.py" --target-key "$1"
}

sf_pending_job() {
  printf '%s' "$1" | python3 "$SF_HOOK_DIRECTORY/deploy-verdict.py" --pending "$2"
}
