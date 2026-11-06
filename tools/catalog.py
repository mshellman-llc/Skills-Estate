"""Expose task entrypoints while retaining complete implementation modules."""
import json
from pathlib import Path
import re


def retired_entries(root):
    path = Path(root) / 'config/retired-entrypoints.json'
    if not path.exists():
        return {}
    record = json.loads(path.read_text())
    if record.get('format') != 1 or not isinstance(record.get('entries'), dict):
        raise ValueError('Unsupported retirement policy')
    return record['entries']


def check_retirements(root, record):
    for name, rule in retired_entries(root).items():
        public = record['entries']
        runtime = rule['retained_runtime']
        if rule.get('allowed_as_mode'):
            if name in public or any(item['source'] == runtime for item in public.values()):
                raise ValueError('Retired workflow cannot become a public entrypoint: ' + name)
            owners = {key for key, item in public.items() if runtime in item.get('modes', {}).values()}
            if owners != {rule['successor']}:
                raise ValueError('Retired mode must remain in its recorded successor: ' + name)
            continue
        if name in public or any(item['source'] == runtime or runtime in item.get('modes', {}).values()
                                 for item in public.values()):
            raise ValueError('Retired workflow cannot become a public entrypoint or mode: ' + name)
        if rule['successor'] not in public or runtime not in record.get('internal', []):
            raise ValueError('Retirement must preserve its successor and internal runtime: ' + name)
        for router in (Path(root) / 'agents').glob('*-router.md'):
            if re.search(r'^- `' + re.escape(name) + r'`\s*$', router.read_text(), re.M):
                raise ValueError('Router selects retired standalone skill: ' + str(router))


def excluded_sources(root):
    path = Path(root) / 'config/retired-entrypoints.json'
    return set(json.loads(path.read_text()).get('excluded_sources', [])) if path.exists() else set()


def check_public_names(root, names):
    forbidden = set(retired_entries(root)) | excluded_sources(root)
    if forbidden.intersection(names):
        raise ValueError('Retired or excluded entrypoint: ' + ', '.join(sorted(forbidden.intersection(names))))


def source_names(root):
    return {p.parent.name for p in Path(root).glob('skills/*/SKILL.md')} - excluded_sources(root)


def entries(root):
    root = Path(root)
    path = root / 'config/skill-catalog.json'
    modules = source_names(root)
    if not path.exists():
        if retired_entries(root):
            raise ValueError('A retirement policy requires an explicit skill catalog')
        return {name: {'source': name, 'pack': 'core', 'modes': {}}
                for name in sorted(modules)}
    record = json.loads(path.read_text())
    if record.get('format') != 1 or not isinstance(record.get('entries'), dict):
        raise ValueError('Unsupported skill catalog')
    check_retirements(root, record)
    if excluded_sources(root) & set(record.get('internal', [])):
        raise ValueError('Excluded source in catalog internal selection')
    result = record['entries']
    check_public_names(root, result)
    owners = {}

    def claim(module, owner):
        if module in owners:
            raise ValueError(f'Duplicate catalog owner for {module}: {owners[module]} and {owner}')
        owners[module] = owner

    for module in record.get('internal', []):
        claim(module, 'internal')
    for name, item in result.items():
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name):
            raise ValueError('Invalid public skill name: ' + name)
        if ({item['source']} | set(item.get('modes', {}).values())) & excluded_sources(root):
            raise ValueError('Excluded source in public workflow or mode')
        if item['source'] not in modules:
            raise ValueError('Missing primary workflow: ' + item['source'])
        claim(item['source'], name + ' primary')
        for mode, module in item.get('modes', {}).items():
            if not mode.strip() or module not in modules:
                raise ValueError('Missing mode workflow: ' + str(module))
            claim(module, name + ' mode ' + mode)
    used = set(owners)
    if used != modules:
        raise ValueError('Catalog module coverage differs: ' + ', '.join(sorted(used ^ modules)))
    return dict(sorted(result.items()))


def dependencies(root, item, closure):
    source = item['source']
    result = set(closure(root, source))
    for module in item.get('modes', {}).values():
        if module != source:
            result.add(module)
            result.update(closure(root, module))
    result.discard(source)
    if ({source} | result) & excluded_sources(root):
        raise ValueError('Excluded source in dependency closure')
    return sorted(result)


def apply_entrypoint(package, name, item):
    """Keep the full primary workflow and attach complete mode workflows."""
    package = Path(package)
    file = package / 'SKILL.md'
    body = file.read_text()
    body = re.sub(r'(?m)^name:.*$', 'name: ' + name, body, count=1)
    if item.get('description'):
        body = re.sub(r'(?m)^description:.*$',
                      lambda _: 'description: ' + json.dumps(item['description'], ensure_ascii=False),
                      body, count=1)
    routes = []
    for mode, module in item.get('modes', {}).items():
        path = '_runtime/' + module + '/WORKFLOW.md'
        if not (package / path).is_file():
            raise ValueError('Mode workflow absent from package: ' + path)
        routes.append('| ' + mode + ' | [' + module + '](' + path + ') |')
    if routes:
        end = re.match(r'\A---\n.*?\n---\n', body, re.S).end()
        routing = ('\n## Choose the requested task\n\n'
                   'Use the primary workflow below unless the request matches a mode in this table. '
                   'For a matching mode, read its complete linked workflow and required references, '
                   'then produce that mode\'s output. Preserve its calculations, failure handling and '
                   'acceptance checks. One request does not require every mode.\n\n'
                   '| Requested mode | Complete workflow |\n| --- | --- |\n' + '\n'.join(routes) + '\n\n')
        body = body[:end] + routing + body[end:]
    file.write_text(body)
    # Host-specific display metadata must not retain the retired entrypoint.
    metadata = package / 'agents/openai.yaml'
    if metadata.exists():
        text = metadata.read_text().replace(item['source'], name)
        metadata.write_text(text)
