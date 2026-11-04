"""Command implementations shared by the series' entry scripts.

Project layout (all paths can be overridden):
  <project>/config/site.json        engagement config
  <project>/content/*.json          stories, questions, journeys, processes
  <project>/tracker/tickets.json    canonical tickets from the latest intake
  <project>/tracker/history/        earlier canonical exports, by hash
  <project>/tracker/intake-log.json one intake record per export
  <project>/dist/                   rendered site
"""
import json
import shutil
import sys
from pathlib import Path

from . import decisions, gate, render, stories, tracker, validate


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def project_paths(project):
    p = Path(project)
    return {'config': p / 'config/site.json', 'content': p / 'content', 'tracker': p / 'tracker',
            'tickets': p / 'tracker/tickets.json', 'dist': p / 'dist', 'exports': p / 'exports'}


def intake(config_path, export, out_dir, origin, scope):
    config = validate.load(config_path, 'site')
    out = Path(out_dir)
    current_path = out / 'tickets.json'
    previous = json.loads(current_path.read_text()) if current_path.exists() else None
    document, warnings = tracker.load(export, config)
    if previous and previous['source']['sha256'] == document['source']['sha256']:
        return {'status': 'unchanged', 'sha256': document['source']['sha256']}
    record = tracker.intake_record(export, document, warnings, origin, scope, previous)
    change = tracker.delta(previous, document)
    if previous:
        dump(out / 'history' / f'tickets-{previous["source"]["sha256"][:12]}.json', previous)
    dump(current_path, document)
    dump(out / 'delta.json', change)
    log_path = out / 'intake-log.json'
    log = json.loads(log_path.read_text()) if log_path.exists() else []
    log.append(record)
    dump(log_path, log)
    return {'status': 'recorded', 'tickets': len(document['tickets']), 'added': len(change['added']),
            'removed': len(change['removed']), 'changed': len(change['changed']), 'conflicts': warnings}


def queue(content_dir, tickets_path, delta_path, out_dir):
    tickets_doc = validate.load(tickets_path, 'tickets')
    stories_doc = validate.load(Path(content_dir) / 'stories.json', 'stories')
    questions_path = Path(content_dir) / 'questions.json'
    questions_doc = validate.load(questions_path, 'questions') if questions_path.exists() else None
    synced = stories.sync(stories_doc, tickets_doc, questions_doc)
    change = json.loads(Path(delta_path).read_text())
    result = stories.review_queue(change, synced, tickets_doc)
    dump(Path(out_dir) / 'review-queue.json', result)
    lines = ['# Review queue', '']
    if result['affected_stories']:
        lines += ['## Stories whose tickets changed', '']
        for item in result['affected_stories']:
            lines.append(f'- {item["label"]} ({item["story"]})')
            for key, changes in item['changes'].items():
                for field, (old, new) in changes.items():
                    lines.append(f'  - {key} {field}: {old} -> {new}')
    if result['new_tickets']:
        lines += ['', '## New tickets to map or class', '']
        for item in result['new_tickets']:
            options = ', '.join(f'{c["label"]} ({c["story"]})' for c in item['candidates']) or 'no close match'
            lines.append(f'- {item["key"]} {item["summary"]} [{item["status"]}]; candidates: {options}')
    if result['removed']:
        lines += ['', '## Tickets no longer in the export', ''] + [f'- {k}' for k in result['removed']]
    (Path(out_dir) / 'review-queue.md').write_text('\n'.join(lines) + '\n')
    return result


def build(config_path, content_dir, tickets_path, dist, force=True):
    config, tickets_doc, content = render.load_inputs(config_path, content_dir, tickets_path)
    data, problems = render.compute(config, tickets_doc, content)
    if problems:
        return {'status': 'failed', 'problems': problems}
    manifest = render.write_site(data, config, config_path, dist, force=force)
    return {'status': 'rendered', 'dist': str(dist), 'files': len(manifest['files']),
            'brand': manifest['brand'], 'brand_substitutions': manifest['brand_substitutions'],
            'must_share': data['share']['must_share'], 'unclassed': len(data['unclassed'])}


def check(config_path, content_dir, tickets_path, dist, browser=True):
    results = gate.data(config_path, content_dir, tickets_path, dist)
    if browser:
        results += gate.browser(dist)
    else:
        results.append({'rule': 'B0', 'status': 'pending', 'detail': 'browser checks skipped on request'})
    return gate.summarize(results)


def export(config_path, content_dir, tickets_path, saved_path, reviews_path, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written = []
    questions_path = Path(content_dir) / 'questions.json'
    if questions_path.exists():
        questions_doc = validate.load(questions_path, 'questions')
        saved = decisions.load_saved(saved_path)
        (out / 'decisions.csv').write_text(decisions.export_csv(questions_doc, saved))
        (out / 'decisions.md').write_text(decisions.export_markdown(questions_doc, saved))
        written += ['decisions.csv', 'decisions.md']
    if reviews_path:
        tickets_doc = validate.load(tickets_path, 'tickets')
        stories_doc = validate.load(Path(content_dir) / 'stories.json', 'stories')
        synced = stories.sync(stories_doc, tickets_doc)
        (out / 'class-reviews.csv').write_text(decisions.export_reviews(synced, decisions.load_reviews(reviews_path)))
        written.append('class-reviews.csv')
    return {'status': 'exported', 'files': written}


def init(project, example):
    p = project_paths(project)
    if p['config'].exists():
        raise ValueError(f'{p["config"]} exists; refusing to overwrite an engagement')
    for name in ('config', 'content', 'mockups'):
        source = Path(example) / name
        if source.is_dir():
            shutil.copytree(source, Path(project) / name, dirs_exist_ok=False)
    return {'status': 'initialized', 'project': str(project),
            'next': 'Replace every example value in config/ and content/ before the first build.'}


def emit(result):
    print(json.dumps(result, indent=2, ensure_ascii=False))
    status = result.get('status')
    return 0 if status in ('recorded', 'unchanged', 'rendered', 'passed', 'exported', 'initialized', 'ok') else (
        3 if status == 'pending' else 1)


def run(fn, *args):
    try:
        return emit(fn(*args))
    except (ValueError, FileNotFoundError, KeyError) as error:
        print(json.dumps({'status': 'error', 'error': str(error)}), file=sys.stderr)
        return 2
