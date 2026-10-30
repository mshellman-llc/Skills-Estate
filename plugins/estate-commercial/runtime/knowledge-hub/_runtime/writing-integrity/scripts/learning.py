#!/usr/bin/env python3
"""Keep private correction evidence and a bounded writing profile. Python 3.9+."""
import argparse
import contextlib
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import uuid

VERSION = 1
MAX_RULES = 12
MAX_WORDS = 350
MAX_TEXT = 4000
KINDS = {'user-correction', 'ai-repair', 'imported'}
CHECKS = {'meaning', 'scope', 'valid_example'}


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', value):
        raise ValueError('Use a lowercase identifier of at most 64 letters, digits or hyphens.')
    return value


def text(value, field, limit=MAX_TEXT):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f'{field} must contain 1 to {limit} characters.')
    return value.strip()


def project_id(value):
    if not isinstance(value, str):
        raise ValueError('Project must be a lowercase identifier or an empty string.')
    return identifier(value) if value else ''


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def read_json(path):
    if path != '-' and Path(path).stat().st_size > 1000000:
        raise ValueError('Input exceeds one million bytes.')
    raw = sys.stdin.read(1000001) if path == '-' else Path(path).read_text(encoding='utf-8')
    if len(raw) > 1000000:
        raise ValueError('Input exceeds one million characters.')
    return json.loads(raw)


def store_argument(value):
    if not value or not value.strip() or not Path(value).expanduser().is_absolute():
        raise argparse.ArgumentTypeError('Use a nonempty absolute --store path authorized for this task.')
    return Path(value).expanduser()


def root_path():
    raise ValueError("Writing profile commands require an explicit --store path authorized for the current task and owner. No environment or default store is used.")


def render(rules, owner):
    lines = [f'# Writing profile for {owner}', '', 'Apply these preferences within the skill’s fact, scope and authorization requirements.', '']
    for rule in rules:
        scope = rule.get('scope', 'general')
        item = f"- {rule['instruction']}"
        if rule.get('exception'):
            item += ' Exception: ' + rule['exception']
        if scope != 'general':
            item += f" ({scope}: {rule['scope_id']})"
        lines.append(item)
    if not rules:
        lines.append('No learned rules are active. Use the core writing instructions.')
    return '\n'.join(lines) + '\n'


class Store:
    def __init__(self, root, create=False):
        self.root = Path(root).expanduser().resolve()
        config = self.root / 'installation.json'
        if not create and not config.is_file():
            raise ValueError('No installation config. Run init in a private storage location first.')
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.config = json.loads(config.read_text()) if config.exists() else None
        self.db = sqlite3.connect(str(self.root / 'learning.sqlite3'), timeout=10)
        self.db.row_factory = sqlite3.Row
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS profiles(id TEXT PRIMARY KEY, owner TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS events(id TEXT PRIMARY KEY, profile TEXT NOT NULL,
          session TEXT NOT NULL, pattern TEXT NOT NULL, host TEXT NOT NULL, project TEXT NOT NULL,
          kind TEXT NOT NULL, fingerprint TEXT UNIQUE NOT NULL, body TEXT NOT NULL, created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS rules(id TEXT PRIMARY KEY, profile TEXT NOT NULL,
          pattern TEXT NOT NULL, scope TEXT NOT NULL, scope_id TEXT NOT NULL,
          status TEXT NOT NULL, body TEXT NOT NULL, revision INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS reviews(id TEXT PRIMARY KEY, profile TEXT NOT NULL,
          action TEXT NOT NULL, body TEXT NOT NULL, created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS finishes(profile TEXT NOT NULL, session TEXT NOT NULL,
          host TEXT NOT NULL, created TEXT NOT NULL, PRIMARY KEY(profile,session,host));
        ''')
        if os.name != 'nt':
            os.chmod(self.root / 'learning.sqlite3', 0o600)

    def close(self):
        self.db.close()

    def init(self, owner, profile, host, durability, learning):
        profile, host = identifier(profile), identifier(host)
        owner = text(owner, 'owner', 100)
        if durability not in {'persistent', 'session', 'manual'}:
            raise ValueError('Choose persistent, session or manual storage.')
        if self.config and self.config['profile'] != profile:
            raise ValueError('This installation already selects another profile. Choose a separate store for another owner.')
        with self.db:
            existing = self.db.execute('SELECT owner FROM profiles WHERE id=?', (profile,)).fetchone()
            if existing and existing['owner'] != owner:
                raise ValueError('This profile belongs to another owner. Choose a different profile ID.')
            self.db.execute('INSERT OR IGNORE INTO profiles VALUES(?,?)', (profile, owner))
        if self.config and self.config['profile'] != profile:
            raise ValueError('This installation already selects another profile. Choose a separate store for another owner.')
        config = dict(self.config or {})
        config.update(version=VERSION, installation_id=config.get('installation_id', str(uuid.uuid4())),
                      profile=profile, owner=owner, default_host=host, durability=durability,
                      learning_enabled=bool(learning))
        tmp = self.root / 'installation.json.tmp'
        tmp.write_text(json.dumps(config, indent=2) + '\n')
        if os.name != 'nt':
            os.chmod(tmp, 0o600)
        os.replace(tmp, self.root / 'installation.json')
        self.config = config
        return self.status(profile)

    def profile(self, profile=None):
        profile = identifier(profile or self.config['profile'])
        row = self.db.execute('SELECT * FROM profiles WHERE id=?', (profile,)).fetchone()
        if not row:
            raise ValueError('Unknown profile. Initialize its owner explicitly.')
        return dict(row)

    def enabled(self):
        if not self.config or not self.config['learning_enabled']:
            raise ValueError('Learning is not enabled for this installation.')

    def status(self, profile=None):
        p = self.profile(profile)
        return {'version': VERSION, 'store': str(self.root), 'installation': self.config,
                'profile': p, 'events': self.db.execute('SELECT count(*) FROM events WHERE profile=?', (p['id'],)).fetchone()[0],
                'active_rules': len(self.rules(p['id'])), 'limits': {'rules': MAX_RULES, 'words': MAX_WORDS}}

    def rules(self, profile, active=True):
        sql = 'SELECT body FROM rules WHERE profile=?' + (' AND status="active"' if active else '') + ' ORDER BY pattern,scope,scope_id,id'
        return [json.loads(row['body']) for row in self.db.execute(sql, (profile,))]

    def capture(self, profile, event):
        self.enabled()
        p = self.profile(profile)
        if not isinstance(event, dict):
            raise ValueError('An event must be an object.')
        kind = event.get('kind')
        if kind not in KINDS - {'imported'}:
            raise ValueError('Choose user-correction or ai-repair.')
        body = {k: text(event.get(k), k) for k in ['session', 'before', 'after', 'reason', 'source_ref']}
        body.update(profile=p['id'], kind=kind, pattern=identifier(event.get('pattern')),
                    host=identifier(event.get('host', self.config['default_host'])), project=project_id(event.get('project', '')),
                    tags=self.tags(event.get('tags', ['general'])))
        fingerprint = digest(body)
        old = self.db.execute('SELECT body FROM events WHERE fingerprint=?', (fingerprint,)).fetchone()
        if old:
            return {'event': json.loads(old['body']), 'duplicate': True}
        body.update(id=str(uuid.uuid4()), installation=self.config['installation_id'], created=now())
        with self.db:
            cursor = self.db.execute('INSERT OR IGNORE INTO events VALUES(?,?,?,?,?,?,?,?,?,?)',
                            (body['id'], p['id'], body['session'], body['pattern'], body['host'], body['project'],
                             kind, fingerprint, json.dumps(body), body['created']))
            if not cursor.rowcount:
                row = self.db.execute('SELECT body FROM events WHERE fingerprint=?', (fingerprint,)).fetchone()
                return {'event': json.loads(row['body']), 'duplicate': True}
        return {'event': body, 'duplicate': False}

    @staticmethod
    def tags(value):
        if not isinstance(value, list) or not 1 <= len(value) <= 8:
            raise ValueError('Supply one to eight topic tags.')
        return sorted({identifier(tag) for tag in value})

    def evidence(self, profile, ids):
        if not isinstance(ids, list) or not ids:
            raise ValueError('A rule needs correction evidence IDs.')
        rows = []
        for event_id in set(ids):
            row = self.db.execute('SELECT body FROM events WHERE id=? AND profile=?', (event_id, profile)).fetchone()
            if not row:
                raise ValueError('Evidence ID is missing from this owner profile.')
            rows.append(json.loads(row['body']))
        return rows

    def promote(self, profile, proposal):
        self.enabled()
        p = self.profile(profile)
        if not isinstance(proposal, dict):
            raise ValueError('A rule proposal must be an object.')
        pattern = identifier(proposal.get('pattern'))
        scope = proposal.get('scope', 'general')
        if scope not in {'general', 'host', 'project'}:
            raise ValueError('Choose a general, host or project rule.')
        scope_id = '' if scope == 'general' else identifier(proposal.get('scope_id'))
        instruction = text(proposal.get('instruction'), 'instruction', 500)
        exception = proposal.get('exception', '')
        if not isinstance(exception, str) or len(exception) > 400:
            raise ValueError('An exception must be text of at most 400 characters, or an empty string.')
        exception = exception.strip()
        review = proposal.get('review', {})
        if not isinstance(review, dict):
            raise ValueError('A review must be an object.')
        events = self.evidence(p['id'], proposal.get('evidence')) if review.get('basis') != 'owner-transfer' else []
        if review.get('basis') == 'user-correction':
            if not any(e['kind'] == 'user-correction' for e in events):
                raise ValueError('An AI repair cannot establish a user preference.')
        elif review.get('basis') == 'owner-transfer':
            confirmation = review.get('owner_confirmation')
            if not isinstance(confirmation, dict):
                raise ValueError('An owner transfer needs a confirmation statement and source reference.')
            text(confirmation.get('statement'), 'owner confirmation')
            text(confirmation.get('source_ref'), 'owner confirmation source')
            transfer = self.db.execute('SELECT body FROM reviews WHERE id=? AND profile=? AND action="import"', (review.get('transfer_id'), p['id'])).fetchone()
            if not transfer or not any(x.get('pattern') == pattern and x.get('instruction') == instruction and x.get('exception') == exception and x.get('scope') == scope and x.get('scope_id') == scope_id for x in json.loads(transfer['body'])['rules']):
                raise ValueError('The proposed rule must match an owner-confirmed transfer.')
        elif review.get('basis') == 'writing-standard':
            text(review.get('standard_ref'), 'standard_ref')
        else:
            raise ValueError('Review against a user correction, the writing standard or an owner-confirmed transfer.')
        for check in CHECKS:
            text(review.get(check), check)
        cases = review.get('cases', [])
        if not isinstance(cases, list) or not {'repair', 'keep'} <= {c.get('kind') for c in cases if isinstance(c, dict)}:
            raise ValueError('Record a repair case and a valid example that should be kept.')
        for case in cases:
            if not isinstance(case, dict):
                raise ValueError('A review case must be an object.')
            for field in ['input', 'output', 'assessment']:
                text(case.get(field), field)
            if case.get('result') != 'pass':
                raise ValueError('Every recorded case must pass before activation.')
        rule = {'id': str(uuid.uuid4()), 'profile': p['id'], 'pattern': pattern, 'scope': scope,
                'scope_id': scope_id, 'instruction': instruction, 'exception': exception,
                'tags': self.tags(proposal.get('tags', ['general'])),
                'evidence': sorted({e['id'] for e in events}), 'review': review, 'revision': 1, 'status': 'active'}
        if review.get('basis') == 'owner-transfer':
            rule['owner_provenance'] = {'claimed_owner': p['owner'], 'mechanism': 'procedural attestation',
                                        'identity_verified': False, 'confirmation': review['owner_confirmation'],
                                        'transfer_id': review['transfer_id']}
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            active = self.rules(p['id'])
            same = [x for x in active if (x['pattern'], x['scope'], x['scope_id']) == (pattern, scope, scope_id)]
            retiring = set(proposal.get('supersedes', []))
            if same:
                current = same[0]
                if current['instruction'] == instruction and current['exception'] == exception and current['tags'] == rule['tags']:
                    current['evidence'] = sorted(set(current['evidence']) | set(rule['evidence']))
                    current['revision'] += 1
                    self.db.execute('UPDATE rules SET body=?,revision=? WHERE id=?', (json.dumps(current), current['revision'], current['id']))
                    self.log(p['id'], 'reinforce', {'rule': current['id'], 'review': review})
                    return {'rule': current, 'action': 'reinforced'}
                if current['id'] not in retiring or proposal.get('expected_revision') != current['revision']:
                    raise ValueError('A changed rule needs its current ID in supersedes and its expected_revision.')
            if not retiring <= {x['id'] for x in active}:
                raise ValueError('A superseded rule must be active in this profile.')
            for old in active:
                if old['id'] in retiring:
                    if (old['scope'], old['scope_id']) != (scope, scope_id):
                        raise ValueError('Consolidation cannot broaden the scope of a rule.')
                    rule['evidence'] = sorted(set(rule['evidence']) | set(old['evidence']))
            remaining = [x for x in active if x['id'] not in retiring] + [rule]
            if len(remaining) > MAX_RULES or len(render(remaining, p['owner']).split()) > MAX_WORDS:
                raise ValueError('Profile budget exceeded. Consolidate or retire an existing rule; the correction remains saved.')
            for rule_id in retiring:
                old = next(x for x in active if x['id'] == rule_id)
                old['status'] = 'superseded'
                self.db.execute('UPDATE rules SET status=?,body=? WHERE id=?', ('superseded', json.dumps(old), rule_id))
            self.db.execute('INSERT INTO rules VALUES(?,?,?,?,?,?,?,?)',
                            (rule['id'], p['id'], pattern, scope, scope_id, 'active', json.dumps(rule), 1))
            self.log(p['id'], 'activate', rule)
        return {'rule': rule, 'action': 'activated'}

    def log(self, profile, action, body):
        self.db.execute('INSERT INTO reviews VALUES(?,?,?,?,?)', (str(uuid.uuid4()), profile, action, json.dumps(body), now()))

    def retire(self, profile, rule_id, reason):
        p = self.profile(profile)
        reason = text(reason, 'reason')
        with self.db:
            row = self.db.execute('SELECT body FROM rules WHERE id=? AND profile=? AND status="active"', (rule_id, p['id'])).fetchone()
            if not row:
                raise ValueError('No active rule with that ID in this profile.')
            rule = json.loads(row['body']); rule['status'] = 'retired'
            self.db.execute('UPDATE rules SET status=?,body=? WHERE id=?', ('retired', json.dumps(rule), rule_id))
            self.log(p['id'], 'retire', {'rule': rule_id, 'reason': reason})
        return {'retired': rule_id}

    def context(self, profile=None, host=None, project='', tags=None):
        p = self.profile(profile)
        host = identifier(host or self.config['default_host'])
        project = project_id(project)
        wanted = set(self.tags(tags or ['general'])) | {'general'}
        selected = [rule for rule in self.rules(p['id'])
                    if (rule['scope'] == 'general' or rule['scope'] == 'host' and rule['scope_id'] == host
                        or rule['scope'] == 'project' and rule['scope_id'] == project)
                    and wanted.intersection(rule['tags'])]
        return {'profile': p['id'], 'host': host, 'project': project, 'active_markdown': render(selected, p['owner']),
                'active_rule_ids': [x['id'] for x in selected], 'durability': self.config['durability']}

    def examples(self, profile, pattern, limit=2):
        p = self.profile(profile); identifier(pattern)
        if not 1 <= limit <= 3:
            raise ValueError('Retrieve one to three examples at a time.')
        rows = self.db.execute('SELECT body FROM events WHERE profile=? AND pattern=? ORDER BY created DESC,id LIMIT ?', (p['id'], pattern, limit))
        return [json.loads(row['body']) for row in rows]

    def finish(self, profile, session, host=None):
        self.enabled()
        p = self.profile(profile); session = text(session, 'session')
        host = identifier(host or self.config['default_host'])
        with self.db:
            self.db.execute('INSERT OR REPLACE INTO finishes VALUES(?,?,?,?)', (p['id'], session, host, now()))
        return {'session': session, 'captured_this_session': self.db.execute('SELECT count(*) FROM events WHERE profile=? AND session=? AND host=?', (p['id'], session, host)).fetchone()[0],
                'active_rules': len(self.rules(p['id'])), 'durability': self.config['durability'],
                'checkpoint': 'recorded', 'background_hook': False}

    def export(self, profile, include_events=False, session=None):
        p = self.profile(profile)
        query = 'SELECT body FROM events WHERE profile=?' + (' AND session=?' if session else '') + ' ORDER BY created,id'
        params = (p['id'], text(session, 'session')) if session else (p['id'],)
        events = [json.loads(row['body']) for row in self.db.execute(query, params)] if include_events else []
        rules = self.rules(p['id'])
        for rule in rules:
            rule.pop('review', None)
            if not include_events:
                rule['evidence'] = []
        payload = {'version': VERSION, 'owner': p['owner'], 'profile': p['id'], 'rules': rules, 'events': events, 'created': now()}
        return {'payload': payload, 'sha256': digest(payload)}

    def import_data(self, profile, bundle, owner):
        self.enabled(); p = self.profile(profile)
        if not isinstance(bundle, dict) or not isinstance(bundle.get('payload'), dict):
            raise ValueError('A transfer must contain a payload object.')
        data = bundle['payload']
        if digest(data) != bundle.get('sha256') or data.get('version') != VERSION:
            raise ValueError('Invalid transfer format or checksum.')
        if owner != p['owner'] or data.get('owner') != owner:
            raise ValueError('Confirm the matching owner; profiles for different people cannot be merged.')
        if not isinstance(data.get('events'), list) or not isinstance(data.get('rules'), list):
            raise ValueError('Transfer events and rules must be lists.')
        imported = 0
        # Imported wording is evidence for review. It never activates itself.
        with self.db:
            for candidate in data['rules']:
                if not isinstance(candidate, dict):
                    raise ValueError('Each imported rule must be an object.')
                identifier(candidate.get('pattern'))
                text(candidate.get('instruction'), 'instruction')
                exception = candidate.get('exception', '')
                if not isinstance(exception, str) or len(exception) > 400:
                    raise ValueError('Invalid imported exception.')
            for original in data['events']:
                if not isinstance(original, dict):
                    raise ValueError('Invalid event.')
                for field in ['before', 'after', 'reason', 'source_ref', 'session']:
                    text(original.get(field), field)
                identifier(original.get('pattern')); identifier(original.get('host'))
                project_id(original.get('project', '')); self.tags(original.get('tags', ['general']))
                body = dict(original); body.update(profile=p['id'], kind='imported', origin_kind=original.get('origin_kind', original.get('kind')))
                incoming_id = text(body.get('id'), 'id', 100)
                existing = self.db.execute('SELECT body FROM events WHERE id=?', (incoming_id,)).fetchone()
                if existing:
                    old_body = json.loads(existing['body'])
                    ignored = {'kind', 'origin_kind', 'profile'}
                    if {k:v for k,v in old_body.items() if k not in ignored} != {k:v for k,v in body.items() if k not in ignored}:
                        raise ValueError('An imported event ID conflicts with local evidence.')
                    continue
                fingerprint = digest(body)
                self.db.execute('INSERT INTO events VALUES(?,?,?,?,?,?,?,?,?,?)',
                                (incoming_id, p['id'], body['session'], body['pattern'], body['host'], body.get('project', ''), 'imported', fingerprint, json.dumps(body), text(body.get('created'), 'created', 100)))
                imported += 1
            transfer_id = digest(data)
            old = self.db.execute('SELECT id FROM reviews WHERE profile=? AND action="import" AND id=?', (p['id'], transfer_id)).fetchone()
            if not old:
                self.db.execute('INSERT INTO reviews VALUES(?,?,?,?,?)', (transfer_id, p['id'], 'import', json.dumps(data), now()))
        return {'imported_events': imported, 'candidate_rules': len(data['rules']), 'activated_rules': 0, 'transfer_id': transfer_id,
                'owner_provenance': {'claimed_owner': owner, 'mechanism': 'procedural confirmation', 'identity_verified': False}}

    def dismiss(self, profile, event_id, reason):
        self.enabled()
        p = self.profile(profile)
        self.evidence(p['id'], [event_id])
        with self.db:
            self.log(p['id'], 'dismiss', {'event': event_id, 'reason': text(reason, 'reason')})
        return {'dismissed': event_id, 'evidence_retained': True}

    def transfers(self, profile=None):
        p = self.profile(profile)
        rows = self.db.execute('SELECT id,body FROM reviews WHERE profile=? AND action="import" ORDER BY created DESC LIMIT 8', (p['id'],))
        return [{'transfer_id': row['id'], 'rules': json.loads(row['body'])['rules'][:MAX_RULES]} for row in rows]

    def pending(self, profile=None):
        p = self.profile(profile)
        active_evidence = {event for rule in self.rules(p['id'], False) for event in rule['evidence']}
        for row in self.db.execute('SELECT body FROM reviews WHERE profile=? AND action="dismiss"', (p['id'],)):
            active_evidence.add(json.loads(row['body'])['event'])
        rows = self.db.execute('SELECT id,pattern,kind FROM events WHERE profile=? ORDER BY created DESC', (p['id'],))
        grouped = {}
        for row in rows:
            if row['id'] not in active_evidence:
                key = row['pattern']; grouped.setdefault(key, {'pattern': key, 'count': 0, 'kinds': set()})
                grouped[key]['count'] += 1; grouped[key]['kinds'].add(row['kind'])
        return [{'pattern': x['pattern'], 'count': x['count'], 'kinds': sorted(x['kinds'])} for x in sorted(grouped.values(), key=lambda x: (-x['count'], x['pattern']))[:8]]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--store', type=store_argument, default=None)
    ap.add_argument('--profile')
    commands = ap.add_subparsers(dest='command', required=True)
    init = commands.add_parser('init'); init.add_argument('--owner', required=True); init.add_argument('--profile-id', required=True); init.add_argument('--host', required=True); init.add_argument('--durability', choices=['persistent', 'session', 'manual'], required=True); init.add_argument('--enable-learning', action='store_true')
    for command in ['status', 'pending', 'transfers']:
        commands.add_parser(command)
    for command in ['capture', 'promote']:
        commands.add_parser(command).add_argument('file', help='JSON file, or - for stdin')
    context = commands.add_parser('context'); context.add_argument('--host'); context.add_argument('--project', default=''); context.add_argument('--tags', default='general'); context.add_argument('--markdown', action='store_true')
    examples = commands.add_parser('examples'); examples.add_argument('--pattern', required=True); examples.add_argument('--limit', type=int, default=2)
    retire = commands.add_parser('retire'); retire.add_argument('--id', required=True); retire.add_argument('--reason', required=True)
    dismiss = commands.add_parser('dismiss'); dismiss.add_argument('--event', required=True); dismiss.add_argument('--reason', required=True)
    finish = commands.add_parser('finish'); finish.add_argument('--session', required=True); finish.add_argument('--host')
    export = commands.add_parser('export'); export.add_argument('--include-events', action='store_true'); export.add_argument('--session'); export.add_argument('--out', type=Path, required=True)
    seal = commands.add_parser('seal'); seal.add_argument('file'); seal.add_argument('--out', type=Path, required=True)
    transfer = commands.add_parser('import'); transfer.add_argument('file'); transfer.add_argument('--owner', required=True)
    args = ap.parse_args()
    try:
        with contextlib.closing(Store(args.store or root_path(), create=args.command == 'init')) as store:
            if args.command == 'init': result = store.init(args.owner, args.profile_id, args.host, args.durability, args.enable_learning)
            elif args.command == 'status': result = store.status(args.profile)
            elif args.command == 'context':
                result = store.context(args.profile, args.host, args.project, args.tags.split(','))
                if args.markdown:
                    print(result['active_markdown'], end=''); return 0
            elif args.command == 'capture': result = store.capture(args.profile, read_json(args.file))
            elif args.command == 'promote': result = store.promote(args.profile, read_json(args.file))
            elif args.command == 'pending': result = store.pending(args.profile)
            elif args.command == 'transfers': result = store.transfers(args.profile)
            elif args.command == 'examples': result = store.examples(args.profile, args.pattern, args.limit)
            elif args.command == 'retire': result = store.retire(args.profile, args.id, args.reason)
            elif args.command == 'dismiss': result = store.dismiss(args.profile, args.event, args.reason)
            elif args.command == 'finish': result = store.finish(args.profile, args.session, args.host)
            elif args.command == 'import': result = store.import_data(args.profile, read_json(args.file), args.owner)
            elif args.command == 'seal':
                incoming = read_json(args.file)
                if not isinstance(incoming, dict):
                    raise ValueError('A transfer input must be an object.')
                payload = incoming.get('payload', incoming)
                if not isinstance(payload, dict):
                    raise ValueError('A transfer payload must be an object.')
                if payload.get('version') != VERSION or not isinstance(payload.get('rules'), list) or not isinstance(payload.get('events'), list):
                    raise ValueError('A transfer payload needs version 1, rules and events.')
                text(payload.get('owner'), 'owner', 100); identifier(payload.get('profile'))
                result = {'payload': payload, 'sha256': digest(payload)}
                with os.fdopen(os.open(args.out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'w', encoding='utf-8') as stream:
                    stream.write(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
                result = {'file': str(args.out.resolve()), 'sha256': result['sha256'], 'authority': 'Checksum only; import still requires owner confirmation and review.'}
            elif args.command == 'export':
                result = store.export(args.profile, args.include_events, args.session)
                if len(json.dumps(result, ensure_ascii=False)) > 1000000:
                    raise ValueError('Transfer too large. Export raw events for one --session at a time.')
                with os.fdopen(os.open(args.out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'w', encoding='utf-8') as stream:
                    stream.write(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
                result = {'file': str(args.out.resolve()), 'sha256': result['sha256'], 'includes_events': args.include_events}
        print(json.dumps(result, indent=2, ensure_ascii=False)); return 0
    except (ValueError, OSError, sqlite3.Error, KeyError, TypeError, RecursionError) as exc:
        print(str(exc), file=sys.stderr); return 2


if __name__ == '__main__':
    raise SystemExit(main())
