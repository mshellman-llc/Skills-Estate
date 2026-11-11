#!/bin/bash
# Requirement 20: there is a clean uninstall. install -> (dirty) -> uninstall must
# leave the repo and the machine as if the skill had never run, and must remove ONLY
# what install wrote (a user's own CLAUDE.md prose survives).
#
# Black box: runs the real scripts/install.sh then scripts/uninstall.sh. HOME is
# redirected to a throwaway dir so the machine half never touches the real machine,
# and sf/gh are stubbed to no-ops so install does not stall on a CLI's first run.
#
# Run: bash references/hooks/tests/uninstall.test.sh

set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SKILL=$(cd "$HERE/../../.." && pwd)
INSTALL="$SKILL/scripts/install.sh"
UNINSTALL="$SKILL/scripts/uninstall.sh"
for s in "$INSTALL" "$UNINSTALL"; do [ -f "$s" ] || { echo "missing script: $s"; exit 1; }; done
command -v git >/dev/null 2>&1 || { echo "git required"; exit 1; }
command -v jq  >/dev/null 2>&1 || { echo "jq required; skipping"; exit 0; }

WORK=$(mktemp -d "${TMPDIR:-/tmp}/uninstall test.XXXXXX") || exit 1
WORK=$(cd "$WORK" && pwd -P)
trap 'rm -rf "$WORK"' EXIT
BIN="$WORK/bin"; mkdir -p "$BIN"
printf '#!/bin/bash\nexit 0\n' > "$BIN/sf"; printf '#!/bin/bash\nexit 0\n' > "$BIN/gh"
chmod +x "$BIN/sf" "$BIN/gh"

HOMEDIR=""   # set per run
PASS=0; FAIL=0
ok() { PASS=$((PASS+1)); echo "  PASS $1"; }
no() { FAIL=$((FAIL+1)); echo "  FAIL $1"; }

# fresh throwaway repo + home; $1 = tag
setup() {
  local repo="$WORK/repo-$1" home="$WORK/home-$1"; mkdir -p "$repo" "$home"
  ( cd "$repo" && git init -q -b main && git config user.email t@t.test && git config user.name t \
      && printf '{"packageDirectories":[{"path":"force-app","default":true}]}\n' > sfdx-project.json \
      && echo x > README.md && git add -A && git commit -qm init ) >/dev/null 2>&1
  printf '%s\t%s' "$repo" "$home"
}
run_install()   { ( cd "$1" && HOME="$2" PATH="$BIN:$PATH" perl -e 'alarm 90; exec @ARGV' bash "$INSTALL"   --repo --mode native --trunk main --host none --review local --org-alias testorg --drift off ) >/dev/null 2>&1; }
run_uninstall() { ( cd "$1" && HOME="$2" PATH="$BIN:$PATH" perl -e 'alarm 90; exec @ARGV' bash "$UNINSTALL" ) >/dev/null 2>&1; }

# ── Part 1: full install then uninstall leaves nothing ──────────────────────────
echo "== install then uninstall reverses every mutation =="
IFS=$'\t' read -r REPO HOME1 <<<"$(setup full)"
run_install "$REPO" "$HOME1"
# sanity: install actually set things up (else the uninstall asserts prove nothing)
INSTALLED_OK=1
git -C "$REPO" config --get-regexp '^aleysian\.' >/dev/null 2>&1 || INSTALLED_OK=0
[ -d "$HOME1/.aleysian" ] || INSTALLED_OK=0
[ "$INSTALLED_OK" = 1 ] && ok "precondition: install configured the repo and ~/.aleysian" \
                        || no "precondition FAILED — install did not set up; later asserts are meaningless"

run_uninstall "$REPO" "$HOME1"
git -C "$REPO" config --get-regexp '^aleysian\.' >/dev/null 2>&1 \
  && no "aleysian git config still present" || ok "no aleysian git config"
hp=$(git -C "$REPO" config core.hooksPath 2>/dev/null || echo "")
[ -z "$hp" ] && ok "core.hooksPath cleared" || no "core.hooksPath still set: $hp"
[ -d "$HOME1/.aleysian" ] && no "~/.aleysian still exists" || ok "~/.aleysian removed"
if [ -f "$HOME1/.claude/settings.json" ]; then
  if jq -e --arg h "$HOME1/.aleysian" '[.. | .command? // empty | select(contains($h))] | length == 0' "$HOME1/.claude/settings.json" >/dev/null 2>&1; then
    ok "settings.json has no entry pointing at ~/.aleysian"
  else
    no "settings.json still references ~/.aleysian"
  fi
else
  ok "settings.json absent (nothing to reference)"
fi
EX="$REPO/.git/info/exclude"
if [ -f "$EX" ] && grep -qxE 'CLAUDE\.md|\.claude/|tmp-retrieve/|node_modules' "$EX"; then
  no "exclude still has our entries"
else
  ok "exclude entries removed"
fi
[ -d "$REPO/.git/aleysian" ] && no ".git/aleysian state remains" || ok ".git/aleysian removed"
[ -f "$REPO/CLAUDE.md" ] && no "CLAUDE.md remains (was only our block)" || ok "CLAUDE.md removed (was only our block)"

# ── Part 2: user's own CLAUDE.md prose survives; only our block is removed ───────
echo "== a user's own CLAUDE.md content is preserved; only the managed block goes =="
IFS=$'\t' read -r REPO2 HOME2 <<<"$(setup prose)"
printf '# My project notes\n\nHand-written guidance the client owns.\n' > "$REPO2/CLAUDE.md"
run_install "$REPO2" "$HOME2"
grep -q 'BEGIN aleysian-delivery-standards' "$REPO2/CLAUDE.md" && ok "install added the managed block to the existing CLAUDE.md" || no "install did not add the block"
run_uninstall "$REPO2" "$HOME2"
if [ -f "$REPO2/CLAUDE.md" ] && grep -q 'Hand-written guidance the client owns.' "$REPO2/CLAUDE.md" \
   && ! grep -q 'aleysian-delivery-standards' "$REPO2/CLAUDE.md"; then
  ok "user prose kept, managed block removed"
else
  no "user CLAUDE.md not correctly preserved/cleaned"
fi

# ── Part 3: uninstall is idempotent ─────────────────────────────────────────────
echo "== uninstall is safe to re-run =="
if run_uninstall "$REPO" "$HOME1"; then ok "second uninstall exits cleanly" ; else no "second uninstall errored"; fi

echo
printf '%d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
