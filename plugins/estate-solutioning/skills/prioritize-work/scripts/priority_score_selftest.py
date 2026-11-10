#!/usr/bin/env python3
"""Selftest for priority_score.py.

The fixtures describe an invented island ferry booking app. Every ID, title,
source and number in them is synthetic. Expected scores were worked out by
hand from each method's formula and are written here as literals.

Paths resolve from this file, so the test runs from any working directory.
Prints one line per failed check, then a count of passed checks.
Exits 0 when everything passes and 1 otherwise.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
SCORER = HERE / 'priority_score.py'
FIXTURES = HERE / 'fixtures'
TOP_IMPACT_PHRASE = 'share the highest impact'
TABLE_HEADER = '| Rank | ID | Title | Score | Formula | Flags |'
PROPOSAL_SENTENCE = 'Proposal only: the decision owner sets the final order'
REPORT_KEYS = {'framework', 'ranking', 'errors', 'notes'}
ROW_KEYS = {'id', 'title', 'job', 'score', 'formula', 'flags', 'rank'}


class Results:
    def __init__(self):
        self.passed = 0
        self.failed = []

    def check(self, label, condition, detail=''):
        if condition:
            self.passed += 1
        else:
            self.failed.append(label + (': ' + detail if detail else ''))


def run(*args):
    command = [sys.executable, str(SCORER), *(str(arg) for arg in args)]
    return subprocess.run(command, capture_output=True, text=True, timeout=60)


def scored(path, framework):
    """Run the scorer with JSON output; return the exit code, parsed report and stderr."""
    result = run(path, '--framework', framework, '--format', 'json')
    try:
        report = json.loads(result.stdout)
    except ValueError:
        report = {'framework': None, 'ranking': [], 'errors': [], 'notes': []}
    return result.returncode, report, result.stderr


def ids(report):
    return [row['id'] for row in report['ranking']]


def scores(report):
    return [row['score'] for row in report['ranking']]


def rows(report):
    return {row['id']: row for row in report['ranking']}


def flagged(row, fragment):
    return any(fragment in flag for flag in row['flags'])


def rejected(report, prefix, fragment=''):
    return any(error.startswith(prefix) and fragment in error for error in report['errors'])


def rice_with_sources(results, folder):
    code, report, stderr = scored(FIXTURES / 'rice_fully_sourced.json', 'rice')
    results.check('sourced RICE exits 0', code == 0, stderr)
    results.check('sourced RICE order', ids(report) == ['FRY-012', 'FRY-011', 'FRY-015', 'FRY-013', 'FRY-014'],
                  str(ids(report)))
    results.check('sourced RICE scores', scores(report) == [750, 640, 240, 180, 90], str(scores(report)))
    results.check('sourced RICE raises no flags', all(row['flags'] == [] for row in report['ranking']))
    results.check('report keys', set(report) == REPORT_KEYS, str(sorted(report)))
    results.check('row keys', all(set(row) == ROW_KEYS for row in report['ranking']))
    results.check('ranks are consecutive', [row['rank'] for row in report['ranking']] == [1, 2, 3, 4, 5])
    by_id = rows(report)
    results.check('formula shows the percent as a fraction',
                  by_id.get('FRY-015', {}).get('formula') == '(1800 * 0.25 * 0.8) / 1.5 = 240')
    results.check('job falls back to problem',
                  by_id.get('FRY-011', {}).get('job') == 'Riders lose phone signal at the pier and cannot show a ticket')


def rice_evidence_rules(results, folder):
    code, report, stderr = scored(FIXTURES / 'rice_evidence.json', 'rice')
    by_id = rows(report)
    results.check('evidence file exits 0', code == 0, stderr)
    results.check('evidence file order',
                  ids(report) == ['FRY-024', 'FRY-021', 'FRY-023', 'FRY-022', 'FRY-026', 'FRY-025'], str(ids(report)))
    capped = by_id.get('FRY-021', {'score': None, 'formula': '', 'flags': []})
    results.check('unsourced confidence capped', capped['score'] == 250 and '* 0.5)' in capped['formula'],
                  capped['formula'])
    results.check('cap flag quotes 0.9', flagged(capped, '0.9') and flagged(capped, 'cap'), str(capped['flags']))
    results.check('unsourced effort flagged', flagged(by_id.get('FRY-022', {'flags': []}), 'engineering'))
    results.check('off-scale impact flagged', flagged(by_id.get('FRY-023', {'flags': []}), 'off the RICE scale'))
    percent = by_id.get('FRY-024', {'score': None, 'formula': '', 'flags': ['missing']})
    results.check('percent 80 read as 0.8', percent['score'] == 320 and '* 0.8)' in percent['formula']
                  and percent['flags'] == [], percent['formula'])
    small = by_id.get('FRY-025', {'score': None, 'flags': []})
    results.check('confidence 8 flagged as percent', small['score'] == 40 and flagged(small, 'read as 8%'),
                  str(small['flags']))
    results.check('missing job flagged', flagged(by_id.get('FRY-026', {'flags': []}), 'frame-jobs-to-be-done'))


def rejections(results, folder):
    code, report, stderr = scored(FIXTURES / 'rice_rejections.json', 'rice')
    results.check('rejections exit 1', code == 1, stderr)
    results.check('valid items still ranked', ids(report) == ['FRY-037', 'FRY-038', 'FRY-031'], str(ids(report)))
    results.check('numeric text accepted', scores(report) == [200, 187.5, 150], str(scores(report)))
    results.check('seven rejections', len(report['errors']) == 7, str(report['errors']))
    results.check('absent field named', rejected(report, 'FRY-032:', 'effort'))
    results.check('null field named', rejected(report, 'FRY-033:', 'reach'))
    results.check('duplicate id rejected', rejected(report, 'FRY-031 (item 4)', 'item 1'))
    results.check('percent text rejected', rejected(report, 'FRY-034:', '"80%"'))
    results.check('zero effort rejected', rejected(report, 'FRY-035:', 'greater than 0'))
    results.check('bare string rejected', rejected(report, 'item 7:', 'JSON object'))
    results.check('missing id uses title', rejected(report, '"Cabin upgrade" (item 8):', 'id'))


def ice_concentration(results, folder):
    code, report, stderr = scored(FIXTURES / 'ice_concentrated.json', 'ice')
    results.check('ICE exits 0', code == 0, stderr)
    results.check('ICE scores', scores(report) == [30, 24, 22.5, 12, 9.6], str(scores(report)))
    results.check('ICE order', ids(report) == ['INIT-02', 'INIT-01', 'INIT-03', 'INIT-04', 'INIT-05'])
    results.check('top-impact note at 40%', any(TOP_IMPACT_PHRASE in note for note in report['notes']),
                  str(report['notes']))
    code, report, stderr = scored(FIXTURES / 'ice_rejected_top.json', 'ice')
    results.check('rejected ICE items exit 1', code == 1, stderr)
    results.check('scored ICE subset', ids(report) == ['INIT-11', 'INIT-14', 'INIT-15', 'INIT-16']
                  and scores(report) == [18, 14, 9, 8], str(scores(report)))
    results.check('rejected items not counted for impact',
                  not any(TOP_IMPACT_PHRASE in note for note in report['notes']), str(report['notes']))


def odi(results, folder):
    code, report, stderr = scored(FIXTURES / 'odi_outcomes.json', 'odi')
    by_id = rows(report)
    results.check('ODI exits 0', code == 0, stderr)
    results.check('ODI scores', ids(report) == ['OUT-01', 'OUT-03', 'OUT-04', 'OUT-02']
                  and scores(report) == [15, 13, 9.5, 7], str(scores(report)))
    results.check('satisfaction above importance adds 0',
                  by_id.get('OUT-02', {}).get('formula') == '7 + max(7 - 8, 0) = 7')
    results.check('unsourced importance is a hypothesis', flagged(by_id.get('OUT-04', {'flags': []}), 'hypothesis'))
    results.check('sourced importance unflagged', by_id.get('OUT-01', {}).get('flags') == [])


def opportunity(results, folder):
    code, report, stderr = scored(FIXTURES / 'opportunity_jobs.json', 'opportunity')
    by_id = rows(report)
    results.check('opportunity exits 0', code == 0, stderr)
    results.check('opportunity scores', ids(report) == ['JOB-1', 'JOB-3', 'JOB-2']
                  and scores(report) == [6, 4.5, 3.6], str(scores(report)))
    converted = by_id.get('JOB-2', {'formula': '', 'flags': []})
    results.check('rating converted and flagged', converted['formula'] == '6 * (1 - 0.4) = 3.6'
                  and flagged(converted, 'converted to 0.4'), str(converted['flags']))


def wsjf(results, folder):
    code, report, stderr = scored(FIXTURES / 'wsjf_portfolio.json', 'wsjf')
    results.check('WSJF exits 1', code == 1, stderr)
    results.check('WSJF scores', ids(report) == ['PF-1', 'PF-2', 'PF-4'] and scores(report) == [8, 7, 2],
                  str(scores(report)))
    results.check('unsized job flagged', flagged(rows(report).get('PF-2', {'flags': []}), 'job size'))
    results.check('job size 0 rejected', rejected(report, 'PF-3:', 'job_size'))


def weighted(results, folder):
    code, report, stderr = scored(FIXTURES / 'weighted_options.json', 'weighted')
    results.check('weighted exits 1', code == 1, stderr)
    results.check('rescaled weights used', ids(report) == ['OPT-B', 'OPT-C', 'OPT-A']
                  and scores(report) == [3.9, 3.1, 2.8], str(scores(report)))
    results.check('rescale noted', any('summed to 10' in note for note in report['notes']), str(report['notes']))
    results.check('missing criterion rejected', rejected(report, 'OPT-D:', 'fare revenue'))
    result = run(FIXTURES / 'weighted_zero.json', '--framework', 'weighted')
    results.check('zero weights exit 2', result.returncode == 2 and result.stderr.startswith('error:')
                  and result.stdout == '', result.stderr)


def unusable_input(results, folder):
    broken = folder / 'broken.json'
    broken.write_text('[{"id": "FRY-051", "reach": 10,}]')
    empty = folder / 'empty.json'
    empty.write_text('[]')
    cases = [('bad JSON', broken), ('object without items', FIXTURES / 'items_under_wrong_key.json'),
             ('empty list', empty), ('unreadable file', folder / 'absent.json')]
    for label, path in cases:
        result = run(path, '--framework', 'rice')
        results.check(label + ' exits 2', result.returncode == 2 and result.stderr.startswith('error:')
                      and result.stdout == '', f'exit {result.returncode}, stderr {result.stderr!r}')


def ties(results, folder):
    code, report, stderr = scored(FIXTURES / 'ice_ties.json', 'ice')
    results.check('ties exit 0', code == 0, stderr)
    results.check('tied scores keep input order', ids(report) == ['INIT-22', 'INIT-21', 'INIT-23'], str(ids(report)))
    results.check('ranks have no gaps', [row['rank'] for row in report['ranking']] == [1, 2, 3])
    results.check('tie note lists both', any(note.startswith('Tied') and 'INIT-21' in note and 'INIT-22' in note
                                             for note in report['notes']), str(report['notes']))


def markdown(results, folder):
    result = run(FIXTURES / 'rice_fully_sourced.json', '--framework', 'rice')
    results.check('markdown table header', TABLE_HEADER in result.stdout)
    results.check('markdown proposal sentence', PROPOSAL_SENTENCE in result.stdout)
    target = folder / 'report.md'
    written = run(FIXTURES / 'rice_fully_sourced.json', '--framework', 'rice', '--output', target)
    text = target.read_text() if target.exists() else ''
    results.check('output file written', written.returncode == 0 and TABLE_HEADER in text and written.stdout == '')
    blocked = run(FIXTURES / 'rice_fully_sourced.json', '--framework', 'rice', '--output', folder / 'no-such-dir' / 'r.md')
    results.check('unwritable output exits 2', blocked.returncode == 2 and blocked.stderr.startswith('error:'))
    strings = folder / 'strings.json'
    strings.write_text('["FRY-061", 7]')
    nothing = run(strings, '--framework', 'ice')
    results.check('nothing scored exits 1', nothing.returncode == 1)
    results.check('nothing scored has no table', TABLE_HEADER not in nothing.stdout
                  and 'No candidate could be scored' in nothing.stdout, nothing.stdout)


def main():
    results = Results()
    cases = (rice_with_sources, rice_evidence_rules, rejections, ice_concentration, odi,
             opportunity, wsjf, weighted, unusable_input, ties, markdown)
    with tempfile.TemporaryDirectory() as temp:
        for case in cases:
            try:
                case(results, Path(temp))
            except Exception as exc:  # a malformed report or a hung run must not hide the later cases
                results.failed.append(f'{case.__name__} stopped early: {exc!r}')
    for failure in results.failed:
        print('FAIL ' + failure)
    total = results.passed + len(results.failed)
    print(f'priority_score_selftest: {results.passed} of {total} checks passed')
    return 1 if results.failed else 0


if __name__ == '__main__':
    sys.exit(main())
