#!/usr/bin/env python3
"""Build, refresh, check and export a review site for one engagement.

  python3 review_site.py init    --project <dir>                 # copy the synthetic example to start
  python3 review_site.py intake  --project <dir> --input <export> --origin "..." --scope "..."
  python3 review_site.py build   --project <dir>
  python3 review_site.py check   --project <dir> [--skip-browser]
  python3 review_site.py refresh --project <dir> --input <export> --origin "..." --scope "..."
  python3 review_site.py export  --project <dir> [--saved answers.json] [--reviews moscow.json]
"""
import argparse
import sys
from pathlib import Path


def _kit():
    here = Path(__file__).resolve().parent
    for candidate in (here.parent / '_runtime/review-site-runtime', here.parents[1] / 'review-site-runtime'):
        if (candidate / 'lib/rsk').is_dir():
            return candidate
    sys.exit('review-site-runtime runtime is missing from this package')


KIT = _kit()
sys.path.insert(0, str(KIT / 'lib'))
from rsk import cli  # noqa: E402


def refresh(paths, export, origin, scope, allow_older=False):
    result = {'intake': cli.intake(paths['config'], export, paths['tracker'], origin, scope, allow_older)}
    if result['intake']['status'] == 'failed':
        return {**result, 'status': 'failed'}
    delta = paths['tracker'] / 'delta.json'
    if result['intake']['status'] == 'recorded' and (paths['content'] / 'stories.json').exists():
        queue = cli.queue(paths['content'], paths['tickets'], delta, paths['tracker'])
        result['queue'] = {'affected_stories': len(queue['affected_stories']), 'new_tickets': len(queue['new_tickets']),
                           'removed': len(queue['removed']), 'file': str(paths['tracker'] / 'review-queue.md')}
    result['build'] = cli.build(paths['config'], paths['content'], paths['tickets'], paths['dist'])
    result['status'] = result['build']['status']
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command', choices=['init', 'intake', 'build', 'check', 'refresh', 'export'])
    parser.add_argument('--project', required=True)
    parser.add_argument('--input')
    parser.add_argument('--origin', default='')
    parser.add_argument('--scope', default='')
    parser.add_argument('--saved')
    parser.add_argument('--reviews')
    parser.add_argument('--skip-browser', action='store_true')
    parser.add_argument('--allow-older', action='store_true', help='replace a newer export with this older one')
    a = parser.parse_args()
    p = cli.project_paths(a.project)
    if a.command in ('intake', 'refresh') and not (a.input and a.origin and a.scope):
        parser.error(a.command + ' needs --input, --origin and --scope')
    if a.command == 'init':
        return cli.run(cli.init, a.project, KIT / 'examples/northwind')
    if a.command == 'intake':
        return cli.run(cli.intake, p['config'], a.input, p['tracker'], a.origin, a.scope, a.allow_older)
    if a.command == 'build':
        return cli.run(cli.build, p['config'], p['content'], p['tickets'], p['dist'])
    if a.command == 'check':
        return cli.run(cli.check, p['config'], p['content'], p['tickets'], p['dist'], not a.skip_browser)
    if a.command == 'refresh':
        return cli.run(refresh, p, a.input, a.origin, a.scope, a.allow_older)
    return cli.run(cli.export, p['config'], p['content'], p['tickets'], a.saved, a.reviews, p['exports'])


if __name__ == '__main__':
    sys.exit(main())
