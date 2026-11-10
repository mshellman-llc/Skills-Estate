#!/usr/bin/env python3
"""Build selected, framework-independent Skills Estate website exports."""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent
TARGETS = ('estate', 'portfolio')
KINDS = ('skills', 'workflows', 'plugins')
CONFIG = HERE.parents[1] / 'config/skills-publication.json'


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()


def revision(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def validate(settings):
    if settings.get('format') != 1 or set(settings.get('targets', {})) != set(TARGETS):
        raise ValueError('Publication settings need estate and portfolio targets')
    for target in TARGETS:
        if set(settings['targets'][target]) != set(KINDS):
            raise ValueError('Each target needs skills, workflows and plugins')
        for kind in KINDS:
            for key, item in settings['targets'][target][kind].items():
                if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', key):
                    raise ValueError('Invalid publication content ID')
                if set(item) != {'visible', 'download', 'featured', 'order'}:
                    raise ValueError('Invalid publication controls for ' + key)
                if any(type(item[x]) is not bool for x in ('visible', 'download', 'featured')):
                    raise ValueError('Publication switches must be booleans')
                if type(item['order']) is not int or not 0 <= item['order'] <= 10000:
                    raise ValueError('Order must be an integer from 0 to 10000')
    return settings


def load(path=CONFIG):
    return validate(json.loads(Path(path).read_text()))


def choice(settings, target, kind, key):
    return settings['targets'][target][kind].get(key, {'visible': False, 'download': False, 'featured': False, 'order': 1000})


def inventory(data, workflows=None, bundles=None):
    workflows = workflows if workflows is not None else json.loads((HERE / 'workflows.json').read_text())
    if bundles is None:
        config=HERE.parents[1] / 'config/plugin-bundles.json'
        bundles=json.loads(config.read_text())['bundles'] if config.is_file() else {p['id']:{'description':p['description']} for p in data.get('pluginInventory',[])}
    return {
        'skills': [{'id': s['id'], 'title': s['title'], 'category': data['families'][s['family']]['title']} for s in data['skills']],
        'workflows': [{'id': r['id'], 'title': r['title'], 'category': r['audience'], 'requires': [x['skill'] for x in r['steps']]} for r in workflows],
        'plugins': [{'id': key, 'title': {'estate-salesforce':'Salesforce development','estate-career':'Career and applications','estate-personal':'Personal and creative'}.get(key,key.removeprefix('estate-').replace('-', ' ').capitalize()), 'category': 'Installable plugins', 'description': item['description']} for key, item in bundles.items()],
    }


def project(data, settings, target, workflows=None, bundles=None):
    validate(settings)
    if target not in TARGETS:
        raise ValueError('Choose estate or portfolio')
    workflows = workflows if workflows is not None else json.loads((HERE / 'workflows.json').read_text())
    result = copy.deepcopy(data)
    result.pop('pluginInventory',None)
    result['skills'] = []
    for original in data['skills']:
        item = choice(settings, target, 'skills', original['id'])
        if not item['visible']:
            continue
        skill = copy.deepcopy(original)
        skill['presentation'] = {'featured': item['featured'], 'order': item['order']}
        skill['downloadAllowed'] = item['download']
        if not item['download']:
            skill['downloadPackages'] = []
        result['skills'].append(skill)
    visible = {s['id'] for s in result['skills']}
    for skill in result['skills']:
        skill['mentions'] = [m for m in skill['mentions'] if m['name'] in visible]
        if skill.get('profile'):
            for key in ('calls', 'dependsOn', 'usedBy', 'bundles'):
                skill['profile'][key] = [x for x in skill['profile'].get(key, []) if x in visible]
    result['workflows'] = []
    omitted = []
    for route in workflows:
        item = choice(settings, target, 'workflows', route['id'])
        if not item['visible']:
            continue
        missing = sorted({x['skill'] for x in route['steps']} - visible)
        if missing:
            omitted.append({'id': route['id'], 'missing': missing})
            continue
        route = copy.deepcopy(route)
        route['presentation'] = {'featured': item['featured'], 'order': item['order']}
        result['workflows'].append(route)
    result['workflows'].sort(key=lambda r: (not r['presentation']['featured'], r['presentation']['order'], r['title']))
    result['plugins'] = []
    for plugin in inventory(data, workflows, bundles)['plugins']:
        item = choice(settings, target, 'plugins', plugin['id'])
        if item['visible']:
            result['plugins'].append({**plugin, 'downloadAllowed': item['download'], 'url': 'https://github.com/mshellman-llc/Skills-Estate/releases/download/plugins-latest/' + plugin['id'] + '.zip' if item['download'] else '', 'presentation': {'featured': item['featured'], 'order': item['order']}})
    result['plugins'].sort(key=lambda r: (not r['presentation']['featured'], r['presentation']['order'], r['title']))
    result['counts'] = {key: sum(s['status'] == key for s in result['skills']) for key in ('github', 'local-revision', 'local-addition')}
    result['counts'].update(total=len(result['skills']), canonical=sum(s['status'] != 'local-addition' for s in result['skills']), withExamples=sum(bool(s.get('examples')) for s in result['skills']))
    result['publication'] = {'format': 1, 'target': target, 'settingsRevision': revision(settings), 'sourceCommit': data['baseCommit']}
    # No excluded records or owner settings are added to the public payload.
    return result, omitted


def component_source():
    template = (HERE / 'template.html').read_text()
    body = template.split('<body>', 1)[1].split('<script type="application/json" id="estate-data">', 1)[0]
    # Toast and print targets occur after the data element in the standalone page.
    if 'id="toast"' not in body:body += '<div id="toast" class="toast" role="status" hidden></div>'
    if 'id="print-detail"' not in body:body += '<div id="print-detail" class="print-detail"></div>'
    body = re.sub(r'<script[^>]*>.*?</script>', '', body, flags=re.S)
    body = body.replace('<!--downloads-->', '').replace('<!--/downloads-->', '')
    code = template.rsplit('<script>', 1)[1].split('</script>', 1)[0]
    code = code.replace("const DATA=JSON.parse(document.getElementById('estate-data').textContent);", 'const DATA=data;')
    code = code.replace('const ROUTES=__ESTATE_ROUTES__;', 'const ROUTES=routes;')
    a = code.index("const configText="); b = code.index('const roleLabel=', a)
    code = code[:a] + 'const VIEWER=null;\n' + code[b:]
    code = code.replace('document.querySelectorAll', 'root.querySelectorAll').replace('document.querySelector', 'root.querySelector').replace('document.addEventListener', 'root.addEventListener').replace('document.body.append', 'root.append').replace('document.body.classList', 'root.classList')
    code = code.replace("const DOWNLOAD_BASE=new URL(DATA.downloadBase||'.',location.href);", 'const DOWNLOAD_BASE=new URL(downloadBase,location.href);')
    code = code.replace("history.replaceState(null,'','#skill='+encodeURIComponent(s.id))", "onSelect?.(s.id)")
    code = code.replace("history.replaceState(null,'',location.pathname+location.search)", 'onSelect?.(null)')
    code = code.replace("window.addEventListener('afterprint',()=>{document.body.classList.remove('printing-detail');$('#print-detail').innerHTML=''})", "window.addEventListener('afterprint',()=>{root.classList.remove('printing-detail');$('#print-detail').innerHTML=''},{signal:controller.signal})")
    code = code.replace("window.addEventListener('afterprint',()=>{root.classList.remove('printing-detail');$('#print-detail').innerHTML=''})", "window.addEventListener('afterprint',()=>{root.classList.remove('printing-detail');$('#print-detail').innerHTML=''},{signal:controller.signal})")
    code = code.replace("const requested=new URLSearchParams(location.hash.slice(1)).get('skill')", 'const requested=initialSkill')
    code = code.replace("$('#update-map').onclick=", "$('#update-map').hidden=true;$('#update-map').onclick=")
    header = '''// Portable Skills Estate UI. No framework, account or privileged API key is required.
export function mountSkillsEstate(element, {data, routes=data.workflows||[], stylesheet=new URL('./explorer.css',import.meta.url).href, downloadBase=new URL('.',import.meta.url).href, initialSkill=null, onSelect=null}={}) {
 if(!data||!Array.isArray(data.skills)||!Array.isArray(data.families))throw new Error('A Skills Estate catalog is required');
 const shadow=element.shadowRoot||element.attachShadow({mode:'open'});shadow.replaceChildren();
 const link=document.createElement('link');link.rel='stylesheet';link.href=stylesheet;shadow.append(link);
 const root=document.createElement('div');root.className='estate-root';shadow.append(root);
 const controller=new AbortController();
'''
    footer = '''
 root.querySelector('.skip')?.addEventListener('click',e=>{e.preventDefault();root.querySelector('#results').focus();root.querySelector('#results').scrollIntoView({block:'start'})});
 return { destroy(){controller.abort();shadow.replaceChildren()}, openSkill, closeSkill };
}
export class SkillsEstateExplorer extends HTMLElement {
 connectedCallback(){
  this._abort=new AbortController();this.textContent='Loading skills…';
  this.ready=(async()=>{
   const source=this.getAttribute('catalog-src');if(!source)throw new Error('Set catalog-src to the published catalog URL');
   const response=await fetch(source,{signal:this._abort.signal});if(!response.ok)throw new Error('The skills catalog could not be loaded');
   const data=await response.json();if(!this.isConnected)return;
   this.textContent='';this._view=mountSkillsEstate(this,{data,downloadBase:this.getAttribute('downloads-base-url')||new URL('.',new URL(source,location.href)).href,onSelect:id=>this.dispatchEvent(new CustomEvent('skill-select',{detail:{id},bubbles:true}))});
  })().catch(error=>{if(error.name==='AbortError')return;this.textContent=error.message;this.setAttribute('role','alert')});
 }
 disconnectedCallback(){this._abort?.abort();this._view?.destroy()}
}
if(!customElements.get('skills-estate-explorer'))customElements.define('skills-estate-explorer',SkillsEstateExplorer);
'''
    return header + 'root.innerHTML=' + json.dumps(body) + ';\n' + code + footer


def export(data, settings, target, output, packages=None):
    from rendering import render_snapshot
    output = Path(output).resolve()
    if output.is_symlink():
        raise ValueError('Choose a regular export directory')
    if output.exists() and any(output.iterdir()):
        raise ValueError('Choose an empty export directory; existing exports are kept')
    payload, omitted = project(data, settings, target)
    output.mkdir(parents=True, exist_ok=True)
    payload['taskDownloadsAvailable']=bool(packages)
    render_snapshot(payload, output / 'index.html')
    (output / 'catalog.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
    (output / 'workflows.json').write_text(json.dumps(payload['workflows'], ensure_ascii=False, indent=2) + '\n')
    (output / 'skills-estate.js').write_text(component_source())
    css = ':host{display:block;min-width:0}\n'+(HERE / 'explorer.css').read_text().replace(':root', ':host').replace('html{', ':host{').replace('body{', '.estate-root{').replace('body.printing-detail','.estate-root.printing-detail')
    (output / 'explorer.css').write_text(css)
    (output / 'integration-example.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Skills Estate integration example</title><style>body{font:16px system-ui;margin:0;background:white;color:#242521}.host-heading{padding:24px;margin:0}skills-estate-explorer{display:block;--estate-accent:#a3401d}</style><h1 class="host-heading">Skills Estate integration example</h1><p class="host-heading">This host page imports the reusable component. Its styles remain scoped to the explorer.</p><script type="module" src="./skills-estate.js"></script><skills-estate-explorer catalog-src="./catalog.json"></skills-estate-explorer></html>''')
    shutil.copytree(HERE / 'assets', output / 'assets', dirs_exist_ok=True)
    names = sorted({n for skill in payload['skills'] for n in skill.get('downloadPackages', [])})
    downloads = False
    if packages:
        packages = Path(packages).resolve()
        if (packages/'manifest.json').is_file():manifest=json.loads((packages/'manifest.json').read_text())
        else:
            release=json.loads((packages/'release.json').read_text())
            manifest={'commit':release['source_commit'],'packages':release['packages']}
        if manifest.get('commit') != data['baseCommit']:
            raise ValueError('Download packages must match the catalog source commit')
        dest = output / 'downloads' / data['baseCommit']; dest.mkdir(parents=True)
        selected = {}
        for name in names:
            item = manifest['packages'][name]
            if item.get('file') != name + '.zip':raise ValueError('Invalid package filename')
            raw = (packages / item['file']).read_bytes()
            if hashlib.sha256(raw).hexdigest() != item['sha256']:raise ValueError('Package hash mismatch: ' + name)
            with zipfile.ZipFile(packages / item['file']) as archive:
                if archive.testzip():raise ValueError('Corrupt package: ' + name)
            (dest / item['file']).write_bytes(raw); selected[name] = item
        (dest / 'manifest.json').write_text(json.dumps({'commit': data['baseCommit'], 'packages': selected}, indent=2) + '\n')
        downloads = True
    manifest = {'format': 1, 'target': target, 'sourceCommit': data['baseCommit'], 'settingsRevision': revision(settings), 'skills': len(payload['skills']), 'workflows': len(payload['workflows']), 'plugins': len(payload['plugins']), 'taskDownloadsIncluded': downloads, 'generatedAt': datetime.now(timezone.utc).isoformat()}
    manifest['files'] = {str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.rglob('*')) if p.is_file()}
    (output / 'publication.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest, omitted


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog', type=Path, default=HERE / 'index.json')
    parser.add_argument('--settings', type=Path, default=CONFIG)
    parser.add_argument('--target', choices=TARGETS, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--packages', type=Path)
    args = parser.parse_args()
    result, omitted = export(json.loads(args.catalog.read_text()), load(args.settings), args.target, args.output, args.packages)
    print(json.dumps({'output': str(args.output), 'skills': result['skills'], 'workflows': result['workflows'], 'plugins': result['plugins'], 'workflowsBlockedByHiddenSkills': omitted}))


if __name__ == '__main__':
    main()
