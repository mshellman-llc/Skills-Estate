#!/bin/bash
set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
INSTALL="$HERE/../../../scripts/install.sh"
TMP=$(mktemp -d "${TMPDIR:-/tmp}/install-devops.XXXXXX") || exit 1
trap 'rm -rf "$TMP"' EXIT
export HOME="$TMP/home"
R="$TMP/repo"
BIN="$TMP/bin"

mkdir -p "$HOME" "$R" "$BIN" && cd "$R" || exit 1
cat > "$BIN/sf" <<'SH'
#!/bin/bash
case "$*" in
  "devops pipeline get"*)
    printf '%s\n' '{"status":0,"result":{"id":"PIPE1","connectedProjects":[{"id":"0I0TEST"}],"stages":[{"id":"PROD","nextStageId":null,"branchName":"main"},{"id":"STAGE","nextStageId":"PROD","branchName":"staging"}]}}'
    ;;
  *) exit 1 ;;
esac
SH
chmod +x "$BIN/sf"
export PATH="$BIN:$PATH"
git init -q -b main .
git config user.email t@t.test
git config user.name t
printf '{"packageDirectories":[{"path":"force-app","default":true}],"sourceApiVersion":"65.0"}\n' > sfdx-project.json
git add sfdx-project.json && git commit -qm baseline

bash "$INSTALL" --repo --platform both --mode native --delivery devops-center \
  --host github --review pr --protected other \
  --devops-org-alias prod --devops-project-id 0I0TEST --devops-pipeline-id PIPE1 >/dev/null

PASS=0; FAIL=0
check() {
  if "$@"; then PASS=$((PASS+1)); echo "  PASS $*"
  else FAIL=$((FAIL+1)); echo "  FAIL $*"; fi
}

echo "== DevOps Center installer coherence =="
PROTECTED=$(git config aleysian.protected)
check grep -qw other <<< "$PROTECTED"
check grep -qw staging <<< "$PROTECTED"
check grep -qw main <<< "$PROTECTED"
check test "$(git config aleysian.squash)" = require
check test "$(git config aleysian.devops.branchpattern)" = '^WI-[0-9]+$'
check test "$(git config aleysian.devops.pipelineid)" = PIPE1
check test "$(git config aleysian.trunk)" = staging
check grep -q 'DevOps Center owns every merge' CLAUDE.md
check grep -q 'DevOps Center owns every merge' AGENTS.md
check grep -q 'plugin/capability preflight' AGENTS.md
if grep -q '2.2.0' AGENTS.md; then
  FAIL=$((FAIL+1)); echo "  FAIL AGENTS.md embeds a plugin version"
else
  PASS=$((PASS+1)); echo "  PASS AGENTS.md keeps plugin details in the promotion skill"
fi

echo "== Shared development-org variant =="
git branch stevenc
bash "$INSTALL" --repo --platform both --mode native --delivery devops-center \
  --host github --review pr --protected other \
  --devops-org-alias prod --devops-project-id 0I0TEST --devops-pipeline-id PIPE1 \
  --devops-work-model shared --devops-integration-branch stevenc \
  --devops-environment StevenC >/dev/null
PROTECTED=$(git config aleysian.protected)
check grep -qw stevenc <<< "$PROTECTED"
check test "$(git config aleysian.devops.workmodel)" = shared
check test "$(git config aleysian.devops.developmentbranchpattern)" = '^dev/WI-[0-9]+$'
check grep -q 'shared development org and its integration branch agree' CLAUDE.md
check grep -q 'aleysian-devops-package' AGENTS.md

if bash "$INSTALL" --repo --platform both --mode native --delivery devops-center \
  --host gitlab --devops-work-model shared --devops-integration-branch stevenc \
  --devops-environment StevenC --trunk staging >/dev/null 2>&1; then
  FAIL=$((FAIL+1)); echo "  FAIL non-GitHub shared mode was allowed"
else
  PASS=$((PASS+1)); echo "  PASS non-GitHub shared mode was refused"
fi

echo "== Pipeline topology is authoritative =="
if bash "$INSTALL" --repo --platform both --mode native --delivery devops-center \
  --trunk wrong --host github --devops-org-alias prod --devops-project-id 0I0TEST \
  --devops-pipeline-id PIPE1 >/dev/null 2>&1; then
  FAIL=$((FAIL+1)); echo "  FAIL mismatching --trunk was allowed"
else
  PASS=$((PASS+1)); echo "  PASS mismatching --trunk was refused"
fi

echo
echo "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
