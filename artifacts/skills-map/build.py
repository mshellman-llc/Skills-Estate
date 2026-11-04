#!/usr/bin/env python3
"""Build a portable, offline map from complete SKILL.md entrypoints (stdlib only)."""
import argparse, base64, hashlib, html, json, re, subprocess
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

def render_snapshot(data,output):
    encoded=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    template=(HERE/'template.html').read_text()
    faces=[]
    for weight,name in [(400,'Regular'),(600,'SemiBold'),(700,'Bold')]:
        font=base64.b64encode((HERE/f'assets/fonts/PlusJakartaSans-{name}.ttf').read_bytes()).decode()
        faces.append('@font-face{font-family:"Plus Jakarta Sans";font-style:normal;font-weight:'+str(weight)+';font-display:swap;src:url(data:font/ttf;base64,'+font+') format("truetype")}')
    notice=html.escape((HERE/'assets/fonts/OFL.txt').read_text())
    result=template.replace('__MAP_FONT_FACES__','\n'.join(faces)).replace('__ESTATE_DATA__',encoded)
    result=result.replace('</head>','<script type="text/plain" id="font-license">'+notice+'</script>\n</head>')
    Path(output).write_text(result)

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
    package_members={task:{item['source'],*task_dependencies(root,item,runtime_closure)} for task,item in task_catalog.items()}
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
            'markdown':source, 'html':markdown(readable_body(body)), 'excerptHtml':''.join(markdown(p) for p in excerpt),
            'headings':headings, 'mentions':links, 'resources':resources})
    showcase = load_showcase(root, {s['id']: s['sourceSha256'] for s in skills})
    for s in skills:
        s['examples'] = showcase.get(s['id'], [])
    data={'schemaVersion':1, 'generatedAt':datetime.now(timezone.utc).isoformat(), 'baseCommit':ref,
          'repository':'mshellman-llc/Skills-Estate', 'families':[{'id':g['id'],'title':g['title'],'description':g['description']} for g in load_groups(HERE.parents[1],check_coverage=False)], 'skills':skills}
    data['counts']={s:sum(x['status']==s for x in skills) for s in ['github','local-revision','local-addition']}
    data['counts']['canonical']=sum(x['id'] in base_skills for x in skills)
    data['counts']['total']=len(skills)
    data['counts']['withExamples']=sum(bool(x['examples']) for x in skills)
    encoded=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    output=args.output.resolve(); output.parent.mkdir(parents=True,exist_ok=True)
    render_snapshot(data,output)
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
    build(p.parse_args())
