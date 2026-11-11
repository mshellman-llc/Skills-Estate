#!/bin/bash
# Regression tests for claude-hooks/guard-local-merge.sh — blocks local git merge
# into trunk on hosted repos (GitHub/GitLab/Azure), where the PR mechanism is the
# correct landing path.
#
# The gap this hook closes: guard-pr-merge.sh intercepts `gh pr merge` (the host's
# merge command) but not `git merge` (a local merge). An agent doing
# `git merge feature && git push` bypassed the entire PR flow — no review artifact,
# no merge record, untraceable commits on trunk.
#
# Coverage:
#   - BLOCKS local merge into trunk on GitHub/GitLab/Azure
#   - ALLOWS merge on non-trunk branches (syncing trunk down)
#   - ALLOWS merging remote-tracking refs (origin/main — what git pull does)
#   - INERT on host=none (local merge IS the mechanism there)
#   - INERT on host=bitbucket (guard-push.sh is the gate there)
#   - Escape hatch ALEY_ALLOW_LOCAL_MERGE=1 is honoured
#   - Non-merge commands are not this hook's business
#
# Self-contained: builds its own throwaway repos, touches nothing else.
#
# Run: bash references/hooks/tests/guard-local-merge.test.sh

set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
HOOK="${SFDS_LOCAL_MERGE_HOOK:-$HERE/../claude-hooks/guard-local-merge.sh}"
[ -f "$HOOK" ] || { echo "missing hook: $HOOK"; exit 1; }

command -v python3 >/dev/null 2>&1 || { echo "python3 required; skipping"; exit 0; }
command -v git     >/dev/null 2>&1 || { echo "git required"; exit 1; }

TMP=$(mktemp -d "${TMPDIR:-/tmp}/guard-local-merge.XXXXXX") || exit 1
TMP=$(cd "$TMP" && pwd -P)
OUT="$TMP/hook.out"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

# A base repo: one commit on main, GitHub host, native mode.
mkbase() { # $1=dir [$2=host (default github)]
  local d="$1" h="${2:-github}"
  mkdir -p "$d"
  ( cd "$d" \
    && git init -q -b main . >/dev/null 2>&1 \
    && git config user.email t@t.test && git config user.name t \
    && git config aleysian.mode native \
    && git config aleysian.trunk main \
    && git config aleysian.host "$h" \
    && echo x > readme.md && git add -A >/dev/null 2>&1 \
    && git commit -qm init >/dev/null 2>&1 )
}

# Create a feature branch with one commit.
mkfeature() { # $1=dir $2=branch-name
  ( cd "$1" \
    && git checkout -q -b "$2" \
    && echo "feature work" > feature.txt \
    && git add -A >/dev/null 2>&1 \
    && git commit -qm "feat: feature work" >/dev/null 2>&1 \
    && git checkout -q main )
}

PASS=0; FAIL=0

run() { # $1=expect(allow|block) $2=cwd $3=label $4=command text
  local want="$1" cwd="$2" label="$3" cmd="$4" got rc
  printf '%s' "$cmd" \
    | python3 -c 'import json,sys; print(json.dumps({"tool_name":"Bash","tool_input":{"command":sys.stdin.read()}}))' \
    | ( cd "$cwd" && bash "$HOOK" ) >"$OUT" 2>&1
  rc=$?
  got=allow; [ $rc -ne 0 ] && got=block
  if [ "$got" = "$want" ]; then
    PASS=$((PASS+1)); printf '  PASS [%s] %s\n' "$got" "$label"
  else
    FAIL=$((FAIL+1)); printf '  FAIL expected=%s got=%s :: %s\n' "$want" "$got" "$label"; sed -n '2,4p' "$OUT"
  fi
}

# ── core: local merge into trunk on GitHub is BLOCKED ─────────────────────────
echo "== local merge into trunk on hosted repos is blocked =="
GH="$TMP/gh-merge"; mkbase "$GH"; mkfeature "$GH" "feat/42-thing"
run block "$GH" "git merge feature into main (github)"         "git merge feat/42-thing"
run block "$GH" "git merge --squash feature into main"         "git merge --squash feat/42-thing"
run block "$GH" "git merge --no-ff feature into main"          "git merge --no-ff feat/42-thing"

echo "== same on GitLab and Azure =="
GL="$TMP/gl-merge"; mkbase "$GL" gitlab; mkfeature "$GL" "feat/gl"
run block "$GL" "git merge feature into main (gitlab)"         "git merge feat/gl"

AZ="$TMP/az-merge"; mkbase "$AZ" azure; mkfeature "$AZ" "feat/az"
run block "$AZ" "git merge feature into main (azure)"          "git merge feat/az"

# ── allowed: merging into a non-trunk branch (syncing down) ───────────────────
echo "== merging trunk into a feature branch is allowed (syncing down) =="
SYNC="$TMP/sync-down"; mkbase "$SYNC"; mkfeature "$SYNC" "feat/sync"
( cd "$SYNC" && git checkout -q feat/sync )
run allow "$SYNC" "git merge main into feature (syncing down)" "git merge main"

# ── allowed: merging a remote-tracking ref (what git pull does) ───────────────
echo "== merging origin/* is allowed (syncing with remote) =="
# Need an actual remote-tracking ref for the rev-parse check.
REMOTE_BASE="$TMP/remote-base"; mkbase "$REMOTE_BASE"
REMOTE_CLONE="$TMP/remote-clone"
git clone -q "$REMOTE_BASE" "$REMOTE_CLONE" 2>/dev/null
( cd "$REMOTE_CLONE" \
  && git config aleysian.mode native \
  && git config aleysian.trunk main \
  && git config aleysian.host github )
run allow "$REMOTE_CLONE" "git merge origin/main (remote sync)" "git merge origin/main"

# ── inert on host=none (local merge IS the mechanism) ─────────────────────────
echo "== inert on host=none =="
NONE="$TMP/host-none"; mkbase "$NONE" none; mkfeature "$NONE" "feat/local"
run allow "$NONE" "git merge on host=none (aleysian-merge territory)" "git merge feat/local"

# ── inert on host=bitbucket (guard-push.sh is the gate) ──────────────────────
echo "== inert on host=bitbucket =="
BB="$TMP/host-bb"; mkbase "$BB" bitbucket; mkfeature "$BB" "feat/bb"
run allow "$BB" "git merge on host=bitbucket (push gate territory)"   "git merge feat/bb"

echo "== DevOps Center protects every pipeline branch =="
DC="$TMP/devops-center"; mkbase "$DC"; mkfeature "$DC" "WI-000001"
( cd "$DC" && git config aleysian.delivery devops-center \
  && git config aleysian.trunk staging \
  && git config aleysian.protected "staging main" )
run block "$DC" "main is protected even when staging is trunk" "git merge WI-000001"
ALEY_ALLOW_LOCAL_MERGE=1 \
  run block "$DC" "local-merge hatch does not unlock a DevOps stage" "git merge WI-000001"

# ── escape hatch ──────────────────────────────────────────────────────────────
echo "== escape hatch ALEY_ALLOW_LOCAL_MERGE=1 is honoured =="
ALEY_ALLOW_LOCAL_MERGE=1 \
  run allow "$GH" "escape hatch allows the merge" "git merge feat/42-thing"

# ── non-merge commands are not this hook's business ───────────────────────────
echo "== non-merge commands are ignored =="
run allow "$GH" "git status is not a merge"    "git status"
run allow "$GH" "git commit is not a merge"    "git commit -m 'test'"
run allow "$GH" "git push is not a merge"      "git push origin main"
run allow "$GH" "gh pr merge is not git merge" "gh pr merge --squash --delete-branch"

# ── no aleysian.mode = inert (master gate) ────────────────────────────────────
echo "== no aleysian.mode = inert (master gate) =="
UNMANAGED="$TMP/unmanaged"
mkdir -p "$UNMANAGED"
( cd "$UNMANAGED" \
  && git init -q -b main . >/dev/null 2>&1 \
  && git config user.email t@t.test && git config user.name t \
  && echo x > readme.md && git add -A >/dev/null 2>&1 \
  && git commit -qm init >/dev/null 2>&1 \
  && git checkout -q -b feat/un \
  && echo y > y.txt && git add -A >/dev/null 2>&1 \
  && git commit -qm feat >/dev/null 2>&1 \
  && git checkout -q main )
run allow "$UNMANAGED" "no aleysian.mode -> master gate exits 0" "git merge feat/un"

echo
echo "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
