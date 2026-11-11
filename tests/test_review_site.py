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
KIT = ROOT / 'skills/review-site-runtime'
EXAMPLE = KIT / 'examples/northwind'
SITE = ROOT / 'skills/build-review-site/scripts/review_site.py'
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
        self.dir = Path(self.temp.name) / 'build-review-site'
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
        self.assertEqual(t['NW-21']['blocks'], ['NW-13', 'NW-22'])
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


class RegressionTests(unittest.TestCase):
    def config(self):
        return json.loads((EXAMPLE / 'config/site.json').read_text())

    def temp(self):
        folder = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, folder)
        return folder

    def test_json_adapter_keeps_only_schema_fields(self):
        path = self.temp() / 'pull.json'
        path.write_text(json.dumps({'tickets': [{'key': 'AB-1', 'summary': 'Login', 'status': 'Done', 'assignee': 'A Person',
                                                 'comments': ['private note'], 'description': '## Acceptance criteria\n- Logs in',
                                                 'reporter': 'B Person'}]}))
        config = {'tracker': {'adapter': 'json'}}
        doc, _ = tracker.load(path, config)
        text = json.dumps(doc)
        for private in ('A Person', 'B Person', 'private note', 'assignee', 'reporter', '"description"'):
            self.assertNotIn(private, text)
        self.assertEqual(doc['tickets'][0]['acceptance'], ['Logs in'])
        self.assertEqual(doc['tickets'][0]['comment_count'], 1)

    def test_same_export_is_reprocessed_after_a_status_map_change(self):
        folder = self.temp()
        rows = list(csv.reader(FIRST.read_text(encoding='utf-8').splitlines()))
        rows[5][rows[0].index('Status')] = 'Parked'
        export = folder / 'export.csv'
        with export.open('w', newline='') as handle:
            csv.writer(handle).writerows(rows)
        config = self.config()
        (folder / 'site.json').write_text(json.dumps(config))
        first = cli.intake(folder / 'site.json', export, folder / 'tracker', 'x', 'y')
        self.assertTrue(first['conflicts'])
        config['tracker']['status_map'] = {'Parked': 'blocked'}
        (folder / 'site.json').write_text(json.dumps(config))
        second = cli.intake(folder / 'site.json', export, folder / 'tracker', 'x', 'y')
        self.assertEqual(second['status'], 'recorded')
        self.assertEqual(second['changed'], 1)
        self.assertEqual(cli.intake(folder / 'site.json', export, folder / 'tracker', 'x', 'y')['status'], 'unchanged')

    def test_older_export_does_not_replace_a_newer_one(self):
        folder = self.temp()
        (folder / 'site.json').write_text(json.dumps(self.config()))
        cli.intake(folder / 'site.json', SECOND, folder / 'tracker', 'x', 'y')
        self.assertEqual(cli.intake(folder / 'site.json', FIRST, folder / 'tracker', 'x', 'y')['status'], 'failed')
        self.assertEqual(cli.intake(folder / 'site.json', FIRST, folder / 'tracker', 'x', 'y', allow_older=True)['status'], 'recorded')

    def test_numeric_parent_ids_and_subtasks(self):
        folder = self.temp()
        export = folder / 'export.csv'
        with export.open('w', newline='') as handle:
            w = csv.writer(handle)
            w.writerow(['Summary', 'Issue key', 'Issue id', 'Issue Type', 'Status', 'Parent', 'Description'])
            w.writerow(['Epic', 'AB-1', '500', 'Epic', 'To Do', '', ''])
            w.writerow(['Story', 'AB-2', '501', 'Story', 'To Do', '500', ''])
            w.writerow(['Task', 'AB-3', '502', 'Sub-task', 'To Do', '501', ''])
            w.writerow(['Orphan', 'AB-4', '503', 'Story', 'To Do', '999', ''])
        doc, warnings = tracker.load(export, {'tracker': {'adapter': 'jira-csv'}})
        t = {x['key']: x for x in doc['tickets']}
        self.assertEqual((t['AB-2']['parent'], t['AB-2']['epic']), ('AB-1', 'AB-1'))
        self.assertEqual((t['AB-3']['parent'], t['AB-3']['epic']), ('AB-2', 'AB-1'))
        self.assertIsNone(t['AB-4']['epic'])
        self.assertTrue(any('AB-4' in w for w in warnings))

    def test_wiki_nested_items_and_plain_headings(self):
        description = 'Acceptance Criteria:\n# The form saves.\n## Required fields are checked.\n# A number is shown.\n\nNotes:\nnot criteria'
        self.assertEqual(tracker.acceptance(description), ['The form saves.', '  Required fields are checked.', 'A number is shown.'])
        markdown = '## Acceptance criteria\n- Saves\n## Notes\n- other'
        self.assertEqual(tracker.acceptance(markdown, markup='markdown'), ['Saves'])

    def test_export_reviews_leaves_decision_exports_alone(self):
        project = Project(self)
        exports = project.dir / 'exports'
        exports.mkdir()
        (exports / 'decisions.csv').write_text('kept')
        reviews = self.temp() / 'moscow.json'
        reviews.write_text(json.dumps({'st-form': {'class': 'should'}}))
        script = ROOT / 'skills/build-moscow-story-map/scripts/story_map.py'
        p = project.paths
        result = run(script, 'export-reviews', '--config', p['config'], '--content', p['content'], '--tickets', p['tickets'],
                     '--reviews', reviews, '--out', exports)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((exports / 'decisions.csv').read_text(), 'kept')
        self.assertTrue((exports / 'class-reviews.csv').exists())

    def test_logo_in_a_subfolder_and_as_a_path(self):
        from rsk import brand
        folder = self.temp()
        (folder / 'assets').mkdir()
        (folder / 'assets/mark.svg').write_text('<svg viewBox="0 0 10 10"><rect width="10" height="10"/></svg>')
        for logo in ({'file': 'assets/mark.svg', 'alt': 'A & B "Co"'}, 'assets/mark.svg'):
            profile = {'name': 'Client', 'status': 'confirmed', 'colors': {'accent': '#123456'}, 'logo': logo}
            (folder / 'profile.json').write_text(json.dumps(profile))
            merged, base, missing = brand.load(folder / 'profile.json')
            markup = brand.logo(merged, base)
            self.assertIn('class="logo"', markup)
            self.assertNotIn('"Co"', markup)
            self.assertIn('text', missing)

    def test_structure_problems_are_reported(self):
        config = self.config()
        stories_doc = json.loads((EXAMPLE / 'content/stories.json').read_text())
        stories_doc['stories'].append(dict(stories_doc['stories'][0]))
        stories_doc['stories'].append({'id': 'bad id', 'label': 'x', 'step': 'intake', 'class': 'could',
                                       'tickets': ['NW-12'], 'depends_on': ['st-none'], 'roles': ['nobody']})
        tickets = {'NW-1': {'blocked_by': ['NW-2']}, 'NW-2': {'blocked_by': ['NW-1']}, 'NW-3': {'blocked_by': ['NW-3']}}
        questions_doc = {'groups': [], 'questions': []}
        found = ' | '.join(render.structure_problems(config, stories_doc, questions_doc, tickets))
        for expected in ('duplicate story id st-form', "id 'bad id'", 'primary ticket NW-11', 'primary ticket NW-12',
                         'unknown story st-none', 'unknown role nobody', 'Blocks cycle', 'NW-3 blocks itself'):
            self.assertIn(expected, found)

    def test_comments_use_one_subscription(self):
        page = (KIT / 'assets/site/decisions.js').read_text()
        self.assertEqual(page.count('store.list('), 1)
        self.assertNotIn('/items', page)


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
        self.assertEqual(json.loads((dist / 'manifest.json').read_text())['brand'], 'Neutral')

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
    def test_status_menu_works_by_keyboard(self):
        script = '''const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();
const errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto('file://'+process.argv[1]);await p.waitForTimeout(200);
await p.focus('.card-wrap .tag');await p.keyboard.press('ArrowDown');const expanded=await p.getAttribute('.card-wrap .tag','aria-expanded');
await p.keyboard.press('ArrowDown');await p.keyboard.press('Enter');await p.waitForTimeout(100);
const r=await p.evaluate(()=>({st:document.querySelector('.card-wrap .tag').dataset.st,menu:!!document.querySelector('.st-menu'),
focus:document.activeElement===document.querySelector('.card-wrap .tag'),inSummary:!!document.querySelector('summary .tag')}));
console.log(JSON.stringify({...r,expanded,errors}));await b.close();})();'''
        out = subprocess.run(['node', '-e', script, str(self.project.paths['dist'] / 'decisions.html')], capture_output=True, text=True)
        result = json.loads(out.stdout)
        self.assertEqual(result, {'st': 'Proposed', 'menu': False, 'focus': True, 'inSummary': False, 'expanded': 'true', 'errors': []})

    @integration('browser')
    def test_hostile_content_does_not_run(self):
        hostile = '<img src=x onerror="window.__pwned=1"></script><svg onload="window.__pwned=1">'
        p = self.project.paths
        for name in ('stories', 'questions', 'journeys', 'processes'):
            path = p['content'] / f'{name}.json'
            def poison(value):
                if isinstance(value, dict):
                    return {k: (hostile + v if isinstance(v, str) and k in fields and v not in enums else poison(v)) for k, v in value.items()}
                return [poison(v) for v in value] if isinstance(value, list) else value
            enums = {'Proposed answer', 'Answer'}
            fields = {'label', 'text', 'what', 'interim', 'context', 'lead', 'question', 'today', 'after', 'area', 'title'}
            path.write_text(json.dumps(poison(json.loads(path.read_text()))))
        result = cli.build(*self.args)
        self.assertEqual(result['status'], 'rendered', result)
        script = '''const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();let bad=0;
p.on('dialog',d=>{bad++;d.dismiss();});for(const f of process.argv.slice(1)){await p.goto('file://'+f);await p.waitForTimeout(200);
for(const sel of ['.chip','details.card summary','.tile','[data-panel]']){const el=await p.$(sel);if(el)await el.click();}
await p.waitForTimeout(100);if(await p.evaluate(()=>window.__pwned))bad++;}console.log(bad);await b.close();})();'''
        pages = [str(x) for x in sorted(p['dist'].glob('*.html'))]
        out = subprocess.run(['node', '-e', script, *pages], capture_output=True, text=True)
        self.assertEqual(out.stdout.strip(), '0', out.stderr)

    @integration('browser')
    def test_browser_rules_pass_and_catch_mixed_table_sizes(self):
        results = {r['rule']: r for r in gate.browser(self.project.paths['dist'])}
        for rule in ('R-ERR-1', 'R-LAYOUT-1', 'R-TYPE-1', 'R-FOLD-1', 'R-DEC-1', 'R-NUM-1', 'R-COLOR-1', 'R-TINT-1'):
            self.assertEqual(results[rule]['status'], 'passed', results[rule])
        css = self.project.paths['dist'] / 'assets/site.css'
        css.write_text(css.read_text() + '\n#changes td:nth-child(2) a,#changes td.dim{font-size:12px!important}'
                                          # The neutral accent is the text color, so give the
                                          # accent rule a distinct accent to police.
                                          '\n:root{--accent:#7B321A}.lead{color:var(--accent)}')
        results = {r['rule']: r for r in gate.browser(self.project.paths['dist'])}
        self.assertEqual(results['R-TYPE-1']['status'], 'failed')
        self.assertEqual(results['R-COLOR-1']['status'], 'failed')


class PortabilityTests(unittest.TestCase):
    # Hashed words from the engagement this series was first built for, so the
    # test can guard against them without spelling them out.
    FORBIDDEN = {'187bf09aede83421', '516591197179fc74', '88bdf61c0ac07844', 'b32fdf6db1469bd6', 'd1945071d3df3e11', 'd5656c9039b74e65'}

    def test_series_contains_no_client_identity(self):
        import hashlib
        for name in ('review-site-runtime', 'build-review-site', 'import-tracker-export', 'build-moscow-story-map', 'manage-decision-register'):
            for path in (ROOT / 'skills' / name).rglob('*'):
                if path.is_file():
                    words = set(re.findall(r'[a-z0-9]+', path.read_text(errors='ignore').lower()))
                    hits = {hashlib.sha256(w.encode()).hexdigest()[:16] for w in words} & self.FORBIDDEN
                    self.assertFalse(hits, path)

    def test_built_package_runs_from_its_own_runtime(self):
        import catalog
        from portable import assemble, runtime_closure
        temp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, temp)
        package = temp / 'build-review-site'
        item = catalog.entries(ROOT)['build-review-site']
        assemble(ROOT, item['source'], package, catalog.dependencies(ROOT, item, runtime_closure))
        catalog.apply_entrypoint(package, 'build-review-site', item)
        for needed in ('_runtime/review-site-runtime/lib/rsk/render.py', '_runtime/writing-diagnostics/scripts/writing_check.py',
                       '_runtime/brand-renderer/scripts/browser_launch_policy.cjs', 'references/estate/brand.md'):
            self.assertTrue((package / needed).is_file(), needed)
        project = Project(self, script=package / 'scripts/review_site.py')
        p = project.paths
        results = {r['rule']: r['status'] for r in gate.data(p['config'], p['content'], p['tickets'], p['dist'])}
        self.assertEqual(results, {'D1': 'passed', 'D2': 'passed', 'D3': 'passed', 'W1': 'passed'})


if __name__ == '__main__':
    unittest.main()
