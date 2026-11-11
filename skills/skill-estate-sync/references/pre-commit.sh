#!/usr/bin/env bash
# house-skills pre-commit hook: gate every commit on selftests, rebuild bundles.
# Install:  ln -s ../../skills/skill-estate-sync/references/pre-commit.sh .git/hooks/pre-commit
# (run from the house-skills repo root; chmod +x the target if needed)
set -euo pipefail
# The estate lives under house-skills/, so the git toplevel is one level above it.
# Resolving $REPO from the toplevel alone made every path below miss.
REPO="$(git rev-parse --show-toplevel)"
[ -d "$REPO/house-skills/skills" ] && REPO="$REPO/house-skills"
echo "[estate-sync] running selftests + rebuilding bundles..."
if ! python3 "$REPO/skills/skill-estate-sync/scripts/build_bundles.py" --source "$REPO/skills" --out "$REPO/dist"; then
  echo "[estate-sync] a skill failed its selftest; commit blocked. Fix it or bundle with --no-gate deliberately." >&2
  exit 1
fi
git add "$REPO/dist" 2>/dev/null || true
echo "[estate-sync] ok"
