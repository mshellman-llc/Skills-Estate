#!/usr/bin/env python3
"""Build a portable, offline map from complete SKILL.md entrypoints (stdlib only)."""
import argparse, hashlib, html, json, re, subprocess
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
import sys
sys.path.insert(0,str(HERE.parents[1]/'tools'))
from browse import load_groups
from skill_guide import load as load_guides, assessment, overview_excerpt, readable_body, scan
FAMILIES = [(g['title'],g['description'],' '.join(g['skills'])) for g in load_groups(HERE.parents[1],check_coverage=False)]
DEFAULT_PUBLISHED_REF = 'refs/remotes/origin/main'
GROUPS = {name: i for i, (_, _, members) in enumerate(FAMILIES) for name in members.split()}

def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.DEVNULL)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def blob_digest(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()

def frontmatter(source):
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', source, re.S)
    if not match:
        raise ValueError('SKILL.md needs frontmatter')
    fields = {}
    for line in match[1].splitlines():
        if line.startswith(('name:', 'description:')):
            key, value = line.split(':', 1)
            fields[key] = value.strip().strip('"').strip("'")
    if not fields.get('name') or not fields.get('description'):
        raise ValueError('Missing name or one-line description')
    return fields, source[match.end():]

def inline(text):
    """Render only a small, escaped Markdown subset; no source HTML is executed."""
    s = html.escape(text)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    def link(m):
        label, target = m.groups()
        if target.startswith(('https://', 'http://')):
            return f'<a href="{target}" target="_blank" rel="noopener noreferrer">{label}</a>'
        return f'{label} <span class="ref">({target})</span>'
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, s)
    return s

def markdown(text):
    """Readable view. Exact Markdown is retained separately for download and comparison."""
    out, paragraph, listing, code = [], [], None, None
    def flush():
        if paragraph:
            out.append('<p>' + inline(' '.join(paragraph)) + '</p>'); paragraph.clear()
    def endlist():
        nonlocal listing
        if listing:
            out.append(f'</{listing}>'); listing = None
    lines = text.splitlines(); i = 0
    while i < len(lines):
        line = lines[i]; i += 1
        if line.startswith('```'):
            flush(); endlist()
            if code is None: code = []
            else: out.append('<pre><code>' + html.escape('\n'.join(code)) + '</code></pre>'); code = None
            continue
        if code is not None: code.append(line); continue
        if not line.strip(): flush(); endlist(); continue
        heading = re.match(r'^(#{1,6})\s+(.+)', line)
        if heading:
            flush(); endlist(); level = min(len(heading[1])+1, 6)
            out.append(f'<h{level}>{inline(heading[2])}</h{level}>'); continue
        if line.strip().startswith('|') and i < len(lines) and re.match(r'^\s*\|[\s:|\-]+\|\s*$', lines[i]):
            flush(); endlist()
            cells = lambda row: [x.strip() for x in row.strip().strip('|').split('|')]
            heads = cells(line); i += 1
            out.append('<div class="table-scroll"><table><thead><tr>' + ''.join('<th scope="col">'+inline(c)+'</th>' for c in heads) + '</tr></thead><tbody>')
            while i < len(lines) and lines[i].strip().startswith('|'):
                out.append('<tr>'+''.join('<td>'+inline(c)+'</td>' for c in cells(lines[i]))+'</tr>'); i += 1
            out.append('</tbody></table></div>'); continue
        item = re.match(r'^\s*(?:([-*])\s+|(\d+)\.\s+)(.+)', line)
        if item:
            flush(); tag = 'ul' if item[1] else 'ol'
            if listing != tag:
                endlist(); out.append(f'<{tag}>'); listing = tag
            out.append('<li>'+inline(item[3])+'</li>'); continue
        if line.startswith('>'):
            flush(); endlist(); out.append('<blockquote>'+inline(line.lstrip('> '))+'</blockquote>'); continue
        endlist(); paragraph.append(line.strip())
    flush(); endlist()
    if code is not None: out.append('<pre><code>'+html.escape('\n'.join(code))+'</code></pre>')
    return ''.join(out)

def connection_excerpt(body, match):
    """Render the relevant source row or paragraph without exposing Markdown syntax."""
    previous_break=body.rfind('\n\n',0,match.start())
    start=previous_break+2 if previous_break>=0 else 0
    end=body.find('\n\n',match.end())
    context=body[start:end if end!=-1 else len(body)].strip()
    line_start=body.rfind('\n',0,match.start())+1
    line_end=body.find('\n',match.end())
    row=body[line_start:line_end if line_end!=-1 else len(body)].strip()
    if row.startswith('|'):
        lines=context.splitlines()
        for i in range(len(lines)-1):
            if lines[i].strip().startswith('|') and re.fullmatch(r'\s*\|[\s:|\-]+\|\s*',lines[i+1]):
                # Preserve the exact matching row and its original column labels.
                return {'context':row,'contextHtml':markdown('\n'.join([lines[i],lines[i+1],row]))}
    return {'context':context,'contextHtml':markdown(context)}

def included(parts):
    """Single inclusion rule for package files, given path parts relative to the skill folder."""
    return not any(x.startswith('.') or x == '__pycache__' for x in parts) and Path(parts[-1]).suffix != '.pyc'

def inventory(folder):
    result = []
    for p in sorted(folder.rglob('*')):
        rel = p.relative_to(folder)
        if not p.is_file() or not included(rel.parts): continue
        result.append({'path': rel.as_posix(), 'sha256': digest(p.read_bytes()), 'bytes': p.stat().st_size, 'gitBlob': blob_digest(p.read_bytes())})
    return result

def verified_base(baseline, base, published_ref):
    """Resolve an explicit base commit and require it to be reachable from the published ref.

    The published ref is a locally observed remote-tracking ref, not a live GitHub check;
    this function performs no network work.
    """
    if not base:
        raise ValueError('Explicit --base commit is required; it is not defaulted to HEAD')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._/@^~-]*', base) or '..' in base:
        raise ValueError('Malformed base: '+repr(base))
    if not published_ref or not published_ref.startswith('refs/remotes/') or published_ref.endswith('/'):
        raise ValueError('Published ref must be a remote-tracking ref under refs/remotes/: '+repr(published_ref))
    if subprocess.run(['git', 'check-ref-format', published_ref], capture_output=True).returncode != 0:
        raise ValueError('Malformed published ref: '+repr(published_ref))
    try:
        published = git(baseline, 'rev-parse', '--verify', '--quiet', published_ref+'^{commit}').decode().strip()
    except subprocess.CalledProcessError:
        raise ValueError('Published ref not found in baseline repo (fetch it first): '+published_ref)
    try:
        commit = git(baseline, 'rev-parse', '--verify', '--quiet', base+'^{commit}').decode().strip()
    except subprocess.CalledProcessError:
        raise ValueError('Base is not a commit in the baseline repo: '+base)
    result = subprocess.run(['git', '-C', str(baseline), 'merge-base', '--is-ancestor', commit, published], capture_output=True)
    if result.returncode == 1:
        raise ValueError(f'Base {commit} is not reachable from {published_ref}; it is unpublished')
    if result.returncode != 0:
        raise ValueError('Could not check base ancestry against '+published_ref)
    return commit

SHOWCASE_FIELDS = ('skill', 'title', 'source', 'model', 'date', 'skillSha256')
SHOWCASE_SOURCES = {'fictional', 'real-redacted'}
SHOWCASE_SECTIONS = ('## Request', '## Output')

def showcase_example(path):
    """Parse one recorded example. Its output is shown as recorded, rendered without executing HTML."""
    source = path.read_text(encoding='utf-8')
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', source, re.S)
    if not match:
        raise ValueError(f'{path}: example needs frontmatter')
    fields = {}
    for line in match[1].splitlines():
        if ':' in line:
            key, value = line.split(':', 1)
            fields[key.strip()] = value.strip().strip('"').strip("'")
    missing = [k for k in SHOWCASE_FIELDS if not fields.get(k)]
    if missing:
        raise ValueError(f'{path}: missing {", ".join(missing)}')
    if fields['source'] not in SHOWCASE_SOURCES:
        raise ValueError(f'{path}: source must be fictional or real-redacted')
    if fields['source'] == 'real-redacted' and not fields.get('approvedBy'):
        raise ValueError(f'{path}: a real-redacted example needs approvedBy')
    if not re.fullmatch(r'[0-9a-f]{64}', fields['skillSha256']):
        raise ValueError(f'{path}: skillSha256 must be a SHA-256 hex digest')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', fields['date']):
        raise ValueError(f'{path}: date must be YYYY-MM-DD')
    body = source[match.end():]
    for heading in SHOWCASE_SECTIONS:
        if not re.search('^'+re.escape(heading)+r'\s*$', body, re.M):
            raise ValueError(f'{path}: missing "{heading}" section')
    return {'id': path.stem, 'title': fields['title'], 'source': fields['source'],
            'approvedBy': fields.get('approvedBy') or None, 'model': fields['model'], 'date': fields['date'],
            'skillSha256': fields['skillSha256'], 'skill': fields['skill'], 'markdown': body, 'html': markdown(body)}

def load_showcase(root, current):
    """Group recorded examples by skill; `current` maps skill id to its SKILL.md SHA-256."""
    examples = {}
    folder = root / 'showcase'
    if not folder.is_dir():
        return examples
    for path in sorted(folder.glob('*/*.md')):
        if path.name == 'README.md' or path.name.startswith('.'):
            continue
        item = showcase_example(path)
        if item['skill'] != path.parent.name:
            raise ValueError(f'{path}: skill field must match its folder')
        if item['skill'] not in current:
            raise ValueError(f'{path}: unknown skill {item["skill"]}')
        item['current'] = item['skillSha256'] == current[item['skill']]
        examples.setdefault(item['skill'], []).append(item)
    for items in examples.values():
        items.sort(key=lambda x: (x['source'] != 'real-redacted', x['date'], x['id']), reverse=False)
    return examples

DOWNLOADS=re.compile(r'<!--downloads-->.*?<!--/downloads-->|/\*downloads\*/.*?/\*/downloads\*/',re.S)

TOOL_SUFFIXES = ('.py', '.cjs', '.mjs', '.js', '.sh')

def manifest_fields(path):
    """Read the few skill.yaml fields the map shows. The estate uses only the standard library, so
    this handles the manifest's simple layout: top-level keys, scalar lists, lists of mappings with
    scalar values, and one level of nested mappings with scalar lists (connectors)."""
    if not path.is_file():
        return None
    data, key, sub, item = {}, None, None, None
    for line in path.read_text().splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        indent = len(line) - len(line.lstrip())
        text = line.strip()
        if text.startswith('- ') and indent <= 2 and key and not isinstance(data.get(key), dict):
            indent = 1  # list items may sit at the key's own margin
        if indent == 0 and ':' not in text:
            continue  # continuation of a wrapped scalar
        if indent == 0:
            key, sub, item = text.split(':', 1)[0], None, None
            value = text.split(':', 1)[1].strip()
            data[key] = [] if value in ('', '[]') else value.strip('"\'')
        elif text.startswith('- '):
            value = text[2:].strip()
            target = data[key][sub] if isinstance(data.get(key), dict) and sub else data.setdefault(key, [])
            if not isinstance(target, list):
                target = data[key] = []
            if ':' in value and not value.startswith(('"', "'")):
                k, v = value.split(':', 1); item = {k.strip(): v.strip().strip('"\'')}; target.append(item)
            else:
                item = None; target.append(value.strip('"\''))
        elif ':' in text:
            k, v = text.split(':', 1); k, v = k.strip(), v.strip()
            if item is not None and (indent >= 4 or not isinstance(data.get(key), dict)):
                item[k] = v.strip('"\'')
            else:
                if not isinstance(data.get(key), dict):
                    data[key] = {}
                sub = k; item = None
                data[key][k] = [] if v in ('', '[]') else v.strip('"\'')
    return data

def router_skills(root):
    """Map each skill to the router agents that list it under Available skills."""
    routes = {}
    for path in sorted((root / 'agents').glob('*-router.md')):
        text = path.read_text()
        section = re.search(r'^## Available skills\n(.*?)(?=^## |\Z)', text, re.M | re.S)
        for name in re.findall(r'^- `([a-z0-9-]+)`', section[1] if section else '', re.M):
            routes.setdefault(name, []).append(path.stem)
    return routes

def skill_profile(name, folder, resources, guide, reuse, role, dependencies, used_by, routes, bundle_entries={}):
    manifest = manifest_fields(folder / 'skill.yaml') or {}
    connectors = manifest.get('connectors') if isinstance(manifest.get('connectors'), dict) else None
    authored = (guide or {}).get('connectors')
    if connectors is not None:
        connectors = {'required': connectors.get('required') or [], 'optional': connectors.get('optional') or [], 'source': 'skill.yaml'}
    elif isinstance(authored, dict):
        connectors = {'required': authored.get('required', []), 'optional': authored.get('optional', []), 'source': 'guide'}
    outputs = [o for o in manifest.get('outputs', []) if isinstance(o, dict)]
    return {
        'tools': [r['path'] for r in resources if r['path'].startswith('scripts/') and r['path'].endswith(TOOL_SUFFIXES)],
        'connectors': connectors,
        'outputs': [{'name': o.get('name', ''), 'format': o.get('format', '')} for o in outputs],
        'modes': role['modes'],
        'agents': routes.get(name, []),
        'plugins': sorted(n for n, entries in bundle_entries.items() if entries & ({*role['tasks'], *(m['task'] for m in role['modes'])})),
        'bundles': dependencies.get(name, []),
        'usedBy': sorted(used_by.get(name, [])),
        'calls': [c for c in manifest.get('calls', []) if isinstance(c, str)],
        'dependsOn': [c for c in manifest.get('depends_on', []) if isinstance(c, str)],
        'runtimes': [r for r in manifest.get('runtimes', []) if isinstance(r, str)],
        'setup': (reuse or {}).get('setup', '') or (guide or {}).get('requires', ''),
        'expect': (guide or {}).get('expect', ''),
        'declared': bool(manifest),
    }

def render_snapshot(data,output,downloads=True):
    encoded=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    template=(HERE/'template.html').read_text()
    if not downloads:
        # Hosts that cannot save files (the claude.ai artifact viewer) get no download controls or download code.
        template=DOWNLOADS.sub('',template)
    else:
        template=template.replace('<!--downloads-->','').replace('<!--/downloads-->','').replace('/*downloads*/','').replace('/*/downloads*/','')
    Path(output).write_text(template.replace('__ESTATE_DATA__',encoded))

def plugin_map(root):
    """Map each task package to the marketplace plugin that installs it."""
    path=root/'config/plugin-bundles.json'
    if not path.is_file(): return {}
    bundles=json.loads(path.read_text())['bundles']
    return {task:{'plugin':name,'optIn':bool(item.get('opt_in'))} for name,item in bundles.items() for task in item['entries']}

def marketplace(root):
    path=root/'.claude-plugin/marketplace.json'
    return json.loads(path.read_text())['name'] if path.is_file() else None

def load_workflows(root, names):
    """Newcomer workflows from the reader-guide config; every step must name a mapped skill."""
    path=root/'config/skill-guide.json'
    items=json.loads(path.read_text()).get('workflows',[]) if path.is_file() else []
    seen=set()
    for item in items:
        if item['id'] in seen: raise ValueError('Duplicate workflow id: '+item['id'])
        seen.add(item['id'])
        for field in ('title','when','note'):
            if not str(item.get(field,'')).strip(): raise ValueError(f'Workflow {item["id"]} needs {field}')
        if not item.get('steps'): raise ValueError(f'Workflow {item["id"]} needs steps')
        for step in item['steps']:
            if step.get('skill') not in names: raise ValueError(f'Workflow {item["id"]} names an unmapped skill: {step.get("skill")}')
            for field in ('give','get'):
                if not str(step.get(field,'')).strip(): raise ValueError(f'Workflow {item["id"]} step {step["skill"]} needs {field}')
    return items

def build(args):
    root = args.repo.resolve(); baseline = (args.baseline_repo or root).resolve()
    guides = load_guides(HERE.parents[1])
    ref = verified_base(baseline, args.base, args.published_ref)
    tree = [e for e in git(baseline, 'ls-tree', '-r', '-z', ref, 'skills').decode().split('\0') if e]
    base_blobs = {}
    for entry in tree:
        meta, path = entry.split('\t', 1)
        parts = path.split('/')
        if len(parts) > 2 and included(parts[2:]):
            base_blobs[path] = meta.split()[2]
    base_files = list(base_blobs)
    base_skills = {p.split('/')[1] for p in base_files if re.fullmatch(r'skills/[^/]+/SKILL.md', p)}
    folders = {p.parent.name: (p.parent, False) for p in root.glob('skills/*/SKILL.md')}
    for folder in args.extra:
        folder = folder.resolve()
        name = folder.name
        if name in folders: raise ValueError('Extra shadows canonical skill: '+name)
        if not (folder/'SKILL.md').is_file(): raise ValueError('Missing extra SKILL.md: '+str(folder))
        folders[name] = (folder, True)
    from catalog import entries as task_entries, dependencies as task_dependencies
    from portable import runtime_closure
    task_catalog=task_entries(root)
    plugins=plugin_map(root)
    package_members={task:{item['source'],*task_dependencies(root,item,runtime_closure)} for task,item in task_catalog.items()}
    dependencies = json.loads((root/'config/runtime-dependencies.json').read_text()) if (root/'config/runtime-dependencies.json').is_file() else {}
    used_by = {}
    for owner, needs in dependencies.items():
        for need in needs:
            used_by.setdefault(need, []).append(owner)
    routes = router_skills(root)
    bundle_entries = {n: set(b.get('entries', [])) for n, b in json.loads((root/'config/plugin-bundles.json').read_text())['bundles'].items()} if (root/'config/plugin-bundles.json').is_file() else {}
    skills = []
    for name, (folder, extra) in sorted(folders.items()):
        if name not in GROUPS: raise ValueError('Assign a family before building: '+name)
        raw = (folder/'SKILL.md').read_bytes(); source = raw.decode('utf-8')
        meta, body = frontmatter(source)
        if meta['name'] != name: raise ValueError('Folder/name mismatch: '+name)
        resources = inventory(folder)
        if next(x['sha256'] for x in resources if x['path']=='SKILL.md') != digest(raw):
            raise ValueError('Entrypoint changed while capturing: '+name)
        repo_path = f'skills/{name}/SKILL.md'
        base_blob = base_blobs.get(repo_path)
        package_changed = False
        if name in base_skills:
            expected = {p[len('skills/'+name+'/'):] for p in base_files if p.startswith('skills/'+name+'/')}
            package_changed = expected != {x['path'] for x in resources}
            if not package_changed:
                package_changed = any(base_blobs.get(f'skills/{name}/{x["path"]}') != x['gitBlob'] for x in resources)
        status = 'local-addition' if extra or name not in base_skills else 'local-revision' if package_changed else 'github'
        title = re.search(r'^#\s+(.+)', body, re.M)
        title = title[1] if title else name.replace('-', ' ').capitalize()
        title = {'jtbd-framing': 'JTBD framing', 'ddoc': 'Deal decision deck', 'rom': 'Rough order of magnitude', 'sow': 'Statement of work', 'sow-quality': 'SOW quality', 's2d-handoff': 'Sales-to-delivery handoff'}.get(name, title)
        title = title[:1].upper()+title[1:]
        excerpt = overview_excerpt(body)
        guide = guides.get(name, {})
        guide_current = guide.get('reviewedEntrypointSha256') == digest(raw)
        reuse = assessment(root, name, guide, resources) if (root/'config/runtime-dependencies.json').is_file() else None
        primary=[task for task,item in task_catalog.items() if item['source']==name]
        modes=[{'task':task,'mode':mode} for task,item in task_catalog.items() for mode,module in item.get('modes',{}).items() if module==name]
        role={'kind':'task' if primary else 'mode' if modes else 'support','tasks':primary,'modes':modes}
        headings = re.findall(r'^#{2,3}\s+(.+)', body, re.M)
        link_body = readable_body(body)
        links = []
        for other in folders:
            if other == name: continue
            pattern = r'(?<![\w-])'+re.escape(other)+r'(?![\w-])' if '-' in other else r'(?:`'+re.escape(other)+r'`|\['+re.escape(other)+r'\]|'+re.escape(other)+r' skill)'
            matches = list(re.finditer(pattern, link_body))
            if matches:
                links.append({'name':other,**connection_excerpt(link_body,matches[0])})
        skills.append({'id':name, 'title':title, 'family':GROUPS[name], 'description':meta['description'], 'status':status,
            'entrypointChanged': base_blob is not None and blob_digest(raw) != base_blob,
            'sourcePath':repo_path if not extra else f'local-skills/{name}/SKILL.md',
            'sourceSha256':digest(raw), 'githubUrl': f'https://github.com/mshellman-llc/Skills-Estate/blob/{ref}/{repo_path}' if base_blob is not None else None,
            'taskPackages':[{'name':task,'mode':None} for task,item in task_catalog.items() if item['source']==name]+[{'name':task,'mode':mode} for task,item in task_catalog.items() for mode,module in item.get('modes',{}).items() if module==name],
            'downloadPackages':[task for task,members in package_members.items() if name in members],
            'guide':guide if guide_current else None, 'guideStatus':'current' if guide_current else 'needs-review', 'reuse':reuse,
            'catalogRole':role,
            'install':[{'task':task,**plugins[task]} for task in dict.fromkeys(primary+[m['task'] for m in modes]) if task in plugins],
            'profile':skill_profile(name, folder, resources, guide if guide_current else None, reuse, role, dependencies, used_by, routes, bundle_entries),
            'markdown':source, 'html':markdown(readable_body(body)), 'excerptHtml':''.join(markdown(p) for p in excerpt),
            'headings':headings, 'mentions':links, 'resources':resources})
    showcase = load_showcase(root, {s['id']: s['sourceSha256'] for s in skills})
    for s in skills:
        if not s['install'] and s['catalogRole']['kind']=='support':
            bundled={plugins[task]['plugin']:plugins[task] for task in s['downloadPackages'] if task in plugins}
            s['install']=[{'task':None,**item,'bundled':True} for _,item in sorted(bundled.items())]
    for s in skills:
        s['examples'] = showcase.get(s['id'], [])
    data={'schemaVersion':1, 'generatedAt':datetime.now(timezone.utc).isoformat(), 'baseCommit':ref,
          'repository':'mshellman-llc/Skills-Estate', 'marketplace':marketplace(root), 'workflows':load_workflows(root,{s['id'] for s in skills}), 'families':[{'id':g['id'],'title':g['title'],'description':g['description']} for g in load_groups(HERE.parents[1],check_coverage=False)], 'skills':skills}
    data['counts']={s:sum(x['status']==s for x in skills) for s in ['github','local-revision','local-addition']}
    data['counts']['canonical']=sum(x['id'] in base_skills for x in skills)
    data['counts']['total']=len(skills)
    data['counts']['withExamples']=sum(bool(x['examples']) for x in skills)
    encoded=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    output=args.output.resolve(); output.parent.mkdir(parents=True,exist_ok=True)
    render_snapshot(data,output,downloads=not getattr(args,'no_downloads',False))
    output.with_suffix('.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'output':str(output),'base':ref,'counts':data['counts']}))
    return data

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',type=Path,default=HERE.parents[1]); p.add_argument('--base',required=True,help='Git commit for comparison; must be reachable from --published-ref')
    p.add_argument('--published-ref',default=DEFAULT_PUBLISHED_REF,help='Locally refreshed remote-tracking ref that marks published history (default: %(default)s)')
    p.add_argument('--baseline-repo',type=Path,help='Git checkout containing the compared commit; defaults to --repo')
    p.add_argument('--extra',type=Path,action='append',default=[],help='Explicit local skill folder; can repeat')
    p.add_argument('--output',type=Path,default=HERE/'index.html')
    p.add_argument('--no-downloads',action='store_true',help='Omit download buttons and code, for hosts that cannot save files such as the claude.ai artifact viewer')
    build(p.parse_args())
