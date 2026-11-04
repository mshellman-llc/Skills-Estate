"""Explicit integration-test selection and preflight without launching a browser."""
from functools import wraps
import json
import os
from pathlib import Path
import shutil
import subprocess
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
CAPABILITIES = ('browser', 'loopback', 'generated-map', 'skill-toolchain')
ENVIRONMENT_KEY = 'ESTATE_TEST_INTEGRATIONS'


def enabled_capabilities():
    return set(filter(None, os.environ.get(ENVIRONMENT_KEY, '').split(',')))


def integration(capability):
    if capability not in CAPABILITIES:
        raise ValueError('Unknown integration capability: ' + capability)

    def decorate(method):
        @wraps(method)
        def selected(self, *args, **kwargs):
            if capability not in enabled_capabilities():
                self.skipTest('Deferred integration: ' + capability +
                              '; run tools/run_tests.py --integration ' + capability)
            # Direct unittest invocation must also fail if an explicitly enabled
            # browser runtime is unavailable. No launch occurs in this check.
            if capability == 'browser':
                runtime = preflight(capability)
                modules = runtime['module_root']
                with patch.dict(os.environ, {
                    'ESTATE_NODE': runtime['node'], 'ESTATE_NODE_MODULES': modules,
                    'NODE_PATH': os.pathsep.join(filter(None, (modules, os.environ.get('NODE_PATH')))),
                    'PW_MODULE': runtime['playwright_entry'],
                }):
                    return method(self, *args, **kwargs)
            return method(self, *args, **kwargs)
        selected.estate_integration = capability
        return selected
    return decorate


def toolchain_preflight():
    """Selftests outside the standard library need jq and python-pptx; CI installs both."""
    missing = []
    if not shutil.which('jq'):
        missing.append('jq (install it with your package manager)')
    try:
        import pptx  # noqa: F401
    except ImportError:
        missing.append('python-pptx (pip install -r requirements-test.txt)')
    if missing:
        raise RuntimeError('Skill toolchain is missing: ' + ', '.join(missing))
    return {'capability': 'skill-toolchain', 'status': 'tools_available', 'jq': shutil.which('jq')}


def preflight(capability):
    if capability not in CAPABILITIES:
        raise ValueError('Unknown integration capability: ' + capability)
    if capability == 'skill-toolchain':
        return toolchain_preflight()
    if capability != 'browser':
        return {'capability': capability, 'status': 'selected'}
    node = os.environ.get('ESTATE_NODE') or shutil.which('node')
    if not node:
        raise RuntimeError('Node is missing. Set ESTATE_NODE to run browser tests.')
    roots = [Path(value) for key in ('ESTATE_NODE_MODULES', 'NODE_PATH')
             for value in os.environ.get(key, '').split(os.pathsep) if value]
    roots.append(ROOT / 'node_modules')
    entry = next((base / 'playwright' / name for base in roots
                  for name in ('index.mjs', 'index.js')
                  if (base / 'playwright' / name).is_file()), None)
    if entry is None:
        raise RuntimeError('Playwright was not found in the configured module directories. Set ESTATE_NODE_MODULES.')
    # Read the installed runtime's browser path. Importing Playwright does not
    # launch it; no launch API appears in this preflight.
    script = """
import fs from 'node:fs';
const pw = await import(process.argv[1]);
const {default: policy} = await import(process.argv[2]);
const options = policy.launchOptions();
const executable = options.executablePath || (pw.chromium ?? pw.default.chromium).executablePath();
fs.accessSync(executable, fs.constants.X_OK);
if (!fs.statSync(executable).isFile()) throw new Error('Browser executable is not a file');
console.log(JSON.stringify({executable}));
"""
    policy = ROOT / 'skills/brand-renderer/scripts/browser_launch_policy.cjs'
    result = subprocess.run([node, '--input-type=module', '-e', script,
                             entry.resolve().as_uri(), policy.as_uri()],
                            capture_output=True, text=True, timeout=15)
    if result.returncode:
        raise RuntimeError('Browser preflight failed before launch: ' + (result.stderr or result.stdout).strip())
    details = json.loads(result.stdout)
    return {'capability': capability, 'status': 'runtime_files_available',
            'node': str(node), 'module_root': str(entry.resolve().parent.parent),
            'playwright_entry': entry.resolve().as_uri(), **details}
