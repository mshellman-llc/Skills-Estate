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
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from test_capabilities import integration
from catalog import source_names
MAP = ROOT / 'artifacts' / 'skills-map'
spec = importlib.util.spec_from_file_location('map_builder', MAP / 'build.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

class DownloadVariantTests(unittest.TestCase):
    def render(self, downloads):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)/'map.html'
            builder.render_snapshot({'skills': []}, out, downloads=downloads)
            return out.read_text()

    def test_default_build_keeps_download_controls(self):
        page = self.render(True)
        self.assertIn('id="export"', page)
        self.assertIn('data-download', page)
        self.assertNotIn('downloads-->', page)
        self.assertNotIn('downloads*/', page)

    def test_artifact_build_has_no_download_controls_or_code(self):
        page = self.render(False)
        for text in ('id="export"', 'data-download', 'packageDownload', 'function download(', '.download=', 'downloads-->', 'downloads*/'):
            self.assertNotIn(text, page)
        self.assertIn('id="print-map"', page)
        self.assertIn('data-print-detail', page)

class SkillsMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='estate-map-fixture-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.output = Path(cls.temp.name)/'index.html'
        baseline=Path(cls.temp.name)/'baseline';baseline.mkdir()
        for command in (['init','-q'],['commit','-q','--allow-empty','-m','Synthetic baseline'],
                        ['update-ref','refs/remotes/fixture/main','HEAD']):
            subprocess.run(['git','-C',str(baseline),*command],env={**os.environ,**GIT_ENV},
                           capture_output=True,text=True,check=True)
        # Exercise the real builder against current source without overwriting
        # the committed snapshot or depending on its last regeneration date.
        with contextlib.redirect_stdout(io.StringIO()):
            cls.data = builder.build(argparse.Namespace(repo=ROOT,baseline_repo=baseline,
                base='HEAD',published_ref='refs/remotes/fixture/main',extra=[],output=cls.output))

    def test_all_canonical_skills_appear_once(self):
        expected = source_names(ROOT)
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
        text = self.output.read_text()
        embedded = re.search(r'<script type="application/json" id="estate-data">(.*?)</script>', text, re.S)[1]
        self.assertEqual(json.loads(embedded), self.data)
        self.assertNotIn('<', embedded)

    @integration('generated-map')
    def test_committed_snapshot_matches_current_source_inventory(self):
        snapshot=json.loads((MAP/'index.json').read_text())
        expected={s['id']:s for s in self.data['skills']}
        actual={s['id']:s for s in snapshot['skills']}
        instruction='Generated map is stale. Rebuild artifacts/skills-map/build.py from the intended published baseline.'
        self.assertEqual(set(expected),set(actual),instruction)
        for name,skill in expected.items():
            with self.subTest(skill=name):
                for field in ('markdown','sourceSha256','resources','examples'):
                    self.assertEqual(skill[field],actual[name][field],instruction)
        html=(MAP/'index.html').read_text()
        embedded=re.search(r'<script type="application/json" id="estate-data">(.*?)</script>',html,re.S)[1]
        self.assertEqual(json.loads(embedded),snapshot,'Generated HTML and JSON disagree')

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

    def test_connection_tables_show_only_the_matching_row(self):
        source='| Need | Reference |\n| --- | --- |\n| General advice | Other reference |\n| Saved files | [Diagnostic toolkit](../prose-pass/SKILL.md) |\n| Another topic | Unrelated reference |'
        excerpt=builder.connection_excerpt(source,re.search('prose-pass',source))
        self.assertEqual(excerpt['context'],'| Saved files | [Diagnostic toolkit](../prose-pass/SKILL.md) |')
        self.assertIn('<table>',excerpt['contextHtml'])
        self.assertIn('<th scope="col">Need</th>',excerpt['contextHtml'])
        self.assertIn('<td>Saved files</td>',excerpt['contextHtml'])
        self.assertNotIn('Other reference',excerpt['contextHtml'])
        self.assertNotIn('Unrelated reference',excerpt['contextHtml'])

    def test_connection_prose_renders_links_lists_and_escapes_source_html(self):
        source='Use **prose-pass** for diagnostics.\n\n<script>prose-pass</script>'
        excerpt=builder.connection_excerpt(source,re.search('prose-pass',source))
        self.assertTrue(excerpt['context'].startswith('Use '))
        self.assertIn('<strong>prose-pass</strong>',excerpt['contextHtml'])
        unsafe=builder.connection_excerpt(source,list(re.finditer('prose-pass',source))[1])
        self.assertNotIn('<script>',unsafe['contextHtml'])

    def test_removed_blocks_stay_absent_from_readable_and_raw_sources(self):
        for skill in self.data['skills']:
            with self.subTest(skill=skill['id']):
                self.assertNotIn('ESTATE-WRITING:',skill['html'])
                self.assertNotIn('build-card.md',skill['excerptHtml'])
                self.assertNotIn('ESTATE-WRITING:',skill['markdown'])

    def test_catalog_roles_match_primary_mode_and_internal_ownership(self):
        catalog=json.loads((ROOT/'config/skill-catalog.json').read_text())
        primary={item['source'] for item in catalog['entries'].values()}
        modes={module for item in catalog['entries'].values() for module in item.get('modes',{}).values()}
        for skill in self.data['skills']:
            expected='task' if skill['id'] in primary else 'mode' if skill['id'] in modes else 'support'
            self.assertEqual(skill['catalogRole']['kind'],expected)

def example_text(skill='ddoc', source='fictional', sha='0'*64, extra='', sections=('## Request','## Output')):
    head=f'---\nskill: {skill}\ntitle: Sample run\nsource: {source}\nmodel: test-model\ndate: 2026-11-04\nskillSha256: {sha}\n{extra}---\n'
    return head+''.join(f'{s}\n\nText.\n\n' for s in sections)

class ShowcaseTests(unittest.TestCase):
    def setUp(self):
        self._tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root=Path(self._tmp.name)

    def write(self, rel, text):
        path=self.root/rel
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(text)
        return path

    def test_examples_group_by_skill_and_flag_older_versions(self):
        self.write('showcase/ddoc/current.md',example_text(sha='a'*64))
        self.write('showcase/ddoc/older.md',example_text(sha='b'*64))
        self.write('showcase/ddoc/README.md','Not an example.\n')
        examples=builder.load_showcase(self.root,{'ddoc':'a'*64})
        by_id={x['id']:x for x in examples['ddoc']}
        self.assertEqual(set(by_id),{'current','older'})
        self.assertTrue(by_id['current']['current'])
        self.assertFalse(by_id['older']['current'])
        self.assertIn('<h3>Output</h3>',by_id['current']['html'])

    def test_real_examples_need_an_approver(self):
        self.write('showcase/ddoc/real.md',example_text(source='real-redacted'))
        with self.assertRaisesRegex(ValueError,'approvedBy'):
            builder.load_showcase(self.root,{'ddoc':'0'*64})
        self.write('showcase/ddoc/real.md',example_text(source='real-redacted',extra='approvedBy: Megan Shellman\n'))
        self.assertEqual(builder.load_showcase(self.root,{'ddoc':'0'*64})['ddoc'][0]['approvedBy'],'Megan Shellman')

    def test_malformed_examples_are_rejected(self):
        cases={'unknown skill':example_text(skill='nope'),'folder':example_text(skill='rom'),
               'source':example_text(source='imagined'),'sha':example_text(sha='short'),
               'section':example_text(sections=('## Request',))}
        for label,text in cases.items():
            with self.subTest(case=label):
                folder='nope' if label=='unknown skill' else 'ddoc'
                path=self.write(f'showcase/{folder}/case.md',text)
                with self.assertRaises(ValueError):
                    builder.load_showcase(self.root,{'ddoc':'0'*64,'rom':'0'*64})
                path.unlink()

    def test_example_output_cannot_execute_html(self):
        self.write('showcase/ddoc/x.md',example_text()+'<script>alert(1)</script>\n')
        html=builder.load_showcase(self.root,{'ddoc':'0'*64})['ddoc'][0]['html']
        self.assertNotIn('<script>',html)

    def test_examples_stay_out_of_skill_packages(self):
        # Examples are a repository showcase, not runtime material: no assembly module reads them.
        for module in ('estate','portable','plugins','catalog','releases'):
            with self.subTest(module=module):
                self.assertNotIn('showcase',(ROOT/'tools'/f'{module}.py').read_text())


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
