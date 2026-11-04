#!/usr/bin/env python3
"""Turn a tracker export into canonical tickets, an intake record and a delta.

  python3 intake.py --config site.json --input export.csv --out tracker/ \
      --origin "Jira export from the client PM" --scope "project NW, all issues"
"""
import argparse
import sys
from pathlib import Path


def _kit():
    here = Path(__file__).resolve().parent
    for candidate in (here.parent / '_runtime/review-site-kit', here.parents[1] / 'review-site-kit'):
        if (candidate / 'lib/rsk').is_dir():
            return candidate
    sys.exit('review-site-kit runtime is missing from this package')


KIT = _kit()
sys.path.insert(0, str(KIT / 'lib'))
from rsk import cli  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--config', required=True, help='engagement site.json')
    parser.add_argument('--input', required=True, help='tracker export file')
    parser.add_argument('--out', required=True, help='tracker folder; tickets.json, delta.json and intake-log.json go here')
    parser.add_argument('--origin', required=True, help='who supplied the export and how')
    parser.add_argument('--scope', required=True, help='what the export covers')
    a = parser.parse_args()
    return cli.run(cli.intake, a.config, a.input, a.out, a.origin, a.scope)


if __name__ == '__main__':
    sys.exit(main())
