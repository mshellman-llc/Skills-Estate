#!/bin/bash
set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
HOOK="$HERE/../githooks/pre-commit"
TMP=$(mktemp -d "${TMPDIR:-/tmp}/precommit-devops.XXXXXX") || exit 1
trap 'rm -rf "$TMP"' EXIT
R="$TMP/repo"; W="$TMP/wi"; OUT="$TMP/out"

mkdir -p "$R/force-app/main/default" && cd "$R" || exit 1
git init -q -b main .
git config user.email t@t.test; git config user.name t
git config estate.mode native
git config estate.delivery devops-center
git config estate.trunk staging
git config estate.protected 'staging main'
git config estate.format off
git config estate.pmd advise
git config core.hooksPath /dev/null
printf '<x/>\n' > force-app/main/default/a.xml
git add -A && git commit -qm baseline
git branch staging
git worktree add -q -b WI-000001 "$W"

PASS=0; FAIL=0
run() {
  local want="$1" cwd="$2" label="$3" got=allow rc
  ( cd "$cwd" && bash "$HOOK" ) >"$OUT" 2>&1
  rc=$?; [ "$rc" -ne 0 ] && got=block
  if [ "$got" = "$want" ]; then PASS=$((PASS+1)); echo "  PASS [$got] $label"
  else FAIL=$((FAIL+1)); echo "  FAIL expected=$want got=$got $label"; sed -n '1,8p' "$OUT"; fi
}

echo "== DevOps Center pre-commit topology =="
printf '<x>main</x>\n' > "$R/force-app/main/default/a.xml"
git -C "$R" add force-app
run block "$R" "protected main cannot commit source"
git -C "$R" restore --staged --worktree force-app/main/default/a.xml

printf '<x>wi</x>\n' > "$W/force-app/main/default/a.xml"
git -C "$W" add force-app
run allow "$W" "WI worktree can commit source"
git -C "$W" branch -m feature/not-a-wi
run block "$W" "non-WI worktree cannot commit source"
git -C "$W" config estate.devops.workmodel shared
git -C "$W" config estate.devops.developmentbranchpattern '^dev/WI-[0-9]+$'
git -C "$W" branch -m dev/WI-000001
run allow "$W" "shared dev/WI worktree can commit source"

echo "== Merge-aware WI delta =="
M="$TMP/merge-repo"; MW="$TMP/merge-wi"; CHAIN="$TMP/client-hooks"; LOG="$TMP/tool-log"
mkdir -p "$M/force-app/main/default/lwc/card" "$M/node_modules/.bin" "$CHAIN"
cd "$M" || exit 1
git init -q -b main .
git config user.email t@t.test; git config user.name t
git config core.hooksPath /dev/null
git config estate.mode stealth
git config estate.delivery devops-center
git config estate.trunk staging
git config estate.protected 'staging main'
git config estate.format off
git config estate.pmd advise
git config estate.chainhooks "$CHAIN"
printf 'export default 0;\n' > force-app/main/default/lwc/card/wi.js
git add -A && git commit -qm baseline
git branch staging
git worktree add -q -b WI-000010 "$MW"

printf 'export default 10;\n' > "$MW/force-app/main/default/lwc/card/wi.js"
git -C "$MW" add -A && git -C "$MW" commit -qm 'WI-000010 change'
git -C "$M" switch -q staging
printf 'export default 8;\n' > "$M/force-app/main/default/lwc/card/alreadyPromoted.js"
git -C "$M" add -A && git -C "$M" commit -qm 'WI-000008 baseline'

cat > "$M/node_modules/.bin/eslint" <<EOF
#!/bin/bash
printf 'eslint %s\n' "\$*" >> "$LOG"
EOF
cat > "$M/node_modules/.bin/lint-staged" <<EOF
#!/bin/bash
printf 'lint-staged %s\n' "\$*" >> "$LOG"
EOF
chmod +x "$M/node_modules/.bin/eslint" "$M/node_modules/.bin/lint-staged"
printf '#!/bin/bash\nnpx lint-staged\n' > "$CHAIN/pre-commit"
chmod +x "$CHAIN/pre-commit"

git -C "$MW" merge --no-commit staging >/dev/null
run allow "$MW" "stage sync gates the net WI delta"
if grep -q 'eslint .*wi.js' "$LOG" && ! grep -q 'eslint .*alreadyPromoted.js' "$LOG"; then
  PASS=$((PASS+1)); echo "  PASS [scope] Estate lint excludes imported stage files"
else
  FAIL=$((FAIL+1)); echo "  FAIL Estate lint scope"; cat "$LOG"
fi
MERGED_STAGE=$(git -C "$MW" rev-parse MERGE_HEAD)
if grep -q "lint-staged --diff $MERGED_STAGE" "$LOG"; then
  PASS=$((PASS+1)); echo "  PASS [scope] chained lint-staged uses MERGE_HEAD"
else
  FAIL=$((FAIL+1)); echo "  FAIL chained lint-staged scope"; cat "$LOG"
fi

echo
echo "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
