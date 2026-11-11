#!/bin/bash
set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PACKAGE="$HERE/../bin/aleysian-devops-package"
TMP=$(mktemp -d "${TMPDIR:-/tmp}/devops package.XXXXXX") || exit 1
trap 'rm -rf "$TMP"' EXIT
R="$TMP/repo"; O="$TMP/origin.git"; BIN="$TMP/bin"; RECEIPT="$TMP/receipt"; OUT="$TMP/out"
mkdir -p "$R/force-app/main/default" "$BIN"
git init -q --bare "$O"
git -C "$R" init -q -b staging .
git -C "$R" config user.email t@t.test; git -C "$R" config user.name t
printf '<a>base</a>\n' > "$R/force-app/main/default/a.xml"
printf '<b>base</b>\n' > "$R/force-app/main/default/b.xml"
printf '{"packageDirectories":[{"path":"force-app","default":true}],"sourceApiVersion":"65.0"}\n' > "$R/sfdx-project.json"
git -C "$R" add force-app sfdx-project.json && git -C "$R" commit -qm base
BASE=$(git -C "$R" rev-parse HEAD)
git -C "$R" branch stevenc
git -C "$R" branch WI-000001
git -C "$R" checkout -qb dev/WI-000001
printf '<a>wi1</a>\n' > "$R/force-app/main/default/a.xml"
git -C "$R" add force-app && git -C "$R" commit -qm 'WI-000001 development'
DEV_HEAD=$(git -C "$R" rev-parse HEAD)

# Simulate the accepted squash on the integration branch. An unrelated file may
# differ; the owned WI file must remain byte-identical.
git -C "$R" checkout -q stevenc
printf '<a>wi1</a>\n' > "$R/force-app/main/default/a.xml"
printf '<b>another wi</b>\n' > "$R/force-app/main/default/b.xml"
git -C "$R" add force-app && git -C "$R" commit -qm 'accepted shared state'
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
PATH="$BIN:$PATH"; export PATH

PASS=0; FAIL=0
pass() { PASS=$((PASS+1)); echo "  PASS $1"; }
fail() { FAIL=$((FAIL+1)); echo "  FAIL $1"; sed -n '1,12p' "$OUT"; }

echo "== exact WI packaging =="
git -C "$R" checkout -q WI-000001
if (cd "$R" && "$PACKAGE" --development-branch dev/WI-000001) > "$OUT" 2>&1; then
  pass "accepted development patch applies to generated WI branch"
else
  fail "package command should succeed"
fi
[ "$(cat "$R/force-app/main/default/a.xml")" = '<a>wi1</a>' ] \
  && pass "owned file is byte-identical" || fail "owned file content differs"
[ "$(cat "$R/force-app/main/default/b.xml")" = '<b>base</b>' ] \
  && pass "unrelated integration change is excluded" || fail "unrelated change leaked"
jq -e --arg base "$BASE" --arg head "$DEV_HEAD" \
  '.workItem == "WI-000001" and .developmentBase == $base and .acceptedDevelopmentHead == $head and (.files|length) == 1 and .metadataMembers == [{"type":"TestType","fullName":"a"}]' \
  "$R/.aleysian/work-items/WI-000001.json" >/dev/null \
  && pass "scope ledger records the development boundary" || fail "scope ledger is wrong"

echo "== same-file overlap fails closed =="
git -C "$R" reset -q --hard HEAD
rm -rf "$R/.aleysian"
git -C "$R" checkout -q stevenc
printf '<a>later wi</a>\n' > "$R/force-app/main/default/a.xml"
git -C "$R" add force-app && git -C "$R" commit -qm 'later overlap'
git -C "$R" push -q origin stevenc
git -C "$R" rev-parse stevenc > "$RECEIPT"
git -C "$R" checkout -q WI-000001
if (cd "$R" && "$PACKAGE" --development-branch dev/WI-000001) > "$OUT" 2>&1; then
  fail "overlap should block"
else
  grep -q 'shared component overlap' "$OUT" && pass "later same-file change blocks packaging" \
    || fail "overlap blocked for the wrong reason"
fi

echo
echo "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
