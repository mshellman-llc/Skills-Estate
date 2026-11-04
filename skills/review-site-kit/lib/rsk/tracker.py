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


# Jira wiki headings (*Title*, h2. Title) and Markdown headings of level 2 or more.
# A single '#' starts a numbered list item in Jira wiki markup, so it is never a heading.
HEADING = re.compile(r'(?:\*[^*]+\*:?|h\d\.\s*.+|#{2,6}\s+.+|\*\*[^*]+\*\*:?)')


def section(description, name):
    lines, out, active = (description or '').replace('\r', '').split('\n'), [], False
    for line in lines:
        stripped = line.strip()
        if HEADING.fullmatch(stripped):
            title = re.sub(r'^(h\d\.|#+)\s*', '', stripped).strip('*: ').lower()
            if active:
                break
            if title.startswith(name.lower()):
                active = True
            continue
        if active and stripped:
            out.append(line)
    return out


def acceptance(description, base_url=''):
    out = []
    for line in section(description, 'Acceptance Criteria'):
        bullet = re.match(r'\s*(#+|\*+|-)\s*(.*)', line)
        text = clean(bullet.group(2) if bullet else line, base_url)
        if not text:
            continue
        nested = bullet and bullet.group(1)[0] in '#*' and len(bullet.group(1)) > 1
        out.append(('  ' if nested else '') + text)
    return out


def background(description, base_url=''):
    return [t for t in (clean(line, base_url) for line in section(description, 'Background')) if t]


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
    types = {}
    for record in rows:
        key = (record.get('Issue key') or [''])[0]
        types[key] = (record.get('Issue Type') or [''])[0]
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
        parent = first('Parent key') or first('Parent') or None
        epic = first('Custom field (Epic Link)')
        if not epic and parent and types.get(parent, 'Epic') == 'Epic':
            epic = parent
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
    tickets, warnings = [], []
    get = lambda row, field: (row.get(columns[field]) if field in columns else None) or ''
    for row in rows:
        key = get(row, 'key').strip()
        if not key:
            continue
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
            'acceptance': acceptance(description, base_url) or _split(get(row, 'acceptance')),
            'background': background(description, base_url),
            'blocked_by': _split(get(row, 'blocked_by')), 'blocks': _split(get(row, 'blocks')),
            'comment_count': 0,
        })
    return tickets, warnings


def json_tickets(path):
    data = json.loads(Path(path).read_text())
    items = data['tickets'] if isinstance(data, dict) else data
    return items, []


def load(path, config):
    tracker = config.get('tracker', {})
    adapter = tracker.get('adapter', 'jira-csv')
    base_url = tracker.get('base_url', '')
    if adapter == 'jira-csv':
        tickets, warnings = jira_csv(path, base_url, tracker.get('status_map'))
    elif adapter == 'table-csv':
        tickets, warnings = table_csv(path, tracker.get('columns', {}), base_url, tracker.get('status_map'))
    elif adapter == 'json':
        tickets, warnings = json_tickets(path)
    else:
        raise ValueError(f'unknown tracker adapter: {adapter}')
    document = {'format': 1,
                'source': {'adapter': adapter, 'file': Path(path).name, 'sha256': _sha(path),
                           'rows': len(tickets), 'base_url': base_url},
                'tickets': tickets}
    validate.require(document, 'tickets')
    return document, warnings


# ---------- intake record and delta ----------

FIELDS = ('summary', 'status', 'sprint', 'points', 'epic', 'type', 'description_sha', 'blocked_by')


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

