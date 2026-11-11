#!/bin/bash
set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
STATUS="$HERE/../bin/aleysian-devops-shared-status"
TMP=$(mktemp -d "${TMPDIR:-/tmp}/devops shared status.XXXXXX") || exit 1
trap 'rm -rf "$TMP"' EXIT
R="$TMP/repo"; O="$TMP/origin.git"; BIN="$TMP/bin"; RECEIPT="$TMP/receipt"; STATE="$TMP/state"
mkdir -p "$R" "$BIN"
git init -q --bare "$O"
git -C "$R" init -q -b staging .
git -C "$R" config user.email t@t.test
git -C "$R" config user.name t
printf 'base\n' > "$R/file"
git -C "$R" add file && git -C "$R" commit -qm base
git -C "$R" branch stevenc
git -C "$R" remote add origin "$O"
git -C "$R" push -q origin staging stevenc
git -C "$R" config aleysian.delivery devops-center
git -C "$R" config aleysian.devops.workmodel shared
git -C "$R" config aleysian.devops.integrationbranch stevenc
git -C "$R" config aleysian.devops.environment StevenC
git -C "$R" config aleysian.host github
git -C "$R" rev-parse stevenc > "$RECEIPT"
printf 'success\n' > "$STATE"

cat > "$BIN/gh" <<'SH'
#!/bin/bash
if [ "$1 $2" = "repo view" ]; then printf 'Aleysian/Test\n'; exit 0; fi
case "$*" in
  *'/deployments -f environment=StevenC'*)
    printf '[{"id":42,"sha":"%s"}]\n' "$(cat "$RECEIPT")" ;;
  *'/deployments/42/statuses'*)
    printf '[{"state":"%s"}]\n' "$(cat "$STATE")" ;;
  *) exit 1 ;;
esac
SH
chmod +x "$BIN/gh"
export RECEIPT STATE
PATH="$BIN:$PATH"; export PATH

PASS=0; FAIL=0
run() {
  local want="$1" label="$2" rc
  (cd "$R" && "$STATUS" --json) > "$TMP/out" 2>&1; rc=$?
  if [ "$rc" -eq "$want" ]; then PASS=$((PASS+1)); echo "  PASS [$rc] $label"
  else FAIL=$((FAIL+1)); echo "  FAIL expected=$want got=$rc $label"; cat "$TMP/out"; fi
}

echo "== centralized shared-org receipt =="
run 0 "matching deployment SHA is synced"

git -C "$R" checkout -q stevenc
printf 'next\n' >> "$R/file"
git -C "$R" add file && git -C "$R" commit -qm next
git -C "$R" push -q origin stevenc
run 3 "remote branch ahead of receipt is frozen"

git -C "$R" rev-parse stevenc > "$RECEIPT"
run 0 "new successful receipt restores sync"

printf 'failure\n' > "$STATE"
run 2 "no successful deployment is unverified"

echo
echo "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
