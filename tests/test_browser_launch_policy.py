"""Exercise browser selection with a fake launcher; never start a browser."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import ast

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from portable import assemble, runtime_closure


class BrowserLaunchPolicyTests(unittest.TestCase):
    def test_installed_chrome_is_rejected_before_launch(self):
        node = os.environ.get('ESTATE_NODE') or shutil.which('node')
        self.assertTrue(node, 'Node is required for the synthetic policy check')
        script = r'''
const assert = require('node:assert/strict');
const fs = require('node:fs'), os = require('node:os'), path = require('node:path');
const {launchOptions} = require(process.argv[1]);
let launches = 0;
const fake = {launch(options) { launches++; return options; }};
for (const env of [
  {PW_CHROMIUM:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'},
  {PW_CHROMIUM:'/Applications/../Applications/Google Chrome.app/Contents/MacOS/Google Chrome'},
  {PW_CHROMIUM:'/Users/example/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary'},
  {PLAYWRIGHT_CHANNEL:'chrome'}, {PLAYWRIGHT_CHANNEL:'chrome-beta'}
]) assert.throws(() => fake.launch(launchOptions(env)), /disabled/);
assert.equal(launches, 0);
const folder = fs.mkdtempSync(path.join(os.tmpdir(), 'estate-browser-policy-'));
try {
  const app = path.join(folder, 'Google Chrome.app'); fs.mkdirSync(app);
  const binary = path.join(app, 'fake'); fs.writeFileSync(binary, 'fixture');
  const alias = path.join(folder, 'renamed-browser'); fs.symlinkSync(binary, alias);
  assert.throws(() => fake.launch(launchOptions({PW_CHROMIUM:alias})), /disabled/);
  assert.equal(launches, 0);
} finally {fs.rmSync(folder, {recursive:true, force:true});}
assert.deepEqual(fake.launch(launchOptions({})), {headless:true});
assert.deepEqual(launchOptions({PLAYWRIGHT_CHANNEL:'chromium'}), {headless:true});
assert.equal(launches, 1); // This is the fake function, not Playwright.
console.log('Synthetic checks passed; no browser imported or launched.');
'''
        result = subprocess.run(
            [node, '-e', script, str(ROOT / 'skills/render-offering-brief/scripts/browser_launch_policy.cjs')],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_repository_harnesses_use_the_guard(self):
        for name in ['tests/test_journey_map_render.py', 'tests/test_roadmap_kit.py',
                     'artifacts/skills-map/verify.cjs',
                     'skills/render-offering-brief/scripts/render_pdf.mjs',
                     'skills/build-deck/scripts/check_html.mjs',
                     'skills/compare-scope-options/scripts/check_scope.mjs',
                     'skills/build-interactive-proposal/scripts/qa_proposal.mjs',
                     'skills/assess-solution-delivery/scripts/qa_field_guide.mjs',
                     'skills/prepare-sales-pursuit/scripts/build_brief.py']:
            with self.subTest(path=name):
                text = (ROOT / name).read_text()
                self.assertIn('launchOptions()', text)
                self.assertNotIn("||'chrome'", text)
                self.assertNotIn('executablePath:process.env.PW_CHROMIUM', text)

    def test_source_and_portable_launchers_refuse_before_fake_browser(self):
        node = os.environ.get('ESTATE_NODE') or shutil.which('node')
        self.assertTrue(node)
        modules = {'build-deck': 'check_html.mjs', 'compare-scope-options': 'check_scope.mjs',
                   'build-interactive-proposal': 'qa_proposal.mjs', 'assess-solution-delivery': 'qa_field_guide.mjs',
                   'render-offering-brief': 'render_pdf.mjs', 'prepare-sales-pursuit': None}
        with tempfile.TemporaryDirectory(prefix='estate-browser-entrypoints-') as temp:
            base = Path(temp)
            marker = base / 'browser-called'
            fake = base / 'fake-playwright.mjs'
            fake.write_text("import fs from 'node:fs'; export const chromium = {launch() {fs.writeFileSync(process.env.BROWSER_MARKER, 'called'); throw new Error('Fake launcher was reached');}};")
            source = base / 'input.html'; source.write_text('<main>Synthetic input</main>')
            plan = base / 'plan.json'; plan.write_text('{}')
            for module, script in modules.items():
                package = base / module
                assemble(ROOT, module, package, runtime_closure(ROOT, module))
                for layout, folder in [('source', ROOT / 'skills' / module), ('portable', package)]:
                    with self.subTest(module=module, layout=layout):
                        out = base / (module + '-' + layout)
                        policy = (ROOT / 'skills/brand-renderer/scripts/browser_launch_policy.cjs'
                                  if layout == 'source' else package / '_runtime/brand-renderer/scripts/browser_launch_policy.cjs')
                        env = {**os.environ, 'PW_MODULE': fake.as_uri(),
                               'PW_CHROMIUM': '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                               'BROWSER_MARKER': str(marker), 'ESTATE_BROWSER_POLICY': policy.as_uri()}
                        if module == 'prepare-sales-pursuit':
                            tree = ast.parse((folder / 'scripts/build_brief.py').read_text())
                            body = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                                        and any(isinstance(t, ast.Name) and t.id == 'VERIFY_JS' for t in n.targets))
                            runner = base / (layout + '-call-prep.mjs'); runner.write_text(body)
                            args = [str(source), str(out)]
                        else:
                            runner = folder / 'scripts' / script
                            args = [source.as_uri(), str(out), str(plan)]
                            if module == 'render-offering-brief': args = [str(source), str(out.with_suffix('.pdf')), '1']
                        if module in ('build-interactive-proposal', 'assess-solution-delivery'): out.mkdir()
                        result = subprocess.run([node, str(runner), *args], env=env, capture_output=True, text=True)
                        diagnostics = result.stdout + result.stderr
                        for report in base.rglob('*.json'):
                            if report.parent == out or report.name.startswith(out.name + '.'):
                                diagnostics += report.read_text(errors='replace')
                        self.assertNotEqual(result.returncode, 0, diagnostics)
                        self.assertIn('disabled', diagnostics)
                        self.assertFalse(marker.exists(), 'The fake browser must never be invoked')
