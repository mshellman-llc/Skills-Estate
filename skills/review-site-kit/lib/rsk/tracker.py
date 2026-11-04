"""Tracker adapters, description parsing, intake records and deltas.

Every adapter returns the canonical tickets document (schema/tickets.schema.json).
Downstream code reads only that document, so a new tracker needs one adapter.
"""
import csv
import datetime as dt
import hashlib
import json
import re
from pathlib import Path

from . import validate

csv.field_size_limit(10 ** 9)

DEFAULT_CATEGORIES = {
    'done': ['done', 'closed', 'resolved', 'complete', 'completed', 'released', 'deployed'],
    'canceled': ['canceled', 'cancelled', "won't do", 'wont do', 'rejected', 'duplicate'],
    'blocked': ['blocked', 'on hold'],
    'todo': ['to do', 'todo', 'backlog', 'open', 'new', 'needs refinement', 'refinement',
             'prioritize', 'ready', 'ready for dev', 'selected for development'],
}
WIP_HINTS = ('progress', 'review', 'sqa', 'qa', 'test', 'uat', 'develop', 'build')


def categorize(status, status_map=None):
    """Map a tracker status to todo, wip, done, canceled or blocked. Returns (category, known)."""
    status_map = {k.lower(): v for k, v in (status_map or {}).items()}
    key = (status or '').strip().lower()
    if key in status_map:
        return status_map[key], True
    for category, names in DEFAULT_CATEGORIES.items():
        if key in names:
            return category, True
    if any(hint in key for hint in WIP_HINTS):
        return 'wip', True
    return 'todo', False


# ---------- description text ----------

def clean(text, base_url=''):
    text = re.sub(r'\[([^\]|]+)\|([^\]|]+)(\|smart-link)?\]',
                  lambda m: m.group(2) if m.group(1) == m.group(2) else m.group(1), text)
    if base_url:
        text = re.sub(re.escape(base_url.rstrip('/')) + r'/(?:browse/)?([A-Z][A-Z0-9]+-\d+)', r'\1', text)
    text = re.sub(r'\{\{([^}]*)\}\}', r'\1', text)
    text = re.sub(r'(?<![\w*])\*([^*\n]+)\*(?![\w*])', r'\1', text)
    text = re.sub(r'(?<![\w_])_([^_\n]+)_(?![\w_])', r'\1', text)
    text = re.sub(r'\*\*([^*\n]+)\*\*', r'\1', text)
    text = text.replace(' ', ' ')
    return re.sub(r'[ \t]+', ' ', text).strip()


# Section headings differ by markup. Jira wiki uses *Title* or h2. Title, and a
# leading # or ## starts a numbered list item, so it is never a heading there.
# Markdown (table exports from other trackers) uses ## Title or **Title**.
# Both accept a known section name alone on its line, with or without a colon.
WIKI_HEADING = re.compile(r'(?:\*[^*]+\*:?|h\d\.\s*.+)')
MARKDOWN_HEADING = re.compile(r'(?:#{1,6}\s+.+|\*\*[^*]+\*\*:?)')
KNOWN_SECTIONS = ('background', 'acceptance criteria', 'acceptance', 'description', 'notes', 'technical notes',
                  'dependencies', 'out of scope', 'open questions', 'user story', 'definition of done', 'requirements')


def _title(line):
    return re.sub(r'^(h\d\.|#+)\s*', '', line).strip('*: ').lower()


def section(description, name, markup='wiki'):
    heading = WIKI_HEADING if markup == 'wiki' else MARKDOWN_HEADING
    lines, out, active = (description or '').replace('\r', '').split('\n'), [], False
    for line in lines:
        stripped = line.strip()
        if heading.fullmatch(stripped) or stripped.rstrip(':').strip().lower() in KNOWN_SECTIONS:
            if active:
                break
            if _title(stripped).startswith(name.lower()):
                active = True
            continue
        if active and stripped:
            out.append(line)
    return out


def acceptance(description, base_url='', markup='wiki'):
    out = []
    for line in section(description, 'Acceptance Criteria', markup):
        bullet = re.match(r'\s*(#+|\*+|-)\s+(.*)', line) or re.match(r'\s*(\d+)[.)]\s+(.*)', line)
        text = clean(bullet.group(2) if bullet else line, base_url)
        if not text:
            continue
        marker = bullet.group(1) if bullet else ''
        nested = marker[:1] in ('#', '*') and len(marker) > 1 or (bullet and line[:1] in ' \t' and markup != 'wiki')
        out.append(('  ' if nested else '') + text)
    return out


def background(description, base_url='', markup='wiki'):
    return [t for t in (clean(line, base_url) for line in section(description, 'Background', markup)) if t]


# ---------- adapters ----------

def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _points(value):
    try:
        return float(value) if value not in (None, '') else None
    except ValueError:
        return None


DATE_FORMATS = ('%d-%b-%y %I:%M %p', '%d/%b/%y %I:%M %p', '%d/%b/%Y %I:%M %p', '%Y-%m-%d %H:%M', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d', '%m/%d/%Y')


def _date(value):
    """Return an ISO timestamp for the export's date formats, or the raw text when none fits."""
    if not value:
        return None
    text = value.strip()
    for fmt in DATE_FORMATS:
        try:
            return dt.datetime.strptime(text, fmt).isoformat(timespec='minutes')
        except ValueError:
            pass
    try:
        return dt.datetime.fromisoformat(text.replace('Z', '+00:00')).isoformat(timespec='minutes')
    except ValueError:
        return text


def _sprint_sort(name):
    numbers = re.findall(r'\d+', name or '')
    return (int(numbers[-1]) if numbers else 10 ** 6, name or '')


SUBTASK = re.compile(r'sub-?task', re.I)


def _epic_of(key, parent, types, parents):
    """A story's parent is its epic; a sub-task's epic is its parent's parent.

    When the parent is not in the export, a non-sub-task's parent is taken as its
    epic, which is how Jira's issue hierarchy works; a sub-task gets no epic.
    """
    if not parent:
        return None
    kind = types.get(parent)
    if kind == 'Epic':
        return parent
    if SUBTASK.search(types.get(key, '')):
        grand = parents.get(parent)
        return grand if grand and types.get(grand) == 'Epic' else None
    return parent if kind is None else None


def jira_csv(path, base_url='', status_map=None):
    """Jira 'All fields' CSV. Repeated headers (Sprint, Labels, links, Comment) become lists."""
    with open(path, encoding='utf-8-sig', newline='') as handle:
        reader = csv.reader(handle)
        header = next(reader)
        rows = []
        for row in reader:
            record = {}
            for name, value in zip(header, row):
                if value != '':
                    record.setdefault(name, []).append(value)
            rows.append(record)
    point_columns = [h for h in dict.fromkeys(header) if re.search(r'story ?point', h, re.I)]
    types, ids, parents = {}, {}, {}
    for record in rows:
        key = (record.get('Issue key') or [''])[0]
        types[key] = (record.get('Issue Type') or [''])[0]
        if record.get('Issue id'):
            ids[record['Issue id'][0]] = key
    for record in rows:
        key = (record.get('Issue key') or [''])[0]
        raw = (record.get('Parent key') or record.get('Parent') or [None])[0]
        parents[key] = ids.get(raw, raw) if raw else None
    tickets, warnings, seen = [], [], set()
    for record in rows:
        first = lambda name: (record.get(name) or [None])[0]
        key = first('Issue key')
        if not key:
            warnings.append('row without an Issue key skipped')
            continue
        if key in seen:
            warnings.append(f'duplicate key {key}; first row kept')
            continue
        seen.add(key)
        status = first('Status') or ''
        category, known = categorize(status, status_map)
        if not known:
            warnings.append(f'{key}: status "{status}" mapped to todo; add it to tracker.status_map')
        parent = parents.get(key)
        if parent and not re.fullmatch(r'[A-Z][A-Z0-9_]*-\d+', parent):
            warnings.append(f'{key}: parent {parent} is not in this export; epic left empty')
            parent = None
        epic = first('Custom field (Epic Link)') or _epic_of(key, parent, types, parents)
        sprints = sorted(set(record.get('Sprint', [])), key=_sprint_sort)
        description = first('Description') or ''
        points = next((_points(first(c)) for c in point_columns if _points(first(c)) is not None), None)
        links = {name: values for name, values in record.items() if 'issue link' in name.lower()}
        blocked_by = [v for name, values in links.items() if name.lower().startswith('inward issue link (blocks)') for v in values]
        blocks = [v for name, values in links.items() if name.lower().startswith('outward issue link (blocks)') for v in values]
        tickets.append({
            'key': key, 'summary': first('Summary') or '', 'type': first('Issue Type') or '',
            'status': status, 'category': category, 'epic': epic, 'parent': parent,
            'sprint': sprints[-1] if sprints else None, 'sprints': sprints, 'points': points,
            'labels': sorted(set(record.get('Labels', []))), 'priority': first('Priority'),
            'created': _date(first('Created')), 'updated': _date(first('Updated')),
            'description_sha': hashlib.sha256(description.encode()).hexdigest()[:12],
            'acceptance': acceptance(description, base_url), 'background': background(description, base_url),
            'blocked_by': sorted(set(blocked_by)), 'blocks': sorted(set(blocks)),
            'comment_count': len(record.get('Comment', [])),
        })
    return tickets, warnings


def _split(value):
    return [v.strip() for v in re.split(r'[;,]', value or '') if v.strip()]


def table_csv(path, columns, base_url='', status_map=None):
    """Any tracker exported as a table. `columns` maps canonical fields to column names."""
    need = {'key', 'summary', 'status'}
    if not need <= set(columns):
        raise ValueError('tracker.columns must name key, summary and status')
    with open(path, encoding='utf-8-sig', newline='') as handle:
        rows = list(csv.DictReader(handle))
    tickets, warnings, seen = [], [], set()
    get = lambda row, field: (row.get(columns[field]) if field in columns else None) or ''
    for row in rows:
        key = get(row, 'key').strip()
        if not key:
            continue
        if key in seen:
            warnings.append(f'duplicate key {key}; first row kept')
            continue
        seen.add(key)
        status = get(row, 'status')
        category, known = categorize(status, status_map)
        if not known:
            warnings.append(f'{key}: status "{status}" mapped to todo; add it to tracker.status_map')
        description = get(row, 'description')
        sprints = _split(get(row, 'sprint'))
        tickets.append({
            'key': key, 'summary': get(row, 'summary'), 'type': get(row, 'type'), 'status': status,
            'category': category, 'epic': get(row, 'epic') or None, 'parent': get(row, 'parent') or None,
            'sprint': sprints[-1] if sprints else None, 'sprints': sprints, 'points': _points(get(row, 'points')),
            'labels': _split(get(row, 'labels')), 'priority': get(row, 'priority') or None,
            'created': _date(get(row, 'created')), 'updated': _date(get(row, 'updated')),
            'description_sha': hashlib.sha256(description.encode()).hexdigest()[:12],
            'acceptance': acceptance(description, base_url, 'markdown') or _split(get(row, 'acceptance')),
            'background': background(description, base_url, 'markdown'),
            'blocked_by': _split(get(row, 'blocked_by')), 'blocks': _split(get(row, 'blocks')),
            'comment_count': 0,
        })
    return tickets, warnings


FIELDS_KEPT = ('key', 'summary', 'type', 'status', 'category', 'epic', 'parent', 'sprint', 'sprints', 'points',
               'labels', 'priority', 'created', 'updated', 'description_sha', 'acceptance', 'background',
               'blocked_by', 'blocks', 'comment_count')


def json_tickets(path, base_url='', status_map=None):
    """Tickets pulled through a connector. Each is rebuilt from the kept fields only,
    so comments, people and full descriptions never reach tickets.json."""
    data = json.loads(Path(path).read_text())
    items = data['tickets'] if isinstance(data, dict) else data
    tickets, warnings, seen = [], [], set()
    for item in items:
        key = str(item.get('key') or '').strip()
        if not key or key in seen:
            warnings.append(f'ticket without a key or duplicate key {key!r} skipped')
            continue
        seen.add(key)
        status = str(item.get('status') or '')
        category, known = categorize(status, status_map)
        if item.get('category') in ('todo', 'wip', 'done', 'canceled', 'blocked') and not status_map:
            category, known = item['category'], True
        if not known:
            warnings.append(f'{key}: status "{status}" mapped to todo; add it to tracker.status_map')
        description = item.get('description') or ''
        sprints = list(item.get('sprints') or ([item['sprint']] if item.get('sprint') else []))
        ticket = {name: item.get(name) for name in FIELDS_KEPT}
        ticket.update({
            'key': key, 'summary': str(item.get('summary') or ''), 'type': str(item.get('type') or ''),
            'status': status, 'category': category, 'sprints': sprints, 'sprint': sprints[-1] if sprints else None,
            'points': _points(item.get('points')), 'labels': list(item.get('labels') or []),
            'created': _date(item.get('created')), 'updated': _date(item.get('updated')),
            'description_sha': item.get('description_sha') or hashlib.sha256(description.encode()).hexdigest()[:12],
            'acceptance': list(item.get('acceptance') or acceptance(description, base_url, 'markdown')),
            'background': list(item.get('background') or background(description, base_url, 'markdown')),
            'blocked_by': sorted(set(item.get('blocked_by') or [])), 'blocks': sorted(set(item.get('blocks') or [])),
            'comment_count': int(item.get('comment_count') or len(item.get('comments') or [])),
        })
        tickets.append(ticket)
    return tickets, warnings


def _inverse_links(tickets):
    """A Blocks link recorded on only one side is copied to the other side."""
    by_key = {t['key']: t for t in tickets}
    for t in tickets:
        for other in t['blocks']:
            if other in by_key and t['key'] not in by_key[other]['blocked_by']:
                by_key[other]['blocked_by'] = sorted(by_key[other]['blocked_by'] + [t['key']])
        for other in t['blocked_by']:
            if other in by_key and t['key'] not in by_key[other]['blocks']:
                by_key[other]['blocks'] = sorted(by_key[other]['blocks'] + [t['key']])


def load(path, config):
    tracker = config.get('tracker', {})
    adapter = tracker.get('adapter', 'jira-csv')
    base_url = tracker.get('base_url', '')
    if adapter == 'jira-csv':
        tickets, warnings = jira_csv(path, base_url, tracker.get('status_map'))
    elif adapter == 'table-csv':
        tickets, warnings = table_csv(path, tracker.get('columns', {}), base_url, tracker.get('status_map'))
    elif adapter == 'json':
        tickets, warnings = json_tickets(path, base_url, tracker.get('status_map'))
    else:
        raise ValueError(f'unknown tracker adapter: {adapter}')
    _inverse_links(tickets)
    document = {'format': 1,
                'source': {'adapter': adapter, 'file': Path(path).name, 'sha256': _sha(path),
                           'rows': len(tickets), 'base_url': base_url},
                'tickets': tickets}
    validate.require(document, 'tickets')
    return document, warnings


# ---------- intake record and delta ----------

FIELDS = ('summary', 'status', 'category', 'sprint', 'points', 'epic', 'type', 'description_sha', 'blocked_by')


def delta(previous, current):
    old = {t['key']: t for t in (previous or {}).get('tickets', [])}
    new = {t['key']: t for t in current['tickets']}
    changed = []
    for key in sorted(set(old) & set(new), key=natural):
        diffs = {f: [old[key].get(f), new[key].get(f)] for f in FIELDS if old[key].get(f) != new[key].get(f)}
        if diffs:
            changed.append({'key': key, 'changes': diffs})
    return {'format': 1,
            'previous_sha256': (previous or {}).get('source', {}).get('sha256'),
            'current_sha256': current['source']['sha256'],
            'added': sorted(set(new) - set(old), key=natural),
            'removed': sorted(set(old) - set(new), key=natural),
            'changed': changed}


def natural(key):
    parts = re.split(r'(\d+)', key or '')
    return [int(p) if p.isdigit() else p for p in parts]


def intake_record(path, document, warnings, origin, scope, previous=None, redactions=None):
    return {'format': 1,
            'original_name': Path(path).name,
            'sha256': document['source']['sha256'],
            'received': dt.date.today().isoformat(),
            'origin': origin, 'scope': scope,
            'adapter': document['source']['adapter'],
            'tickets': len(document['tickets']),
            'latest_update': max((t.get('updated') or '' for t in document['tickets']), default=''),
            'redactions': redactions if redactions is not None else
                ['comment text dropped; counts kept', 'assignee and reporter dropped', 'description kept only as acceptance and background extracts'],
            'conflicts': warnings,
            'previous_sha256': (previous or {}).get('source', {}).get('sha256')}

