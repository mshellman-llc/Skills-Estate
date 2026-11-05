#!/usr/bin/env python3
"""Render the small static sharing edition of the map from index.json (stdlib only).

The full map embeds every instruction and example and is too large for some sharing
reviews. This edition keeps the reader guides, output formats, install lines and workflows. Each skill links to its instructions on GitHub.
"""
import argparse, html, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROLE = {'task': 'Task package', 'mode': 'Task mode', 'support': 'Supporting module'}
e = lambda t: html.escape(str(t), quote=True)

CSS = '''
:root{--bg:#fff;--surface:#f6f6f4;--ink:#1a1a1a;--muted:#5b5b5b;--line:#dedcd6;--accent:#1f5f8b}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#141414;--surface:#1e1e1e;--ink:#ececec;--muted:#a8a8a8;--line:#333;--accent:#7fb7e0}}
:root[data-theme="dark"]{--bg:#141414;--surface:#1e1e1e;--ink:#ececec;--muted:#a8a8a8;--line:#333;--accent:#7fb7e0}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif}
.wrap{max-width:1120px;margin:0 auto;padding:0 24px 48px}a{color:var(--accent)}code{font-size:14px;word-break:break-word}
header{padding:40px 0 20px;border-bottom:1px solid var(--line)}h1{font-size:clamp(30px,5vw,44px);line-height:1.1;margin:0 0 12px;letter-spacing:-.02em}
.lede{font-size:18px;color:var(--muted);max-width:720px;margin:0 0 8px}.meta{font-size:14px;color:var(--muted);margin:0}
.guide{padding:20px 0;border-bottom:1px solid var(--line)}.guide p,.guide li{max-width:780px}.guide p{margin:0 0 12px}.guide ol{padding-left:22px}.guide summary{cursor:pointer;font-weight:600}
.legend{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:8px 28px;margin:0 0 12px;font-size:14px}.legend div{display:flex;gap:10px;align-items:baseline}.legend dd{margin:0;color:var(--muted)}
.tools{padding:14px 0;border-bottom:1px solid var(--line)}.tools input{width:100%;font:inherit;padding:10px 12px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--ink)}
nav{display:flex;flex-wrap:wrap;gap:6px 16px;margin-top:10px;font-size:14px}
h2{font-size:24px;margin:36px 0 4px}.n{font-size:15px;color:var(--muted);font-weight:400}.fd{color:var(--muted);margin:0 0 16px}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;align-items:start}
.skill{border:1px solid var(--line);border-radius:8px;background:var(--surface)}.skill summary{cursor:pointer;padding:14px 16px;list-style:none;display:grid;gap:4px}
.skill summary::-webkit-details-marker{display:none}.t{font-weight:600;font-size:17px}.w{color:var(--muted);font-size:15px}
.tags{display:flex;flex-wrap:wrap;gap:6px;margin-top:4px}.tag{font-size:12px;border:1px solid var(--line);border-radius:4px;padding:1px 7px;color:var(--muted);background:var(--bg);white-space:nowrap}.fmt{border-style:dashed}
.skill[open]{background:var(--bg)}.skill>dl,.skill>p{margin:0 16px 12px;font-size:15px}.skill dt{font-weight:600;font-size:13px;margin-top:8px}.skill dd{margin:0}.ex{font-style:italic}
.flow{border:1px solid var(--line);border-radius:8px;padding:16px 18px;margin-bottom:14px}.flow h3{margin:0 0 4px;font-size:19px}.flow>p{margin:0 0 10px;font-size:15px}
.flow ol{margin:0 0 10px;padding-left:22px}.flow li{margin-bottom:10px;font-size:15px}.flow li dl{margin:4px 0 0;display:grid;grid-template-columns:70px 1fr;gap:2px 10px}.flow li dt{font-weight:600}.flow li dd{margin:0}.note{color:var(--muted)}
footer{margin-top:40px;padding-top:16px;border-top:1px solid var(--line);font-size:14px;color:var(--muted)}
.empty{color:var(--muted)}[hidden]{display:none!important}
@media(max-width:720px){.wrap{padding:0 16px 40px}.grid{grid-template-columns:1fr}.flow li dl{grid-template-columns:1fr}}
'''

JS = '''
const q=document.getElementById('q'),cards=[...document.querySelectorAll('.skill')],fams=[...document.querySelectorAll('.family')],empty=document.getElementById('empty');
q.addEventListener('input',()=>{const w=q.value.toLowerCase().trim().split(/\\s+/).filter(Boolean);let n=0;cards.forEach(c=>{const ok=w.every(x=>c.textContent.toLowerCase().includes(x));c.hidden=!ok;if(ok)n++});fams.forEach(f=>f.hidden=!f.querySelector('.skill:not([hidden])'));empty.hidden=n>0});
function openHash(){const t=document.getElementById(decodeURIComponent(location.hash.slice(1)));if(t&&t.tagName==='DETAILS'){t.open=true;t.scrollIntoView({block:'start'})}}
addEventListener('hashchange',openHash);openHash();
'''

def command(s):
    own = [i for i in s.get('install', []) if i.get('task')]
    return f'/{own[0]["plugin"]}:{own[0]["task"]}' if own else ''

def install_line(s, market):
    own = [i for i in s.get('install', []) if i.get('task')]
    if own:
        i = own[0]
        mode = next((t['mode'] for t in s.get('taskPackages', []) if t['name'] == i['task'] and t.get('mode')), None)
        lead = f'The {e(mode)} mode of <code>{e(i["task"])}</code>. ' if mode else ''
        return f'{lead}Plugin <strong>{e(i["plugin"])}</strong>{" (opt-in)" if i.get("optIn") else ""}, then <code>{e(command(s))}</code>.'
    if s.get('install'):
        return 'Bundled inside ' + ', '.join(f'<strong>{e(i["plugin"])}</strong>' for i in s['install']) + '.'
    return 'Not in a marketplace plugin.'

def formats(s):
    return (s.get('guide') or {}).get('formats', [])

def card(s, market):
    g = s['guide'] or {'what': s['description'], 'when': '', 'inputs': '', 'outputs': '', 'example': ''}
    tags = f'<span class="tag">{ROLE[s["catalogRole"]["kind"]]}</span>' + ''.join(f'<span class="tag fmt">{e(f)}</span>' for f in formats(s))
    needs = [s['profile']['setup']] if (s.get('profile') or {}).get('setup') else []
    needs_html = ('<p><strong>Needs:</strong> ' + '. '.join(e(n).rstrip('.') for n in needs) + '.</p>') if needs else ''
    return (f'<details class="skill" id="skill-{e(s["id"])}"><summary><span class="t">{e(s["title"])}</span><span class="w">{e(g["what"])}</span><span class="tags">{tags}</span></summary>'
            f'<dl><dt>When to use it</dt><dd>{e(g["when"])}</dd><dt>What to give it</dt><dd>{e(g["inputs"])}</dd><dt>What you get</dt><dd>{e(g["outputs"])}</dd>'
            f'<dt>Example request</dt><dd class="ex">{e(g["example"])}</dd><dt>How to install</dt><dd>{install_line(s, market)}</dd></dl>{needs_html}</details>')

def workflow(w, by):
    plugins = list(dict.fromkeys(i['plugin'] for st in w['steps'] for i in by[st['skill']].get('install', []) if i.get('task')))
    steps = ''.join(
        f'<li><a href="#skill-{e(st["skill"])}">{e(by[st["skill"]]["title"])}</a>{" <code>"+e(command(by[st["skill"]]))+"</code>" if command(by[st["skill"]]) else ""}'
        f'<dl><dt>Give it</dt><dd>{e(st["give"])}</dd><dt>You get</dt><dd>{e(st["get"])}</dd></dl></li>' for st in w['steps'])
    install = ('<p><strong>Install:</strong> ' + ', '.join(f'<code>{e(p)}</code>' for p in plugins) + '</p>') if plugins else ''
    return f'<section class="flow" id="workflow-{e(w["id"])}"><h3>{e(w["title"])}</h3><p>{e(w["when"])}</p><ol>{steps}</ol>{install}<p class="note">{e(w["note"])}</p></section>'

def render(data):
    by = {s['id']: s for s in data['skills']}
    market = data.get('marketplace') or 'skills-estate'
    kinds = {k: sum(s['catalogRole']['kind'] == k for s in data['skills']) for k in ROLE}
    families = ''
    for i, f in enumerate(data['families']):
        members = sorted((s for s in data['skills'] if s['family'] == i), key=lambda s: s['title'].lower())
        families += (f'<section class="family" id="{e(f["id"])}"><h2>{e(f["title"])} <span class="n">{len(members)}</span></h2><p class="fd">{e(f["description"])}</p>'
                     '<div class="grid">' + ''.join(card(s, market) for s in members) + '</div></section>')
    nav = ''.join(f'<a href="#{e(f["id"])}">{e(f["title"])}</a>' for f in data['families'])
    flows = ''.join(workflow(w, by) for w in data.get('workflows', []))
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Skills Estate shared map</title><style>{CSS}</style></head><body><div class="wrap">
<header><h1>Skills Estate map</h1><p class="lede">Explore what each skill does, when to use it, and how it connects to the rest of your estate.</p><p class="meta">{kinds["task"]} tasks · {len(data["skills"])} source workflows · {kinds["mode"]} modes · {kinds["support"]} supporting modules</p></header>
<section class="guide" aria-label="How to use this map"><p><strong>Start with the workflows</strong> if you know the job but not the skills. Each workflow lists the skills in order, what to give each one, what you get back and which plugin to install. To look up one skill, search or pick a family, then open it.</p>
<dl class="legend"><div><dt><span class="tag">Task package</span></dt><dd>A skill you install and ask for directly.</dd></div><div><dt><span class="tag">Task mode</span></dt><dd>A mode inside another skill's package.</dd></div><div><dt><span class="tag">Supporting module</span></dt><dd>Shared guidance bundled into task packages.</dd></div><div><dt><span class="tag fmt">Excel workbook</span></dt><dd>What the skill hands back.</dd></div></dl>
<details><summary>How to install skills</summary><p>The skills install as plugins from the Skills Estate marketplace, the private <code>mshellman-llc/Skills-Estate</code> repository. You need access to that repository.</p>
<ol><li><strong>Claude app:</strong> open Customize, then Plugins, then Add, and add the marketplace <code>mshellman-llc/Skills-Estate</code> with automatic sync on. Then add the plugin you need.</li>
<li><strong>Claude Code:</strong> run <code>/plugin marketplace add mshellman-llc/Skills-Estate</code>, then <code>/plugin install PLUGIN@{e(market)}</code>.</li>
<li><strong>Codex on a Mac:</strong> run <code>python3 tools/estate.py update</code> from a Skills Estate checkout.</li></ol>
<p>After installing, ask for the work in plain words. The <strong>estate-personal</strong> plugin is opt-in.</p></details></section>
<div class="tools"><label for="q" class="meta">Find a skill</label><input id="q" type="search" placeholder="Try discovery, scope, writing, Salesforce…" autocomplete="off"><nav aria-label="Sections"><a href="#workflows">Workflows</a>{nav}</nav></div>
<main><section id="workflows"><h2>Workflows</h2><p class="fd">Pick the job you are doing. Each step says what to give the skill and what you get back.</p>{flows}</section>
{families}<p id="empty" class="empty" hidden>No skills match that search.</p></main>
<footer><p>Snapshot of {len(data["skills"])} skills from <a href="https://github.com/{e(data["repository"])}" target="_blank" rel="noopener noreferrer">{e(data["repository"])}</a> at commit {e(data["baseCommit"][:7])}, generated {e(data["generatedAt"][:10])}. Full instructions, example runs and package downloads are in the full map and the repository.</p></footer>
</div><script>{JS}</script></body></html>'''

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', type=Path, default=HERE / 'index.json')
    p.add_argument('--output', type=Path, default=HERE.parents[1] / 'build' / 'skills-map-share.html')
    a = p.parse_args()
    page = render(json.loads(a.data.read_text()))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(page)
    print(json.dumps({'output': str(a.output), 'bytes': len(page.encode())}))
