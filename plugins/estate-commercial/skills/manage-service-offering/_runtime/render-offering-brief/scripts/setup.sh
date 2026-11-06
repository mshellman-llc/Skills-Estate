#!/usr/bin/env bash
# Read-only checks; dependency installation is an explicit project setup step.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"${PYTHON:-python3}" - "$ROOT" <<'CHECK'
from pathlib import Path
import sys, shutil
root=Path(sys.argv[1]);sys.path.insert(0,str(root/'scripts'))
import jinja2, pypdf
from render_playbook import preflight
print(preflight())
import os
node=os.environ.get('ESTATE_NODE') or shutil.which('node')
if not node:raise SystemExit('Node.js is missing; set ESTATE_NODE')
print('Python dependencies and brand profile are available. Node:',node)
print('Run a synthetic render to verify Playwright, Chromium and PDF layout.')
CHECK
