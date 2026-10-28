#!/bin/bash
# Resolve the first promotable branch from a DevOps Center pipeline's linked stages.
#
# The first stage is the unique stage whose id is not named by any other stage's
# nextStageId. This is the same algorithm used by Salesforce's DevOps Center CLI.

set -eu

PIPELINE_ID=""
TARGET_ORG=""
PROJECT_ID=""
INPUT=""

die() { printf 'resolve-devops-landing.sh: %s\n' "$*" >&2; exit 1; }

while [ $# -gt 0 ]; do
  case "$1" in
    --pipeline-id) PIPELINE_ID="$2"; shift ;;
    --target-org)  TARGET_ORG="$2"; shift ;;
    --project-id)  PROJECT_ID="$2"; shift ;;
    --input)       INPUT="$2"; shift ;;
    -h|--help)
      sed -n '1,18p' "$0"
      exit 0
      ;;
    *) die "unknown argument: $1" ;;
  esac
  shift
done

command -v jq >/dev/null 2>&1 || die "jq is required"

TMP=""
cleanup() { [ -z "$TMP" ] || rm -f "$TMP"; }
trap cleanup EXIT

if [ -n "$INPUT" ]; then
  [ -f "$INPUT" ] || die "input file does not exist: $INPUT"
  PAYLOAD="$INPUT"
else
  [ -n "$PIPELINE_ID" ] || die "--pipeline-id is required"
  [ -n "$TARGET_ORG" ] || die "--target-org is required"
  command -v sf >/dev/null 2>&1 || die "sf CLI is required"
  TMP=$(mktemp "${TMPDIR:-/tmp}/sfds-pipeline.XXXXXX") || die "could not create a temporary file"
  sf devops pipeline get --pipeline-id "$PIPELINE_ID" --target-org "$TARGET_ORG" --json > "$TMP" \
    || die "could not read pipeline $PIPELINE_ID from $TARGET_ORG"
  PAYLOAD="$TMP"
fi

jq -er --arg expectedPipeline "$PIPELINE_ID" --arg project "$PROJECT_ID" '
  if ((.status // 0) != 0) then error("pipeline query did not succeed") else . end
  | .result as $result
  | if ($result | type) != "object" then error("pipeline result is missing") else . end
  | if ($result | .stages | type) != "array" or ($result.stages | length) == 0
      then error("pipeline has no stages") else . end
  | if ($expectedPipeline != "" and ($result.id // "") != "" and $expectedPipeline != ($result.id // ""))
      then error("pipeline response does not match the requested pipeline id") else . end
  | if ($project != "" and
        ([$result.connectedProjects[]?.id] | index($project)) == null)
      then error("project is not attached to this pipeline") else . end
  | ($result.stages) as $stages
  | ([$stages[].nextStageId | select(type == "string" and length > 0)]) as $nextIds
  | ([$stages[] | select(.id as $id | ($nextIds | index($id)) == null)]) as $roots
  | if ($roots | length) != 1
      then error("pipeline topology must have exactly one first stage")
    elif (($roots[0].branchName // "") | length) == 0
      then error("the first pipeline stage has no branch")
    else $roots[0].branchName
    end
' "$PAYLOAD" 2>/dev/null || die "could not derive one landing branch from the pipeline topology"
