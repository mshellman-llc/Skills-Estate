#!/usr/bin/env python3
"""Validate explorer content and copy a fresh, identity-free static application."""
import argparse
import json
from pathlib import Path
import re
import shutil
import sys
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
COLLECTIONS = ('people', 'modules', 'priorities', 'decisions', 'sources')


def validate(data):
    if not isinstance(data, dict):
        raise ValueError('Content must be a JSON object.')
    meta = data.get('meta')
    if not isinstance(meta, dict):
        raise ValueError('meta must be an object.')
    for key in ('title', 'brand', 'headline', 'intro'):
        if not isinstance(meta.get(key), str) or not meta[key].strip():
            raise ValueError(f'meta.{key} must be a nonempty string.')
    if not isinstance(data.get('paths'), list) or not data['paths']:
        raise ValueError('Provide at least one path.')
    for key in COLLECTIONS:
        data.setdefault(key, [])
        if not isinstance(data[key], list):
            raise ValueError(f'{key} must be an array.')
    ids = {}
    for group in ('paths',) + COLLECTIONS:
        seen = set()
        for item in data[group]:
            if not isinstance(item, dict):
                raise ValueError(f'Each {group} item must be an object.')
            ident = item.get('id')
            if not isinstance(ident, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', ident):
                raise ValueError(f'{group} IDs need safe linking characters.')
            if ident in seen:
                raise ValueError(f'Duplicate {group} ID: {ident}')
            seen.add(ident)
            label = 'name' if group == 'people' else 'title'
            if not isinstance(item.get(label), str) or not item[label].strip():
                raise ValueError(f'{group}/{ident} needs {label}.')
        ids[group] = seen
    for path in data['paths']:
        stages = path.get('stages')
        if not isinstance(stages, list) or not stages:
            raise ValueError(f'Path {path["id"]} needs stages.')
        stage_ids = set()
        for stage in stages:
            if not isinstance(stage, dict):
                raise ValueError('Each stage must be an object.')
            for key in ('id', 'title', 'summary', 'goal', 'action'):
                if not isinstance(stage.get(key), str) or not stage[key].strip():
                    raise ValueError(f'Each stage needs {key}.')
            if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', stage['id']):
                raise ValueError('Stage IDs need safe linking characters.')
            if stage['id'] in stage_ids:
                raise ValueError(f'Duplicate stage in {path["id"]}: {stage["id"]}')
            stage_ids.add(stage['id'])
    def walk(value, location='content'):
        if isinstance(value, dict):
            for key, val in value.items():
                if key in ('sourceIds', 'moduleIds', 'roleIds'):
                    target = {'sourceIds': 'sources', 'moduleIds': 'modules', 'roleIds': 'people'}[key]
                    if not isinstance(val, list) or any(not isinstance(x, str) or x not in ids[target] for x in val):
                        raise ValueError(f'Unresolved or malformed {key} at {location}.')
                if key == 'url' and val:
                    if not isinstance(val, str) or urlparse(val).scheme not in ('https', 'http') or not urlparse(val).netloc:
                        raise ValueError(f'Unsafe source URL at {location}.')
                walk(val, location + '.' + key)
        elif isinstance(value, list):
            for i, item in enumerate(value):
                walk(item, f'{location}[{i}]')
    walk(data)
    return data


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--content', type=Path, required=True)
    ap.add_argument('--output', type=Path)
    ap.add_argument('--validate-only', action='store_true')
    args = ap.parse_args()
    data = validate(json.loads(args.content.read_text(encoding='utf-8')))
    if args.validate_only:
        print(json.dumps({'valid': True, 'paths': len(data['paths']), 'sources': len(data['sources'])}))
        return
    if not args.output:
        ap.error('--output is required unless --validate-only is used')
    out = args.output.expanduser().resolve()
    if out.is_relative_to(ROOT) or ROOT.is_relative_to(out):
        raise ValueError('Create the project outside the installed skill tree.')
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise ValueError('Output must be a new or empty directory. Existing projects are not overwritten.')
    out.mkdir(parents=True, exist_ok=True)
    dist = out / 'dist'
    dist.mkdir()
    for name in ('index.html', 'styles.css', 'app.js', 'icon.svg'):
        shutil.copy2(ROOT / 'assets' / 'site' / name, dist / name)
    (dist / 'data.js').write_text('window.EXPLORER = ' + json.dumps(data, ensure_ascii=False) + ';\n', encoding='utf-8')
    (out / '.openai').mkdir()
    (out / '.openai' / 'hosting.json').write_text(json.dumps({'static': {'directory': 'dist'}}, indent=2) + '\n')
    (out / '.gitignore').write_text('.env\n.env.*\nnode_modules/\n*.tar.gz\n*.zip\n')
    print(json.dumps({'project': str(out), 'static_directory': 'dist', 'project_identity': None, 'paths': len(data['paths'])}))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as exc:
        print(f'Explorer creation failed: {exc}', file=sys.stderr)
        sys.exit(1)
