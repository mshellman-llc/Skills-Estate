#!/usr/bin/env python3
"""Render a field-guide body into standalone HTML using a canonical brand profile.

Usage: python3 build_field_guide.py BODY --output guide.html [--profile brand.md]
Fonts and logos are embedded only when the selected profile declares them.
The neutral profile works without proprietary assets. Inspect the resulting page
and exercise its widgets with qa_field_guide.py before delivery.
"""
import argparse
from pathlib import Path
import sys
from brand_runtime import apply_profile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("body", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--profile", type=Path, help="canonical Markdown brand profile")
    args = parser.parse_args()
    try:
        html, profile = apply_profile(args.body.read_text(encoding="utf-8"), args.profile)
        out = args.output or Path("build") / (args.body.stem + ".html")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
    except (OSError, ValueError) as exc:
        print("Build failed: " + str(exc), file=sys.stderr)
        return 1
    print("Rendered {} with profile {}".format(out, profile["name"]))
    print("Next: source parity, interaction checks, rendered visual review, and prose review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
