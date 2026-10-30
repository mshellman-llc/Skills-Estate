#!/usr/bin/env python3
"""Inspect local DevOps Center plugin capabilities, or a supplied offline manifest.

This script never authenticates, queries an org, or promotes metadata.
"""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

PLUGIN = '@salesforce/plugin-devops-center'
REQUIRED = ('devops:promotion:validate', 'devops:promote',
            'devops:work-item:prepare', 'devops:promotion:complete')


def inspect_manifest(value, require_combine=False):
    if isinstance(value, list):
        if len(value) != 1:
            raise ValueError('Expected exactly one plugin manifest.')
        value = value[0]
    if not isinstance(value, dict):
        raise ValueError('Plugin manifest must be an object or a one-object array.')
    package = value.get('pjson', {})
    if not isinstance(package, dict):
        raise ValueError('Plugin pjson must be an object.')
    version = value.get('version') or value.get('tag') or package.get('version')
    match = re.fullmatch(r'(\d+)\.(\d+)\.(\d+)(?:\+[A-Za-z0-9.-]+)?', version or '') if isinstance(version, str) else None
    if not match:
        raise ValueError('Plugin must report a stable numeric version, for example 2.2.0.')
    if tuple(map(int, match.groups())) < (2, 0, 0):
        raise ValueError('Plugin version 2.0.0 or newer is required; inspect the available upgrade before installing.')
    ids = value.get('commandIDs')
    commands = value.get('commands')
    if not isinstance(ids, list) or any(not isinstance(item, str) for item in ids):
        raise ValueError('commandIDs must be a list of strings.')
    if not isinstance(commands, list) or any(not isinstance(item, dict) for item in commands):
        raise ValueError('commands must be a list of command objects.')
    required = list(REQUIRED) + (['devops:work-item:combine'] if require_combine else [])
    missing = [name for name in required if name not in ids]
    if missing:
        raise ValueError('Missing capabilities: ' + ', '.join(missing))
    promote = [item for item in commands if item.get('id') == 'devops:promote']
    if len(promote) != 1 or not isinstance(promote[0].get('flags'), dict) or not isinstance(promote[0]['flags'].get('skip-validation'), dict):
        raise ValueError('Plugin must expose one promote command with the skip-validation flag.')
    return {'plugin': PLUGIN, 'version': version, 'capability_check': 'passed',
            'checked_commands': required, 'combine_available': 'devops:work-item:combine' in ids,
            'org_verified': False, 'promotion_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, help='Offline JSON from plugins inspect; makes no CLI calls')
    parser.add_argument('--require-combine', action='store_true')
    args = parser.parse_args()
    try:
        if args.manifest:
            raw = args.manifest.read_text(encoding='utf-8')
            basis = 'supplied manifest; installed plugin not checked'
        else:
            binary = shutil.which(os.environ.get('SF_BIN', 'sf'))
            if not binary:
                raise ValueError('Salesforce CLI is not installed; use --manifest for offline inspection.')
            response = subprocess.run([binary, 'plugins', 'inspect', PLUGIN, '--json'],
                                      capture_output=True, text=True, timeout=30,
                                      env={**os.environ, 'SF_DISABLE_LOG_FILE': 'true'})
            if response.returncode:
                raise ValueError('Plugin inspection failed; inspect the local CLI installation before promotion.')
            raw = response.stdout
            basis = 'local plugins inspect output; no org accessed'
        result = inspect_manifest(json.loads(raw), args.require_combine)
        print(json.dumps({**result, 'basis': basis}, separators=(',', ':')))
        return 0
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print('BLOCKED: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
