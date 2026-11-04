"""Decision register: checks, merging saved answers, and round-trip exports.

Saved answers come from the published page's shared store (collection `answers`,
one document per question id) or a browser export of the same records.
"""
import csv
import io
import json
from pathlib import Path

STATUSES = ['Open', 'Proposed', 'Partly answered', 'Answered', 'Deferred', 'Blocked', 'Sandbox check']
CLASS_NAMES = {'must': 'Must', 'should': 'Should', 'could': 'Could', 'wont': "Won't"}


def problems(questions_doc, stories=None, tickets=None):
    found = []
    ids = [q['id'] for q in questions_doc['questions']]
    groups = {g['id'] for g in questions_doc['groups']}
    for qid in {i for i in ids if ids.count(i) > 1}:
        found.append(f'duplicate question id {qid}')
    story_ids = {s['id'] for s in stories or []}
    for q in questions_doc['questions']:
        if q['group'] not in groups:
            found.append(f'{q["id"]}: unknown group {q["group"]}')
        for sid in q.get('stories', []):
            if stories is not None and sid not in story_ids:
                found.append(f'{q["id"]}: unknown story {sid}')
        for key in q.get('tickets', []):
            if tickets is not None and key not in tickets:
                found.append(f'{q["id"]}: ticket {key} not in the tracker export')
    return found


def load_saved(path):
    """Accept {id: record}, [{id, data}] or {"answers": ...} from the store or a browser export."""
    if not path:
        return {}
    data = json.loads(Path(path).read_text())
    if isinstance(data, dict) and 'answers' in data and isinstance(data['answers'], (dict, list)):
        data = data['answers']
    if isinstance(data, list):
        return {item.get('id') or item.get('doc_id'): item.get('data', item) for item in data}
    return data


def load_reviews(path):
    if not path:
        return {}
    data = json.loads(Path(path).read_text())
    for key in ('moscow', 'reviews'):
        if isinstance(data, dict) and key in data:
            data = data[key]
    if isinstance(data, list):
        return {item.get('id') or item.get('doc_id'): item.get('data', item) for item in data}
    return data


def merged(questions_doc, saved):
    """Current view of each question: saved status and answer win over the authored ones."""
    rows = []
    for q in questions_doc['questions']:
        s = saved.get(q['id'], {})
        status = s.get('status') or ('Answered' if s.get('state') in ('Answered', 'Proposal accepted') else q['status'])
        answer = s.get('answer') or (q.get('answer') or {}).get('text', '')
        rows.append({'id': q['id'], 'group': q['group'], 'question': q['text'], 'status': status,
                     'answer': answer, 'conditions': s.get('conditions', ''), 'state': s.get('state', ''),
                     'updated': s.get('at', ''), 'tickets': ' '.join(q.get('tickets', []))})
    return rows


def export_csv(questions_doc, saved):
    """A table the client can import into the tracker as comments or a decision log."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(['Issue key', 'Question id', 'Question', 'Status', 'Answer', 'Conditions', 'Updated'])
    for row in merged(questions_doc, saved):
        keys = row['tickets'].split() or ['']
        for key in keys:
            writer.writerow([key, row['id'], row['question'], row['status'], row['answer'], row['conditions'], row['updated']])
    return buffer.getvalue()


def export_markdown(questions_doc, saved):
    groups = {g['id']: g['label'] for g in questions_doc['groups']}
    lines, current = ['# Decision log', ''], None
    for row in merged(questions_doc, saved):
        if row['group'] != current:
            current = row['group']
            lines += [f'## {groups.get(current, current)}', '']
        lines.append(f'**{row["question"]}** ({row["status"]})')
        if row['answer']:
            lines.append(f'Answer: {row["answer"]}')
        if row['conditions']:
            lines.append(f'Conditions: {row["conditions"]}')
        if row['tickets']:
            lines.append(f'Tickets: {row["tickets"]}')
        lines.append('')
    return '\n'.join(lines)


def export_reviews(stories, reviews):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(['Story id', 'Story', 'Issue key', 'Class on the map', 'Class decided', 'Note', 'Updated'])
    for s in stories:
        r = reviews.get(s['id'])
        if not r:
            continue
        decided = r.get('class') or s['class']
        for key in s.get('tickets') or ['']:
            writer.writerow([s['id'], s['label'], key, CLASS_NAMES[s['class']],
                             CLASS_NAMES.get(decided, decided), r.get('note', ''), r.get('at', '')])
    return buffer.getvalue()
