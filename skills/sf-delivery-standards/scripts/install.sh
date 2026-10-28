#!/bin/bash
# install.sh — the "do" half of `/sf-delivery-standards init`.
#
# Two independent things, in this order:
#
#   MACHINE (once, then refreshed on upgrade)
#     ~/.estate/{githooks,claude-hooks,bin,templates,VERSION}
#     hook entries merged into the selected Claude/Codex user config (and stale deny rules
#     retracted — retrieve-blocking now lives in the gated guard, not machine-wide)
#
#   CLONE (per repo)
#     estate.* git config, core.hooksPath, .git/info/exclude, state dir,
#     the matching CLAUDE.md and/or AGENTS.md managed block
#
# The machine half is idempotent and safe to re-run. The clone half writes only
# keys it was given: re-running init after answering one question differently
# changes that key and leaves the rest alone.
#
# USAGE
#   install.sh --machine-only
#   install.sh --repo   --mode native|stealth --delivery direct|engine|devops-center \
#                       --trunk BR --host H --ticket-system S \
#                       [--ticket-project KEY] [--ticket-remote ours|client] \
#                       [--ticket-pattern RE] [--format client|check|off] \
#                       [--pmd block|advise] [--drift tracking|off] \
#                       [--org-alias A] [--squash require|prefer|merge] [--review pr|local]
#                       [--protected "br1 br2"] [--devops-org-alias A]
#                       [--devops-project-id ID] [--devops-pipeline-id ID]
#                       [--devops-work-model isolated|shared]
#                       [--devops-integration-branch BR] [--devops-environment NAME]
#   install.sh --block [--force]   # (re)render the CLAUDE.md block from current config
#                                  # --force replaces a hand-edited block; --block alone
#                                  # refuses to and shows the diff instead
#
# Nothing here prompts. The Q&A is the skill's job — see references/init-guide.md.
# A script that asks questions cannot be re-run from an agent, and this one must be.

set -eu

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$SKILL_DIR/references/hooks"
HOME_DIR="$HOME/.estate"
VERSION="1.10"

# The skill's OWN library, not the armed one: this script is what defines what
# "installed" will mean, so it must reason with the version it is about to install.
# It is sourced for the git-topology helpers (main_repo_root, in_worktree) — a second
# implementation of worktree detection in here would be one more place for the
# physical-vs-logical path bug to come back.
HOOK_NO_GATE=1
. "$SRC/claude-hooks/_lib.sh"

say()  { printf '  %s\n' "$*"; }
head_() { printf '\n%s\n' "$*"; }
die()  { printf '\ninstall.sh: %s\n' "$*" >&2; exit 1; }

# ═══════════════════════════════════════════════════════════════
# MACHINE
# ═══════════════════════════════════════════════════════════════
install_machine() {
  head_ "Machine install -> $HOME_DIR"
  mkdir -p "$HOME_DIR"/{githooks,claude-hooks,bin,templates}

  # Prune before copying: a plain cp adds and overwrites but never REMOVES, so a
  # hook the skill has since deleted (e.g. a retired guard) would linger in the
  # armed dir and keep firing after a re-arm. Clearing our hook files first makes
  # the armed dir mirror the source exactly. (Only *.sh lives here.)
  rm -f "$HOME_DIR"/claude-hooks/*.sh
  cp "$SRC"/claude-hooks/*.sh   "$HOME_DIR/claude-hooks/"
  cp "$SRC"/githooks/pre-commit "$SRC"/githooks/commit-msg "$HOME_DIR/githooks/"
  cp "$SRC"/bin/*               "$HOME_DIR/bin/" 2>/dev/null || true
  cp "$SKILL_DIR"/references/templates/* "$HOME_DIR/templates/" 2>/dev/null || true

  chmod +x "$HOME_DIR"/claude-hooks/*.sh "$HOME_DIR"/githooks/* "$HOME_DIR"/bin/* 2>/dev/null || true
  # The two sourced libraries are not hooks. Leaving them executable invites
  # someone to run one and wonder why nothing happened.
  chmod -x "$HOME_DIR"/claude-hooks/_lib.sh "$HOME_DIR"/claude-hooks/_config.sh \
           "$HOME_DIR"/claude-hooks/_ticket.sh "$HOME_DIR"/claude-hooks/_block.sh 2>/dev/null || true

  echo "$VERSION" > "$HOME_DIR/VERSION"
  say "installed $(ls "$HOME_DIR/claude-hooks" | wc -l | tr -d ' ') hook files, v$VERSION"

  if [ "$PLATFORM" = "claude" ] || [ "$PLATFORM" = "both" ]; then
    install_agents
  fi
  case "$PLATFORM" in
    claude) merge_claude_settings ;;
    codex) merge_codex_settings ;;
    both) merge_claude_settings; merge_codex_settings ;;
  esac
  path_hint
}

# ── Subagents shipped with the skill ─────────────────────────
#
# These are Claude Code agents (invoked via the Task tool), and registration is
# nothing more than presence in ~/.claude/agents/. Unlike the hooks, they are NOT
# enforcement — an agent is a capability the model may call, not a wall — so a
# missing one degrades a workflow, it does not fail one open. They live with the
# machine install so `init --update` refreshes them and `audit` can tell you the
# one running is the one this skill version ships.
#
# ~/.claude/agents/ is a shared, user-level dir that other skills and the user's
# own agents live in, so we copy only our own files by name and never clear it.
install_agents() {
  local dst="$HOME/.claude/agents"
  local src="$SKILL_DIR/references/agents"
  [ -d "$src" ] || return 0
  mkdir -p "$dst"
  local n=0
  for f in "$src"/*.md; do
    [ -e "$f" ] || continue
    cp "$f" "$dst/" && n=$((n+1))
  done
  [ "$n" -gt 0 ] && say "installed $n subagent(s) -> $dst"
}

# ── The delicate step ────────────────────────────────────────
#
# The user's ~/.claude/settings.json probably has hooks of their own, from other
# projects and other skills. Overwriting it would be the single most destructive
# thing this installer could do, so: back up first, then for each event REPLACE
# only OUR footprint (any hook whose command lives under ~/.estate/claude-hooks/)
# with the current fragment, leaving every other hook untouched. Replace, not
# append: appending cannot express a REMOVAL, so a since-deleted guard — or a
# matcher group whose command set changed — would survive a re-arm and keep firing.
merge_claude_settings() {
  local settings="$HOME/.claude/settings.json"
  local fragment="$SKILL_DIR/references/templates/claude-settings-fragment.json"
  command -v jq >/dev/null 2>&1 || die "jq is required to merge $settings safely.
  Install it (brew install jq) and re-run. Hand-editing that file is not a good
  substitute — a malformed settings.json disables every hook you have."

  mkdir -p "$(dirname "$settings")"
  [ -f "$settings" ] || echo '{}' > "$settings"

  local backup="${settings}.bak.$(date -u +%Y%m%dT%H%M%SZ)"
  cp "$settings" "$backup"

  local frag tmp
  # Drop every top-level _comment* key, not just _comment — the fragment documents
  # more than one decision now, and a named-key-only delete leaves the next one behind.
  frag=$(sed "s|__HOME__|$HOME|g" "$fragment" \
         | jq 'with_entries(select(.key | startswith("_comment") | not))')
  tmp="${settings}.tmp$$"

  # The deny rules this installer retracts from an existing settings.json.
  #
  # None of these are in the fragment anymore — see the _comment_deny note there.
  # A deny rule in the USER-level file is enforced by the harness in every repo on
  # the machine, gate or no gate, so it interferes with unrelated Salesforce
  # projects that never went through init (requirement 1). Retracting them on
  # re-arm is how already-armed machines get clean.
  #
  #   Bash(sf project retrieve:*)      — a prefix match, so it also denied
  #     `sf project retrieve preview`, the exact no-write probe drift=tracking needs.
  #   Bash(sf project retrieve start:*), Bash(sfdx project retrieve:*),
  #   Bash(sfdx force:source:retrieve:*) — these three used to deny retrieve INTO
  #     the tree machine-wide. That job now belongs to guard-sf-flags.sh, which does
  #     it ONLY in a managed repo — the correct scope. Nothing is lost in a managed
  #     repo; the interference in every other repo is gone.
  #
  # Retracting a deny rule is otherwise forbidden here — see the merge rules below.
  # These are exempt because earlier versions of this installer are what wrote them.
  local retired='["Bash(sf project retrieve:*)","Bash(sf project retrieve start:*)","Bash(sfdx project retrieve:*)","Bash(sfdx force:source:retrieve:*)"]'

  # Merge rules, and why each is what it is:
  #   hooks       per event, FIRST strip our own footprint out of the existing
  #               array — every hook command under ~/.estate/claude-hooks/, and
  #               any group thereby emptied — then concatenate the fragment and
  #               de-dup by the full matcher+command shape. Stripping first is what
  #               makes a re-arm reflect a REMOVAL: without it, a since-deleted hook
  #               or a changed matcher group survives as a stale second group (its
  #               command set no longer matches the fragment's, so the de-dup keeps
  #               both). Only OUR entries are touched — the user's own hooks and
  #               other skills' entries (different paths) are preserved verbatim.
  #   deny        union, minus $retired. Never remove any OTHER existing deny rule:
  #               it is someone's deliberate guardrail and we cannot know whose.
  jq -n --argjson base "$(cat "$settings")" --argjson frag "$frag" \
        --argjson retired "$retired" --arg ours "/.estate/claude-hooks/" '
    def is_ours($h): (($h.command // "") | contains($ours));
    def strip_ours($arr): ($arr // [])
      | map(.hooks = ((.hooks // []) | map(select(is_ours(.) | not))))
      | map(select((.hooks | length) > 0));
    def merge_event($a; $b): (strip_ours($a)) + ($b // [])
      | group_by([(.matcher // ""), ([.hooks[]?.command] | sort | join("|"))])
      | map(.[0]);
    $base
    | .permissions.deny = ((((.permissions.deny // []) + ($frag.permissions.deny // []))
                            - $retired) | unique)
    | .hooks = ( reduce ($frag.hooks | keys[]) as $e
                 ((.hooks // {}); .[$e] = merge_event(.[$e]; $frag.hooks[$e])) )
  ' > "$tmp"

  if jq -e . "$tmp" >/dev/null 2>&1; then
    mv "$tmp" "$settings"
    say "merged hook entries into $settings, retracted stale deny rules (backup: $(basename "$backup"))"
  else
    rm -f "$tmp"
    die "the merged settings.json did not parse — nothing was changed. Backup at $backup."
  fi
}

# Codex uses the same lifecycle names and exit-2 blocking contract, but discovers
# hooks in ~/.codex/hooks.json and has no TaskCompleted event. Unified exec emits
# PostToolUse when a long-running command actually finishes, so the recorders stay
# on PostToolUse only in this fragment.
merge_codex_settings() {
  local settings="$HOME/.codex/hooks.json"
  local fragment="$SKILL_DIR/references/templates/codex-hooks-fragment.json"
  command -v jq >/dev/null 2>&1 || die "jq is required to merge $settings safely."

  mkdir -p "$(dirname "$settings")"
  [ -f "$settings" ] || echo '{}' > "$settings"
  jq -e . "$settings" >/dev/null 2>&1 || die "$settings is invalid JSON; left unchanged."

  local backup="${settings}.bak.$(date -u +%Y%m%dT%H%M%SZ)"
  local frag tmp
  cp "$settings" "$backup"
  frag=$(sed "s|__HOME__|$HOME|g" "$fragment")
  tmp="${settings}.tmp$$"

  jq -n --argjson base "$(cat "$settings")" --argjson frag "$frag" \
        --arg ours "/.estate/claude-hooks/" '
    def is_ours($h): (($h.command // "") | contains($ours));
    def strip_ours($arr): ($arr // [])
      | map(.hooks = ((.hooks // []) | map(select(is_ours(.) | not))))
      | map(select((.hooks | length) > 0));
    def merge_event($a; $b): (strip_ours($a)) + ($b // [])
      | group_by([(.matcher // ""), ([.hooks[]?.command] | sort | join("|"))])
      | map(.[0]);
    $base
    | .description = ($base.description // $frag.description)
    | .hooks = ( reduce ($frag.hooks | keys[]) as $e
                 ((.hooks // {}); .[$e] = merge_event(.[$e]; $frag.hooks[$e])) )
  ' > "$tmp"

  if jq -e . "$tmp" >/dev/null 2>&1; then
    mv "$tmp" "$settings"
    say "merged hook entries into $settings (backup: $(basename "$backup")); review them with /hooks"
  else
    rm -f "$tmp"
    die "the merged Codex hooks.json did not parse; nothing was changed. Backup at $backup."
  fi
}

path_hint() {
  case ":$PATH:" in
    *":$HOME_DIR/bin:"*) ;;
    *) say "NOTE: add $HOME_DIR/bin to PATH so 'estate-merge' and 'estate-ticket-status' are callable:"
       say "        echo 'export PATH=\"\$HOME/.estate/bin:\$PATH\"' >> ~/.zshrc" ;;
  esac
}

# ═══════════════════════════════════════════════════════════════
# CLONE
# ═══════════════════════════════════════════════════════════════
MODE=""; DELIVERY=""; TRUNK=""; HOST=""; TSYS=""; TPROJ=""; TREMOTE=""; TPAT=""
FORMAT=""; PMD=""; DRIFT=""; ORG=""; SQUASH=""; REVIEW=""; PROTECTED=""
DEVOPS_ORG=""; DEVOPS_PROJECT=""; DEVOPS_PIPELINE=""; DEVOPS_WORK_MODEL=""
DEVOPS_INTEGRATION=""; DEVOPS_ENVIRONMENT=""

# A stealth install owns its host contracts locally. If the target path is already
# tracked, writing the managed block would modify the client's repository even though
# .git/info/exclude makes the file look ignored to casual inspection. Refuse before
# either the machine or clone half mutates anything. The user must explicitly choose
# native mode before a tracked contract can be updated.
contract_targets() {
  local root="$1" target
  case "$PLATFORM" in
    claude)
      target="$root/CLAUDE.md"
      [ -f "$target" ] || { [ -f "$root/.claude/CLAUDE.md" ] && target="$root/.claude/CLAUDE.md"; }
      printf '%s\n' "$target"
      ;;
    codex)
      printf '%s\n' "$root/AGENTS.md"
      ;;
    both)
      target="$root/CLAUDE.md"
      [ -f "$target" ] || { [ -f "$root/.claude/CLAUDE.md" ] && target="$root/.claude/CLAUDE.md"; }
      printf '%s\n%s\n' "$target" "$root/AGENTS.md"
      ;;
  esac
}

preflight_contract_ownership() {
  local root effective_mode target rel tracked
  git rev-parse --git-dir >/dev/null 2>&1 || die "not a git repository."
  root=$(git rev-parse --show-toplevel)
  effective_mode="$MODE"
  [ -n "$effective_mode" ] || effective_mode=$(git config --get estate.mode 2>/dev/null || echo "")
  [ "$effective_mode" = "stealth" ] || return 0

  tracked=""
  while IFS= read -r target; do
    rel=${target#"$root"/}
    if [ -n "$(git -C "$root" ls-files -- "$rel" 2>/dev/null)" ]; then
      tracked="${tracked}${tracked:+, }$rel"
    fi
  done < <(contract_targets "$root")

  [ -z "$tracked" ] || die "stealth mode cannot update tracked host contract(s): $tracked.
  Nothing was changed. Restore any existing generated edits. Then either keep stealth
  and leave the client's tracked files untouched, or deliberately switch to native
  mode before updating and committing them. To refresh machine hooks only, run:
  $0 --machine-only --platform $PLATFORM"
}

install_repo() {
  git rev-parse --git-dir >/dev/null 2>&1 || die "not a git repository."
  [ -f sfdx-project.json ] || say "WARNING: no sfdx-project.json here. This stack is for Salesforce
     projects; in anything else the hooks will be inert but the config is still written."

  local root; root=$(git rev-parse --show-toplevel); cd "$root"

  if [ "${DELIVERY:-direct}" = "devops-center" ]; then
    local effective_work_model effective_host effective_integration effective_environment
    effective_work_model="${DEVOPS_WORK_MODEL:-$(git config --get estate.devops.workmodel 2>/dev/null || echo isolated)}"
    effective_host="${HOST:-$(git config --get estate.host 2>/dev/null || echo github)}"
    effective_integration="${DEVOPS_INTEGRATION:-$(git config --get estate.devops.integrationbranch 2>/dev/null || echo "")}"
    effective_environment="${DEVOPS_ENVIRONMENT:-$(git config --get estate.devops.environment 2>/dev/null || echo "")}"
    case "$effective_work_model" in isolated|shared) ;; *) die "--devops-work-model must be isolated or shared" ;; esac
    if [ "$effective_work_model" = "shared" ]; then
      [ "$effective_host" = "github" ] || die "shared DevOps Center development currently requires --host github for centralized deployment receipts"
      [ -n "$effective_integration" ] || die "shared DevOps Center development requires --devops-integration-branch"
      [ -n "$effective_environment" ] || die "shared DevOps Center development requires --devops-environment"
    fi
    if [ -n "$DEVOPS_PIPELINE" ]; then
      [ -n "$DEVOPS_ORG" ] || die "--devops-org-alias is required with --devops-pipeline-id"
      local resolved_landing
      if [ -n "$DEVOPS_PROJECT" ]; then
        resolved_landing=$("$SKILL_DIR/scripts/resolve-devops-landing.sh" \
          --pipeline-id "$DEVOPS_PIPELINE" --target-org "$DEVOPS_ORG" \
          --project-id "$DEVOPS_PROJECT") \
          || die "could not derive the DevOps Center landing branch. Verify the pipeline topology, project attachment, and control-org authentication."
      else
        resolved_landing=$("$SKILL_DIR/scripts/resolve-devops-landing.sh" \
          --pipeline-id "$DEVOPS_PIPELINE" --target-org "$DEVOPS_ORG") \
          || die "could not derive the DevOps Center landing branch. Verify the pipeline topology and control-org authentication."
      fi
      if [ -n "$TRUNK" ] && [ "$TRUNK" != "$resolved_landing" ]; then
        die "--trunk '$TRUNK' disagrees with the pipeline topology landing branch '$resolved_landing'. The pipeline is authoritative."
      fi
      TRUNK="$resolved_landing"
      say "DevOps Center topology: landing branch=$TRUNK"
    elif [ -z "$TRUNK" ]; then
      die "DevOps Center init needs --devops-pipeline-id so it can derive the landing branch, or an explicit provisional --trunk before the pipeline exists."
    else
      say "WARNING: DevOps Center landing branch '$TRUNK' is provisional because no --devops-pipeline-id was supplied. Audit cannot verify topology until init is rerun with the pipeline id."
    fi
  fi

  head_ "Clone config -> $root"
  set_cfg mode          "$MODE"
  set_cfg delivery      "$DELIVERY"
  set_cfg trunk         "$TRUNK"
  set_cfg host          "$HOST"
  set_cfg review        "$REVIEW"
  set_cfg ticket.system "$TSYS"
  set_cfg ticket.project "$TPROJ"
  set_cfg ticket.remote "$TREMOTE"
  set_cfg ticket.pattern "$TPAT"
  set_cfg format        "$FORMAT"
  set_cfg pmd           "$PMD"
  set_cfg drift         "$DRIFT"
  set_cfg orgalias      "$ORG"
  set_cfg squash        "$SQUASH"
  set_cfg protected     "$PROTECTED"
  set_cfg devops.orgalias "$DEVOPS_ORG"
  set_cfg devops.projectid "$DEVOPS_PROJECT"
  set_cfg devops.pipelineid "$DEVOPS_PIPELINE"
  set_cfg devops.workmodel "$DEVOPS_WORK_MODEL"
  set_cfg devops.integrationbranch "$DEVOPS_INTEGRATION"
  set_cfg devops.environment "$DEVOPS_ENVIRONMENT"

  if [ "$(git config estate.delivery 2>/dev/null || echo direct)" = "devops-center" ]; then
    git config estate.ticket.system pattern
    git config estate.ticket.pattern '(^|[^[:alnum:]])WI-[0-9]+([^[:alnum:]]|$)'
    git config estate.devops.branchpattern '^WI-[0-9]+$'
    git config estate.devops.developmentbranchpattern '^dev/WI-[0-9]+$'
    git config estate.squash require
    local dc_protected dc_required dc_result dc_branch
    dc_protected=$(git config estate.protected 2>/dev/null || echo "")
    dc_required="$(git config estate.trunk 2>/dev/null || echo staging) main"
    if [ "$(git config --get estate.devops.workmodel 2>/dev/null || echo isolated)" = "shared" ]; then
      dc_required="$dc_required $(git config --get estate.devops.integrationbranch)"
    fi
    dc_result=""
    for dc_branch in $dc_protected $dc_required; do
      case " $dc_result " in
        *" $dc_branch "*) ;;
        *) dc_result="${dc_result:+$dc_result }$dc_branch" ;;
      esac
    done
    git config estate.protected "$dc_result"
    say "DevOps Center coherence: ticket=WI pattern, squash=require, owned branches protected"
  fi

  # host=none has no PR to review, so review=local is the only coherent answer.
  # Enforced here rather than trusted to the caller: an incoherent pair produces a
  # merge gate that checks for a record nothing ever writes.
  if [ "$(git config estate.host || echo)" = "none" ]; then
    git config estate.review local
    say "host=none -> review=local (forced: there is no PR to review)"
  fi

  set_target_org
  arm_hooks "$root"
  write_excludes "$root"
  mkdir -p "$(git rev-parse --git-common-dir)/estate"
  install_block "$root"
  warn_in_worktree "$root"
  warn_off_trunk
}

# ── init belongs in the main checkout ────────────────────────────
#
# The clone half writes per-clone state: git config (shared by every worktree, so
# fine), but also the CLAUDE.md block and the project-local target-org, which are
# per-WORKING-TREE. Run from a worktree, the block lands on the worktree's branch
# instead of trunk, and only set_target_org() redirects itself to the main checkout.
#
# A warning rather than a refusal, for the same reason as warn_off_trunk: init is
# idempotent and legitimately re-run, and a hard stop would leave a half-configured
# clone behind.
warn_in_worktree() {
  local gitdir common
  gitdir=$(git rev-parse --absolute-git-dir 2>/dev/null) || return 0
  common=$(git rev-parse --git-common-dir 2>/dev/null) || return 0
  case "$common" in /*) ;; *) common="$1/$common" ;; esac
  # Both sides resolved the SAME way. --absolute-git-dir is physical and a bare pwd
  # is logical, so under any symlinked path (macOS /var, a symlinked home) the
  # comparison is always true and this warns in the main checkout too.
  gitdir=$(cd "$gitdir" 2>/dev/null && pwd -P) || return 0
  common=$(cd "$common" 2>/dev/null && pwd -P) || return 0
  [ "$gitdir" != "$common" ] || return 0

  printf '\n'
  say "NOTE: init ran inside a WORKTREE, not the main checkout."
  say "      The managed block was written to this worktree's CLAUDE.md, which lives on"
  say "      this branch — not on trunk, where every other worktree reads it from."
  say "      The project-local target-org was written to the main checkout regardless."
  say "      Re-run init from the main checkout on trunk (it is idempotent) and commit"
  say "      the block there."
  printf '\n'
  return 0
}

# ── the project-local target org, in the MAIN checkout ───────
#
# ensure-worktree-config.sh sets target-org in a WORKTREE by copying the main
# clone's value — and there is nothing to copy if the main clone never had one.
# Real deploys run in the main checkout, so that is where the gap bites: sf fails
# with NoDefaultEnvError, whose own advice (`use -o / --target-org`) is blocked by
# guard-sf-flags.sh on purpose. The step dead-ends unless this is set here.
#
# .sf/config.json is gitignored, so this is machine-local state, not a change to
# anyone's tree. A missing or unhappy sf CLI is a warning, never a failed install:
# nothing else here depends on it, and re-running init fixes it later.
set_target_org() {
  local want have root
  want=$(git config estate.orgalias 2>/dev/null || echo "")
  [ -n "$want" ] || return 0

  # ── write it in the MAIN checkout, wherever init was run from ──────────────
  #
  # `sf config set` writes ./.sf/config.json relative to cwd. Run init from inside a
  # worktree and the file lands in the worktree — so the main checkout, which is
  # exactly where real deploys run and the only place this gap actually bites, still
  # has nothing. The step this function exists to unblock stays blocked, and the
  # install reports success.
  root=$(main_repo_root ".") || root="$PWD"

  have=""
  if [ -f "$root/.sf/config.json" ]; then
    if command -v jq >/dev/null 2>&1; then
      have=$(jq -r '."target-org" // empty' "$root/.sf/config.json" 2>/dev/null || echo "")
    else
      say "WARNING: $root/.sf/config.json exists but jq is missing, so its target-org cannot be read — left alone."
      return 0
    fi
  fi

  if [ "$have" = "$want" ]; then
    say "target-org = $want (already set project-locally)"
    return 0
  fi
  if [ -n "$have" ]; then
    # Someone pointed this clone at that org for a reason this script cannot see.
    # Silently repointing it would redirect every deploy made from here.
    say "WARNING: this clone's target-org is '$have', but estate.orgalias is '$want'."
    say "         Left as-is. Reconcile them deliberately:  sf config set target-org=$want"
    return 0
  fi

  if ! command -v sf >/dev/null 2>&1; then
    say "WARNING: sf CLI not found, so target-org was not set. Deploys from here will fail with"
    say "         NoDefaultEnvError. Once sf is installed:  sf config set target-org=$want"
    return 0
  fi
  if ( cd "$root" && sf config set "target-org=$want" >/dev/null 2>&1 ); then
    say "target-org = $want (project-local, $root/.sf/config.json — gitignored)"
  else
    say "WARNING: 'sf config set target-org=$want' failed in $root. Deploys from there will"
    say "         fail with NoDefaultEnvError, and --target-org is blocked by design."
    say "         Run it by hand:  cd '$root' && sf config set target-org=$want"
  fi
}

# ── the managed block belongs on trunk ───────────────────────
#
# A worktree materialises TRACKED content from the branch it was cut from. A block
# committed only on some other branch therefore exists in no worktree cut from
# trunk: every agent there reads whatever contract trunk still carries, while the
# hooks armed on this machine enforce this one. "Native mode: commit CLAUDE.md" is
# satisfied to the letter by a commit on the wrong branch, which is why the branch
# has to be checked on its own.
#
# A warning, not a refusal: init is idempotent and legitimately re-run mid-branch,
# and a hard stop would leave a half-configured clone behind.
warn_off_trunk() {
  [ "$(git config estate.mode || echo)" = "stealth" ] && return 0
  local branch want label
  branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
  want=$(git config estate.trunk 2>/dev/null || echo main)
  [ -n "$branch" ] || return 0
  [ "$branch" != "$want" ] || return 0

  label="'$branch'"
  [ "$branch" = "HEAD" ] && label="a detached HEAD"

  printf '\n'
  say "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  say "!!  WRONG BRANCH. This checkout is on $label; trunk is '$want'."
  say "!!"
  say "!!  The managed block was just written HERE. A worktree materialises"
  say "!!  tracked content from the branch it is cut from, so a block committed"
  say "!!  anywhere but '$want' exists in NO worktree cut from '$want' — every"
  say "!!  agent there reads the contract trunk still carries, while the hooks"
  say "!!  on this machine enforce this one. Nothing reports that disagreement:"
  say "!!  it surfaces as a guard blocking work the contract never mentioned."
  say "!!"
  say "!!  Check out '$want' and re-run init there (it is idempotent), then"
  say "!!  commit the block on '$want'."
  say "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  printf '\n'
  return 0
}

set_cfg() {
  [ -n "${2:-}" ] || return 0
  git config "estate.$1" "$2"
  say "estate.$1 = $2"
}

# ── core.hooksPath, preserving whatever it displaced ─────────
arm_hooks() {
  local want="$HOME_DIR/githooks" current abs
  current=$(git config core.hooksPath || echo "")
  if [ -n "$current" ] && [ "$current" != "$want" ]; then
    abs="$current"; case "$abs" in /*) ;; *) abs="$1/$current" ;; esac
    if [ -d "$abs" ]; then
      git config estate.chainhooks "$abs"
      say "chaining the project's existing hooks: $current (they still run, after ours)"
    fi
  elif [ -z "$current" ] && [ -d "$1/.husky" ]; then
    # husky's prepare script has not run yet in this clone, but it will the moment
    # someone runs npm install — and it will repoint hooksPath at .husky. Record it
    # now so the re-armer has somewhere to chain to when that happens.
    git config estate.chainhooks "$1/.husky"
    say "found .husky/ — recorded as estate.chainhooks so their gates keep running"
  fi
  git config core.hooksPath "$want"
  say "core.hooksPath = $want"
}

# ── .git/info/exclude: the per-clone gitignore ───────────────
#
# In stealth mode, CLAUDE.md and .claude/ are OURS and must not appear in the
# client's tree — but they also must not be added to THEIR .gitignore, which is a
# tracked file. .git/info/exclude is the per-clone equivalent: same effect, not a
# file anyone else ever sees. It lives in the common dir, so one entry covers every
# worktree.
write_excludes() {
  local f; f="$(git rev-parse --git-common-dir)/info/exclude"
  case "$f" in /*) ;; *) f="$1/$f" ;; esac
  mkdir -p "$(dirname "$f")"; touch "$f"
  # node_modules carries NO trailing slash, and must not be given one: a pattern
  # ending in / matches directories only, and ensure-worktree-config.sh SYMLINKS
  # node_modules into every worktree. A symlink is not a directory, so `node_modules/`
  # leaves it showing as untracked in each worktree — where one `git add -A` commits
  # a symlink to a machine-specific absolute path.
  local entries="tmp-retrieve/
node_modules"

  # .claude/ is excluded only where it is OURS. A repo that already TRACKS .claude/
  # keeps its own hooks and settings there, and excluding a tracked path makes
  # `git add .claude/settings.json` refuse a file git is already tracking, hides every
  # new file under it, and breaks lint-staged's re-stage after prettier rewrites one —
  # which leaves a permanently dirty tree and a commit that disagrees with the formatter.
  if [ -n "$(git ls-files -- .claude 2>/dev/null | head -1)" ]; then
    say ".claude/ is tracked here — leaving it OUT of exclude (excluding a tracked path breaks git add and any re-staging formatter)"
    # Skipping the write is not enough on its own: the harm is the line's PRESENCE,
    # and an earlier install wrote it in every clone set up before .claude/ was
    # tracked. Retract our own entry — and only ever that exact line.
    if grep -qxF '.claude/' "$f" 2>/dev/null; then
      { grep -vxF '.claude/' "$f" || true; } > "${f}.tmp$$" && mv "${f}.tmp$$" "$f" \
        && say "removed the stale .claude/ entry an earlier install left in exclude"
    fi
  else
    entries=".claude/
$entries"
  fi
  # Host instruction files are excluded only in stealth mode. In native mode they
  # must be committed so worktrees materialize the contract.
  if [ "$(git config estate.mode || echo)" = "stealth" ]; then
    case "$PLATFORM" in
      claude) entries="CLAUDE.md
$entries" ;;
      codex) entries="AGENTS.md
$entries" ;;
      both) entries="CLAUDE.md
AGENTS.md
$entries" ;;
    esac
  fi
  local added=0
  while IFS= read -r e; do
    [ -z "$e" ] && continue
    grep -qxF "$e" "$f" 2>/dev/null || { printf '%s\n' "$e" >> "$f"; added=$((added+1)); }
  done <<< "$entries"
  [ "$added" -gt 0 ] && say "added $added entry(ies) to $(basename "$(dirname "$f")")/exclude (untracked, per-clone)"
  return 0
}

# ── the CLAUDE.md managed block ──────────────────────────────
install_block_file() {
  local root="$1" target="$2" rendered status

  HOOK_NO_GATE=1 . "$HOME_DIR/claude-hooks/_config.sh"
  . "$HOME_DIR/claude-hooks/_block.sh"

  status=$(block_status "$target")
  rendered=$(mktemp)
  # Not `|| true`: a failed render must never reach block_install, or it replaces a
  # working contract with a malformed one that hashes as valid.
  if ! block_render "$HOME_DIR/templates/claude-md-block.md" > "$rendered"; then
    rm -f "$rendered"
    die "the managed instruction block failed to render (see above). $(basename "$target") was NOT modified."
  fi

  case "$status" in
    MODIFIED)
      # Never silently overwrite: the human may have edited it for a good reason,
      # and the diff is the only way to find out which.
      #
      # The advice here used to say "re-run to accept ours", which does nothing at
      # all — this branch returns before block_install, so a re-run reaches exactly
      # this point again and prints the same diff. Advice that cannot work is worse
      # than none: it costs a cycle and teaches people the tool is broken. So name
      # the operation that actually applies, and provide it (--force, below).
      if [ "$FORCE" = "1" ]; then
        say "the existing managed block does NOT match its recorded hash — overwriting it"
        say "because --force was given. The previous content is in git history if it mattered."
      else
        say "the existing managed block does NOT match its recorded hash — NOT overwriting."
        printf '\n'
        diff <(block_extract "$target") <(sed -e '1d' -e '$d' "$rendered") | head -40 || true
        printf '\n'
        say "Left = what is in the file, right = what the config says it should be. Then:"
        say "  keep OURS   $0 --block --force"
        say "  keep YOURS  edit nothing, and accept that the fence stays broken until the"
        say "              block is re-rendered — the hash cannot be made to match an edit"
        say "              by hand, which is the entire point of it."
        rm -f "$rendered"
        return 0
      fi ;;
    OK)      say "managed block already current in $(basename "$target")" ;;
    MISSING) say "inserting the managed block into $(basename "$target")" ;;
  esac
  block_install "$target" "$rendered"
  rm -f "$rendered"

  if [ "$(git config estate.mode || echo)" != "stealth" ]; then
    say "NOTE: native mode — COMMIT $(basename "$target"). A worktree materialises tracked"
    say "      content only, so an uncommitted $(basename "$target") does not exist in any worktree."
  fi
}

install_block() {
  local root="$1" target
  case "$PLATFORM" in
    claude)
      target="$root/CLAUDE.md"
      [ -f "$target" ] || { [ -f "$root/.claude/CLAUDE.md" ] && target="$root/.claude/CLAUDE.md"; }
      install_block_file "$root" "$target"
      ;;
    codex)
      install_block_file "$root" "$root/AGENTS.md"
      ;;
    both)
      target="$root/CLAUDE.md"
      [ -f "$target" ] || { [ -f "$root/.claude/CLAUDE.md" ] && target="$root/.claude/CLAUDE.md"; }
      install_block_file "$root" "$target"
      install_block_file "$root" "$root/AGENTS.md"
      ;;
  esac
}

# ═══════════════════════════════════════════════════════════════
DO_MACHINE=0; DO_REPO=0; DO_BLOCK=0; FORCE=0; PLATFORM="both"
while [ $# -gt 0 ]; do
  case "$1" in
    --machine-only) DO_MACHINE=1 ;;
    --repo)         DO_MACHINE=1; DO_REPO=1 ;;
    --block)        DO_BLOCK=1 ;;
    # Only honoured with --block. A full init must never silently replace a block
    # someone edited on purpose; asking for the overwrite explicitly is the point.
    --force)        FORCE=1 ;;
    --platform)       PLATFORM="$2"; shift ;;
    --mode)           MODE="$2"; shift ;;
    --delivery)       DELIVERY="$2"; shift ;;
    --trunk)          TRUNK="$2"; shift ;;
    --host)           HOST="$2"; shift ;;
    --review)         REVIEW="$2"; shift ;;
    --ticket-system)  TSYS="$2"; shift ;;
    --ticket-project) TPROJ="$2"; shift ;;
    --ticket-remote)  TREMOTE="$2"; shift ;;
    --ticket-pattern) TPAT="$2"; shift ;;
    --format)         FORMAT="$2"; shift ;;
    --pmd)            PMD="$2"; shift ;;
    --drift)          DRIFT="$2"; shift ;;
    --org-alias)      ORG="$2"; shift ;;
    --squash)         SQUASH="$2"; shift ;;
    --protected)      PROTECTED="$2"; shift ;;
    --devops-org-alias) DEVOPS_ORG="$2"; shift ;;
    --devops-project-id) DEVOPS_PROJECT="$2"; shift ;;
    --devops-pipeline-id) DEVOPS_PIPELINE="$2"; shift ;;
    --devops-work-model) DEVOPS_WORK_MODEL="$2"; shift ;;
    --devops-integration-branch) DEVOPS_INTEGRATION="$2"; shift ;;
    --devops-environment) DEVOPS_ENVIRONMENT="$2"; shift ;;
    -h|--help) sed -n '1,40p' "$0"; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
  shift
done

case "$PLATFORM" in claude|codex|both) ;; *) die "--platform must be claude, codex, or both" ;; esac
case "${DELIVERY:-direct}" in direct|engine|devops-center) ;; *) die "--delivery must be direct, engine, or devops-center" ;; esac

# --force is a deliberate, targeted overwrite of ONE artifact. A full init that
# silently replaced a block someone edited on purpose would be the most destructive
# thing here, so the combination is refused rather than quietly honoured.
if [ "$FORCE" = "1" ] && [ "$DO_REPO" = "1" ]; then
  die "--force applies to --block only. Run the init first, then, if the block still
  reports as hand-edited and you have read the diff:  $0 --block --force"
fi

# Ownership is a precondition, not a late block-rendering error. --repo includes
# the machine half, so this must run before install_machine to keep the failed
# operation side-effect free. --machine-only remains available when the user wants
# to refresh hooks without changing repository contracts.
if [ "$DO_REPO" = "1" ] || [ "$DO_BLOCK" = "1" ]; then
  preflight_contract_ownership
fi

[ "$DO_MACHINE" = "1" ] && install_machine
[ "$DO_REPO" = "1" ] && install_repo
if [ "$DO_BLOCK" = "1" ] && [ "$DO_REPO" = "0" ]; then
  git rev-parse --git-dir >/dev/null 2>&1 || die "not a git repository."
  install_block "$(git rev-parse --show-toplevel)"
fi
[ "$DO_MACHINE" = "0" ] && [ "$DO_REPO" = "0" ] && [ "$DO_BLOCK" = "0" ] && { sed -n '1,40p' "$0"; exit 1; }

head_ "Done. Verify with:  $SKILL_DIR/scripts/audit.sh"
