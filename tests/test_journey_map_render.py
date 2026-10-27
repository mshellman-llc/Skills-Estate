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

class JourneyMapRenderTests(unittest.TestCase):
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
 const browser = await chromium.launch({headless:true, executablePath:process.env.PW_CHROMIUM || undefined});
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
  assert.equal(await page.locator('.hypothesis').count(),10);
  const order=await page.locator('#grid > .lab, #grid > .vis').allTextContents();
  assert.deepEqual(order.slice(-5),['Front-stage','Line of visibility','Back-stage','Line of internal interaction','Supporting']);
  assert.equal(await page.locator('.card').count(),3);
  assert.equal(await page.locator('.curve').getAttribute('points'),'50,66 150,91 250,66 350,116 450,41');
  assert.match(await page.locator('#basis').innerText(),/Synthetic example/);
  await page.screenshot({path:path.join(out,'desktop.png'),fullPage:true});
  results.push({case:'normal',passed:true});
  await page.setViewportSize({width:390,height:844});
  await page.reload();
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  assert.equal(await page.locator('.board').evaluate(e=>e.scrollWidth>e.clientWidth),true);
  await page.locator('.board').evaluate(e=>e.scrollLeft=300);
  assert.ok(await page.locator('.board').evaluate(e=>e.scrollLeft)>0);
  await page.screenshot({path:path.join(out,'mobile.png'),fullPage:true});
  results.push({case:'mobile-scroll',passed:true});
  await render('evidence','MAP.emotionBasis="evidence"; MAP.rows[2].basis="reported"; MAP.rows[3].basis="observed";');
  assert.equal(await page.locator('.curve.hyp, .hypothesis').count(),0);
  assert.equal(await page.locator('.curve').count(),1);
  results.push({case:'evidence',passed:true});
  await render('unknown','MAP.emotion=null; MAP.emotionBasis="not captured"; MAP.blueprint[1].cells[0]=null; MAP.rows[2].cells[0]=null;');
  assert.equal(await page.locator('[role=alert]').count(),0);
  assert.equal(await page.locator('.curve').count(),0);
  assert.match(await page.locator('.emotion').innerText(),/Not captured/);
  assert.match(await page.locator('#grid').innerText(),/Not captured/);
  assert.equal(await page.locator('.hypothesis').count(),9);
  results.push({case:'unknown',passed:true});
  await render('qualitative', 'MAP.emotion=null; MAP.emotionBasis="not captured"; MAP.emotionLabels=[{text:"Uncertain at intake",basis:"reported",source:"Agent A interview"},null,{text:"Relieved after account confirmation",basis:"reported",source:"Agent A interview"},null,{text:"Possible relief",basis:"hypothesis",source:"Validate after a confirmed fix"}];');
  assert.equal(await page.locator('[role=alert], .curve').count(),0);
  assert.equal(await page.locator('.feeling').count(),5);
  const feelings=await page.locator('.feeling').allTextContents();
  assert.match(feelings[0],/Uncertain at intake/);
  assert.match(feelings[2],/Relieved after account confirmation/);
  assert.equal(feelings[1],'Not captured');
  assert.match(feelings[2],/reported · Agent A interview/);
  assert.equal(await page.locator('.feeling.hypothesis').count(),1);
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
  for (const [name,mutation,expected] of [
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
        result = subprocess.run([node, str(runner), str(ROOT/'skills/journey-mapping/assets/journey-map.html'), str(out)],
                                text=True,capture_output=True,env=os.environ.copy())
        (out/'run.log').write_text(result.stdout+result.stderr)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        cases = json.loads(result.stdout)
        self.assertEqual(len({case['case'] for case in cases}), len(cases))
        expected = {'normal', 'mobile-scroll', 'evidence', 'unknown', 'qualitative-without-scores',
                    'feeling-text-escaped', 'boundaries', 'short-feelings', 'long-feelings',
                    'null-feelings', 'nonobject-feeling', 'blank-feeling-source', 'unbased-feeling',
                    'blank-feeling', 'invalid-feeling-basis', 'short-row', 'long-row', 'out-of-range',
                    'missing-emotion', 'uncaptured-with-scores', 'missing-row-basis', 'bad-phase'}
        self.assertTrue(expected <= {case['case'] for case in cases})

    def test_documented_json_rebuild_preserves_data_and_prevents_script_breakout(self):
        layout = (ROOT / 'skills/journey-mapping/references/rendered-map-layout.md').read_text()
        code = re.search(r'```python\n(.*?)\n```', layout, re.S)[1]
        data = {'eyebrow': 'Synthetic test', 'title': '</script><img src=x onerror=alert(1)>',
                'lead': 'Source text must remain text.', 'phases': ['Receive'],
                'emotion': None, 'emotionBasis': 'not captured', 'basisNote': 'Synthetic data only.',
                'rows': [{'label': label, 'cells': [None], **({'basis': 'not captured'}
                         if label in ('Thoughts', 'Pain points') else {})}
                         for label in ['Step and touchpoint', 'Goal', 'Thoughts', 'Pain points', 'Opportunities']],
                'blueprint': [{'label': label, 'cells': [None]}
                              for label in ['Front-stage', 'Back-stage', 'Supporting']], 'friction': []}
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            (base/'map-data.json').write_text(json.dumps(data))
            starter = ROOT/'skills/journey-mapping/assets/journey-map.html'
            build = subprocess.run([sys.executable, '-c', 'STARTER = '+repr(str(starter))+'\n'+code],
                                   cwd=base, capture_output=True, text=True)
            self.assertEqual(build.returncode, 0, build.stderr)
            html = (base/'journey-map.html').read_text()
            embedded = html.split('const MAP = ', 1)[1].split(';\n\nconst el', 1)[0]
            self.assertEqual(json.loads(embedded), data)
            runner = base/'check.cjs'
            runner.write_text("""
const {chromium}=require('playwright'),assert=require('assert/strict'),url=require('url');
(async()=>{const b=await chromium.launch({headless:true,executablePath:process.env.PW_CHROMIUM||undefined});
try {const p=await b.newPage();await p.goto(url.pathToFileURL(process.argv[2]).href);
assert.equal(await p.locator('[role=alert], img').count(),0);
assert.equal(await p.locator('h1').innerText(),'</script><img src=x onerror=alert(1)>');
} finally {await b.close();}})().catch(e=>{console.error(e);process.exit(1)});
""", encoding='utf-8')
            node = os.environ.get('ESTATE_NODE') or shutil.which('node')
            result = subprocess.run([node, str(runner), str(base/'journey-map.html')],
                                    capture_output=True, text=True, env=os.environ.copy())
            self.assertEqual(result.returncode, 0, result.stdout+result.stderr)

    def test_neutral_starter_passes_the_selected_profile_check(self):
        result = subprocess.run([sys.executable, str(ROOT/'skills/brand-renderer/scripts/brand_check.py'),
                                 str(ROOT/'skills/journey-mapping/assets/journey-map.html')],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)


if __name__ == '__main__':
    unittest.main()
