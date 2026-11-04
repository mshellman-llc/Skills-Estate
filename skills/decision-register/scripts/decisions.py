#!/usr/bin/env python3
"""Check the decision register and export saved answers for the client's tracker.

  python3 decisions.py check  --content content/ --tickets tracker/tickets.json
  python3 decisions.py export --content content/ --saved answers.json --out exports/
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
from rsk import decisions, stories, validate  # noqa: E402


def check(content, tickets):
    questions_doc = validate.load(Path(content) / 'questions.json', 'questions')
    tickets_doc = validate.load(tickets, 'tickets') if tickets else None
    stories_path = Path(content) / 'stories.json'
    story_list = validate.load(stories_path, 'stories')['stories'] if stories_path.exists() else None
    problems = decisions.problems(questions_doc, story_list, stories.index(tickets_doc) if tickets_doc else None)
    counts = {}
    for q in questions_doc['questions']:
        counts[q['status']] = counts.get(q['status'], 0) + 1
    return {'status': 'failed' if problems else 'ok', 'problems': problems, 'questions': len(questions_doc['questions']),
            'by_status': counts, 'no_owner': [q['id'] for q in questions_doc['questions'] if not q.get('owner')]}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command', choices=['check', 'export'])
    parser.add_argument('--content', required=True)
    parser.add_argument('--tickets')
    parser.add_argument('--saved', help='answers exported from the shared store or a browser')
    parser.add_argument('--out', default='.')
    a = parser.parse_args()
    if a.command == 'check':
        return cli.run(check, a.content, a.tickets)
    return cli.run(cli.export, None, a.content, a.tickets, a.saved, None, a.out)


if __name__ == '__main__':
    sys.exit(main())
