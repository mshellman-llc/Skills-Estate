#!/bin/bash
# Regression tests for claude-hooks/ensure-worktree-config.sh.
#
# This hook NEVER blocks — it exits 0 on every path. So an exit-code-only suite
# would pass unconditionally while proving nothing. Each case here checks three
# things instead:
#
#   the exit code    still allow, always. A fixer that blocks is a bug.
#   the OUTPUT       it must be silent unless it changed something, and it must
#                    say what it changed when it did.
#   the SIDE EFFECT  the symlink is either there or it is not.
#
# What it is for: a linked worktree does not get gitignored files. That means no
# .sf/config.json (so every `sf` command silently falls through to the machine's
# GLOBAL default org — the most expensive mistake in this workflow), no
# node_modules, and in stealth mode no CLAUDE.md at all — a worktree agent with no
# contract in context. The hook repairs those the moment a command needs them.
#
# FIXTURE NOTES, each load-bearing:
#
#   aleysian.mode   The master gate: every hook exits 0 at once in a repo with no
#                   `aleysian.mode`. Without it every case here is silent for the
#                   wrong reason and the suite proves nothing. The unmanaged repo
#                   below exists to check the gate still holds.
#   spaces          The real checkout is "64 Org", so worktree paths always contain
#                   one and are always quoted. `cd "<spaced path>" && npm ...` has
#                   to retarget correctly or the hook inspects the wrong tree and
#                   silently does nothing — a failure that looks exactly like
#                   success here, since success is usually silence.
#   pwd -P          macOS $TMPDIR is under /var -> /private/var. in_worktree()
#                   compares a physical git dir against a resolved common dir; an
#                   unresolved root makes the MAIN checkout read as a worktree and
#                   this hook starts symlinking things into the clone itself.
#   unset ALEY_*    org_alias() falls back to $ALEY_ORG_ALIAS / $SOLO_ORG_ALIAS. If
#                   the developer running the suite has either exported, the
#                   "nothing knows the alias" cases would take a different branch
#                   and invoke the real `sf` CLI.
#
# ONE CASE FAILS ON PURPOSE — see "SUSPECTED HOOK BUG" at the bottom of this
# header. Do not fix it by loosening the expectation.
#
# Self-contained: builds its own throwaway repos, touches nothing else.
#
# Run: bash references/hooks/tests/ensure-worktree-config.test.sh
#
# ── SUSPECTED HOOK BUG pinned by the failing case ────────────────────────────
#
#   C1  The `exit 0` at ensure-worktree-config.sh:68 is inside the target-org
#       branch, but it abandons the whole hook. When a worktree has no target-org
#       and no alias can be found, the CLAUDE.md / .forceignore symlinks and the
#       node_modules symlink below it never happen — three independent repairs
#       coupled to an unrelated failure. In stealth mode that leaves the worktree
#       with no CLAUDE.md, which is precisely the outcome the hook's own comment
#       says the stack exists to prevent. `return`-style flow (set a flag, skip
#       only the org section) would fix it; nothing else in the hook depends on
#       that exit.

set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
HOOK="$HERE/../claude-hooks/ensure-worktree-config.sh"
[ -f "$HOOK" ] || { echo "missing hook: $HOOK"; exit 1; }

command -v python3 >/dev/null 2>&1 || { echo "python3 required; skipping"; exit 0; }

unset ALEY_ORG_ALIAS SOLO_ORG_ALIAS

TMP=$(mktemp -d "${TMPDIR:-/tmp}/ensure wt.XXXXXX") || exit 1
TMP=$(cd "$TMP" && pwd -P)

M="$TMP/main repo"     # the managed clone
W="$TMP/wt GH-1"       # its worktree, spaced path on purpose
U="$TMP/plain repo"    # unmanaged repo, no aleysian.* at all
UW="$TMP/plain wt"     # ... and its worktree
OUT="$TMP/hook.out"

cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

mkdir -p "$M" && cd "$M" || exit 1
git init -q -b main .                                     >/dev/null 2>&1
git config user.email t@t.test; git config user.name t
git config aleysian.mode native
git config aleysian.trunk main
echo x > f.txt
git add -A >/dev/null 2>&1 && git commit -qm init >/dev/null 2>&1
mkdir -p node_modules/.bin && echo '{}' > node_modules/marker.json
echo "the contract" > CLAUDE.md
echo '**/jsconfig.json' > .forceignore

git worktree add --detach "$W" HEAD >/dev/null 2>&1 \
  || { echo "could not create temp worktree; skipping"; exit 0; }

mkdir -p "$U" && ( cd "$U" \
  && git init -q -b main . >/dev/null 2>&1 \
  && git config user.email t@t.test && git config user.name t \
  && echo x > f.txt && git add -A >/dev/null 2>&1 && git commit -qm init >/dev/null 2>&1 \
  && mkdir -p node_modules && echo '{}' > node_modules/marker.json \
  && git worktree add --detach "$UW" HEAD >/dev/null 2>&1 )

PASS=0; FAIL=0

ok()   { PASS=$((PASS+1)); echo "  PASS $1"; }
bad()  { FAIL=$((FAIL+1)); echo "  FAIL $1"; }

# Everything this hook might have created. Removed between cases so each one
# starts from a fresh worktree.
reset_wt() { rm -f "$W/node_modules" "$W/CLAUDE.md" "$W/.forceignore"; rm -rf "$W/.sf"; }

# run <expect allow|block> <cwd> <label> <command text>
# Leaves the hook's combined output in $OUT for the assertions below.
run() {
  local want="$1" cwd="$2" label="$3" cmd="$4" got rc
  printf '%s' "$cmd" \
    | python3 -c 'import json,sys; print(json.dumps({"tool_name":"Bash","tool_input":{"command":sys.stdin.read()}}))' \
    | ( cd "$cwd" && bash "$HOOK" ) >"$OUT" 2>&1
  rc=$?
  got=allow; [ $rc -ne 0 ] && got=block
  if [ "$got" = "$want" ]; then ok "[$got] $label"
  else bad "expected=$want got=$got :: $label"; sed -n '1,3p' "$OUT"; fi
}

# Plain ASCII substrings only. grep -E is byte-oriented, so `.` does not match a
# multi-byte character and a pattern spanning an em dash never fires.
outhas()   { grep -qF "$1" "$OUT" && ok "      says: $1" || { bad "      expected output containing: $1"; sed -n '1,3p' "$OUT"; }; }
outquiet() { [ ! -s "$OUT" ] && ok "      silent (changed nothing)" || { bad "      expected silence, got output"; sed -n '1,3p' "$OUT"; }; }
islink()   { [ -L "$2" ] && ok "      linked: $1" || bad "      expected a symlink at: $2"; }
nolink()   { [ ! -e "$2" ] && ok "      untouched: $1" || bad "      expected NO symlink at: $2"; }

echo "== stays out of the way =="
reset_wt
run allow "$M"  "main checkout, npm (it configures itself)" "npm run lint"
outquiet
run allow "$W"  "worktree, a command needing neither"       "git status --short"
outquiet
nolink "node_modules" "$W/node_modules"
# A heredoc body is data. `sf` inside a commit message is not an sf invocation.
run allow "$W"  "worktree, sf inside a heredoc body"        "$(printf 'git commit -F - <<EOF\nsf project deploy start ran fine\nEOF\n')"
outquiet
run allow "$W"  "curl -sf is not the sf CLI"                "curl -sf https://example.test/x"
outquiet

echo "== the master gate: an unmanaged repo's worktree must be untouched =="
run allow "$UW" "unmanaged worktree, npm"                   "npm run lint"
outquiet
nolink "node_modules" "$UW/node_modules"

echo "== node_modules =="
reset_wt
run allow "$W"  "worktree, npm run lint"                    "npm run lint"
outhas "linked node_modules"
islink "node_modules" "$W/node_modules"
run allow "$W"  "again — idempotent, and says nothing"      "npm run lint"
outquiet
reset_wt
# The space is the test: if the quoted `cd` target were truncated at it, the hook
# would inspect the MAIN clone, find it is not a worktree, exit silently, and the
# missing symlink would be the only evidence.
run allow "$M"  "cd \"<spaced worktree>\" && npx jest"        "cd \"$W\" && npx jest --silent"
islink "node_modules" "$W/node_modules"
reset_wt
mv "$M/node_modules" "$TMP/node_modules.stash"
run allow "$W"  "main clone has no node_modules to lend"    "npm run lint"
outquiet
nolink "node_modules" "$W/node_modules"
mv "$TMP/node_modules.stash" "$M/node_modules"

echo "== target-org =="
reset_wt
run allow "$W"  "sf command, nothing knows the alias"       "sf project deploy start --dry-run"
outhas "no target-org"
outhas "GLOBAL default org"
run allow "$W"  "sfdx counts too"                           "npx sfdx force:source:deploy -p force-app"
outhas "no target-org"
if command -v jq >/dev/null 2>&1; then
  reset_wt
  mkdir -p "$W/.sf" && echo '{"target-org":"already-set"}' > "$W/.sf/config.json"
  run allow "$W" "worktree already has a target-org"        "sf project deploy start --dry-run"
  outquiet
fi

echo "== stealth mode materializes the untracked contract =="
reset_wt
git -C "$M" config aleysian.mode stealth
run allow "$W"  "stealth worktree, npm"                     "npm run lint"
outhas "linked CLAUDE.md"
islink "CLAUDE.md"   "$W/CLAUDE.md"
islink ".forceignore" "$W/.forceignore"

echo "== native mode does not: CLAUDE.md is tracked there =="
reset_wt
git -C "$M" config aleysian.mode native
run allow "$W"  "native worktree, npm"                      "npm run lint"
outhas "linked node_modules"
nolink "CLAUDE.md" "$W/CLAUDE.md"

echo "== an unrelated failure must not cancel the other repairs  [C1] =="
# One command needing BOTH, in stealth mode, in a worktree where the org cannot be
# determined. The org note is correct and expected. What must not happen is the
# rest of the hook being skipped: CLAUDE.md and node_modules have nothing to do
# with target-org, and a stealth worktree with no CLAUDE.md is the failure this
# whole stack exists to prevent.
reset_wt
git -C "$M" config aleysian.mode stealth
run allow "$W"  "npm test && sf deploy, no org known"       "npm test && sf project deploy start --dry-run"
outhas "no target-org"
islink "CLAUDE.md"    "$W/CLAUDE.md"
islink "node_modules" "$W/node_modules"
git -C "$M" config aleysian.mode native

echo
echo "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
