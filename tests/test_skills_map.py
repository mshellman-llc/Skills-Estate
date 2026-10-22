import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / 'artifacts' / 'skills-map'
spec = importlib.util.spec_from_file_location('map_builder', MAP / 'build.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

class SkillsMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((MAP / 'index.json').read_text())

    def test_all_canonical_skills_appear_once(self):
        expected = {p.parent.name for p in ROOT.glob('skills/*/SKILL.md')}
        actual = [s['id'] for s in self.data['skills']]
        self.assertEqual(set(actual), expected)
        self.assertEqual(len(actual), len(set(actual)))
        self.assertEqual(self.data['counts']['total'], len(expected))

    def test_exact_sources_and_resource_bytes_survive(self):
        for s in self.data['skills']:
            with self.subTest(skill=s['id']):
                folder = ROOT / 'skills' / s['id']
                raw = (folder / 'SKILL.md').read_bytes()
                self.assertEqual(s['markdown'].encode(), raw)
                self.assertEqual(s['sourceSha256'], hashlib.sha256(raw).hexdigest())
                self.assertEqual(s['resources'], builder.inventory(folder))
                self.assertIn(s['status'], {'github', 'local-revision', 'local-addition'})
                if s['status'] == 'github':
                    self.assertFalse(s['entrypointChanged'])
                if s['githubUrl'] is None:
                    self.assertEqual(s['status'], 'local-addition')

    def test_embedded_html_data_matches_json(self):
        text = (MAP/'index.html').read_text()
        embedded = re.search(r'<script type="application/json" id="estate-data">(.*?)</script>', text, re.S)[1]
        self.assertEqual(json.loads(embedded), self.data)
        self.assertNotIn('<', embedded)

    def test_connections_have_source_evidence(self):
        names={s['id'] for s in self.data['skills']}
        for s in self.data['skills']:
            for mention in s['mentions']:
                self.assertIn(mention['name'], names)
                self.assertIn(mention['name'], mention['context'])
                self.assertIn(mention['context'], s['markdown'])

    def test_markdown_cannot_execute_source_html_or_script_urls(self):
        rendered=builder.markdown('<script>alert(1)</script>\n\n[bad](javascript:alert)\n\n[good](https://example.com)')
        self.assertNotIn('<script>', rendered)
        self.assertNotIn('href="javascript:', rendered)
        self.assertIn('href="https://example.com"', rendered)

    def test_markdown_keeps_tables_and_code(self):
        rendered=builder.markdown('| Name | State |\n| --- | --- |\n| Scope | Draft |\n\n```sh\necho "safe"\n```')
        self.assertIn('<table>', rendered)
        self.assertIn('<td>Draft</td>', rendered)
        self.assertIn('echo &quot;safe&quot;', rendered)

GIT_ENV = {'GIT_AUTHOR_NAME': 't', 'GIT_AUTHOR_EMAIL': 't@example.invalid',
           'GIT_COMMITTER_NAME': 't', 'GIT_COMMITTER_EMAIL': 't@example.invalid',
           'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_SYSTEM': os.devnull}

def skill_text(name, extra=''):
    return f'---\nname: {name}\ndescription: Fixture {name}.\n---\n# {name}\n\nBody paragraph.{extra}\n'

class SourceStateComparisonTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.repo = self.tmp / 'repo'
        self.repo.mkdir()
        self.git('init', '-q')
        self.write({'skills/ddoc/SKILL.md': skill_text('ddoc'), 'skills/ddoc/references/a.md': 'a\n',
                    '.hidden-root': 'x\n'}, self.repo)
        self.base = self.commit('base')
        self.publish(self.base)

    def git(self, *args, repo=None):
        env = {**os.environ, **GIT_ENV}
        return subprocess.check_output(['git', '-C', str(repo or self.repo), *args], env=env, stderr=subprocess.DEVNULL).decode().strip()

    def write(self, files, repo=None):
        for rel, text in files.items():
            path = (repo or self.repo) / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)

    def commit(self, message, repo=None):
        self.git('add', '-A', repo=repo)
        self.git('commit', '-q', '-m', message, repo=repo)
        return self.git('rev-parse', 'HEAD', repo=repo)

    def publish(self, sha, ref='refs/remotes/origin/main', repo=None):
        self.git('update-ref', ref, sha, repo=repo)

    def run_build(self, base='unset', published_ref=builder.DEFAULT_PUBLISHED_REF, baseline_repo=None, output=None):
        output = output or self.tmp / 'out' / 'map.html'
        args = argparse.Namespace(repo=self.repo, baseline_repo=baseline_repo, extra=[], output=output,
                                  base=self.base if base == 'unset' else base, published_ref=published_ref)
        with contextlib.redirect_stdout(io.StringIO()):
            data = builder.build(args)
        return {s['id']: s for s in data['skills']}

    def assert_rejected(self, **kwargs):
        output = self.tmp / 'rejected' / 'map.html'
        with self.assertRaises(ValueError):
            self.run_build(output=output, **kwargs)
        self.assertFalse(output.parent.exists())
        self.assertFalse(output.exists() or output.with_suffix('.json').exists())

    def test_identical_tree_is_github(self):
        skill = self.run_build()['ddoc']
        self.assertEqual(skill['status'], 'github')
        self.assertFalse(skill['entrypointChanged'])

    def test_resource_only_revision(self):
        self.write({'skills/ddoc/references/a.md': 'changed\n'})
        skill = self.run_build()['ddoc']
        self.assertEqual(skill['status'], 'local-revision')
        self.assertFalse(skill['entrypointChanged'])

    def test_added_and_removed_resource_are_revisions(self):
        self.write({'skills/ddoc/references/new.md': 'n\n'})
        self.assertEqual(self.run_build()['ddoc']['status'], 'local-revision')
        (self.repo / 'skills/ddoc/references/new.md').unlink()
        (self.repo / 'skills/ddoc/references/a.md').unlink()
        self.assertEqual(self.run_build()['ddoc']['status'], 'local-revision')

    def test_entrypoint_revision(self):
        self.write({'skills/ddoc/SKILL.md': skill_text('ddoc', ' More.')})
        skill = self.run_build()['ddoc']
        self.assertEqual(skill['status'], 'local-revision')
        self.assertTrue(skill['entrypointChanged'])

    def test_addition_is_local_without_github_url(self):
        self.write({'skills/rom/SKILL.md': skill_text('rom')})
        skills = self.run_build()
        self.assertEqual(skills['rom']['status'], 'local-addition')
        self.assertIsNone(skills['rom']['githubUrl'])
        self.assertEqual(skills['ddoc']['status'], 'github')

    def test_hidden_and_cache_files_are_filtered_on_both_sides(self):
        # Hidden/cache files committed in the baseline and present locally do not make a revision.
        self.write({'skills/ddoc/.secret': 's\n', 'skills/ddoc/__pycache__/x.pyc': 'p\n',
                    'skills/ddoc/references/.hid': 'h\n', 'skills/ddoc/tool.pyc': 'p\n'})
        newer = self.commit('with hidden')
        self.publish(newer)
        skill = self.run_build(base=newer)['ddoc']
        self.assertEqual(skill['status'], 'github')
        self.assertEqual([r['path'] for r in skill['resources']], ['SKILL.md', 'references/a.md'])
        # Changing only filtered files locally is also not a revision.
        self.write({'skills/ddoc/.secret': 'changed\n', 'skills/ddoc/.new': 'n\n'})
        self.assertEqual(self.run_build(base=newer)['ddoc']['status'], 'github')

    def test_historical_published_ancestor_is_allowed(self):
        self.write({'skills/ddoc/references/a.md': 'later\n'})
        tip = self.commit('later')
        self.publish(tip)
        self.assertEqual(self.run_build(base=self.base)['ddoc']['status'], 'local-revision')

    def test_separate_baseline_repo(self):
        other = self.tmp / 'baseline'
        subprocess.check_call(['git', 'clone', '-q', str(self.repo), str(other)], env={**os.environ, **GIT_ENV}, stderr=subprocess.DEVNULL)
        self.publish(self.base, 'refs/remotes/origin/main', repo=other)
        self.write({'skills/ddoc/references/a.md': 'changed\n'})
        skill = self.run_build(baseline_repo=other)['ddoc']
        self.assertEqual(skill['status'], 'local-revision')

    def test_custom_published_ref(self):
        self.publish(self.base, 'refs/remotes/upstream/release')
        self.git('update-ref', '-d', 'refs/remotes/origin/main')
        self.assertEqual(self.run_build(published_ref='refs/remotes/upstream/release')['ddoc']['status'], 'github')

    def test_rejects_missing_base(self):
        self.assert_rejected(base=None)
        self.assert_rejected(base='')

    def test_rejects_unpublished_commit(self):
        self.write({'skills/ddoc/references/a.md': 'unpublished\n'})
        local = self.commit('local only')
        self.assert_rejected(base=local)

    def test_rejects_missing_published_ref(self):
        self.assert_rejected(published_ref='refs/remotes/origin/absent')
        self.git('update-ref', '-d', 'refs/remotes/origin/main')
        self.assert_rejected()

    def test_rejects_malformed_refs(self):
        for base in ['--output=x', 'a b', 'main..HEAD', 'not-a-commit', '0' * 40]:
            with self.subTest(base=base):
                self.assert_rejected(base=base)
        for ref in ['origin/main', 'refs/heads/main', 'refs/remotes/', 'refs/remotes/origin/ma..in', 'refs/remotes/origin/a b', '']:
            with self.subTest(published_ref=ref):
                self.assert_rejected(published_ref=ref)

if __name__ == '__main__':
    unittest.main()
