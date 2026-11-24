#!/usr/bin/env python3
"""Bound external writing reviews by artifact, across working folders and sessions."""
import contextlib
import fcntl
import json
import os
import uuid
from pathlib import Path

MAX_ROUNDS = 2


class PolicyError(ValueError):
    pass


def home():
    return Path(os.environ.get('WRITING_AGENT_HOME') or Path.home() / '.agents' / 'writing').expanduser()


def key(path):
    return str(Path(path).expanduser().resolve())


@contextlib.contextmanager
def ledger():
    base = home()
    base.mkdir(parents=True, exist_ok=True)
    with (base / 'review-policy.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        path = base / 'review-policy.json'
        data = json.loads(path.read_text()) if path.exists() else {}
        if not isinstance(data, dict):
            raise PolicyError('Review policy state is not an object; repair it before starting a reviewer.')
        yield data
        temp = path.with_suffix('.tmp')
        temp.write_text(json.dumps(data, indent=1) + '\n')
        temp.replace(path)


def read(path):
    with ledger() as data:
        return dict(data.get(key(path), {}))


def prepare(path, folder, digest, writers=(), requested=None):
    with ledger() as data:
        entry = data.setdefault(key(path), {'audience': 'external', 'rounds': [], 'writers': [],
                                             'reviewer_session': str(uuid.uuid4()), 'launches': 0, 'resumes': 0})
        entry['audience'] = 'external'
        entry['aliases'] = sorted(set(entry.get('aliases', [])) | {str(Path(path).expanduser().absolute()), key(path)})
        entry['writers'] = sorted(set(entry['writers']) | set(writers))
        directory = key(folder)
        same = next((r for r in reversed(entry['rounds']) if r['directory'] == directory and r['digest'] == digest), None)
        number = same['round'] if same else len(entry['rounds']) + 1
        if same and requested == len(entry['rounds']) + 1:
            number, same = requested, None
        if number > MAX_ROUNDS:
            raise PolicyError('The two-round review budget is exhausted. Keep remaining errors open; '
                              'do not start another reviewer or reset the review folder.')
        if requested is not None and requested != number:
            raise PolicyError(f'This artifact is on review round {number}; --round cannot reset or extend its budget.')
        if not same:
            entry['rounds'].append({'round': number, 'directory': directory, 'digest': digest})
        return dict(entry, round=number, max_reviewers=1, max_rounds=MAX_ROUNDS)


def validate(path, digest, documents, requested=None):
    """One reviewer supplies every pass; the writer stays separate."""
    with ledger() as data:
        entry = data.get(key(path))
        if not entry or not entry.get('rounds'):
            raise PolicyError('Declare external copy and prepare its review once with --audience external --prepare DIR.')
        current = entry['rounds'][-1]
        if current['digest'] != digest:
            raise PolicyError('The text or rules changed. Prepare the same review folder for the remaining round.')
        number = current['round']
        if requested is not None and requested != number:
            raise PolicyError(f'This artifact is on review round {number}; --round cannot reset or extend its budget.')
        names, sessions = set(), set()
        for doc in documents:
            name = str(doc.get('reviewer') or '').strip()
            if not name:
                raise PolicyError('Every review record, including the document map, must name the same reviewer.')
            names.update(x.strip() for x in name.split(' + ') if x.strip())
            sessions.update(x.strip() for x in str(doc.get('session') or '').split(' + ') if x.strip())
            sessions.update(doc.get('verdict_writers') or [])
        if len(names) != 1 or len(sessions) > 1:
            raise PolicyError('Only one independent reviewer may supply the line pass, document pass and spot audit.')
        name = next(iter(names))
        if entry.get('reviewer') and entry['reviewer'] != name:
            raise PolicyError('Continue with the original reviewer; do not replace it or launch another.')
        if name in entry['writers'] or sessions.intersection(entry['writers']):
            raise PolicyError('The independent reviewer cannot be the writer.')
        entry['reviewer'] = name
        if sessions:
            actual = next(iter(sessions))
            if entry.get('session_bound') and actual != entry['reviewer_session']:
                raise PolicyError('The review records must come from the reserved reviewer session.')
            entry['reviewer_session'] = actual
            entry['session_bound'] = True
        return dict(entry, round=number, max_reviewers=1, max_rounds=MAX_ROUNDS)


def internal(path):
    with ledger() as data:
        if key(path) in data:
            data[key(path)]['audience'] = 'internal'


def authorize_launch(session, text, resume=None, batch=False):
    with ledger() as data:
        choices = [e for path, e in data.items() if e.get('audience') == 'external'
                   and session in e.get('writers', [])
                   and any(alias in text for alias in [path, *e.get('aliases', [])])]
        if len(choices) != 1:
            raise PolicyError('Internal work stays in the main session. A reviewer requires one declared external file '
                              'prepared with the writer session ID; include that file in the review request.')
        entry = choices[0]
        if batch:
            raise PolicyError('Reviewer batches and parallel launches are disabled. Use the one reserved reviewer.')
        if resume:
            if resume != entry['reviewer_session'] or not entry['launches'] or entry['resumes'] >= 1:
                raise PolicyError('Only one follow-up in the original reviewer session is allowed.')
            entry['resumes'] += 1
        elif entry['launches']:
            raise PolicyError('This file already has its independent reviewer. Do not launch another.')
        else:
            entry['launches'] = 1
        return entry['reviewer_session']
