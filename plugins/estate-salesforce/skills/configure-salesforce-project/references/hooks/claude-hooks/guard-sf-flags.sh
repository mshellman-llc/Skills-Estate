#!/bin/bash
# PreToolUse (Bash) — sf CLI flag hygiene, for ANY sf/sfdx subcommand.
#
#   --target-org / -o    the default org is configured project-locally; naming one
#                        by hand risks aiming a command at the wrong org
#   --use-most-recent    resolves to whatever job the org saw last, which may be
#                        another agent's deploy
#   retrieve             the repo is the source of truth; never pull org state
#                        over force-app/. This hook is the ONLY layer — an earlier
#                        settings.json deny was removed (a machine-wide deny fires
#                        in every repo on the machine, violating non-interference).
#
# TWO CARVE-OUTS. First, for the drift module: `retrieve start --output-dir <path>`
# is allowed when <path> is outside every working tree, or is the conventional
# tmp-retrieve/ scratch dir. That is the sanctioned reconciliation path for an
# org-side change — it cannot touch tracked files by construction, so the reason
# the block exists does not apply to it.
#
# Second, the worktree carve-out: a plain retrieve (no --output-dir) run from a
# LINKED worktree is allowed. It lands in that worktree's own force-app/ — the
# agent's throwaway branch checkout, never main and never the org — and the PR
# diff catches it before merge. The block exists to protect the source-of-truth
# checkout (main); a linked worktree is not that. An explicit --output-dir is
# judged by the first carve-out regardless of cwd, so a force-app target still
# blocks even from a worktree.
#
# Everything else still blocks.
#
# The retrieve block has an escape hatch: ALEY_/SW_/SOLO_ALLOW_RETRIEVE. Since
# this hook is now the only layer (the settings.json deny was removed), the hatch
# is a real bypass — it lets one retrieve through and records it to the hatch-log
# so an override is on the record rather than silent. Initial seeding needs
# neither block nor hatch: it runs before this stack is installed. The normal way
# to capture an org-side change is the scratch-dir path, NOT the hatch — see
# references/drift-reconcile.md and references/seeding-guide.md.
#
# EVERY sf invocation in the command is judged, one at a time. A verdict reached
# on one of them never ends the scan — an `allow` is a `continue`, not an `exit`,
# because `sf project retrieve preview && sf project retrieve start` is one Bash
# call containing one harmless command and one that overwrites force-app/.

set -u
HOOK_EVENT="PreToolUse"
HOOK_DEFER_GATE=1   # the master gate fires in hook_read_input, once the target repo is known
. "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

hook_read_input
COMMAND=$(hook_command_text)

# ── Isolate the sf invocations, one per line ─────────────────
#
# This used to be two sed expressions over the whole command:
#
#   sed -E 's/.*((^|[[:space:]"'(])(sf|sfdx)[[:space:]])/\1/'   # keep from "sf "
#   sed -E 's/[|;&].*$//'                                        # drop the rest
#
# Both halves were wrong, and each one shipped a real bug:
#
#   The leading `.*` is GREEDY, so only the LAST sf invocation survived. In
#   `sf project deploy start -o wrongorg && sf project deploy report --job-id X`
#   the first command's --target-org was never inspected — a total bypass of the
#   one gate that keeps a command from being aimed at the wrong org.
#
#   sed is LINE-ORIENTED, so in a multi-line command every line WITHOUT an sf on
#   it passed through untouched and its flags were then attributed to sf. A
#   `find force-app -name '*.cls' -o -name '*.xml'` on the line after a deploy was
#   refused with "BLOCKED: --target-org / -o on an sf command" — a flag the author
#   never passed, on a command that was not sf.
#
# So the command is SPLIT into shell commands instead: on newlines, and on the
# unquoted separators | ; & (split_commands below). Then every piece whose command
# word is sf or sfdx is kept, from that word to the end of the piece.
#
# `grep -oE '...(sf|sfdx)[[:space:]].*$'` takes the LEFTMOST match, i.e. the FIRST
# sf in the piece. That is what makes a prefix harmless rather than concealing:
# `ALEY_ALLOW_RETRIEVE=1 sf project retrieve start` and `env -i sf project ...`
# both still surface their real invocation.
#
# The leading (^|[[:space:]"'(]) is load-bearing in both directions: it keeps a
# QUOTED invocation visible, so `bash -c "sf project deploy start -o x"` is still
# an sf command, while refusing to match a word that merely ENDS in sf (`mysf`).
#
# split_commands is quote-aware — a `;`, `&` or `|` inside a quoted argument is
# NOT a separator, so `sf project deploy start --tests "A & B" -o x` stays one
# piece and its -o is still seen. (The old code cut at the first separator
# whatever the quoting, which lost the tail of any such command.) What it still
# does not model: a backslash-escaped quote inside a quoted string flips the
# quote state, and a backslash-escaped separator reads as a separator. Both need
# a shell grammar rather than a scanner; heredoc bodies are already gone by here
# (strip_heredocs), which removes the case that actually came up in practice.
split_commands() {
  awk 'BEGIN { SQ = sprintf("%c", 39); DQ = sprintf("%c", 34) }
{
  out = ""; q = ""; n = length($0)
  for (i = 1; i <= n; i++) {
    c = substr($0, i, 1)
    if (q == "") {
      if (c == SQ || c == DQ)            { q = c; out = out c; continue }
      if (c == "|" || c == ";" || c == "&") { out = out "\n"; continue }
      out = out c
    } else {
      if (c == q) { q = "" }
      out = out c
    }
  }
  print out
}'
}

SF_SEGMENTS=$(printf '%s\n' "$COMMAND" \
  | split_commands \
  | grep -oE '(^|[[:space:]"'"'"'(])(sf|sfdx)[[:space:]].*$' \
  | sed -E 's/^[[:space:]"'"'"'(]+//')

[ -n "$SF_SEGMENTS" ] || exit 0

# One sf invocation per iteration. Fed by a heredoc rather than a pipe on purpose:
# a pipe would put the loop in a subshell, where block()'s `exit 2` would end the
# subshell and the hook would go on to allow the tool call.
RETRIEVE_NOTED=0
while IFS= read -r SEG; do
  [ -z "$SEG" ] && continue

  # DevOps Center commands target the control org, not the project-local development
  # org. Keep that exception narrow and deterministic: the configured alias is
  # required explicitly, and structured output is required for agent consumption.
  if is_devops_center && echo "$SEG" | grep -qE '^(sf|sfdx)[[:space:]]+devops\b'; then
    WANT_DEVOPS_ORG=$(devops_org_alias)
    [ -n "$WANT_DEVOPS_ORG" ] || block \
      "BLOCKED: estate.devops.orgalias is not configured for this DevOps Center repo." \
      "" \
      "Set it once, then re-render the delivery contract:" \
      "  git config estate.devops.orgalias <control-org-alias>" \
      "  /configure-salesforce-project audit --fix"
    if ! echo "$SEG" | grep -qE -- "(--target-org|-o)[=[:space:]]+${WANT_DEVOPS_ORG}([[:space:]]|$)"; then
      block \
        "BLOCKED: sf devops commands must explicitly target '$WANT_DEVOPS_ORG'." \
        "" \
        "The project-local target org is the development sandbox. DevOps Center lives" \
        "in a different control org, so relying on the default sends this command to" \
        "the wrong Salesforce surface." \
        "" \
        "Add:  --target-org $WANT_DEVOPS_ORG --json"
    fi
    if ! echo "$SEG" | grep -qE -- '(^|[[:space:]])--json([[:space:]]|$)'; then
      block \
        "BLOCKED: sf devops commands require --json in this delivery mode." \
        "" \
        "The managed DevOps Center skills verify status and record IDs from structured" \
        "output. Add --json rather than parsing terminal prose."
    fi
    continue
  fi

  if echo "$SEG" | grep -qE -- '(--target-org|--targetusername|(^|[[:space:]])-o([[:space:]]|=))'; then
    block \
      "BLOCKED: --target-org / -o on an sf command." \
      "" \
      "  $COMMAND" \
      "" \
      "The target org is set project-locally (.sf/config.json, gitignored) and every" \
      "sf command resolves it automatically. Passing it by hand risks sending a command" \
      "meant for the scratch org somewhere else." \
      "" \
      "In a fresh worktree the config is absent — set it once, do not pass the flag:" \
      "  sf config set target-org=<alias>"
  fi

  if echo "$SEG" | grep -qE -- '--use-most-recent'; then
    block \
      "BLOCKED: --use-most-recent." \
      "" \
      "It resolves to the org's latest job, which may belong to another agent." \
      "Capture the id when you start the job and pass it explicitly:" \
      "" \
      "  JOB_ID=\$(sf project deploy start ... --json --async | jq -r '.result.id')" \
      "  sf project deploy report --job-id \"\$JOB_ID\""
  fi

  echo "$SEG" | grep -qE '\b(project[[:space:]]+retrieve|force:source:retrieve|force:mdapi:retrieve)\b' \
    || continue

  # `retrieve preview` reads and writes nothing. The drift probe uses it.
  echo "$SEG" | grep -qE '\bretrieve[[:space:]]+preview\b' && continue

  # ── The scratch-dir carve-out ──────────────────────────────
  # Judge the resolved TARGET, not the flag's spelling: --output-dir tmp-retrieve
  # is safe because of where it lands, and ../../force-app would not be.
  #
  # QUOTED ALTERNATIVES COME FIRST in the token pattern, then the bare form, and
  # the quotes are stripped afterwards. Exactly the ordering — and for exactly the
  # reason — documented at command_repo_dir() and source_tree_root() in _lib.sh: a
  # bare [^[:space:]]+ alone truncates a quoted path at its first space, and every
  # worktree of a checkout named "64 Org" has a space in its path. With the bare
  # form alone, `--output-dir "/…/64 Org/force-app"` read as `/…/64`, which is
  # under no working tree at all, so this took the "outside every tree" exit and
  # ALLOWED a retrieve straight over force-app/. Do not "simplify" it.
  OUT=$(echo "$SEG" | grep -oE -- "(--output-dir|-r)[[:space:]]+(\"[^\"]+\"|'[^']+'|[^[:space:]|&;]+)" \
        | sed -E 's/^(--output-dir|-r)[[:space:]]+//' | head -1)
  if [ -n "$OUT" ]; then
    OUT=${OUT%\"}; OUT=${OUT#\"}; OUT=${OUT%\'}; OUT=${OUT#\'}
    case "$OUT" in /*) ABS="$OUT" ;; *) ABS="$PWD/$OUT" ;; esac
    PARENT=$(dirname "$ABS")
    while [ ! -d "$PARENT" ] && [ "$PARENT" != "/" ] && [ "$PARENT" != "." ]; do PARENT=$(dirname "$PARENT"); done
    TREE=$(git -C "$PARENT" rev-parse --show-toplevel 2>/dev/null || echo "")
    case "$ABS" in
      */force-app*|*/force-app) ;;                    # never, whatever the flag says
      *)
        if [ -z "$TREE" ]; then
          continue                                     # outside every working tree
        elif [ "${ABS#$TREE/}" != "${ABS}" ] && [ "$(basename "$ABS")" = "tmp-retrieve" ]; then
          if [ "$RETRIEVE_NOTED" = 0 ]; then
            RETRIEVE_NOTED=1
            note "Retrieving into the scratch dir '$OUT'. Nothing tracked can be touched." \
                 "Copy across only what you meant, in a worktree on a ticket, and deploy it" \
                 "back — the deploy is what makes the org and the repo the same thing again."
          fi
          continue
        fi ;;
    esac
  fi

  # ── The worktree carve-out ─────────────────────────────────
  # A plain retrieve (no --output-dir) lands in force-app/ under the project root
  # of the current directory. Run from a LINKED worktree that is the worktree's
  # own force-app/ — the agent's throwaway branch checkout, never main and never
  # the org, and the PR diff shows every change before it can merge. That clobber
  # is the agent's own call, so allow it; the block is there to protect the
  # source-of-truth checkout (main), which a linked worktree is not. An explicit
  # --output-dir is NOT relaxed here — it already went through the scratch-dir
  # rules above, which refuse any force-app target whatever the cwd. git reports a
  # linked worktree's git-dir as <repo>/.git/worktrees/<name>; main's is <repo>/.git.
  if [ -z "$OUT" ]; then
    case "$(git rev-parse --absolute-git-dir 2>/dev/null || echo)" in
      */worktrees/*)
        if [ "$RETRIEVE_NOTED" = 0 ]; then
          RETRIEVE_NOTED=1
          if is_devops_center; then
            note "Retrieving inside a linked WI worktree is allowed. This can overwrite" \
                 "this branch's force-app/ with development-org state, but the review" \
                 "diff will show every change. Keep only what this WI owns, then commit," \
                 "validate, push, and create the DevOps Center review."
          else
            note "Retrieving inside a linked worktree is allowed. This can overwrite this" \
                 "branch's force-app/ with org state, but only this worktree's files:" \
                 "never main, never the org, and the PR diff will show every change" \
                 "before it merges. Pull across only what the ticket needs, then deploy" \
                 "it back. The deploy makes the org and the repo one thing again."
          fi
        fi
        continue ;;
    esac
  fi

  if [ "${ALEY_ALLOW_RETRIEVE:-}" = "1" ] || [ "${SW_ALLOW_RETRIEVE:-}" = "1" ] || [ "${SOLO_ALLOW_RETRIEVE:-}" = "1" ]; then
    record_hatch ALLOW_RETRIEVE "$COMMAND"
    if [ "$RETRIEVE_NOTED" = 0 ]; then
      RETRIEVE_NOTED=1
      if is_devops_center; then
        note "ESCAPE HATCH USED: a retrieve from the development org was allowed." \
             "Recorded to the hatch-log. Retrieve into a scratch tree, move only the" \
             "named components into the WI worktree, then commit, validate, push, and" \
             "create the DevOps Center review."
      else
        note "ESCAPE HATCH USED: a retrieve from the org was allowed." \
             "Recorded to the hatch-log. Retrieve into a scratch tree" \
             "(--output-dir tmp-retrieve), never over force-app/, then bring the" \
             "specific files across in a worktree on a ticket and deploy them back." \
             "A retrieve that lands in force-app/ reverts anything deployed but not" \
             "yet pulled back, with no diff anyone read on purpose."
      fi
    fi
    continue
  fi
  if is_devops_center; then
    HANDOFF="  4. Review, commit, validate, push, and create the DevOps Center review."
  else
    HANDOFF="  4. Review, commit, validate, merge, and deploy through the normal local loop."
  fi
  block \
    "BLOCKED: retrieving from the org." \
    "" \
    "This is the main checkout — the source of truth the org is downstream of. A" \
    "blind retrieve overwrites force-app/ with org state, silently reverting anything" \
    "deployed but not yet pulled — with no diff and no ticket. (Inside a linked" \
    "worktree this is allowed — your own branch's files, and the PR diff catches it.)" \
    "" \
    "Reported a Setup change? Start with the component names the user supplied:" \
    "  1. Treat the report as the candidate set. Query those exact MemberType and" \
    "     MemberName values in SourceMember. Use broad discovery only when the user" \
    "     cannot name the change." \
    "  2. Subtract anything a newer trunk commit or deploy receipt already explains." \
    "     SourceMember identifies metadata, not author or intent." \
    "  3. Retrieve confirmed added/modified components only into tmp-retrieve in the" \
    "     ticket worktree. For IsNameObsolete=true, verify and delete the tracked" \
    "     source deliberately; a deleted component cannot be retrieved." \
    "$HANDOFF" \
    "" \
    "Full playbook: references/drift-reconcile.md. Empty-repo seeding is a different" \
    "operation that runs BEFORE this stack — references/seeding-guide.md."
done <<SEGMENTS
$SF_SEGMENTS
SEGMENTS

exit 0
