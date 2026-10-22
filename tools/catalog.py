"""Expose task entrypoints while retaining complete implementation modules."""
import json
from pathlib import Path
import re


def entries(root):
    root = Path(root)
    path = root / 'config/skill-catalog.json'
    modules = {p.name for p in (root / 'skills').iterdir() if (p / 'SKILL.md').is_file()}
    if not path.exists():
        return {name: {'source': name, 'pack': 'core', 'modes': {}}
                for name in sorted(modules)}
    record = json.loads(path.read_text())
    if record.get('format') != 1 or not isinstance(record.get('entries'), dict):
        raise ValueError('Unsupported skill catalog')
    result = record['entries']
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
