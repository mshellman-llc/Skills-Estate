#!/bin/bash
# Literal command hygiene only. An explicit alias still needs an org-ID preflight.
if ! command -v python3 >/dev/null 2>&1; then
  echo 'BLOCKED: Python 3 is required for the Salesforce command guard.' >&2
  exit 2
fi
exec python3 "$(dirname "${BASH_SOURCE[0]}")/guard-sf-flags.py"
