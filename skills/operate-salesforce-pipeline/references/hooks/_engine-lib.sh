#!/usr/bin/env bash
# Sourced by every guard in this directory. Not a hook itself: no matcher, no
# entry in settings.json.
#
# SELF-CONTAINED ON PURPOSE. This reads nothing from configure-salesforce-project and
# writes nothing into it. The two stacks compose by staying out of each other's
# files: that one is topology-agnostic and governs the loop against ONE org,
# this one adds the refusals that only make sense when a pipeline.yml says some
# orgs belong to an engine. An agent working the local loop needs to know
# nothing about this layer, and needs to change nothing to accommodate it.

# ── hook payload ─────────────────────────────────────────────
hook_command() {
  local input
  input=$(cat 2>/dev/null || true)
  printf '%s' "$input" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    print(""); sys.exit(0)
print((d.get("tool_input") or {}).get("command", "") or "")
' 2>/dev/null
}

# Exit 2 is the PreToolUse "block" contract; the message goes to stderr.
block() {
  printf '\n' >&2
  for line in "$@"; do printf '%s\n' "$line" >&2; done
  printf '\n' >&2
  exit 2
}
note() { for line in "$@"; do printf '%s\n' "$line" >&2; done; }

# ── the master gate ──────────────────────────────────────────
#
# No pipeline.yml, no opinion. This is what makes these hooks safe to register
# machine-wide: in any repo without one they exit 0 before doing anything, the
# same way configure-salesforce-project' hooks exit 0 without estate.mode.
#
# gate_or_exit — print the pipeline path, or drain stdin and exit 0.
#
# These hooks sit in front of EVERY Bash call on the machine, and in a repo with
# no pipeline.yml the answer is "no opinion". Reaching that with two git calls
# instead of a python3 start halves the cost of the no-op case.
#
# The drain is not optional. The caller writes the payload to our stdin; exiting
# without reading it leaves that write to fail with EPIPE, which showed up as
# BrokenPipeError the moment the gate moved ahead of the parse. `cat` costs a
# few ms against python3's ~25 and buys back the guarantee that a guard cannot
# upset the harness invoking it.
# Sets the global PIPELINE. Call it BARE — never as `$(gate_or_exit)`, because a
# command substitution runs in a subshell and the `exit 0` below would kill only
# that subshell, leaving the hook running with an empty path and awk reading from
# a drained stdin. A guard that keeps going after its own gate said stop is worse
# than no guard.
gate_or_exit() {
  if PIPELINE=$(find_pipeline); then return 0; fi
  cat >/dev/null 2>&1 || true
  exit 0
}

# Prints the path, or returns 1.
find_pipeline() {
  local root common
  root=$(git rev-parse --show-toplevel 2>/dev/null) || return 1
  if [ -f "$root/pipeline.yml" ]; then printf '%s' "$root/pipeline.yml"; return 0; fi
  # In a worktree, --show-toplevel is the worktree. pipeline.yml is tracked in
  # every engine repo so it materializes there too, but fall back to the main
  # checkout for the case where it is not.
  common=$(git rev-parse --git-common-dir 2>/dev/null) || return 1
  case "$common" in /*) ;; *) common="$root/$common" ;; esac
  if [ -f "$(dirname "$common")/pipeline.yml" ]; then
    printf '%s' "$(dirname "$common")/pipeline.yml"; return 0
  fi
  return 1
}

# ── what the engine manages ──────────────────────────────────
#
# Emits "branch<TAB>username<TAB>org_name" per ENGINE-MANAGED environment.
#
# tier: sandbox rows are EXCLUDED, and that exclusion is load-bearing rather
# than tidy. A registered sandbox is board visibility and a release source; its
# owner deploys to it and merges into it every day. Treating one as engine-owned
# would block the daily loop this layer sits above.
#
# awk rather than a YAML parser: these hooks run in a client repo with whatever
# toolchain it happens to have, and a hook that needs `yq` installed is a hook
# that silently does not run. Conventional 2-space nesting is assumed; a parse
# that comes back empty means every caller declines to judge rather than guesses.
pipeline_envs() {
  awk '
    { line=$0; sub(/#.*/,"",line) }
    line ~ /^[A-Za-z_]/ {
      if (inenv && cur != "") emit()
      inenv=(line ~ /^environments:[ \t]*$/); cur=""; next
    }
    inenv && line ~ /^[ \t]+[A-Za-z_][A-Za-z0-9_.-]*:[ \t]*$/ {
      if (cur != "") emit()
      key=line; sub(/:[ \t]*$/,"",key); sub(/^[ \t]+/,"",key); cur=key
      br=""; un=""; on=""; tr="pipeline"; next
    }
    inenv && cur != "" {
      if (line ~ /^[ \t]+branch:/)   { v=line; sub(/^.*branch:[ \t]*/,"",v);   gsub(/[ \t"'"'"']/,"",v); br=v }
      if (line ~ /^[ \t]+username:/) { v=line; sub(/^.*username:[ \t]*/,"",v); gsub(/[ \t"'"'"']/,"",v); un=v }
      if (line ~ /^[ \t]+org_name:/) { v=line; sub(/^.*org_name:[ \t]*/,"",v); gsub(/[ \t"'"'"']/,"",v); on=v }
      if (line ~ /^[ \t]+tier:/)     { v=line; sub(/^.*tier:[ \t]*/,"",v);     gsub(/[ \t"'"'"']/,"",v); tr=v }
    }
    function emit() { if (tr != "sandbox" && br != "") print br "\t" un "\t" on; cur="" }
    END { if (inenv && cur != "") emit() }
  ' "$1" 2>/dev/null
}
