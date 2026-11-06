#!/usr/bin/env bash
# PreToolUse (Bash) — the engine's one enforceable rule:
#
#   NEVER run a real `sf project deploy` against an org the engine manages.
#
# WHY THIS RULE LIVES HERE
# ------------------------
# Everything else an agent should not do to a Salesforce org — deploy the whole
# tree, run RunLocalTests, deploy from a dirty or unsynced branch, edit
# force-app/ outside a worktree — is expressible relative to ONE org and ONE
# trunk, and belongs to configure-salesforce-project, which is topology-agnostic on
# purpose. This rule is not expressible there: it needs to know that some orgs
# belong to a pipeline, which is a fact only `pipeline.yml` carries.
#
# So this is a layer, not a fork. It adds refusals on top of that stack and
# duplicates none of them, reads none of its config, and writes none of its
# files. Its sibling guard-engine-merge.sh covers the merge surface.
#
# WHAT A VIOLATION COSTS
# ----------------------
# `deployed/<branch>` is the engine's statement about what is in the org. A
# manual deploy makes that statement false with nothing to detect it: the tag
# still points at the last commit the engine deployed, git still looks
# consistent, and the next delta is computed from a baseline that no longer
# describes the org. The recovery is pause, reconcile, move the tag, resume.
#
# WHAT IS ALLOWED, DELIBERATELY
# -----------------------------
# `--dry-run` / `--check-only` against a pipeline org. That is a checkOnly
# request: it mutates nothing, and it is exactly what the engine itself runs to
# validate. Refusing it would block a legitimate way to debug a failing
# validation locally.
#
# MASTER GATE
# -----------
# No `pipeline.yml` in the repo, no opinion — exit 0 immediately. That mirrors
# `estate.mode` in configure-salesforce-project and is what makes this hook safe to
# register machine-wide.
#
# tier: sandbox rows are EXCLUDED. A registered sandbox is board visibility, not
# an engine-managed org; its owner deploys to it themselves, every day. Blocking
# that would break the loop this skill exists above.
#
# WHAT THIS DOES NOT COVER, AND IT IS NOT A DETAIL
# ------------------------------------------------
# A Claude Code hook fires on a tool call the MODEL makes. A command a human
# types in a terminal, or runs from an IDE, never passes through the harness and
# is never seen here. So the accurate claim is "an agent cannot deploy to a
# pipeline org through this session", NOT "the pipeline orgs are protected".
#
# That is a defensible boundary — agents issue hundreds of commands unattended,
# and a human typing a prod deploy is usually doing it on purpose — but it has to
# be stated, because "protected" is what people remember. Branch protection and
# the org's own permissions are the controls that bind a human; this one binds
# the agent.
#
# HONEST LIMIT
# ------------
# The target org is resolved from the command's own -o/--target-org, then the
# repo's .sf/config.json, then the global one, then through the SF alias store.
# If none of that resolves, the org check cannot run and says so rather than
# blocking — but the BRANCH check still applies, and configure-salesforce-project'
# guard-sf-flags.sh already refuses -o/--target-org outright, so the normal path
# is the configured default and that always resolves.

set -u
. "$(dirname "${BASH_SOURCE[0]}")/_engine-lib.sh"

# Master gate FIRST. These hooks sit in front of every Bash call on the machine,
# and in a repo with no pipeline.yml the honest answer is "no opinion" — so reach
# it with two git calls rather than paying a python3 start to parse a payload we
# are about to discard.
gate_or_exit

COMMAND=$(hook_command)
[ -z "$COMMAND" ] && exit 0

# ── is this a real deploy? ───────────────────────────────────
# `sf project deploy start` and the legacy `sfdx force:source:deploy`. Anything
# else — retrieve, a quick-deploy resume, `deploy report` — does not mutate the
# org and is not this hook's business.
echo "$COMMAND" | grep -qE '\b(sf|sfdx)[[:space:]]+(project[[:space:]]+deploy[[:space:]]+start|force:source:deploy)\b' || exit 0

# checkOnly requests mutate nothing, and validating against a pipeline org is a
# legitimate way to debug a failing engine validation locally.
echo "$COMMAND" | grep -qE -- '(--dry-run|--check-only|(^|[[:space:]])-c([[:space:]]|$))' && exit 0

ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
ENVS=$(pipeline_envs "$PIPELINE")
[ -z "$ENVS" ] && exit 0

# ── check 1: are we standing on an environment branch? ───────
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
if [ -n "$BRANCH" ]; then
  while IFS=$'\t' read -r br un on; do
    [ -z "$br" ] && continue
    if [ "$BRANCH" = "$br" ]; then
      block \
        "BLOCKED: '$BRANCH' is an engine-managed environment branch." \
        "" \
        "This org is deployed by the engine, from merges, and by nothing else." \
        "A manual deploy here makes deployed/$br false with nothing able to detect" \
        "it: the tag still points at the last commit the engine shipped, git still" \
        "looks consistent, and the next delta is computed from a baseline that no" \
        "longer describes the org." \
        "" \
        "Ship it the way everything else ships: open a PR into $br and let the" \
        "engine validate and deploy it." \
        "" \
        "Genuinely reconciling the org by hand? That is pause -> fix -> move the tag" \
        "-> resume, deliberately, not a deploy command:" \
        "  scripts/engine.sh pause"
    fi
  done <<<"$ENVS"
fi

# ── check 2: what org is this actually pointed at? ───────────
# Explicit flag first (configure-salesforce-project refuses these outright, so reaching
# here with one set means that guard is absent — check it anyway rather than
# assume another skill is installed).
# Two extractions rather than one alternation: `--target-org` CONTAINS `-o`, so a
# single pattern with a greedy prefix matches the `-o` inside `--target-org` and
# then fails on the rest, silently yielding nothing. That failure is invisible —
# it reads as "no target org set" and waves the deploy through.
TARGET=$(printf '%s' "$COMMAND" | grep -oE -- '--target-org[[:space:]=]+[^[:space:]]+' | head -1 \
  | sed -E 's/^--target-org[[:space:]=]+//; s/^"//; s/"$//')
if [ -z "$TARGET" ]; then
  TARGET=$(printf '%s' "$COMMAND" | grep -oE -- '(^|[[:space:]])-o[[:space:]=]+[^[:space:]]+' | head -1 \
    | sed -E 's/^[[:space:]]*-o[[:space:]=]+//; s/^"//; s/"$//')
fi

if [ -z "$TARGET" ]; then
  for cfg in "$ROOT/.sf/config.json" "$HOME/.sf/config.json"; do
    [ -f "$cfg" ] || continue
    TARGET=$(python3 -c '
import json, sys
try:
    print(json.load(open(sys.argv[1])).get("target-org", "") or "")
except Exception:
    print("")
' "$cfg" 2>/dev/null)
    [ -n "$TARGET" ] && break
  done
fi

if [ -z "$TARGET" ]; then
  note "note: could not resolve a target org, so the engine's org check did not run." \
       "      The branch check above did."
  exit 0
fi

# Resolve an alias to its username. The alias store is a local file, so this
# costs nothing and needs no network — `sf org list` would need both.
RESOLVED=$(python3 -c '
import json, os, sys
want = sys.argv[1]
for p in ("~/.sfdx/alias.json", "~/.sf/alias.json"):
    p = os.path.expanduser(p)
    if not os.path.isfile(p):
        continue
    try:
        d = json.load(open(p))
    except Exception:
        continue
    orgs = d.get("orgs", d)
    if isinstance(orgs, dict) and want in orgs:
        print(orgs[want]); sys.exit(0)
print("")
' "$TARGET" 2>/dev/null)

while IFS=$'\t' read -r br un on; do
  [ -z "$br" ] && continue
  for candidate in "$TARGET" "$RESOLVED"; do
    [ -z "$candidate" ] && continue
    if { [ -n "$un" ] && [ "$candidate" = "$un" ]; } || { [ -n "$on" ] && [ "$candidate" = "$on" ]; }; then
      block \
        "BLOCKED: '$TARGET' is the org the engine deploys to for '$br'." \
        "" \
        "${RESOLVED:+(resolves to $RESOLVED)}" \
        "A manual deploy makes deployed/$br false with nothing able to detect it." \
        "The tag still points at the last commit the engine shipped, so git looks" \
        "consistent while the org no longer matches it, and the next delta is" \
        "computed from a baseline that has stopped being true." \
        "" \
        "Open a PR into '$br' and let the engine deploy it." \
        "" \
        "Meant to target your own sandbox? Check what you are pointed at:" \
        "  sf config get target-org"
    fi
  done
done <<<"$ENVS"

exit 0
