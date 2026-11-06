"""Turn a brand profile into the page's CSS custom properties.

The profile format is the estate brand policy's JSON block. With no profile,
the policy's neutral profile applies. Missing roles fall back to the neutral
value and are reported as substitutions.
"""
import html
import json
import re
from pathlib import Path

from . import paths

ROLES = ['background', 'text', 'muted', 'border', 'surface', 'accent',
         'status-good', 'status-warning', 'status-critical']


def _json_block(text):
    match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.S)
    if not match:
        raise ValueError('no JSON profile block found')
    return json.loads(match.group(1))


def neutral():
    policy = paths.brand_policy()
    if not policy:
        raise ValueError('estate brand policy not found; the package is incomplete')
    return _json_block(policy.read_text())


def load(path=None):
    base = neutral()
    if not path:
        return base, Path(), []
    path = Path(path)
    text = path.read_text()
    profile = json.loads(text) if path.suffix == '.json' else _json_block(text)
    if profile.get('status') not in ('confirmed', 'authorized'):
        raise ValueError(f'brand profile {path.name} is {profile.get("status")!r}; '
                         'a draft needs the user\'s authorization for this artifact')
    substitutions = [role for role in ROLES if role not in profile.get('colors', {})]
    colors = {**base['colors'], **profile.get('colors', {})}
    merged = {**base, **profile, 'colors': colors,
              'type': {**base.get('type', {}), **profile.get('type', {})},
              'layout': {**base.get('layout', {}), **(profile.get('layout') or {})}}
    return merged, path.parent, substitutions


def css(profile):
    c, t, layout = profile['colors'], profile.get('type', {}), profile.get('layout') or {}
    radius = layout.get('radius_px', 6)
    lines = [f'--{role}:{c[role]};' for role in ROLES if role in c]
    lines += [f'--font-body:{t.get("body", "system-ui, sans-serif")};',
              f'--font-head:{t.get("headings", t.get("body", "system-ui, sans-serif"))};',
              f'--radius:{radius}px;']
    return ':root{' + ''.join(lines) + '}'


def logo_path(profile, base_dir):
    item = profile.get('logo')
    file = item.get('file') if isinstance(item, dict) else item
    path = Path(base_dir) / str(file)
    if not path.is_file():
        raise ValueError(f'logo file missing: {path}')
    return path


def logo(profile, base_dir):
    """Inline an SVG logo or return an <img> for a raster file; empty when the profile has none.
    The logo is a file path, or an object with `file` and `alt`."""
    item = profile.get('logo')
    if not item:
        return ''
    alt = html.escape((item.get('alt') if isinstance(item, dict) else None) or profile.get('name', 'Logo'), quote=True)
    path = logo_path(profile, base_dir)
    if path.suffix == '.svg':
        svg = path.read_text()
        svg = re.sub(r'<\?xml[^>]*>', '', svg)
        return svg.replace('<svg', f'<svg class="logo" role="img" aria-label="{alt}"', 1)
    return f'<img class="logo" src="assets/{path.name}" alt="{alt}">'
