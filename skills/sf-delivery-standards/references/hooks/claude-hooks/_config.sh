#!/bin/bash
# Per-repo configuration + the master mode gate. SOURCED by _lib.sh, never run.
#
# ── WHY GIT CONFIG ──────────────────────────────────────────────────────────
# Every per-repo decision this stack makes lives in LOCAL git config under the
# `aleysian.` namespace. Four properties, none of which a tracked config file has:
#
#   invisible to the client   .git/config is never tracked, so nothing about how
#                             we work lands in their repo
#   shared by every worktree  linked worktrees read the clone's .git/config, so a
#                             worktree agent sees the same answers as the orchestrator
#   one call from any hook    git config aleysian.trunk — no parsing, no path math
#   diffable                  `audit` re-reads it and compares against the skill's
#                             expectations, which is how drift becomes visible
#
# ── THE MASTER GATE ─────────────────────────────────────────────────────────
# These hooks are installed at USER level (~/.claude/settings.json) and armed
# per-clone via core.hooksPath, which means they fire in every repo on the
# machine — including repos that have nothing to do with Salesforce.
#
# `aleysian.mode` is the switch. A repo that has never been through
# `/sf-delivery-standards init` has no such key, so sourcing _lib.sh exits 0
# immediately and the hook is a no-op. That is a deliberate design choice: the
# alternative (guards that try to be clever about which repo they are in) fails
# open in exactly the repos where it matters.
#
# Set HOOK_NO_GATE=1 BEFORE sourcing to opt out — install.sh and audit.sh do,
# because they run in a repo precisely to make it configured.

# ── Raw reads ───────────────────────────────────────────────────────────────

# cfg <key> [default] — one aleysian.* value. Never fails.
cfg() {
  local v
  v=$(git config --get "aleysian.$1" 2>/dev/null) || v=""
  [ -n "$v" ] && { printf '%s' "$v"; return 0; }
  printf '%s' "${2:-}"
}

# ── Derived accessors, each with the default that keeps v1 behaving like
#    the predecessor when init recorded nothing more specific ────────────────

mode()           { cfg mode; }                       # native | stealth
delivery()       { cfg delivery direct; }            # direct | engine | devops-center
trunk()          { cfg trunk main; }                 # org-synced branch, or DevOps Center landing branch
host()           { cfg host github; }                # github|gitlab|bitbucket|azure|none
review()         { local r; r=$(cfg review); [ -n "$r" ] && { printf '%s' "$r"; return; }
                   [ "$(host)" = "none" ] && printf 'local' || printf 'pr'; }
ticket_system()  { cfg ticket.system github; }       # github|jira|pattern|none
ticket_project() { cfg ticket.project; }             # Jira project key, e.g. SFO
ticket_remote()  { cfg ticket.remote ours; }         # ours | client
ticket_types()   { cfg ticket.types; }               # what the project HAS
ticket_cancreate(){ cfg ticket.cancreate; }          # what automation can CREATE
ticket_blocked() { cfg ticket.blocked; }             # "Type:Field,Field;Type:Field"
format_policy()  { cfg format client; }              # client | check | off
pmd_policy()     { cfg pmd block; }                  # block | advise
chainhooks()     { cfg chainhooks; }                 # path to the client's hook dir
drift_policy()   { cfg drift off; }                  # tracking | off (audittrail retired)
qa_policy()      { cfg qa ask; }                     # auto | ask | off — acceptance-criteria QA at step 7
org_alias()      { local a; a=$(cfg orgalias); printf '%s' "${a:-${ALEY_ORG_ALIAS:-${SOLO_ORG_ALIAS:-}}}"; }
devops_org_alias(){ cfg devops.orgalias; }            # DevOps Center control org
devops_project_id(){ cfg devops.projectid; }          # DevOps Center project record id
devops_pipeline_id(){ cfg devops.pipelineid; }        # pipeline whose topology owns the landing branch
devops_branch_pattern(){ cfg devops.branchpattern '^WI-[0-9]+$'; }
devops_work_model(){ cfg devops.workmodel isolated; } # isolated | shared
devops_integration_branch(){ cfg devops.integrationbranch; } # shared development-org branch
devops_environment(){ cfg devops.environment; }       # centralized deployment receipt environment
devops_development_branch_pattern(){ cfg devops.developmentbranchpattern '^dev/WI-[0-9]+$'; }
# require = one commit per ticket on trunk (the default, and right for one org)
# prefer  = advisory; the client's repo policy forbids squash
# merge   = the INVERSE: merge commits are required and --squash is refused. For a
#           repo whose promotion model cherry-picks merge commits (-m 1) and
#           reverts them (-m 1) — a squashed merge is neither selectively
#           promotable nor cleanly revertible there.
squash_policy()  { cfg squash require; }             # require | prefer | merge

# Branches this clone must never merge INTO. Space separated, empty by default,
# so a repo that never sets it behaves exactly as before this existed.
#
# Deliberately a plain branch list rather than anything that knows why: on one
# project these are release branches, on another a client-owned main, on another
# the environment branches some external system deploys from. The hook only needs
# to know the set — whatever populates it is what knows the reason.
protected()      { cfg protected; }

# How this clone stays aware of the remote trunk. Matters most on a SHARED org +
# SHARED branch, where several developers push to one branch and deploy to one
# sandbox: each has a local clone that can silently fall behind while the org and
# the remote move on. `fetch` (the default) refreshes origin/<trunk> so the drift
# is visible — at session start, and always before a deploy. `off` restores the
# old local-only behaviour for anyone who wants no session-start network.
# NEVER a value that pulls/merges into the tree — that mutation stays manual.
sync_policy()    { cfg sync fetch; }                 # fetch | off

is_native()  { [ "$(mode)" = "native" ]; }
is_stealth() { [ "$(mode)" = "stealth" ]; }
is_devops_center() { [ "$(delivery)" = "devops-center" ]; }
is_devops_shared() { is_devops_center && [ "$(devops_work_model)" = "shared" ]; }
is_devops_source_branch() { # <branch>
  printf '%s\n' "$1" | grep -qE "$(devops_branch_pattern)" && return 0
  is_devops_shared && printf '%s\n' "$1" | grep -qE "$(devops_development_branch_pattern)"
}

# Best-effort, non-interactive, timed refresh of origin/<trunk>. Shared by the
# session-start status and the deploy guard so both compare against a CURRENT
# remote rather than a stale cached ref — the drift a shared org + shared branch
# invites. It NEVER blocks or mutates: a missing perl, a slow network or an
# auth-less remote just leaves the cached ref in place and returns non-zero, and
# GIT_TERMINAL_PROMPT=0 guarantees it can never hang on a credential prompt. It
# updates ONLY the remote-tracking ref — not the working tree, not a local branch
# — so it is safe anywhere, including inside a worktree. (perl alarm survives the
# exec, same pattern audit.sh relies on.)
fetch_trunk() {   # [timeout-seconds]
  [ "$(host)" = "none" ] && return 1
  local t="${1:-8}" tr; tr=$(trunk)
  local rs="+refs/heads/$tr:refs/remotes/origin/$tr"
  if command -v perl >/dev/null 2>&1; then
    GIT_TERMINAL_PROMPT=0 perl -e 'alarm shift; exec @ARGV or exit 127' "$t" \
      git fetch --quiet origin "$rs" >/dev/null 2>&1
  else
    GIT_TERMINAL_PROMPT=0 git fetch --quiet origin "$rs" >/dev/null 2>&1
  fi
}

# ── The gate ────────────────────────────────────────────────────────────────
#
# Two conditions, both cheap. Order matters: `git config` in a non-repo prints
# nothing and returns non-zero, so the mode check alone is already safe.
#
# HOOK_DEFER_GATE=1 postpones this until hook_read_input() has read the command
# and retargeted — see sfds_retarget() below. Set it ONLY in a hook whose very
# first action is hook_read_input(), because a hook that defers and then never
# reads input is a hook with no gate at all.
# ── Leaving stdin unread breaks the caller's pipe ───────────────────────────
#
# A hook that exits without reading its payload leaves the harness's write failing
# with EPIPE. That matters here more than anywhere else in the stack: the gate below
# exits at SOURCE time in every repo with no aleysian.mode, these hooks are installed
# user-level and fire in every repo on the machine, so this is the single
# most-executed path in the whole stack — and it was the one leaving a broken pipe
# behind on every Bash call in every non-Salesforce project.
#
# Found by the sf-deploy-engine hooks hitting the same thing after they moved their
# own gate ahead of the payload parse. Their conclusion applies unchanged: a guard
# that can upset the harness invoking it is not worth the milliseconds it saves.
#
# Skipped when stdin is a terminal, where `cat` would block waiting for EOF — which
# is exactly how someone runs a hook by hand to see what it does.
sfds_drain_stdin() {
  [ -t 0 ] || cat >/dev/null 2>&1
  return 0
}

sfds_gate() {
  [ "${HOOK_NO_GATE:-}" = "1" ] && return 0
  # Spelled as an `if` rather than an && chain: a false chain leaves a non-zero
  # exit status behind, which is a trap for any caller that ever adds `set -e`.
  if [ "${HOOK_DEFER_GATE:-}" = "1" ] && [ "${SFDS_GATED:-}" != "1" ]; then
    return 0
  fi
  # ONE git subprocess on the inert path. `git config` in a non-repo prints
  # nothing and returns non-zero (see the note above), so an empty mode already
  # means "not a repo we manage" — the `git rev-parse --git-dir` that used to run
  # first was a redundant second subprocess on the single most-executed path in
  # the stack (every Bash/Edit call in every repo on the machine). Dropping it
  # roughly halves the git-spawn cost of the inert path; measured ~59ms -> ~22ms
  # wall-clock for a Bash matcher group of 10 guards in an unmanaged repo.
  [ -n "$(mode)" ] || { sfds_drain_stdin; exit 0; }
  return 0
}

# ── Judging the right repo ──────────────────────────────────────────────────
#
# Every `aleysian.*` read goes through `git config`, which answers for the repo
# containing the process's cwd. A hook's cwd is the SESSION's project directory,
# not the repo the command it is inspecting will act on. When those differ, every
# guard applies the wrong project's rules — observed: a `git commit` in the
# skills repo blocked by 64-Org's Jira ref rules, in a repo that has no
# `aleysian.mode` at all and where every guard should have been inert.
#
# The fix is to stand where the command stands. chdir'ing the hook process is
# enough on its own: `cfg()`, `current_branch "."`, `state_dir "."` and the
# `$PWD`-relative path resolution in the guards then all describe the target,
# with no repo argument threaded through any of them. It is also MORE correct for
# relative paths, because a command's relative paths are relative to the
# directory that command runs in — which is precisely where we now are.
#
# Then re-run the gate. That is the load-bearing half: the target repo gets the
# same "no mode means inert" treatment cwd would have got, so a command aimed at
# an unmanaged repo is not judged by this one's rules, in either direction.
#
# Same lesson as source_tree_root(): judge the target, not the shell.
sfds_retarget() {
  local dir="${1:-}" top
  if [ -n "$dir" ] && [ -d "$dir" ]; then
    top=$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null) && cd "$top" 2>/dev/null
  fi
  # A non-repo, or a path we could not resolve, leaves cwd alone: the command
  # acts outside any repo we manage, and cwd's answer is the only one available.
  SFDS_GATED=1
  sfds_gate
}

# ── State directory ─────────────────────────────────────────────────────────
#
# All machine-local state moves INSIDE .git/, in the common dir.
#
# The predecessor kept it at <root>/.claude/.deploy-log and gitignored it. That
# works in a repo we own; in a client's repo it means either committing our
# bookkeeping to their tree or adding entries to THEIR .gitignore. Both are
# visible changes to their artifacts for a reason that is none of their business.
#
# $(git rev-parse --git-common-dir)/aleysian/ is untracked by construction — it
# is not in any working tree, so there is nothing to ignore and nothing to
# commit. It is per-clone (correct: these logs describe THIS clone's history
# against the org) and common across worktrees (correct: a worktree's validate
# must be visible to the orchestrator's merge gate).
state_dir() {
  local d
  d=$(git -C "${1:-.}" rev-parse --git-common-dir 2>/dev/null) || return 1
  case "$d" in /*) ;; *) d="$(cd "${1:-.}" && pwd)/$d" ;; esac
  d="$(cd "$d" 2>/dev/null && pwd)/aleysian" || return 1
  mkdir -p "$d" 2>/dev/null
  printf '%s' "$d"
}

# ── Ticket reference pattern ────────────────────────────────────────────────
#
# What commit-msg requires, and what the label/close/DoD automation reads back
# out of commit messages. Per-system defaults, overridable by init.
#
# GitHub's pattern is KEYWORD-ANCHORED for a reason that survives the fork: a
# bare `#N` scan reads issue numbers out of ordinary prose, which is enough to
# label and unlock tickets nobody touched. Jira needs no keyword — `SFO-123` is
# already a distinctive token, and Jira's own git integrations index it.
default_ref_pattern() {
  case "$(ticket_system)" in
    github)  printf '%s' '(refs?|fix(es|ed)?|close[sd]?|resolve[sd]?)[[:space:]]+#[0-9]+' ;;
    jira)    local p; p=$(ticket_project)
             if [ -n "$p" ]; then printf '%s' "${p}-[0-9]+"
             else printf '%s' '[A-Z][A-Z0-9]+-[0-9]+'; fi ;;
    pattern) printf '%s' '.+' ;;   # init should have recorded something real
    *)       printf '%s' '.*' ;;
  esac
}

ref_pattern() { cfg ticket.pattern "$(default_ref_pattern)"; }

# One ticket ref per line, extracted from a commit message body on stdin.
# GitHub yields bare numbers (12); every other system yields whole keys (SFO-12),
# because that is what their CLIs take as an argument.
extract_refs() {
  local re; re=$(ref_pattern)
  if [ "$(ticket_system)" = "github" ]; then
    grep -oiE "$re" | grep -oE '[0-9]+$' | sort -u
  else
    grep -oE "$re" | sort -u
  fi
}

# How a ticket is named in prose, for hook messages. Never build a CLI argument
# from this — use the ref itself.
ticket_label() {
  case "$(ticket_system)" in
    github) printf '#%s' "$1" ;;
    *)      printf '%s' "$1" ;;
  esac
}

# An example ref, for error messages and the CLAUDE.md block.
ticket_example() {
  case "$(ticket_system)" in
    github)  printf 'refs #42' ;;
    jira)    printf '%s-42' "$(ticket_project 2>/dev/null || echo ABC)" ;;
    pattern) printf '%s' "$(cfg ticket.example 'the project ticket token')" ;;
    *)       printf 'no ticket system configured' ;;
  esac
}
