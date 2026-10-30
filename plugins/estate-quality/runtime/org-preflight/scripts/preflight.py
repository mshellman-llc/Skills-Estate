#!/usr/bin/env python3
"""Compare a fresh Salesforce Organization identity with an exact intended org.

Use --target-org for a live, read-only CLI query, --identity-json for a fresh
connector response, or the compatibility --live-id / --is-sandbox arguments.
Supplied evidence is checked, but its freshness cannot be proved by this script.
No mode performs a write or supplies authorization to perform one.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
REGISTRY = HERE / 'orgs.json'
ORG_ID = re.compile(r'^00D(?:[A-Za-z0-9]{12}|[A-Za-z0-9]{15})$')
KINDS = ('production', 'sandbox')
QUERY = 'SELECT Id, Name, IsSandbox, InstanceName FROM Organization'


def org_key(value):
    if not isinstance(value, str) or not ORG_ID.fullmatch(value):
        raise ValueError('Organization ID must be a 15- or 18-character Salesforce 00D ID')
    return value[:15]  # Salesforce 15-character IDs are case-sensitive.


def load_registry(path):
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        raise ValueError('orgs.json does not parse or cannot be read') from exc
    if not isinstance(data, dict) or not isinstance(data.get('orgs'), dict):
        raise ValueError('Registry must contain an orgs object')
    orgs = data['orgs']
    keys, aliases = set(), set()
    for oid, entry in orgs.items():
        key = org_key(oid)
        if key in keys:
            raise ValueError('Registry contains duplicate 15/18-character org identities')
        keys.add(key)
        if not isinstance(entry, dict) or entry.get('kind') not in KINDS:
            raise ValueError('Registry entry needs kind production or sandbox')
        alias = entry.get('alias')
        if not isinstance(alias, str) or not alias.strip():
            raise ValueError('Registry entry needs a nonempty alias')
        if alias.casefold() in aliases:
            raise ValueError('Registry aliases must be unique')
        aliases.add(alias.casefold())
    return orgs


def resolve_expected(expect, orgs):
    if not expect:
        raise ValueError('No --expect given. State the intended org ID or registered alias.')
    if ORG_ID.fullmatch(expect):
        return expect
    for oid, entry in orgs.items():
        if entry['alias'].casefold() == expect.casefold():
            return oid
    if not orgs:
        raise ValueError('orgs.json is empty. Supply the exact intended 00D org ID; a kind alone is insufficient.')
    raise ValueError('Unknown intended org. Registered aliases: ' + ', '.join(entry['alias'] for entry in orgs.values()))


def extract_identity(payload):
    if not isinstance(payload, dict):
        raise ValueError('Identity response must be a JSON object')
    if 'status' in payload and (type(payload['status']) is not int or payload['status'] != 0):
        raise ValueError('Identity query did not succeed')
    result = payload.get('result', payload)
    if not isinstance(result, dict):
        raise ValueError('Identity query result must be an object')
    records = result.get('records')
    if not isinstance(records, list) or len(records) != 1:
        raise ValueError('Identity query must return exactly one Organization record')
    record = records[0]
    if not isinstance(record, dict):
        raise ValueError('Organization record must be an object')
    org_key(record.get('Id'))
    if type(record.get('IsSandbox')) is not bool:
        raise ValueError('Organization.IsSandbox must be a JSON boolean')
    for key in ('Name', 'InstanceName'):
        if not isinstance(record.get(key), str) or not record[key].strip():
            raise ValueError('Organization.' + key + ' is missing')
    return {'id': record['Id'], 'name': record['Name'],
            'is_sandbox': record['IsSandbox'], 'instance': record['InstanceName']}


def fetch_cli(target, executable):
    if not target.strip() or target.startswith('-'):
        raise ValueError('CLI target must be a nonempty alias or username')
    try:
        result = subprocess.run([executable, 'data', 'query', '--target-org', target,
                                 '--query', QUERY, '--json'], capture_output=True,
                                text=True, timeout=45,
                                env={**os.environ, 'SF_DISABLE_LOG_FILE': 'true'})
    except FileNotFoundError as exc:
        raise ValueError('Salesforce CLI is unavailable. Local preparation can continue; connect an org before a write.') from exc
    except subprocess.TimeoutExpired as exc:
        raise ValueError('Identity query timed out. No write may proceed.') from exc
    if result.returncode:
        # Do not echo potentially sensitive CLI diagnostics or authentication data.
        raise ValueError('Salesforce identity query failed. Confirm the connection and intended target before a write.')
    try:
        return extract_identity(json.loads(result.stdout))
    except json.JSONDecodeError as exc:
        raise ValueError('Salesforce CLI returned invalid JSON') from exc


def decide(live, expected, orgs, allow_production):
    live_key = org_key(live['id'])
    kind = 'sandbox' if live['is_sandbox'] else 'production'
    for oid, entry in orgs.items():
        if org_key(oid) == live_key and entry['kind'] != kind:
            raise ValueError('Registry kind disagrees with Organization.IsSandbox. The org wins; correct the registry.')
    if org_key(expected) != live_key:
        raise ValueError('Live org differs from the exact intended org')
    if kind == 'production' and not allow_production:
        raise ValueError('Live org is PRODUCTION. --allow-production is required in addition to existing user authorization.')
    return kind


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = parser.add_mutually_exclusive_group()
    inputs.add_argument('--target-org', help='Explicit CLI connection to query; never uses the default org')
    inputs.add_argument('--identity-json', type=Path, help='Fresh Organization query response from a connector')
    inputs.add_argument('--live-id', help='Compatibility input: Organization.Id supplied by caller')
    parser.add_argument('--is-sandbox', choices=['true', 'false'])
    parser.add_argument('--live-name', default='')
    parser.add_argument('--expect', help='Exact intended 00D ID or registered alias; no kind-only matching')
    parser.add_argument('--registry', type=Path, default=REGISTRY)
    parser.add_argument('--sf', default='sf', help='Salesforce CLI executable')
    parser.add_argument('--allow-production', action='store_true')
    parser.add_argument('--receipt', type=Path, help='New JSON receipt; existing files are never replaced')
    args = parser.parse_args()
    report = {'state': 'refused', 'checkedAt': datetime.now(timezone.utc).isoformat(),
              'writePerformed': False, 'authorizationGranted': False}
    try:
        if args.receipt and args.receipt.exists():
            raise ValueError('Receipt exists; choose a new attempt path')
        orgs = load_registry(args.registry)
        expected = resolve_expected(args.expect, orgs)
        report['expectedOrgId'] = expected
        if args.target_org or args.identity_json:
            if args.is_sandbox is not None or args.live_name:
                raise ValueError('Do not mix caller identity fields with a CLI or JSON response')
        if args.target_org:
            report['evidenceMode'] = 'live-cli-query'
            live = fetch_cli(args.target_org, args.sf)
            report['connection'] = args.target_org
        elif args.identity_json:
            report['evidenceMode'] = 'caller-supplied-query-response'
            source = args.identity_json.read_bytes()
            report['evidenceSha256'] = hashlib.sha256(source).hexdigest()
            live = extract_identity(json.loads(source))
        elif args.live_id and args.is_sandbox is not None:
            report['evidenceMode'] = 'caller-supplied-fields'
            live = {'id': args.live_id, 'name': args.live_name, 'is_sandbox': args.is_sandbox == 'true'}
        else:
            raise ValueError('Live org identity incomplete. Local preparation can continue; connect an org before a write.')
        report['identity'] = live
        report['kind'] = decide(live, expected, orgs, args.allow_production)
        report['state'] = 'identity-match'
        report['productionAcknowledged'] = args.allow_production
        print('PREFLIGHT PASS: exact intended org matches (' + report['kind'] + ')')
        if report['evidenceMode'] != 'live-cli-query':
            print('Caller supplied the identity; obtain it freshly through the same connection that will perform the write.')
        print('A matching identity does not authorize a write. Keep the same connection for the authorized action.')
        code = 0
    except (ValueError, OSError) as exc:
        report['reason'] = str(exc)
        print('PREFLIGHT REFUSED: ' + str(exc))
        code = 2
    if args.receipt and not args.receipt.exists():
        try:
            args.receipt.parent.mkdir(parents=True, exist_ok=True)
            with args.receipt.open('x') as stream:
                json.dump(report, stream, indent=2)
                stream.write('\n')
        except OSError:
            print('PREFLIGHT REFUSED: receipt could not be saved')
            return 2
    return code


if __name__ == '__main__':
    sys.exit(main())
