#!/bin/bash
set -u

HERE=$(cd "$(dirname "$0")" && pwd)
PREFLIGHT="$HERE/../scripts/preflight.sh"
ROUTE="$HERE/../scripts/promotion-route.sh"
TMP=${ESTATE_TEST_OUTPUT:-}
if [ -z "$TMP" ]; then
  TMP=$(mktemp -d "${TMPDIR:-/tmp}/devops-promote-test.XXXXXX") || exit 1
fi
printf 'Retained test files: %s\n' "$TMP"
FAKE="$TMP/sf"

write_sf() {
  local version=$1 include_commands=$2 include_flag=$3
  cat > "$FAKE" <<EOF
#!/bin/bash
[ "\${SCENARIO:-ok}" != missing ] || exit 1
cat <<'JSON'
[{"version":"$version","commandIDs":$include_commands,"commands":[{"id":"devops:promote","flags":$include_flag}]}]
JSON
EOF
  chmod +x "$FAKE"
}

PASS=0; FAIL=0
expect() {
  local want=$1 label=$2; shift 2
  local n=$((PASS+FAIL+1))
  cp "$FAKE" "$TMP/fake-$n.sh"
  "$@" >"$TMP/out-$n" 2>&1; local rc=$? got=pass
  [ "$rc" -ne 0 ] && got=fail
  if [ "$got" = "$want" ]; then PASS=$((PASS+1)); printf 'PASS %s\n' "$label"
  else FAIL=$((FAIL+1)); printf 'FAIL %s\n' "$label"; cat "$TMP/out-$n"; fi
}

write_sf 2.2.0 '["devops:promotion:validate","devops:promote","devops:work-item:prepare","devops:promotion:complete"]' '{"skip-validation":{}}'
expect pass 'supported version and capabilities' env SF_BIN="$FAKE" bash "$PREFLIGHT"
expect fail 'missing plugin' env SCENARIO=missing SF_BIN="$FAKE" bash "$PREFLIGHT"

write_sf 1.4.1 '["devops:promote","devops:work-item:prepare","devops:promotion:complete"]' '{}'
expect fail 'obsolete plugin' env SF_BIN="$FAKE" bash "$PREFLIGHT"

write_sf 2.2.0 '["devops:promotion:validate","devops:promote","devops:work-item:prepare","devops:promotion:complete"]' '{}'
expect fail 'missing skip-validation capability' env SF_BIN="$FAKE" bash "$PREFLIGHT"

expect pass 'first-stage development WI skips prepare' bash -c \
  '"$1" --current-stage-id "" --target-stage-id first --first-stage-id first | grep -q '"'"'"action":"skip"'"'"'' _ "$ROUTE"
expect pass 'existing-stage one-off routes prepare' bash -c \
  '"$1" --current-stage-id first --target-stage-id uat --first-stage-id first | grep -q '"'"'"action":"prepare"'"'"'' _ "$ROUTE"
expect fail 'stage-less WI cannot skip to later stage' bash "$ROUTE" \
  --current-stage-id "" --target-stage-id uat --first-stage-id first

printf '%s passed, %s failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
