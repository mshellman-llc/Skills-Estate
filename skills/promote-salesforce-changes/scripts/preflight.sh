#!/bin/bash
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$HERE/preflight.py" "$@"
