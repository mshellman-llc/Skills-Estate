#!/usr/bin/env python3
"""Export or verify a token snapshot derived from the selected brand policy.

Runtime loaders read the profile directly. This command supports consumers that
need a JSON snapshot; the snapshot is never a second authoring authority.
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'brand'))
from brand_profile import selected_tokens


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--check', type=Path, help='Fail when this snapshot differs from the selected profile')
    args = parser.parse_args()
    try:
        _, tokens = selected_tokens(args.profile)
        if args.check:
            existing = json.loads(args.check.read_text())
            if existing != tokens:
                print('Token snapshot differs from the selected profile.', file=sys.stderr)
                return 1
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(tokens, indent=2) + '\n')
        elif not args.check:
            print(json.dumps(tokens, indent=2))
        return 0
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
