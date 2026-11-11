#!/bin/bash
# audit.sh — verify every installed piece of the stack. Read-only by default.
#
#   audit.sh            report only
#   audit.sh --fix      self-heal the mechanical items (1-8); never touches 9-11
#
# WHY AUDIT IS A FIRST-CLASS SUB-COMMAND
# --------------------------------------
# Every part of this stack can be silently disabled, and none of the failures look
# like failures. hooksPath gets repointed by someone else's npm install. A hook
# loses its exec bit and git skips it without a word. The CLAUDE.md block gets
# edited by the very agent it constrains. An install goes stale against the skill
# driving it. In each case the work continues and looks fine — which is worse than
# a visible break, because nobody knows to be careful.
#
# So the question this answers is not "is it installed" but "is it still armed".
#
# Exit codes: 0 = clean, 1 = problems found (or, with --fix, problems remaining).
# Judgment items never affect the exit code — they are for a human to read.

set -u

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
HOME_DIR="$HOME/.aleysian"
FIX=0
PROBE=1
for a in "$@"; do
  case "$a" in
    --fix)      FIX=1 ;;
    # Sections 9-11 make up to three sequential network calls (org resolve, tracker
    # auth, drift preview) at 20-30s each, plus `sf` CLI startup. Against a real repo
    # that can exceed two minutes, which is long enough to get killed by whatever is
    # driving it — and a diagnostic that gets killed reports nothing, which is worse
    # than any finding it would have produced. --no-probe runs everything that is
    # local and deterministic, and is what the regression suite uses.
    --no-probe) PROBE=0 ;;
  esac
done

# ── Which libraries to read, and why the skew matters ────────────────────────
#
# The ARMED copies, deliberately: this script reports on what is actually
# installed, and reading the skill's own libraries would hide every version skew
# it exists to find.
#
# But the skew cuts both ways, and the other direction is fatal. This script ships
# WITH the skill, so it can call an accessor an older install does not have yet —
# and an undefined function is a `command not found` on stderr, which the stderr
# guard below correctly turns into "audit could NOT complete cleanly". Correct, and
# useless: the entire run is lost to one missing one-line accessor, including every
# check that would have worked. That happened for real — `protected()` arrived in
# the skill and every audit against a v1 install died on it.
#
# So: read the armed copies, then verify they provide what this script calls. A gap
# is a REPORTED failure, not a fatal one — fall back to the skill's own libraries so
# the remaining sections still evaluate and the user gets a diagnosis instead of a
# shell error.
#
# _lib.sh is sourced rather than _config.sh directly because it pulls in _config.sh
# and _ticket.sh itself AND provides the state-path helpers (checklist, deploy_log)
# that this script also calls.
HOOK_NO_GATE=1
LIB_SRC="$HOME_DIR/claude-hooks"
[ -f "$LIB_SRC/_lib.sh" ] || LIB_SRC="$SKILL_DIR/references/hooks/claude-hooks"
LIB_OWN="$SKILL_DIR/references/hooks/claude-hooks"
. "$LIB_SRC/_lib.sh"
. "$LIB_SRC/_block.sh"

# Every library function this script calls. Extend it when you add a call, or the
# next skew is silent again — and silent is how this one survived.
LIB_SKEW=""
for fn in mode delivery is_devops_center is_devops_shared trunk host review ticket_system ticket_remote ticket_project \
          format_policy pmd_policy drift_policy squash_policy \
          org_alias devops_org_alias devops_project_id devops_pipeline_id devops_branch_pattern \
          devops_work_model devops_integration_branch devops_environment devops_development_branch_pattern \
          protected chainhooks cfg state_dir checklist \
          ticket_cli_present block_status block_extract block_render_body \
          block_recorded_hash main_repo_root; do
  command -v "$fn" >/dev/null 2>&1 || LIB_SKEW="$LIB_SKEW $fn"
done
if [ -n "$LIB_SKEW" ] && [ "$LIB_SRC" != "$LIB_OWN" ]; then
  . "$LIB_OWN/_lib.sh"
  . "$LIB_OWN/_block.sh"
fi

# Every network call below goes through this. An unauthenticated or misconfigured CLI
# can block indefinitely waiting on a prompt or a socket — and audit ran for two
# minutes before being killed during development, which is a worse failure than any
# it reports: a diagnostic that hangs gets skipped, and then nothing is verified.
#
# macOS ships no `timeout`/`gtimeout`, so perl's alarm is the portable option.
with_timeout() {
  local secs="$1"; shift
  if command -v perl >/dev/null 2>&1; then
    perl -e 'alarm shift; exec @ARGV or exit 127' "$secs" "$@" 2>/dev/null
  else
    "$@" 2>/dev/null
  fi
}

# ── macOS bash 3.2 cannot parse `case` inside $() ────────────────────────────
#
#   /bin/bash -c 'x="$(case a in a) echo y ;; esac)"'
#   -> syntax error near unexpected token `newline'
#
# bash 5 accepts it, `bash -n` accepts it (substitutions are not expanded at parse
# time), and the failure is a runtime stderr message plus an EMPTY result — so the
# enclosing test silently evaluates false. That is how this script once reported a
# tracker CLI as "not authenticated" when it was authenticated.
#
# Every command string that varies by ticket system is therefore built with if/elif in
# a named function. Do not "tidy" these back into a case inside $(). Only GitHub has a
# shell-checkable tracker CLI now — Jira runs through the Rovo MCP, agent-side.
auth_probe_cmd() {
  if [ "$(ticket_system)" = "github" ]; then printf 'gh auth status'
  else printf 'false'; fi
}

# ── Nothing may report clean after writing to stderr ─────────────────────────
#
# The parse bug above produced a shell error on stderr and then "Audit clean". A section
# that failed to EVALUATE is not a passing section, and "clean" is the word someone
# trusts before moving on. So stderr is captured for the whole run and checked at the end.
STDERR_LOG=$(mktemp)
exec 3>&2 2>"$STDERR_LOG"
# fd 2 points at STDERR_LOG. Writing the captured text back to fd 2 would append
# the file to itself forever; preserve the caller's original stderr on fd 3.
cleanup_stderr() { cat "$STDERR_LOG" >&3 2>/dev/null; rm -f "$STDERR_LOG"; exec 3>&-; }

FAIL=0
ok()    { printf '  \033[32mok\033[0m    %s\n' "$*"; }
bad()   { printf '  \033[31mFAIL\033[0m  %s\n' "$*"; FAIL=1; }
fixed() { printf '  \033[33mfixed\033[0m %s\n' "$*"; }
info()  { printf '        %s\n' "$*"; }
sect()  { printf '\n\033[1m%s\033[0m\n' "$*"; }

git rev-parse --git-dir >/dev/null 2>&1 || { echo "audit.sh: not a git repository."; exit 1; }
ROOT=$(git rev-parse --show-toplevel); cd "$ROOT"

# ── The ref that decides what a worktree contains ────────────────────────────
#
# A worktree materialises tracked content from the branch it was cut from, and
# tooling conventionally cuts from origin/<trunk> rather than the local branch
# (64-Org's scripts/new-ticket does exactly that). So origin is the authority for
# "will a worktree get the contract".
#
# Reading the LOCAL branch produced an immediate false alarm on a clone whose local
# trunk merely lagged origin: the block was on origin/<trunk>, every worktree had
# it, and audit said no CLAUDE.md was committed on trunk. A false alarm costs the
# same trust as a false clean — people stop reading the output either way.
#
# Preference: the branch's configured upstream, then origin/<trunk>, then the local
# branch. host=none has no remote and falls through to local, which is correct there.
trunk_ref() {
  local t up
  t=$(trunk)
  up=$(git rev-parse --symbolic-full-name "${t}@{upstream}" 2>/dev/null)
  if [ -n "$up" ]; then printf '%s' "$up"; return 0; fi
  if git rev-parse --verify --quiet "origin/$t" >/dev/null 2>&1; then
    printf 'origin/%s' "$t"; return 0
  fi
  if git rev-parse --verify --quiet "$t" >/dev/null 2>&1; then printf '%s' "$t"; return 0; fi
  return 0
}

# Machine-local state and the project-local org belong to the ORIGINAL clone, not
# to whichever worktree this happens to run in.
MAIN_ROOT=$(main_repo_root "." 2>/dev/null || echo "$ROOT")
[ -n "$MAIN_ROOT" ] || MAIN_ROOT="$ROOT"

printf '\n\033[1msf-delivery-standards audit\033[0m  —  %s\n' "$ROOT"

# ═══ 1. config complete and internally coherent ═══════════════
sect "1. Config (git config aleysian.*)"
if [ -z "$(mode)" ]; then
  bad "aleysian.mode is unset — this repo has never been initialised, and the ENTIRE"
  info "stack is inert here (every hook exits 0 on a repo with no mode). Run init."
  printf '\n'
  exit 1
fi
ok "mode=$(mode)  delivery=$(delivery)  trunk=$(trunk)  host=$(host)  review=$(review)  sync=$(sync_policy)"
ok "ticket=$(ticket_system)/$(ticket_remote)$([ -n "$(ticket_project)" ] && printf ' project=%s' "$(ticket_project)")"
ok "format=$(format_policy)  pmd=$(pmd_policy)  drift=$(drift_policy)  squash=$(squash_policy)  qa=$(qa_policy)"
[ -n "$(protected)" ] && ok "protected (never merge into): $(protected)"

case "$(mode)" in native|stealth) ;; *) bad "mode='$(mode)' is not native or stealth" ;; esac
case "$(delivery)" in direct|engine|devops-center) ;; *) bad "delivery='$(delivery)' is not direct, engine, or devops-center" ;; esac
if [ -f pipeline.yml ] && [ "$(squash_policy)" != "merge" ]; then
  bad "pipeline.yml is present but aleysian.squash=$(squash_policy). The delivery engine"
  info "promotes and reverts merge commits. Set: git config aleysian.squash merge"
fi
if is_devops_center; then
  [ ! -f pipeline.yml ] || bad "delivery=devops-center but pipeline.yml is present. This repo must not also be owned by sf-deploy-engine."
  [ "$(squash_policy)" = "require" ] || bad "delivery=devops-center requires aleysian.squash=require"
  for p in "$(trunk)" main; do
    case " $(protected) " in *" $p "*) ;; *) bad "delivery=devops-center requires '$p' in aleysian.protected" ;; esac
  done
  printf 'WI-000001\n' | grep -qE "$(devops_branch_pattern)" \
    || bad "aleysian.devops.branchpattern does not match the canonical WI-000001 shape"
  [ "$(ticket_system)" = "pattern" ] || bad "delivery=devops-center requires ticket.system=pattern for WI association"
  printf 'WI-000001\n' | grep -qE "$(cfg ticket.pattern)" \
    || bad "aleysian.ticket.pattern does not match the canonical WI-000001 shape"
  [ -n "$(devops_org_alias)" ] || bad "delivery=devops-center requires aleysian.devops.orgalias for sf devops commands"
  [ -n "$(devops_project_id)" ] || bad "delivery=devops-center requires aleysian.devops.projectid for WI lookup and review"
  [ -n "$(devops_pipeline_id)" ] || bad "delivery=devops-center has only a provisional landing branch. Rerun init with --devops-pipeline-id so topology is authoritative."
  case "$(devops_work_model)" in isolated|shared) ;; *) bad "aleysian.devops.workmodel='$(devops_work_model)' is not isolated or shared" ;; esac
  if is_devops_shared; then
    [ "$(host)" = "github" ] || bad "shared DevOps Center development requires host=github for centralized deployment receipts"
    [ -n "$(devops_integration_branch)" ] || bad "shared DevOps Center development requires aleysian.devops.integrationbranch"
    [ -n "$(devops_environment)" ] || bad "shared DevOps Center development requires aleysian.devops.environment"
    printf 'dev/WI-000001\n' | grep -qE "$(devops_development_branch_pattern)" \
      || bad "aleysian.devops.developmentbranchpattern does not match dev/WI-000001"
    case " $(protected) " in
      *" $(devops_integration_branch) "*) ;;
      *) bad "shared DevOps Center development requires '$(devops_integration_branch)' in aleysian.protected" ;;
    esac
    if [ -n "$(devops_integration_branch)" ] \
       && ! git rev-parse --verify --quiet "origin/$(devops_integration_branch)" >/dev/null 2>&1 \
       && ! git rev-parse --verify --quiet "$(devops_integration_branch)" >/dev/null 2>&1; then
      bad "shared integration branch '$(devops_integration_branch)' does not resolve locally or on origin"
    fi
  fi
fi
if [ -z "$(trunk_ref)" ]; then
  bad "aleysian.trunk='$(trunk)' resolves to no branch here — not locally, and not as"
  info "origin/$(trunk). Nothing that compares against trunk can evaluate: not the merge"
  info "gate, not the deploy gate, not the contract-on-trunk check in section 6."
elif [ "$(trunk_ref)" != "$(trunk)" ]; then
  ok "trunk ref: $(trunk_ref) (the ref worktrees are cut from)"
fi
if [ "$(host)" = "none" ] && [ "$(review)" != "local" ]; then
  if [ "$FIX" = "1" ]; then git config aleysian.review local; fixed "review=local (host=none has no PR to review)"
  else bad "host=none but review=$(review) — incoherent. The merge gate would look for a record nothing writes."; fi
fi
if [ "$(ticket_system)" = "jira" ] && [ -z "$(ticket_project)" ]; then
  bad "ticket.system=jira but ticket.project is unset — the ref pattern falls back to"
  info "a generic [A-Z]+-[0-9]+, which matches any project's keys including the client's."
fi
if [ -z "$(org_alias)" ]; then
  bad "aleysian.orgalias is unset — sf commands in a fresh worktree fall through to the"
  info "machine's GLOBAL default org. Fix: git config aleysian.orgalias <alias>"
else
  # ── the alias is only half the answer ──────────────────────────────────────
  #
  # aleysian.orgalias records our INTENT. Deploys resolve their org from
  # .sf/config.json, and guard-sf-flags.sh hard-blocks --target-org, so that file is
  # the single thing deciding where a deploy lands. If it disagrees with the alias,
  # or is missing, the two halves of the configuration contradict each other and
  # nothing said so — that is the exact condition that dead-ended a real deploy step
  # with NoDefaultEnvError while every other check reported clean.
  #
  # Read from the MAIN checkout: real deploys run there, and that is where install.sh
  # writes it. A worktree's own .sf/config.json is set separately by
  # ensure-worktree-config.sh.
  WANT_ORG=$(org_alias)
  SFCFG="$MAIN_ROOT/.sf/config.json"
  if [ ! -f "$SFCFG" ]; then
    bad "no $SFCFG — the main checkout has no project-local target-org, so a real deploy"
    info "from there fails with NoDefaultEnvError, and --target-org is blocked by design."
    if [ "$FIX" = "1" ] && command -v sf >/dev/null 2>&1; then
      ( cd "$MAIN_ROOT" && sf config set "target-org=$WANT_ORG" >/dev/null 2>&1 ) \
        && fixed "set target-org=$WANT_ORG in $MAIN_ROOT" \
        || info "could not set it; run by hand: cd '$MAIN_ROOT' && sf config set target-org=$WANT_ORG"
    else
      info "Fix: cd '$MAIN_ROOT' && sf config set target-org=$WANT_ORG"
    fi
  elif ! command -v jq >/dev/null 2>&1; then
    bad "$SFCFG exists but jq is missing, so its target-org cannot be read — whether the"
    info "org this repo deploys to matches aleysian.orgalias is UNVERIFIED. Install jq."
  else
    HAVE_ORG=$(jq -r '."target-org" // empty' "$SFCFG" 2>/dev/null || echo "")
    if [ "$HAVE_ORG" = "$WANT_ORG" ]; then
      ok "target-org=$HAVE_ORG agrees with aleysian.orgalias"
    elif [ -z "$HAVE_ORG" ]; then
      bad "$SFCFG has no target-org — deploys from the main checkout fail with"
      info "NoDefaultEnvError. Fix: cd '$MAIN_ROOT' && sf config set target-org=$WANT_ORG"
    else
      # Never auto-fixed, even with --fix: someone pointed this clone at that org for
      # a reason this script cannot see, and silently repointing it would redirect
      # every deploy made from here.
      bad "target-org='$HAVE_ORG' but aleysian.orgalias='$WANT_ORG' — these contradict."
      info "Every deploy from the main checkout goes to '$HAVE_ORG', while every gate,"
      info "message and worktree default in this stack assumes '$WANT_ORG'. Not"
      info "auto-fixed: reconcile it deliberately, because one of the two is wrong and"
      info "this script cannot tell which."
      info "  cd '$MAIN_ROOT' && sf config set target-org=$WANT_ORG    # or fix the alias"
    fi
  fi
fi

# ═══ 2. core.hooksPath and the git hooks ══════════════════════
sect "2. Git hooks"
WANT="$HOME_DIR/githooks"
CUR=$(git config core.hooksPath || echo "")
if [ "$CUR" = "$WANT" ]; then ok "core.hooksPath -> $WANT"
elif [ "$FIX" = "1" ]; then
  [ -n "$CUR" ] && [ -d "$CUR" ] && git config aleysian.chainhooks "$CUR"
  git config core.hooksPath "$WANT"; fixed "core.hooksPath was '$CUR', now $WANT"
else bad "core.hooksPath is '${CUR:-unset}', not $WANT — git hooks are NOT running"; fi

for h in pre-commit commit-msg; do
  if [ ! -f "$WANT/$h" ]; then bad "$WANT/$h is missing"
  elif [ ! -x "$WANT/$h" ]; then
    if [ "$FIX" = "1" ]; then chmod +x "$WANT/$h"; fixed "chmod +x $h"
    else bad "$WANT/$h is not executable — git skips it SILENTLY"; fi
  elif ! head -1 "$WANT/$h" | grep -q '^#!'; then bad "$WANT/$h has no shebang"
  else ok "$h present, executable, shebang'd"; fi
done

COMMON=$(git rev-parse --git-common-dir); case "$COMMON" in /*) ;; *) COMMON="$ROOT/$COMMON" ;; esac
for h in pre-commit commit-msg; do
  [ -f "$COMMON/hooks/$h" ] && bad "stale $COMMON/hooks/$h — ignored (hooksPath wins) but misleads anyone debugging"
done

# ═══ 3. chained hooks still exist ═════════════════════════════
sect "3. Chained project hooks"
CHAIN=$(chainhooks)
if [ -z "$CHAIN" ]; then ok "none recorded (nothing to chain)"
elif [ -d "$CHAIN" ]; then
  ok "chaining $CHAIN"
  for h in pre-commit commit-msg; do
    [ -f "$CHAIN/$h" ] && { [ -x "$CHAIN/$h" ] && info "  their $h will run after ours" \
      || bad "their $CHAIN/$h is not executable — it will be skipped"; }
  done
else bad "aleysian.chainhooks='$CHAIN' no longer exists — the project's own gates are not running"; fi

# Every hook this skill installs. ONE list, because section 4 checks that each is
# configured and section 4b checks that nothing in the repo duplicates one — and
# two lists that must agree are a bug waiting for someone to edit only one.
SKILL_HOOKS="verify-git-hooks session-status guard-force-app guard-force-app-bash
guard-sf-deploy guard-sf-flags guard-worktree-nesting guard-closing-keywords
guard-devops-handoff guard-pr-merge guard-push
record-escape-hatch record-validate auto-label-deploy post-merge-nudge
stop-dod-check ensure-worktree-config"
SKILL_HOOK_COUNT=$(printf '%s\n' $SKILL_HOOKS | grep -c .)

# The state files this skill owns. A repo hook that writes any of these names is
# writing our ledger, whatever it calls itself — see section 4b.
SKILL_LEDGERS="deploy-log validate-log hatch-log pending-jobs dod-state approve-log
drift-log ship-log client-checklist"

# ═══ 4. user-level agent hook settings ════════════════════════
CLAUDE_SETTINGS="$HOME/.claude/settings.json"
CODEX_SETTINGS="$HOME/.codex/hooks.json"
SETTINGS_FILES=("$CLAUDE_SETTINGS" "$CODEX_SETTINGS")
sect "4. Agent hooks (Claude and Codex)"
if ! command -v jq >/dev/null 2>&1; then
  bad "jq is not installed, so this cannot be verified (and install cannot merge safely)"
else
  for SETTINGS in "${SETTINGS_FILES[@]}"; do
    if [ ! -f "$SETTINGS" ] || ! grep -q '/.aleysian/claude-hooks/' "$SETTINGS" 2>/dev/null; then
      if [ "$FIX" = "1" ]; then
        "$SKILL_DIR/scripts/install.sh" --machine-only --platform both >/dev/null 2>&1 \
          && fixed "registered the delivery hooks in both hosts (missing from $SETTINGS)" \
          || bad "dual-host re-arm failed — run scripts/install.sh --machine-only --platform both"
      else
        bad "the stack is not registered in $SETTINGS — that host's agent guards are OFF"
      fi
      continue
    fi
    CONFIGURED=$(jq -r '.hooks // {} | to_entries[] | .value[]? | .hooks[]? | select(.type=="command") | .command' \
                   "$SETTINGS" 2>/dev/null || true)
    MISSING=()
    for w in $SKILL_HOOKS; do
      printf '%s\n' "$CONFIGURED" | grep -qF "$w.sh" || MISSING+=("$w")
    done
    if [ "${#MISSING[@]}" -eq 0 ]; then ok "all $SKILL_HOOK_COUNT hooks configured in $SETTINGS"
    elif [ "$FIX" = "1" ]; then
      "$SKILL_DIR/scripts/install.sh" --machine-only --platform both >/dev/null 2>&1 \
        && fixed "re-merged hook entries in both hosts (missing from $SETTINGS: ${MISSING[*]})" \
        || bad "re-merge failed — run scripts/install.sh --machine-only and read the output"
    else bad "NOT configured in $SETTINGS, so these guards are OFF there: ${MISSING[*]}"; fi

    # A hook named in settings but absent or unreadable on disk is the same silent hole.
    while IFS= read -r cmd; do
      [ -z "$cmd" ] && continue
      S=${cmd%% *}
      case "$S" in "$HOME_DIR"/*) ;; *) continue ;; esac
      [ -f "$S" ] || { bad "$S is configured but does not exist"; continue; }
      [ -x "$S" ] || { if [ "$FIX" = "1" ]; then chmod +x "$S"; fixed "chmod +x $(basename "$S")"
                       else bad "$(basename "$S") is not executable — that guard is OFF"; fi }
    done < <(printf '%s\n' "$CONFIGURED")
  done

  # Retrieve deny rules are no longer part of this stack. This check is Claude-only:
  # Codex hooks.json has no permissions.deny surface. A deny rule in Claude's
  # user-level file is enforced by the harness in EVERY repo on the machine, so it
  # over-blocked retrieves in unrelated projects (req 1). Retrieve-blocking now
  # lives in guard-sf-flags.sh, which is gated and fires only in a managed repo.
  # So the correct state is ABSENT; a rule still present is stale from an older
  # install, and --fix retracts it by re-arming.
  DENY=$(jq -r '[.permissions.deny[]?] | join(" ")' "$CLAUDE_SETTINGS" 2>/dev/null || true)
  case "$DENY" in
    *"sf project retrieve"*|*"sfdx project retrieve"*|*"sfdx force:source:retrieve"*)
      if [ "$FIX" = "1" ]; then
        "$SKILL_DIR/scripts/install.sh" --machine-only >/dev/null 2>&1 \
          && fixed "retracted stale machine-wide retrieve deny rules" \
          || bad "could not retract stale deny rules — run scripts/install.sh --machine-only"
      else
        bad "stale machine-wide retrieve deny rule(s) present — they over-block retrieves in unrelated projects (req 1); rerun with --fix to retract"
      fi ;;
    *) ok "no machine-wide retrieve deny rules (retrieve-blocking is scoped to managed repos via guard-sf-flags.sh)" ;;
  esac
fi

# ═══ 4b. hooks the REPO wires for itself ══════════════════════
#
# Sections 1-4 all answer "is OUR stack armed". None of them can see a second
# stack. That blind spot has already cost: 64-Org carried three hooks of its own
# in .claude/hooks/, forked from this skill's ancestor before this skill existed.
# Adopting the skill installed a newer implementation ALONGSIDE the fork instead of
# retiring it, and the ledger migration then left one of the forked hooks writing
# to a path no reader reads. Audit reported clean, exit 0, the whole time — every
# question it asked was answered correctly and none of them was this one.
#
# So: enumerate them, and refuse to call a repo clean while any of them is
# unaccounted for. Two failures are unconditional, because they are duplication
# rather than coexistence:
#
#   name collision    a repo hook named like one of ours is a second
#                     implementation of a job that already has one
#   ledger collision  a repo hook that writes one of our state files is a
#                     competing writer, whatever it is named. This is the check
#                     that catches the real case: `record-deploy.sh` collides
#                     with NO skill hook name, so the name check alone misses it.
#
# Anything else is unclassifiable from here — a client repo may legitimately run
# its own formatter or test hook that has nothing to do with us. Per the rule for
# every check in this file, "cannot tell" reports FAIL, not ok. But it is a FAIL a
# human clears once, by recording the review in aleysian.repohooks — because a
# check that fails forever gets ignored, which costs exactly what a check that
# never fires costs.
sect "4b. Repo-level hooks (Claude/Codex project config)"
REPO_HOOKS=""
if command -v jq >/dev/null 2>&1; then
  for S in "$ROOT/.claude/settings.json" "$ROOT/.claude/settings.local.json"; do
    [ -f "$S" ] || continue
    REPO_HOOKS="$REPO_HOOKS
$(jq -r '.hooks // {} | to_entries[] | .value[]? | .hooks[]? | select(.type=="command") | .command' \
     "$S" 2>/dev/null || true)"
  done
  if [ -f "$ROOT/.codex/hooks.json" ]; then
    REPO_HOOKS="$REPO_HOOKS
$(jq -r '.hooks // {} | to_entries[] | .value[]? | .hooks[]? | select(.type=="command") | .command' \
     "$ROOT/.codex/hooks.json" 2>/dev/null || true)"
  fi
fi
REPO_HOOKS=$(printf '%s\n' "$REPO_HOOKS" | grep . || true)

if ! command -v jq >/dev/null 2>&1; then
  bad "jq is not installed, so repo-level hooks cannot be enumerated — a second hook"
  info "stack in this repo would be invisible. Install jq (brew install jq)."
elif [ -z "$REPO_HOOKS" ]; then
  ok "none — this repo wires no hooks of its own"
else
  ACKED=$(cfg repohooks)
  UNACKED=""
  while IFS= read -r cmd; do
    [ -z "$cmd" ] && continue
    RH=${cmd%% *}                       # drop any arguments
    RB=$(basename "$RH")
    RB_NOEXT=${RB%.sh}

    # Resolve for reading. Repo-level commands are conventionally relative.
    RP="$RH"; case "$RP" in /*) ;; *) RP="$ROOT/$RH" ;; esac

    COLLIDE=""
    for w in $SKILL_HOOKS; do
      [ "$RB_NOEXT" = "$w" ] && COLLIDE="name"
    done
    if [ -z "$COLLIDE" ] && [ -f "$RP" ]; then
      for L in $SKILL_LEDGERS; do
        grep -q -- "$L" "$RP" 2>/dev/null && { COLLIDE="ledger:$L"; break; }
      done
    fi

    case "$COLLIDE" in
      name)
        bad "$RB duplicates this skill's $RB_NOEXT.sh — two implementations of one job."
        info "One of them is stale, and nothing reports which. Retire the repo copy, or"
        info "rename it if it genuinely does something different." ;;
      ledger:*)
        bad "$RB writes this skill's '${COLLIDE#ledger:}' state — a competing ledger writer."
        info "Two writers means the readers see whichever wrote last, or a file nobody"
        info "reads. Check which path it writes: ours live in \$(git rev-parse"
        info "--git-common-dir)/aleysian/, and a hook still writing an older location is"
        info "recording into the void. Retire it, or point it at the shared helpers." ;;
      *)
        if printf '%s\n' "$ACKED" | tr ' ' '\n' | grep -qxF "$RB"; then
          info "$RB — reviewed and accepted (aleysian.repohooks)"
        else
          UNACKED="$UNACKED $RB"
        fi ;;
    esac
  done < <(printf '%s\n' "$REPO_HOOKS")

  if [ -n "$UNACKED" ]; then
    bad "unreviewed repo-level hook(s):$UNACKED"
    info "These may be fine — a repo's own formatter or test hook is none of our"
    info "business. But nothing here can tell that from a second copy of one of our"
    info "guards, and an unexamined parallel stack is how the last one survived two"
    info "sessions. Read them, then record that you did:"
    info "  git config aleysian.repohooks \"$(printf '%s' "${ACKED:+$ACKED }")$(printf '%s' "$UNACKED" | sed 's/^ //')\""
  fi
fi

# ═══ 5. install version vs skill version ══════════════════════
sect "5. Install version"
if [ -n "$LIB_SKEW" ]; then
  bad "the INSTALLED libraries do not provide what this audit calls:$LIB_SKEW"
  info "So the armed hooks are older than the skill driving this check, and the two"
  info "disagree about what configuration even exists. This run fell back to the"
  info "skill's own libraries so the sections above could still evaluate — they"
  info "describe the skill, NOT what is currently enforcing. Refresh the install:"
  info "  $SKILL_DIR/scripts/install.sh --machine-only"
fi
if [ ! -d "$HOME_DIR" ]; then bad "$HOME_DIR does not exist — nothing is installed"
elif [ ! -f "$HOME_DIR/VERSION" ]; then bad "$HOME_DIR/VERSION missing — cannot tell what is installed"
else
  INST=$(head -1 "$HOME_DIR/VERSION" | tr -d '[:space:]')
  if [ "$INST" = "$BLOCK_VERSION" ]; then ok "v$INST matches the skill"
  elif [ "$FIX" = "1" ]; then
    "$SKILL_DIR/scripts/install.sh" --machine-only >/dev/null 2>&1 && fixed "refreshed v$INST -> v$BLOCK_VERSION"
  else bad "installed v$INST, skill is v$BLOCK_VERSION — the hooks running are not the hooks documented"; fi
fi

# Subagents shipped by the skill. Not enforcement — a capability — so a missing or
# stale one never fails the audit's exit code; it is reported for a human to refresh.
# The agent that IS present must match the skill's copy, or the doctrine running is
# not the doctrine documented (same reasoning as the version check above).
AGENT_SRC="$SKILL_DIR/references/agents"
AGENT_DST="$HOME/.claude/agents"
if [ -d "$AGENT_SRC" ]; then
  for f in "$AGENT_SRC"/*.md; do
    [ -e "$f" ] || continue
    a=$(basename "$f")
    if [ ! -f "$AGENT_DST/$a" ]; then
      if [ "$FIX" = "1" ]; then mkdir -p "$AGENT_DST"; cp "$f" "$AGENT_DST/" && fixed "installed subagent $a"
      else info "subagent $a is not installed in $AGENT_DST — install.sh --machine-only (or audit --fix)"; fi
    elif ! cmp -s "$f" "$AGENT_DST/$a"; then
      if [ "$FIX" = "1" ]; then cp "$f" "$AGENT_DST/" && fixed "refreshed subagent $a"
      else info "subagent $a differs from the skill's copy — install.sh --machine-only (or audit --fix)"; fi
    else ok "subagent $a present and current"; fi
  done
fi

# ═══ 6. the host instruction managed block ════════════════════
sect "6. AGENTS.md / CLAUDE.md managed block"
CLAUDE_CMD_FILE="$ROOT/CLAUDE.md"
[ -f "$CLAUDE_CMD_FILE" ] || CLAUDE_CMD_FILE="$ROOT/.claude/CLAUDE.md"
for CMD_FILE in "$CLAUDE_CMD_FILE" "$ROOT/AGENTS.md"; do
  CMD_REL=${CMD_FILE#"$ROOT"/}
  if [ "$(mode)" = "stealth" ] && [ -n "$(git ls-files -- "$CMD_REL" 2>/dev/null)" ]; then
    bad "$CMD_REL is tracked while aleysian.mode=stealth. Updating its managed block would modify the client's repository."
    info "Restore any generated edit. Keep stealth and leave the tracked file untouched,"
    info "or deliberately switch to native before updating and committing the contract."
    continue
  fi
  case "$(block_status "$CMD_FILE")" in
    OK)      ok "present, hash matches ($(basename "$CMD_FILE"))" ;;
    MISSING)
      if [ "$FIX" = "1" ]; then "$SKILL_DIR/scripts/install.sh" --block --platform both >/dev/null && fixed "inserted both managed blocks"
      else bad "$(basename "$CMD_FILE") absent — that host's contract is not in context"; fi ;;
    MODIFIED)
      # Deliberately NOT auto-fixed even with --fix. The hash proves the content
      # changed; it cannot tell you whether an agent stripped a rule or a human added
      # a genuinely useful line. Overwriting silently would destroy the second case
      # to fix the first.
      bad "$(basename "$CMD_FILE") EDITED since generation — content no longer matches its recorded hash."
      info "Rules may have been weakened or removed. Do not trust the block. The diff"
      info "(left = what is in the file, right = what the config says it should be):"
      printf '\n'
      TMPL="$HOME_DIR/templates/claude-md-block.md"
      [ -f "$TMPL" ] || TMPL="$SKILL_DIR/references/templates/claude-md-block.md"
      diff <(block_extract "$CMD_FILE") <(block_render_body "$TMPL" 2>/dev/null) | head -40
      printf '\n'
      info "This is not auto-fixed even with --fix: the hash proves the content changed,"
      info "but not whether an agent stripped a rule or a human added a useful line."
      info "  discard the edit, restore ours:  $SKILL_DIR/scripts/install.sh --block --platform both --force"
      info "  keep the edit: there is no way to re-hash it in place, and that is deliberate —"
      info "  a fence you can silently re-bless is not a fence. Fold the change into the"
      info "  config or the template instead, then re-render."
      ;;
  esac
done

# ── the same block, ON TRUNK ─────────────────────────────────
#
# The check above answers "does THIS working tree have the contract". That is not
# the question that matters most, because most agent work happens in worktrees, and
# a worktree materialises TRACKED content from its base branch. A block that exists
# only in the working tree — uncommitted, or committed on some other line — is
# present in exactly one place and absent from every worktree, which then run against
# whatever stale prose their branch does carry. Nothing about that looks wrong: the
# working-tree check says "present, hash matches" while no worktree has the contract
# at all. That is the false-clean this whole script exists to prevent, so it is a
# FAIL, not a note.
TRUNK_BR=$(trunk_ref)
if [ -z "$TRUNK_BR" ]; then TRUNK_BR=$(trunk); fi
if ! git rev-parse --verify --quiet "$TRUNK_BR" >/dev/null 2>&1; then
  # Already reported as a FAIL in section 1 (and the same condition covers a repo
  # with no commits yet), so state what could not be checked and move on.
  info "trunk '$TRUNK_BR' does not resolve here — the block on trunk was NOT verified (see 1)."
elif [ "$(mode)" = "stealth" ]; then
  # In stealth mode CLAUDE.md is ours, not the client's: it is in info/exclude and
  # never committed, so trunk carries no block BY DESIGN. Worktrees get it by symlink
  # from the main clone instead, which section 8 checks. Failing here would be a
  # permanent false alarm, which costs the same trust as a false clean.
  info "stealth mode: host contracts are untracked by design, so trunk carries no managed block."
  info "Worktrees get it by symlink from the main clone — section 8 checks that instead."
else
  TRUNK_PATH=""
  for P in AGENTS.md CLAUDE.md .claude/CLAUDE.md; do
    if git cat-file -e "$TRUNK_BR:$P" >/dev/null 2>&1; then TRUNK_PATH="$P"; break; fi
  done
  if [ -z "$TRUNK_PATH" ]; then
    bad "no CLAUDE.md is committed on trunk ($TRUNK_BR) — so NO worktree has the contract."
    info "A worktree materialises tracked content from its base branch. With nothing on"
    info "trunk, every worktree agent works from whatever prose its branch happens to"
    info "carry — typically an older contract that contradicts the hooks now armed."
    info "Fix: commit CLAUDE.md on $TRUNK_BR. A block present only in this working tree,"
    info "or only on a feature branch, protects nobody."
    case "$CMD_FILE" in
      */.claude/CLAUDE.md)
        info "Note: the block here lives in .claude/CLAUDE.md, and .claude/ is in"
        info "info/exclude — it can never reach trunk. Move it to the repo-root CLAUDE.md." ;;
    esac
  else
    TRUNK_TMP=$(mktemp)
    git show "$TRUNK_BR:$TRUNK_PATH" > "$TRUNK_TMP" 2>/dev/null
    TRUNK_STATUS=$(block_status "$TRUNK_TMP")
    case "$TRUNK_STATUS" in
      OK)
        ok "present on trunk ($TRUNK_BR:$TRUNK_PATH), hash matches"
        # If the LOCAL branch of the same name disagrees with the ref checked above,
        # say so — but as an info, not a failure. Which one a worktree gets depends on
        # what the project's tooling cuts from, and this script cannot know that. The
        # previous version guessed local, and false-alarmed on a clone that was merely
        # behind origin.
        case "$TRUNK_BR" in
          "$(trunk)") ;;    # already the local branch; nothing to compare
          *)
            if git rev-parse --verify --quiet "$(trunk)" >/dev/null 2>&1 \
               && [ "$(git rev-parse "$TRUNK_BR" 2>/dev/null)" != "$(git rev-parse "$(trunk)" 2>/dev/null)" ]; then
              info "…the LOCAL '$(trunk)' is at a different commit than $TRUNK_BR. If anything"
              info "cuts worktrees from the local branch rather than the remote, it may see a"
              info "different contract. git fetch && git merge --ff-only to remove the doubt."
            fi ;;
        esac
        # Valid but stale is the same failure one step later: worktrees keep serving
        # the committed version, not the one this clone just re-rendered.
        if [ -f "$CMD_FILE" ] \
           && [ "$(block_recorded_hash "$TRUNK_TMP")" != "$(block_recorded_hash "$CMD_FILE")" ]; then
          info "…but it differs from this working tree's block. Until that change is committed"
          info "to $TRUNK_BR, every worktree still reads the older contract."
        fi ;;
      MISSING)
        bad "$TRUNK_BR:$TRUNK_PATH exists but contains NO managed block — so no worktree"
        info "has the contract. A worktree materialises tracked content from its base"
        info "branch; agents there follow whatever prose that branch carries, which is"
        info "typically an older contract that contradicts the hooks now armed."
        info "Fix: install the block and commit it on $TRUNK_BR." ;;
      MODIFIED)
        bad "$TRUNK_BR:$TRUNK_PATH carries a block that does NOT match its recorded hash —"
        info "the committed contract was hand-edited, and every worktree inherits that"
        info "edited copy. Rules may have been weakened or removed. Review it on trunk,"
        info "then re-hash deliberately (scripts/install.sh --block) and commit." ;;
    esac
    rm -f "$TRUNK_TMP"
  fi
fi

# ═══ 7. state dir and excludes ════════════════════════════════
sect "7. State + excludes"
SD="$COMMON/aleysian"
if [ -d "$SD" ] && [ -w "$SD" ]; then
  ok "$SD writable ($(ls "$SD" 2>/dev/null | wc -l | tr -d ' ') file(s))"
  for f in deploy-log validate-log hatch-log; do
    [ -f "$SD/$f" ] && info "  $f: $(wc -l < "$SD/$f" | tr -d ' ') entries"
  done
elif [ "$FIX" = "1" ]; then mkdir -p "$SD" && fixed "created $SD"
else bad "$SD missing or not writable — validate/deploy proof cannot be recorded, so the merge gate will block everything"; fi

EXC="$COMMON/info/exclude"
# This list must match what install.sh writes, entry for entry. Where the two
# disagree, audit reports a repo install just configured correctly — and --fix then
# writes back whatever install deliberately left out.
#
# node_modules carries NO trailing slash: a pattern ending in / matches directories
# only, and ensure-worktree-config.sh SYMLINKS node_modules into each worktree. A
# symlink is not a directory, so the slashed form leaves it untracked-and-visible in
# every worktree, one `git add -A` away from committing a machine-specific path.
NEED="tmp-retrieve/ node_modules"

# .claude/ is excluded only where it is OURS. A repo that already TRACKS .claude/
# keeps its own hooks and settings there, and excluding a tracked path is actively
# harmful rather than merely redundant — see the inverse check below. So in that
# case its ABSENCE from exclude is correct and must not be reported as a gap.
CLAUDE_TRACKED=0
[ -n "$(git ls-files -- .claude 2>/dev/null | head -1)" ] && CLAUDE_TRACKED=1
[ "$CLAUDE_TRACKED" = "0" ] && NEED=".claude/ $NEED"

if [ "$(mode)" = "stealth" ]; then
  [ -f "$ROOT/CLAUDE.md" ] && NEED="CLAUDE.md $NEED"
  [ -f "$ROOT/AGENTS.md" ] && NEED="AGENTS.md $NEED"
fi
MISS_EXC=""
for e in $NEED; do grep -qxF "$e" "$EXC" 2>/dev/null || MISS_EXC="$MISS_EXC $e"; done
if [ -z "$MISS_EXC" ]; then ok "info/exclude covers:$NEED"
elif [ "$FIX" = "1" ]; then
  mkdir -p "$(dirname "$EXC")"; for e in $MISS_EXC; do echo "$e" >> "$EXC"; done
  fixed "added to info/exclude:$MISS_EXC"
else bad "info/exclude is missing:$MISS_EXC"; fi

# The inverse, and the more damaging direction: excluding a path git already tracks.
# `git add .claude/settings.json` then refuses a file git is tracking, new files under
# it are invisible, and lint-staged cannot re-stage what prettier --write rewrote —
# which leaves a permanently dirty tree and a commit that disagrees with the formatter.
# An install performed before .claude/ was tracked leaves exactly this line behind.
if [ "$CLAUDE_TRACKED" = "1" ] && grep -qxF '.claude/' "$EXC" 2>/dev/null; then
  if [ "$FIX" = "1" ]; then
    # Only ever that exact line — everything else in exclude belongs to someone else.
    { grep -vxF '.claude/' "$EXC" || true; } > "$EXC.sfds.$$" && mv "$EXC.sfds.$$" "$EXC" \
      && fixed "removed .claude/ from info/exclude (this repo TRACKS .claude/)"
  else
    bad ".claude/ is in info/exclude, but this repo TRACKS .claude/ — git add refuses"
    info "files git already tracks there, new files under it are invisible to git, and a"
    info "re-staging formatter (lint-staged + prettier --write) can never re-stage what it"
    info "rewrote. Remove that one line; --fix does it."
  fi
fi

# ═══ 8. worktrees ═════════════════════════════════════════════
sect "8. Worktrees"
WTS=0
while IFS= read -r WT; do
  [ -z "$WT" ] || [ "$WT" = "$ROOT" ] && continue
  WTS=$((WTS+1))
  for F in CLAUDE.md AGENTS.md; do
    [ -f "$ROOT/$F" ] || continue
    if [ "$(mode)" = "stealth" ]; then
      if [ -e "$WT/$F" ]; then ok "$(basename "$WT"): $F present"
      elif [ "$FIX" = "1" ]; then
        ln -s "$ROOT/$F" "$WT/$F" && fixed "$(basename "$WT"): linked $F"
      else bad "$(basename "$WT") has NO $F — that host has no contract in context"; fi
    elif [ -e "$WT/$F" ]; then
      ok "$(basename "$WT"): $F present"
    else
      bad "$(basename "$WT") has NO $F. That host has no contract in context"
      info "Native mode tracks host contracts. Update this branch from $(trunk), or recreate"
      info "the worktree after the bootstrap commit; --fix cannot invent tracked branch content."
    fi
  done
  [ -f "$WT/.forceignore" ] || [ -L "$WT/.forceignore" ] || info "$(basename "$WT"): no .forceignore (changes what a deploy includes)"
done < <(git worktree list --porcelain 2>/dev/null | awk '/^worktree /{print substr($0,10)}')
[ "$WTS" = "0" ] && ok "none open"

# ═══ 8b. DevOps Center topology ══════════════════════════════
#
# This is the one remote fact that can make every local branch gate consistently
# wrong. The pipeline is authoritative for the WI review target. A successful
# query that disagrees is fatal; an unavailable query is reported but does not
# convert a network outage into a claim that local enforcement is broken.
if is_devops_center; then
  sect "8b. DevOps Center landing topology"
  if [ "$PROBE" = "0" ]; then
    info "--no-probe: pipeline topology was not queried. Local config still ran."
  elif [ -z "$(devops_pipeline_id)" ] || [ -z "$(devops_org_alias)" ]; then
    info "pipeline id or control-org alias is missing, so topology cannot be verified."
  else
    if [ -n "$(devops_project_id)" ]; then
      LANDING=$(with_timeout 30 "$SKILL_DIR/scripts/resolve-devops-landing.sh" \
        --pipeline-id "$(devops_pipeline_id)" --target-org "$(devops_org_alias)" \
        --project-id "$(devops_project_id)" 2>/dev/null || echo "")
    else
      LANDING=$(with_timeout 30 "$SKILL_DIR/scripts/resolve-devops-landing.sh" \
        --pipeline-id "$(devops_pipeline_id)" --target-org "$(devops_org_alias)" \
        2>/dev/null || echo "")
    fi
    if [ -z "$LANDING" ]; then
      info "could not query one landing branch from pipeline $(devops_pipeline_id)."
      info "Verify control-org authentication, pipeline stages, branches, and project attachment."
    elif [ "$LANDING" != "$(trunk)" ]; then
      bad "pipeline $(devops_pipeline_id) says the landing branch is '$LANDING', but aleysian.trunk='$(trunk)'."
      info "Rerun init with --devops-pipeline-id $(devops_pipeline_id). Do not hand-edit only"
      info "the branch key because protected branches and the managed contract must change together."
    else
      ok "landing branch '$LANDING' matches the first linked pipeline stage"
    fi
  fi
fi

# ═══ 8c. Shared development-org receipt ══════════════════════
if is_devops_shared; then
  sect "8c. Shared development-org receipt"
  if [ "$PROBE" = "0" ]; then
    info "--no-probe: centralized deployment receipt was not queried."
  else
    STATUS_BIN="$HOME_DIR/bin/aleysian-devops-shared-status"
    [ -x "$STATUS_BIN" ] || STATUS_BIN="$SKILL_DIR/references/hooks/bin/aleysian-devops-shared-status"
    STATUS_OUT=$(with_timeout 35 "$STATUS_BIN" --json); STATUS_RC=$?
    if [ "$STATUS_RC" -eq 0 ]; then
      STATUS_BRANCH=$(printf '%s' "$STATUS_OUT" | jq -r '.branch // "?"')
      STATUS_SHA=$(printf '%s' "$STATUS_OUT" | jq -r '.deployedSha // ""' | cut -c1-12)
      ok "origin/$STATUS_BRANCH matches successful deployment $STATUS_SHA"
    elif [ "$STATUS_RC" -eq 3 ]; then
      STATUS_BRANCH=$(printf '%s' "$STATUS_OUT" | jq -r '.branch // "?"')
      STATUS_REMOTE=$(printf '%s' "$STATUS_OUT" | jq -r '.remoteSha // ""' | cut -c1-12)
      STATUS_DEPLOYED=$(printf '%s' "$STATUS_OUT" | jq -r '.deployedSha // ""' | cut -c1-12)
      bad "origin/$STATUS_BRANCH=$STATUS_REMOTE but latest successful deployment=$STATUS_DEPLOYED"
      info "The shared landing queue stays frozen until the coordinator restores branch=deployed SHA."
    else
      STATUS_ERROR=$(printf '%s' "$STATUS_OUT" | jq -r '.error // empty' 2>/dev/null || echo "")
      bad "centralized shared-org state is unverified: ${STATUS_ERROR:-status command failed}"
      info "Check gh authentication, origin/$(devops_integration_branch), and the GitHub environment receipt."
    fi
  fi
fi

# ═══ 8d. Persistent DevOps Center branches ═══════════════════
if is_devops_shared; then
  sect "8d. Persistent DevOps Center branches"
  if [ "$PROBE" = "0" ]; then
    info "--no-probe: GitHub deletion protection was not queried."
  else
    BRANCH_STATUS_BIN="$HOME_DIR/bin/aleysian-devops-branch-status"
    [ -x "$BRANCH_STATUS_BIN" ] || BRANCH_STATUS_BIN="$SKILL_DIR/references/hooks/bin/aleysian-devops-branch-status"
    CHECKED_BRANCHES=""
    for PIPELINE_BRANCH in "$(devops_integration_branch)" "$(trunk)" main; do
      [ -n "$PIPELINE_BRANCH" ] || continue
      case " $CHECKED_BRANCHES " in *" $PIPELINE_BRANCH "*) continue ;; esac
      CHECKED_BRANCHES="$CHECKED_BRANCHES $PIPELINE_BRANCH"
      BRANCH_STATUS=$(with_timeout 30 "$BRANCH_STATUS_BIN" --branch "$PIPELINE_BRANCH" --json); BRANCH_RC=$?
      if [ "$BRANCH_RC" -eq 0 ]; then
        BRANCH_MECHANISM=$(printf '%s' "$BRANCH_STATUS" | jq -r '.mechanism // "?"')
        ok "GitHub branch '$PIPELINE_BRANCH' exists and blocks deletion ($BRANCH_MECHANISM)"
      else
        BRANCH_ERROR=$(printf '%s' "$BRANCH_STATUS" | jq -r '.error // empty' 2>/dev/null || echo "")
        bad "GitHub branch '$PIPELINE_BRANCH' is not proven persistent: ${BRANCH_ERROR:-status command failed}"
      fi
    done
  fi
fi

# ═══ 9-11. Judgment items — reported, never fixed, never fatal ═
sect "9-11. Judgment items (reported only)"

if [ "$PROBE" = "0" ]; then
  info "--no-probe: the org, tracker-auth and drift probes were SKIPPED."
  info "Those are the only checks that touch the network. Everything above is local"
  info "and did run — but an unreachable org or an expired tracker session would not"
  info "have been noticed. Re-run without --no-probe before trusting a clean result."
elif command -v sf >/dev/null 2>&1 && [ -n "$(org_alias)" ]; then
  if with_timeout 20 sf org display --target-org "$(org_alias)" >/dev/null; then
    info "org '$(org_alias)' resolves"
  else
    info "org '$(org_alias)' did not resolve within 20s — sf org login web, or fix aleysian.orgalias"
  fi
fi

if [ "$PROBE" = "0" ]; then
  :
elif [ "$(ticket_system)" = "jira" ]; then
  # Jira has no shell-callable CLI in this stack anymore: all Jira work is done by the
  # agent through the Atlassian Rovo MCP, which a bash audit cannot reach or probe.
  info "Jira runs agent-side through the Atlassian Rovo MCP (company-wide, interactive"
  info "auth) — there is nothing here for a bash audit to shell-check. Confirm the Rovo"
  info "MCP is connected in your Claude client."
elif ! ticket_cli_present; then
  case "$(ticket_system)" in
    github) info "gh is not installed — deploy annotation and issue reads degrade to no-ops" ;;
    *)      info "ticket.system=$(ticket_system) — no CLI integration, refs and audit trail only" ;;
  esac
elif with_timeout 20 sh -c "$(auth_probe_cmd)" >/dev/null 2>&1; then
  info "$(ticket_system) CLI available and authenticated"
else
  # Installed but not authenticated is the more dangerous state of the two: every
  # call fails while the install looks fine.
  info "$(ticket_system) CLI is installed but NOT authenticated — every tracker read and"
  info "write will fail silently. Reads degrade to UNKNOWN (safe); writes do nothing."
  info "  gh auth login"
fi

# Read into a variable first. Logic inside $() is the shape that broke this script
# once already on bash 3.2 — see the auth_probe_cmd note above.
# Drift is REACTIVE now — no per-session org probe, so there is nothing to network-test
# here. The value is a declaration (is this a source-tracked org?), reported as-is.
case "$(drift_policy)" in
  tracking) info "drift=tracking — source-tracked org; capture Setup changes reactively (references/drift-reconcile.md)." ;;
  off) info "drift=off — Setup-change capture is on you when you self-report one (references/drift-reconcile.md)." ;;
  *) info "drift='$(drift_policy)' is not tracking|off (audittrail is retired). Set: git config aleysian.drift tracking" ;;
esac

CL=$(checklist "." 2>/dev/null || echo "")
if [ -n "$CL" ] && [ -f "$CL" ] && [ -s "$CL" ]; then
  printf '\n        \033[1mOpen client-conversation items:\033[0m\n'
  sed 's/^/          /' "$CL"
fi

# ═══ Verdict ══════════════════════════════════════════════════
printf '\n'

# An unevaluated check must never be able to report clean — see the stderr note above.
if [ -s "$STDERR_LOG" ]; then
  printf '\033[31mAudit could NOT complete cleanly.\033[0m Something errored while checking,\n'
  printf 'so at least one section did not actually evaluate. Its result — pass or fail — means\n'
  printf 'nothing. Errors:\n\n'
  sed 's/^/  /' "$STDERR_LOG" | head -20
  printf '\n'
  cleanup_stderr
  exit 1
fi

if [ "$FAIL" = "0" ]; then
  cleanup_stderr
  printf '\033[32mAudit clean.\033[0m The stack is armed in this clone.\n\n'
  exit 0
else
  cleanup_stderr
  printf '\033[31mAudit found problems.\033[0m Until they are resolved the workflow is NOT fully\n'
  printf 'enforced — do not assume otherwise. Mechanical items: re-run with --fix\n\n'
  exit 1
fi
