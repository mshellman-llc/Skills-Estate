"""Render the journey starter and exercise data failures in Chromium."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import unittest
import re
import tempfile
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from test_capabilities import integration

class JourneyMapRenderTests(unittest.TestCase):
    @integration("browser")
    def test_render_and_failure_cases(self):
        node = os.environ.get('ESTATE_NODE') or shutil.which('node')
        self.assertTrue(node, 'Node is required')
        out = ROOT / '.local/verification/journey-map'
        out.mkdir(parents=True, exist_ok=True)
        runner = out / 'check.cjs'
        runner.write_text(r'''
const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const {chromium} = require('playwright');
(async () => {
 const [source, out] = process.argv.slice(2);
 const html = fs.readFileSync(source, 'utf8');
 const browser = await chromium.launch(require(process.env.ESTATE_BROWSER_POLICY).launchOptions());
 const page = await browser.newPage({viewport:{width:1440,height:1100}});
 const errors=[]; page.on('pageerror', e => errors.push(e.message));
 const results=[];
 async function render(name, mutate='') {
  const body=html.replace('try {\nvalidateMap(MAP);', `${mutate}\ntry {\nvalidateMap(MAP);`);
  fs.writeFileSync(path.join(out,name+'.html'),body);
  await page.goto(require('url').pathToFileURL(path.join(out,name+'.html')).href);
 }
 try {
  await render('normal');
  assert.equal(await page.locator('[role=alert]').count(),0);
  assert.equal(await page.locator('.curve.hyp').count(),1);
  assert.equal(await page.locator('.hypothesis, .basis-tag').count(),0, 'Evidence is referenced, not labelled in every cell');
  assert.deepEqual(await page.locator('#evidence li').allTextContents(),['Thoughts: Hypothesis','Pain points: Hypothesis','Opportunity: Hypothesis · Synthetic example']);
  assert.equal(await page.locator('#grid .ref').count(),2);
  assert.equal(await page.locator('#opp-section .opp-list li').count(),3, 'Without the inlined components the opportunity map is a list');
  assert.equal(await page.locator('#opp-section .ref').count(),3);
  const order=await page.locator('#grid > .lab, #grid > .vis').allTextContents();
  assert.deepEqual(order.slice(-5),['Front-stage','Line of visibility','Back-stage','Line of internal interaction','Supporting']);
  assert.equal(await page.locator('.card').count(),3);
  assert.equal(await page.locator('.curve').getAttribute('points'),'50,66 150,91 250,66 350,116 450,41');
  assert.match(await page.locator('#basis').innerText(),/Synthetic example/);
  await page.screenshot({path:path.join(out,'desktop.png'),fullPage:true});
  results.push({case:'normal',passed:true});
  assert.equal(await page.locator('main').count(),1);
  await page.setViewportSize({width:390,height:844});
  await page.reload();
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  assert.equal(await page.locator('.board').evaluate(e=>e.scrollWidth>e.clientWidth),true);
  await page.locator('.board').evaluate(e=>e.scrollLeft=300);
  assert.ok(await page.locator('.board').evaluate(e=>e.scrollLeft)>0);
  await page.screenshot({path:path.join(out,'mobile.png'),fullPage:true});
  results.push({case:'mobile-scroll',passed:true});
  await render('evidence','MAP.emotionBasis="evidence"; MAP.rows[2].basis="reported"; MAP.rows[3].basis="observed";');
  assert.equal(await page.locator('.curve.hyp').count(),0);
  assert.deepEqual(await page.locator('#evidence li').allTextContents(),['Thoughts: Reported','Pain points: Observed','Opportunity: Hypothesis · Synthetic example']);
  assert.equal(await page.locator('.curve').count(),1);
  results.push({case:'evidence',passed:true});
  await render('unknown','MAP.emotion=null; MAP.emotionBasis="not captured"; MAP.blueprint[1].cells[0]=null; MAP.rows[2].cells[0]=null;');
  assert.equal(await page.locator('[role=alert]').count(),0);
  assert.equal(await page.locator('.curve').count(),0);
  assert.match(await page.locator('.emotion').innerText(),/Not captured/);
  assert.match(await page.locator('#grid').innerText(),/Not captured/);
  assert.equal(await page.locator('#evidence li').count(),3);
  const missingCells = await page.locator('#grid .cell').evaluateAll(cells => cells.filter(c => c.textContent === 'Not captured').length);
  assert.ok(missingCells >= 2, 'Missing values retain a single visible label');
  assert.equal(await page.locator('#evidence').innerText().then(t => /not captured/i.test(t)),false);
  results.push({case:'unknown',passed:true});
  await render('qualitative', 'MAP.emotion=null; MAP.emotionBasis="not captured"; MAP.emotionLabels=[{text:"Uncertain at intake",basis:"reported",source:"Agent A interview"},null,{text:"Relieved after account confirmation",basis:"reported",source:"Agent A interview"},null,{text:"Possible relief",basis:"hypothesis",source:"Validate after a confirmed fix"}];');
  assert.equal(await page.locator('[role=alert], .curve').count(),0);
  assert.equal(await page.locator('.feeling').count(),5);
  const feelings=await page.locator('.feeling').allTextContents();
  assert.match(feelings[0],/Uncertain at intake/);
  assert.match(feelings[2],/Relieved after account confirmation/);
  assert.equal(feelings[1],'Not captured');
  const evidenceText=await page.locator('#evidence').innerText();
  assert.match(evidenceText,/Feeling, phase 03: Reported · Agent A interview/);
  assert.match(evidenceText,/Feeling, phase 05: Hypothesis · Validate after a confirmed fix/);
  assert.equal(await page.locator('.feeling .ref').count(),3);
  assert.match(await page.locator('#legend').innerText(),/scores: not captured/);
  assert.ok((await page.locator('#grid > .lab').allTextContents()).includes('Emotion scores'));
  await page.setViewportSize({width:1440,height:1100});
  await page.reload();
  await page.screenshot({path:path.join(out,'qualitative-desktop.png'),fullPage:true});
  await page.setViewportSize({width:390,height:844});
  await page.reload();
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  await page.screenshot({path:path.join(out,'qualitative-mobile.png'),fullPage:true});
  results.push({case:'qualitative-without-scores',passed:true});
  await render('escaped-feeling', 'MAP.emotionLabels=[{text:"<img src=x onerror=alert(1)>",basis:"reported",source:"<b>interview</b>"},null,null,null,null];');
  assert.equal(await page.locator('.feeling img, .feeling b').count(),0);
  assert.match(await page.locator('.feeling').first().innerText(),/<img src=x/);
  results.push({case:'feeling-text-escaped',passed:true});
  await render('boundaries','MAP.emotion=[1,5,2.5,1,5];');
  assert.equal(await page.locator('.curve').getAttribute('points'),'50,116 150,16 250,78.5 350,116 450,16');
  results.push({case:'boundaries',passed:true});
  await render('unknown-visibility','MAP.visibilityUnknown=["Warehouse scan",null,null,null,null]; MAP.rows[4].cells[0]=null; MAP.rows[1].basis="hypothesis";');
  assert.equal(await page.title(),"The support agent's journey");
  const labels = await page.locator('#grid .lab').allTextContents();
  assert.ok(labels.indexOf('Visibility not captured') < labels.indexOf('Front-stage'));
  assert.equal(await page.getByText('Warehouse scan',{exact:true}).count(),1);
  assert.equal(await page.getByText('None proposed',{exact:true}).count(),1);
  assert.match(await page.locator('#evidence').innerText(),/Goal: Hypothesis/);
  const swatches=await page.locator('.sw').evaluateAll(nodes=>nodes.map(n=>getComputedStyle(n).backgroundColor));
  assert.equal(new Set(swatches).size,3);
  const otherBackgrounds=await page.locator('.bp, .opp').evaluateAll(nodes=>nodes.map(n=>getComputedStyle(n).backgroundColor));
  assert.ok(otherBackgrounds.every(color=>color!==swatches[1]));
  const goalRefs=await page.locator('#grid .lab').evaluateAll(labs=>labs.filter(l=>l.firstChild && l.firstChild.textContent==='Goal').map(l=>l.querySelectorAll('.ref').length));
  assert.deepEqual(goalRefs,[1], 'A hypothesis row carries one reference on its label');
  assert.equal(await page.locator('.cell').first().evaluate(n=>getComputedStyle(n).fontSize),'16px');
  results.push({case:'unknown-visibility-and-empty-opportunity',passed:true});
  await render('uncaptured-opportunities','MAP.rows[4].basis="not captured"; MAP.rows[4].cells=Array(5).fill(null); MAP.visibilityUnknown=Array(5).fill(null);');
  assert.equal(await page.getByText('None proposed',{exact:true}).count(),0);
  assert.equal(await page.getByText('Visibility not captured',{exact:true}).count(),0);
  results.push({case:'uncaptured-opportunities',passed:true});
  for (const [name,mutation,expected] of [
   ['unknown-visibility-shape','MAP.visibilityUnknown=[4,null,null,null,null];','Unknown visibility'],
   ['invalid-emotion-basis','MAP.emotionBasis="guessed";','evidence basis'],
   ['blank-basis-note','MAP.basisNote=" ";','evidence-basis note'],
   ['missing-basis-note','delete MAP.basisNote;','evidence-basis note'],
   ['wrong-row-order','MAP.rows.reverse();','documented order'],
   ['nontext-cell','MAP.rows[0].cells[0]={text:"note"};','text or null'],
   ['empty-phases','MAP.phases=[];','named phase'],
   ['nontext-phase','MAP.phases[0]=4;','named phase'],
   ['nonarray-friction','MAP.friction={};','valid phase'],
   ['zero-friction-phase','MAP.friction[0].phase="0";','valid phase'],
   ['nontext-friction-title','MAP.friction[0].title=4;','valid phase'],
   ['string-score','MAP.emotion[0]="3";','1 to 5'],
   ['nan-score','MAP.emotion[0]=NaN;','1 to 5'],
   ['invalid-row-basis','MAP.rows[2].basis="guessed";','own evidence basis'],
   ['invalid-goal-basis','MAP.rows[1].basis="guessed";','invalid evidence basis'],
   ['contradictory-goal-basis','MAP.rows[1].basis="not captured";','text marked not captured'],
   ['contradictory-row-basis','MAP.rows[2].basis="not captured";','text marked not captured'],
   ['long-feelings','MAP.emotionLabels=[null,null,null,null,null,null];','exactly one'],
   ['null-feelings','MAP.emotionLabels=null;','exactly one'],
   ['nonobject-feeling','MAP.emotionLabels=["reported",null,null,null,null];','source or hypothesis reason'],
   ['blank-feeling-source','MAP.emotionLabels=[{text:"Relieved",basis:"reported",source:" "},null,null,null,null];','source or hypothesis reason'],
   ['short-feelings','MAP.emotionLabels=[null];','exactly one'],
   ['unbased-feeling','MAP.emotionLabels=[{text:"Relieved",basis:"reported"},null,null,null,null];','source or hypothesis reason'],
   ['blank-feeling','MAP.emotionLabels=[{text:" ",basis:"reported",source:"Interview"},null,null,null,null];','source or hypothesis reason'],
   ['invalid-feeling-basis','MAP.emotionLabels=[{text:"Relieved",basis:"guessed",source:"Interview"},null,null,null,null];','source or hypothesis reason'],
   ['short-row','MAP.rows[0].cells.pop();','exactly one'],
   ['long-row','MAP.rows[0].cells.push("extra evidence");','exactly one'],
   ['out-of-range','MAP.emotion[0]=9;','1 to 5'],
   ['missing-emotion','delete MAP.emotion;','not captured'],
   ['uncaptured-with-scores','MAP.emotionBasis="not captured";','Use null'],
   ['missing-row-basis','delete MAP.rows[2].basis;','own evidence basis'],
   ['bad-phase','MAP.friction[0].phase="99";','valid phase'],
   ['bad-opportunity-kind','MAP.opportunityMap[0].kind="idea";','valid phase, kind'],
   ['unsourced-opportunity','delete MAP.opportunityMap[0].source;','valid phase, kind'],
   ['opportunity-without-measure','MAP.opportunityMap[1].measure=" ";','valid phase, kind'],
  ]) {
   await render(name,mutation);
   assert.ok((await page.locator('[role=alert]').innerText()).includes(expected));
   assert.equal(await page.locator('.curve, .card').count(),0);
   results.push({case:name,passed:true});
  }
  assert.deepEqual(errors,[]);
  fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(results,null,2));
  console.log(JSON.stringify(results));
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
''', encoding='utf-8')
        result = subprocess.run([node, str(runner), str(ROOT/'skills/map-journey/assets/journey-map.html'), str(out)],
                                text=True,capture_output=True,env={**os.environ, "ESTATE_BROWSER_POLICY": str(ROOT/"skills/brand-renderer/scripts/browser_launch_policy.cjs")})
        (out/'run.log').write_text(result.stdout+result.stderr)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        cases = json.loads(result.stdout)
        self.assertEqual(len({case['case'] for case in cases}), len(cases))
        expected = {'normal', 'mobile-scroll', 'evidence', 'unknown', 'unknown-visibility-and-empty-opportunity', 'qualitative-without-scores',
                    'feeling-text-escaped', 'boundaries', 'short-feelings', 'long-feelings',
                    'null-feelings', 'nonobject-feeling', 'blank-feeling-source', 'unbased-feeling',
                    'blank-feeling', 'invalid-feeling-basis', 'short-row', 'long-row', 'out-of-range',
                    'missing-emotion', 'uncaptured-with-scores', 'missing-row-basis', 'bad-phase',
                    'bad-opportunity-kind', 'unsourced-opportunity', 'opportunity-without-measure'}
        self.assertTrue(expected <= {case['case'] for case in cases})

    def rebuild(self, base):
        layout = (ROOT / 'skills/map-journey/references/rendered-map-layout.md').read_text()
        self.assertIn('python3 scripts/build_journey_map.py map-data.json --output', layout)
        data = {'eyebrow': 'Synthetic test', 'title': '</script><img src=x onerror=alert(1)>',
                'lead': 'Source text must remain text.', 'phases': ['Receive'],
                'emotion': None, 'emotionBasis': 'not captured', 'basisNote': 'Synthetic data only.',
                'rows': [{'label': label, 'cells': [None], **({'basis': 'not captured'}
                         if label in ('Thoughts', 'Pain points') else {})}
                         for label in ['Step and touchpoint', 'Goal', 'Thoughts', 'Pain points', 'Opportunities']],
                'blueprint': [{'label': label, 'cells': [None]}
                              for label in ['Front-stage', 'Back-stage', 'Supporting']], 'friction': [],
                'opportunityMap': [{'phase': '01', 'kind': 'quick win', 'title': '</script>Route on arrival',
                                    'outcome': 'Cases reach an owner', 'measure': 'Minutes to first owner',
                                    'basis': 'hypothesis', 'source': 'Synthetic test'}]}
        (base/'map-data.json').write_text(json.dumps(data))
        build = subprocess.run([sys.executable, str(ROOT/'skills/map-journey/scripts/build_journey_map.py'),
                                'map-data.json', '--output', 'journey-map.html'],
                               cwd=base, capture_output=True, text=True)
        self.assertEqual(build.returncode, 0, build.stderr)
        html = (base/'journey-map.html').read_text()
        embedded = html.split('const MAP = ', 1)[1].split(';\n\nconst el', 1)[0]
        self.assertEqual(json.loads(embedded), data)
        self.assertNotIn("</script>", embedded.casefold())
        self.assertNotIn("<img", embedded.casefold())
        return data, html, embedded

    def test_json_build_preserves_data_and_escapes_script_breakout(self):
        with tempfile.TemporaryDirectory() as folder:
            self.rebuild(Path(folder))

    @integration("browser")
    def test_json_build_renders_roadmap_without_executing_markup(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            self.rebuild(base)
            runner = base/'check.cjs'
            runner.write_text("""
const {chromium}=require('playwright'),assert=require('assert/strict'),url=require('url');
(async()=>{const b=await chromium.launch(require(process.env.ESTATE_BROWSER_POLICY).launchOptions());
try {const p=await b.newPage();await p.goto(url.pathToFileURL(process.argv[2]).href);
assert.equal(await p.locator('[role=alert], img').count(),0);
assert.equal(await p.locator('h1').innerText(),'</script><img src=x onerror=alert(1)>');
assert.equal(await p.locator('#opps .rk-card').count(),1);
assert.equal(await p.locator('#opps .rk-card-title').innerText().then(t=>t.startsWith('</script>Route on arrival')),true);
assert.equal(await p.locator('#opps .rk-ref').getAttribute('href'),'#ev-1');
} finally {await b.close();}})().catch(e=>{console.error(e);process.exit(1)});
""", encoding='utf-8')
            node = os.environ.get('ESTATE_NODE') or shutil.which('node')
            result = subprocess.run([node, str(runner), str(base/'journey-map.html')],
                                    capture_output=True, text=True, env={**os.environ, "ESTATE_BROWSER_POLICY": str(ROOT/"skills/brand-renderer/scripts/browser_launch_policy.cjs")})
            self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
            check = subprocess.run([sys.executable, str(ROOT/'skills/brand-renderer/scripts/brand_check.py'),
                                    str(base/'journey-map.html')], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(check.returncode, 0, check.stdout+check.stderr)

    def test_neutral_starter_passes_the_selected_profile_check(self):
        result = subprocess.run([sys.executable, str(ROOT/'skills/brand-renderer/scripts/brand_check.py'),
                                 str(ROOT/'skills/map-journey/assets/journey-map.html')],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)


if __name__ == '__main__':
    unittest.main()
