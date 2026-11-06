#!/bin/bash
# The CLAUDE.md managed block: render it, hash it, insert it, verify it.
# SOURCED by _lib.sh and by scripts/{install,audit,render-claude-block}.sh.
#
# ── WHY A BLOCK IN CLAUDE.md AT ALL ─────────────────────────────────────────
# Skill auto-triggering is probabilistic; CLAUDE.md is in context every session
# with no trigger to miss. So the CONTRACT (the invariant, the step order, the
# rules) lives in CLAUDE.md, the ENFORCEMENT lives in hooks, and the REFERENCE
# lives in the skill. Inlining the whole skill into CLAUDE.md would be the
# anti-pattern; a capped, generated, hash-fenced summary is not.
#
# ── WHY A HASH FENCE ────────────────────────────────────────────────────────
# The failure this exists to catch is real and was observed: an agent edited its
# own CLAUDE.md and removed the enforcement rules, then proceeded confidently
# without them. Nothing about the file looked wrong afterwards.
#
# So the BEGIN marker carries a hash of the block's own body. Any hand-edit
# inside the fence changes the body without changing the recorded hash, and
# verify-git-hooks.sh notices at the next session start. Corruption becomes
# self-announcing within one session instead of persisting silently.
#
# The hash covers ONLY the lines between the markers, and the BEGIN line is
# excluded because it contains the hash — including it would be circular.

BLOCK_BEGIN_RE='^<!-- BEGIN estate-delivery-standards'
BLOCK_END='<!-- END estate-delivery-standards -->'
BLOCK_VERSION="1.10"

# block_hash — 12 hex chars of the body on stdin. Short enough to read in a
# marker, long enough that nobody is colliding it by accident.
block_hash() {
  if command -v shasum >/dev/null 2>&1; then shasum -a 256 | awk '{print substr($1,1,12)}'
  else sha256sum | awk '{print substr($1,1,12)}'; fi
}

# block_extract <file> — the body between the markers, exclusive of both.
# Empty output means no block.
# Leading and trailing blank lines are stripped before the body is hashed.
#
# A markdown formatter owns the whitespace around a block: prettier inserts a
# blank line between an HTML comment and the heading that follows it, so in any
# repo that runs prettier over *.md the block is rewritten on the first commit
# that touches CLAUDE.md and the hash never matches again. A fence that fails on
# every commit is one nobody reads, which costs exactly what a fence that never
# fires costs.
#
# Stripping only the outer blank lines keeps the fence honest: it still detects
# any change to a rule, a step, or a command. Nobody weakens a contract by
# adding a blank line to the top of it.
block_extract() {
  [ -f "$1" ] || return 0
  awk -v b="$BLOCK_BEGIN_RE" -v e="$BLOCK_END" '
    $0 ~ b { inb = 1; next }
    index($0, e) { inb = 0; next }
    inb { print }
  ' "$1" | block_strip_blank_edges
}

# Drop blank lines from the top and bottom of stdin. Both the extractor and the
# renderer run their body through this, so the two sides always hash the same
# shape — a normalizer applied on only one side is worse than none, because
# every block then reads as MODIFIED the moment it is written.
block_strip_blank_edges() {
  awk '
    { line[NR] = $0 }
    END {
      first = 1; last = NR
      while (first <= last && line[first] ~ /^[[:space:]]*$/) first++
      while (last >= first && line[last]  ~ /^[[:space:]]*$/) last--
      for (i = first; i <= last; i++) print line[i]
    }
  '
}

# block_recorded_hash <file> — the hash the marker claims.
block_recorded_hash() {
  [ -f "$1" ] || return 0
  grep -m1 -E "$BLOCK_BEGIN_RE" "$1" 2>/dev/null \
    | grep -oE 'hash:[0-9a-f]+' | cut -d: -f2
}

# block_status <file> -> MISSING | OK | MODIFIED
block_status() {
  local body rec act
  body=$(block_extract "$1")
  [ -z "$body" ] && { printf 'MISSING'; return 0; }
  rec=$(block_recorded_hash "$1")
  act=$(printf '%s\n' "$body" | block_hash)
  [ "$rec" = "$act" ] && printf 'OK' || printf 'MODIFIED'
}

# ── Rendering ───────────────────────────────────────────────────────────────
#
# Substitution is done with awk on literal placeholder names rather than `envsubst`
# or `eval`, because the values come from git config — i.e. from a file a client
# could in principle write — and neither of those is safe against a value
# containing shell or template syntax.
#
# block_render <template-file> -> the finished block on stdout, hash included.
block_render() {
  local tmpl="$1" body

  if command -v is_devops_center >/dev/null 2>&1 && is_devops_center; then
    if command -v is_devops_shared >/dev/null 2>&1 && is_devops_shared; then
      tmpl="$(dirname "$tmpl")/devops-center-shared-md-block.md"
    else
      tmpl="$(dirname "$tmpl")/devops-center-md-block.md"
    fi
  fi

  local TRUNK ORG HOSTV REVIEWV TICKETSYS TICKETEX FMT PMD SQUASH MERGE PUSHCL HATCH TNOTES TACT DEVOPSORG DEVOPSPROJECT DEVOPSINTEGRATION DEVOPSENVIRONMENT
  TRUNK=$(trunk); ORG=$(org_alias); HOSTV=$(host); REVIEWV=$(review)
  TICKETSYS=$(ticket_system); TICKETEX=$(ticket_example)
  FMT=$(format_policy); PMD=$(pmd_policy); SQUASH=$(squash_policy)
  DEVOPSORG=""; DEVOPSPROJECT=""; DEVOPSINTEGRATION=""; DEVOPSENVIRONMENT=""
  command -v devops_org_alias >/dev/null 2>&1 && DEVOPSORG=$(devops_org_alias)
  command -v devops_project_id >/dev/null 2>&1 && DEVOPSPROJECT=$(devops_project_id)
  command -v devops_integration_branch >/dev/null 2>&1 && DEVOPSINTEGRATION=$(devops_integration_branch)
  command -v devops_environment >/dev/null 2>&1 && DEVOPSENVIRONMENT=$(devops_environment)

  # How the AGENT acts on the tracker — a hook cannot, because it cannot reach the
  # session's MCP. Jira is the Rovo MCP; GitHub is `gh`. Single line, so it rides on
  # -v (a newline there would blank the whole block — see the TNOTES note below).
  if [ "$TICKETSYS" = "jira" ]; then
    TACT="Jira actions are yours to run, via the Atlassian Rovo MCP (mcp__*__createJiraIssue / addCommentToJiraIssue / getJiraIssue / searchJiraIssuesUsingJql) — never a CLI, and a hook cannot reach the MCP. Transition or close a ticket only when the user asks."
  elif [ "$TICKETSYS" = "github" ]; then
    TACT="Ticket actions use gh (gh issue create / comment / view). Do not close an issue as part of this loop — only when the user asks."
  else
    TACT="Reference tickets by their id; this project has no tracker CLI integration, and this loop does not close tickets."
  fi

  # The rendered instruction must match what guard-pr-merge.sh will actually
  # allow. `squash=merge` inverts the gate, so a block that still said --squash
  # would put the contract and the enforcement in direct contradiction — and the
  # contract is the half the agent reads first.
  if [ "$SQUASH" = "merge" ]; then
    case "$HOSTV" in
      github) MERGE="Merge: gh pr create --base $TRUNK … then gh pr merge --merge --delete-branch (MERGE COMMIT — never --squash/--rebase)" ;;
      gitlab) MERGE="Merge: glab mr create --target-branch $TRUNK … then glab mr merge (MERGE COMMIT — never --squash)" ;;
      azure)  MERGE="Merge: az repos pr create --target-branch $TRUNK … then az repos pr update --id N --squash false --status completed (MERGE COMMIT)" ;;
      bitbucket)
              MERGE="Merge: push the branch (the push gate checks the validate), then merge the PR in Bitbucket's web UI with a MERGE COMMIT — there is no CLI for it" ;;
      none)   MERGE="Merge: git merge --no-ff <branch> into $TRUNK — a real merge commit, never a squash" ;;
    esac
  else
    case "$HOSTV" in
      github) MERGE="Merge: gh pr create --base $TRUNK … then gh pr merge --squash --delete-branch" ;;
      gitlab) MERGE="Merge: glab mr create --target-branch $TRUNK … then glab mr merge --squash" ;;
      azure)  MERGE="Merge: az repos pr create --target-branch $TRUNK … then az repos pr update --id N --squash true --status completed" ;;
      bitbucket)
              MERGE="Merge: push the branch (the push gate checks the validate), then merge the PR in Bitbucket's web UI — there is no CLI for it" ;;
      none)   MERGE="Merge: estate-merge <branch> — the local review gate. Never plain git merge into $TRUNK" ;;
    esac
  fi

  if [ "$HOSTV" = "none" ]; then
    PUSHCL=""
  else
    PUSHCL=" + pushed to origin"
  fi

  # ── What this project's tracker actually permits ──────────────
  #
  # Rendered from the estate.ticket.{types,cancreate,blocked} config recorded at
  # setup (see init-guide.md Phase 2b — an agent introspects the Jira project via the
  # Rovo MCP), rather than assumed, because the answer is per-project and getting it
  # wrong wastes a turn on a create that cannot succeed. An agent that knows "Story is
  # blocked by a required field here" asks the human for a ticket instead of retrying.
  TNOTES=""
  local TT TC TB
  TT=$(ticket_types); TC=$(ticket_cancreate); TB=$(ticket_blocked)
  if [ -n "$TT" ] || [ -n "$TB" ]; then
    TNOTES="   Tracker facts for this project (probed at setup, not assumed):"
    [ -n "$TT" ] && TNOTES="$TNOTES
   - types available: $TT"
    [ -n "$TC" ] && TNOTES="$TNOTES
   - automation can create: $TC"
    if [ -n "$TB" ]; then
      TNOTES="$TNOTES
   - CANNOT be created programmatically: $(printf '%s' "$TB" | tr ';' ' ')
     (required fields block it). Ask the human to open the ticket, then reference it —
     do not retry the create, and do not invent values for a required field."
    fi
  fi

  HATCH="ALEY_ALLOW_UNVALIDATED_MERGE=1, ALEY_SKIP_DOD=1, ALEY_ALLOW_RETRIEVE=1, git commit --no-verify, and the docs-only / no-deploy ticket labels"
  [ "$HOSTV" = "bitbucket" ] && HATCH="$HATCH, ALEY_ALLOW_UNVALIDATED_PUSH=1"

  # TNOTES is multi-line, and `awk -v` CANNOT carry a newline — it fails with
  # "newline in string" and produces NOTHING. That is how an earlier version wrote a
  # completely empty managed block with a valid hash over the empty body: the contract
  # silently vanished and the fence confirmed it was fine.
  #
  # So multi-line substitution goes through a file and getline, the same way
  # block_install() injects the block itself. Single-line values stay on -v.
  local notesfile; notesfile=$(mktemp)
  printf '%s' "$TNOTES" > "$notesfile"

  body=$(awk -v notesfile="$notesfile" \
    -v trunk="$TRUNK" -v org="${ORG:-<not set — run: sf config set target-org=…>}" \
    -v host="$HOSTV" -v review="$REVIEWV" \
    -v tsys="$TICKETSYS" -v tex="$TICKETEX" -v tact="$TACT" \
    -v fmt="$FMT" -v pmd="$PMD" -v squash="$SQUASH" \
    -v devopsorg="${DEVOPSORG:-<not set>}" -v devopsproject="${DEVOPSPROJECT:-<not set>}" \
    -v devopsintegration="${DEVOPSINTEGRATION:-<not set>}" -v devopsenvironment="${DEVOPSENVIRONMENT:-<not set>}" \
    -v merge="$MERGE" -v pushcl="$PUSHCL" -v hatch="$HATCH" '
    {
      gsub(/\{\{TRUNK\}\}/, trunk);            gsub(/\{\{ORG_ALIAS\}\}/, org)
      gsub(/\{\{HOST\}\}/, host);              gsub(/\{\{REVIEW\}\}/, review)
      gsub(/\{\{TICKET_SYSTEM\}\}/, tsys);     gsub(/\{\{TICKET_EXAMPLE\}\}/, tex)
      gsub(/\{\{TICKET_ACTIONS\}\}/, tact)
      gsub(/\{\{FORMAT_POLICY\}\}/, fmt);      gsub(/\{\{PMD_POLICY\}\}/, pmd)
      gsub(/\{\{SQUASH_POLICY\}\}/, squash);   gsub(/\{\{MERGE_INSTRUCTIONS\}\}/, merge)
      gsub(/\{\{DEVOPS_ORG_ALIAS\}\}/, devopsorg); gsub(/\{\{DEVOPS_PROJECT_ID\}\}/, devopsproject)
      gsub(/\{\{DEVOPS_INTEGRATION_BRANCH\}\}/, devopsintegration); gsub(/\{\{DEVOPS_ENVIRONMENT\}\}/, devopsenvironment)
      gsub(/\{\{PUSH_CLAUSE\}\}/, pushcl);     gsub(/\{\{HATCH_LIST\}\}/, hatch)
      # The notes placeholder owns its whole line, so replace the LINE rather than
       # substituting into it. An absent probe leaves no blank line behind, or the hash
       # would differ depending on whether a probe had run — which reads as corruption.
      if ($0 ~ /^\{\{TICKET_NOTES\}\}$/) {
        while ((getline line < notesfile) > 0) print line
        close(notesfile)
        next
      }
      print
    }' "$tmpl")

  rm -f "$notesfile"

  # ── The guard that should have existed from the start ───────────────────
  #
  # Everything downstream trusts block_render's output: install writes it, audit
  # hashes it, the session check compares it. If rendering half-fails, an empty or
  # truncated body gets a perfectly valid hash and the corruption is invisible
  # BECAUSE the fence is working as designed. So validate the body itself, and fail
  # loudly rather than emitting something that will verify.
  if [ "$(printf '%s\n' "$body" | grep -c .)" -lt 20 ] \
     || ! printf '%s' "$body" | grep -q 'Invariant'; then
    {
      echo "block_render: refusing to emit a malformed managed block."
      echo "  rendered $(printf '%s\n' "$body" | grep -c .) non-empty lines; expected 20+ including the invariant."
      echo "  Template: $tmpl"
      echo "  This is a rendering bug, not a config problem — writing it would replace the"
      echo "  contract with nothing and hash it as valid."
    } >&2
    return 1
  fi

  local h; h=$(printf '%s\n' "$body" | block_strip_blank_edges | block_hash)
  # ONE line, deliberately: block_extract() skips exactly the line matching
  # BLOCK_BEGIN_RE, so any continuation line would end up inside the hashed body
  # and every block would read as MODIFIED on the first audit.
  # The blank line after the HTML marker is Prettier's canonical Markdown shape.
  # Emitting it up front keeps a freshly generated block byte-stable when the
  # repo's client formatter runs at commit time. block_extract intentionally
  # strips this outer whitespace before hashing, so the fence still covers only
  # the contract itself.
  printf '<!-- BEGIN estate-delivery-standards v%s hash:%s — managed block, generated by /configure-salesforce-project. Do not hand-edit: the hash is re-checked at every session start and a mismatch is reported as corruption. To change it, change the config and run: /configure-salesforce-project audit --fix -->\n\n' "$BLOCK_VERSION" "$h"
  printf '%s\n' "$body"
  printf '%s\n' "$BLOCK_END"
}

# The body, without the two marker lines — for diffing a file's block against a
# freshly rendered one. Kept here so callers cannot disagree about the offsets.
block_render_body() { block_render "$1" | sed -e '1d' -e '$d'; }

# block_install <claude-md> <rendered-block-file>
#
# Replaces an existing block in place, or appends. Content OUTSIDE the markers is
# never touched — the human's own project notes live there and are the reason this
# is a block rather than a whole managed file.
block_install() {
  local target="$1" new="$2" tmp
  tmp="${target}.sfds.$$"
  if [ -f "$target" ] && grep -qE "$BLOCK_BEGIN_RE" "$target" 2>/dev/null; then
    awk -v b="$BLOCK_BEGIN_RE" -v e="$BLOCK_END" -v nf="$new" '
      $0 ~ b { inb = 1; while ((getline line < nf) > 0) print line; close(nf); next }
      index($0, e) { inb = 0; next }
      !inb { print }
    ' "$target" > "$tmp" && mv "$tmp" "$target"
  else
    { [ -f "$target" ] && { cat "$target"; echo ""; }
      cat "$new"; } > "$tmp" && mv "$tmp" "$target"
  fi
}
