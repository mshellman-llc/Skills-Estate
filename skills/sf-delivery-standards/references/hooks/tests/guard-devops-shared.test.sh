#!/bin/bash
set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
HOOK="$HERE/../claude-hooks/guard-devops-shared.sh"
TMP=$(mktemp -d "${TMPDIR:-/tmp}/guard devops shared.XXXXXX") || exit 1
trap 'rm -rf "$TMP"' EXIT
R="$TMP/repo"; O="$TMP/origin.git"; BIN="$TMP/bin"; RECEIPT="$TMP/receipt"; OUT="$TMP/out"
mkdir -p "$R" "$BIN"
git init -q --bare "$O"
git -C "$R" init -q -b staging .
git -C "$R" config user.email t@t.test; git -C "$R" config user.name t
printf 'base\n' > "$R/file"
git -C "$R" add file && git -C "$R" commit -qm base
git -C "$R" branch stevenc
git -C "$R" branch WI-000001
git -C "$R" remote add origin "$O"
git -C "$R" push -q origin staging stevenc WI-000001
git -C "$R" config aleysian.mode native
git -C "$R" config aleysian.delivery devops-center
git -C "$R" config aleysian.host github
git -C "$R" config aleysian.trunk staging
git -C "$R" config aleysian.devops.workmodel shared
git -C "$R" config aleysian.devops.integrationbranch stevenc
git -C "$R" config aleysian.devops.environment StevenC
git -C "$R" config aleysian.devops.branchpattern '^WI-[0-9]+$'
git -C "$R" config aleysian.devops.developmentbranchpattern '^dev/WI-[0-9]+$'
git -C "$R" rev-parse stevenc > "$RECEIPT"

cat > "$BIN/gh" <<'SH'
#!/bin/bash
if [ "$1 $2" = "repo view" ]; then printf 'Aleysian/Test\n'; exit 0; fi
case "$*" in
  *'/deployments -f environment=StevenC'*) printf '[{"id":42,"sha":"%s"}]\n' "$(cat "$RECEIPT")" ;;
  *'/deployments/42/statuses'*) printf '[{"state":"success"}]\n' ;;
  *) exit 1 ;;
esac
SH
chmod +x "$BIN/gh"
export RECEIPT
PATH="$BIN:$PATH"; export PATH

PASS=0; FAIL=0
run() {
  local want="$1" label="$2" cmd="$3" got=allow rc
  (cd "$R" && printf '%s' "$cmd" \
    | python3 -c 'import json,sys; print(json.dumps({"tool_name":"Bash","tool_input":{"command":sys.stdin.read()}}))' \
    | bash "$HOOK") > "$OUT" 2>&1
  rc=$?; [ "$rc" -ne 0 ] && got=block
  if [ "$got" = "$want" ]; then PASS=$((PASS+1)); echo "  PASS [$got] $label"
  else FAIL=$((FAIL+1)); echo "  FAIL expected=$want got=$got $label"; sed -n '1,10p' "$OUT"; fi
}

echo "== shared development branch creation =="
run block "stale implicit base is refused" "git worktree add '$TMP/dev' -b dev/WI-000001"
run allow "explicit deployed integration base is allowed" "git worktree add '$TMP/dev' -b dev/WI-000001 origin/stevenc"

git -C "$R" checkout -q stevenc
printf 'ahead\n' >> "$R/file"
git -C "$R" add file && git -C "$R" commit -qm ahead
git -C "$R" push -q origin stevenc
git -C "$R" checkout -q staging
run block "branch ahead of deployment receipt freezes new work" "git worktree add '$TMP/dev' -b dev/WI-000002 origin/stevenc"

git -C "$R" checkout -q WI-000001
run block "integration branch cannot merge into package" "git merge origin/stevenc"

git -C "$R" config aleysian.devops.workmodel isolated
run allow "isolated DevOps Center mode is unchanged" "git merge origin/stevenc"
git -C "$R" config aleysian.delivery direct
run allow "direct delivery is unchanged" "git worktree add '$TMP/dev' -b dev/WI-000003 origin/stevenc"

echo
echo "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
