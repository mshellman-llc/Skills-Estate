"""Roadmap components in single-file estate pages: profile-only styling, evidence numbers and host wiring."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / 'skills/roadmap-artifacts'
sys.path.insert(0, str(KIT / 'scripts'))
import rk_embed  # noqa: E402
from build import check  # noqa: E402


def brand_check(path):
    return subprocess.run([sys.executable, str(ROOT / 'skills/brand-renderer/scripts/brand_check.py'), str(path)],
                          cwd=ROOT, capture_output=True, text=True)


def plan(**extra):
    base = {'kit': 1, 'id': 'test', 'persist': False, 'meta': {'title': 'Synthetic test'},
            'blocks': [{'type': 'callouts', 'items': [{'title': 'One', 'cite': [1]}]},
                       {'type': 'evidence', 'items': ['Hypothesis · synthetic']}]}
    base.update(extra)
    return base


class EstateStylesheetTests(unittest.TestCase):
    def test_stylesheet_uses_profile_roles_only(self):
        css = rk_embed.estate_css()
        self.assertEqual(re.findall(r'#[0-9a-fA-F]{3,8}\b', css), [])
        self.assertNotRegex(css, r'@import|https?:|url\(')
        self.assertEqual(set(re.findall(r'var\(--brand-([a-z0-9-]+)\)', css)) - rk_embed.CORE, set())
        self.assertNotRegex(css, r'border(?:-top|-left|-right|-bottom)?:\s*2px')
        self.assertNotRegex(css, r'border-radius:\s*[1-9]\d*px')

    def test_text_on_color_follows_profile_contrast(self):
        dark = {'background': '#FFFFFF', 'text': '#111111', 'accent': '#0B2A4A', 'chart-1': '#0B2A4A'}
        css = rk_embed.estate_css(dark)
        self.assertIn('--rk-on-accent: var(--brand-background)', css)
        self.assertIn('--rk-chart-1-on: var(--brand-background)', css)
        light = dict(dark, **{'chart-1': '#FAE69F'})
        self.assertIn('--rk-chart-1-on: var(--brand-text)', rk_embed.estate_css(light))

    def test_status_roles_are_reported_when_missing(self):
        self.assertEqual(rk_embed.status_report({'status-good': '#0CA30C', 'status-warning': '#FAB219',
                                                 'status-critical': '#D03B3B'}), [])
        self.assertEqual(len(rk_embed.status_report({})), 3)


class PlanCheckTests(unittest.TestCase):
    def test_cites_need_entries(self):
        self.assertEqual(check(plan()), [])
        broken = plan()
        broken['blocks'][0]['items'][0]['cite'] = [2]
        self.assertTrue(any('cite 2' in e for e in check(broken)))
        two = plan()
        two['blocks'].append({'type': 'evidence', 'items': ['x']})
        self.assertTrue(any('one evidence block' in e for e in check(two)))

    def test_standalone_page_refuses_cites_without_a_list_and_live_bindings(self):
        no_list = plan(blocks=[{'type': 'callouts', 'items': [{'title': 'One', 'cite': [1]}]}])
        with self.assertRaisesRegex(ValueError, 'evidence block'):
            rk_embed.build_page(no_list)
        live = json.loads((KIT / 'examples/06-sheets-live.json').read_text())
        with self.assertRaisesRegex(ValueError, 'live bindings'):
            rk_embed.build_page(live)


class PageTests(unittest.TestCase):
    def test_examples_build_to_pages_that_pass_the_brand_check(self):
        with tempfile.TemporaryDirectory() as folder:
            for example in sorted((KIT / 'examples').glob('0[1-5]-*.json')):
                data = json.loads(example.read_text())
                for mode in ('relaxed', 'compact', 'editorial'):
                    data['meta']['mode'] = mode
                    out = Path(folder) / f'{example.stem}-{mode}.html'
                    document, resource, notes = rk_embed.build_page(data)
                    self.assertEqual(resource['name'], 'Baseline')
                    self.assertEqual(notes, [])
                    self.assertNotIn('__RK_', document)
                    out.write_text(document)
                    result = brand_check(out)
                    self.assertEqual(result.returncode, 0, out.name + result.stdout)

    def test_pages_render_without_network_or_errors(self):
        node = os.environ.get('ESTATE_NODE') or shutil.which('node')
        self.assertTrue(node, 'Node is required')
        jtbd = (ROOT / 'skills/jtbd-framing/references/rendering-with-roadmap-components.md').read_text()
        worked = json.loads(re.search(r'```json\n(.*?)\n```', jtbd, re.S)[1])
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            pages = {'jtbd': worked, 'timeline': json.loads((KIT / 'examples/05-raid.json').read_text())}
            for name, data in pages.items():
                (base / f'{name}.html').write_text(rk_embed.build_page(data)[0])
            runner = base / 'check.cjs'
            runner.write_text(r"""
const {chromium}=require('playwright'),assert=require('assert/strict'),url=require('url'),path=require('path');
(async()=>{const b=await chromium.launch({headless:true,executablePath:process.env.PW_CHROMIUM||undefined});
try {for (const [name,check] of [['jtbd',async p=>{
  assert.equal(await p.locator('.rk-evidence li').count(),2);
  assert.equal(await p.locator('.rk-ref[href="#ev-1"]').count(),3);
  assert.equal(await p.locator('#ev-2').count(),1);
  assert.equal(await p.locator('.rk-col-title span').first().innerText(),'1 item');
 }],['timeline',async p=>{assert.ok(await p.locator('.rk-tl-bar').count()>0);}]]) {
  const p=await b.newPage({viewport:{width:1280,height:900}});const errors=[];let remote=0;
  p.on('pageerror',e=>errors.push(e.message));
  await p.route('**/*',r=>{if(r.request().url().startsWith('file:'))r.continue();else{remote++;r.abort();}});
  await p.goto(url.pathToFileURL(path.join(process.argv[2],name+'.html')).href);
  await check(p);
  assert.deepEqual(errors,[]);assert.equal(remote,0);
  await p.setViewportSize({width:390,height:844});await p.reload();
  assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,name+' scrolls sideways');
  await p.close();}
} finally {await b.close();}})().catch(e=>{console.error(e);process.exit(1)});
""", encoding='utf-8')
            result = subprocess.run([node, str(runner), str(base)], capture_output=True, text=True, env=os.environ.copy())
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_proposal_draws_quoted_phases_on_a_week_axis(self):
        node = os.environ.get('ESTATE_NODE') or shutil.which('node')
        skill = ROOT / 'skills/interactive-proposal'
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / 'proposal.html'
            build = subprocess.run([sys.executable, str(skill / 'scripts/build_proposal.py'), str(skill / 'fixtures/proposal.json'),
                                    '--quote', str(skill / 'fixtures/quote.json'), '--output', str(out)],
                                   capture_output=True, text=True)
            self.assertEqual(build.returncode, 0, build.stderr)
            self.assertEqual(brand_check(out).returncode, 0)
            runner = Path(folder) / 'check.cjs'
            runner.write_text(r"""
const {chromium}=require('playwright'),assert=require('assert/strict'),url=require('url');
(async()=>{const b=await chromium.launch({headless:true,executablePath:process.env.PW_CHROMIUM||undefined});
try {const p=await b.newPage();const errors=[];p.on('pageerror',e=>errors.push(e.message));
await p.goto(url.pathToFileURL(process.argv[2]).href);
await p.locator('[role=tab]').last().click();
const labels=await p.locator('#timeline-chart .rk-tl-bar').evaluateAll(n=>n.map(x=>x.getAttribute('aria-label')));
assert.deepEqual(labels.map(l=>l.split(',').slice(0,2).join(',')),['Configure, week 1 to week 3','Validate, week 4 to week 6']);
assert.equal(await p.locator('#timeline').isVisible(),false);
assert.deepEqual(errors,[]);
} finally {await b.close();}})().catch(e=>{console.error(e);process.exit(1)});
""", encoding='utf-8')
            result = subprocess.run([node, str(runner), str(out)], capture_output=True, text=True, env=os.environ.copy())
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
