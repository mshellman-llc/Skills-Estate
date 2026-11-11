#!/usr/bin/env bash
#
# init.sh — point an existing repo at an already-running engine.
#
#   init.sh              wire this clone up, then verify
#   init.sh --check      report what would change, write nothing
#
# This does NOT provision an engine. If there is no Cloud Run service and no
# GitHub App yet, that is references/provisioning.md.
#
# What it writes, all of it per-clone and none of it in the working tree:
#
#   ~/.estate-engine/hooks/       the engine's two guards, machine-wide. They
#                                   exit 0 in any repo with no pipeline.yml, so
#                                   installing them affects nothing else.
#   selected Claude/Codex config    registers those two hooks, merged additively.
#   .vscode/settings.json           engineUrl, so the extension finds the engine.
#                                   The ONE tracked file, and only if absent or
#                                   missing that key.
#
# It writes NOTHING into sf-delivery-standards and reads none of its files. The
# single point of contact is one git config value in THIS repo, using that
# skill's own documented key: `estate.squash prefer`. Its merge gate defaults
# to requiring --squash, which would deadlock against the engine's
# merge-commits-only rule; `prefer` makes its policy advisory and lets the
# engine's own guard enforce the stricter, correct rule. Set only when that
# stack is actually installed here.
#
# Nothing is prompted for. Every value is derived from pipeline.yml, which is the
# authority on what the environments are — never ask a human for that list.
#
# Dependencies: bash, git, python3 (stdlib). No jq, no npm, no yq.

set -eu

CHECK=0
PLATFORM="both"
while [ $# -gt 0 ]; do
  case "$1" in
    --check) CHECK=1 ;;
    --platform) PLATFORM="$2"; shift ;;
    -h|--help) sed -n '2,/^set -eu/p' "$0" | sed 's/^# \{0,1\}//; s/^#$//' | sed '$d'; exit 0 ;;
    *) printf 'init.sh: unknown option %s\n' "$1" >&2; exit 2 ;;
  esac
  shift
done
case "$PLATFORM" in claude|codex|both) ;; *) printf '%s\n' '--platform must be claude, codex, or both' >&2; exit 2 ;; esac

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ENGINE_HOME="$HOME/.estate-engine"
say()  { printf '  %s\n' "$*"; }
head_() { printf '\n%s\n' "$*"; }
die()  { printf '\ninit.sh: %s\n' "$*" >&2; exit 1; }

git rev-parse --git-dir >/dev/null 2>&1 || die "not a git repository"
ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"

[ -f pipeline.yml ] || die "no pipeline.yml in $ROOT — this repo is not engine-managed.
The local loop against a single org is sf-delivery-standards, not this skill."

# ── read pipeline.yml ─────────────────────────────────────────────────────────
# Same awk shape doctor.sh uses. Deliberately dependency-free: this has to run in
# a client repo before anything has been installed.
read -r -d '' ENV_AWK <<'AWK' || true
{ line=$0; sub(/#.*/,"",line) }
line ~ /^[A-Za-z_]/ { inenv=(line ~ /^environments:[ \t]*$/); curenv=""; next }
inenv && line ~ /^[ \t]+[A-Za-z_][A-Za-z0-9_.-]*:[ \t]*$/ {
  key=line; sub(/:[ \t]*$/,"",key); sub(/^[ \t]+/,"",key); curenv=key; next
}
inenv && curenv!="" && line ~ /^[ \t]+(branch|tier):/ {
  k=line; sub(/^[ \t]+/,"",k); sub(/:.*/,"",k)
  v=line; sub(/^.*:[ \t]*/,"",v); gsub(/[ \t"']/,"",v)
  if (v!="") print curenv "\t" k "\t" v
}
AWK

ROWS=$(awk "$ENV_AWK" pipeline.yml 2>/dev/null || true)
[ -n "$ROWS" ] || die "could not parse any environments out of pipeline.yml.
Either the file is malformed, or it uses indentation this parser does not expect.
Nothing has been written."

# Engine-managed branches, for the report below and for the hooks to recognise at
# runtime. A tier: sandbox row is deliberately NOT one: it is a branch people are
# supposed to merge into and deploy to every day.
PROTECTED=$(printf '%s\n' "$ROWS" | python3 -c '
import sys
envs = {}
for line in sys.stdin:
    parts = line.rstrip("\n").split("\t")
    if len(parts) != 3: continue
    name, key, val = parts
    envs.setdefault(name, {})[key] = val
out = [e["branch"] for e in envs.values()
       if e.get("branch") and e.get("tier", "pipeline") != "sandbox"]
print(" ".join(sorted(set(out))))
')
[ -n "$PROTECTED" ] || die "parsed environments but found no pipeline-tier branches. Nothing written."

SANDBOXES=$(printf '%s\n' "$ROWS" | python3 -c '
import sys
envs = {}
for line in sys.stdin:
    parts = line.rstrip("\n").split("\t")
    if len(parts) != 3: continue
    name, key, val = parts
    envs.setdefault(name, {})[key] = val
print(" ".join(sorted(n for n, e in envs.items() if e.get("tier") == "sandbox")))
')

ENGINE_URL_CFG=$(grep -E '^[[:space:]]*engine_url:' pipeline.yml | head -1 \
  | sed -E 's/^[^:]*:[[:space:]]*//; s/[[:space:]]*$//; s/^"//; s/"$//' || true)

head_ "Read from pipeline.yml"
say "engine-managed branches: $PROTECTED"
[ -n "$SANDBOXES" ] && say "tier: sandbox (not protected, deliberately): $SANDBOXES"
if [ -n "$ENGINE_URL_CFG" ]; then say "engine_url: $ENGINE_URL_CFG"; else
  say "engine_url: NOT SET — the VS Code extension and the scripts here cannot find the engine"
fi

if [ "$CHECK" = "1" ]; then
  head_ "Would write"
  say "install + register ~/.estate-engine/hooks/{guard-engine-deploy,guard-engine-merge}.sh"
  say "git config estate.squash prefer  (only if sf-delivery-standards is armed here)"
  [ -n "$ENGINE_URL_CFG" ] && say ".vscode/settings.json -> sfDeployEngine.engineUrl"
  printf '\nNothing written (--check).\n'
  exit 0
fi

# ── write ─────────────────────────────────────────────────────────────────────
# ── machine: the engine's own hooks ───────────────────────────────────────────
#
# User level, not in the repo, for the same reason sf-delivery-standards puts
# its hooks there: a worktree agent can edit .claude/hooks/ in its own branch and
# disarm the thing governing it. It cannot edit ~/.
#
# Safe to install machine-wide because both hooks exit 0 immediately in any repo
# without a pipeline.yml. That is their master gate.
head_ "Engine hooks -> $ENGINE_HOME"
mkdir -p "$ENGINE_HOME/hooks"
cp "$SKILL_DIR/references/hooks/_engine-lib.sh" \
   "$SKILL_DIR/references/hooks/guard-engine-deploy.sh" \
   "$SKILL_DIR/references/hooks/guard-engine-merge.sh" "$ENGINE_HOME/hooks/"
chmod +x "$ENGINE_HOME/hooks/guard-engine-deploy.sh" "$ENGINE_HOME/hooks/guard-engine-merge.sh"
# _engine-lib.sh is sourced, never run. Leaving it executable invites someone to
# run it and wonder why nothing happened.
chmod -x "$ENGINE_HOME/hooks/_engine-lib.sh"
say "installed guard-engine-deploy.sh, guard-engine-merge.sh"

if ENGINE_HOME="$ENGINE_HOME" ALEY_PLATFORM="$PLATFORM" python3 - <<'PY'
import json, os, sys

home = os.environ["ENGINE_HOME"]
platform = os.environ["ALEY_PLATFORM"]
wanted = [f"{home}/hooks/guard-engine-deploy.sh",
          f"{home}/hooks/guard-engine-merge.sh"]
paths = []
if platform in ("claude", "both"):
    paths.append(os.path.expanduser("~/.claude/settings.json"))
if platform in ("codex", "both"):
    paths.append(os.path.expanduser("~/.codex/hooks.json"))
total_added = 0
for settings in paths:
    try:
        with open(settings) as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    except json.JSONDecodeError:
        print(f"{settings} is not valid JSON — left alone", file=sys.stderr)
        sys.exit(3)
    pre = data.setdefault("hooks", {}).setdefault("PreToolUse", [])
    existing = {h.get("command") for entry in pre for h in entry.get("hooks", [])}
    for cmd in wanted:
        if cmd not in existing:
            pre.append({"matcher": "Bash", "hooks": [{"type": "command", "command": cmd}]})
            total_added += 1
    os.makedirs(os.path.dirname(settings), exist_ok=True)
    with open(settings, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
sys.exit(0 if total_added else 1)
PY
then say "registered engine guards for platform=$PLATFORM (Codex hooks require review with /hooks)"
else
  case $? in
    1) say "already registered for platform=$PLATFORM" ;;
    *) say "could not update the selected hook config — register these by hand:"
       say "  PreToolUse / Bash -> $ENGINE_HOME/hooks/guard-engine-deploy.sh"
       say "  PreToolUse / Bash -> $ENGINE_HOME/hooks/guard-engine-merge.sh" ;;
  esac
fi

head_ "Clone config"

# One value, in THIS repo, using sf-delivery-standards' own documented key, and
# only when that stack is armed here. Its merge gate defaults to squash=require
# and would refuse the merge commits the engine's promotion model depends on;
# `prefer` demotes that to advisory. The engine's guard-engine-merge.sh then
# enforces merge-commits-only, which is the stricter rule.
if [ -n "$(git config --get estate.mode 2>/dev/null || true)" ]; then
  CUR=$(git config --get estate.squash 2>/dev/null || echo "require")
  if [ "$CUR" = "require" ]; then
    git config estate.squash prefer
    say "estate.squash: require -> prefer"
    say "  (their gate stops demanding --squash; the engine's own guard requires"
    say "   merge commits, which promotion and rollback both depend on)"
  else
    say "estate.squash = $CUR (left alone)"
  fi
else
  say "sf-delivery-standards is not armed here (no estate.mode) — nothing to reconcile."
  say "If you install it later, re-run this to set estate.squash=prefer."
fi

# Anything this clone used to be told about protected branches is now the
# engine's own hooks' business, read from pipeline.yml directly.
if [ -n "$(git config --get estate.protected 2>/dev/null || true)" ]; then
  git config --unset estate.protected 2>/dev/null || true
  say "removed estate.protected (superseded by the engine's own merge guard)"
fi

# ── .vscode/settings.json ─────────────────────────────────────────────────────
if [ -n "$ENGINE_URL_CFG" ]; then
  head_ "VS Code"
  mkdir -p .vscode
  if ENGINE="$ENGINE_URL_CFG" python3 - <<'PY'
import json, os, sys
path = ".vscode/settings.json"
key  = "sfDeployEngine.engineUrl"
url  = os.environ["ENGINE"]
try:
    with open(path) as f:
        data = json.load(f)
    if not isinstance(data, dict):
        print("existing settings.json is not an object — left alone", file=sys.stderr)
        sys.exit(3)
except FileNotFoundError:
    data = {}
except json.JSONDecodeError:
    # Never rewrite a file we could not parse. VS Code tolerates comments in
    # settings.json and json.load does not, so this is a normal outcome, not a
    # corruption — and clobbering someone's editor config is not a repair.
    print("existing settings.json is not plain JSON (comments?) — left alone", file=sys.stderr)
    sys.exit(3)

if data.get(key) == url:
    sys.exit(1)          # already correct
data[key] = url
with open(path, "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
sys.exit(0)
PY
  then say "wrote sfDeployEngine.engineUrl to .vscode/settings.json"
  else
    case $? in
      1) say ".vscode/settings.json already correct" ;;
      *) say "left .vscode/settings.json alone — set this key by hand:"
         say "  \"sfDeployEngine.engineUrl\": \"$ENGINE_URL_CFG\"" ;;
    esac
  fi
fi

# ── verify ────────────────────────────────────────────────────────────────────
head_ "Verifying"
if [ -x "$SCRIPT_DIR/doctor.sh" ]; then
  "$SCRIPT_DIR/doctor.sh" || true
else
  say "doctor.sh not executable next to this script — run it manually"
fi

head_ "Next"
say "1. Mint a CLI token if you have not:  $SCRIPT_DIR/engine.sh login"
say "2. Arm the local loop:                sf-delivery-standards init"
say "3. Anything doctor flagged above."
printf '\n'
