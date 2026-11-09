#!/bin/bash
# Regression tests for claude-hooks/guard-sf-flags.sh — sf CLI flag hygiene on ANY
# sf/sfdx subcommand:
#
#   --target-org / -o / --targetusername  -> block (the org is configured project-locally)
#   --use-most-recent                     -> block (resolves to another agent's job)
#   project retrieve / force:*:retrieve   -> block, WITH the scratch-dir carve-out:
#         retrieve preview                            allowed (reads nothing, writes nothing)
#         --output-dir <outside every working tree>    allowed
#         --output-dir tmp-retrieve (inside a tree)    allowed, with a note
#         --output-dir anything under force-app        never, whatever the flag says
#         a plain retrieve run from a LINKED worktree   allowed (its own branch's files;
#                                                       the PR diff catches it) — but an
#                                                       explicit --output-dir force-app
#                                                       still blocks, even from a worktree
#         ESTATE_/SOLO_ALLOW_RETRIEVE=1              allowed, recorded to the hatch-log
#
# Both directions are tested. This hook's cheapest failure mode is a FALSE BLOCK:
# it inspects a text segment cut out of the command line, and every `-o` in the
# universe lives in that same text. `grep -o`, `sort -o`, `curl -o` after a pipe
# are therefore first-class cases here, not afterthoughts.
#
# THINGS THIS FILE IS DELIBERATE ABOUT — each one has cost this stack a shipped bug:
#
#   * `git config estate.mode native`. Every hook exits 0 immediately in a repo
#     with no estate.mode (the master gate in _config.sh). Without this line
#     every case below "passes" as allow while testing absolutely nothing.
#
#   * The temp root and the checkout contain a SPACE, and that is exactly what the
#     retrieve carve-out gets wrong (see KNOWN DEFECTS). One CONTROL repo is
#     created with no space in its path, so the evidence separates "the guard is
#     wrong" from "the path is wrong" — that is the only reason it exists.
#
#   * `sf` and `sfdx` are POISON stubs: they record the call and fail. This hook is
#     pure text + git and must never shell out to a Salesforce CLI. If a future
#     change makes it do so, the last case here goes red and whoever wrote it has
#     to supply a stub that REQUIRES the arguments the hook is supposed to pass —
#     a stub that answers regardless of its arguments once kept twelve cases green
#     against a guard that was doing nothing.
#
#   * Block assertions carry an expected ASCII substring of the hook's own message,
#     so a -o case cannot pass on a retrieve block or vice versa. Match plain ASCII
#     only: grep is byte-oriented and `.` does not match the em dash the hook prints.
#
#   * bash 3.2 / BSD sed compatible: no associative arrays, no `case` inside $(),
#     no sed \b.
#
# Self-contained: builds its own throwaway repos and worktree, touches nothing else.
#
# Run: bash references/hooks/tests/guard-sf-flags.test.sh
#
# Cases marked REGRESSION are the ones that first went red here and drove a fix in
# the hook — the chained-sf bypass, the multi-line false block, and the quoted
# --output-dir truncation. Each is verified to FAIL against the pre-fix hook; a
# case that passes both before and after a fix pins nothing.

set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
HOOK="$HERE/../claude-hooks/guard-sf-flags.sh"
[ -f "$HOOK" ] || { echo "missing hook: $HOOK"; exit 1; }

command -v python3 >/dev/null 2>&1 || { echo "python3 required; skipping"; exit 0; }

# ── throwaway repos, space in the name on purpose ────────────
TMP=$(mktemp -d "${TMPDIR:-/tmp}/sf flags test.XXXXXX") || exit 1
TMP=$(cd "$TMP" && pwd -P)
# The control repo, and ONLY the control repo, has no space in its path.
CTL=$(mktemp -d "${TMPDIR:-/tmp}/sf-flags-control.XXXXXX") || exit 1
CTL=$(cd "$CTL" && pwd -P)

M="$TMP/main repo"                     # the managed clone
W="$TMP/wt GH-1"                       # a linked worktree; space is load-bearing
UN="$TMP/plain repo"                   # a git repo with NO estate.mode
C="$CTL/repo"                          # same as M, but no space in the path
BIN="$TMP/bin"
CALLS="$TMP/cli-calls"
OUT="$TMP/hook.out"
OUTSIDE="/tmp/sf-flags-outside-$$"     # outside every working tree, and unspaced
HATCHLOG="$M/.git/estate/hatch-log"

cleanup() { rm -rf "$TMP" "$CTL"; }
trap cleanup EXIT

seed_repo() { # $1=path — a managed clone with a force-app/ tree
  mkdir -p "$1/force-app/main/default/classes" || return 1
  ( cd "$1" \
    && git init -q -b main . \
    && git config user.email t@t.test \
    && git config user.name t \
    && git config estate.mode native \
    && git config estate.trunk main \
    && git config estate.host github \
    && echo x > force-app/main/default/classes/A.cls \
    && git add -A && git commit -qm init ) >/dev/null 2>&1
}

seed_repo "$M" || exit 1
seed_repo "$C" || exit 1
mkdir -p "$BIN"
cd "$M" || exit 1

git worktree add --detach "$W" HEAD >/dev/null 2>&1 \
  || { echo "could not create temp worktree; skipping"; exit 0; }
W=$(cd "$W" && pwd)

# An unmanaged repo. A command aimed at it must be judged by ITS config (none),
# not by this one's — that is what sfds_retarget() + the deferred gate are for.
mkdir -p "$UN"
( cd "$UN" && git init -q -b main . && git config user.email t@t.test \
    && git config user.name t && echo y > f.txt && git add -A \
    && git commit -qm init ) >/dev/null 2>&1

# ── poison CLI stubs ─────────────────────────────────────────
for c in sf sfdx; do
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
  # grep would otherwise read as its own option.
  if [ -n "${4:-}" ] && ! grep -F -q -e "$4" "$OUT"; then
    FAIL=$((FAIL+1))
    printf '  FAIL right verdict, WRONG GATE :: %s\n    wanted text: %s\n' "$2" "$4"
    sed -n '1,4p' "$OUT"
    return 0
  fi
  PASS=$((PASS+1)); printf '  PASS [%s] %s\n' "$got" "$2"
}

ORG_MSG="BLOCKED: --target-org / -o on an sf command."
UMR_MSG="BLOCKED: --use-most-recent."
RET_MSG="BLOCKED: retrieving from the org."

echo "== the master gate and the hook's scope =="
run allow "unmanaged repo target, --target-org" \
    "cd \"$UN\" && sf project deploy start --target-org someorg"
run allow "unmanaged repo target, retrieve" \
    "cd \"$UN\" && sf project retrieve start --metadata ApexClass:Foo"
run allow "no sf anywhere, -o in a pipe stage"  "git log --oneline | grep -o deploy"
run allow "curl -o, no sf on the line"          "curl -o /tmp/x.json https://example.test/x"
run allow "sort -o, no sf on the line"          "sort -o /tmp/out.txt /tmp/in.txt"
run allow "a command that merely ENDS in sf"    "mysf deploy --target-org someorg"
run allow "retrieve inside a heredoc body is data, not a command" \
    "$(printf 'git commit -F - <<EOF\nrefs #7 do not run sf project retrieve start\nEOF')"
# Pinned as it behaves today: the entry pattern accepts a quote before `sf` on
# purpose, so `bash -c "sf ..."` is still seen — and an echoed mention is caught
# with it. Failing closed on a quoted string is the cheap direction of that trade.
run block "an sf command quoted inside echo is still matched" \
    "echo \"sf project deploy start --target-org someorg\"" "$ORG_MSG"

echo
echo "== --target-org / -o / --targetusername: must BLOCK =="
run block "--target-org <alias>"    "sf project deploy start --target-org someorg" "$ORG_MSG"
run block "--target-org=<alias>"    "sf project deploy start --target-org=someorg" "$ORG_MSG"
run block "-o <alias>"              "sf project deploy start -o someorg"           "$ORG_MSG"
run block "-o=<alias>"              "sf project deploy start -o=someorg"           "$ORG_MSG"
run block "--targetusername"        "sfdx force:source:deploy --targetusername someorg -p x" "$ORG_MSG"
run block "on a report, not a deploy" "sf project deploy report --job-id 0AfXX0000000001AAA -o someorg" "$ORG_MSG"

echo
echo "== ...and must ALLOW the sanctioned shapes and every downstream -o =="
run allow "no org flag at all"       "sf project deploy start --source-dir force-app/main/default/classes/A.cls"
run allow "grep -o after a pipe"     "sf project deploy start --source-dir A.cls | grep -o Succeeded"
run allow "sort -o after a pipe"     "sf apex run --file scripts/x.apex | sort -o /tmp/out.txt"
run allow "-o after a semicolon"     "sf project deploy report --job-id 0Af1 ; ls -o force-app"
run allow "no bare -o inside a longer flag" "sf sobject describe --sobject Account"
run allow "a config set is how the org is named" "sf config set target-org=myscratch"

echo
echo "== --use-most-recent =="
run block "on a deploy report"  "sf project deploy report --use-most-recent"       "$UMR_MSG"
run block "on a deploy resume"  "sf project deploy resume --use-most-recent"       "$UMR_MSG"
run allow "an explicit job id is the alternative the hook asks for" \
    "sf project deploy report --job-id \"\$JOB_ID\""
run allow "the words appear only downstream of a pipe" \
    "sf project deploy report --job-id 0Af1 | grep -c use-most-recent"

echo
echo "== retrieve: must BLOCK =="
run block "bare retrieve start"        "sf project retrieve start"                        "$RET_MSG"
run block "retrieve guidance starts from the user's reported components" \
    "sf project retrieve start" "Start with the component names the user supplied"
run block "retrieve guidance handles SourceMember deletions" \
    "sf project retrieve start" "IsNameObsolete=true"
run block "retrieve start --metadata"  "sf project retrieve start --metadata ApexClass:Foo" "$RET_MSG"
run block "legacy force:source:retrieve" "sfdx force:source:retrieve -p force-app/main/default" "$RET_MSG"
run block "legacy force:mdapi:retrieve"  "sfdx force:mdapi:retrieve -k package.xml -r force-app" "$RET_MSG"
run block "--output-dir force-app"       "sf project retrieve start --output-dir force-app"  "$RET_MSG"
run block "--output-dir force-app/main/default" \
    "sf project retrieve start --output-dir force-app/main/default"                          "$RET_MSG"
run block "--output-dir ../../force-app (judged by target, not spelling)" \
    "sf project retrieve start --output-dir ../../force-app"                                 "$RET_MSG"
run block "--output-dir <dir inside the tree that is not tmp-retrieve>" \
    "sf project retrieve start --output-dir scratch"                                         "$RET_MSG"
# Fails CLOSED, which is the right direction: the carve-out's token pattern only
# accepts `--output-dir <space> path`, so the `=` spelling reads as no output dir
# at all. Pinned so a future rewrite does not silently invert it.
run block "--output-dir=tmp-retrieve is not parsed, so it blocks" \
    "sf project retrieve start --output-dir=tmp-retrieve"                                    "$RET_MSG"

echo
echo "== retrieve: the carve-outs must ALLOW =="
run allow "retrieve preview reads and writes nothing" "sf project retrieve preview"
run allow "retrieve preview with flags"               "sf project retrieve preview --ignore-conflicts"
run allow "--output-dir tmp-retrieve"                 "sf project retrieve start --output-dir tmp-retrieve --metadata ApexClass:Foo"
run allow "--output-dir \"tmp-retrieve\" quoted"      "sf project retrieve start --output-dir \"tmp-retrieve\""
run allow "-r tmp-retrieve (short flag)"              "sfdx force:mdapi:retrieve -k package.xml -r tmp-retrieve"
run allow "an unspaced path outside every working tree" \
    "sf project retrieve start --output-dir $OUTSIDE"
RUN_CWD="$W" run allow "tmp-retrieve resolved against a WORKTREE, not the clone" \
    "sf project retrieve start --output-dir tmp-retrieve"

echo
echo "== retrieve: the worktree carve-out =="
# The block protects the MAIN checkout, where a retrieve into force-app/ silently
# reverts deployed-but-unretrieved work with no diff read. A LINKED worktree is not
# that checkout: a plain retrieve there lands in the worktree's own force-app/ — the
# agent's throwaway branch files, caught by the PR diff before merge — so it is
# allowed. The same command still BLOCKS in the primary checkout (every block case
# above runs in $M). And an EXPLICIT --output-dir is judged by the scratch-dir rules
# regardless of cwd, so a force-app target blocks even from a worktree — the carve-out
# is for the plain, cwd-relative form only.
RUN_CWD="$W" run allow "plain retrieve from a linked worktree is the agent's own files" \
    "sf project retrieve start --metadata ApexClass:Foo"
RUN_CWD="$W" run allow "bare retrieve start from a linked worktree" \
    "sf project retrieve start"
RUN_CWD="$W" run block "explicit --output-dir force-app FROM a worktree still blocks" \
    "sf project retrieve start --output-dir force-app"                                  "$RET_MSG"

echo
echo "== retrieve: the escape hatch is allowed AND recorded =="
rm -f "$HATCHLOG"
ESTATE_ALLOW_RETRIEVE=1 run allow "ESTATE_ALLOW_RETRIEVE=1"  "sf project retrieve start --metadata ApexClass:Foo"
SOLO_ALLOW_RETRIEVE=1   run allow "SOLO_ALLOW_RETRIEVE=1"    "sf project retrieve start --metadata ApexClass:Foo"
SOLO_ALLOW_RETRIEVE=1 run allow "SOLO_ALLOW_RETRIEVE=1"  "sf project retrieve start --metadata ApexClass:Foo"
# A hatch that allows without recording is a silent override — the whole point of
# the log. Three uses, three lines.
if [ "$(grep -c ALLOW_RETRIEVE "$HATCHLOG" 2>/dev/null || echo 0)" -eq 3 ]; then
  PASS=$((PASS+1)); echo "  PASS [allow] all three hatch uses landed in the hatch-log"
else
  FAIL=$((FAIL+1))
  echo "  FAIL hatch-log did not record 3 ALLOW_RETRIEVE lines: $HATCHLOG"
  sed -n '1,5p' "$HATCHLOG" 2>/dev/null
fi
# The hook reads its OWN environment. A PreToolUse hook does not inherit an
# assignment written inside the command it is inspecting, so this must still block.
run block "the hatch as a command-line prefix is NOT the hatch" \
    "ESTATE_ALLOW_RETRIEVE=1 sf project retrieve start --metadata ApexClass:Foo" "$RET_MSG"

echo
echo "== CONTROL: with no space in the repo path, an absolute force-app target blocks =="
# The reference point for the quoted-path regression cases below: same command,
# same guard, only the path differs. These two passed even before the fix — which
# is exactly why they cannot be the only evidence.
RUN_CWD="$C" run block "quoted absolute .../force-app, unspaced repo" \
    "sf project retrieve start --output-dir \"$C/force-app\" --metadata ApexClass:Foo" "$RET_MSG"
RUN_CWD="$C" run block "unquoted absolute .../force-app, unspaced repo" \
    "sf project retrieve start --output-dir $C/force-app --metadata ApexClass:Foo"     "$RET_MSG"

echo
echo "== REGRESSION: a quoted path must not truncate at its first space =="
# The token pattern was [^[:space:]|&;]+ with no quoted alternative, so a quoted
# path was cut at its first space: "/…/sf flags test.X/main repo/force-app" read as
# "/…/sf", which is under no force-app and under no working tree, so the hook took
# its "outside every tree" exit and ALLOWED a retrieve straight over force-app/.
# Every worktree of a checkout named "64 Org" has a space in its path. Same bug
# class as GH-436; the CONTROL cases above are what prove the space is the trigger.
run block "REGRESSION double-quoted absolute .../force-app, SPACED repo" \
    "sf project retrieve start --output-dir \"$M/force-app\" --metadata ApexClass:Foo" "$RET_MSG"
run block "REGRESSION single-quoted absolute .../force-app, SPACED repo" \
    "sf project retrieve start --output-dir '$M/force-app' --metadata ApexClass:Foo"   "$RET_MSG"
run block "REGRESSION quoted path INTO a spaced worktree's force-app" \
    "sf project retrieve start --output-dir \"$W/force-app/main/default\""             "$RET_MSG"
# The other half of the same fix: a quoted SAFE target must still be read as safe,
# not blocked because the quotes confused the parse.
run allow "quoted absolute tmp-retrieve in a spaced repo is still allowed" \
    "sf project retrieve start --output-dir \"$M/tmp-retrieve\" --metadata ApexClass:Foo"

echo
echo "== REGRESSION: EVERY sf invocation in the command is judged, not just the last =="
# SF_SEGMENT used to keep only the LAST `sf ` occurrence (a greedy `.*`), so in a
# chain the FIRST command's flags were never inspected — a straight bypass of the
# wrong-org gate. This is the highest-value case in either suite.
run block "REGRESSION --target-org on the FIRST of two chained sf commands" \
    "sf project deploy start --target-org wrongorg && sf project deploy report --job-id 0Af1" "$ORG_MSG"
run block "REGRESSION -o on the FIRST of two chained sf commands" \
    "sf project deploy start -o wrongorg && sf project deploy report --job-id 0Af1"           "$ORG_MSG"
run block "-o on the SECOND of two chained sf commands" \
    "sf project deploy start --source-dir A.cls && sf project deploy report -o wrongorg"      "$ORG_MSG"
# These two are NOT regressions — the old greedy rule happened to inspect the last
# command, which was the dangerous one. They pin the new loop's semantics instead:
# an allow verdict on one segment is a `continue`, never an `exit 0`, or a harmless
# first sf command becomes a way to smuggle the second one past the gate.
run block "a retrieve hidden behind a harmless first sf command" \
    "sf project retrieve preview && sf project retrieve start --metadata ApexClass:Foo"       "$RET_MSG"
run block "a second retrieve with a different, unsafe --output-dir" \
    "sf project retrieve start --output-dir tmp-retrieve && sf project retrieve start --output-dir force-app" \
    "$RET_MSG"
run block "semicolon chains too"  "sf project deploy start --source-dir A.cls ; sf apex run -o wrongorg" "$ORG_MSG"
run allow "two clean sf commands in a chain stay clean" \
    "sf project deploy start --source-dir A.cls && sf project deploy report --job-id 0Af1"
# A prefix must not conceal the invocation: grep -oE takes the LEFTMOST sf, so an
# env assignment or an `env -i` in front of it changes nothing.
run block "an env-assignment prefix does not hide the flag" \
    "SF_USE_PROGRESS_BAR=false sf project deploy start -o wrongorg" "$ORG_MSG"
run block "an env -i prefix does not hide the flag" \
    "env -i sf project deploy start --target-org wrongorg"          "$ORG_MSG"
# The quote before `sf` is deliberate and must survive the rewrite: a wrapped
# invocation is still an invocation.
run block "bash -c \"sf ... -o\" stays visible" \
    "bash -c \"sf project deploy start -o wrongorg\"" "$ORG_MSG"

echo
echo "== REGRESSION: a foreign -o on another LINE is not an sf flag =="
# sed is line-oriented, so lines without `sf ` used to survive verbatim inside
# SF_SEGMENT and their flags were attributed to sf. A multi-line Bash call — the
# normal shape of one — was refused with a message naming a flag nobody passed.
run allow "REGRESSION multi-line: find -o on a later line" \
    "$(printf 'sf project deploy start --source-dir force-app/main/default/classes/A.cls\nfind force-app -name "*.cls" -o -name "*.xml"\n')"
run allow "REGRESSION multi-line: curl -o on a later line" \
    "$(printf 'sf project deploy start --source-dir A.cls\ncurl -o /tmp/x.json https://example.test/x\n')"
run allow "REGRESSION multi-line: ls -o on an EARLIER line" \
    "$(printf 'ls -o force-app\nsf project deploy start --source-dir A.cls\n')"
run allow "backslash continuation is one command, no false flag" \
    "$(printf 'sf project deploy start --source-dir A.cls \\\\\n  --test-level RunSpecifiedTests --tests ATest\n')"
# ...and the real thing on a multi-line command must still be caught.
run block "multi-line: a real -o on the sf line still blocks" \
    "$(printf 'sf project deploy start -o wrongorg\nfind force-app -name "*.cls" -o -name "*.xml"\n')" "$ORG_MSG"
run block "multi-line: a retrieve on the second line still blocks" \
    "$(printf 'git status --porcelain\nsf project retrieve start --metadata ApexClass:Foo\n')"          "$RET_MSG"

echo
echo "== the cost of splitting on | ; & : documented, unchanged from the old code =="
# The split is quote-aware, so a separator INSIDE a quoted argument no longer cuts
# the command: this one is caught, where a naive split would have dropped the -o.
run block "an & inside a quoted argument does not hide what follows it" \
    "sf project deploy start --tests \"A & B\" -o wrongorg" "$ORG_MSG"
run allow "a quoted & in a non-sf command is still not our business" \
    "git commit -m \"Foo & Bar\" && git push"
run block "escaped quotes with no separator after them change nothing" \
    "sf project deploy start --tests \"A \\\"B\\\"\" -o wrongorg" "$ORG_MSG"
# The one residual limit, pinned as it behaves: a BACKSLASH-ESCAPED quote flips the
# scanner's quote state, so a separator AFTER it reads as a real separator and the
# tail of that command is not inspected. Closing it needs a shell grammar rather
# than a scanner. The pre-fix code lost the tail of EVERY command containing a
# quoted separator, so this is strictly narrower than what it replaced — and it
# fails open, which is why it is written down here rather than left to be found.
run allow "LIMIT: escaped quote followed by an & loses the tail (as it always did)" \
    "sf project deploy start --tests \"A \\\" B & C\" -o wrongorg"

echo
echo "== documented gap: pinned as it behaves TODAY, not as it should =="
# -u is the legacy short form of --targetusername, which the hook blocks by long
# name only (guard-sf-flags.sh:42). Left as allow because sfdx force:* is EOL;
# raise a ticket before relying on this gate for legacy commands.
run allow "sfdx -u <alias> is not covered" "sfdx force:source:deploy -u someorg -p force-app/main/default"

echo
echo "== DevOps Center uses an explicit control org and JSON =="
git config estate.delivery devops-center
git config estate.devops.orgalias control64
run block "missing DevOps control org" \
    "sf devops work-item list --project-id 0DB --json" "must explicitly target 'control64'"
run block "wrong DevOps control org" \
    "sf devops work-item list --project-id 0DB --target-org wrong --json" "must explicitly target 'control64'"
run block "missing structured output" \
    "sf devops work-item list --project-id 0DB --target-org control64" "require --json"
run allow "configured DevOps control org" \
    "sf devops work-item list --project-id 0DB --target-org control64 --json"
git config estate.delivery direct

echo
echo "== this hook must never shell out to a Salesforce CLI =="
if [ -s "$CALLS" ]; then
  FAIL=$((FAIL+1))
  echo "  FAIL the hook invoked a stubbed CLI:"; sed -n '1,5p' "$CALLS"
  echo "  If that is now intended, write a stub that REQUIRES the arguments the"
  echo "  hook is supposed to pass and fails without them."
else
  PASS=$((PASS+1)); echo "  PASS [allow] no sf/sfdx subprocess was spawned"
fi

echo
printf '%d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
