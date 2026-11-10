#!/usr/bin/env python3
"""Package the local owner kit and selected static websites without a framework."""
import argparse
import json
from pathlib import Path
import shutil
import tempfile
import zipfile

import publication

HERE = Path(__file__).resolve().parent
OWNER_FILES = ('index.html', 'index.json', 'viewer.py', 'owner.py', 'publication.py',
               'rendering.py', 'template.html', 'explorer.css', 'workflows.json',
               'manage.html', 'open-map.command', 'README.md', 'INTEGRATION.md')


def archive(folder, destination):
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as output:
        for path in sorted(folder.rglob('*')):
            if path.is_file():output.write(path, path.relative_to(folder).as_posix())


def package(output, settings=publication.CONFIG, packages=None):
    output = Path(output);output.mkdir(parents=True, exist_ok=True)
    settings = publication.load(settings)
    data = json.loads((HERE / 'index.json').read_text())
    with tempfile.TemporaryDirectory() as scratch:
        root = Path(scratch);owner = root / 'owner';owner.mkdir()
        for name in OWNER_FILES:shutil.copy2(HERE / name, owner / name)
        shutil.copytree(HERE / 'assets', owner / 'assets')
        (owner / 'visibility.json').write_text(json.dumps(settings, indent=2) + '\n')
        reports = {}
        for target in publication.TARGETS:
            public = root / target
            manifest, omitted = publication.export(data, settings, target, public, packages)
            archive(public, output / ('skills-estate-' + target + '.zip'))
            reports[target] = {**manifest, 'blockedWorkflows': omitted}
            # Owner previews can reuse the exact-source task packages offline.
            if target == 'estate' and (public / 'downloads').is_dir():
                shutil.copytree(public / 'downloads', owner / 'downloads')
        archive(owner, output / 'skills-estate-owner.zip')
        (output / 'portable-manifest.json').write_text(json.dumps(reports, indent=2) + '\n')
    return {'output': str(output), 'sourceCommit': data['baseCommit'],
            'archives': ['skills-estate-owner.zip', 'skills-estate-estate.zip', 'skills-estate-portfolio.zip']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--settings', type=Path, default=publication.CONFIG)
    parser.add_argument('--packages', type=Path)
    args = parser.parse_args()
    print(json.dumps(package(args.output, args.settings, args.packages)))
