#!/usr/bin/env bash
#
# engine.sh — talk to an sf-deploy-engine instance from a terminal or an agent.
#
# The engine's /api/* routes sit behind Google Workspace SSO. A browser has a
# session cookie and the VS Code extension has a keychain entry; a bash process
# has neither, which is why a bare curl against /api/* returns 401 or 503 and why
# this script exists. It sends a CLI token as `Authorization: Bearer`.
#
#   ENGINE_URL   base URL. Falls back to `engine_url:` in pipeline.yml.
#   SFDE_TOKEN       explicit token for the selected endpoint.
#   SFDE_TOKEN_FILE  explicit absolute file path; no shared default is read.
#
# Mint the token once (valid 30 days):
#   engine.sh login          # prints/opens the URL, then explains the one-liner
#
# COMMANDS
#   status [ENV]                    FSM state, in-flight item and queue
#   topology                        the route DAG
#   board                           kanban payload
#   history [--env E] [--limit N]   activity feed
#   ticket REF                      trace one ticket across every deploy
#
#   retry ENV                       re-enqueue a deploy on a FROZEN environment
#   revalidate --pr N               re-validate at the PR's live head SHA
#   rollback --env E (--ticket T | --sha S) [--mode pr|direct]
#   release [--to ENV] --from ENV TICKET... [--from ENV TICKET...]
#   pause | resume
#
# Every command accepts --raw to print the response body unformatted.
#
# Dependencies: bash, curl, python3 (stdlib only). No jq, no npm.

set -euo pipefail

TOKEN_FILE="${SFDE_TOKEN_FILE:-}"
RAW=0

usage() { sed -n '2,/^set -euo/p' "$0" | sed 's/^# \{0,1\}//; s/^#$//' | sed '$d'; }

die() { printf 'engine.sh: %s\n' "$*" >&2; exit 1; }

# ── Where is the engine ───────────────────────────────────────────────────────
#
# pipeline.yml is the authority. Reading it with grep rather than a YAML parser
# is deliberate: this script must work in a client repo with no toolchain, and
# `engine_url` is a top-level scalar that never needs real parsing.
resolve_engine_url() {
  if [ -n "${ENGINE_URL:-}" ]; then printf '%s' "${ENGINE_URL%/}"; return; fi
  local f
  for f in pipeline.yml "$(git rev-parse --show-toplevel 2>/dev/null)/pipeline.yml"; do
    [ -f "$f" ] || continue
    local u
    u=$(grep -E '^[[:space:]]*engine_url:' "$f" | head -1 | sed -E 's/^[^:]*:[[:space:]]*//; s/[[:space:]]*$//; s/^"//; s/"$//')
    if [ -n "$u" ]; then printf '%s' "${u%/}"; return; fi
  done
  die "no ENGINE_URL set and no engine_url: found in pipeline.yml"
}

read_token() {
  if [ -n "${SFDE_TOKEN:-}" ]; then printf '%s' "$SFDE_TOKEN"; return; fi
  case "$TOKEN_FILE" in /*) ;; *) return 1 ;; esac
  [ -r "$TOKEN_FILE" ] && [ -f "$TOKEN_FILE" ] || return 1
  tr -d '\n' < "$TOKEN_FILE"
}

# ── HTTP ──────────────────────────────────────────────────────────────────────
#
# Status code and body are captured together so a failure can be explained
# instead of printed as a bare JSON error. The three failure modes below look
# identical to a naive caller and have completely different fixes.
call() {
  local method="$1" path="$2" body="${3:-}"
  local url token code out
  url="$(resolve_engine_url)$path"

  if ! token="$(read_token)"; then
    die "no explicitly selected CLI token. Set SFDE_TOKEN or an absolute SFDE_TOKEN_FILE for this endpoint; engine.sh login describes enrollment"
  fi

  local tmp; tmp=$(mktemp)
  # shellcheck disable=SC2064
  trap "rm -f '$tmp'" RETURN

  if [ -n "$body" ]; then
    code=$(curl -sS -o "$tmp" -w '%{http_code}' -X "$method" "$url" \
      -H "Authorization: Bearer $token" \
      -H 'Content-Type: application/json' \
      --data "$body")
  else
    code=$(curl -sS -o "$tmp" -w '%{http_code}' -X "$method" "$url" \
      -H "Authorization: Bearer $token")
  fi
  out=$(cat "$tmp")

  case "$code" in
    2*) ;;
    401)
      printf 'engine.sh: 401 unauthorized.\n\n' >&2
      printf 'The CLI token is missing, expired (they last 30 days), or was minted\n' >&2
      printf 'against a SESSION_SECRET that has since been rotated.\n\n  engine.sh login\n' >&2
      exit 1 ;;
    503)
      printf 'engine.sh: 503 from %s\n\n' "$path" >&2
      printf '%s\n\n' "$out" >&2
      printf 'Two different causes, and they are not related:\n' >&2
      printf '  * EVERY route but /health 503s -> the Workspace SSO gate is failing closed\n' >&2
      printf '    because GOOGLE_OAUTH_CLIENT_ID / _SECRET / SESSION_SECRET are unset on the\n' >&2
      printf '    service. That is a provisioning fix, not a caller-side one.\n' >&2
      printf '  * ONLY some /api routes 503, with a written reason -> EXECUTION_MODE is\n' >&2
      printf '    scale-to-zero. The thin service has no repo clone and no worker. Expected.\n' >&2
      exit 1 ;;
    *)
      printf 'engine.sh: HTTP %s from %s\n%s\n' "$code" "$path" "$out" >&2
      exit 1 ;;
  esac

  if [ "$RAW" = "1" ]; then printf '%s\n' "$out"; else
    printf '%s' "$out" | python3 -m json.tool 2>/dev/null || printf '%s\n' "$out"
  fi
}

# JSON built by python3 rather than string concatenation: ticket identifiers and
# environment names reach an endpoint that interpolates some of them into git
# commands, so nothing here hand-quotes anything.
json() { python3 -c 'import json,sys; print(json.dumps(json.loads(sys.stdin.read())))' ; }

# ── Commands ──────────────────────────────────────────────────────────────────

cmd_login() {
  local url; url="$(resolve_engine_url)/auth/login?redirect=cli"
  printf 'Open this and sign in with a Workspace account:\n\n  %s\n\n' "$url"
  printf 'Use the login flow for this endpoint. Save its token in a private endpoint-specific file (mode 600), then set SFDE_TOKEN_FILE to that absolute path. Never paste the token into chat.\n'
  printf 'The token lasts 30 days; re-run this login when a call reports 401.\n'
  if command -v open >/dev/null 2>&1; then open "$url" >/dev/null 2>&1 || true; fi
}

cmd_status() {
  local env="${1:-}"
  if [ -z "$env" ]; then call GET /api/status; return; fi
  RAW=1 call GET /api/status | python3 -c '
import json,sys
d = json.load(sys.stdin)
env = sys.argv[1]
e = d.get("environments", {}).get(env)
if e is None:
    print(f"unknown environment: {env}", file=sys.stderr)
    print("known: " + ", ".join(d.get("environments", {})), file=sys.stderr)
    sys.exit(1)
print(json.dumps({"paused": d.get("paused"), env: e}, indent=2))
' "$env"
}

cmd_retry() {
  [ $# -ge 1 ] || die "usage: engine.sh retry ENV"
  call POST "/api/retry/$1"
}

cmd_revalidate() {
  local pr=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --pr) pr="${2:-}"; shift 2 ;;
      --pr=*) pr="${1#*=}"; shift ;;
      *) die "unexpected argument: $1" ;;
    esac
  done
  [ -n "$pr" ] || die "usage: engine.sh revalidate --pr N"
  call POST /api/revalidate "$(printf '{"prNumber": %s}' "$pr" | json)"
}

cmd_rollback() {
  local env="" ticket="" sha="" mode="pr"
  while [ $# -gt 0 ]; do
    case "$1" in
      --env)    env="${2:-}"; shift 2 ;;
      --ticket) ticket="${2:-}"; shift 2 ;;
      --sha)    sha="${2:-}"; shift 2 ;;
      --mode)   mode="${2:-}"; shift 2 ;;
      *) die "unexpected argument: $1" ;;
    esac
  done
  [ -n "$env" ] || die "--env is required"
  if [ -n "$ticket" ] && [ -n "$sha" ]; then die "give exactly one of --ticket or --sha"; fi
  if [ -z "$ticket" ] && [ -z "$sha" ]; then die "give exactly one of --ticket or --sha"; fi
  case "$mode" in pr|direct) ;; *) die "--mode must be pr or direct" ;; esac

  if [ "$mode" = "direct" ]; then
    printf 'Direct rollback pushes the revert straight to %s with no validation.\n' "$env" >&2
    printf 'This is the emergency path. Ctrl-C now if you meant --mode pr.\n\n' >&2
  fi

  local body
  body=$(ENV="$env" TICKET="$ticket" SHA="$sha" MODE="$mode" python3 -c '
import json, os
b = {"environment": os.environ["ENV"], "mode": os.environ["MODE"]}
if os.environ["TICKET"]: b["ticket"] = os.environ["TICKET"]
else: b["sha"] = os.environ["SHA"]
print(json.dumps(b))
')
  call POST /api/rollback "$body"
}

# release: --from applies to every ticket that follows it, until the next --from.
# That is what lets one release gather work from several sandboxes, which is the
# whole point of the multi-source shape.
cmd_release() {
  local to="" args=()
  while [ $# -gt 0 ]; do
    case "$1" in
      --to) to="${2:-}"; shift 2 ;;
      --to=*) to="${1#*=}"; shift ;;
      --from) args+=("--from" "${2:-}"); shift 2 ;;
      --from=*) args+=("--from" "${1#*=}"); shift ;;
      -*) die "unexpected option: $1" ;;
      *) args+=("$1"); shift ;;
    esac
  done
  [ ${#args[@]} -gt 0 ] || die "usage: engine.sh release [--to ENV] --from ENV TICKET..."

  local body
  body=$(TO="$to" python3 -c '
import json, os, sys
to = os.environ["TO"]
tickets, cur = [], None
it = iter(sys.argv[1:])
for a in it:
    if a == "--from":
        cur = next(it)
    else:
        if cur is None:
            print("engine.sh: name a source before the tickets, e.g. --from preprod GH-397", file=sys.stderr)
            print("The API requires a source per ticket; there is no default.", file=sys.stderr)
            sys.exit(2)
        tickets.append({"ticket": a, "from": cur})
if not tickets:
    print("engine.sh: no tickets given", file=sys.stderr); sys.exit(2)
body = {"tickets": tickets}
if to: body["to"] = to
print(json.dumps(body))
' "${args[@]}")
  call POST /api/release "$body"
}

cmd_ticket() {
  [ $# -ge 1 ] || die "usage: engine.sh ticket REF     (GH-397, EXAMPLE-42, jira:EXAMPLE-42)"
  # The canonical form contains a colon, so the ref is URL-encoded here.
  local enc; enc=$(python3 -c 'import sys,urllib.parse; print(urllib.parse.quote(sys.argv[1], safe=""))' "$1")
  call GET "/api/ticket/$enc"
}

cmd_history() {
  local q="" env="" limit=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --env) env="${2:-}"; shift 2 ;;
      --limit) limit="${2:-}"; shift 2 ;;
      *) die "unexpected argument: $1" ;;
    esac
  done
  [ -n "$env" ] && q="?env=$env"
  if [ -n "$limit" ]; then
    if [ -n "$q" ]; then q="$q&limit=$limit"; else q="?limit=$limit"; fi
  fi
  call GET "/api/history$q"
}

# ── Dispatch ──────────────────────────────────────────────────────────────────

ARGS=()
for a in "$@"; do
  case "$a" in
    --raw) RAW=1 ;;
    -h|--help) usage; exit 0 ;;
    *) ARGS+=("$a") ;;
  esac
done
set -- "${ARGS[@]+"${ARGS[@]}"}"

[ $# -ge 1 ] || { usage; exit 2; }
CMD="$1"; shift

case "$CMD" in
  login)      cmd_login "$@" ;;
  status)     cmd_status "$@" ;;
  topology)   call GET /api/topology ;;
  board)      call GET /api/board ;;
  history)    cmd_history "$@" ;;
  ticket)     cmd_ticket "$@" ;;
  retry)      cmd_retry "$@" ;;
  revalidate) cmd_revalidate "$@" ;;
  rollback)   cmd_rollback "$@" ;;
  release)    cmd_release "$@" ;;
  pause)      call POST /api/pause ;;
  resume)     call POST /api/resume ;;
  *) die "unknown command: $CMD (try --help)" ;;
esac
