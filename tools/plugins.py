#!/usr/bin/env python3
"""Generate private Claude and Codex candidates from the canonical skill build."""
import argparse
import json
from pathlib import Path
import posixpath
import re
import shutil
import tempfile
import zipfile

import estate
from catalog import entries as catalog_entries, retired_entries
from portable import assemble, runtime_closure

BUNDLES = {f'estate-{name}' for name in
           ('pursuit', 'solutioning', 'commercial', 'delivery', 'quality', 'governance', 'product', 'writing',
            'personal')}
OPT_IN = 'estate-personal'  # the only bundle a user installs by choice; it has no router


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate configuration key: ' + key)
        result[key] = value
    return result


def config(root):
    value = json.loads((root / 'config/plugin-bundles.json').read_text(), object_pairs_hook=strict_object)
    if value.get('format') != 1 or set(value.get('bundles', {})) != BUNDLES:
        raise ValueError('Declare the eight domain bundles and estate-personal')
    if not re.fullmatch(r'\d+\.\d+\.\d+', value.get('version', '')):
        raise ValueError('Plugin version must be major.minor.patch')
    public = catalog_entries(root)
    catalog = json.loads((root / 'config/skill-catalog.json').read_text())
    owners, internal_owners, routers = {}, {}, {}
    for bundle, item in value['bundles'].items():
        if not isinstance(item.get('description'), str) or not item['description'].strip():
            raise ValueError('Bundle needs a description: ' + bundle)
        if item.get('opt_in') != (bundle == OPT_IN):
            raise ValueError('Only the personal bundle must be opt-in')
        for key, known, claimed in [('entries', public, owners), ('internal', catalog['internal'], internal_owners)]:
            for name in item.get(key, []):
                if name not in known:
                    raise ValueError(f'Unknown {key} classification: {name}')
                if name in claimed:
                    raise ValueError(f'Duplicate bundle owner: {name}')
                claimed[name] = bundle
        router = item.get('router_source')
        if not router:
            if bundle != OPT_IN:
                raise ValueError('Missing domain router: ' + bundle)
            continue
        path = Path(router)
        if path.is_absolute() or '..' in path.parts or path.parts[:1] != ('agents',):
            raise ValueError('Router source must remain in agents/')
        if not (root / path).is_file() or (root / path).is_symlink():
            raise ValueError('Missing or linked router source: ' + router)
        name = path.stem
        if name in routers:
            raise ValueError('Duplicate router owner: ' + name)
        routers[name] = bundle
        for module in router_modules(root, item):
            if module not in estate.names(root):
                raise ValueError('Router points to absent workflow: ' + module)
            runtime_closure(root, module)
    if set(owners) != set(public) or set(internal_owners) != set(catalog['internal']):
        raise ValueError('Missing bundle classification')
    expected_routers = {p.stem for p in (root / 'agents').glob('*-router.md')}
    if set(routers) != expected_routers:
        raise ValueError('Router coverage differs from source')
    release = value.get('release', {})
    if set(release.get('modules', {})) != set(estate.names(root)) or set(release.get('routers', {})) != expected_routers:
        raise ValueError('Every workflow and router needs a release disposition')
    for row in [release.get('shared', {}), *release['modules'].values(), *release['routers'].values()]:
        if row.get('status') not in ('pending', 'accepted'):
            raise ValueError('Release status must be pending or accepted')
    return value


def router_modules(root, item):
    """The existing router is the authoring source for its historical selection."""
    if not item.get('router_source'):
        return []
    text = (root / item['router_source']).read_text()
    if '## Available skills\n' not in text:
        raise ValueError('Router has no skill selection section')
    selection = text.split('## Available skills\n', 1)[1].split('\n## ', 1)[0]
    modules = re.findall(r'^- `([a-z0-9-]+)`\s*$', selection, re.M)
    if not modules:
        raise ValueError('Router has no workflow selection')
    selected = list(dict.fromkeys(modules + item.get('additional_routes', []) + item.get('controls', [])))
    # Embedded modes still route to their owning task entrypoint. Retired
    # diagnostics have no selectable mode and must never be router choices.
    retired = {name for name, rule in retired_entries(root).items()
               if not rule.get('allowed_as_mode')} & set(selected)
    if retired:
        raise ValueError('Router selects retired standalone skill: ' + ', '.join(sorted(retired)))
    return selected


# Files that never reach a package or decide what a package contains: reader
# guides, browse grouping, the version receipt, and local test and verification
# tooling. Editing them must not reopen review of the shared assembly.
# tests/test_release_review.py checks that no assembly module reads them.
SHARED_EXCLUDED = frozenset({
    'config/plugin-bundles.json',          # hashed above without its release block
    'config/plugin-version-history.json',  # a receipt, like the release block
    'config/skill-guide.json',
    'config/skill-groups.json',
    'tools/browse.py',
    'tools/run_preserved_test.py',
    'tools/run_tests.py',
    'tools/skill_guide.py',
    'tools/test_capabilities.py',
    'tools/upstream_drift.py',
    'tools/verify.py',
    'tools/release_review.py',
})


def shared_hash(root, settings):
    # Release receipts do not hash themselves. Membership and routing still do.
    inputs = {key: value for key, value in settings.items() if key != 'release'}
    records = [('bundle-inputs', estate.sha(json.dumps(inputs, sort_keys=True).encode()))]
    for directory in ('policies', 'tools', 'config'):
        for file in estate.files(root / directory):
            if file.relative_to(root).as_posix() in SHARED_EXCLUDED or '__pycache__' in file.parts:
                continue
            records.append((str(file.relative_to(root)), estate.sha(file.read_bytes())))
    for name in estate.DEPENDENCY_INPUTS:
        file = root / name
        if file.exists():
            records.append((name, estate.sha(file.read_bytes())))
    return estate.sha(json.dumps(records, sort_keys=True).encode())


def required_modules(root, item, manifest):
    required = set(item['internal']) | set(router_modules(root, item))
    for name in item['entries']:
        package = manifest['packages'][name]
        required.add(package['source_module'])
        required.update(package['runtime_dependencies'])
    for module in list(required):
        required.update(runtime_closure(root, module))
    return sorted(required)


def release_gaps(root, settings, selected, manifest, entrypoints=None):
    gaps = []
    release = settings['release']
    checks = [('shared assembly', release['shared'], shared_hash(root, settings))]
    required = set()
    if entrypoints is not None:
        required.update(required_modules(root, {'entries': entrypoints, 'internal': []}, manifest))
    for name in selected if entrypoints is None else []:
        item = settings['bundles'][name]
        required.update(required_modules(root, item, manifest))
        if item.get('router_source'):
            path = root / item['router_source']
            checks.append((path.stem, release['routers'][path.stem], estate.sha(path.read_bytes())))
    for module in sorted(required):
        checks.append((module, release['modules'][module], estate.tree_hash(root / 'skills' / module)))
    for label, review, digest in checks:
        if review.get('status') != 'accepted' or review.get('reviewed_sha256') != digest or not review.get('evidence'):
            gaps.append({'subject': label, 'required_sha256': digest, 'status': 'review required'})
    return gaps


def router_text(root, item, targets, host):
    text = (root / item['router_source']).read_text()
    front = re.match(r'\A---\n(.*?)\n---\n', text, re.S)
    if not front:
        raise ValueError('Router frontmatter is missing')
    name = Path(item['router_source']).stem
    description = re.search(r'^description:\s*(.+)$', front[1], re.M)
    if not description:
        raise ValueError('Router description is missing')
    body = text[front.end():].split('## Available skills\n', 1)[0].rstrip()
    # Preserve the source's routing method and replace its list and control paths.
    base = Path('agents') if host == 'claude' else Path('skills') / name
    links = []
    for module in router_modules(root, item):
        target = posixpath.relpath(targets[module], str(base))
        links.append(f'- [{module}]({target})')
    body += '\n\n## Available workflows\n\n' + '\n'.join(links) + '\n'
    controls = item.get('controls', [])
    if controls:
        body += ('\n## Required controls\n\n'
                 'Read the bundled knowledge-hub workflow for configured durable records, '
                 'evidence-core for source and claim checks, and quality-gate for artifact completion. '
                 'Use the links above; these resources are included in this plugin.\n')
    body += '\nSelect the smallest workflow that fits the request, then read its complete instructions and required references.\n'
    return f'---\nname: {name}\ndescription: {description[1]}\n---\n' + body


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def build_plugins(root=estate.ROOT, selected=None, candidate=False, owner=False):
    root = Path(root)
    settings = config(root)
    selected = sorted(set(selected or settings['bundles']))
    if set(selected) - set(settings['bundles']):
        raise ValueError('Unknown selected bundle')
    from plugin_version import check as check_version
    check_version(root, settings)
    manifest = estate.build(root)
    gaps = release_gaps(root, settings, selected, manifest)
    if gaps and not (candidate or owner):
        raise ValueError('Release blocked: ' + ', '.join(x['subject'] for x in gaps))
    # The owner publishes their own marketplace from main; gaps are recorded, not enforced.
    state = 'reviewed' if not gaps else 'owner-published' if owner else 'candidate-unreviewed'
    stage = Path(tempfile.mkdtemp(prefix='plugin-build-', dir=root / '.local'))
    destination = root / 'dist/plugins'
    outputs = {}
    try:
        for host in ('claude', 'codex'):
            host_root = stage / host
            marketplace = []
            for name in selected:
                item = settings['bundles'][name]
                package = host_root / 'plugins' / name
                package.mkdir(parents=True)
                # Preserve the pinned environment inputs without running an installer.
                for dependency in estate.DEPENDENCY_INPUTS:
                    source = root / dependency
                    if source.is_file():
                        shutil.copy2(source, package / dependency)
                targets = {}
                for entry in item['entries']:
                    source = root / 'build/skills' / entry
                    target = package / 'skills' / entry
                    shutil.copytree(source, target)
                    record = manifest['packages'][entry]
                    targets[record['source_module']] = f'skills/{entry}/SKILL.md'
                    for module in record.get('modes', {}).values():
                        targets[module] = f'skills/{entry}/_runtime/{module}/WORKFLOW.md'
                for module in sorted(set(item['internal']) | set(router_modules(root, item))):
                    if module in targets:
                        continue
                    target = package / 'runtime' / module
                    assemble(root, module, target, runtime_closure(root, module), entrypoint_name='WORKFLOW.md')
                    targets[module] = f'runtime/{module}/WORKFLOW.md'
                if item.get('router_source'):
                    router = Path(item['router_source']).stem
                    target = package / ('agents/' + router + '.md' if host == 'claude' else 'skills/' + router + '/SKILL.md')
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(router_text(root, item, targets, host))
                description = item['description']
                if gaps and not owner:
                    description = 'Unreviewed candidate for isolated testing. ' + description
                portable = {'$schema': 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json',
                            'name': name, 'version': settings['version'], 'description': description,
                            'author': {'name': 'Skills Estate'}}
                write_json(package / 'plugin.json', portable)
                write_json(package / '.claude-plugin/plugin.json', {k: v for k, v in portable.items() if k != '$schema'})
                write_json(package / '.codex-plugin/plugin.json', {'name': name, 'version': settings['version'],
                           'description': description, 'skills': './skills/'})
                receipt = {'status': state, 'host_adapter': host, 'source_sha256': manifest['source_sha256'],
                           'entries': item['entries'], 'required_modules': required_modules(root, item, manifest),
                           'opt_in': item['opt_in'], 'review_gaps': gaps}
                write_json(package / 'estate-release.json', receipt)
                # Verify every generated router link against the actual candidate.
                if item.get('router_source'):
                    for link in re.findall(r'\]\(([^)]+)\)', target.read_text()):
                        resolved = (target.parent / link).resolve()
                        if not resolved.is_relative_to(package.resolve()) or not resolved.is_file():
                            raise ValueError('Router target is missing or escapes plugin: ' + link)
                digest = estate.tree_hash(package)
                archive = host_root / (name + '.zip')
                with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as output:
                    for file in estate.files(package):
                        info = zipfile.ZipInfo(str(file.relative_to(package)), date_time=(2020, 1, 1, 0, 0, 0))
                        info.external_attr = (0o100000 | (file.stat().st_mode & 0o777)) << 16
                        output.writestr(info, file.read_bytes(), compress_type=zipfile.ZIP_DEFLATED)
                outputs[f'{host}/{name}'] = {'tree_sha256': digest, 'zip_sha256': estate.sha(archive.read_bytes())}
                marketplace.append({'name': name, 'source': './plugins/' + name} if host == 'claude' else
                                   {'name': name, 'source': {'source': 'local', 'path': './plugins/' + name},
                                    'policy': {'installation': 'AVAILABLE', 'authentication': 'ON_INSTALL'}, 'category': 'Productivity'})
            market = {'name': settings['marketplace'], 'plugins': marketplace}
            if host == 'claude':
                market['owner'] = {'name': 'Skills Estate'}
            write_json(host_root / ('.claude-plugin/marketplace.json' if host == 'claude' else '.agents/plugins/marketplace.json'), market)
        if estate.source_hash(root) != manifest['source_sha256']:
            raise ValueError('Source changed during plugin build')
        result = {'status': state, 'source_sha256': manifest['source_sha256'], 'selected': selected,
                  'packages': outputs, 'review_gaps': gaps,
                  'states': {'built': True, 'source_reviewed': not gaps, 'host_verified': False,
                             'installed': False, 'published': False}}
        write_json(stage / 'release.json', result)
        destination.parent.mkdir(exist_ok=True)
        previous = root / '.local/previous-plugin-build'
        if previous.exists():
            raise ValueError('Previous plugin build needs recovery before replacing it')
        if destination.exists():
            destination.rename(previous)
        try:
            stage.rename(destination)
        except BaseException:
            if previous.exists():
                previous.rename(destination)
            raise
        if previous.exists():
            shutil.rmtree(previous)
        return result
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def root_marketplace(root):
    """The marketplace file on main. Claude Code and Cowork read it from the default branch.
    Each plugin is a folder under plugins/ on main, which CI regenerates from every push."""
    settings = config(root)
    plugins = [{'name': name, 'description': item['description'], 'source': './plugins/' + name}
               for name, item in sorted(settings['bundles'].items())]
    return {'name': 'skills-estate', 'owner': {'name': 'Megan Shellman'},
            'metadata': {'description': "Megan's Skills Estate skills, published from main."}, 'plugins': plugins}


def write_root_marketplace(root=estate.ROOT, check=False):
    path = Path(root) / '.claude-plugin/marketplace.json'
    text = json.dumps(root_marketplace(root), indent=2) + '\n'
    if path.exists() and path.read_text() == text:
        return []
    if check:
        raise ValueError('Regenerate .claude-plugin/marketplace.json with tools/plugins.py --root-marketplace')
    path.parent.mkdir(exist_ok=True)
    path.write_text(text)
    return [str(path.relative_to(root))]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', action='append')
    parser.add_argument('--candidate', action='store_true', help='Build unreviewed candidates for isolated verification only')
    parser.add_argument('--owner', action='store_true', help="Build the owner's marketplace from main; review gaps are recorded, not enforced")
    parser.add_argument('--root-marketplace', action='store_true', help='Write the marketplace file that lives on main')
    args = parser.parse_args()
    if args.root_marketplace:
        print(json.dumps({'written': write_root_marketplace()}))
        return
    with estate.lock():
        result = build_plugins(selected=args.bundle, candidate=args.candidate, owner=args.owner)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
