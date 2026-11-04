"""Locate the kit and its sibling runtimes in a source checkout or a built package.

Source checkout: <repo>/skills/review-site-kit, siblings under <repo>/skills.
Built package:   <package>/_runtime/review-site-kit, siblings under <package>/_runtime.
"""
from pathlib import Path

KIT = Path(__file__).resolve().parents[2]
SIBLINGS = KIT.parent


def sibling(name):
    path = SIBLINGS / name
    return path if path.is_dir() else None


def writing_checker():
    for name in ('prose-pass', 'writing-integrity'):
        base = sibling(name)
        if base:
            for candidate in (base / 'scripts/writing_check.py',
                              base / '_runtime/prose-pass/scripts/writing_check.py'):
                if candidate.is_file():
                    return candidate
    return None


def launch_policy():
    base = sibling('brand-renderer')
    candidate = base / 'scripts/browser_launch_policy.cjs' if base else None
    return candidate if candidate and candidate.is_file() else None


def brand_policy():
    """The estate brand policy: generated into packages, authored at the repository root."""
    for candidate in (SIBLINGS.parent / 'references/estate/brand.md',
                      SIBLINGS.parent / 'policies/brand.md',
                      KIT / 'references/estate/brand.md'):
        if candidate.is_file():
            return candidate
    return None


def schema(name):
    return KIT / 'schema' / f'{name}.schema.json'


def assets():
    return KIT / 'assets/site'
