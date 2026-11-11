#!/bin/bash
# uninstall.sh — reverse everything install.sh did, leaving the repo and the machine
# as if the skill had never run (requirement 20). Trust in an enforcement stack is
# proportional to how easily it comes out; this is that exit.
#
#   MACHINE  retract the aleysian hook entries (and any legacy retrieve deny rules)
#            from ~/.claude/settings.json, then remove ~/.aleysian.
#   CLONE    restore core.hooksPath (to whatever it displaced, else default), remove
#            the aleysian.* git config, strip the .git/info/exclude entries and the
#            CLAUDE.md managed block, and delete the .git/aleysian state dir.
#
#   uninstall.sh                 both halves (default)
#   uninstall.sh --machine-only  ~/.aleysian + settings only
#   uninstall.sh --repo          this clone only
#
# Idempotent and safe to re-run. It removes ONLY what install wrote: a user's own
# hooks in settings.json, their own deny rules, and any CLAUDE.md content outside our
# fence are all left untouched. The project-local .sf/config.json (your target-org)
# is deliberately left alone.
set -u

HOME_DIR="$HOME/.aleysian"
DO_MACHINE=0; DO_REPO=0

head_() { printf '\n== %s ==\n' "$*"; }
say()   { printf '   %s\n' "$*"; }
die()   { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

while [ $# -gt 0 ]; do
  case "$1" in
    --machine-only) DO_MACHINE=1 ;;
    --repo)         DO_REPO=1 ;;
    -h|--help)      sed -n '1,20p' "$0"; exit 0 ;;
    *)              die "unknown argument: $1" ;;
  esac
  shift
done
# no flag => do both
[ "$DO_MACHINE" = "0" ] && [ "$DO_REPO" = "0" ] && { DO_MACHINE=1; DO_REPO=1; }

uninstall_repo() {
  head_ "Clone: reverse the per-repo setup"
  git rev-parse --git-dir >/dev/null 2>&1 || { say "not a git repository — nothing to reverse here"; return 0; }
  local root common; root=$(git rev-parse --show-toplevel 2>/dev/null)
  common=$(git rev-parse --git-common-dir 2>/dev/null); case "$common" in /*) ;; *) common="$root/$common" ;; esac

  # 1. core.hooksPath — restore whatever we displaced, recorded in aleysian.chainhooks;
  #    otherwise clear it back to git's default (.git/hooks). Only touch it if it is
  #    still ours, so a hooksPath a user set for their own reasons is left alone.
  local hp chain; hp=$(git config core.hooksPath 2>/dev/null || echo "")
  chain=$(git config aleysian.chainhooks 2>/dev/null || echo "")
  if [ "$hp" = "$HOME_DIR/githooks" ]; then
    if [ -n "$chain" ] && [ -d "$chain" ]; then
      git config core.hooksPath "$chain"; say "restored core.hooksPath -> $chain (the hooks we had chained)"
    else
      git config --unset core.hooksPath 2>/dev/null || true; say "cleared core.hooksPath (back to default .git/hooks)"
    fi
  elif [ -n "$hp" ]; then
    say "core.hooksPath is '$hp' — not ours, left alone"
  fi

  # 2. the aleysian.* config (this also drops aleysian.chainhooks read above)
  if git config --get-regexp '^aleysian\.' >/dev/null 2>&1; then
    git config --remove-section aleysian 2>/dev/null && say "removed the [aleysian] git config section"
  else
    say "no [aleysian] git config present"
  fi

  # 3. the .git/info/exclude entries install added — exact-line matches only
  local f="$common/info/exclude"
  if [ -f "$f" ]; then
    local before after e; before=$(grep -c '' "$f" 2>/dev/null || echo 0)
    for e in 'CLAUDE.md' 'AGENTS.md' '.claude/' 'tmp-retrieve/' 'node_modules'; do
      { grep -vxF "$e" "$f" || true; } > "$f.tmp$$" && mv "$f.tmp$$" "$f"
    done
    after=$(grep -c '' "$f" 2>/dev/null || echo 0)
    say "removed $((before-after)) exclude entry(ies) from info/exclude"
  fi

  # 4. the CLAUDE.md managed block, in either location it may live. Strip only the
  #    fenced block; keep any other content. If nothing but the block was there,
  #    remove the file. (In stealth the file is entirely ours and goes; in native it
  #    may hold user prose, which stays.)
  local cf; for cf in "$root/CLAUDE.md" "$root/AGENTS.md" "$root/.claude/CLAUDE.md"; do
    [ -f "$cf" ] || continue
    grep -q '^<!-- BEGIN aleysian-delivery-standards' "$cf" 2>/dev/null || continue
    awk '
      /^<!-- BEGIN aleysian-delivery-standards/ { skip=1 }
      skip==0 { print }
      /<!-- END aleysian-delivery-standards -->/ { skip=0 }
    ' "$cf" > "$cf.tmp$$"
    if grep -q '[^[:space:]]' "$cf.tmp$$" 2>/dev/null; then
      mv "$cf.tmp$$" "$cf"; say "removed the managed block from $cf (kept the rest)"
    else
      rm -f "$cf.tmp$$" "$cf"; say "removed $cf (it held only our block)"
    fi
  done

  # 5. machine-local state
  if [ -d "$common/aleysian" ]; then
    rm -rf "$common/aleysian" && say "removed .git/aleysian state (logs, dod-state, pending-jobs)"
  fi

  [ -f "$root/.sf/config.json" ] && say "left .sf/config.json (your target-org) alone — remove by hand if you want it gone"
}

uninstall_machine() {
  head_ "Machine: retract settings entries and remove $HOME_DIR"
  local settings
  for settings in "$HOME/.claude/settings.json" "$HOME/.codex/hooks.json"; do
  if [ -f "$settings" ]; then
    if command -v jq >/dev/null 2>&1; then
      local backup tmp; backup="${settings}.bak.$(date -u +%Y%m%dT%H%M%SZ 2>/dev/null || echo manual)"
      cp "$settings" "$backup"
      tmp="${settings}.tmp$$"
      # Drop every hook command that points into ~/.aleysian; prune the matcher-groups
      # and event arrays that become empty; drop the legacy retrieve deny rules. Leave
      # the user's own hooks and their own deny rules exactly as they were.
      if jq --arg home "$HOME_DIR" '
          (.hooks // {}) as $h
          | .hooks = (
              $h
              | to_entries
              | map(.value |= ( map(.hooks |= map(select(((.command // "") | contains($home)) | not)))
                                | map(select((.hooks | length) > 0)) ))
              | map(select((.value | length) > 0))
              | from_entries
            )
          | if (.hooks | length) == 0 then del(.hooks) else . end
          | if (.permissions.deny) then
              .permissions.deny |= map(select(test("sf project retrieve|sfdx project retrieve|sfdx force:source:retrieve") | not))
            else . end
          | if (.permissions.deny? // []) == [] then (.permissions |= del(.deny)) else . end
          | if (.permissions? // {}) == {} then del(.permissions) else . end
        ' "$settings" > "$tmp" 2>/dev/null && jq -e . "$tmp" >/dev/null 2>&1; then
        mv "$tmp" "$settings"
        say "retracted aleysian hook + legacy deny entries from $settings (backup: $(basename "$backup"))"
      else
        rm -f "$tmp"
        say "WARNING: could not rewrite $settings safely — left unchanged. Remove the ~/.aleysian entries by hand."
      fi
    else
      say "WARNING: jq not installed — cannot edit $settings safely. Remove the ~/.aleysian hook entries by hand."
    fi
  else
    say "no $settings to edit"
  fi
  done

  if [ -d "$HOME_DIR" ]; then
    rm -rf "$HOME_DIR" && say "removed $HOME_DIR"
  else
    say "$HOME_DIR already absent"
  fi
}

[ "$DO_REPO" = "1" ]    && uninstall_repo
[ "$DO_MACHINE" = "1" ] && uninstall_machine

head_ "Done"
say "Verify with:  git config --get-regexp aleysian   (expect nothing)"
say "              ls ~/.aleysian                       (expect: No such file)"
