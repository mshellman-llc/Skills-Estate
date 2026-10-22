#!/usr/bin/env python3
"""Build a portable, offline map from complete SKILL.md entrypoints (stdlib only)."""
import argparse, hashlib, html, json, re, subprocess
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
FAMILIES = [
 ('Pursuit and discovery', 'Understand the account, the customer journey, and the next conversation.', 'call-prep discovery-brief discovery-synthesis jtbd-framing playbook-fit-router sales-process-mapping sales-journey-critique live-meeting-synthesis'),
 ('Scope and proposals', 'Define an offer, compare options, and put scope and commercials in writing.', 'architecture-doc business-case ddoc deal-desk interactive-proposal playbook-builder playbook-onepager playbook-suite rom scope-reference scoping-agent solution-brief sow sow-quality'),
 ('Delivery and Salesforce', 'Move from an accepted handoff through implementation, testing, and closeout.', 'cutover-closeout delivery-kickoff delivery-status delivery-suite dx-devops-promote dx-devops-work-item-manage org-preflight requirements-capture s2d-handoff sf-delivery-standards sf-deploy-engine sf-enterprise-patterns sf-headless-screenshot sf-solo-devops team-onboarding uat-validation'),
 ('Product and experience', 'Research needs, define products, and review the experience people use.', 'accessibility-audit analytics-strategy independent-product information-architecture journey-mapping pm-spec-writing process product-development-pathway spec-writer system-design usability-testing'),
 ('Knowledge and context', 'Find the current record, preserve evidence, and carry work between sessions.', 'beastmode-capture beastmode-context beastmode-health beastmode-reconcile brain-work-item evidence-core knowledge-hub session-handoff transcript-ingestion'),
 ('Writing and presentation', 'Shape the words, visual structure, and author voice of an artifact.', 'client-brand deck-builder editorial-design megan-writing-style personal-writing-style-runtime writing-integrity writing-style-builder'),
 ('Career and personal', 'Prepare career materials and work with the private planning and creative tools.', 'career-application career-materials-and-outreach career-progression-and-offers case-study-builder resume-numbers-and-keywords fortunes-weave sticker-sheets'),
 ('Estate and engineering controls', 'Maintain skills, review changes, and verify where a result actually exists.', 'code-simplify execution-truth github-repository-work quality-gate skill-creation-walkthrough skill-estate-sync'),
]
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

def inventory(folder):
    result = []
    for p in sorted(folder.rglob('*')):
        rel = p.relative_to(folder)
        if not p.is_file() or any(x.startswith('.') or x == '__pycache__' for x in rel.parts) or p.suffix == '.pyc': continue
        result.append({'path': rel.as_posix(), 'sha256': digest(p.read_bytes()), 'bytes': p.stat().st_size, 'gitBlob': blob_digest(p.read_bytes())})
    return result

def build(args):
    root = args.repo.resolve(); baseline = (args.baseline_repo or root).resolve()
    ref = args.base or git(baseline, 'rev-parse', 'HEAD').decode().strip()
    ref = git(baseline, 'rev-parse', ref+'^{commit}').decode().strip()
    tree = git(baseline, 'ls-tree', '-r', ref, 'skills').decode().splitlines()
    base_blobs = {line.split('\t',1)[1]: line.split('\t',1)[0].split()[2] for line in tree}
    base_files = list(base_blobs)
    base_skills = {p.split('/')[1] for p in base_files if re.fullmatch(r'skills/[^/]+/SKILL.md', p)}
    folders = {p.parent.name: (p.parent, False) for p in root.glob('skills/*/SKILL.md')}
    for folder in args.extra:
        folder = folder.resolve()
        name = folder.name
        if name in folders: raise ValueError('Extra shadows canonical skill: '+name)
        if not (folder/'SKILL.md').is_file(): raise ValueError('Missing extra SKILL.md: '+str(folder))
        folders[name] = (folder, True)
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
        paragraphs = re.split(r'\n\s*\n', re.sub(r'^#\s+.+\n', '', body, count=1).strip())
        # Show source paragraphs in their original order. Shared policy routing remains in the runbook.
        work = [p for p in paragraphs if not re.match(r'^(Read \[shared workflow\]|#{1,6} |```|\|)', p)]
        excerpt = work[:3]
        headings = re.findall(r'^#{2,3}\s+(.+)', body, re.M)
        links = []
        for other in folders:
            if other == name: continue
            pattern = r'(?<![\w-])'+re.escape(other)+r'(?![\w-])' if '-' in other else r'(?:`'+re.escape(other)+r'`|\['+re.escape(other)+r'\]|'+re.escape(other)+r' skill)'
            matches = list(re.finditer(pattern, body))
            if matches:
                m=matches[0]; start=max(0,body.rfind('\n\n',0,m.start())+2); end=body.find('\n\n',m.end())
                links.append({'name': other, 'context': body[start:end if end != -1 else len(body)].strip()})
        skills.append({'id':name, 'title':title, 'family':GROUPS[name], 'description':meta['description'], 'status':status,
            'entrypointChanged': base_blob is not None and blob_digest(raw) != base_blob,
            'sourcePath':repo_path if not extra else f'local-skills/{name}/SKILL.md',
            'sourceSha256':digest(raw), 'githubUrl': f'https://github.com/mshellman-llc/Skills-Estate/blob/{ref}/{repo_path}' if base_blob is not None else None,
            'markdown':source, 'html':markdown(body), 'excerptHtml':''.join(markdown(p) for p in excerpt),
            'headings':headings, 'mentions':links, 'resources':resources})
    data={'schemaVersion':1, 'generatedAt':datetime.now(timezone.utc).isoformat(), 'baseCommit':ref,
          'repository':'mshellman-llc/Skills-Estate', 'families':[{'title':x[0],'description':x[1]} for x in FAMILIES], 'skills':skills}
    data['counts']={s:sum(x['status']==s for x in skills) for s in ['github','local-revision','local-addition']}
    data['counts']['canonical']=sum(x['id'] in base_skills for x in skills)
    data['counts']['total']=len(skills)
    encoded=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    output=args.output.resolve(); output.parent.mkdir(parents=True,exist_ok=True)
    template=(HERE/'template.html').read_text()
    output.write_text(template.replace('__ESTATE_DATA__',encoded))
    output.with_suffix('.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'output':str(output),'base':ref,'counts':data['counts']}))
    return data

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',type=Path,default=HERE.parents[1]); p.add_argument('--base',help='Verified Git commit for comparison; defaults to repo HEAD')
    p.add_argument('--baseline-repo',type=Path,help='Git checkout containing the compared commit; defaults to --repo')
    p.add_argument('--extra',type=Path,action='append',default=[],help='Explicit local skill folder; can repeat')
    p.add_argument('--output',type=Path,default=HERE/'index.html')
    build(p.parse_args())
