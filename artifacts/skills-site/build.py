#!/usr/bin/env python3
"""Build the Skills Estate map page from a Skills-Estate checkout and the LiveLaughCode design system files.

Usage: python3 build.py [--repo PATH] [--llc DIR] [--target estate] [--out index.html]

--repo    a Skills-Estate checkout (default: the checkout this file sits in)
--llc     a folder holding tokens.css, bundle.css, meridian.css, bundle.js, the Instrument Sans
          font files and react.production.min.js / react-dom.production.min.js (React 18 UMD).
          Engrace-ItalicVF.woff2 is used when present; without it the wordmark falls back to a
          local Engrace install. Default: vendor/ beside this file.
--target  apply config/skills-publication.json for that website (estate or portfolio).
          Without it every skill, workflow and plugin in the catalog is shown.
--app     the page script (default: app.js beside this file)
"""
import argparse, base64, datetime, json, os, re, subprocess, sys

ap = argparse.ArgumentParser()
HERE = os.path.dirname(os.path.abspath(__file__))
ap.add_argument('--repo', default=os.path.normpath(os.path.join(HERE, '..', '..')))
ap.add_argument('--llc', default=os.path.join(HERE, 'vendor'))
ap.add_argument('--target', choices=['estate', 'portfolio'])
ap.add_argument('--app', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.js'))
ap.add_argument('--out', default=os.path.join(HERE, 'index.html'))
ap.add_argument('--page-url', default='', help='address the Copy link button uses; empty means the address the page is served from')
a = ap.parse_args()

R = a.repo
idx = json.load(open(os.path.join(R, 'artifacts/skills-map/index.json')))
wfs = json.load(open(os.path.join(R, 'artifacts/skills-map/workflows.json')))

def git(*args):
    try:
        return subprocess.check_output(['git', '-C', R] + list(args), text=True).strip()
    except Exception:
        return ''

head = git('rev-parse', 'HEAD') or idx.get('baseCommit', '')
head_date = git('log', '-1', '--format=%cI') or idx.get('generatedAt', '')

# Fail loudly when the catalog no longer matches the skills folder on main.
skills_dir = os.path.join(R, 'skills')
on_disk = {d for d in os.listdir(skills_dir) if os.path.exists(os.path.join(skills_dir, d, 'SKILL.md'))}
in_index = {s['id'] for s in idx['skills']}
drift = sorted(on_disk ^ in_index)

hidden = []
if a.target:
    # Show only what the owner published for this website; excluded records never enter the page.
    sys.path.insert(0, os.path.join(R, 'artifacts', 'skills-map'))
    import publication
    proj, omitted = publication.project(idx, publication.load(os.path.join(R, 'config', 'skills-publication.json')), a.target, wfs)
    hidden = sorted(in_index - {s['id'] for s in proj['skills']})
    idx = dict(idx, skills=proj['skills'], pluginInventory=[{'id': p['id'], 'description': p['description']} for p in proj['plugins']])
    wfs = proj['workflows']

fams = idx['families']
ids = {s['id'] for s in idx['skills']}

KIND = {'task': 'Task package', 'mode': 'Task mode', 'support': 'Supporting module'}
CONNECTOR_NAMES = {'google-drive': 'Google Drive', 'github': 'GitHub', 'salesforce': 'Salesforce', 'jira': 'Jira',
                   'slack': 'Slack', 'gmail': 'Gmail', 'granola': 'Granola', 'linear': 'Linear', 'notion': 'Notion',
                   'asana': 'Asana', 'google-sheets': 'Google Sheets', 'google-calendar': 'Google Calendar',
                   'figma': 'Figma', 'supabase': 'Supabase', 'railway': 'Railway', 'confluence': 'Confluence'}

def cname(c):
    if c in ids:
        return {'skill': c}
    return {'text': CONNECTOR_NAMES.get(c, c.replace('-', ' ').capitalize())}

def clean(t):
    return re.sub(r'\s+', ' ', (t or '')).strip()

skills = []
for s in idx['skills']:
    g, p, role = s['guide'], s['profile'], s['catalogRole']
    prep = g.get('preparation') or {}
    conn = p.get('connectors') or {}
    modes_of = [m['task'] for m in role.get('modes', []) if m.get('task')]
    mode_names = [m['mode'] for m in role.get('modes', []) if m.get('mode')]
    rec = {
        'id': s['id'], 'title': s['title'], 'family': fams[s['family']]['id'],
        'kind': role['kind'],
        'plugin': (p.get('plugins') or [None])[0],
        'what': clean(g.get('what')), 'when': clean(g.get('when')), 'inputs': clean(g.get('inputs')),
        'outputs': clean(g.get('outputs')), 'example': clean(g.get('example')),
        'overview': clean(g.get('overview') or g.get('expect')),
        'where': clean(prep.get('where')), 'missing': clean(prep.get('missing')),
        'requires': clean(g.get('requires')), 'setup': clean(p.get('setup')),
        'prepSkills': [x for x in (g.get('preparationSkills') or []) if isinstance(x, str) and x in ids],
        'needs': [cname(c) for c in conn.get('required', [])],
        'optional': [cname(c) for c in conn.get('optional', [])],
        'modeOf': [x for x in modes_of if x in ids], 'modeName': mode_names[0] if mode_names else '',
        'usedBy': [x for x in p.get('usedBy', []) if x in ids],
        'uses': sorted({x for x in (p.get('calls', []) + p.get('dependsOn', [])) if x in ids and x != s['id']}),
        'examples': len(s.get('examples') or []),
        'src': 'https://github.com/mshellman-llc/Skills-Estate/blob/main/' + s['sourcePath'],
    }
    skills.append({k: v for k, v in rec.items() if v not in ('', [], None)})

# Modes a task offers, for the task's own panel.
by_id = {s['id']: s for s in skills}
for s in skills:
    for t in s.get('modeOf', []):
        by_id[t].setdefault('modes', []).append(s['id'])

workflows = []
for w in wfs:
    steps = [{'skill': st['skill'], 'why': clean(st.get('why'))} for st in w['steps'] if st['skill'] in ids]
    workflows.append({'id': w['id'], 'kind': w['audience'], 'title': w['title'], 'desc': clean(w.get('desc')),
                      'prompt': clean(w.get('prompt')), 'inputs': clean(w.get('inputs')), 'outcome': clean(w.get('outcome')),
                      'note': clean(w.get('note')), 'steps': steps})

plugins = []
for pl in idx['pluginInventory']:
    members = [s['id'] for s in skills if s.get('plugin') == pl['id']]
    plugins.append({'id': pl['id'], 'desc': clean(pl.get('description')), 'skills': members})

data = {
    'commit': head[:7], 'commitUrl': 'https://github.com/mshellman-llc/Skills-Estate/commit/' + head,
    'date': head_date[:10],
    'families': [{'id': f['id'], 'title': f['title'], 'desc': clean(f.get('description'))} for f in fams],
    'skills': skills, 'workflows': workflows, 'plugins': plugins,
    'pageUrl': a.page_url,
    'icons': json.load(open(os.path.join(os.path.dirname(os.path.abspath(a.app)), 'icons.json'))),
    'counts': {k: sum(1 for s in skills if s['kind'] == k) for k in KIND},
}

L = a.llc
def rd(n, mode='r'):
    with open(os.path.join(L, n), mode) as f:
        return f.read()

def font_uri(n):
    return 'data:font/woff2;base64,' + base64.b64encode(rd(n, 'rb')).decode()

tokens = rd('tokens.css')
for n in ['instrument-sans-latin-400-normal.woff2', 'instrument-sans-latin-500-normal.woff2',
          'instrument-sans-latin-600-normal.woff2', 'Engrace-ItalicVF.woff2']:
    path = os.path.join(L, n)
    tokens = tokens.replace('url("fonts/%s")' % n, 'url("%s")' % font_uri(n) if os.path.exists(path) else 'local("Engrace")')

def safe(js):
    return js.replace('</script', '<\\/script').replace('<!--', '\\x3C!--')

def safe_css(css):
    return css.replace('</style', '<\\/style')

payload = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/').replace('<!--', '<\\!--')

engrace = os.path.join(L, 'Engrace-ItalicVF.woff2')
meridian_css = safe_css(re.sub(r'@import url\([^)]*\);?', '', rd('meridian.css')))
bundle_css = safe_css(rd('bundle.css').replace('url("../fonts/Engrace-ItalicVF.woff2")', 'url("%s")' % font_uri('Engrace-ItalicVF.woff2') if os.path.exists(engrace) else 'local("Engrace")'))
page_css = safe_css(open(os.path.join(os.path.dirname(os.path.abspath(a.app)), 'page.css')).read())
scripts = ''.join('<script>%s</script>\n' % safe(t) for t in (rd('react.production.min.js'), rd('react-dom.production.min.js'), rd('bundle.js'), open(a.app).read()))
tokens_css = safe_css(tokens)

html = f'''<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Skills Estate map</title>
<style>{tokens_css}</style>
<style>{meridian_css}</style>
<style>{bundle_css}</style>
<style>{page_css}</style>
</head>
<body>
<div id="root" class="mer-app"></div>
<noscript>This page needs JavaScript to list the skills.</noscript>
<script id="estate-data" type="application/json">{payload}</script>
{scripts}</body>
</html>
'''
os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
open(a.out, 'w').write(html)
print(json.dumps({'out': a.out, 'bytes': len(html.encode()), 'commit': head[:7], 'skills': len(skills),
                  'workflows': len(workflows), 'plugins': len(plugins), 'counts': data['counts'], 'target': a.target, 'hidden': hidden, 'drift': drift}))
if drift:
    sys.exit('Catalog drift: index.json and skills/ disagree on ' + ', '.join(drift))
