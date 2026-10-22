#!/bin/bash
# Regression tests for claude-hooks/guard-sf-deploy.sh — the six checks that keep
# `main === org` true:
#
#   1  `deploy validate`                 -> block (rejects NoTestRun; use --dry-run)
#   2  RunLocalTests / RunAllTestsInOrg  -> block (20+ minute org-wide runs)
#   3  --source-dir force-app            -> block (whole-tree deploy)
#   4  real deploy off trunk / worktree  -> block (orphaned deploy)
#   5  real deploy from a dirty trunk    -> block (org gets code not in git)
#   6  real deploy from an unsynced trunk-> block (org gets code not on the remote)
#
# Both directions are tested. A guard that blocks the sanctioned path costs as
# much trust as one that misses the dangerous one, so every gate has ALLOW cases
# next to its BLOCK cases: --dry-run from a worktree, force-app/main/default,
# RunSpecifiedTests, dirt outside force-app/, report/resume/quick, host=none.
#
# THINGS THIS FILE IS DELIBERATE ABOUT — each one has cost this stack a shipped bug:
#
#   * `git config estate.mode native`. Every hook exits 0 immediately in a repo
#     with no estate.mode (the master gate in _config.sh). Without this line
#     every case below "passes" as allow while testing absolutely nothing.
#
#   * The temp root, the checkout and the worktree all contain a SPACE. Quoted-path
#     truncation is the single most productive bug class in this stack (GH-436,
#     source_tree_root(), command_repo_dir()). The space is the test — do not tidy it.
#
#   * `sf` and `gh` are POISON stubs: they record the call and fail. This hook is
#     pure git + text and must never shell out to a Salesforce CLI. If a future
#     change makes it do so, the last case here goes red and whoever wrote it has
#     to supply a stub that REQUIRES the arguments the hook is supposed to pass —
#     a stub that answers regardless of its arguments once kept twelve cases green
#     against a guard that was doing nothing.
#
#   * Block assertions carry an expected ASCII substring of the hook's own message,
#     so a case cannot pass because some OTHER gate fired. Match plain ASCII only:
#     grep is byte-oriented and `.` does not match the em dash in the hook's output.
#
#   * bash 3.2 / BSD sed compatible: no associative arrays, no `case` inside $(),
#     no sed \b.
#
# Self-contained: builds its own throwaway repo, bare remote and worktree,
# touches nothing else.
#
# Run: bash references/hooks/tests/guard-sf-deploy.test.sh
#
# Cases marked REGRESSION are the ones that first went red here and drove a fix in
# the hook. Each one is verified to FAIL against the pre-fix hook — a case that
# passes both before and after a fix pins nothing.

set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
HOOK="$HERE/../claude-hooks/guard-sf-deploy.sh"
[ -f "$HOOK" ] || { echo "missing hook: $HOOK"; exit 1; }

command -v python3 >/dev/null 2>&1 || { echo "python3 required; skipping"; exit 0; }

# ── throwaway repo, space in the name on purpose ─────────────
# Resolve symlinks in the temp root: on macOS $TMPDIR lives under /var, a symlink
# to /private/var, and in_worktree() compares an unresolved --absolute-git-dir
# against a resolved git_common_dir(). This test must not depend on that either way.
TMP=$(mktemp -d "${TMPDIR:-/tmp}/sf deploy test.XXXXXX") || exit 1
TMP=$(cd "$TMP" && pwd -P)
M="$TMP/main repo"                     # the managed clone
W="$TMP/wt GH-1"                       # a linked worktree; space is load-bearing
UN="$TMP/plain repo"                   # a git repo with NO estate.mode
ORIGIN="$TMP/origin.git"
BIN="$TMP/bin"
CALLS="$TMP/cli-calls"
OUT="$TMP/hook.out"
FA="force-app/main/default/classes"

cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

mkdir -p "$M/$FA" "$BIN" || exit 1
cd "$M" || exit 1
git init -q -b main . >/dev/null 2>&1
git config user.email t@t.test; git config user.name t
git config estate.mode native        # THE MASTER GATE — see the header
git config estate.trunk main
git config estate.host github
echo x > "$FA/A.cls"
echo readme > docs.md
git add -A >/dev/null 2>&1 && git commit -qm init >/dev/null 2>&1

git worktree add --detach "$W" HEAD >/dev/null 2>&1 \
  || { echo "could not create temp worktree; skipping"; exit 0; }
W=$(cd "$W" && pwd)

# An unmanaged repo. A deploy aimed at it must be judged by ITS config (none),
# not by this one's — that is what sfds_retarget() + the deferred gate are for.
mkdir -p "$UN/$FA"
( cd "$UN" && git init -q -b main . && git config user.email t@t.test \
    && git config user.name t && echo y > "$FA/A.cls" && git add -A \
    && git commit -qm init ) >/dev/null 2>&1

# ── poison CLI stubs ─────────────────────────────────────────
for c in sf sfdx gh; do
  cat > "$BIN/$c" <<STUB
#!/bin/bash
echo "$c \$*" >> "$CALLS"
exit 1
STUB
  chmod +x "$BIN/$c"
done
PATH="$BIN:$PATH"; export PATH

PASS=0; FAIL=0

run() { # $1=expect(allow|block)  $2=label  $3=command text  [$4=ASCII substring the output must contain]
  local got rc
  printf '%s' "$3" \
    | python3 -c 'import json,sys; print(json.dumps({"tool_name":"Bash","tool_input":{"command":sys.stdin.read()}}))' \
    | ( cd "${RUN_CWD:-$M}" && bash "$HOOK" ) >"$OUT" 2>&1
  rc=$?
  got=allow; [ $rc -ne 0 ] && got=block
  if [ "$got" != "$1" ]; then
    FAIL=$((FAIL+1))
    printf '  FAIL expected=%s got=%s :: %s\n' "$1" "$got" "$2"
    sed -n '1,4p' "$OUT"
    return 0
  fi
  # -e is required, not decoration: the expected text often BEGINS with "--", which
  # grep would otherwise read as its own option ("--test-level RunLocalTests ...").
  if [ -n "${4:-}" ] && ! grep -F -q -e "$4" "$OUT"; then
    FAIL=$((FAIL+1))
    printf '  FAIL right verdict, WRONG GATE :: %s\n    wanted text: %s\n' "$2" "$4"
    sed -n '1,4p' "$OUT"
    return 0
  fi
  PASS=$((PASS+1)); printf '  PASS [%s] %s\n' "$got" "$2"
}

echo "== the master gate and the hook's scope =="
# A deploy aimed at a repo with no estate.mode: inert, whatever the command says.
run allow "unmanaged repo target, whole-tree deploy" \
    "cd \"$UN\" && sf project deploy start --source-dir force-app"
run allow "not an sf command"            "npm run deploy"
run allow "deploy only in a pipe stage"  "git log --oneline | grep deploy"
run allow "sf, but not a deploy"         "sf apex run --file scripts/x.apex"
# strip_heredocs() is why a commit body may quote the commands these guards hunt.
run allow "banned command inside a heredoc body" \
    "$(printf 'cat <<EOF\nsf project deploy validate --source-dir x\nEOF')"

echo
echo "== 1. deploy validate: must BLOCK, whatever else is on the line =="
run block "plain validate"        "sf project deploy validate --source-dir $FA/A.cls" \
    "'deploy validate' is the production quick-deploy path"
run block "validate + --dry-run"  "sf project deploy validate --dry-run --source-dir $FA/A.cls" \
    "'deploy validate' is the production quick-deploy path"
run allow "start --dry-run is the sanctioned validate" \
    "sf project deploy start --dry-run --source-dir $FA/A.cls --test-level RunSpecifiedTests --tests ATest"

echo
echo "== 2. org-wide test levels: must BLOCK even on a dry run =="
run block "RunLocalTests"              "sf project deploy start --source-dir $FA/A.cls --test-level RunLocalTests" \
    "--test-level RunLocalTests runs every test in the org"
run block "RunAllTestsInOrg"           "sf project deploy start --source-dir $FA/A.cls --test-level RunAllTestsInOrg" \
    "--test-level RunAllTestsInOrg runs every test in the org"
run block "lower case (grep is -i)"    "sf project deploy start --source-dir $FA/A.cls --test-level runlocaltests" \
    "runs every test in the org"
run block "dry run does NOT exempt it" "sf project deploy start --dry-run --source-dir $FA/A.cls --test-level RunLocalTests" \
    "runs every test in the org"
run allow "RunSpecifiedTests"          "sf project deploy start --source-dir $FA/A.cls --test-level RunSpecifiedTests --tests ATest"
run allow "NoTestRun"                  "sf project deploy start --source-dir $FA/A.cls --test-level NoTestRun"

echo
echo "== 3. whole-tree deploys =="
run block "--source-dir force-app"     "sf project deploy start --source-dir force-app" \
    "deploying the entire force-app/ tree"
run block "--source-dir=force-app"     "sf project deploy start --source-dir=force-app" \
    "deploying the entire force-app/ tree"
run block "-d force-app"               "sf project deploy start -d force-app --test-level NoTestRun" \
    "deploying the entire force-app/ tree"
run block "trailing flag after it"     "sf project deploy start --source-dir force-app --wait 33" \
    "deploying the entire force-app/ tree"
run block "a dry run of the whole tree is still the whole tree" \
    "sf project deploy start --source-dir force-app --dry-run" \
    "deploying the entire force-app/ tree"
run allow "force-app/main/default is the documented scratch-org bootstrap" \
    "sf project deploy start --source-dir force-app/main/default --test-level NoTestRun"
run allow "one file"                   "sf project deploy start --source-dir $FA/A.cls"
run allow "a path that merely starts with force-app" \
    "sf project deploy start --source-dir force-app-extras/x.cls"
# REGRESSION (guard-sf-deploy.sh:58). The old token was
#   --source-dir[= ]force-app($|[[:space:]])
# so a trailing slash defeated the anchor and a quote defeated the literal, and
# both of these deployed the whole tree with the guard reporting itself armed.
# Same bug class as GH-436: no quoted alternative in a path pattern.
run block "REGRESSION trailing slash: force-app/" \
    "sf project deploy start --source-dir force-app/" \
    "deploying the entire force-app/ tree"
run block "REGRESSION double-quoted: \"force-app\"" \
    "sf project deploy start --source-dir \"force-app\"" \
    "deploying the entire force-app/ tree"
run block "REGRESSION single-quoted: 'force-app'" \
    "sf project deploy start --source-dir 'force-app'" \
    "deploying the entire force-app/ tree"
run block "REGRESSION quoted AND slashed: \"force-app/\"" \
    "sf project deploy start --source-dir \"force-app/\"" \
    "deploying the entire force-app/ tree"
run block "REGRESSION --source-dir=force-app/" \
    "sf project deploy start --source-dir=force-app/" \
    "deploying the entire force-app/ tree"
run block "REGRESSION -d \"force-app\"" \
    "sf project deploy start -d \"force-app\" --test-level NoTestRun" \
    "deploying the entire force-app/ tree"
# The other half of the same fix: the bootstrap exemption must survive it.
run allow "quoted bootstrap path still allowed" \
    "sf project deploy start --source-dir \"force-app/main/default\" --test-level NoTestRun"
run allow "quoted single file still allowed" \
    "sf project deploy start --source-dir \"$FA/A.cls\""

echo
echo "== 4. real deploys come from the main checkout, on trunk =="
run allow "on trunk, clean, no remote yet" "sf project deploy start --source-dir $FA/A.cls"
run block "from a worktree (cd, quoted spaced path)" \
    "cd \"$W\" && sf project deploy start --source-dir $FA/A.cls" \
    "real deploys run from the main checkout"
run block "from a worktree, --async is still a real deploy" \
    "cd \"$W\" && sf project deploy start --source-dir $FA/A.cls --async" \
    "real deploys run from the main checkout"
run allow "--dry-run from a worktree IS the merge gate" \
    "cd \"$W\" && sf project deploy start --dry-run --source-dir $FA/A.cls --test-level RunSpecifiedTests --tests ATest"
# The hook's own cwd is a worktree and the command names no directory: the
# location check must still fire. Nothing in the command text gives this away.
RUN_CWD="$W" run block "hook standing IN a worktree, no cd in the command" \
    "sf project deploy start --source-dir $FA/A.cls" \
    "real deploys run from the main checkout"
RUN_CWD="$W" run allow "...and --dry-run from there is fine" \
    "sf project deploy start --dry-run --source-dir $FA/A.cls"

git checkout -q -b feature/x
run block "on a feature branch in the main checkout" \
    "sf project deploy start --source-dir $FA/A.cls" \
    "real deploys run from the main checkout"
git checkout -q main
git checkout -q --detach HEAD
run block "detached HEAD in the main checkout" \
    "sf project deploy start --source-dir $FA/A.cls" \
    "real deploys run from the main checkout"
git checkout -q main
git branch -q -D feature/x

echo
echo "== 4b. subcommands that are not a deploy: allowed from anywhere =="
run allow "report"  "cd \"$W\" && sf project deploy report --job-id 0AfXX0000000001AAA"
run allow "resume"  "cd \"$W\" && sf project deploy resume --job-id 0AfXX0000000001AAA"
run allow "cancel"  "cd \"$W\" && sf project deploy cancel --job-id 0AfXX0000000001AAA"
run allow "preview" "cd \"$W\" && sf project deploy preview --source-dir $FA/A.cls"
run allow "quick"   "cd \"$W\" && sf project deploy quick --job-id 0AfXX0000000001AAA"

echo
echo "== 5. trunk must be clean where it matters =="
echo change >> "$M/$FA/A.cls"
run block "modified tracked force-app file" \
    "sf project deploy start --source-dir $FA/A.cls" \
    "has uncommitted force-app/ changes"
run allow "a dry run of a dirty tree is allowed on purpose" \
    "sf project deploy start --dry-run --source-dir $FA/A.cls"
git -C "$M" checkout -- force-app
echo new > "$M/$FA/B.cls"
run block "UNTRACKED file under force-app" \
    "sf project deploy start --source-dir $FA/A.cls" \
    "has uncommitted force-app/ changes"
rm -f "$M/$FA/B.cls"
echo notes >> "$M/docs.md"
run allow "dirt OUTSIDE force-app is none of its business" \
    "sf project deploy start --source-dir $FA/A.cls"
git -C "$M" checkout -- docs.md

echo
echo "== trunk is estate.trunk, NOT the literal string main =="
git branch -q sandbox/steve
git config estate.trunk sandbox/steve
run block "standing on main when trunk is sandbox/steve" \
    "sf project deploy start --source-dir $FA/A.cls" \
    "real deploys run from the main checkout on 'sandbox/steve'"
git checkout -q sandbox/steve
run allow "standing on the configured trunk" "sf project deploy start --source-dir $FA/A.cls"
git checkout -q main
git config estate.trunk main
git branch -q -D sandbox/steve

echo
echo "== 6. trunk must match the remote =="
run allow "no origin at all: nothing to compare (documented fail-open)" \
    "sf project deploy start --source-dir $FA/A.cls"
git init -q --bare "$ORIGIN" >/dev/null 2>&1
git remote add origin "$ORIGIN"
git push -q -u origin main >/dev/null 2>&1
run allow "in sync with origin" "sf project deploy start --source-dir $FA/A.cls"

echo ahead >> "$M/$FA/A.cls"; git commit -qam "unpushed" >/dev/null 2>&1
run block "local trunk AHEAD of origin" \
    "sf project deploy start --source-dir $FA/A.cls" \
    "is AHEAD of origin/main"
git config estate.host none
run allow "host=none: there is no remote to be behind" \
    "sf project deploy start --source-dir $FA/A.cls"
git config estate.host github

git push -q origin main >/dev/null 2>&1              # back in sync
echo remote_only >> "$M/$FA/A.cls"; git commit -qam "merged upstream" >/dev/null 2>&1
git push -q origin main >/dev/null 2>&1
git reset -q --hard HEAD~1                            # local now behind
run block "local trunk BEHIND origin" \
    "sf project deploy start --source-dir $FA/A.cls" \
    "is BEHIND origin/main"
echo diverge >> "$M/$FA/A.cls"; git commit -qam "local divergence" >/dev/null 2>&1
run block "local trunk DIVERGED from origin" \
    "sf project deploy start --source-dir $FA/A.cls" \
    "is AHEAD of origin/main"
git fetch -q origin >/dev/null 2>&1
git reset -q --hard origin/main

echo
echo "== DevOps Center real deploys stay in a clean WI worktree =="
git -C "$W" switch -qc WI-000001
git config estate.delivery devops-center
RUN_CWD="$M" run block "pipeline/main checkout cannot deploy" \
    "sf project deploy start --source-dir $FA/A.cls" "must come from a WI branch"
RUN_CWD="$W" run allow "clean WI worktree can deploy to its local dev org" \
    "sf project deploy start --source-dir $FA/A.cls --test-level NoTestRun"
git config estate.devops.workmodel shared
git config estate.devops.integrationbranch stevenc
git config estate.devops.environment StevenC
RUN_CWD="$W" run block "shared mode routes real deploy through centralized coordinator" \
    "sf project deploy start --source-dir $FA/A.cls --test-level NoTestRun" "local real deploys are disabled"
git config estate.devops.workmodel isolated
echo dirty >> "$W/$FA/A.cls"
RUN_CWD="$W" run block "dirty WI worktree cannot deploy" \
    "sf project deploy start --source-dir $FA/A.cls --test-level NoTestRun" "commit the WI source"
git -C "$W" restore "$FA/A.cls"
unset RUN_CWD
git config estate.delivery direct

echo
echo "== documented gaps: pinned as they behave TODAY, not as they should =="
# `sfdx force:source:deploy` is a real deploy, but checks 4-6 only recognise
# `deploy start` (guard-sf-deploy.sh:73), so the legacy spelling reaches the org
# from a worktree unchecked. Left as allow because sfdx force:* is EOL and the
# whole-tree check (3) still covers its -d flag; raise a ticket before relying on it.
run allow "legacy sfdx force:source:deploy from a worktree bypasses 4-6" \
    "cd \"$W\" && sfdx force:source:deploy -p $FA/A.cls"
run block "...but its whole-tree flag is still caught" \
    "cd \"$W\" && sfdx force:mdapi:deploy -d force-app -w 10" \
    "deploying the entire force-app/ tree"

echo
echo "== this hook must never shell out to a Salesforce CLI =="
if [ -s "$CALLS" ]; then
  FAIL=$((FAIL+1))
  echo "  FAIL the hook invoked a stubbed CLI:"; sed -n '1,5p' "$CALLS"
  echo "  If that is now intended, write a stub that REQUIRES the arguments the"
  echo "  hook is supposed to pass and fails without them."
else
  PASS=$((PASS+1)); echo "  PASS [allow] no sf/sfdx/gh subprocess was spawned"
fi

echo
printf '%d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
