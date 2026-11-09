#!/bin/bash
# Requirement 19: in stealth mode, nothing of ours is committed to the client's tree.
#
# The stack never tracks hook logic or registration in the repo in ANY mode (logic
# lives in ~/.estate, registration in the user-level settings file). In STEALTH
# mode, additionally, the CLAUDE.md contract and .claude/ are kept out of the tree
# entirely, via .git/info/exclude — so a client reviewing their own repo sees no
# estate artifact. This suite proves that end to end by actually running the
# installer's repo half, and contrasts it with NATIVE mode, where CLAUDE.md is
# meant to be committed (a worktree materialises tracked content only, so an ignored
# CLAUDE.md would silently not exist in any worktree — requirement 13).
#
# Black box on purpose: it runs scripts/install.sh so the real write_excludes /
# install_block are what is under test. HOME is redirected to a throwaway dir so the
# machine half touches nothing real, and sf/gh are stubbed to no-ops so the install
# does not block on a CLI's first-run/network work.
#
# Run: bash references/hooks/tests/stealth-footprint.test.sh

set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SKILL=$(cd "$HERE/../../.." && pwd)
INSTALL="$SKILL/scripts/install.sh"
[ -f "$INSTALL" ] || { echo "missing installer: $INSTALL"; exit 1; }
command -v git >/dev/null 2>&1 || { echo "git required"; exit 1; }
command -v jq  >/dev/null 2>&1 || { echo "jq required (install merges settings with it); skipping"; exit 0; }

WORK=$(mktemp -d "${TMPDIR:-/tmp}/stealth footprint.XXXXXX") || exit 1
WORK=$(cd "$WORK" && pwd -P)
trap 'rm -rf "$WORK"' EXIT

# instant no-op sf/gh so the installer's `sf config set` etc. cannot stall.
BIN="$WORK/bin"; mkdir -p "$BIN"
printf '#!/bin/bash\nexit 0\n' > "$BIN/sf"; printf '#!/bin/bash\nexit 0\n' > "$BIN/gh"
chmod +x "$BIN/sf" "$BIN/gh"

PASS=0; FAIL=0
ok() { PASS=$((PASS+1)); echo "  PASS $1"; }
no() { FAIL=$((FAIL+1)); echo "  FAIL $1"; }

# init_repo <mode> -> prints the repo path, having run a full repo init in $mode
init_repo() {
  local mode="$1" home repo
  home="$WORK/home-$mode"; repo="$WORK/repo-$mode"; mkdir -p "$home" "$repo"
  ( cd "$repo" && git init -q -b main \
      && git config user.email t@t.test && git config user.name t \
      && printf '{"packageDirectories":[{"path":"force-app","default":true}]}\n' > sfdx-project.json \
      && echo x > README.md && git add -A && git commit -qm init ) >/dev/null 2>&1
  # MUST run install FROM INSIDE the throwaway repo — install.sh acts on cwd's repo,
  # so running it anywhere else would configure whatever repo the test happens to sit
  # in. The subshell confines both cwd and the redirected HOME.
  ( cd "$repo" && HOME="$home" PATH="$BIN:$PATH" perl -e 'alarm 90; exec @ARGV' bash "$INSTALL" \
      --repo --mode "$mode" --trunk main --host none --review local \
      --org-alias testorg --drift off ) >/dev/null 2>&1
  printf '%s' "$repo"
}

echo "== stealth: a client-tree init leaves NOTHING of ours to commit =="
SREPO=$(init_repo stealth)
DIRTY=$(git -C "$SREPO" status --porcelain)
[ -z "$DIRTY" ] && ok "git status is clean (no untracked/modified artifacts)" \
                || no "git status is NOT clean in stealth: [$DIRTY]"
ARTS=$(git -C "$SREPO" ls-files | grep -iE 'CLAUDE|\.claude|estate' || true)
[ -z "$ARTS" ] && ok "no estate artifact is tracked" \
               || no "tracked artifacts present in stealth: [$ARTS]"
if grep -qxF 'CLAUDE.md' "$SREPO/.git/info/exclude" 2>/dev/null; then
  ok "CLAUDE.md is in .git/info/exclude"
else
  no "CLAUDE.md is NOT excluded in stealth"
fi
if [ -f "$SREPO/CLAUDE.md" ] && git -C "$SREPO" check-ignore CLAUDE.md >/dev/null 2>&1; then
  ok "CLAUDE.md exists on disk but is git-ignored (present for the agent, invisible to the client)"
else
  no "CLAUDE.md is not both present and ignored in stealth"
fi

echo "== native (contrast): CLAUDE.md is meant to be committed, so it must NOT be ignored =="
NREPO=$(init_repo native)
if [ -f "$NREPO/CLAUDE.md" ] && ! git -C "$NREPO" check-ignore CLAUDE.md >/dev/null 2>&1; then
  ok "native: CLAUDE.md exists and is committable (not ignored)"
else
  no "native: CLAUDE.md is missing or wrongly ignored"
fi
# the contrast that proves the stealth exclusion is mode-specific, not blanket:
grep -qxF 'CLAUDE.md' "$NREPO/.git/info/exclude" 2>/dev/null \
  && no "native: CLAUDE.md was excluded (it must be committed on trunk — req 13)" \
  || ok "native: CLAUDE.md is not excluded"

echo "== stealth: tracked host contracts stop install and audit reports the conflict =="
THOME="$WORK/home-stealth-tracked"
TREPO="$WORK/repo-stealth-tracked"
TOUT="$WORK/stealth-tracked.out"
mkdir -p "$THOME" "$TREPO"
(
  cd "$TREPO" || exit 1
  git init -q -b main
  git config user.email t@t.test
  git config user.name t
  printf '{"packageDirectories":[{"path":"force-app","default":true}]}\n' > sfdx-project.json
  printf '# Client Claude instructions\n' > CLAUDE.md
  printf '# Client Codex instructions\n' > AGENTS.md
  git add -A
  git commit -qm init
)
CLAUDE_BEFORE=$(git -C "$TREPO" hash-object CLAUDE.md)
AGENTS_BEFORE=$(git -C "$TREPO" hash-object AGENTS.md)

if ( cd "$TREPO" && HOME="$THOME" PATH="$BIN:$PATH" bash "$INSTALL" \
    --repo --platform both --mode stealth --trunk main --host none --review local \
    --org-alias testorg --drift off ) >"$TOUT" 2>&1; then
  no "stealth install accepted tracked host contracts"
else
  ok "stealth install refuses tracked host contracts"
fi
grep -q 'Nothing was changed' "$TOUT" \
  && ok "installer explains that the failed operation was side-effect free" \
  || no "installer did not report the side-effect-free refusal"
[ ! -e "$THOME/.estate" ] && [ -z "$(git -C "$TREPO" config --get estate.mode 2>/dev/null)" ] \
  && ok "ownership preflight runs before machine and clone mutation" \
  || no "failed ownership preflight left machine or clone state behind"
[ "$CLAUDE_BEFORE" = "$(git -C "$TREPO" hash-object CLAUDE.md)" ] \
  && [ "$AGENTS_BEFORE" = "$(git -C "$TREPO" hash-object AGENTS.md)" ] \
  && ok "tracked host contracts were not modified" \
  || no "tracked host contracts changed during the refused install"

git -C "$TREPO" config estate.mode stealth
if ( cd "$TREPO" && HOME="$THOME" bash "$INSTALL" --block --platform both ) >"$TOUT" 2>&1; then
  no "stealth block update accepted tracked host contracts"
else
  ok "stealth block update refuses tracked host contracts"
fi

if ( cd "$TREPO" && HOME="$THOME" bash "$SKILL/scripts/audit.sh" --no-probe ) >"$TOUT" 2>&1; then
  no "audit reported clean with tracked stealth contracts"
else
  ok "audit fails with tracked stealth contracts"
fi
grep -q 'CLAUDE.md is tracked while estate.mode=stealth' "$TOUT" \
  && grep -q 'AGENTS.md is tracked while estate.mode=stealth' "$TOUT" \
  && ok "audit names both tracked ownership violations" \
  || no "audit did not name both tracked ownership violations"

echo
printf '%d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
