"""Story map calculations: tracker sync, readiness, Must share, unclassed tickets,
critical path and candidate mapping for new tickets.

Authored story fields (label, what, interim, class) are never rewritten here.
Computed fields are recalculated on every run and written under `computed`.
"""
import html
import re

from .tracker import natural

CLASSES = ('must', 'should', 'could', 'wont')
DEFAULT_CLASS_LABELS = {'must': 'Must', 'should': 'Should', 'could': 'Could', 'wont': "Won't"}
OPEN_QUESTION = {'Open', 'Blocked', 'Partly answered', 'Sandbox check', 'Proposed'}
DEFAULT_READINESS = ['acceptance', 'estimate', 'no_open_questions', 'no_blocked_dependency']


def index(tickets_doc):
    return {t['key']: t for t in tickets_doc['tickets']}


def story_status(story, tickets):
    keys = [k for k in story.get('tickets', []) if k in tickets]
    if not story.get('tickets'):
        return {'category': 'untracked', 'label': 'Not in the tracker yet'}
    if not keys:
        return {'category': 'missing', 'label': 'Ticket not in this export'}
    primary = tickets[keys[0]]
    return {'category': primary['category'], 'label': primary['status']}


def open_blockers(story, tickets, stories_by_id):
    found = []
    for key in story.get('tickets', []):
        for blocker in tickets.get(key, {}).get('blocked_by', []):
            ticket = tickets.get(blocker)
            if ticket is None or ticket['category'] not in ('done', 'canceled'):
                found.append(blocker)
    for dep in story.get('depends_on', []):
        other = stories_by_id.get(dep)
        if other is not None and not other.get('tickets'):
            found.append(dep)
    return sorted(set(found), key=natural)


def sync(stories_doc, tickets_doc, questions_doc=None, config=None):
    """Return a new list of stories with a `computed` block. Inputs are not modified."""
    config = config or {}
    tickets = index(tickets_doc)
    by_id = {s['id']: s for s in stories_doc['stories']}
    questions = (questions_doc or {}).get('questions', [])
    rules = config.get('readiness') or DEFAULT_READINESS
    out = []
    for story in stories_doc['stories']:
        keys = story.get('tickets', [])
        present = [tickets[k] for k in keys if k in tickets]
        primary = present[0] if present else None
        status = story_status(story, tickets)
        accept = story.get('acceptance') or [line for t in present for line in t.get('acceptance', [])]
        linked = [q for q in questions if story['id'] in q.get('stories', [])
                  or set(keys) & set(q.get('tickets', []))]
        open_q = [q['id'] for q in linked if q['status'] in OPEN_QUESTION]
        blockers = open_blockers(story, tickets, by_id)
        points = primary.get('points') if primary else None
        checks = {
            'acceptance': bool(accept),
            'estimate': points is not None,
            'no_open_questions': not open_q,
            'no_blocked_dependency': not blockers,
            'ticketed': bool(present),
        }
        done = status['category'] == 'done'
        ready = done or all(checks[r] for r in rules)
        computed = {'status': status, 'sprint': primary.get('sprint') if primary else None,
                    'points': points, 'acceptance': accept, 'questions': [q['id'] for q in linked],
                    'open_questions': open_q, 'blockers': blockers,
                    'checks': {r: checks[r] for r in rules}, 'ready': ready,
                    'epic': story.get('epic') or (primary.get('epic') if primary else None) or story.get('planned_in')}
        out.append({**story, 'computed': computed})
    return out


def must_share(stories):
    """Open points by class and the Must share of Must+Should+Could open points."""
    totals = {c: 0.0 for c in CLASSES}
    unestimated = 0
    for story in stories:
        c = story['computed']
        if c['status']['category'] in ('done', 'canceled'):
            continue
        if c['points'] is None:
            if story['class'] in ('must', 'should'):
                unestimated += 1
            continue
        totals[story['class']] += c['points']
    scoped = totals['must'] + totals['should'] + totals['could']
    share = totals['must'] / scoped if scoped else 0.0
    return {'open_points': totals, 'must_share': round(share, 4), 'unestimated_must_should': unestimated}


def unclassed(stories, tickets_doc, config=None):
    """Open tickets under the release's epics that no story references."""
    config = config or {}
    epics = set(config.get('release_epics') or [s['computed']['epic'] for s in stories if s['computed']['epic']])
    referenced = {k for s in stories for k in s.get('tickets', [])}
    out = []
    for t in tickets_doc['tickets']:
        if t.get('epic') in epics and t['key'] not in referenced and t['key'] not in epics \
                and t['category'] not in ('done', 'canceled') and (t.get('type') or '').lower() != 'epic':
            out.append({'key': t['key'], 'summary': t['summary'], 'epic': t['epic'], 'status': t['status']})
    return sorted(out, key=lambda x: natural(x['key']))


def _sprint_columns(keys, tickets, order):
    found = {tickets[k].get('sprint') for k in keys if k in tickets and tickets[k].get('sprint')}
    ordered = [s for s in (order or []) if s in found]
    ordered += sorted(found - set(ordered), key=natural)
    return ordered + ['No sprint']


def critical_path(stories, tickets_doc, config=None, classes=None):
    """Open Must tickets plus their open upstream blockers, laid out by sprint, as SVG markup.

    Colors come from CSS custom properties so the page's brand profile applies.
    Done tickets drop off; canceled blockers show as dashed arrows.
    """
    config = config or {}
    tickets = index(tickets_doc)
    labels = {**DEFAULT_CLASS_LABELS, **(classes or {})}
    must = [s for s in stories if s['class'] == 'must']
    by_key = {}
    for s in stories:
        for k in s.get('tickets', [])[:1]:
            by_key.setdefault(k, s)
    nodes = {s['tickets'][0] for s in must if s.get('tickets') and s['tickets'][0] in tickets
             and tickets[s['tickets'][0]]['category'] not in ('done', 'canceled')}
    stack = list(nodes)
    while stack:
        key = stack.pop()
        for blocker in tickets.get(key, {}).get('blocked_by', []):
            t = tickets.get(blocker)
            if blocker not in nodes and (t is None or t['category'] != 'done'):
                nodes.add(blocker)
                stack.append(blocker)
    edges = [(b, k) for k in nodes for b in tickets.get(k, {}).get('blocked_by', []) if b in nodes]
    untracked = [s for s in must if not s.get('tickets')]
    columns = _sprint_columns(nodes, tickets, config.get('tracker', {}).get('sprint_order'))
    column_of = lambda k: (tickets.get(k, {}).get('sprint') or 'No sprint') if k in tickets else 'No sprint'
    rows, layout = {}, {}
    ordered = sorted(nodes, key=natural) + [s['id'] for s in untracked]
    for column in columns:
        used = set()
        for key in [k for k in ordered if (column_of(k) if k in nodes else 'No sprint') == column]:
            parents = [rows[b] for b, a in edges if a == key and b in rows]
            want = round(sum(parents) / len(parents)) if parents else 0
            while want in used:
                want += 1
            used.add(want)
            rows[key] = want
            layout[key] = (columns.index(column), want)
    W, H, GX, GY, X0, Y0 = 250, 50, 110, 14, 4, 34
    width = X0 * 2 + len(columns) * W + (len(columns) - 1) * GX + 40
    height = Y0 + (max(rows.values(), default=0) + 1) * (H + GY) + 8
    pos = {k: (X0 + c * (W + GX), Y0 + r * (H + GY)) for k, (c, r) in layout.items()}
    base = config.get('tracker', {}).get('base_url', '')
    out = [f'<svg class="cp" viewBox="0 0 {width} {height}" role="img" aria-label="Open Must stories and their blockers by sprint">',
           '<defs>' + ''.join(f'<marker id="cp-{n}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="cp-head-{n}"/></marker>' for n in ('fwd', 'back', 'off')) + '</defs>']
    for i, column in enumerate(columns):
        out.append(f'<text class="cp-col" x="{X0 + i * (W + GX)}" y="20">{html.escape(column)}</text>')
    for a, b in edges:
        (ax, ay), (bx, by) = pos[a], pos[b]
        ay, by = ay + H / 2, by + H / 2
        kind = 'off' if tickets.get(a, {}).get('category') == 'canceled' else ('back' if bx < ax else 'fwd')
        if bx > ax:
            d = f'M{ax + W} {ay} C{ax + W + 55} {ay} {bx - 55} {by} {bx} {by}'
        elif bx == ax:
            d = f'M{ax + W} {ay} C{ax + W + 40} {ay} {ax + W + 40} {by} {ax + W} {by}'
        else:
            d = f'M{ax} {ay} C{ax - 55} {ay} {bx + W + 55} {by} {bx + W} {by}'
        out.append(f'<path class="cp-edge cp-{kind}" d="{d}" marker-end="url(#cp-{kind})"/>')

    def box(x, y, title, sub, kind, href):
        title = title if len(title) <= 34 else title[:33] + '…'
        body = (f'<g class="cp-node cp-{kind}"><rect x="{x}" y="{y}" width="{W}" height="{H}"/>'
                f'<text class="cp-t" x="{x + 10}" y="{y + 21}">{html.escape(title)}</text>'
                f'<text class="cp-s" x="{x + 10}" y="{y + 39}">{html.escape(sub)}</text></g>')
        return f'<a href="{html.escape(href)}" target="_blank" rel="noopener">{body}</a>' if href else body

    untracked_by_id = {s['id']: s for s in untracked}
    for key, (x, y) in pos.items():
        if key in untracked_by_id:
            s = untracked_by_id[key]
            out.append(box(x, y, s['label'], 'Not in the tracker yet · ' + labels['must'], 'untracked', ''))
            continue
        t = tickets.get(key)
        story = by_key.get(key)
        href = base + key if base else ''
        if story and t:
            out.append(box(x, y, story['label'], f'{key} · {labels[story["class"]]} · {t["status"]}', story['class'], href))
        elif t:
            out.append(box(x, y, t['summary'], f'{key} · {t["status"]}', 'outside', href))
        else:
            out.append(box(x, y, key, f'{key} · not in this export', 'outside', href))
    out.append('</svg>')
    return {'svg': ''.join(out), 'nodes': sorted(nodes, key=natural), 'edges': sorted(edges),
            'untracked': [s['id'] for s in untracked], 'columns': columns}


WORD = re.compile(r'[a-z0-9]{3,}')
STOP = {'the', 'and', 'for', 'with', 'from', 'opportunity', 'opportunities', 'add', 'update', 'create', 'new'}


def candidates(ticket, stories, limit=3):
    """Rank stories a new ticket may belong to, by shared words and epic. The model decides."""
    words = set(WORD.findall(ticket['summary'].lower())) - STOP
    scored = []
    for s in stories:
        text = ' '.join([s['label'], s.get('what', '')]).lower()
        overlap = len(words & (set(WORD.findall(text)) - STOP))
        same_epic = 1 if ticket.get('epic') and ticket['epic'] == s['computed']['epic'] else 0
        score = overlap + 2 * same_epic
        if score:
            scored.append((score, s['id'], s['label']))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [{'story': sid, 'label': label, 'score': score} for score, sid, label in scored[:limit]]


def review_queue(delta, stories, tickets_doc):
    """Stories whose tickets changed, and new tickets with candidate stories."""
    tickets = index(tickets_doc)
    touched = {c['key']: c['changes'] for c in delta.get('changed', [])}
    affected = []
    for s in stories:
        hits = {k: touched[k] for k in s.get('tickets', []) if k in touched}
        if hits:
            affected.append({'story': s['id'], 'label': s['label'], 'changes': hits})
    referenced = {k for s in stories for k in s.get('tickets', [])}
    new = []
    for key in delta.get('added', []):
        t = tickets.get(key)
        if t and key not in referenced and (t.get('type') or '').lower() != 'epic':
            new.append({'key': key, 'summary': t['summary'], 'epic': t.get('epic'),
                        'status': t['status'], 'candidates': candidates(t, stories)})
    return {'affected_stories': affected, 'new_tickets': new, 'removed': delta.get('removed', [])}
