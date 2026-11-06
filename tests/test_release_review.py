"""Check release-review status and approval recording, and the shared-assembly exclusions."""
import datetime as dt
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import plugins
import release_review

# Modules that assemble or install plugins. None of them may read a file the shared hash skips.
ASSEMBLY = ('estate', 'portable', 'plugins', 'catalog', 'releases', 'brand', 'marketplace_guard',
            'promote_maintenance')


class SharedExclusionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ('policies', 'tools', 'config'):
            (self.root / name).mkdir()
        (self.root / 'policies/writing.md').write_text('Write plainly.\n')
        (self.root / 'tools/estate.py').write_text('# assembly\n')
        (self.root / 'tools/browse.py').write_text('# pages\n')
        (self.root / 'config/skill-guide.json').write_text('{}\n')
        self.settings = {'format': 1, 'bundles': {}, 'release': {'shared': {}}}

    def digest(self):
        return plugins.shared_hash(self.root, self.settings)

    def test_excluded_files_do_not_change_the_shared_hash(self):
        before = self.digest()
        (self.root / 'tools/browse.py').write_text('# pages, edited\n')
        (self.root / 'config/skill-guide.json').write_text('{"edited": true}\n')
        (self.root / 'tools/__pycache__').mkdir()
        (self.root / 'tools/__pycache__/estate.cpython-312.pyc').write_bytes(b'cache')
        self.settings['release']['shared'] = {'status': 'accepted'}
        self.assertEqual(self.digest(), before)

    def test_showcase_examples_do_not_change_the_shared_hash(self):
        before = self.digest()
        (self.root / 'showcase/prepare-sales-pursuit').mkdir(parents=True)
        (self.root / 'showcase/prepare-sales-pursuit/example.md').write_text('An example run.\n')
        self.assertEqual(self.digest(), before)

    def test_policy_tool_and_routing_changes_still_change_it(self):
        before = self.digest()
        (self.root / 'policies/writing.md').write_text('Write plainly. Cite sources.\n')
        self.assertNotEqual(self.digest(), before)
        middle = self.digest()
        (self.root / 'tools/estate.py').write_text('# assembly, edited\n')
        self.assertNotEqual(self.digest(), middle)
        late = self.digest()
        self.settings['bundles'] = {'estate-x': {'entries': ['task']}}
        self.assertNotEqual(self.digest(), late)

    def test_no_assembly_module_reads_an_excluded_file(self):
        excluded_tools = {Path(p).stem for p in plugins.SHARED_EXCLUDED if p.startswith('tools/')}
        excluded_config = {Path(p).name for p in plugins.SHARED_EXCLUDED
                           if p.startswith('config/') and p != 'config/plugin-bundles.json'}
        for module in ASSEMBLY:
            with self.subTest(module=module):
                source = (ROOT / 'tools' / f'{module}.py').read_text()
                if module == 'plugins':
                    source = re.sub(r'SHARED_EXCLUDED = frozenset\(\{.*?\}\)', '', source, flags=re.S)
                imported = set(re.findall(r'^\s*(?:import|from)\s+(\w+)', source, re.M))
                self.assertEqual(sorted(imported & excluded_tools), [])
                self.assertEqual(sorted(n for n in excluded_config if n in source), [])


class ReleaseReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ('policies', 'tools', 'config', 'agents', 'skills/alpha', 'skills/beta'):
            (self.root / name).mkdir(parents=True)
        (self.root / 'policies/writing.md').write_text('Write plainly.\n')
        (self.root / 'skills/alpha/SKILL.md').write_text('alpha\n')
        (self.root / 'skills/beta/SKILL.md').write_text('beta\n')
        (self.root / 'agents/delivery-router.md').write_text('router\n')
        settings = {'format': 1, 'bundles': {}, 'release': {
            'shared': {'status': 'pending'},
            'modules': {'alpha': {'status': 'pending'}, 'beta': {'status': 'pending'}},
            'routers': {'delivery-router': {'status': 'pending'}}}}
        self.save(settings)

    def save(self, settings):
        (self.root / release_review.SETTINGS).write_text(json.dumps(settings, indent=2) + '\n')

    def states(self):
        return {(r['kind'], r['name']): r['state'] for r in release_review.status(self.root)}

    def test_new_subjects_are_pending(self):
        self.assertEqual(set(self.states().values()), {'pending'})

    def test_accept_records_only_named_subjects_with_dated_evidence(self):
        changed = release_review.accept(self.root, {('module', 'alpha')}, 'Example Maintainer',
                                        'Read the alpha diff', today=dt.date(2026, 11, 4))
        self.assertEqual([c['name'] for c in changed], ['alpha'])
        states = self.states()
        self.assertEqual(states[('module', 'alpha')], 'current')
        self.assertEqual(states[('module', 'beta')], 'pending')
        self.assertEqual(states[('shared', 'shared assembly')], 'pending')
        review = release_review.load(self.root)['release']['modules']['alpha']
        self.assertEqual(review['evidence'], 'Owner approval by Example Maintainer on 2026-11-04. Basis: Read the alpha diff')

    def test_changed_bytes_make_an_accepted_subject_stale(self):
        release_review.accept(self.root, {('module', 'alpha'), ('router', 'delivery-router')}, 'Example Maintainer', 'Read both')
        (self.root / 'skills/alpha/SKILL.md').write_text('alpha, edited\n')
        states = self.states()
        self.assertEqual(states[('module', 'alpha')], 'stale')
        self.assertEqual(states[('router', 'delivery-router')], 'current')
        self.assertEqual(release_review.main(['--root', str(self.root), 'status']), 1)

    def test_accepting_a_current_subject_changes_nothing(self):
        release_review.accept(self.root, {('module', 'alpha')}, 'Example Maintainer', 'First review', today=dt.date(2026, 11, 1))
        self.assertEqual(release_review.accept(self.root, {('module', 'alpha')}, 'Example Maintainer', 'Again'), [])
        evidence = release_review.load(self.root)['release']['modules']['alpha']['evidence']
        self.assertIn('2026-11-01', evidence)

    def test_refuses_missing_approver_evidence_or_subjects(self):
        for approver, evidence, subjects in (('', 'Read it', {('module', 'alpha')}),
                                             ('Example Maintainer', ' ', {('module', 'alpha')}),
                                             ('Example Maintainer', 'Read it', set()),
                                             ('Example Maintainer', 'Read it', {('module', 'gamma')})):
            with self.subTest(approver=approver, evidence=evidence, subjects=subjects):
                with self.assertRaises(ValueError):
                    release_review.accept(self.root, subjects, approver, evidence)
        self.assertEqual(set(self.states().values()), {'pending'})

    def test_stale_option_never_accepts_pending_subjects(self):
        release_review.accept(self.root, {('module', 'alpha')}, 'Example Maintainer', 'Read alpha')
        (self.root / 'skills/alpha/SKILL.md').write_text('alpha, edited\n')
        code = release_review.main(['--root', str(self.root), 'accept', '--approved-by', 'Example Maintainer',
                                    '--evidence', 'Read the alpha change', '--stale'])
        self.assertEqual(code, 0)
        states = self.states()
        self.assertEqual(states[('module', 'alpha')], 'current')
        self.assertEqual(states[('module', 'beta')], 'pending')
        self.assertEqual(states[('shared', 'shared assembly')], 'pending')

    def test_cli_requires_evidence(self):
        with self.assertRaises(SystemExit):
            release_review.main(['--root', str(self.root), 'accept', '--approved-by', 'Example Maintainer', '--module', 'alpha'])


class BundleSubjectTests(unittest.TestCase):
    def test_bundle_covers_its_modules_and_router(self):
        settings = release_review.load(ROOT)
        bundle = sorted(settings['bundles'])[0]
        subjects = release_review.bundle_subjects(ROOT, settings, bundle)
        self.assertTrue(subjects)
        known = set(release_review.digests(ROOT, settings))
        self.assertEqual(sorted(subjects - known), [])
        with self.assertRaises(ValueError):
            release_review.bundle_subjects(ROOT, settings, 'estate-missing')


if __name__ == '__main__':
    unittest.main()
