#!/usr/bin/env python3
"""Resolve only the assets the selected profile actually requires."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "brand"))
from brand_profile import load_profile, resolve_profile


def resolve(explicit=None):
    path = resolve_profile(explicit)
    profile = load_profile(path)
    missing = []

    def asset(value, label):
        if not isinstance(value, str) or not value:
            missing.append(f"{label}: expected a local file path")
            return None
        candidate = Path(value).expanduser()
        if not candidate.is_absolute():
            candidate = path.parent / candidate
        if not candidate.is_file():
            missing.append(f"{label}: {candidate}")
            return None
        return str(candidate.resolve())

    logo = profile.get("logo")
    if isinstance(logo, dict):
        logo = logo.get("path", "")
    resolved_logo = asset(logo, "logo") if logo is not None else None
    fonts = profile["type"].get("files", {})
    if not isinstance(fonts, dict):
        raise ValueError("type.files must map font names to local file paths")
    resolved_fonts = {name: asset(value, f"font {name}") for name, value in fonts.items()}
    return {
        "ok": not missing, "profile": str(path), "profile_name": profile["name"],
        "brand_root": str(path.parent), "logo": resolved_logo,
        "fonts": resolved_fonts, "font_stack": profile["type"]["body"],
        "uses_system_fonts": not fonts, "missing": missing,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        report = resolve(args.profile)
    except (ValueError, OSError, KeyError) as exc:
        report = {"ok": False, "missing": [str(exc)]}
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
