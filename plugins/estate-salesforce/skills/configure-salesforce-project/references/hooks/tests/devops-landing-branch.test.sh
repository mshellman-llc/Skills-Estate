#!/bin/bash
set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
RESOLVER="$HERE/../../../scripts/resolve-devops-landing.sh"
TMP=$(mktemp -d "${TMPDIR:-/tmp}/devops-landing.XXXXXX") || exit 1
trap 'rm -rf "$TMP"' EXIT
PASS=0
FAIL=0

check_eq() {
  local label="$1" want="$2" got="$3"
  if [ "$want" = "$got" ]; then PASS=$((PASS+1)); echo "  PASS $label"
  else FAIL=$((FAIL+1)); echo "  FAIL $label (wanted '$want', got '$got')"; fi
}

check_fail() {
  local label="$1"; shift
  if "$@" >/dev/null 2>&1; then FAIL=$((FAIL+1)); echo "  FAIL $label (allowed)"
  else PASS=$((PASS+1)); echo "  PASS $label"; fi
}

printf '%s\n' '{
  "status": 0,
  "result": {
    "id": "PIPE1",
    "connectedProjects": [{"id": "PROJ1", "name": "64org Delivery"}],
    "stages": [
      {"id": "PROD", "name": "Production", "nextStageId": null, "branchName": "main"},
      {"id": "STAGE", "name": "Staging", "nextStageId": "PROD", "branchName": "staging"}
    ]
  }
}' > "$TMP/good.json"

printf '%s\n' '{
  "status": 0,
  "result": {
    "id": "PIPE1",
    "connectedProjects": [{"id": "PROJ1"}],
    "stages": [
      {"id": "A", "nextStageId": null, "branchName": "a"},
      {"id": "B", "nextStageId": null, "branchName": "b"}
    ]
  }
}' > "$TMP/two-roots.json"

printf '%s\n' '{
  "status": 0,
  "result": {
    "id": "PIPE1",
    "connectedProjects": [{"id": "PROJ1"}],
    "stages": [
      {"id": "STAGE", "nextStageId": "PROD", "branchName": null},
      {"id": "PROD", "nextStageId": null, "branchName": "main"}
    ]
  }
}' > "$TMP/no-branch.json"

echo "== topology-derived landing branch =="
LANDING=$(bash "$RESOLVER" --input "$TMP/good.json" --pipeline-id PIPE1 --project-id PROJ1)
check_eq "uses linked-list root, not array order" staging "$LANDING"
check_fail "rejects a different pipeline" bash "$RESOLVER" --input "$TMP/good.json" --pipeline-id PIPE2 --project-id PROJ1
check_fail "rejects a project not attached to the pipeline" bash "$RESOLVER" --input "$TMP/good.json" --pipeline-id PIPE1 --project-id PROJ2
check_fail "rejects multiple topology roots" bash "$RESOLVER" --input "$TMP/two-roots.json" --pipeline-id PIPE1 --project-id PROJ1
check_fail "rejects a branchless first stage" bash "$RESOLVER" --input "$TMP/no-branch.json" --pipeline-id PIPE1 --project-id PROJ1

echo
echo "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
