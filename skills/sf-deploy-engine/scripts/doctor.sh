#!/usr/bin/env bash
#
# doctor.sh — is this pipeline actually healthy? Read-only.
#
#   doctor.sh            full report
#   doctor.sh --ready    only the promotion queue (what is waiting to ship)
#   doctor.sh --brief    one line per environment
#
# WHY THIS EXISTS
# ---------------
# The engine's failure modes do not look like failures. A pipeline.yml merged
# without a redeploy runs the OLD config indefinitely and every deploy succeeds.
# A deployed/<branch> tag left at the wrong SHA makes the next delta enormous or
# empty, and both look like the engine working. board: [jira] with an unmounted
# token renders an empty board, which reads as "nothing to ship". An environment
# frozen overnight is silent until someone opens the dashboard.
#
# So the question this answers is not "is the engine up" but "is what the engine
# believes still true".
#
# Exit codes: 0 clean, 1 problems found. Judgment items never affect the exit
# code; they are for a human to read.
#
# Env:
#   ENGINE_URL   base URL. Falls back to `engine_url:` in pipeline.yml.
#   SFDE_TOKEN       explicit token for this endpoint.
#   SFDE_TOKEN_FILE  explicit absolute token file; no shared default is read.
#
# Dependencies: bash, git, curl, python3 (stdlib). gh is optional and only used
# for repo-settings checks. No jq, no npm, no yq.

set -u

MODE="full"
case "${1:-}" in
  --ready) MODE="ready" ;;
  --brief) MODE="brief" ;;
  -h|--help) sed -n '2,/^set -u/p' "$0" | sed 's/^# \{0,1\}//; s/^#$//' | sed '$d'; exit 0 ;;
  "") ;;
  *) printf 'doctor.sh: unknown option %s\n' "$1" >&2; exit 2 ;;
esac

PROBLEMS=0
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

ok()   { printf '  ok    %s\n' "$*"; }
bad()  { printf '  FAIL  %s\n' "$*"; PROBLEMS=$((PROBLEMS + 1)); }
warn() { printf '  warn  %s\n' "$*"; }
note() { printf '        %s\n' "$*"; }
sect() { printf '\n%s\n' "$*"; }

# macOS ships no `timeout`. An unauthenticated or misconfigured curl can block on
# a socket, and a diagnostic that hangs gets killed and then nothing is verified.
with_timeout() {
  local secs="$1"; shift
  if command -v perl >/dev/null 2>&1; then
    perl -e 'alarm shift; exec @ARGV or exit 127' "$secs" "$@" 2>/dev/null
  else
    "$@" 2>/dev/null
  fi
}

# ── locate pipeline.yml ───────────────────────────────────────────────────────
find_pipeline() {
  [ -f pipeline.yml ] && { echo pipeline.yml; return; }
  local top; top=$(git rev-parse --show-toplevel 2>/dev/null || true)
  [ -n "$top" ] && [ -f "$top/pipeline.yml" ] && echo "$top/pipeline.yml"
}
PIPELINE_FILE=$(find_pipeline || true)

if [ -z "$PIPELINE_FILE" ]; then
  printf 'doctor.sh: no pipeline.yml found.\n\n' >&2
  printf 'This is not an engine-managed repo. The local loop against a single org\n' >&2
  printf 'is sf-delivery-standards, not this skill.\n' >&2
  exit 2
fi

# ── pipeline.yml parsing ──────────────────────────────────────────────────────
#
# awk rather than a YAML parser, and the parsers below are lifted from the engine
# repo's own scripts/ready-to-ship and scripts/env-status. This must run in a
# client repo with no toolchain: no yq, no npm, no python yaml package. It
# assumes the conventional 2-space nesting these configs are written with, and
# every consumer below degrades to a warning rather than a wrong answer when a
# parse comes back empty.

read -r -d '' ENV_AWK <<'AWK' || true
{ line=$0; sub(/#.*/,"",line) }
line ~ /^[A-Za-z_]/ { inenv=(line ~ /^environments:[ \t]*$/); curenv=""; next }
inenv && line ~ /^[ \t]+[A-Za-z_][A-Za-z0-9_.-]*:[ \t]*$/ {
  key=line; sub(/:[ \t]*$/,"",key); sub(/^[ \t]+/,"",key); curenv=key; next
}
inenv && curenv!="" && line ~ /^[ \t]+branch:/ {
  v=line; sub(/^.*branch:[ \t]*/,"",v); gsub(/[ \t"']/,"",v)
  if (v!="") print curenv "\t" v
}
AWK

read -r -d '' TIER_AWK <<'AWK' || true
{ line=$0; sub(/#.*/,"",line) }
line ~ /^[A-Za-z_]/ { inenv=(line ~ /^environments:[ \t]*$/); curenv=""; next }
inenv && line ~ /^[ \t]+[A-Za-z_][A-Za-z0-9_.-]*:[ \t]*$/ {
  key=line; sub(/:[ \t]*$/,"",key); sub(/^[ \t]+/,"",key); curenv=key; next
}
inenv && curenv!="" && line ~ /^[ \t]+tier:/ {
  v=line; sub(/^.*tier:[ \t]*/,"",v); gsub(/[ \t"']/,"",v)
  if (v!="") print curenv "\t" v
}
AWK

read -r -d '' EDGE_AWK <<'AWK' || true
function flush(   i){ for(i=2;i<=np;i++) print pe[i-1] "\t" pe[i]; np=0 }
{ line=$0; sub(/#.*/,"",line) }
line ~ /^[A-Za-z_]/ {
  if (mode=="path") flush()
  s=line; sub(/:.*/,"",s)
  in_prom=(s=="promotions"); in_routes=(s=="routes"); mode=""; from=""
  next
}
in_prom {
  if (line ~ /from:/){ from=line; sub(/^.*from:[ \t]*/,"",from); gsub(/[ \t"',]/,"",from) }
  else if (line ~ /to:/){ to=line; sub(/^.*to:[ \t]*/,"",to); gsub(/[ \t"',]/,"",to);
    if(from!=""&&to!="") print from "\t" to }
  next
}
in_routes {
  if (line ~ /path:[ \t]*\[/){
    if (mode=="path") flush()
    l=line; sub(/^.*\[/,"",l); sub(/\].*/,"",l); np=0
    n=split(l,a,","); for(i=1;i<=n;i++){ v=a[i]; gsub(/[ \t"']/,"",v); if(v!=""){np++; pe[np]=v} }
    flush(); mode=""; next
  }
  if (line ~ /path:[ \t]*$/){ if(mode=="path") flush(); mode="path"; np=0; next }
  if (mode=="path"){
    if (line ~ /^[ \t]*-[ \t]*/){ v=line; sub(/^[ \t]*-[ \t]*/,"",v); gsub(/[ \t"',]/,"",v);
      if(v!=""){np++; pe[np]=v}; next }
    else if (line ~ /[^ \t]/){ flush(); mode="" }
  }
}
END { if (mode=="path") flush() }
AWK

ENV_ROWS=$(awk "$ENV_AWK"  "$PIPELINE_FILE" 2>/dev/null || true)
TIER_ROWS=$(awk "$TIER_AWK" "$PIPELINE_FILE" 2>/dev/null || true)
EDGE_ROWS=$(awk "$EDGE_AWK" "$PIPELINE_FILE" 2>/dev/null || true)

branch_of() {
  local b; b=$(printf '%s\n' "$ENV_ROWS" | awk -F'\t' -v n="$1" '$1==n{print $2; exit}')
  [ -n "$b" ] && echo "$b" || echo "$1"
}
tier_of() {
  local t; t=$(printf '%s\n' "$TIER_ROWS" | awk -F'\t' -v n="$1" '$1==n{print $2; exit}')
  [ -n "$t" ] && echo "$t" || echo "pipeline"
}
# origin FIRST, deliberately. The question this script asks is "what will the
# engine deploy", and the engine works from origin. A local checkout of an
# environment branch is frequently months stale, and preferring it turns every
# tag comparison below into a confident wrong answer.
resolve_ref() {
  local n=$1 r
  for r in "refs/remotes/origin/$n" "refs/heads/$n" "$n"; do
    git rev-parse -q --verify "$r^{commit}" >/dev/null 2>&1 && { echo "$r"; return 0; }
  done
  return 1
}

# `git fetch --tags` REFUSES to move a tag that already exists locally, prints
# "would clobber existing tag" to stderr, and still exits 0. deployed/<branch> is
# force-moved by the engine on every deploy, so without --force every tag read
# below is stale and every comparison is silently wrong — while the fetch reports
# success. This is the exact class of failure this script exists to catch, so it
# must not have it.
fetch_refs() {
  local err; err=$(git fetch --quiet --tags --prune --force origin 2>&1)
  if [ -n "$err" ] && printf '%s' "$err" | grep -qi 'rejected\|error\|fatal'; then
    warn "git fetch reported: $(printf '%s' "$err" | head -1)"
    note "Tag and branch data below may be stale."
  fi
}

# ── patch-equivalence core (from the engine repo's scripts/ready-to-ship) ──────
#
# Promotions are cherry-picks, so a promoted merge gets a NEW sha downstream and
# `git log D..U` reports it as pending forever. `--cherry-pick` cannot help:
# git assigns merge commits a null patch-id, so it can never match a merge
# against its flattened downstream twin. The patch-id of a merge's FIRST-PARENT
# diff does equal the patch-id of its cherry-pick, and that is what we compare.
compute_unpromoted() {
  local D=$1 U=$2 mb dpids c pid subj
  PENDING_LINES=""; EXCLUDED_COUNT=0
  mb=$(git merge-base "$D" "$U" 2>/dev/null) || return 1
  dpids=$(git rev-list "$mb..$D" 2>/dev/null | while read -r c; do
      git rev-parse -q --verify "$c^" >/dev/null 2>&1 || continue
      git diff "$c^" "$c" | git patch-id --stable | awk '{print $1}'
    done)
  while read -r c; do
    [ -z "$c" ] && continue
    pid=$(git diff "$c^" "$c" 2>/dev/null | git patch-id --stable | awk '{print $1}')
    if [ -n "$pid" ] && [ -n "$dpids" ] && printf '%s\n' "$dpids" | grep -qxF "$pid"; then
      EXCLUDED_COUNT=$((EXCLUDED_COUNT + 1))
    else
      subj=$(git log -1 --format=%s "$c" 2>/dev/null)
      PENDING_LINES+="${c}"$'\t'"${subj}"$'\n'
    fi
  done < <(git rev-list --first-parent --merges "$D..$U" 2>/dev/null)
}

# ── engine URL + token ────────────────────────────────────────────────────────
ENGINE=""
if [ -n "${ENGINE_URL:-}" ]; then
  ENGINE="${ENGINE_URL%/}"
else
  ENGINE=$(grep -E '^[[:space:]]*engine_url:' "$PIPELINE_FILE" | head -1 \
    | sed -E 's/^[^:]*:[[:space:]]*//; s/[[:space:]]*$//; s/^"//; s/"$//')
  ENGINE="${ENGINE%/}"
fi

TOKEN="${SFDE_TOKEN:-}"
if [ -z "$TOKEN" ]; then
  case "${SFDE_TOKEN_FILE:-}" in
    /*) [ ! -r "$SFDE_TOKEN_FILE" ] || TOKEN=$(tr -d '\n' < "$SFDE_TOKEN_FILE") ;;
  esac
fi

STATUS_JSON=""
TOPOLOGY_JSON=""

api_get() { # path -> body on stdout, http code in API_CODE
  local body
  body=$(with_timeout 20 curl -sS -o /dev/stdout -w '\n%{http_code}' \
    -H "Authorization: Bearer $TOKEN" "$ENGINE$1" 2>/dev/null)
  API_CODE=$(printf '%s' "$body" | tail -1)
  printf '%s' "$body" | sed '$d'
}

# ═══════════════════════════════════════════════════════════════════════════════
# 1. Config
# ═══════════════════════════════════════════════════════════════════════════════
check_config() {
  sect "Config ($PIPELINE_FILE)"

  if [ -z "$ENV_ROWS" ]; then
    bad "could not parse any environments out of pipeline.yml"
    note "Either the file is malformed or it uses non-standard indentation."
    note "Everything below that depends on the environment list is unreliable."
    return
  fi
  ok "$(printf '%s\n' "$ENV_ROWS" | wc -l | tr -d ' ') environment(s): $(printf '%s\n' "$ENV_ROWS" | awk -F'\t' '{printf "%s ", $1}')"

  if grep -qE '^[[:space:]]*routes:' "$PIPELINE_FILE"; then
    ok "routes: topology declared"
  elif grep -qE '^[[:space:]]*promotions:' "$PIPELINE_FILE"; then
    warn "using the deprecated promotions: shape"
    note "It still loads, translated into a synthetic 'standard' route, and warns"
    note "at boot. It cannot express hotfix entry points or back_merge. Migrate."
  else
    warn "no routes: or promotions: — this pipeline has no promotion topology"
    note "Deploys still work; /api/release will refuse everything."
  fi

  if [ -z "$ENGINE" ]; then
    bad "no engine_url: in pipeline.yml and no ENGINE_URL set"
    note "The VS Code extension and every script here discover the engine from it."
  else
    ok "engine_url: $ENGINE"
  fi

  # tier: sandbox rows are visibility only. Flagged because a reader who sees one
  # in pipeline.yml reasonably assumes the engine deploys it, and it does not.
  local sb
  sb=$(printf '%s\n' "$TIER_ROWS" | awk -F'\t' '$2=="sandbox"{printf "%s ", $1}')
  [ -n "$sb" ] && note "tier: sandbox (board visibility + release source only, never deployed): $sb"

  # Jira board is a credentialed read. The engine refuses to START without the
  # three config keys, so a RUNNING engine with an empty board is a token problem.
  if grep -qE '^[[:space:]]*board:.*jira' "$PIPELINE_FILE"; then
    local miss=""
    grep -qE '^[[:space:]]*base_url:' "$PIPELINE_FILE" || miss="$miss base_url"
    grep -qE '^[[:space:]]*email:'    "$PIPELINE_FILE" || miss="$miss email"
    grep -qE '^[[:space:]]*projects:' "$PIPELINE_FILE" || miss="$miss projects"
    if [ -n "$miss" ]; then
      bad "board: [jira] is missing:$miss — the engine refuses to start without these"
    else
      ok "jira board config complete (token must be mounted as JIRA_API_TOKEN)"
    fi
  fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# 2. Reachability and auth
# ═══════════════════════════════════════════════════════════════════════════════
check_engine() {
  sect "Engine"
  [ -z "$ENGINE" ] && { bad "no engine URL to check"; return; }

  local health
  health=$(with_timeout 15 curl -sS -o /dev/null -w '%{http_code}' "$ENGINE/health" 2>/dev/null)
  if [ "$health" = "200" ]; then
    ok "/health 200"
  else
    bad "/health returned '${health:-no response}'"
    note "The service is down, or the URL is wrong. Nothing below can be checked."
    return
  fi

  if [ -z "$TOKEN" ]; then
    warn "no CLI token — API checks skipped"
    note "Mint one: scripts/engine.sh login"
    return
  fi

  STATUS_JSON=$(api_get /api/status)
  case "$API_CODE" in
    200) ok "/api/status 200 (authenticated)" ;;
    401)
      bad "/api/status 401 — token missing, expired (30 days) or SESSION_SECRET rotated"
      note "Re-run: scripts/engine.sh login"
      STATUS_JSON=""; return ;;
    503)
      bad "/api/status 503"
      note "If EVERY route but /health 503s, the Workspace SSO gate is failing closed"
      note "because GOOGLE_OAUTH_CLIENT_ID / _SECRET / SESSION_SECRET are unset on the"
      note "service. That is a provisioning fix. If only SOME /api routes 503, this is"
      note "EXECUTION_MODE=scale-to-zero and is expected."
      STATUS_JSON=""; return ;;
    *) bad "/api/status returned $API_CODE"; STATUS_JSON=""; return ;;
  esac

  local paused
  paused=$(printf '%s' "$STATUS_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("paused"))' 2>/dev/null)
  if [ "$paused" = "True" ]; then
    bad "the engine is PAUSED — webhooks are acknowledged and not processed"
    note "A paused engine is indistinguishable from a quiet one on GitHub."
    note "Resume: scripts/engine.sh resume"
  else
    ok "not paused"
  fi

  TOPOLOGY_JSON=$(api_get /api/topology)
  [ "$API_CODE" = "200" ] || TOPOLOGY_JSON=""
}

# ═══════════════════════════════════════════════════════════════════════════════
# 3. Config drift — the one that catches "merged it and nothing happened"
# ═══════════════════════════════════════════════════════════════════════════════
check_drift() {
  sect "Config vs running engine"
  if [ -z "$TOPOLOGY_JSON" ]; then
    warn "no /api/topology — drift not checked"
    return
  fi

  local live disk
  live=$(printf '%s' "$TOPOLOGY_JSON" | python3 -c '
import json,sys
d = json.load(sys.stdin)
print(" ".join(sorted(e["name"] for e in d.get("environments", []))))' 2>/dev/null)
  disk=$(printf '%s\n' "$ENV_ROWS" | awk -F'\t' '{print $1}' | sort | tr '\n' ' ' | sed 's/ $//')

  if [ "$live" = "$disk" ]; then
    ok "the engine's environment list matches pipeline.yml"
  else
    bad "the engine is running a DIFFERENT config than pipeline.yml on disk"
    note "engine: $live"
    note "disk:   $disk"
    note "The engine reads pipeline.yml ONCE, at bootstrap. Merging a config change"
    note "is necessary and not sufficient — redeploy or restart the service."
  fi

  local liveedges diskedges
  liveedges=$(printf '%s' "$TOPOLOGY_JSON" | python3 -c '
import json,sys
d = json.load(sys.stdin)
print(" ".join(sorted(f"{e[\"from\"]}->{e[\"to\"]}" for e in d.get("edges", {}).get("forward", []))))' 2>/dev/null)
  diskedges=$(printf '%s\n' "$EDGE_ROWS" | awk -F'\t' 'NF==2{print $1"->"$2}' | sort | tr '\n' ' ' | sed 's/ $//')
  if [ -n "$diskedges" ] && [ "$liveedges" != "$diskedges" ]; then
    bad "promotion edges differ between the engine and pipeline.yml"
    note "engine: ${liveedges:-none}"
    note "disk:   $diskedges"
  elif [ -n "$diskedges" ]; then
    ok "promotion edges match"
  fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# 4. Per-environment state
# ═══════════════════════════════════════════════════════════════════════════════
check_environments() {
  sect "Environments"
  fetch_refs

  local name branch tier state reason tagref taghead brhead
  while IFS=$'\t' read -r name branch; do
    [ -z "$name" ] && continue
    tier=$(tier_of "$name")

    if [ "$tier" = "sandbox" ]; then
      printf '  --    %s (tier: sandbox — board visibility only, no worker, no tag)\n' "$name"
      continue
    fi

    state=""; reason=""
    if [ -n "$STATUS_JSON" ]; then
      state=$(printf '%s' "$STATUS_JSON" | NAME="$name" python3 -c '
import json,os,sys
e = json.load(sys.stdin).get("environments", {}).get(os.environ["NAME"])
print(e.get("state","") if e else "")' 2>/dev/null)
      reason=$(printf '%s' "$STATUS_JSON" | NAME="$name" python3 -c '
import json,os,sys
e = json.load(sys.stdin).get("environments", {}).get(os.environ["NAME"])
print((e.get("freezeReason") or "") if e else "")' 2>/dev/null)
    fi

    case "$state" in
      FROZEN)
        bad "$name is FROZEN"
        [ -n "$reason" ] && note "reason: $reason"
        note "Read the reason before acting. A metadata failure needs a fix-forward or a"
        note "rollback; retrying identical metadata costs another full test run." ;;
      DEPLOYING) ok "$name DEPLOYING" ;;
      SETTLED)   ok "$name SETTLED" ;;
      "")        warn "$name — no engine state available" ;;
      *)         warn "$name state '$state'" ;;
    esac

    # deployed/<branch> is the engine's statement about the org. A missing tag on
    # a pipeline environment means the engine has never successfully deployed it,
    # or bootstrap was skipped.
    if ! taghead=$(git rev-parse -q --verify "refs/tags/deployed/$branch^{commit}" 2>/dev/null); then
      bad "$name: no deployed/$branch tag"
      note "Either the engine has never deployed here, or provisioning skipped the"
      note "bootstrap step. That step has no error message of its own."
      continue
    fi
    if ! tagref=$(resolve_ref "$branch"); then
      warn "$name: branch '$branch' not found locally"
      continue
    fi
    brhead=$(git rev-parse "$tagref")

    if [ "$taghead" = "$brhead" ]; then
      ok "$name: org matches $branch (${brhead:0:9})"
    else
      local ahead behind
      ahead=$(git rev-list --count "$taghead..$brhead" 2>/dev/null || echo '?')
      behind=$(git rev-list --count "$brhead..$taghead" 2>/dev/null || echo '?')

      if [ "$behind" != "0" ] && [ "$behind" != "?" ]; then
        # The tag is not an ancestor of the branch. The engine only ever advances
        # the tag to a commit it deployed FROM the branch, so this means the
        # branch was rewritten, or the tag was moved by hand, or these refs are
        # not from the same history at all.
        bad "$name: deployed/$branch is $behind commit(s) NOT on $branch"
        note "The tag is not an ancestor of the branch. Either the branch was"
        note "force-pushed/rewritten, or the tag was moved manually. Do not 'fix'"
        note "this by moving the tag until you know which — the tag is the only"
        note "record of what is actually in the org."
      elif [ "$state" = "SETTLED" ]; then
        bad "$name: SETTLED but $branch is $ahead commit(s) ahead of deployed/$branch"
        note "A settled environment whose branch is ahead of its tag is an anomaly: a"
        note "deploy failed silently, was lost, or someone pushed without a webhook."
      elif [ -z "$state" ]; then
        # No engine state (no token, or the API is unreachable) and the branch is
        # ahead of its tag. "Deploy in flight" is a GUESS, and it is the
        # optimistic one — a frozen environment looks identical from git alone.
        # Say unknown; the whole point of this script is not to report a verdict
        # it cannot support.
        warn "$name: $branch is $ahead commit(s) ahead of deployed/$branch, engine state unknown"
        note "Could be a deploy in flight or a freeze — git cannot tell them apart."
        note "Mint a token (scripts/engine.sh login) or check the dashboard."
      else
        note "$name: $branch is $ahead commit(s) ahead of deployed/$branch (deploy in flight)"
      fi
    fi

    # Informational: a stale local checkout is normal and harmless, but it is
    # also the reason a hand-run `git log` disagrees with everything here.
    local localhead
    if localhead=$(git rev-parse -q --verify "refs/heads/$branch^{commit}" 2>/dev/null); then
      if [ "$localhead" != "$brhead" ]; then
        note "$name: your local $branch is not origin/$branch — the checks above used origin"
      fi
    fi
  done <<<"$ENV_ROWS"
}

# ═══════════════════════════════════════════════════════════════════════════════
# 5. Promotion queue
# ═══════════════════════════════════════════════════════════════════════════════
check_ready() {
  sect "Ready to ship"
  if [ -z "$EDGE_ROWS" ]; then
    note "no promotion edges configured"
    return
  fi
  fetch_refs

  local u d uBr dBr uRef dRef n sha subj pr
  while IFS=$'\t' read -r u d; do
    [ -z "$u" ] && continue
    uBr=$(branch_of "$u"); dBr=$(branch_of "$d")
    printf '\n  %s -> %s  (%s -> %s)\n' "$u" "$d" "$uBr" "$dBr"
    uRef=$(resolve_ref "$uBr") || { note "branch '$uBr' not found locally"; continue; }
    dRef=$(resolve_ref "$dBr") || { note "branch '$dBr' not found locally"; continue; }

    compute_unpromoted "$dRef" "$uRef"
    n=0
    if [ -n "$PENDING_LINES" ]; then
      while IFS=$'\t' read -r sha subj; do
        [ -z "$sha" ] && continue
        pr=$(printf '%s' "$subj" | sed -n 's/.*[Mm]erge pull request #\([0-9][0-9]*\).*/\1/p' | head -1)
        [ -z "$pr" ] && pr="--"
        printf '    PR #%-5s %s  (%s)\n' "$pr" "$subj" "${sha:0:9}"
        n=$((n + 1))
      done <<<"$PENDING_LINES"
    fi
    if [ "$n" -eq 0 ]; then
      printf '    nothing pending\n'
    else
      printf '    %d commit(s) ready to promote\n' "$n"
    fi
    [ "${EXCLUDED_COUNT:-0}" -gt 0 ] && printf '    (%d already promoted by cherry-pick, excluded by patch-equivalence)\n' "$EXCLUDED_COUNT"
  done <<<"$EDGE_ROWS"
}

# ═══════════════════════════════════════════════════════════════════════════════
# 6. Repo settings
# ═══════════════════════════════════════════════════════════════════════════════
check_repo() {
  sect "Repo settings"
  command -v gh >/dev/null 2>&1 || { warn "gh not installed — repo settings not checked"; return; }

  local slug json sq rb
  slug=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null)
  [ -z "$slug" ] && { warn "not a GitHub repo, or gh is not authenticated"; return; }

  json=$(with_timeout 20 gh api "repos/$slug" 2>/dev/null)
  [ -z "$json" ] && { warn "could not read repo settings"; return; }

  sq=$(printf '%s' "$json" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("allow_squash_merge"))' 2>/dev/null)
  rb=$(printf '%s' "$json" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("allow_rebase_merge"))' 2>/dev/null)

  if [ "$sq" = "True" ] || [ "$rb" = "True" ]; then
    bad "squash and/or rebase merging is enabled on $slug"
    note "git revert -m 1 (rollback) and git cherry-pick -m 1 (promotion) both need"
    note "real merge commits. A squashed merge is not selectively promotable or"
    note "cleanly revertible, and the UI button is not covered by any agent-side hook."
    note "  gh api repos/$slug -X PATCH -f allow_squash_merge=false -f allow_rebase_merge=false"
  else
    ok "squash and rebase merging disabled"
  fi

}


# ═══════════════════════════════════════════════════════════════════════════════
# 7. The engine's own guards
# ═══════════════════════════════════════════════════════════════════════════════
#
# Its own section, NOT part of the repo-settings check, because that one returns
# early when `gh` is missing or the remote is not GitHub. Nesting the guard audit
# under it meant a GitLab repo — or any machine without gh — skipped the whole
# thing silently while still printing a verdict. An audit that quietly does not
# run is the failure this script exists to make visible.
check_guards() {
  sect "Engine guards"
  # The engine's own guards. Installed at user level so a worktree agent cannot
  # edit them out of its own branch, and inert in any repo with no pipeline.yml.
  local eh="$HOME/.estate-engine/hooks" missing="" h reg
  for h in guard-engine-deploy.sh guard-engine-merge.sh; do
    [ -x "$eh/$h" ] || missing="$missing $h"
  done

  if [ -n "$missing" ]; then
    bad "engine guards not installed:$missing"
    note "Nothing is stopping a manual deploy to a pipeline org, or a hand merge"
    note "into an environment branch."
    note "  scripts/init.sh"
    return
  fi

  reg=$(with_timeout 10 python3 "$SCRIPT_DIR/count_registered_hooks.py" 2>/dev/null)
  if [ "${reg:-0}" -ge 2 ]; then
    ok "engine guards installed and registered"
    note "Registered is not the same as firing: hooks load at SESSION START, so a"
    note "session older than the install runs without them. This check cannot see"
    note "that, and neither can you from inside such a session."

    # ── A SECOND, COMPETING HOOK STACK ────────────────────────────────────────
    #
    # This is the check whose absence let an earlier run of this script report
    # "clean" over a repo where the engine guards were being shadowed.
    #
    # A repo-level .claude/hooks/ deploy or merge guard is registered in the
    # REPO's settings.json, and one block short-circuits the tool call — so
    # whichever stack refuses first is the only one whose reasoning anyone sees.
    # Two stacks that mostly agree are worse than one, because the disagreements
    # are invisible until the day they matter.
    local repo_guards=""
    for h in guard-deploy-tests.sh guard-sf-deploy.sh guard-pr-merge.sh guard-sf-flags.sh; do
      [ -f ".claude/hooks/$h" ] && repo_guards="$repo_guards $h"
    done
    if [ -n "$repo_guards" ]; then
      bad "a second, repo-level hook stack is present:$repo_guards"
      note "Those live in .claude/hooks/ and are registered in this repo's own"
      note "settings.json, so they run alongside the engine guards and can refuse"
      note "first. The engine guard's reasoning is then never shown."
      note ""
      note "It also matters WHICH one wins. The repo-level deploy guard checks the"
      note "command shape and the current branch; it does not resolve the target"
      note "org. A deploy with no --target-org flag, from a clean non-environment"
      note "branch, with the default org pointed at a pipeline org, passes it."
      note "guard-engine-deploy.sh catches that case. Shadowed, it cannot."
      note ""
      note "Pick one lineage. Keep sf-delivery-standards for the local loop and"
      note "these guards for the pipeline, and remove the repo-level copies."
    else
      ok "no competing repo-level hook stack"
    fi

    # ── REGISTRATIONS POINTING AT NOTHING ─────────────────────────────────────
    #
    # Deleting hook scripts without stripping their entries leaves Claude Code
    # running a command that does not exist. It reports
    #
    #   PreToolUse:Bash hook error
    #   Failed with non-blocking status code: /bin/sh: <path>: No such file or directory
    #
    # on every single Bash call. NON-blocking, so nothing is unsafe and nothing
    # stops — which is the problem. The stack reads as more armed than it is, and
    # the noise trains everyone to ignore hook errors, including real ones.
    #
    # This check exists because the removal that motivated it shipped exactly
    # this way: `git rm` staged the deletions, the settings.json edit was left
    # unstaged, and `git commit -m` without -a took only what was staged.
    local dangling
    dangling=$(with_timeout 10 python3 - <<'PYX' 2>/dev/null
import json, os, sys
missing = []
for path in (".claude/settings.json", ".claude/settings.local.json",
             ".codex/hooks.json", os.path.expanduser("~/.claude/settings.json"),
             os.path.expanduser("~/.codex/hooks.json")):
    try:
        with open(path) as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        continue
    for event, entries in (data.get("hooks") or {}).items():
        for entry in entries or []:
            for hook in (entry.get("hooks") or []):
                cmd = (hook.get("command") or "").strip()
                if not cmd:
                    continue
                # Only judge plain script paths; a shell one-liner is not ours to parse.
                target = cmd.split()[0]
                if "/" not in target:
                    continue
                probe = os.path.expanduser(target)
                if not os.path.exists(probe):
                    missing.append(f"{os.path.basename(path)} [{event}] {target}")
print("\n".join(missing))
PYX
)
    if [ -n "$dangling" ]; then
      bad "hook registrations point at files that do not exist:"
      printf '%s\n' "$dangling" | while IFS= read -r d; do note "  $d"; done
      note ""
      note "The agent host reports a non-blocking hook error on EVERY tool call this"
      note "matches. Nothing is unsafe, and that is the trap: the stack reads as"
      note "more armed than it is, and the noise teaches people to ignore hook"
      note "errors — including the ones that matter."
    else
      ok "no dangling hook registrations"
    fi
  else
    bad "engine guards are installed but not registered in Claude or Codex hook settings"
    note "Installed files that no event ever fires are worth nothing."
    note "  scripts/init.sh"
  fi
}

# ═══════════════════════════════════════════════════════════════════════════════

if [ "$MODE" = "ready" ]; then
  check_ready
  printf '\n'
  exit 0
fi

check_config
check_engine
check_drift
check_environments
[ "$MODE" = "full" ] && { check_ready; check_repo; }
check_guards

printf '\n'
if [ "$PROBLEMS" -eq 0 ]; then
  printf 'doctor: clean\n'
  exit 0
fi
printf 'doctor: %d problem(s)\n' "$PROBLEMS"
exit 1
