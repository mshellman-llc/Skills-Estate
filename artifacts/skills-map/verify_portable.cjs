const assert=require('assert/strict');
const {chromium}=require('playwright');
const {launchOptions}=require('../../skills/brand-renderer/scripts/browser_launch_policy.cjs');
(async()=>{
 const browser=await chromium.launch(launchOptions());
 try {
  const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  const origin=process.argv[2];await page.goto(origin+'/manage');
  await page.locator('#search').fill('Assess offering fit');
  await page.getByLabel('Show in portfolio: Assess offering fit',{exact:true}).check();
  await page.locator('#save').click();await page.getByRole('status').filter({hasText:'Choices saved'}).waitFor();
  await page.reload();await page.locator('#search').fill('Assess offering fit');
  assert(await page.getByLabel('Show in portfolio: Assess offering fit',{exact:true}).isChecked());
  assert(await page.getByLabel('Show in Skills Estate: Assess offering fit',{exact:true}).isChecked());
  await page.locator('#target').selectOption('portfolio');
  await page.locator('#select-all').check();await page.getByRole('button',{name:'Disable downloads',exact:true}).click();
  assert.equal(await page.getByLabel('Allow download in portfolio: Assess offering fit',{exact:true}).isChecked(),false);
  await page.getByRole('button',{name:'Preview portfolio',exact:true}).click();
  const preview=page.getByRole('link',{name:'Open preview',exact:true});await preview.waitFor();
  assert((await page.locator('#preview-result').innerText()).includes('1 skills · 0 workflow examples · 0 plugins'));
  const url=new URL(await preview.getAttribute('href'),origin).href.replace('index.html','integration-example.html');
  const widget=await browser.newPage();widget.on('pageerror',e=>errors.push(e.message));await widget.goto(url);
  await widget.locator('.skill-row').waitFor();assert.equal(await widget.locator('.skill-row').count(),1);
  assert.equal(await widget.locator('body').evaluate(e=>getComputedStyle(e).backgroundColor),'rgb(255, 255, 255)');
  await widget.locator('.skill-row').click();assert(await widget.locator('#detail').isVisible());
  assert.equal(await widget.locator('#detail .dialog-body').evaluate(e=>getComputedStyle(e).paddingTop),'20px');
  assert.equal(await widget.locator('[role=tab]').count(),0);assert(await widget.locator('#panel-files').isVisible());assert.equal(await widget.getByRole('button',{name:'Download SKILL.md',exact:true}).count(),0);
  await widget.keyboard.press('Escape');assert.equal(await widget.locator('#detail').isVisible(),false);
  await widget.setViewportSize({width:390,height:844});await widget.locator('.skill-row').click();
  assert(await widget.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  assert(await widget.locator('#detail').evaluate(e=>e.scrollWidth<=e.clientWidth));
  await page.setViewportSize({width:390,height:844});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.locator('#restore').click();await page.getByRole('status').filter({hasText:'Previous choices restored'}).waitFor();
  assert.equal(await page.getByLabel('Show in portfolio: Assess offering fit',{exact:true}).isChecked(),false);
  assert.deepEqual(errors,[]);console.log(JSON.stringify({checks:['saved independent visibility','reload','bulk download controls','one-record export','component integration','host styles preserved','inline expansion','download suppressed','Escape collapse','390px component and owner bounds','previous-save restore'],errors}));
 } finally {await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
