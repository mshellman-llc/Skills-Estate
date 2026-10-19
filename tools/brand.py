#!/usr/bin/env python3
"""Read a brand profile's JSON block and emit CSS variables."""
import argparse
import json
from pathlib import Path
import re


def load_profile(path):
    text = Path(path).read_text()
    blocks = re.findall(r'```json\s*\n(.*?)\n```', text, re.S)
    if len(blocks) != 1:
        raise ValueError('A profile needs exactly one JSON block')
    profile = json.loads(blocks[0])
    if profile.get('status') != 'confirmed':
        raise ValueError('This renderer requires a confirmed profile')
    if not profile.get('name') or not profile.get('source'):
        raise ValueError('A profile needs a name and source')
    colors = profile.get('colors', {})
    for role in ('background', 'text', 'muted', 'border', 'surface', 'accent'):
        if not re.fullmatch(r'#[0-9a-fA-F]{6}', colors.get(role, '')):
            raise ValueError(f'Missing or invalid color: {role}')
    for role, value in colors.items():
        if not re.fullmatch(r'[a-z][a-z0-9-]*', role) or not re.fullmatch(r'#[0-9a-fA-F]{6}', value):
            raise ValueError(f'Invalid color token: {role}')
    for role in ('body', 'headings'):
        if not re.fullmatch(r'[a-zA-Z0-9 ,"\'-]+', profile.get('type', {}).get(role, '')):
            raise ValueError(f'Invalid font stack: {role}')
    return profile


def css(profile):
    values = [f'  --brand-{role}: {value};' for role, value in profile['colors'].items()]
    values += [f'  --brand-font-{role}: {profile["type"][role]};' for role in ('body', 'headings')]
    return ':root {\n' + '\n'.join(values) + '\n}\n'


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('profile', type=Path)
    args = ap.parse_args()
    try:
        print(css(load_profile(args.profile)), end='')
    except (ValueError, KeyError, OSError) as exc:
        ap.exit(2, str(exc) + '\n')
