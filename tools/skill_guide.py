"""Build the reader guide and a bounded, source-based reuse assessment."""
import hashlib
import json
from pathlib import Path
import re
from catalog import excluded_sources

PERSONAL = re.compile(r"\bMegan\b|meganshellman|mshellman|BeastMode|JobHunt|GoGuardian|NeuraFlash|/Volumes/(?:BeastMode|Stickers|Meridian)", re.I)
PERSONAL_SKILLS = set()  # Personal context is supplied separately from functional workflows.
LOCAL_CLEANUP = {}
SETUP = {
    **{n: 'Requires the project’s Salesforce configuration and the documented CLI or connector. Live actions require the intended org and authorization.' for n in 'dx-devops-promote dx-devops-work-item-manage org-preflight sf-delivery-standards sf-deploy-engine sf-enterprise-patterns sf-headless-screenshot sf-solo-devops'.split()},
    'skill-estate-sync': 'Requires an existing Skills Estate checkout, its configured repository pointer, and supported local install paths.',
    'cross-platform-skill-release': 'Requires the destination hosts and their current supported installation or upload method.',
    'personal-writing-style-runtime': 'Requires a confirmed profile for the intended author and an installation adapter.',
    'brand-renderer': 'Requires the bundled rendering runtime and the artifact format’s dependencies. Select the project brand or neutral profile.',
    'sow': 'Requires a confirmed quote model, the project’s approved contract profile, and the document runtime.',
    'sf-headless-screenshot': 'Requires sfqa, a supported browser runtime, and an authorized Salesforce connection.',
    'playbook-suite': 'Requires the caller’s approved specification, manifest and qualifier schemas, and stage-gate workbook. Bundled checks cover the preserved 1.1 compatibility model; they do not certify those external inputs or rendered outputs.',
    'playbook-fit-router': 'Requires caller-supplied qualifier data and its approved schema. The router checks minimum fields; schema and policy conformance need separate evidence.',
}

def text_files(folder):
    for p in sorted(folder.rglob('*')):
        if not p.is_file() or any(x.startswith('.') or x == '__pycache__' for x in p.relative_to(folder).parts):
            continue
        try:
            yield p, p.read_text()
        except (UnicodeError, OSError):
            continue

def skill_names(root):
    # A skill's own identifier (for example `/beastmode-context`) is how it is invoked, not a personal reference.
    names = sorted((p.name for p in (root / 'skills').iterdir() if p.is_dir() and PERSONAL.search(p.name)), key=len, reverse=True)
    return re.compile(r'(?<![\w-])(?:' + '|'.join(map(re.escape, names)) + r')(?![\w-])', re.I) if names else None

def scan(root, folder):
    findings, count = [], 0
    names = skill_names(root)
    for path, text in text_files(folder):
        count += 1
        rel = path.relative_to(root).as_posix()
        example = any(x in path.parts for x in ('fixtures', 'examples')) or 'selftest' in path.name or path.name.startswith('test_')
        for line, value in enumerate(text.splitlines(), 1):
            if PERSONAL.search(names.sub('', value) if names else value):
                findings.append({'path': rel, 'line': line, 'text': value.strip(),
                                 'kind': 'example-or-test' if example else 'workflow-or-reference'})
    return findings, count

def load(root):
    return {name: guide for name, guide in json.loads((root / 'config/skill-guide.json').read_text())['skills'].items()
            if name not in excluded_sources(root)}

def assessment(root, name, guide, resources):
    own, count = scan(root, root / 'skills' / name)
    dependencies = json.loads((root / 'config/runtime-dependencies.json').read_text())
    visited, inherited = set(), []
    def visit(n):
        if n in visited: return
        visited.add(n)
        for dep in dependencies.get(n, []):
            hits, _ = scan(root, root / 'skills' / dep)
            inherited.extend({**h, 'via': dep} for h in hits)
            visit(dep)
    visit(name)
    shared, _ = scan(root, root / 'policies')
    for item in shared: item['kind'] = 'shared-policy'
    review_current = guide.get('reviewedEntrypointSha256') == hashlib.sha256((root/'skills'/name/'SKILL.md').read_bytes()).hexdigest()
    audience = ('megan' if name in PERSONAL_SKILLS else 'general') if review_current else 'review'
    substantive = [h for h in own + inherited if h['kind'] != 'example-or-test']
    reason = ('The entrypoint changed after its intended audience was reviewed. Reassess the current source before sharing.' if not review_current else guide.get('reuseNote') or ('The workflow uses Megan’s personal sources, account, decisions, or project system.' if audience == 'megan' else 'The method accepts the user’s project sources and does not require Megan’s biography or private records.'))
    cleanup = [LOCAL_CLEANUP[name]] if name in LOCAL_CLEANUP else []
    if audience == 'general' and substantive and name not in LOCAL_CLEANUP and name != 'writing-integrity':
        cleanup.append('Review the named personal references before sharing this workflow.')
    if shared:
        cleanup.append('The bundled shared workflow policy names Megan. Generalize that shared wording before distributing a general-use package.')
    fingerprint = hashlib.sha256(json.dumps([{k: r[k] for k in ('path','sha256')} for r in resources], sort_keys=True).encode()).hexdigest()
    return {'audience': audience, 'label': {'megan':'Megan-specific','general':'General use','review':'Needs review'}[audience],
            'reason': reason, 'setup': SETUP.get(name, ''), 'cleanup': cleanup,
            'readiness': 'review' if not review_current else 'personal' if audience == 'megan' else 'cleanup' if cleanup else 'setup' if name in SETUP else 'reusable',
            'references': own, 'dependencyReferences': inherited, 'sharedReferences': shared,
            'textFilesScanned': count, 'packageFingerprint': fingerprint,
            'basis': 'Source classification and automated reference scan; cross-environment execution has not been tested.'}

def report(root):
    guides = load(root)
    rows = []; counts={'general':0,'megan':0,'review':0}
    for name, guide in sorted(guides.items()):
        a = assessment(root, name, guide, [])
        counts[a['audience']]+=1
        links = sorted({f'[{h["path"]}:{h["line"]}](../{h["path"]}#L{h["line"]})' for h in a['references'] if h['kind'] != 'example-or-test'})
        rows.append(f'| `{name}` | {a["label"]} | {a["setup"] or "Supply the task inputs and its supported runtime."} | {"; ".join(links) or "No named personal reference detected in workflow text."} |')
    lines = ['# Skill reuse review', '', f"{counts['general']} general-use methods, {counts['megan']} Megan-specific workflows, and {counts['review']} awaiting source review.", '',
             'Audience describes the intended user. It does not certify execution in every environment. This review combines workflow classification with an automated scan of UTF-8 source files, supporting resources, declared runtime dependencies, and shared policies. Binary assets and private sources outside this repository were not inspected.', '',
             'Every assembled task package receives the shared policies. The shared workflow uses project roles and contains no named personal owner.', '',
             'Discovery synthesis and sales mapping use the current project owner and the intended author’s confirmed profile. Writing-integrity resolves an explicitly configured profile owner. Fixture names and selftest checks are listed separately in the map and do not make a method personal.', '',
             'Functional workflows accept explicit task context. Private originals remain outside the portable collection; this guide is not a certificate of host execution.', '',
             '| Workflow | Built for | Setup | Personal references in source |', '| --- | --- | --- | --- |', *rows, '',
             'Refresh this review with `python3 tools/skill_guide.py --report`. The map recomputes reference findings on each build. Reader-guide copy is bound to its reviewed entrypoint hash; a changed entrypoint shows current instructions until the guide is reviewed again.', '']
    return '\n'.join(lines)

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--report', action='store_true')
    p.add_argument('--check', action='store_true')
    args = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    target = root / 'browse/reuse-review.md'
    rendered = report(root)
    if args.check:
        if not target.is_file() or target.read_text() != rendered:
            raise SystemExit('Reuse review is stale; run python3 tools/skill_guide.py --report')
    elif args.report:
        target.write_text(rendered)

def readable_body(body):
    """Keep task instructions readable while retaining the exact source separately."""
    chunks=re.split(r'(?ms)(^```[^\n]*\n.*?^```\s*$)',body)
    title_removed=False
    for i in range(0,len(chunks),2):
        text=re.sub(r'<!--\s*ESTATE-WRITING:BEGIN\s*-->.*?<!--\s*ESTATE-WRITING:END\s*-->','',chunks[i],flags=re.S)
        # Comments outside code are source annotations, never executable HTML.
        text=re.sub(r'<!--.*?-->','',text,flags=re.S)
        if not title_removed and re.search(r'^#\s+.+$',text,re.M):
            text=re.sub(r'^#\s+.+(?:\n|$)','',text,count=1,flags=re.M);title_removed=True
        kept=[]
        for paragraph in re.split(r'\n\s*\n',text):
            p=paragraph.strip()
            if re.match(r'^Read \[shared workflow\]',p):continue
            if ('build-card.md' in p or 'readout-brief.md' in p) and re.match(r'^(?:>\s*)?(?:\*\*)?Before writing',p):continue
            if re.match(r'^>\s*\[?`?readout-brief\.md',p):continue
            if re.match(r'^(?:Before drafting,\s*)?[Rr]ead\b',p):
                end=re.search(r'\.(?=\s|$)',p)
                if end and 'build-card.md' in p[:end.end()]:p=p[end.end():].lstrip()
            if p:kept.append(p)
        chunks[i]='\n\n'.join(kept)
    return '\n\n'.join(c.strip() for c in chunks if c.strip())

def overview_excerpt(body):
    body = readable_body(body)
    paragraphs = re.split(r'\n\s*\n', body.strip())
    return [p for p in paragraphs if not re.match(r'^(Read \[shared workflow\]|#{1,6} |```|\||>\s*\*\*Before writing:|<!--)', p)][:3]
