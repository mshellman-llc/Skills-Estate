"""Build the reader guide and a bounded, source-based reuse assessment."""
import hashlib
import json
from pathlib import Path
import re

PERSONAL = re.compile(r"\bMegan\b|meganshellman|mshellman|BeastMode|JobHunt|GoGuardian|NeuraFlash|/Volumes/(?:BeastMode|Stickers|Meridian)", re.I)
PERSONAL_SKILLS = set('beastmode-capture beastmode-context beastmode-health beastmode-reconcile brain-work-item career-application career-materials-and-outreach career-progression-and-offers case-study-builder fortunes-weave github-repository-work independent-product megan-writing-style resume-numbers-and-keywords sticker-sheets'.split())
LOCAL_CLEANUP = {
    'discovery-synthesis': 'Replace the instruction that assigns follow-ups to Megan or her team with the actual project owner.',
    'sales-process-mapping': 'Move the conditional Megan writing-profile route into personal configuration.',
    'sales-journey-critique': 'Move the conditional Megan writing-profile and scanner settings into personal configuration.',
}
SETUP = {
    **{n: 'Requires the project’s Salesforce configuration and the documented CLI or connector. Live actions require the intended org and authorization.' for n in 'dx-devops-promote dx-devops-work-item-manage org-preflight sf-delivery-standards sf-deploy-engine sf-enterprise-patterns sf-headless-screenshot sf-solo-devops'.split()},
    'skill-estate-sync': 'Requires an existing Skills Estate checkout, its configured repository pointer, and supported local install paths.',
    'cross-platform-skill-release': 'Requires the destination hosts and their current supported installation or upload method.',
    'personal-writing-style-runtime': 'Requires a confirmed profile for the intended author and an installation adapter.',
    'brand-renderer': 'Requires the bundled rendering runtime and the artifact format’s dependencies. Select the project brand or neutral profile.',
    'sow': 'Requires a confirmed quote model, the project’s approved contract profile, and the document runtime.',
    'sf-headless-screenshot': 'Requires sfqa, a supported browser runtime, and an authorized Salesforce connection.',
}

def text_files(folder):
    for p in sorted(folder.rglob('*')):
        if not p.is_file() or any(x.startswith('.') or x == '__pycache__' for x in p.relative_to(folder).parts):
            continue
        try:
            yield p, p.read_text()
        except (UnicodeError, OSError):
            continue

def scan(root, folder):
    findings, count = [], 0
    for path, text in text_files(folder):
        count += 1
        rel = path.relative_to(root).as_posix()
        example = any(x in path.parts for x in ('fixtures', 'examples')) or 'selftest' in path.name or path.name.startswith('test_')
        for line, value in enumerate(text.splitlines(), 1):
            if PERSONAL.search(value):
                findings.append({'path': rel, 'line': line, 'text': value.strip(),
                                 'kind': 'example-or-test' if example else 'workflow-or-reference'})
    return findings, count

def load(root):
    return json.loads((root / 'config/skill-guide.json').read_text())['skills']

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
    rows = []
    for name, guide in sorted(guides.items()):
        a = assessment(root, name, guide, [])
        links = sorted({f'[{h["path"]}:{h["line"]}](../{h["path"]}#L{h["line"]})' for h in a['references'] if h['kind'] != 'example-or-test'})
        rows.append(f'| `{name}` | {a["label"]} | {a["setup"] or "Supply the task inputs and its supported runtime."} | {"; ".join(links) or "No named personal reference detected in workflow text."} |')
    general = sum(n not in PERSONAL_SKILLS for n in guides)
    lines = ['# Skill reuse review', '', f'{general} general-use methods and {len(guides)-general} Megan-specific workflows.', '',
             'Audience describes the intended user. It does not certify execution in every environment. This review combines workflow classification with an automated scan of UTF-8 source files, supporting resources, declared runtime dependencies, and shared policies. Binary assets and private sources outside this repository were not inspected.', '',
             'Every assembled task package receives the shared policies. `policies/workflow.md` names Megan; generalize that wording before distributing general-use packages. This shared cleanup applies even when a workflow has no personal references of its own.', '',
             'The discovery-synthesis entrypoint assigns follow-ups to Megan or her team. Sales process mapping and sales journey critique include conditional Megan voice routes. Writing-integrity uses Megan as an optional author-profile example; its main workflow resolves an explicitly configured owner. Fixture names and selftest checks are listed separately in the map and do not make a method personal.', '',
             'Megan-specific workflows retain their current sources and permissions. Generalizing those methods requires replacing personal records, decisions, paths, identity, and permissions; deleting a name alone would be insufficient.', '',
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

def overview_excerpt(body):
    body = re.sub(r'<!--\s*ESTATE-WRITING:BEGIN\s*-->.*?<!--\s*ESTATE-WRITING:END\s*-->', '', body, flags=re.S)
    paragraphs = re.split(r'\n\s*\n', re.sub(r'^#\s+.+\n', '', body, count=1).strip())
    return [p for p in paragraphs if not re.match(r'^(Read \[shared workflow\]|#{1,6} |```|\||>\s*\*\*Before writing:|<!--)', p)][:3]
