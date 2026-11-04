"""A small JSON Schema subset validator (standard library only).

Supports type, const, enum, required, properties, items. Enough for the
series' contracts; it reports every error with its JSON path.
"""
import json

from . import paths

TYPES = {'object': dict, 'array': list, 'string': str, 'integer': int,
         'number': (int, float), 'boolean': bool, 'null': type(None)}


def _check(value, schema, where, errors):
    expected = schema.get('type')
    if expected:
        names = expected if isinstance(expected, list) else [expected]
        ok = False
        for name in names:
            kind = TYPES[name]
            if name in ('integer', 'number') and isinstance(value, bool):
                continue
            if isinstance(value, kind):
                ok = True
        if not ok:
            errors.append(f'{where}: expected {"/".join(names)}')
            return
    if 'const' in schema and value != schema['const']:
        errors.append(f'{where}: must equal {schema["const"]!r}')
    if 'enum' in schema and value not in schema['enum']:
        errors.append(f'{where}: {value!r} is not one of {schema["enum"]}')
    if isinstance(value, dict):
        for key in schema.get('required', []):
            if key not in value:
                errors.append(f'{where}: missing "{key}"')
        for key, sub in schema.get('properties', {}).items():
            if key in value:
                _check(value[key], sub, f'{where}.{key}', errors)
    if isinstance(value, list) and 'items' in schema:
        for index, item in enumerate(value):
            _check(item, schema['items'], f'{where}[{index}]', errors)


def errors(value, name):
    schema = json.loads(paths.schema(name).read_text())
    found = []
    _check(value, schema, name, found)
    return found


def require(value, name):
    found = errors(value, name)
    if found:
        raise ValueError('\n'.join(found))
    return value


def load(path, name):
    with open(path, encoding='utf-8') as handle:
        return require(json.load(handle), name)
