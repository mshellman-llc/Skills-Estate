#!/bin/bash
set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
HOOK="$HERE/../claude-hooks/guard-devops-handoff.sh"
PACKAGE="$HERE/../bin/aleysian-devops-package"
TMP=$(mktemp -d "${TMPDIR:-/tmp}/shared handoff.XXXXXX") || exit 1
trap 'rm -rf "$TMP"' EXIT
R="$TMP/repo"; O="$TMP/origin.git"; D="$TMP/dev"; P="$TMP/package"; BIN="$TMP/bin"
RECEIPT="$TMP/receipt"; OUT="$TMP/out"
mkdir -p "$R/force-app/main/default" "$BIN"
git init -q --bare "$O"
git -C "$R" init -q -b staging .
git -C "$R" config user.email t@t.test; git -C "$R" config user.name t
printf '<a>base</a>\n' > "$R/force-app/main/default/a.xml"
printf '{"packageDirectories":[{"path":"force-app","default":true}],"sourceApiVersion":"65.0"}\n' > "$R/sfdx-project.json"
git -C "$R" add force-app sfdx-project.json && git -C "$R" commit -qm base
git -C "$R" branch stevenc
git -C "$R" branch WI-000001
git -C "$R" worktree add -q -b dev/WI-000001 "$D" stevenc
printf '<a>wi1</a>\n' > "$D/force-app/main/default/a.xml"
git -C "$D" add force-app && git -C "$D" commit -qm 'feat: WI-000001'
DEV_HEAD=$(git -C "$D" rev-parse HEAD)

git -C "$R" checkout -q stevenc
printf '<a>wi1</a>\n' > "$R/force-app/main/default/a.xml"
git -C "$R" add force-app && git -C "$R" commit -qm accepted
git -C "$R" checkout -q staging
git -C "$R" worktree add -q "$P" WI-000001
git -C "$R" remote add origin "$O"
git -C "$R" push -q origin staging stevenc WI-000001 dev/WI-000001
git -C "$R" rev-parse stevenc > "$RECEIPT"

git -C "$R" config aleysian.mode native
git -C "$R" config aleysian.delivery devops-center
git -C "$R" config aleysian.host github
git -C "$R" config aleysian.trunk staging
git -C "$R" config aleysian.devops.workmodel shared
git -C "$R" config aleysian.devops.integrationbranch stevenc
git -C "$R" config aleysian.devops.environment StevenC
git -C "$R" config aleysian.devops.branchpattern '^WI-[0-9]+$'
git -C "$R" config aleysian.devops.developmentbranchpattern '^dev/WI-[0-9]+$'

cat > "$BIN/gh" <<'SH'
#!/bin/bash
if [ "$1 $2" = "repo view" ]; then printf 'Aleysian/Test\n'; exit 0; fi
case "$*" in
  *'/branches/'*'/protection'*) printf '{"allow_deletions":{"enabled":false}}\n' ;;
  *'/branches/'*)
    case "$*" in *"${UNSAFE_BRANCH:-__none__}"*) printf '{"protected":false}\n' ;; *) printf '{"protected":true}\n' ;; esac ;;
  *'/deployments -f environment=StevenC'*) printf '[{"id":42,"sha":"%s"}]\n' "$(cat "$RECEIPT")" ;;
  *'/deployments/42/statuses'*) printf '[{"state":"success"}]\n' ;;
  *) exit 1 ;;
esac
SH
chmod +x "$BIN/gh"
cat > "$BIN/sf" <<'SH'
#!/bin/bash
OUT=""; NAME="package.xml"
while [ $# -gt 0 ]; do
  case "$1" in --output-dir) OUT="$2"; shift ;; --name) NAME="$2"; shift ;; esac
  shift
done
mkdir -p "$OUT"
cat > "$OUT/$NAME" <<'XML'
<Package xmlns="http://soap.sforce.com/2006/04/metadata"><types><members>a</members><name>TestType</name></types><version>65.0</version></Package>
XML
SH
chmod +x "$BIN/sf"
export RECEIPT
UNSAFE_BRANCH=""; export UNSAFE_BRANCH
PATH="$BIN:$PATH"; export PATH
mkdir -p "$R/.git/aleysian"

PASS=0; FAIL=0
run() {
  local want="$1" cwd="$2" label="$3" cmd="$4" got=allow rc
  (cd "$cwd" && printf '%s' "$cmd" \
    | python3 -c 'import json,sys; print(json.dumps({"tool_name":"Bash","tool_input":{"command":sys.stdin.read()}}))' \
    | bash "$HOOK") > "$OUT" 2>&1
  rc=$?; [ "$rc" -ne 0 ] && got=block
  if [ "$got" = "$want" ]; then PASS=$((PASS+1)); echo "  PASS [$got] $label"
  else FAIL=$((FAIL+1)); echo "  FAIL expected=$want got=$got $label"; sed -n '1,12p' "$OUT"; fi
}

echo "== development integration review =="
printf '%s dev/WI-000001 now\n' "$DEV_HEAD" > "$R/.git/aleysian/validate-log"
run allow "$D" "validated dev branch targets integration" "gh pr create --base stevenc --title WI-000001"
run block "$D" "dev branch cannot create DevOps review" "sf devops review create --work-item-name WI-000001 --target-org control --json"

echo "== exact package handoff =="
(cd "$P" && "$PACKAGE" --development-branch dev/WI-000001) >/dev/null || exit 1
git -C "$P" add -A && git -C "$P" commit -qm 'feat: package WI-000001'
PACKAGE_HEAD=$(git -C "$P" rev-parse HEAD)
printf '%s WI-000001 now\n' "$PACKAGE_HEAD" >> "$R/.git/aleysian/validate-log"
run allow "$P" "ledger-matched package targets staging" "gh pr create --base staging --title WI-000001"

UNSAFE_BRANCH=staging; export UNSAFE_BRANCH
run block "$P" "deletable staging branch blocks handoff" "gh pr create --base staging --title WI-000001"
UNSAFE_BRANCH=""; export UNSAFE_BRANCH

printf '<extra/>\n' > "$P/force-app/main/default/extra.xml"
git -C "$P" add force-app && git -C "$P" commit -qm 'extra WI-000001'
PACKAGE_HEAD=$(git -C "$P" rev-parse HEAD)
printf '%s WI-000001 now\n' "$PACKAGE_HEAD" >> "$R/.git/aleysian/validate-log"
run block "$P" "extra packaged file blocks review" "gh pr create --base staging --title WI-000001"

echo
echo "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
