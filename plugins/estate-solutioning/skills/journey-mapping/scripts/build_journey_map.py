#!/usr/bin/env python3
"""Build a journey map page from map JSON, with the roadmap components inline.

    python3 scripts/build_journey_map.py map-data.json --output journey-map.html

The page stays one file with no network requests. Colors come from the
starter's :root roles; replace them with a confirmed project profile.
"""
import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
STARTER = HERE.parent / "assets/journey-map.html"


def roadmap_assets():
    for path in (HERE.parent / "_runtime/roadmap-artifacts/scripts", HERE.parent.parent / "roadmap-artifacts/scripts"):
        if (path / "rk_embed.py").is_file():
            sys.path.insert(0, str(path))
            import rk_embed
            return rk_embed.assets()
    raise RuntimeError("Roadmap runtime is missing. Rebuild this skill with its declared dependencies.")


def build(data, starter=None):
    html = (starter or STARTER).read_text(encoding="utf-8")
    start = html.index("const MAP = {")
    end = html.index("\n};", start) + 3
    body = json.dumps(data, ensure_ascii=False, indent=2).replace("<", "\\u003c")
    html = html[:start] + "const MAP = " + body + ";" + html[end:]
    kit = roadmap_assets()
    for slot, value in (("/*__RK_CSS__*/", kit["css"]), ("/*__RK_JS__*/", kit["js"])):
        if html.count(slot) != 1:
            raise ValueError("Starter is missing the roadmap slot " + slot)
        html = html.replace(slot, value)
    return html


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("data", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output exists; choose a new attempt")
    try:
        html = build(json.loads(args.data.read_text(encoding="utf-8")))
    except (ValueError, OSError, RuntimeError) as error:
        parser.exit(2, str(error) + "\n")
    args.output.write_text(html, encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
