#!/usr/bin/env python3
"""Story map calculations from the content files and canonical tickets.

  python3 story_map.py summary --config site.json --content content/ --tickets tracker/tickets.json
  python3 story_map.py queue   --content content/ --tickets tracker/tickets.json --delta tracker/delta.json --out tracker/
  python3 story_map.py export-reviews --config site.json --content content/ --tickets tracker/tickets.json --reviews moscow.json --out exports/
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
from rsk import render  # noqa: E402


def summary(config, content, tickets):
    cfg, tickets_doc, data = render.load_inputs(config, content, tickets)
    computed, problems = render.compute(cfg, tickets_doc, data)
    graph = computed['critical_path'] or {}
    return {'status': 'failed' if problems else 'ok', 'problems': problems,
            'stories': len(computed['stories']),
            'by_class': {c: sum(1 for s in computed['stories'] if s['class'] == c) for c in ('must', 'should', 'could', 'wont')},
            'ready': sum(1 for s in computed['stories'] if s['computed']['ready']),
            'not_ready': [s['id'] for s in computed['stories'] if not s['computed']['ready']],
            'share': computed['share'], 'must_ceiling': computed['must_ceiling'],
            'unclassed': computed['unclassed'],
            'critical_path': {k: graph.get(k) for k in ('nodes', 'edges', 'untracked', 'columns')}}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command', choices=['summary', 'queue', 'export-reviews'])
    parser.add_argument('--config')
    parser.add_argument('--content', required=True)
    parser.add_argument('--tickets', required=True)
    parser.add_argument('--delta')
    parser.add_argument('--reviews')
    parser.add_argument('--out', default='.')
    a = parser.parse_args()
    if a.command == 'summary':
        return cli.run(summary, a.config, a.content, a.tickets)
    if a.command == 'queue':
        return cli.run(lambda *x: {'status': 'ok', **cli.queue(*x)}, a.content, a.tickets, a.delta, a.out)
    return cli.run(cli.export, a.config, a.content, a.tickets, None, a.reviews, a.out)


if __name__ == '__main__':
    sys.exit(main())
