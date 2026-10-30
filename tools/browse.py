#!/usr/bin/env python3
"""Build the GitHub browse pages and shareable collections from the map groups."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urljoin
import zipfile
from catalog import source_names

ROOT = Path(__file__).resolve().parents[1]
START, END = '<!-- SKILL-GROUPS:BEGIN -->', '<!-- SKILL-GROUPS:END -->'

def unique_object(pairs):
    result = {}
    for k, v in pairs:
        if k in result: raise ValueError('Duplicate group field: '+k)
        result[k] = v
    return result

def load_groups(root=ROOT, check_coverage=True):
    root=Path(root)
    config=json.loads((root/'config/skill-groups.json').read_text(), object_pairs_hook=unique_object)
    if config.get('format') != 1 or not config.get('groups'): raise ValueError('Missing skill groups')
    ids, owners = set(), {}
    for group in config['groups']:
        identifier=group['id']
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',identifier) or identifier in ids:
            raise ValueError('Invalid or duplicate group: '+identifier)
        ids.add(identifier)
        if not group.get('title') or not group.get('description'): raise ValueError('Group needs a title and description')
        for name in group['skills']:
            if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',name) or name in owners:
                raise ValueError('Invalid or duplicate skill assignment: '+name)
            owners[name]=identifier
    if check_coverage:
        actual=source_names(root)
        optional=set(config.get('optionalSkills',[]))
        if actual-set(owners) or set(owners)-actual-optional:
            raise ValueError('Group coverage differs: '+', '.join(sorted((actual-set(owners)) | (set(owners)-actual-optional))))
    return config['groups']

def region(text, content):
    block=START+'\n'+content.strip()+'\n'+END
    if START in text:
        if text.count(START)!=1 or text.count(END)!=1: raise ValueError('Ambiguous group index markers')
        return re.sub(re.escape(START)+r'.*?'+re.escape(END),lambda _:block,text,flags=re.S)
    index=text.find('\n## ')
    if index<0: index=len(text)
    return text[:index]+'\n\n'+block+'\n'+text[index:]

def documents(root=ROOT):
    from catalog import entries, retired_entries
    root=Path(root);groups=load_groups(root);public=entries(root)
    retired = retired_entries(root)
    def source_link(name, prefix):
        link = f'[{name}]({prefix}skills/{name}/SKILL.md)'
        if name in retired:
            role = 'embedded workflow' if retired[name].get('allowed_as_mode') else 'internal diagnostics'
            link += f" — {role}; standalone skill retired, use `{retired[name]['successor']}`"
        return '- ' + link
    actual=source_names(root)
    result={};summary=['## Browse by work','', '| Group | Source workflows | Task packages |','| --- | ---: | ---: |']
    for g in groups:
        members=sorted(set(g['skills']) & actual)
        packages={n:item for n,item in public.items() if item['source'] in members or set(item.get('modes',{}).values()) & set(members)}
        summary.append(f"| [{g['title']}](browse/{g['id']}/README.md) | {len(members)} | {len(packages)} |")
        lines=[f"# {g['title']}",'',g['description'],'', '[All groups](../README.md) · [Interactive map](../../artifacts/skills-map/README.md)','',
               '## Task packages','', 'Each task links to its primary workflow. Packages are also listed here when one of their modes belongs to this group.','',
               '| Task | Primary workflow | Additional modes |','| --- | --- | --- |']
        for name,item in sorted(packages.items()):
            modes=', '.join(f"[{label}](../../skills/{module}/SKILL.md)" for label,module in item.get('modes',{}).items())
            lines.append(f"| `{name}` | [{item['source']}](../../skills/{item['source']}/SKILL.md) | {modes} |")
        if not packages: lines += ['','This group contains supporting workflows rather than standalone task packages.']
        lines += ['', '## Source workflows','']
        lines += [source_link(name, '../../') for name in members]
        lines += ['', '## Share this group','',
                  f"Share this GitHub page with someone who has repository access. The `skill-collections` workflow artifact contains `{g['id']}.zip`, with the complete task ZIPs listed above and a manifest.",
                  '', 'Package readiness follows the current [catalog](../../CATALOG.md).', '']
        result[f"browse/{g['id']}/README.md"]='\n'.join(lines)
    table='\n'.join(summary)+'\n'
    result['browse/README.md']='# Skills by work\n\nOpen a group to find its workflows and task packages. The interactive map uses these same groups.\n\n[Review intended audiences and sharing cleanup](reuse-review.md).\n\n'+table.replace('(browse/','(')+'\n[Open the interactive map](../artifacts/skills-map/README.md) · [Get the collections](https://github.com/mshellman-llc/Skills-Estate/actions/workflows/verify.yml)\n'
    counts=f'{len(actual)} source modules and {len(public)} proposed task entrypoints'
    for name in ['README.md','CATALOG.md']:
        body=region((root/name).read_text(),table)
        body,count=re.subn(r'\b\d+ source modules and \d+ proposed task entrypoints',counts,body)
        if count!=1:raise ValueError('Expected one inventory count in '+name)
        result[name]=body
    inventories={
        'Proposed task entrypoints':['| Entrypoint | Primary source | Included modes |','| --- | --- | --- |']+
            [f"| {name} | [{item['source']}](skills/{item['source']}/SKILL.md) | {', '.join(item.get('modes',{}).values())} |" for name,item in public.items()],
        'Source modules':['Each module needs a reviewed capability disposition before release.','']+
            [source_link(name, '') for name in sorted(actual)],
        'Routing agents':[f'- [{p.stem}](agents/{p.name})' for p in sorted((root/'agents').glob('*.md'))]}
    for title,lines in inventories.items():
        pattern=r'(?ms)^## '+re.escape(title)+r'\n.*?(?=^## |\Z)'
        body,count=re.subn(pattern,lambda _: '## '+title+'\n\n'+'\n'.join(lines)+'\n\n',result['CATALOG.md'])
        if count!=1:raise ValueError('Expected one catalog section: '+title)
        result['CATALOG.md']=body
    result['CATALOG.md']=result['CATALOG.md'].rstrip()+'\n'
    return result

def write_pages(root=ROOT, check=False):
    root=Path(root);changed=[]
    for name,body in documents(root).items():
        path=root/name
        if not path.exists() or path.read_text()!=body:
            changed.append(name)
            if not check:
                path.parent.mkdir(parents=True,exist_ok=True);path.write_text(body)
    if check and changed: raise ValueError('Regenerate group pages: '+', '.join(changed))
    return changed

def portable_readme(text,group,revision):
    base=f'https://github.com/mshellman-llc/Skills-Estate/blob/{revision}/browse/{group}/'
    return re.sub(r'\]\(([^)]+)\)',lambda m:']('+urljoin(base,m[1])+')',text)

def collections(root=ROOT):
    from catalog import entries
    import estate
    root=Path(root);public=entries(root);estate.current_build(root)
    revision=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
    release=json.loads((root/'dist/release.json').read_text())
    if release['source_sha256']!=estate.source_hash(root):raise ValueError('Package ZIPs are stale; run sync first')
    output=root/'dist/groups';output.mkdir(exist_ok=True)
    result=[]
    for g in load_groups(root):
        packages=sorted(n for n,item in public.items() if item['source'] in g['skills'] or set(item.get('modes',{}).values()) & set(g['skills']))
        manifest={'group':g['id'],'title':g['title'],'source_sha256':release['source_sha256'],'source_commit':revision,'packages':[]}
        payloads={}
        for name in packages:
            path=root/'dist'/f'{name}.zip';raw=path.read_bytes();digest=hashlib.sha256(raw).hexdigest()
            if digest!=release['packages'][name]['sha256']:raise ValueError('Task ZIP changed: '+name)
            payloads[f'skills/{name}.zip']=raw;manifest['packages'].append({'name':name,'sha256':digest})
        payloads['README.md']=portable_readme((root/f"browse/{g['id']}/README.md").read_text(),g['id'],revision).encode()
        payloads['manifest.json']=(json.dumps(manifest,indent=2)+'\n').encode()
        path=output/f"{g['id']}.zip"
        with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
            for name,raw in sorted(payloads.items()):
                info=zipfile.ZipInfo(name,(2020,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,raw)
        result.append({'group':g['id'],'packages':len(packages),'file':path.name})
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');p.add_argument('--bundle',action='store_true');args=p.parse_args()
    print(json.dumps({'pages':write_pages(check=args.check),'collections':collections() if args.bundle else []}))
