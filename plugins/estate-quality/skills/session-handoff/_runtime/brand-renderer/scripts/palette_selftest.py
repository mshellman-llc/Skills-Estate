#!/usr/bin/env python3
"""Check that renderer values come from the profile and instructions don't fork it."""
import argparse
from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'brand'))
from brand_profile import load_profile
from tokens import T


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    default_skill = Path(__file__).resolve().parents[1] / 'SKILL.md'
    if not default_skill.exists():
        default_skill = default_skill.with_name('WORKFLOW.md')
    parser.add_argument('--skill', type=Path, default=default_skill)
    args = parser.parse_args()
    text = args.skill.read_text()
    selected = load_profile(T.path)
    expected = {v.upper() for v in selected['colors'].values()}
    observed = {v['hex'].upper() for v in T.colors.values()}
    assert observed == expected, f'Token values differ from selected profile: {observed ^ expected}'
    assert 'references/estate/brand.md' in text, 'Skill must point to the shared policy'
    assert not re.search(r'#[0-9a-fA-F]{6}\b', text), 'Skill must not duplicate palette values'
    assert T.is_authoritative, 'The runtime must read an identified profile'
    print(f'PASS: {len(T.colors)} renderer tokens resolve to {len(expected)} profile colors')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
