#!/bin/bash
set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
HOOK="$HERE/../claude-hooks/guard-devops-handoff.sh"
TMP=$(mktemp -d "${TMPDIR:-/tmp}/devops-handoff.XXXXXX") || exit 1
trap 'rm -rf "$TMP"' EXIT
R="$TMP/repo"; W="$TMP/wi"; OUT="$TMP/out"

mkdir -p "$R" && cd "$R" || exit 1
git init -q -b staging .
git config user.email t@t.test; git config user.name t
git config aleysian.mode native
git config aleysian.delivery devops-center
git config aleysian.trunk staging
git config aleysian.devops.branchpattern '^WI-[0-9]+$'
mkdir -p force-app/main/default
printf '<x/>\n' > force-app/main/default/base.xml
git add -A && git commit -qm 'baseline'
git worktree add -q -b WI-000001 "$W"
cd "$W" || exit 1
printf '<x>wi</x>\n' > force-app/main/default/base.xml
git add -A && git commit -qm 'feat: WI change (WI-000001)'

PASS=0; FAIL=0
run() {
  local want="$1" label="$2" cmd="$3" got=allow rc
  printf '%s' "$cmd" | python3 -c 'import json,sys; print(json.dumps({"tool_name":"Bash","tool_input":{"command":sys.stdin.read()}}))' \
    | bash "$HOOK" >"$OUT" 2>&1
  rc=$?; [ "$rc" -ne 0 ] && got=block
  if [ "$got" = "$want" ]; then PASS=$((PASS+1)); echo "  PASS [$got] $label"
  else FAIL=$((FAIL+1)); echo "  FAIL expected=$want got=$got $label"; sed -n '1,8p' "$OUT"; fi
}

echo "== DevOps Center review handoff =="
run block "requires validation" "gh pr create --base staging --title WI-000001"
mkdir -p "$R/.git/aleysian"
printf '%s WI-000001 now\n' "$(git rev-parse HEAD)" > "$R/.git/aleysian/validate-log"
run block "requires explicit base" "gh pr create --title WI-000001"
run allow "validated WI can open staging PR" "gh pr create --base staging --title WI-000001"
run allow "validated WI can use managed review API" "sf devops review create --work-item-name WI-000001 --target-org control --json"

printf '<x>dirty</x>\n' > force-app/main/default/base.xml
run block "dirty WI source cannot hand off" "gh pr create --base staging --title WI-000001"
git restore force-app/main/default/base.xml

git config aleysian.delivery direct
run allow "direct delivery remains unchanged" "gh pr create --title ordinary"

echo
echo "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
