#!/bin/bash
# Regression tests for claude-hooks/record-escape-hatch.sh — the recorder that is
# the ONLY witness to `git commit --no-verify`.
#
# THIS HOOK NEVER BLOCKS. It exits 0 whether it recorded, declined to record, or
# failed to notice anything at all, so the exit code says nothing. Every case below
# asserts the SIDE EFFECT: which kinds landed in .git/estate/hatch-log, and — just
# as important — that nothing landed when nothing was used.
#
# Both directions are real bugs and they are opposite:
#
#   a miss          `--no-verify` disables every git hook, so no git hook can log its
#                   own bypass. If this hook misses it, prettier/ESLint/PMD/Jest and
#                   the issue-ref check were all skipped with no record anywhere.
#
#   a false entry   the hook's own comment is the standard: "a log that cries wolf is
#                   discarded, and false entries in an audit trail are worse than a
#                   thin one". Writing *about* a hatch must not log using one, which
#                   is why the patterns are anchored to a COMMAND POSITION.
#
# The master gate matters here too: every hook exits 0 in a repo with no
# `estate.mode`, so the fixture sets it and one case unsets it again. Without that
# a suite is green against a hook that never ran. A second, unconfigured repo checks
# the other half — a hatch aimed at a repo we do not manage is not ours to record.
#
# Self-contained: builds its own throwaway repos, touches nothing else. Their paths
# contain SPACES on purpose (worktrees here routinely do), so any token pattern that
# truncates at the first space shows up as a missed retarget.
#
# Run: bash references/hooks/tests/record-escape-hatch.test.sh

set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
HOOK="$HERE/../claude-hooks/record-escape-hatch.sh"
[ -f "$HOOK" ] || { echo "missing hook: $HOOK"; exit 1; }

command -v python3 >/dev/null 2>&1 || { echo "python3 required; skipping"; exit 0; }

TMP=$(mktemp -d "${TMPDIR:-/tmp}/record hatch.XXXXXX") || exit 1
TMP=$(cd "$TMP" && pwd -P)
R="$TMP/managed repo"
PLAIN="$TMP/plain repo"
OUT="$TMP/hook.out"

cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

for D in "$R" "$PLAIN"; do
  mkdir -p "$D" && ( cd "$D" && git init -q -b main . >/dev/null 2>&1 \
    && git config user.email t@t.test && git config user.name t \
    && echo x > a.txt && git add -A >/dev/null 2>&1 \
    && git commit -qm "init refs #7" >/dev/null 2>&1 )
done
# Only one of the two is managed. The other has no estate.* config at all, which
# is the state of every repo on the machine that has not been through init.
( cd "$R" && git config estate.mode native && git config estate.trunk main \
  && git config estate.ticket.system github )

HLOG="$R/.git/estate/hatch-log"
PLAIN_HLOG="$PLAIN/.git/estate/hatch-log"
SHORT=$(git -C "$R" rev-parse --short HEAD)

PASS=0; FAIL=0
check() { # <label> <expected> <actual>
  if [ "$2" = "$3" ]; then PASS=$((PASS+1)); echo "  PASS $2 :: $1"
  else FAIL=$((FAIL+1)); echo "  FAIL $1"; echo "       expected [$2]"; echo "       got      [$3]"; fi
}

# The kinds recorded, in order. Field 2 of "<utc stamp> <KIND> <short sha> <detail...>".
hatch() { [ -f "$HLOG" ] || { printf 'NONE'; return; }
          awk 'NF{printf "%s;", $2}' "$HLOG"; }

reset() { rm -f "$HLOG" "$PLAIN_HLOG"; }

RC=0
fire() { # <command text>   (PreToolUse Bash payload)
  ( cd "$R" && python3 -c 'import json,sys
print(json.dumps({"tool_name":"Bash","tool_input":{"command":sys.argv[1]}}))' "$1" \
    | bash "$HOOK" ) >"$OUT" 2>&1
  RC=$?
}
fire_edit() { # <file path>  (a non-Bash tool call carries no command at all)
  ( cd "$R" && python3 -c 'import json,sys
print(json.dumps({"tool_name":"Edit","tool_input":{"file_path":sys.argv[1],
                                                   "old_string":"a","new_string":"b"}}))' "$1" \
    | bash "$HOOK" ) >"$OUT" 2>&1
  RC=$?
}

# one <label> <expected kinds> <command> — the common shape: fire from a clean log.
one() { reset; fire "$3"; check "$1" "$2" "$(hatch)"; }

echo "== the master gate: no estate.mode means no recording at all =="
reset
git -C "$R" config --unset estate.mode
fire 'git commit --no-verify -m "x"'
check "unconfigured repo records nothing" "NONE" "$(hatch)"
git -C "$R" config estate.mode native
fire 'git commit --no-verify -m "x"'
check "the same command records once mode is set" "NO_VERIFY;" "$(hatch)"
check "and it never blocks" "0" "$RC"

echo
echo "== git commit --no-verify, wherever the flag sits =="
one "flag before -m"            "NO_VERIFY;" 'git commit --no-verify -m "wip refs #7"'
one "flag after -m"             "NO_VERIFY;" 'git commit -m "wip refs #7" --no-verify'
one "short -n before -m"        "NO_VERIFY;" 'git commit -n -m "wip refs #7"'
one "short -n after -m"         "NO_VERIFY;" 'git commit -m "wip refs #7" -n'
one "after a && separator"      "NO_VERIFY;" 'git add -A && git commit --no-verify -m "wip"'
one "after a ; separator"       "NO_VERIFY;" 'git add -A ; git commit --no-verify -m "wip"'
one "behind an env assignment"  "NO_VERIFY;" 'GIT_EDITOR=true git commit --no-verify -m "wip"'
one "with a global -c option"   "NO_VERIFY;" 'git -c core.hooksPath=/dev/null commit --no-verify -m "wip"'
one "git -C into the managed repo" "NO_VERIFY;" "git -C \"$R\" commit --no-verify -m \"wip\""

echo
echo "== what is NOT a hatch =="
one "an ordinary commit"        "NONE" 'git commit -m "wip refs #7"'
one "an amend with no flag"     "NONE" 'git commit --amend --no-edit'
one "git push --no-verify"      "NONE" 'git push --no-verify origin main'
one "a commit message ending n" "NONE" 'git commit -m "rename to n"'
one "nothing to do with git"    "NONE" 'npm test -- --no-verify-coverage'

echo
echo "== prose is not a command: writing ABOUT a hatch must not log one =="
# This is the bug the CMDPOS anchor exists for. A doc that explains the rule, or a
# note-to-self about it, used to log a bypass that never happened.
one "echo into a notes file"    "NONE" 'echo "never use git commit --no-verify" >> notes.md'
one "printf into a doc"         "NONE" 'printf "%s\n" "git commit --no-verify is banned" > RULES.md'
one "inside a heredoc body"     "NONE" 'cat <<EOT >> doc.md
git commit --no-verify skips every git hook
EOT'
one "an env hatch named in prose" "NONE" 'echo "set ALEY_SKIP_DOD=1 to silence the Stop check" >> doc.md'
one "grepping for the flag"      "NONE" 'grep -rn -- "--no-verify" docs/'

# KNOWN OVER-RECORD, asserted as current behaviour rather than as correct. A commit
# whose MESSAGE quotes the flag records a hatch that was not used, because the scan
# is not quote-aware — the same class the echo cases above close. Low severity (the
# heredoc form, which is how long messages are written here, is already stripped) and
# a fix would have to distinguish an argument from a flag in shell text. If that ever
# happens, flip this expectation to NONE.
one "a commit MESSAGE quoting the flag (known over-record)" "NO_VERIFY;" \
    'git commit -m "docs: explain why --no-verify is banned"'

echo
echo "== inline env hatches, all three accepted prefixes =="
one "ALEY_ALLOW_UNVALIDATED_MERGE"  "ALLOW_UNVALIDATED_MERGE_INLINE;" \
    'ALEY_ALLOW_UNVALIDATED_MERGE=1 gh pr merge 5 --squash --delete-branch'
one "SW_ALLOW_UNVALIDATED_MERGE"    "ALLOW_UNVALIDATED_MERGE_INLINE;" \
    'SW_ALLOW_UNVALIDATED_MERGE=1 gh pr merge 5 --squash'
one "SOLO_ALLOW_UNVALIDATED_MERGE"  "ALLOW_UNVALIDATED_MERGE_INLINE;" \
    'SOLO_ALLOW_UNVALIDATED_MERGE=1 gh pr merge 5 --squash'
one "ALEY_SKIP_DOD"                 "SKIP_DOD_INLINE;" 'ALEY_SKIP_DOD=1 gh pr merge 5 --squash'
one "SOLO_SKIP_DOD"                 "SKIP_DOD_INLINE;" 'SOLO_SKIP_DOD=1 echo done'
one "=0 is not a hatch"             "NONE" 'ALEY_SKIP_DOD=0 gh pr merge 5 --squash'
one "a lookalike variable"          "NONE" 'ALEY_SKIP_DODGY=1 gh pr merge 5 --squash'

echo "== every hatch in one command is recorded, not just the first =="
one "three at once" "NO_VERIFY;ALLOW_UNVALIDATED_MERGE_INLINE;SKIP_DOD_INLINE;" \
    'ALEY_SKIP_DOD=1 ALEY_ALLOW_UNVALIDATED_MERGE=1 git commit --no-verify -m "wip"'

echo
echo "== the log is an audit trail: every use, with its evidence =="
reset
fire 'git commit --no-verify -m "first"'
fire 'git commit --no-verify -m "second"'
check "two uses are two entries, not one" "NO_VERIFY;NO_VERIFY;" "$(hatch)"
check "each entry carries the commit it was used at" "$SHORT" \
      "$(awk 'NR==1{print $3}' "$HLOG")"
if grep -q -- 'git commit --no-verify -m "second"' "$HLOG"; then
  PASS=$((PASS+1)); echo "  PASS the command itself is recorded as the detail"
else
  FAIL=$((FAIL+1)); echo "  FAIL the command was not recorded as the detail"; cat "$HLOG"
fi
# Plain ASCII substring: the note carries em dashes, which grep -E's '.' cannot match.
if grep -q 'ESCAPE HATCH USED' "$OUT"; then
  PASS=$((PASS+1)); echo "  PASS the use is surfaced to the agent as well as logged"
else
  FAIL=$((FAIL+1)); echo "  FAIL the use was logged silently"; sed -n '1,3p' "$OUT"
fi

echo
echo "== a hatch aimed at a repo we do not manage is not ours to record =="
reset
fire "git -C \"$PLAIN\" commit --no-verify -m \"wip\""
check "nothing in the managed repo's log" "NONE" "$(hatch)"
if [ -f "$PLAIN_HLOG" ]; then
  FAIL=$((FAIL+1)); echo "  FAIL wrote a hatch-log into an unmanaged repo"
else
  PASS=$((PASS+1)); echo "  PASS no hatch-log created in the unmanaged repo"
fi

echo
echo "== a tool call with no command at all =="
reset
fire_edit "$R/a.txt"
check "an Edit is not a hatch" "NONE" "$(hatch)"
check "and it never blocks" "0" "$RC"

echo
printf '%d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
