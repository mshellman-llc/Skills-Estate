#!/bin/bash
# SessionStart: inspect the active checkout without changing its configuration.
HERE="$(cd "$(dirname "$0")" && pwd)" || exit 0
if ! command -v python3 >/dev/null 2>&1; then
  echo "Hook verification unavailable: Python 3 is required. No configuration was changed."
  exit 0
fi
python3 "$HERE/verify-git-hooks.py"
