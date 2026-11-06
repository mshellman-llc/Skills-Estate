#!/usr/bin/env python3
"""Run the accepted updater bundled with this installed maintenance package."""
import argparse
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, required=True)
    parser.add_argument('--home', type=Path, required=True)
    args = parser.parse_args()
    tooling = Path(__file__).resolve().with_name('estate_tools')
    if not (tooling / 'updater.py').is_file():
        parser.error('Updater tooling is missing; use an assembled, installed maintenance package')
    sys.path.insert(0, str(tooling))
    import updater
    try:
        result = updater.update(args.repository, args.home)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
