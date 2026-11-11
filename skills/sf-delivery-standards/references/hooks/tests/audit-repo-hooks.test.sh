#!/bin/bash
# Regression tests for audit.sh section 4b — repo-level hooks that duplicate this
# skill's own.
#
# The blind spot these pin down: sections 1-4 all answer "is OUR stack armed", and
# none of them can see a SECOND stack. 64-Org carried three hooks of its own in
# .claude/hooks/, forked from this skill's ancestor before the skill existed.
# Adopting the skill installed a newer implementation alongside the fork rather
# than retiring it, and a later ledger migration left one forked hook writing to a
# path no reader reads. Audit said clean, exit 0, for two sessions. Every question
# it asked was answered correctly; none of them was this one.
#
# The three cases below are the three ways a repo hook can relate to ours, and the
# middle one is the one that matters most: `record-deploy.sh` collides with NO
# skill hook name, so a name check alone misses it entirely. It is caught only by
# noticing that it writes a state file we own.
#
# Self-contained: builds its own throwaway repo, touches nothing else. It does
# invoke the real audit.sh, so other sections will report FAIL against a synthetic
# repo — that is expected and not asserted on. Only section 4b's lines are checked.
#
# Note on machine coupling: audit.sh deliberately prefers the ARMED libraries in
# ~/.aleysian over the skill's own, because its job is to verify what is actually
# installed. Section 4b uses only cfg(), which is identical in both, so this suite
# is unaffected either way.
#
# Run: bash references/hooks/tests/audit-repo-hooks.test.sh

set -u

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
AUDIT="$HERE/../../../scripts/audit.sh"
[ -f "$AUDIT" ] || { echo "missing audit.sh: $AUDIT"; exit 1; }

command -v jq >/dev/null 2>&1 || { echo "jq required; skipping"; exit 0; }

TMP=$(mktemp -d "${TMPDIR:-/tmp}/audit 4b.XXXXXX") || exit 1
TMP=$(cd "$TMP" && pwd -P)
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

R="$TMP/repo"
mkdir -p "$R/.claude/hooks" && cd "$R" || exit 1
git init -q -b main . >/dev/null 2>&1
git config user.email t@t.test; git config user.name t
git config aleysian.mode native
git config aleysian.trunk main
# ticket.system=none keeps section 9-11 from making a network call, so this suite
# stays fast and offline.
git config aleysian.ticket.system none
echo x > f.txt && git add -A >/dev/null 2>&1 && git commit -qm init >/dev/null 2>&1

# 1. name collision — a second implementation of a hook we ship
printf '#!/bin/bash\nexit 0\n' > .claude/hooks/guard-force-app.sh

# 2. ledger collision — collides with NO skill hook name, but writes our state.
#    This is the shape of the real bug.
printf '#!/bin/bash\necho "$SHA" >> "$(git rev-parse --show-toplevel)/.claude/.deploy-log"\n' \
  > .claude/hooks/record-deploy.sh

# 3. unrelated — a repo's own formatter is none of our business, but nothing here
#    can tell it apart from case 1 or 2 without a human looking once.
printf '#!/bin/bash\nexit 0\n' > .claude/hooks/format-stuff.sh

chmod +x .claude/hooks/*.sh

cat > .claude/settings.json <<'JSON'
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": ".claude/hooks/guard-force-app.sh" },
          { "type": "command", "command": ".claude/hooks/format-stuff.sh" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": ".claude/hooks/record-deploy.sh" }
        ]
      }
    ]
  }
}
JSON

PASS=0; FAIL=0
OUT="$TMP/audit.out"

# --no-probe is not an optimisation here, it is what makes this suite viable: the
# three network probes in sections 9-11 budget 20-30s each plus `sf` startup, and
# this suite invokes audit three times. Without it the suite outlives any sane
# timeout and gets killed, which reports nothing.
audit() { ( cd "$R" && bash "$AUDIT" --no-probe ) > "$OUT" 2>&1; sed -n '/4b\./,/5\. Install/p' "$OUT"; }

# expect_match <yes|no> <pattern> <label>
expect_match() {
  local want="$1" pat="$2" label="$3" got=no
  grep -qE "$pat" "$TMP/section" && got=yes
  if [ "$got" = "$want" ]; then
    PASS=$((PASS+1)); echo "  PASS $label"
  else
    FAIL=$((FAIL+1)); echo "  FAIL $label (expected $want, got $got)"
  fi
}

echo "== unreviewed and colliding hooks are all reported =="
audit > "$TMP/section"
expect_match yes 'guard-force-app\.sh duplicates' "name collision reported"
expect_match yes "record-deploy\.sh writes this skill's 'deploy-log'" "ledger collision reported"
expect_match yes 'unreviewed repo-level hook.*format-stuff\.sh' "unclassified hook reported"
expect_match yes 'FAIL' "section fails, so the repo cannot report clean"

echo "== acknowledging the unrelated hook clears only that one =="
git config aleysian.repohooks "format-stuff.sh"
audit > "$TMP/section"
    # Patterns deliberately avoid the em dash in audit's output: grep -E is
    # byte-oriented, so `.` matches one byte and an em dash is three.
expect_match yes 'format-stuff\.sh.*reviewed and accepted' "acked hook becomes an info line"
expect_match no  'unreviewed repo-level hook' "no unreviewed hooks remain"
expect_match yes 'guard-force-app\.sh duplicates' "name collision still fails after acking"
expect_match yes "record-deploy\.sh writes this skill's" "ledger collision still fails after acking"

echo "== a repo that wires nothing of its own is clean here =="
rm -f .claude/settings.json
git config --unset aleysian.repohooks
audit > "$TMP/section"
expect_match yes 'this repo wires no hooks of its own' "no repo hooks reported as ok"
# Asserted against 4b's OWN failure messages rather than a bare 'FAIL', which is
# what this case actually means. A synthetic repo legitimately fails other sections
# (no managed block, no hooksPath, a stale install), and any of those bleeding into
# the captured range would make a bare-'FAIL' assertion fail for the wrong reason.
expect_match no 'duplicates this skill|writes this skill|unreviewed repo-level hook' \
  "section 4b contributes no failure"

echo
echo "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
