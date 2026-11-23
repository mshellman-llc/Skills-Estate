#!/usr/bin/env python3
"""Build the complete MeganOS pages and their matching catalog as one release."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
FILES = ('private.html', 'public.html', 'catalog.json')


def build(output, root=ROOT):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    source = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    source_date = subprocess.check_output(['git', '-C', str(root), 'log', '-1', '--format=%cI'], text=True).strip()
    builder = root / 'artifacts/skills-site/build.py'
    for name, options in [('private.html', ['--page-url', '/skills']),
                          ('public.html', ['--target', 'portfolio', '--page-url', '/work/skills', '--downloads-base', '/work/skills/download'])]:
        subprocess.run([sys.executable, str(builder), '--repo', str(root), '--out', str(output / name), *options], check=True)
    catalog = {
        'index': json.loads((root / 'artifacts/skills-map/index.json').read_text()),
        'workflows': json.loads((root / 'artifacts/skills-map/workflows.json').read_text()),
        'bundles': json.loads((root / 'config/plugin-bundles.json').read_text()),
        'publication': json.loads((root / 'config/skills-publication.json').read_text()),
    }
    # A rebuild of the same commit has the same bytes, including its as-of date.
    keep = {'id', 'title', 'family', 'catalogRole', 'taskPackages', 'profile', 'guide', 'description', 'githubUrl', 'sourcePath', 'sourceSha256'}
    catalog['index']['skills'] = [{**{k: v for k, v in skill.items() if k in keep},
        'examples': [{k: v for k, v in example.items() if k in {'id', 'title', 'source', 'date', 'skillSha256'}} for example in skill.get('examples', [])]}
        for skill in catalog['index']['skills']]
    catalog['index']['generatedAt'] = source_date
    catalog['index']['baseCommit'] = source
    (output / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, separators=(',', ':')) + '\n')
    manifest = {'format': 1, 'sourceCommit': source, 'files': {}}
    for name in FILES:
        data = (output / name).read_bytes()
        manifest['files'][name] = {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
    (output / 'release.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.out)))
