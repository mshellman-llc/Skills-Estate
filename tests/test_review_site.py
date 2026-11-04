"""Review-site series: intake, story map, decisions, rendering, gates and packaging."""
import csv
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / 'skills/review-site-kit'
EXAMPLE = KIT / 'examples/northwind'
SITE = ROOT / 'skills/review-site/scripts/review_site.py'
sys.path.insert(0, str(KIT / 'lib'))
sys.path.insert(0, str(ROOT / 'tools'))
from rsk import cli, decisions, gate, render, stories, tracker, validate  # noqa: E402
from test_capabilities import integration  # noqa: E402

FIRST = EXAMPLE / 'tracker/jira-2026-01-09.csv'
SECOND = EXAMPLE / 'tracker/jira-2026-01-16.csv'


def run(*args, cwd=None):
    return subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True, cwd=cwd)


class Project:
    """A synthetic engagement built from the example through the public script."""

    def __init__(self, test, script=SITE):
        self.temp = tempfile.TemporaryDirectory()
        test.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name) / 'review-site'
        self.script = script
        for step in (['init'], ['intake', '--input', FIRST], ['refresh', '--input', SECOND]):
            extra = [] if step == ['init'] else ['--origin', 'synthetic fixture', '--scope', 'project NW']
            result = run(script, step[0], '--project', self.dir, *step[1:], *extra)
            test.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.paths = cli.project_paths(self.dir)

    def json(self, relative):
        return json.loads((self.dir / relative).read_text())


class IntakeTests(unittest.TestCase):
    def config(self):
        return json.loads((EXAMPLE / 'config/site.json').read_text())

    def test_jira_repeated_columns_become_lists(self):
        doc, warnings = tracker.load(SECOND, self.config())
        t = {x['key']: x for x in doc['tickets']}
        self.assertEqual(warnings, [])
        self.assertEqual(t['NW-12']['sprints'], ['Sprint 1', 'Sprint 2'])
        self.assertEqual(t['NW-12']['sprint'], 'Sprint 2')
        self.assertEqual(t['NW-22']['blocked_by'], ['NW-21', 'NW-23'])
        self.assertEqual(t['NW-21']['blocks'], ['NW-22'])
        self.assertEqual(t['NW-11']['epic'], 'NW-1')
        self.assertEqual(t['NW-23']['category'], 'canceled')
        self.assertEqual(t['NW-21']['category'], 'wip')
        self.assertEqual(t['NW-11']['acceptance'], ['A request needs a site, a contact and a problem type.',
                                                    'The form confirms the request number on submit.'])
        self.assertEqual(t['NW-11']['updated'], '2026-01-09T16:10')
        self.assertNotIn('Reviewed with the operations lead.', json.dumps(doc))
        self.assertEqual(t['NW-11']['comment_count'], 1)

    def test_delta_and_intake_record(self):
        old, _ = tracker.load(FIRST, self.config())
        new, warnings = tracker.load(SECOND, self.config())
        change = tracker.delta(old, new)
        self.assertEqual(change['added'], ['NW-25'])
        changed = {c['key']: c['changes'] for c in change['changed']}
        self.assertEqual(changed['NW-12']['status'], ['In Progress', 'Done'])
        self.assertEqual(changed['NW-13']['points'], [None, 3.0])
        self.assertIn('summary', changed['NW-31'])
        record = tracker.intake_record(SECOND, new, warnings, 'client PM', 'project NW', old)
        for field in ('original_name', 'sha256', 'received', 'origin', 'scope', 'redactions', 'conflicts', 'previous_sha256'):
            self.assertIn(field, record)
        self.assertEqual(record['previous_sha256'], old['source']['sha256'])

    def test_unknown_status_is_a_conflict_and_status_map_fixes_it(self):
        temp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, temp)
        with FIRST.open(encoding='utf-8') as handle:
            rows = list(csv.reader(handle))
        status = rows[0].index('Status')
        rows[5][status] = 'Parked'
        path = temp / 'export.csv'
        with path.open('w', newline='') as handle:
            csv.writer(handle).writerows(rows)
        _, warnings = tracker.load(path, self.config())
        self.assertTrue(any('Parked' in w for w in warnings))
        config = self.config()
        config['tracker']['status_map'] = {'Parked': 'blocked'}
        doc, warnings = tracker.load(path, config)
        self.assertFalse(any('Parked' in w for w in warnings))
        self.assertIn('blocked', {t['category'] for t in doc['tickets']})

    def test_table_csv_adapter(self):
        temp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, temp)
        path = temp / 'board.csv'
        path.write_text('ID,Title,State,Epic,Iteration,Effort,Blocked by\n'
                        'AB-1,Login page,Active,AB-0,Iteration 2,3,\nAB-2,Reset password,New,AB-0,,,AB-1\n')
        config = {'tracker': {'adapter': 'table-csv', 'columns': {
            'key': 'ID', 'summary': 'Title', 'status': 'State', 'epic': 'Epic', 'sprint': 'Iteration',
            'points': 'Effort', 'blocked_by': 'Blocked by'}, 'status_map': {'Active': 'wip'}}}
        doc, warnings = tracker.load(path, config)
        t = {x['key']: x for x in doc['tickets']}
        self.assertEqual(t['AB-1']['category'], 'wip')
        self.assertEqual(t['AB-2']['blocked_by'], ['AB-1'])
        self.assertEqual(t['AB-1']['points'], 3.0)
        self.assertEqual(warnings, [])

    def test_same_export_twice_changes_nothing(self):
        project = Project(self)
        before = project.json('tracker/intake-log.json')
        result = run(SITE, 'intake', '--project', project.dir, '--input', SECOND, '--origin', 'x', '--scope', 'y')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'unchanged')
        self.assertEqual(project.json('tracker/intake-log.json'), before)
        self.assertEqual(len(before), 2)
        self.assertEqual(len(list((project.dir / 'tracker/history').iterdir())), 1)


class StoryMapTests(unittest.TestCase):
    def setUp(self):
        self.project = Project(self)
        self.tickets = validate.load(self.project.paths['tickets'], 'tickets')
        self.content = {n: validate.load(self.project.paths['content'] / f'{n}.json', n) for n in ('stories', 'questions')}
        self.synced = stories.sync(self.content['stories'], self.tickets, self.content['questions'])
        self.by_id = {s['id']: s for s in self.synced}

    def test_readiness_follows_the_rules(self):
        self.assertTrue(self.by_id['st-dup']['computed']['ready'])
        route = self.by_id['st-route']['computed']
        self.assertFalse(route['ready'])
        self.assertEqual(route['open_questions'], ['q-region'])
        self.assertEqual(route['blockers'], ['NW-21'])
        self.assertTrue(self.by_id['st-cal']['computed']['checks']['acceptance'])
        self.assertEqual(self.by_id['st-training']['computed']['status']['category'], 'untracked')

    def test_must_share_counts_open_estimated_points(self):
        share = stories.must_share(self.synced)
        self.assertEqual(share['open_points']['must'], 11.0)
        self.assertEqual(share['open_points']['could'], 2.0)
        self.assertEqual(share['must_share'], round(11 / 13, 4))

    def test_unclassed_and_critical_path(self):
        config = json.loads(self.project.paths['config'].read_text())
        self.assertEqual([u['key'] for u in stories.unclassed(self.synced, self.tickets, config)], ['NW-24', 'NW-25'])
        graph = stories.critical_path(self.synced, self.tickets, config)
        self.assertEqual(graph['nodes'], ['NW-13', 'NW-21', 'NW-22', 'NW-23'])
        self.assertIn(('NW-21', 'NW-22'), graph['edges'])
        self.assertEqual(graph['untracked'], ['st-training'])
        self.assertIn('cp-off', graph['svg'])
        self.assertNotIn('#', re.sub(r'url\(#[^)]+\)|id="[^"]+"', '', graph['svg']))

    def test_review_queue_lists_changes_and_candidates(self):
        queue = self.project.json('tracker/review-queue.json')
        self.assertEqual({a['story'] for a in queue['affected_stories']}, {'st-dup', 'st-route', 'st-close'})
        self.assertEqual([n['key'] for n in queue['new_tickets']], ['NW-25'])
        self.assertTrue(queue['new_tickets'][0]['candidates'])
        self.assertIn('NW-12 status: In Progress -> Done', (self.project.dir / 'tracker/review-queue.md').read_text())


class DecisionTests(unittest.TestCase):
    def test_saved_status_and_answers_export(self):
        questions = validate.load(EXAMPLE / 'content/questions.json', 'questions')
        saved = {'q-region': {'status': 'Answered', 'answer': 'North and South', 'at': '2026-01-20T10:00'},
                 'q-dup': {'state': 'Proposal accepted'}}
        rows = {r['id']: r for r in decisions.merged(questions, saved)}
        self.assertEqual(rows['q-region']['status'], 'Answered')
        self.assertEqual(rows['q-dup']['status'], 'Answered')
        self.assertEqual(rows['q-photo']['status'], 'Blocked')
        table = list(csv.reader(decisions.export_csv(questions, saved).splitlines()))
        self.assertEqual(table[0][:2], ['Issue key', 'Question id'])
        self.assertIn(['NW-13', 'q-region', 'Which regions get their own queue at launch?', 'Answered', 'North and South', '', '2026-01-20T10:00'], table)
        self.assertIn('## Visit planning', decisions.export_markdown(questions, saved))

    def test_store_listing_shapes_are_accepted(self):
        temp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, temp)
        path = temp / 'answers.json'
        path.write_text(json.dumps([{'id': 'q-slot', 'data': {'status': 'Deferred'}}]))
        self.assertEqual(decisions.load_saved(path), {'q-slot': {'status': 'Deferred'}})

    def test_problems_name_unknown_references(self):
        questions = validate.load(EXAMPLE / 'content/questions.json', 'questions')
        questions['questions'][0]['stories'] = ['st-missing']
        found = decisions.problems(questions, [{'id': 'st-route'}], {'NW-13': {}})
        self.assertTrue(any('st-missing' in p for p in found))


class RenderAndGateTests(unittest.TestCase):
    def setUp(self):
        self.project = Project(self)
        p = self.project.paths
        self.args = (p['config'], p['content'], p['tickets'], p['dist'])

    def test_pages_read_one_data_file(self):
        dist = self.project.paths['dist']
        self.assertEqual(sorted(f.name for f in dist.glob('*.html')),
                         ['build.html', 'decisions.html', 'index.html', 'mockups.html', 'workflow.html'])
        data = render.read_data(dist)
        self.assertEqual(data['source']['sha256'], self.project.json('tracker/tickets.json')['source']['sha256'])
        for page in dist.glob('*.html'):
            text = page.read_text()
            self.assertIn('data/site-data.js', text)
            self.assertNotIn('NW-', text)
        self.assertEqual(json.loads((dist / 'manifest.json').read_text())['brand'], 'Baseline')

    def test_data_gate_passes_then_catches_a_stale_status(self):
        results = {r['rule']: r for r in gate.data(*self.args)}
        for rule in ('D1', 'D2', 'D3', 'W1'):
            self.assertEqual(results[rule]['status'], 'passed', results[rule])
        data_file = self.project.paths['dist'] / 'data/site-data.js'
        text = data_file.read_text().replace('"status":"In Review"', '"status":"Done"')
        data_file.write_text(text)
        results = {r['rule']: r for r in gate.data(*self.args)}
        self.assertEqual(results['D2']['status'], 'failed')
        self.assertEqual(results['D3']['status'], 'failed')

    def test_build_refuses_unknown_references(self):
        path = self.project.paths['content'] / 'stories.json'
        doc = json.loads(path.read_text())
        doc['stories'][0]['tickets'] = ['NW-999']
        path.write_text(json.dumps(doc))
        result = cli.build(*self.args)
        self.assertEqual(result['status'], 'failed')
        self.assertTrue(any('NW-999' in p for p in result['problems']))

    def test_writing_gate_fails_banned_vocabulary(self):
        path = self.project.paths['content'] / 'stories.json'
        doc = json.loads(path.read_text())
        doc['stories'][0]['what'] = 'It is important to note that this robust form seamlessly leverages every request.'
        path.write_text(json.dumps(doc))
        config, tickets, content = render.load_inputs(*self.args[:3])
        result = gate.writing(config, content)
        self.assertEqual(result['status'], 'failed')
        self.assertIn('stories.st-form.what', {f for item in result['findings'] for f in item['fields']})

    def test_export_writes_tracker_files(self):
        temp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, temp)
        saved, reviews = temp / 'answers.json', temp / 'moscow.json'
        saved.write_text(json.dumps({'q-slot': {'status': 'Answered'}}))
        reviews.write_text(json.dumps([{'id': 'st-close', 'data': {'class': 'should', 'note': 'Needed for audits'}}]))
        result = run(SITE, 'export', '--project', self.project.dir, '--saved', saved, '--reviews', reviews)
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = list(csv.reader((self.project.dir / 'exports/class-reviews.csv').read_text().splitlines()))
        self.assertEqual(rows[1], ['st-close', 'Close with work notes', 'NW-31', 'Could', 'Should', 'Needed for audits', ''])

    @integration('browser')
    def test_browser_rules_pass_and_catch_mixed_table_sizes(self):
        results = {r['rule']: r for r in gate.browser(self.project.paths['dist'])}
        for rule in ('R-ERR-1', 'R-LAYOUT-1', 'R-TYPE-1', 'R-FOLD-1', 'R-DEC-1', 'R-NUM-1', 'R-COLOR-1', 'R-TINT-1', 'R-STATUS-1'):
            self.assertEqual(results[rule]['status'], 'passed', results[rule])
        css = self.project.paths['dist'] / 'assets/site.css'
        css.write_text(css.read_text() + '\n#changes td:nth-child(2) a,#changes td.dim{font-size:12px!important}'
                                          '\n.lead{color:var(--accent)}')
        results = {r['rule']: r for r in gate.browser(self.project.paths['dist'])}
        self.assertEqual(results['R-TYPE-1']['status'], 'failed')
        self.assertEqual(results['R-COLOR-1']['status'], 'failed')


class PortabilityTests(unittest.TestCase):
    def test_series_contains_no_client_identity(self):
        pattern = re.compile(r'(?i)telix|pixclara|telixpharma|\bSPM-\d|\bPTAM\b|\bNTAM\b')
        for name in ('review-site-kit', 'review-site', 'tracker-intake', 'moscow-story-map', 'decision-register'):
            for path in (ROOT / 'skills' / name).rglob('*'):
                if path.is_file():
                    self.assertIsNone(pattern.search(path.read_text(errors='ignore')), path)

    def test_built_package_runs_from_its_own_runtime(self):
        import catalog
        from portable import assemble, runtime_closure
        temp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, temp)
        package = temp / 'review-site'
        item = catalog.entries(ROOT)['review-site']
        assemble(ROOT, item['source'], package, catalog.dependencies(ROOT, item, runtime_closure))
        catalog.apply_entrypoint(package, 'review-site', item)
        for needed in ('_runtime/review-site-kit/lib/rsk/render.py', '_runtime/prose-pass/scripts/writing_check.py',
                       '_runtime/brand-renderer/scripts/browser_launch_policy.cjs', 'references/estate/brand.md'):
            self.assertTrue((package / needed).is_file(), needed)
        project = Project(self, script=package / 'scripts/review_site.py')
        p = project.paths
        results = {r['rule']: r['status'] for r in gate.data(p['config'], p['content'], p['tickets'], p['dist'])}
        self.assertEqual(results, {'D1': 'passed', 'D2': 'passed', 'D3': 'passed', 'W1': 'passed'})


if __name__ == '__main__':
    unittest.main()
