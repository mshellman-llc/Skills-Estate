"""Publish gates: data consistency, authored-writing check and browser rules.

A failing gate blocks publishing. Each result names the rule from
references/review-rules.md that it enforces.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from . import paths, render


def authored_strings(config, content):
    """Every string the team wrote, with its location. Tracker text and recorded answers are excluded."""
    found = []

    def add(where, text):
        if isinstance(text, str) and text.strip():
            found.append((where, text.strip()))

    for page, text in (config.get('leads') or {}).items():
        add(f'config.leads.{page}', text)
    for i, item in enumerate(config.get('next_actions', [])):
        add(f'config.next_actions[{i}]', item['text'])
    for i, item in enumerate(config.get('sources', [])):
        add(f'config.sources[{i}]', item['text'])
    for s in content.get('stories', {}).get('stories', []):
        add(f'stories.{s["id"]}.what', s.get('what'))
        add(f'stories.{s["id"]}.interim', s.get('interim'))
    for q in content.get('questions', {}).get('questions', []):
        add(f'questions.{q["id"]}.context', q.get('context'))
        if (q.get('answer') or {}).get('label') == 'Proposed answer':
            add(f'questions.{q["id"]}.answer', q['answer']['text'])
    journeys = content.get('journeys', {})
    for role in journeys.get('roles', []):
        add(f'journeys.{role["id"]}.lead', role.get('lead'))
        for i, step in enumerate(role['steps']):
            for field in ('question', 'today', 'behind', 'handoff', 'open'):
                add(f'journeys.{role["id"]}.steps[{i}].{field}', step.get(field))
    for i, change in enumerate(journeys.get('changes', [])):
        add(f'journeys.changes[{i}].today', change['today'])
        add(f'journeys.changes[{i}].after', change['after'])
    processes = content.get('processes', {})
    for lane in processes.get('lanes', []):
        add(f'processes.{lane["id"]}.lead', lane.get('lead'))
        for step in lane['steps']:
            add(f'processes.{lane["id"]}.{step["id"]}', step['text'])
    for section in processes.get('design', []):
        for i, row in enumerate(section['rows']):
            add(f'processes.design.{section["title"]}[{i}]', row['text'])
    return found


def writing(config, content):
    checker = paths.writing_checker()
    strings = authored_strings(config, content)
    if not checker:
        return {'rule': 'W1', 'status': 'pending', 'detail': 'writing checker missing; read every authored string instead'}
    with tempfile.TemporaryDirectory() as tmp:
        doc = Path(tmp) / 'authored.md'
        doc.write_text('\n\n'.join(text for _, text in strings) + '\n')
        command = [sys.executable, str(checker), '--json', str(doc)]
        house = checker.parent.parent / 'house.json'
        if house.is_file():
            command[2:2] = ['--config', str(house)]
        result = subprocess.run(command, capture_output=True, text=True)
        try:
            report = json.loads(result.stdout)[str(doc)]
        except (ValueError, KeyError):
            return {'rule': 'W1', 'status': 'failed', 'detail': 'checker output unreadable: ' + result.stderr[-400:]}
    findings = []
    for item in report['findings']:
        located = []
        for sample in item.get('samples', []):
            first = sample.split(' / ')[0].strip()
            located += [where for where, text in strings if first and first[:60] in text]
        findings.append({'rule': item['rule'], 'severity': item['severity'], 'message': item['message'],
                         'samples': item.get('samples', []), 'fields': sorted(set(located))})
    failing = [f for f in findings if f['severity'] == 'FAIL']
    return {'rule': 'W1', 'status': 'failed' if failing else 'passed', 'strings': len(strings),
            'findings': findings, 'read': 'WARN findings need a reading pass before publishing'}


def data(config_path, content_dir, tickets_path, dist):
    """Rebuild the data from sources and compare with what the page will show."""
    config, tickets, content = render.load_inputs(config_path, content_dir, tickets_path)
    expected, problems = render.compute(config, tickets, content)
    results = [{'rule': 'D1', 'status': 'failed' if problems else 'passed', 'detail': problems}]
    shown = render.read_data(dist)
    stale = []
    if shown['source']['sha256'] != expected['source']['sha256']:
        stale.append('rendered from a different tracker export')
    for key in ('stories', 'questions', 'journeys', 'changes', 'lanes', 'unclassed', 'tickets'):
        if shown.get(key) != expected.get(key):
            stale.append(f'{key} differ from the sources')
    results.append({'rule': 'D2', 'status': 'failed' if stale else 'passed', 'detail': stale})
    tickets_by_key = {t['key']: t for t in tickets['tickets']}
    wrong = [f'{s["id"]}: shows {s["computed"]["status"]["label"]}, tracker has {tickets_by_key[s["tickets"][0]]["status"]}'
             for s in shown['stories'] if s.get('tickets') and s['tickets'][0] in tickets_by_key
             and s['computed']['status']['label'] != tickets_by_key[s['tickets'][0]]['status']]
    wrong += [f'{k}: shows {v["status"]}, tracker has {tickets_by_key[k]["status"]}'
              for k, v in shown['tickets'].items() if k in tickets_by_key and v['status'] != tickets_by_key[k]['status']]
    results.append({'rule': 'D3', 'status': 'failed' if wrong else 'passed', 'detail': wrong})
    results.append(writing(config, content))
    return results


def browser(dist, node='node'):
    script = paths.KIT / 'checks/browser_checks.cjs'
    policy = paths.launch_policy()
    env = None
    if policy:
        import os
        env = {**os.environ, 'RS_LAUNCH_POLICY': str(policy)}
    result = subprocess.run([node, str(script), str(Path(dist).resolve())], capture_output=True, text=True, env=env)
    try:
        return json.loads(result.stdout)
    except ValueError:
        return [{'rule': 'B0', 'status': 'pending',
                 'detail': 'browser checks did not run: ' + (result.stderr.strip()[-400:] or 'no output')}]


def summarize(results):
    failed = [r for r in results if r['status'] == 'failed']
    pending = [r for r in results if r['status'] == 'pending']
    return {'status': 'failed' if failed else 'pending' if pending else 'passed',
            'failed': [r['rule'] for r in failed], 'pending': [r['rule'] for r in pending], 'results': results}
