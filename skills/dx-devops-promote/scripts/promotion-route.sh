#!/bin/bash
set -u

CURRENT_STAGE_ID=""
TARGET_STAGE_ID=""
FIRST_STAGE_ID=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --current-stage-id) CURRENT_STAGE_ID=${2-}; shift 2 ;;
    --target-stage-id) TARGET_STAGE_ID=${2-}; shift 2 ;;
    --first-stage-id) FIRST_STAGE_ID=${2-}; shift 2 ;;
    *) printf 'BLOCKED: unknown argument %s\n' "$1" >&2; exit 2 ;;
  esac
done

[ -n "$TARGET_STAGE_ID" ] || { echo 'BLOCKED: --target-stage-id is required.' >&2; exit 2; }
[ -n "$FIRST_STAGE_ID" ] || { echo 'BLOCKED: --first-stage-id is required.' >&2; exit 2; }

if [ -z "$CURRENT_STAGE_ID" ]; then
  if [ "$TARGET_STAGE_ID" = "$FIRST_STAGE_ID" ]; then
    printf '{"action":"skip","reason":"development WI entering first linked stage without PipelineStageId"}\n'
    exit 0
  fi
  echo 'BLOCKED: WI has no PipelineStageId and target is not the first linked stage; verify topology and WI state.' >&2
  exit 1
fi

if [ "$CURRENT_STAGE_ID" = "$TARGET_STAGE_ID" ]; then
  echo 'BLOCKED: current and target PipelineStageId are identical; no one-off preparation route exists.' >&2
  exit 1
fi

printf '{"action":"prepare","reason":"one-off promotion between existing pipeline stages"}\n'
