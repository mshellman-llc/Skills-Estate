#!/bin/bash
set -u

SF_BIN=${SF_BIN:-sf}
PLUGIN=@salesforce/plugin-devops-center
MIN_VERSION=2.0.0
VERIFIED_VERSION=2.2.0

die() { printf 'BLOCKED: %s\n' "$*" >&2; exit 1; }

command -v "$SF_BIN" >/dev/null 2>&1 || die "Salesforce CLI is not installed."
command -v jq >/dev/null 2>&1 || die "jq is required for DevOps Center capability inspection."

INSPECT=$($SF_BIN plugins inspect "$PLUGIN" --json 2>/dev/null) \
  || die "$PLUGIN is missing or cannot be inspected. Install or upgrade it before promotion."

ROOT='if type == "array" then .[0] else . end'
VERSION=$(printf '%s' "$INSPECT" | jq -r "($ROOT) | .version // .tag // .pjson.version // empty")
[ -n "$VERSION" ] || die "$PLUGIN did not report a version."

version_at_least() {
  local actual=${1%%-*} minimum=${2%%-*} a b c x y z
  IFS=. read -r a b c <<< "$actual"
  IFS=. read -r x y z <<< "$minimum"
  a=${a:-0}; b=${b:-0}; c=${c:-0}; x=${x:-0}; y=${y:-0}; z=${z:-0}
  [ "$a" -gt "$x" ] || { [ "$a" -eq "$x" ] && { [ "$b" -gt "$y" ] || { [ "$b" -eq "$y" ] && [ "$c" -ge "$z" ]; }; }; }
}

version_at_least "$VERSION" "$MIN_VERSION" \
  || die "$PLUGIN $VERSION is obsolete; version $MIN_VERSION or newer is required. Upgrade the plugin and rerun preflight."

for COMMAND_ID in devops:promotion:validate devops:promote devops:work-item:prepare; do
  printf '%s' "$INSPECT" | jq -e --arg id "$COMMAND_ID" \
    "($ROOT) | [.commandIDs[]?] | index(\$id) != null" >/dev/null \
    || die "$PLUGIN $VERSION does not expose $COMMAND_ID. Upgrade to a supported plugin; do not improvise another command."
done

printf '%s' "$INSPECT" | jq -e \
  "($ROOT) | any(.commands[]?; .id == \"devops:promote\" and (.flags[\"skip-validation\"] != null))" >/dev/null \
  || die "$PLUGIN $VERSION does not expose 'sf devops promote --skip-validation'. Upgrade to a supported plugin."

if [ "$VERSION" != "$VERIFIED_VERSION" ]; then
  printf 'NOTICE: %s %s passed capability checks; this skill is currently verified against %s.\n' \
    "$PLUGIN" "$VERSION" "$VERIFIED_VERSION" >&2
fi
printf 'OK: %s %s exposes promotion validate, conditional prepare, and promote --skip-validation.\n' \
  "$PLUGIN" "$VERSION"
