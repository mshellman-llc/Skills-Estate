#!/usr/bin/env bash
# Optional validation hook. Review existing hooks before installing.
# This does not stage files, install packages, publish, or run behavioral tests.
set -euo pipefail
estate_repo="$(git rev-parse --show-toplevel)"
if [ ! -f "$estate_repo/tools/estate.py" ]; then
  echo '[estate-sync] canonical tools/estate.py is missing' >&2
  exit 2
fi
python3 "$estate_repo/tools/estate.py" validate
