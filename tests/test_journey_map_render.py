"""Render the journey starter and exercise data failures in Chromium."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import unittest

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
  await page.goto("about:blank");
  await page.setContent(body);
 }
 try {
  await render('normal');
  assert.equal(await page.locator('[role=alert]').count(),0);
  assert.equal(await page.locator('.curve.hyp').count(),1);
  assert.equal(await page.locator('.hypothesis').count(),10);
  const order=await page.locator('#grid > .lab, #grid > .vis').allTextContents();
  assert.deepEqual(order.slice(-5),['Front-stage','Line of visibility','Back-stage','Line of internal interaction','Supporting']);
  assert.equal(await page.locator('.card').count(),3);
  assert.match(await page.locator('#basis').innerText(),/Synthetic example/);
  await page.screenshot({path:path.join(out,'desktop.png'),fullPage:true});
  results.push({case:'normal',passed:true});
  await page.setViewportSize({width:390,height:844});
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
  await render('unknown','MAP.emotion=null; MAP.emotionBasis="not captured"; MAP.blueprint[1].cells[0]=null;');
  assert.equal(await page.locator('[role=alert]').count(),0);
  assert.equal(await page.locator('.curve').count(),0);
  assert.match(await page.locator('.emotion').innerText(),/Not captured/);
  assert.match(await page.locator('#grid').innerText(),/Not captured/);
  results.push({case:'unknown',passed:true});
  for (const [name,mutation,expected] of [
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
        self.assertEqual(len(json.loads(result.stdout)),11)

if __name__ == '__main__':
    unittest.main()
