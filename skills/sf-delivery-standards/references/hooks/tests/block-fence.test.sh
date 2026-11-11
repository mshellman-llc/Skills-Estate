#!/bin/bash
# Requirement 13: the CLAUDE.md contract carries a hash of its own body, so any edit
# inside the fence is self-announcing. And the fence must survive the repo's own
# markdown formatter (a blank line inserted around the block is not tampering), or it
# fails on every commit and becomes a check nobody reads.
#
# Tests block_status(): OK when the recorded hash matches the body, MODIFIED when the
# body is edited under an unchanged hash, MISSING when there is no block, and OK again
# when only outer blank lines change (the formatter-tolerance).
#
# Run: bash references/hooks/tests/block-fence.test.sh

set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
BLOCK="$HERE/../claude-hooks/_block.sh"
TEMPLATE="$HERE/../../templates/claude-md-block.md"
[ -f "$BLOCK" ] || { echo "missing: $BLOCK"; exit 1; }
[ -f "$TEMPLATE" ] || { echo "missing: $TEMPLATE"; exit 1; }
# _block.sh is a pure function library (render/hash/extract/verify); sourcing it
# defines block_hash / block_extract / block_status without any config or gate.
# shellcheck source=/dev/null
. "$BLOCK"

TMP=$(mktemp -d "${TMPDIR:-/tmp}/block fence.XXXXXX") || exit 1
trap 'rm -rf "$TMP"' EXIT

PASS=0; FAIL=0
ok() { PASS=$((PASS+1)); echo "  PASS $1"; }
no() { FAIL=$((FAIL+1)); echo "  FAIL $1 (got: ${2:-})"; }

BODY='## Aleysian delivery standards

- Ticket first; one worktree per ticket.
- Validate (dry-run) BEFORE merge; merge BEFORE deploy; close only after deploy.
- Never `--target-org`; the org is pinned.'

# a well-formed block whose marker records the true hash of BODY
write_block() { # $1=file  $2=body-to-embed (defaults to BODY)  $3=extra-marker-blank(1)
  local f="$1" body="${2:-$BODY}" h
  h=$(printf '%s\n' "$body" | block_hash)
  {
    printf '# Project readme\n\nSome client-owned prose.\n\n'
    printf '<!-- BEGIN aleysian-delivery-standards hash:%s v1.0 -->\n' "$h"
    [ "${3:-0}" = 1 ] && printf '\n'          # a blank line right after BEGIN (formatter)
    printf '%s\n' "$body"
    [ "${3:-0}" = 1 ] && printf '\n'          # and one right before END
    printf '<!-- END aleysian-delivery-standards -->\n'
  } > "$f"
}

echo "== an intact block reports OK =="
write_block "$TMP/ok.md"
S=$(block_status "$TMP/ok.md"); [ "$S" = OK ] && ok "intact block -> OK" || no "intact block" "$S"

echo "== an edit inside the fence, under an unchanged hash, reports MODIFIED =="
write_block "$TMP/mod.md"
# weaken a rule without touching the recorded hash — the exact tamper the fence exists for
sed -i.bak 's/Never `--target-org`.*/Anything goes./' "$TMP/mod.md" && rm -f "$TMP/mod.md.bak"
S=$(block_status "$TMP/mod.md"); [ "$S" = MODIFIED ] && ok "tampered body -> MODIFIED" || no "tampered body" "$S"

echo "== a formatter's blank lines around the block are NOT tampering =="
write_block "$TMP/fmt.md" "$BODY" 1
S=$(block_status "$TMP/fmt.md"); [ "$S" = OK ] && ok "outer blank lines -> still OK" || no "formatter blank lines" "$S"

echo "== the renderer emits Prettier's canonical blank after the marker =="
trunk() { printf main; }
org_alias() { printf DevOrg; }
host() { printf github; }
review() { printf pr; }
ticket_system() { printf github; }
ticket_example() { printf GH-42; }
format_policy() { printf client; }
pmd_policy() { printf advise; }
squash_policy() { printf prefer; }
ticket_types() { :; }
ticket_cancreate() { :; }
ticket_blocked() { :; }
block_render "$TEMPLATE" > "$TMP/rendered.md"
SECOND=$(sed -n '2p' "$TMP/rendered.md")
[ -z "$SECOND" ] && ok "rendered marker is followed by a blank line" || no "rendered marker spacing" "$SECOND"
S=$(block_status "$TMP/rendered.md"); [ "$S" = OK ] && ok "rendered canonical block -> OK" || no "rendered canonical block" "$S"
grep -qF 'clone-local receipts mean **unknown**' "$TMP/rendered.md" \
  && ok "rendered block includes existing-ticket intake" \
  || no "existing-ticket intake missing from rendered block"
grep -q 'repo root or ticket worktree as its project folder' "$TMP/rendered.md" \
  && ok "rendered block names the managed project root" \
  || no "managed project-root guidance missing from rendered block"
grep -q '~/.claude/skills/sf-delivery-standards' "$TMP/rendered.md" \
  && no "rendered block hardcodes the Claude-only skill path" \
  || ok "rendered block is host-neutral"

echo "== DevOps Center renders its separate handoff contract =="
is_devops_center() { return 0; }
devops_org_alias() { printf control64; }
devops_project_id() { printf 0DB000000000001; }
trunk() { printf staging; }
org_alias() { printf stevenc2; }
block_render "$TEMPLATE" > "$TMP/devops.md"
grep -qF '**Invariant: DevOps Center owns stage branches and promotion.**' "$TMP/devops.md" \
  && ok "DevOps Center invariant rendered" || no "DevOps Center invariant missing"
grep -qF 'dx-devops-promote' "$TMP/devops.md" \
  && ok "managed promotion skill is in the hot-path contract" || no "promotion skill pointer missing"
grep -qF 'plugin/capability preflight' "$TMP/devops.md" \
  && ok "promotion capability preflight rendered" || no "promotion capability preflight missing"
grep -qF 'references/devops-center.md' "$TMP/devops.md" \
  && ok "conflict-recovery reference rendered" || no "conflict-recovery reference missing"
grep -qF '2.2.0' "$TMP/devops.md" \
  && no "managed contract embeds a plugin version" || ok "managed contract stays version-independent"
grep -qF 'control64' "$TMP/devops.md" \
  && ok "control-org alias rendered" || no "control-org alias missing"
S=$(block_status "$TMP/devops.md"); [ "$S" = OK ] && ok "DevOps Center block -> OK" || no "DevOps Center block" "$S"

echo "== Shared DevOps Center renders the dual-branch contract =="
is_devops_shared() { return 0; }
devops_integration_branch() { printf stevenc; }
devops_environment() { printf StevenC; }
block_render "$TEMPLATE" > "$TMP/devops-shared.md"
grep -qF '**Invariant: the shared development org and its integration branch agree at rest.**' "$TMP/devops-shared.md" \
  && ok "shared-org invariant rendered" || no "shared-org invariant missing"
grep -qF 'dev/WI-######' "$TMP/devops-shared.md" \
  && ok "development branch role rendered" || no "development branch role missing"
grep -qF 'aleysian-devops-package' "$TMP/devops-shared.md" \
  && ok "exact package helper rendered" || no "package helper missing"
grep -qF 'StevenC' "$TMP/devops-shared.md" \
  && ok "central deployment environment rendered" || no "deployment environment missing"
S=$(block_status "$TMP/devops-shared.md"); [ "$S" = OK ] && ok "shared DevOps Center block -> OK" || no "shared DevOps Center block" "$S"

echo "== no block at all reports MISSING =="
printf '# Just a readme\n\nNo managed block here.\n' > "$TMP/none.md"
S=$(block_status "$TMP/none.md"); [ "$S" = MISSING ] && ok "no block -> MISSING" || no "no block" "$S"

echo "== a body change is caught even if the same number of lines is kept =="
write_block "$TMP/line.md"
# swap a command for a lookalike, same line count — a hash-based fence still catches it
sed -i.bak 's/one worktree per ticket/many worktrees per ticket/' "$TMP/line.md" && rm -f "$TMP/line.md.bak"
S=$(block_status "$TMP/line.md"); [ "$S" = MODIFIED ] && ok "subtle same-shape edit -> MODIFIED" || no "subtle edit" "$S"

echo
printf '%d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
