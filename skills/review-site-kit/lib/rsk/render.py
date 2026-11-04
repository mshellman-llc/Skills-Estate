"""Render the review site from the engagement config, content files and tracker tickets.

Pages are fixed templates. Everything the reader sees comes from one data file,
`data/site-data.js`, so a refresh replaces data and never edits page markup.
"""
import datetime as dt
import hashlib
import html
import json
import shutil
from pathlib import Path

from . import brand, decisions, paths, stories as story_lib, validate

PAGE_TITLES = {'scope': 'Scope', 'decisions': 'Decisions', 'workflow': 'Workflow', 'build': 'Build', 'mockups': 'Mockups'}
CONTENT = {'stories': 'stories', 'questions': 'questions', 'journeys': 'journeys', 'processes': 'processes'}
NEEDS = {'scope': ['stories'], 'decisions': ['questions'], 'workflow': ['journeys'], 'build': ['processes'], 'mockups': []}
DEFAULT_CLASSES = {
    'must': {'label': 'Must', 'definition': ''},
    'should': {'label': 'Should', 'definition': ''},
    'could': {'label': 'Could', 'definition': ''},
    'wont': {'label': "Won't", 'definition': ''},
}
DEFAULT_STORE = {'answers': 'answers', 'reviews': 'moscow', 'comments': 'comments'}


def page_file(config, page):
    return 'index.html' if page == config['pages'][0] else f'{page}.html'


def load_inputs(config_path, content_dir, tickets_path):
    config = validate.load(config_path, 'site')
    tickets = validate.load(tickets_path, 'tickets')
    content = {}
    required = {name for page in config['pages'] for name in NEEDS[page]}
    for name in CONTENT:
        path = Path(content_dir) / f'{name}.json'
        if path.exists():
            content[name] = validate.load(path, CONTENT[name])
        elif name in required:
            raise ValueError(f'{path} is required by the selected pages')
    return config, tickets, content


def compute(config, tickets_doc, content):
    tickets = story_lib.index(tickets_doc)
    stories_doc = content.get('stories', {'format': 1, 'steps': [], 'stories': []})
    questions_doc = content.get('questions', {'format': 1, 'groups': [], 'questions': []})
    classes = {k: {**DEFAULT_CLASSES[k], **(config.get('classes') or {}).get(k, {})} for k in DEFAULT_CLASSES}
    synced = story_lib.sync(stories_doc, tickets_doc, questions_doc, config)
    problems = decisions.problems(questions_doc, synced, tickets) if content.get('questions') else []
    step_ids = {s['id'] for s in stories_doc['steps']}
    problems += [f'{s["id"]}: unknown step {s["step"]}' for s in stories_doc['stories'] if s['step'] not in step_ids]
    graph = story_lib.critical_path(synced, tickets_doc, config, {k: v['label'] for k, v in classes.items()}) if synced else None
    unclassed = story_lib.unclassed(synced, tickets_doc, config) if synced else []
    referenced = {k for s in synced for k in s.get('tickets', [])}
    referenced |= {k for q in questions_doc['questions'] for k in q.get('tickets', [])}
    referenced |= {k for c in content.get('journeys', {}).get('changes', []) for k in c.get('tickets', [])}
    referenced |= {k for lane in content.get('processes', {}).get('lanes', []) for st in lane['steps'] for k in st.get('tickets', [])}
    referenced |= {g.get('ticket') for g in questions_doc['groups'] if g.get('ticket')}
    referenced |= {u['key'] for u in unclassed}
    referenced |= {s['computed']['epic'] for s in synced if s['computed']['epic']}
    missing = sorted(k for k in referenced if k not in tickets)
    problems += [f'ticket {k} is referenced but not in the tracker export' for k in missing
                 if not any(s.get('planned_in') == k for s in synced)]
    base = config['tracker'].get('base_url', '')
    ticket_view = {k: {'summary': t['summary'], 'status': t['status'], 'category': t['category'],
                       'sprint': t.get('sprint'), 'points': t.get('points'), 'epic': t.get('epic'),
                       'type': t.get('type'), 'acceptance': t.get('acceptance', []),
                       'url': (base + k) if base else ''}
                   for k, t in tickets.items() if k in referenced}
    return {
        'format': 1,
        'title': config['title'],
        'generated': dt.date.today().isoformat(),
        'source': tickets_doc['source'],
        'pages': [{'id': p, 'title': PAGE_TITLES[p], 'file': page_file(config, p)} for p in config['pages']],
        'leads': config.get('leads', {}),
        'classes': classes,
        'roles': config.get('roles', []),
        'steps': stories_doc['steps'],
        'stories': synced,
        'share': story_lib.must_share(synced),
        'must_ceiling': config.get('must_ceiling', 0.6),
        'readiness_rules': config.get('readiness') or story_lib.DEFAULT_READINESS,
        'unclassed': unclassed,
        'critical_path': graph,
        'groups': questions_doc['groups'],
        'questions': questions_doc['questions'],
        'statuses': decisions.STATUSES,
        'journeys': content.get('journeys', {}).get('roles', []),
        'changes': content.get('journeys', {}).get('changes', []),
        'lanes': content.get('processes', {}).get('lanes', []),
        'design': content.get('processes', {}).get('design', []),
        'next_actions': config.get('next_actions', []),
        'sources': config.get('sources', []),
        'mockups': [{'title': m['title'], 'file': 'mockups/' + Path(m['file']).name} for m in config.get('mockups', [])],
        'store': {**DEFAULT_STORE, **(config.get('store') or {})},
        'tickets': ticket_view,
    }, problems


def _nav(data, current):
    links = []
    for p in data['pages']:
        mark = ' aria-current="page"' if p['id'] == current else ''
        links.append(f'<a href="{p["file"]}"{mark}>{html.escape(p["title"])}</a>')
    return ''.join(links)


def write_site(data, config, config_path, out_dir, force=False):
    out = Path(out_dir)
    if out.exists() and any(out.iterdir()) and not force:
        raise ValueError(f'{out} is not empty; pass --force to replace a previous render')
    if out.exists():
        shutil.rmtree(out)
    (out / 'assets').mkdir(parents=True)
    (out / 'data').mkdir()
    profile_path = config.get('brand_profile')
    if profile_path:
        profile_path = (Path(config_path).parent / profile_path).resolve()
    profile, profile_dir, substitutions = brand.load(profile_path)
    tokens = brand.css(profile)
    logo = brand.logo(profile, profile_dir)
    if logo.startswith('<img'):
        shutil.copy2(Path(profile_dir) / Path(profile['logo']['file']).name, out / 'assets')
    shell = (paths.assets() / 'page.html').read_text()
    for page in data['pages']:
        lead = data['leads'].get(page['id'], '')
        text = (shell.replace('{{TOKENS}}', tokens)
                .replace('{{TITLE}}', html.escape(data['title']))
                .replace('{{PAGE_TITLE}}', html.escape(page['title']))
                .replace('{{PAGE}}', page['id'])
                .replace('{{NAV}}', _nav(data, page['id']))
                .replace('{{LOGO}}', logo)
                .replace('{{LEAD}}', f'<p class="lead">{html.escape(lead)}</p>' if lead else ''))
        (out / page['file']).write_text(text)
        shutil.copy2(paths.assets() / f'{page["id"]}.js', out / 'assets' / f'{page["id"]}.js')
    for name in ('site.css', 'site.js'):
        shutil.copy2(paths.assets() / name, out / 'assets' / name)
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    (out / 'data/site-data.js').write_text('window.RS_DATA=' + payload + ';\n')
    for item in config.get('mockups', []):
        source = (Path(config_path).parent / item['file']).resolve()
        (out / 'mockups').mkdir(exist_ok=True)
        shutil.copy2(source, out / 'mockups' / source.name)
    manifest = {'format': 1, 'brand': profile.get('name'), 'brand_substitutions': substitutions,
                'tracker_sha256': data['source']['sha256'],
                'data_sha256': hashlib.sha256(payload.encode()).hexdigest(),
                'files': {str(p.relative_to(out)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sorted(out.rglob('*')) if p.is_file()}}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    return manifest


def read_data(dist):
    text = (Path(dist) / 'data/site-data.js').read_text()
    return json.loads(text[len('window.RS_DATA='):].rstrip().rstrip(';').replace('<\\/', '</'))
