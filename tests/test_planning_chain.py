"""Check the planning chain: each gate's selftest, the hand-off between them, packaging and provenance."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / 'skills'
sys.path.insert(0, str(ROOT / 'tools'))
from portable import assemble

SELFTESTS = [
    'refine-backlog/scripts/readiness_check_selftest.py',
    'plan-sprint/scripts/sprint_check_selftest.py',
    'prioritize-work/scripts/priority_score_selftest.py',
    'build-roadmap/scripts/outcome_check_selftest.py',
    'frame-jobs-to-be-done/scripts/jtbd_framing_selftest.py',
]
CHAIN_SKILLS = ['refine-backlog', 'plan-sprint', 'prioritize-work']


def run(*args, cwd=None):
    return subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True, cwd=cwd)


class PlanningChainTests(unittest.TestCase):
    def test_each_gate_selftest_passes(self):
        for relative in SELFTESTS:
            with self.subTest(selftest=relative):
                result = run(SKILLS / relative)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_readiness_report_feeds_the_sprint_gate(self):
        refinement = SKILLS / 'refine-backlog/scripts'
        sprint = SKILLS / 'plan-sprint/scripts'
        with tempfile.TemporaryDirectory() as temp:
            report = Path(temp) / 'readiness.json'
            graded = run(refinement / 'readiness_check.py', refinement / 'fixtures/requirements.csv',
                         '--raid-log', refinement / 'fixtures/RAID.md', '--format', 'json', '--output', report)
            self.assertEqual(graded.returncode, 1, 'the fixture holds items that are not ready')
            verdicts = {row['id']: row['verdict'] for row in json.loads(report.read_text())['items']}
            self.assertEqual(verdicts['ONB-001'], 'READY')
            self.assertEqual(verdicts['ONB-004'], 'DISCOVERY')
            planned = run(sprint / 'sprint_check.py', sprint / 'fixtures/plan_pass.json',
                          '--readiness', report, '--raid-log', sprint / 'fixtures/RAID.md')
            self.assertEqual(planned.returncode, 0, planned.stdout + planned.stderr)
            rejected = run(sprint / 'sprint_check.py', sprint / 'fixtures/plan_fail.json',
                           '--readiness', report, '--raid-log', sprint / 'fixtures/RAID.md')
            self.assertEqual(rejected.returncode, 1, rejected.stdout)

    def test_packages_carry_the_shared_chain_contract(self):
        with tempfile.TemporaryDirectory() as temp:
            for name in CHAIN_SKILLS:
                with self.subTest(skill=name):
                    package = Path(temp) / name
                    assemble(ROOT, name, package, [])
                    chain = list(package.rglob('planning-chain.md'))
                    self.assertTrue(chain, f'{name} package is missing planning-chain.md')
                    self.assertIn('refine-backlog', chain[0].read_text())

    def test_adapted_skills_record_provenance_and_license(self):
        declared = sorted(p.parent.name for p in SKILLS.glob('*/UPSTREAM.md'))
        self.assertEqual(declared, sorted(CHAIN_SKILLS + ['frame-jobs-to-be-done', 'build-roadmap']))
        for name in declared:
            with self.subTest(skill=name):
                skill = SKILLS / name
                self.assertTrue((skill / 'LICENSE-UPSTREAM').exists())
                rows = re.findall(r'^\| ([0-9a-f]{64}) \| (\S+) \|$', (skill / 'UPSTREAM.md').read_text(), re.M)
                self.assertTrue(rows, f'{name} UPSTREAM.md lists no adapted files')
                self.assertIn('Commons Clause', (skill / 'UPSTREAM.md').read_text())


class GateInputRegressionTests(unittest.TestCase):
    """Inputs from the independent review that once crashed, misfired or gave the wrong exit code."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name)

    def write(self, name, content):
        path = self.dir / name
        path.write_text(content if isinstance(content, str) else json.dumps(content))
        return path

    def gate(self, relative, *args):
        return run(SKILLS / relative, *args)

    def test_prioritization_reports_bad_items_without_aborting(self):
        script = 'prioritize-work/scripts/priority_score.py'
        mixed = self.write('mixed.json', [
            {'id': 'A', 'job': 'j', 'impact': 3, 'confidence': 0.5, 'ease': 5},
            {'id': 'B', 'job': 'j', 'impact': None, 'confidence': 0.5, 'ease': 5},
            {'id': 'C', 'job': 'j', 'impact': 3, 'confidence': '80%', 'ease': 5},
            {'id': 'D', 'job': 'j', 'impact': 1, 'confidence': 0.5, 'ease': 5},
            {'id': 'E', 'job': 'j', 'impact': 1, 'confidence': 0.5, 'ease': 4},
            {'id': 'F', 'job': 'j', 'impact': 1, 'confidence': 0.5, 'ease': 3}])
        result = self.gate(script, mixed, '--framework', 'ice', '--format', 'json')
        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(sorted(r['id'] for r in report['ranking']), ['A', 'D', 'E', 'F'])
        self.assertFalse(any('share the highest impact' in n for n in report['notes']),
                         'only scored items count toward the top-impact share')
        zero = self.write('zero.json', {'criteria': [{'name': 'x', 'weight': 0}], 'items': [{'id': 'A', 'job': 'j', 'scores': {'x': 1}}]})
        self.assertEqual(self.gate(script, zero, '--framework', 'weighted').returncode, 2)
        strings = self.write('strings.json', ['A', 'B'])
        self.assertEqual(self.gate(script, strings, '--framework', 'ice').returncode, 1)

    def test_sprint_gate_defaults_nulls_and_rejects_malformed_plans(self):
        script = 'plan-sprint/scripts/sprint_check.py'
        members = [{'name': 'A', 'working_days': None}, {'name': 'B', 'hours_per_day': None}, {'name': 'C'}]
        plan = {'goal': 'Ship import', 'items': [],
                'capacity': {'sprint_days': 10, 'hours_per_day': 8, 'focus_factor': 0.7, 'team_members': members}}
        result = self.gate(script, self.write('nulls.json', plan), '--format', 'json')
        self.assertEqual(json.loads(result.stdout)['capacity_hours'], 168.0)
        self.assertEqual(self.gate(script, self.write('list.json', [])).returncode, 2)
        plan['capacity']['team_members'] = [{'name': 'A', 'available_hours': 'abc'}]
        self.assertEqual(self.gate(script, self.write('text.json', plan)).returncode, 2)

    def test_readiness_gate_handles_scenarios_dependencies_and_empty_input(self):
        script = 'refine-backlog/scripts/readiness_check.py'
        header = 'Requirement Number,Name,As A,I Want To,So That,Acceptance Criteria,Estimate Days,Depends On\n'
        row = ('R-1,Import,an agency owner,import my client list in one step,'
               'my first invoice goes out the day I sign up,"Scenario: import\nGiven a client file\n\nWhen I import it\nThen every client appears",2,D-004 D-005\n')
        raid = self.write('RAID.md', '| D-004 | x |\n| D-005 | y |\n')
        result = self.gate(script, self.write('reqs.csv', header + row), '--raid-log', raid, '--format', 'json')
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(self.gate(script, self.write('empty.csv', '')).returncode, 2)
        self.assertEqual(self.gate(script, self.write('obj.json', {'foo': 1})).returncode, 2)
        self.assertEqual(self.gate(script, self.write('ints.json', [1, 2])).returncode, 2)

    def test_outcome_check_reads_numbers_dates_and_owners_precisely(self):
        script = 'build-roadmap/scripts/outcome_check.py'
        plan = {'kit': 1, 'id': 'x', 'meta': {'title': 't', 'source': 'example data'}, 'blocks': [{'type': 'board',
                'columns': [{'id': 'now'}, {'id': 'later'}],
                'cards': [{'id': 'n1', 'col': 'now', 'owner': 'Squad', 'fields': {'Outcome': 'Achieve SOC2 readiness'}},
                          {'id': 'n2', 'col': 'now', 'owner': None, 'fields': {'Outcome': 'Days 24 -> 14'}},
                          {'id': 'l1', 'col': 'later', 'title': 'Decrease 30% of churn across 5 marketplaces'}]}]}
        result = self.gate(script, self.write('plan.json', plan), '--format', 'json')
        findings = {(f['level'], f['card']) for f in json.loads(result.stdout)['findings']}
        self.assertIn(('fail', 'n1'), findings)
        self.assertIn(('warn', 'n2'), findings)
        self.assertNotIn(('warn', 'l1'), findings)
        self.assertEqual(self.gate(script, self.write('list.json', [])).returncode, 2)

    def test_drift_check_reads_variant_rows_and_reports_malformed_ones(self):
        root, upstream = self.dir / 'root', self.dir / 'up'
        (root / 'skills/x').mkdir(parents=True)
        upstream.mkdir()
        rows = []
        for name, form in (('a.md', '| {h} | a.md |'), ('b.md', '| {H} | b.md |'), ('c.md', '| {h} | `c.md` |'), ('d.md', '| {h} | d.md | note |')):
            (upstream / name).write_text(name)
            digest = hashlib.sha256(name.encode()).hexdigest()
            rows.append(form.format(h=digest, H=digest.upper()))
        (root / 'skills/x/UPSTREAM.md').write_text('\n'.join(rows) + '\n')
        sys.path.insert(0, str(ROOT / 'tools'))
        import upstream_drift
        checked = upstream_drift.compare(upstream_drift.declared(root), upstream)
        self.assertEqual([r['state'] for r in checked], ['unchanged'] * 4)
        (root / 'skills/x/UPSTREAM.md').write_text('| abcdef0123456789abcdef0123456789abc | bad.md |\n')
        self.assertTrue(any(r['state'] == 'malformed' for r in upstream_drift.declared(root)))


if __name__ == '__main__':
    unittest.main()
