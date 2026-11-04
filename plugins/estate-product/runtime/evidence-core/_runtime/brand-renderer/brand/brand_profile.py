"""Resolve the selected Markdown brand profile and compile renderer tokens.

No palette lives in this module. The neutral profile is policies/brand.md in
source, or references/estate/brand.md in a portable package.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re


def resolve_profile(explicit=None, *, cwd=None, anchor=None):
    if explicit or os.environ.get("SKILLS_BRAND_PROFILE"):
        path = Path(explicit or os.environ["SKILLS_BRAND_PROFILE"]).expanduser().resolve()
        if not path.is_file():
            raise ValueError(f"Selected brand profile does not exist: {path}")
        return path
    project = Path(cwd or Path.cwd()) / "brand.md"
    if project.is_file():
        return project.resolve()
    here = Path(anchor or __file__).resolve()
    for parent in here.parents:
        # Stop at the package's own policy before looking at an enclosing repo.
        for suffix in ("references/estate/brand.md", "policies/brand.md"):
            path = parent / suffix
            if path.is_file():
                return path
    raise ValueError("No brand policy found. Supply --profile or SKILLS_BRAND_PROFILE.")


def load_profile(path):
    text = Path(path).read_text(encoding="utf-8")
    blocks = re.findall(r"```json\s*\n(.*?)\n```", text, re.S)
    if len(blocks) != 1:
        raise ValueError("A profile needs exactly one JSON block")
    profile = json.loads(blocks[0])
    if profile.get("status") != "confirmed":
        raise ValueError("This renderer requires a confirmed profile")
    if not profile.get("name") or not profile.get("source"):
        raise ValueError("A profile needs a name and source")
    colors = profile.get("colors", {})
    for role in ("background", "text", "muted", "border", "surface", "accent"):
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", colors.get(role, "")):
            raise ValueError(f"Missing or invalid color: {role}")
    for role, value in colors.items():
        if not re.fullmatch(r"[a-z][a-z0-9-]*", role) or not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
            raise ValueError(f"Invalid color token: {role}")
    for role in ("body", "headings"):
        if not re.fullmatch(r"""[a-zA-Z0-9 ,"'-]+""", profile.get("type", {}).get(role, "")):
            raise ValueError(f"Invalid font stack: {role}")
    layout = profile.get("layout", {})
    for key in ("border_px", "radius_px"):
        value = layout.get(key)
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 100:
            raise ValueError(f"Missing or invalid layout value: {key}")
    return profile


def contrast(a, b):
    def luminance(value):
        channels = [int(value[i:i+2], 16) / 255 for i in (1, 3, 5)]
        linear = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in channels]
        return sum(c * w for c, w in zip(linear, (0.2126, 0.7152, 0.0722)))
    x, y = sorted((luminance(a), luminance(b)))
    return (y + 0.05) / (x + 0.05)


def compile_tokens(profile, path, *, mapping_path=None):
    """Keep existing renderer keys while resolving every value from the profile."""
    mapping_path = Path(mapping_path or Path(__file__).with_name("token-roles.json"))
    mapping = json.loads(mapping_path.read_text())
    palette = profile["colors"]
    colors = {}
    for key, role in mapping["roles"].items():
        value = palette[role]
        colors[key] = {
            "hex": value.upper(), "role": role,
            "cssVar": "--brand-" + role,
            "brand": role == "accent", "group": role,
        }
    # Additional project colors are usable without editing the compatibility map.
    for role, value in palette.items():
        colors.setdefault(role, {
            "hex": value.upper(), "role": role, "cssVar": "--brand-" + role,
            "brand": role == "accent", "group": role,
        })
    layout = profile["layout"]
    radius = layout["radius_px"]
    rules = {
        "warmAccentsAllowed": True,
        "warmSurfacesAllowed": [],
        "borderWidthPx": layout["border_px"],
        "borderNeverBlack": False,
        "borderColorsBySurface": {"light": palette["border"], "sand": palette["border"]},
        "radius": {"allowedPx": [radius], "defaultPx": radius, "smallPx": radius,
                   "capPx": radius, "pillPx": 999, "pillUsage": "avatars and status indicators"},
        "headingCase": layout.get("heading_case", "sentence"),
        "labelTrackingEm": layout.get("label_tracking_em", 0),
        "bodyAlign": "left", "titleUnderline": False,
        "footer": {"required": False, "convention": False},
        "markAndLockupTogether": False,
        "shadow": {"allowed": False, "maxOffsetPx": 0},
        "eyebrow": {
            "brandHex": palette["muted"], "defaultHex": palette["muted"],
            "brandContrastOnWhite": round(contrast(palette["muted"], palette["background"]), 2),
            "defaultContrastOnWhite": round(contrast(palette["muted"], palette["background"]), 2),
            "wcagLargeTextMin": 3, "onDarkHex": palette["background"],
        },
    }
    return {
        "provenance": {
            "source": str(Path(path).resolve()),
            "sourceSha256": hashlib.sha256(Path(path).read_bytes()).hexdigest(),
            "mode": "authoritative", "guidelines": profile["name"],
        },
        "colors": colors, "aliases": mapping["aliases"], "rules": rules,
        "type": {**profile["type"], "family": profile["type"]["body"],
                 "numerals": "tabular", "monospaceInBodies": False},
        "logo": profile.get("logo"), "blocked": {},
    }


def selected_tokens(explicit=None, **kwargs):
    path = resolve_profile(explicit, **kwargs)
    return path, compile_tokens(load_profile(path), path)


def css(profile):
    values = [f"  --brand-{role}: {value};" for role, value in profile["colors"].items()]
    values += [f'  --brand-font-{role}: {profile["type"][role]};' for role in ("body", "headings")]
    return ":root {\n" + "\n".join(values) + "\n}\n"
