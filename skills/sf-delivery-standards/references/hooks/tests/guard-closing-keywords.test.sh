#!/bin/bash
# Regression tests for claude-hooks/guard-closing-keywords.sh — "refs, never
# fixes".
#
# WHAT THE HOOK IS FOR
# --------------------
# `fixes #42` in a commit message or PR body closes issue #42 the moment the PR
# merges, which is BEFORE the deploy — and this loop never closes a ticket on merge
# (tickets stay open; closure is production/engine scope). In a client's repo it
# closes THEIR #42.
#
# WHAT IS ACTUALLY BEING PINNED
# -----------------------------
#   the shape filter    only commands that can carry a keyword TO GitHub are this
#                       hook's business. Prose, echo, file writes and `git log
#                       --grep` must pass, or a doc explaining the rule cannot be
#                       written. Under-matching is the dangerous direction and is
#                       tested through every carrier: git commit, gh pr
#                       create/edit/merge, gh issue create/edit, env-var prefixes,
#                       pipelines, `git -C <path with a space>`.
#   which rule fired    rule 1 (closing keyword) and rule 2 (a bare #N under a
#                       non-GitHub tracker) both exit 2, so the exit code alone
#                       cannot tell them apart. Every ambiguous case asserts the
#                       REASON text too — a block with the wrong explanation sends
#                       the agent to fix the wrong thing.
#   the heredoc seam    strip_heredocs() removes heredoc BODIES before any pattern
#                       scan, which is right for guards that read commands and
#                       wrong for a guard whose subject IS the text. Both halves
#                       are pinned: the `git commit -F -` case has a backstop in
#                       the commit-msg git hook, the `gh pr create --body-file -`
#                       case has none and is a live bypass.
#   no escape hatch     there deliberately is not one, so there is nothing to test
#                       except that no env var unlocks it.
#
# The retarget half (whose config gets read when a command names another repo) is
# covered by lib-repo-retarget.test.sh, which drives this same hook. Not repeated
# here beyond the master-gate case.
#
# The repo path contains a SPACE on purpose. Quoted-path truncation has caused
# three shipped bugs here; do not tidy it away.
#
# Self-contained: builds its own throwaway repo, touches nothing else.
#
# Run: bash references/hooks/tests/guard-closing-keywords.test.sh

set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
HOOK="$HERE/../claude-hooks/guard-closing-keywords.sh"
[ -f "$HOOK" ] || { echo "missing hook: $HOOK"; exit 1; }

command -v python3 >/dev/null 2>&1 || { echo "python3 required; skipping"; exit 0; }

TMP=$(mktemp -d "${TMPDIR:-/tmp}/closing keywords test.XXXXXX") || exit 1
TMP=$(cd "$TMP" && pwd -P)
R="$TMP/64 Org repo"
OUT="$TMP/hook.out"

cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

mkdir -p "$R" && cd "$R" || exit 1
git init -q -b main . >/dev/null 2>&1
git config user.email t@t.test; git config user.name t
# THE MASTER GATE. Every hook in this directory exits 0 immediately in a repo with
# no estate.mode. Without this line nothing runs and every case below "passes"
# as allow while testing nothing at all.
git config estate.mode native
git config estate.trunk main
git config estate.host github
git config estate.ticket.system github
echo x > f.txt
git add -A >/dev/null 2>&1 && git commit -qm init >/dev/null 2>&1

PASS=0; FAIL=0
LAST_WANT=""

verdict() { # <expect allow|block> <label> <rc>
  local got=allow
  [ "$3" -ne 0 ] && got=block
  LAST_WANT="$1"
  if [ "$got" = "$1" ]; then
    PASS=$((PASS+1)); printf '  PASS [%s] %s\n' "$got" "$2"
  else
    FAIL=$((FAIL+1)); printf '  FAIL expected=%s got=%s :: %s\n' "$1" "$got" "$2"
    sed -n '1,4p' "$OUT" | sed 's/^/        /'
  fi
}

run() { # <expect allow|block> <label> <bash command text>
  printf '%s' "$3" \
    | python3 -c 'import json,sys; print(json.dumps({"tool_name":"Bash","tool_input":{"command":sys.stdin.read()}}))' \
    | bash "$HOOK" >"$OUT" 2>&1
  verdict "$1" "$2" "$?"
}

# Two rules, one exit code. A block for the wrong reason points the agent at the
# wrong fix, so the reason is asserted wherever both rules could plausibly fire.
reason() { # <expected substring> <label>
  if /usr/bin/grep -q "$1" "$OUT" 2>/dev/null; then
    PASS=$((PASS+1)); printf '  PASS [reason] %s\n' "$2"
  else
    FAIL=$((FAIL+1)); printf '  FAIL reason %s not in output :: %s\n' "$1" "$2"
    sed -n '1,4p' "$OUT" | sed 's/^/        /'
  fi
}

echo "== the master gate: without estate.mode nothing here is armed =="
git config --unset estate.mode
run allow "mode unset, a keyword that would otherwise block" 'git commit -m "fixes #7"'
git config estate.mode native
run block "mode set, same command"                           'git commit -m "fixes #7"'

echo
echo "== the sanctioned form is not touched =="
run allow "refs #7"                     'git commit -m "refs #7: the thing"'
run allow "ref #7"                      'git commit -m "ref #7"'
run allow "no ticket reference at all"   'git commit -m "chore: tidy"'
run allow "a bare #7 under GitHub"       'git commit -m "see #7 for context"'

echo
echo "== every closing keyword GitHub honours =="
run block "fixes #7"     'git commit -m "fixes #7"'
run block "fix #7"       'git commit -m "fix #7"'
run block "fixed #7"     'git commit -m "fixed #7"'
run block "closes #7"    'git commit -m "closes #7"'
run block "close #7"     'git commit -m "close #7"'
run block "closed #7"    'git commit -m "closed #7"'
run block "resolves #7"  'git commit -m "resolves #7"'
run block "resolve #7"   'git commit -m "resolve #7"'
run block "resolved #7"  'git commit -m "resolved #7"'
run block "Fixes #7 (capitalised)"        'git commit -m "Fixes #7"'
run block "FIXES #7 (shouting)"           'git commit -m "FIXES #7"'
run block "keyword in the body, not the subject" 'git commit -m "feat: thing

Closes #7"'
run block "multiple keywords"             'git commit -m "fixes #7, closes #8"'
run block "tab between keyword and ref"   "$(printf 'git commit -m "fixes\t#7"')"

echo
echo "== not a keyword, so not blocked =="
run allow "fixup #7 (no space before up)" 'git commit -m "fixup #7"'
run allow "prose about the keyword, no #N" 'git commit -m "refs #7 and never write the closes keyword"'
run allow "keyword and #N far apart"       'git commit -m "closes the loop; refs #7"'

echo
echo "== the leading edge has no word boundary, and that over-blocks =="
# BSD/POSIX ERE has no \b, and KEYWORDS is not anchored on the left, so any word
# ENDING in a keyword trips rule 1: "hotfix #7" is refused even though GitHub
# would not close #7 for it. Documented here rather than asserted as intent —
# it is an over-block, which fails in the safe direction, and the fix (a left
# boundary) is not free on macOS.
run block "hotfix #7 (over-block, fails safe)" 'git commit -m "hotfix #7"'
run block "prefix #7 (same cause)"             'git commit -m "prefix #7 with the id"'

echo
echo "== which carriers are in scope =="
run block "git commit --amend"            'git commit --amend -m "fixes #7"'
run block "flags between git and commit"  'git --no-pager commit -m "fixes #7"'
run block "after && in a pipeline"        'git add -A && git commit -m "fixes #7"'
run block "after ; in a pipeline"         'true; git commit -m "fixes #7"'
run block "one env-var prefix"            'GIT_AUTHOR_NAME=x git commit -m "fixes #7"'
run block "two env-var prefixes"          'A=1 B=2 git commit -m "fixes #7"'
run block "git -C <path with a space>"    "git -C \"$R\" commit -m \"fixes #7\""
run block "gh pr create --title"          'gh pr create --base main --title "fixes #7" --body x'
run block "gh pr create --body"           'gh pr create --base main --title x --body "closes #7"'
run block "gh pr edit --body"             'gh pr edit 5 --body "resolves #7"'
run block "gh pr merge --subject"         'gh pr merge 5 --squash --subject "fixes #7"'
run block "gh issue create --body"        'gh issue create --title x --body "fixes #7"'
run block "gh issue edit --body"          'gh issue edit 9 --body "fixes #7"'

echo
echo "== out of scope: nothing here can carry a keyword to GitHub =="
run allow "echo"                          'echo "fixes #7"'
run allow "a file write"                   'printf "fixes #7\n" > notes.md'
run allow "git log --grep"                 'git log --grep="fixes #7" --oneline'
run allow "git commit quoted inside a heredoc" 'cat > doc.md <<EOF
never write: git commit -m "fixes #7"
EOF'
# A comment cannot close an issue on GitHub, so this is out of scope by design
# rather than by omission.
run allow "gh issue comment"               'gh issue comment 7 --body "fixes #7"'
run allow "gh pr view"                     'gh pr view 5 --json body'
run allow "gh pr comment"                  'gh pr comment 5 --body "fixes #7"'

echo
echo "== the heredoc seam =="
# strip_heredocs() removes heredoc BODIES before any pattern scan. For a guard
# that reads COMMANDS that is correct — a commit message routinely quotes the
# commands other guards look for. For this guard the body IS the subject.
#
# This half has a backstop: commit-msg carries the same check and sees the real
# message whatever fed it, so the commit is still refused. Allow is therefore the
# right verdict HERE, and the coverage lives in commit-msg.test.sh.
run allow "git commit -F - (commit-msg backstops it)" 'git commit -F - <<MSG
feat: thing

fixes #7
MSG'

# FIXED BUG, kept as the regression. `gh pr create --body-file -` reads the PR body
# from stdin, and a PR body is exactly what NO git hook can ever see — the hook's
# own header says so ("including PR titles and bodies, which no git hook can ever
# see"). strip_heredocs() deleted the body before rule 1 ran, so the keyword reached
# the PR description and closed the issue on merge with nothing in the stack left to
# catch it. The text was right there in the payload; never an inherent limit.
#
# The fix is deliberately narrow: for the commands that PUBLISH a stdin body to the
# tracker, and only those, the raw text is judged with the body left in.
run block "gh pr create --body-file -"          'gh pr create --base main --title x --body-file - <<MSG
fixes #7
MSG'
run block "gh pr create -F - (short form)"      'gh pr create --base main --title x -F - <<MSG
closes #7
MSG'
run block "gh pr edit --body-file -"            'gh pr edit 5 --body-file - <<MSG
resolves #7
MSG'
run block "gh issue create --body-file -"       'gh issue create --title x --body-file - <<MSG
fixes #7
MSG'
run block "gh pr merge --body-file -"           'gh pr merge 5 --squash --body-file - <<MSG
fixes #7
MSG'
# A published body written correctly is still fine, so this did not become a blanket
# refusal of --body-file -.
run allow "a published body with no keyword"    'gh pr create --base main --title x --body-file - <<MSG
refs #7

Deployed and verified; closing is a separate step.
MSG'
# And this one is NOT a false positive, which is why the narrow fix has no
# false-positive class to trade against: GitHub parses closing keywords ANYWHERE in
# a PR description, parentheses and surrounding prose included. A body that quotes
# "fixes #7" really does close issue 7 on merge. Blocking it is the correct answer,
# unlike the same text in a commit message being read by a guard that scans commands.
run block "a published body that quotes the keyword" 'gh pr create --base main --title x --body-file - <<MSG
refs #7 (never write: git commit -m "fixes #7")
MSG'
# The stripping itself is untouched everywhere else: a heredoc body that is not
# going to the tracker is still data.
run allow "heredoc body not bound for the tracker" 'cat > pr-notes.md <<MSG
fixes #7
MSG'

# By contrast this one IS an inherent limit, not a defect: the keyword is in a
# file the hook never sees. Recorded so the two are not confused.
run allow "gh pr create --body-file notes.md (out of reach by construction)" \
  'gh pr create --base main --title x --body-file notes.md'

echo
echo "== rule 2: a bare #N when GitHub is not the tracker =="
git config estate.ticket.system jira
git config estate.ticket.project EXAMPLE
run block "#12 in a commit"          'git commit -m "wip #12"'
reason "GitHub issue reference"      "rule 2 explains the cross-link, not the keyword"
run block "#12 in a PR body"         'gh pr create --base main --title x --body "see #12"'
reason "GitHub issue reference"      "rule 2 fires on PR bodies too"
run allow "a Jira key is fine"       'git commit -m "EXAMPLE-1: the thing"'
run allow "Jira key in a PR title"   'gh pr create --base main --title "EXAMPLE-1 thing" --body y'
run allow "#12 outside a carrier"    'echo "see #12"'

echo "-- rule 1 still wins where both could fire --"
run block "fixes #12 under Jira"     'git commit -m "fixes #12"'
reason "closing keyword"             "rule 1 is reported, not rule 2"

echo "-- ticket.system=pattern --"
git config estate.ticket.system pattern
run block "#12 under a custom pattern" 'git commit -m "wip #12"'
reason "GitHub issue reference"        "rule 2 covers every non-GitHub tracker"

echo "-- ticket.system=none: rule 2 stands down, rule 1 does not --"
git config estate.ticket.system none
run allow "#12 with no tracker configured" 'git commit -m "wip #12"'
run block "fixes #12 with no tracker"      'git commit -m "fixes #12"'
reason "closing keyword"                   "rule 1 is tracker-independent"
git config estate.ticket.system github

echo
echo "== there is no escape hatch, and no env var invents one =="
ALEY_ALLOW_CLOSING_KEYWORD=1 \
  run block "ALEY_ALLOW_CLOSING_KEYWORD=1" 'git commit -m "fixes #7"'
ALEY_SKIP_HOOKS=1 \
  run block "ALEY_SKIP_HOOKS=1"            'git commit -m "fixes #7"'

echo
echo "== payloads with no command at all =="
python3 -c 'import json; print(json.dumps({"tool_name":"Bash","tool_input":{}}))' \
  | bash "$HOOK" >"$OUT" 2>&1
verdict allow "Bash with no command field" "$?"
python3 -c 'import json,sys; print(json.dumps({"tool_name":"Write","tool_input":{"file_path":sys.argv[1]+"/notes.md","content":"fixes #7"}}))' "$R" \
  | bash "$HOOK" >"$OUT" 2>&1
verdict allow "a Write whose CONTENT holds the keyword" "$?"
python3 -c 'import json; print(json.dumps({"tool_name":"mcp__srv__createJiraIssue","tool_input":{"summary":"fixes #7"}}))' \
  | bash "$HOOK" >"$OUT" 2>&1
verdict allow "an MCP tool call" "$?"
printf 'not json at all' | bash "$HOOK" >"$OUT" 2>&1
verdict allow "malformed input" "$?"

echo
printf '%d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
