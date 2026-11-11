#!/bin/bash
set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
STATUS="$HERE/../bin/aleysian-devops-branch-status"
TMP=$(mktemp -d "${TMPDIR:-/tmp}/devops-branch-status.XXXXXX") || exit 1
trap 'rm -rf "$TMP"' EXIT
BIN="$TMP/bin"; OUT="$TMP/out"; LOG="$TMP/gh.log"
mkdir -p "$BIN"

cat > "$BIN/gh" <<'SH'
#!/bin/bash
printf '%s\n' "$*" >> "$GH_LOG"
if [ "$1 $2" = "repo view" ]; then printf 'Aleysian/Test\n'; exit 0; fi
case "$MODE:$*" in
  missing:*'/branches/'*) exit 1 ;;
  unprotected:*'/branches/'*'/protection') printf '{"allow_deletions":{"enabled":false}}\n' ;;
  unprotected:*'/branches/'*) printf '{"protected":false}\n' ;;
  classic_safe:*'/branches/'*'/protection') printf '{"allow_deletions":{"enabled":false}}\n' ;;
  classic_safe:*'/branches/'*) printf '{"protected":true}\n' ;;
  classic_delete:*'/branches/'*'/protection') printf '{"allow_deletions":{"enabled":true}}\n' ;;
  classic_delete:*'/rules/branches/'*) printf '[]\n' ;;
  classic_delete:*'/branches/'*) printf '{"protected":true}\n' ;;
  rules_safe:*'/branches/'*'/protection') exit 1 ;;
  rules_safe:*'/rules/branches/'*) printf '[{"type":"deletion"}]\n' ;;
  rules_safe:*'/branches/'*) printf '{"protected":true}\n' ;;
  *) exit 1 ;;
esac
SH
chmod +x "$BIN/gh"

GH_LOG="$LOG"; export GH_LOG
PATH="$BIN:$PATH"; export PATH
PASS=0; FAIL=0
run() { # mode expected label
  MODE="$1"; export MODE
  local expected="$2" label="$3" rc
  "$STATUS" --branch dev/WI-000001 --json > "$OUT" 2>&1
  rc=$?
  if [ "$rc" -eq "$expected" ]; then
    PASS=$((PASS+1)); echo "  PASS [$rc] $label"
  else
    FAIL=$((FAIL+1)); echo "  FAIL expected=$expected got=$rc $label"; sed -n '1,6p' "$OUT"
  fi
}

command -v jq >/dev/null 2>&1 || { echo "jq required; skipping"; exit 0; }

echo "== permanent GitHub pipeline branches =="
run classic_safe 0 "classic protection blocks deletion"
run rules_safe 0 "active ruleset blocks deletion"
run classic_delete 3 "deletion-enabled protection is unsafe"
run unprotected 3 "unprotected branch is unsafe"
run missing 2 "missing or unreadable branch is unverified"

if grep -q 'dev%2FWI-000001' "$LOG"; then
  PASS=$((PASS+1)); echo "  PASS branch names are URL encoded"
else
  FAIL=$((FAIL+1)); echo "  FAIL branch names were not URL encoded"
fi

echo
echo "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
