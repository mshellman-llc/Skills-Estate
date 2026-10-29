const fs=require('fs');
const path=require('path');
const assert=require('assert/strict');
const {pathToFileURL}=require('url');
const {chromium}=require('playwright');
(async()=>{
 const input=path.resolve(process.argv[2]||path.join(__dirname,'index.html'));
 const output=path.resolve(process.argv[3]||path.join(__dirname,'qa'));
 fs.mkdirSync(output,{recursive:true});
 const data=JSON.parse(fs.readFileSync(input.replace(/\.html$/,'.json'),'utf8'));
 const browser=await chromium.launch({headless:true,channel:process.env.PLAYWRIGHT_CHANNEL||'chrome'});
 const context=await browser.newContext({viewport:{width:1440,height:1100},acceptDownloads:true});
 const page=await context.newPage();const errors=[], requests=[];
 page.on('pageerror',e=>errors.push(e.message));
 const preview=process.env.MAP_PREVIEW_URL;
 page.on('request',r=>{if(/^https?:/.test(r.url())&&(!preview||new URL(r.url()).origin!==new URL(preview).origin))requests.push(r.url())});
 await page.goto(preview||pathToFileURL(input).href);await page.evaluate(()=>document.fonts.ready);
 assert.equal(await page.locator('.skill-row').count(),data.skills.length);
 await page.screenshot({path:path.join(output,'desktop.png')});
 fs.writeFileSync(path.join(output,'rendered.html'),await page.content());
 assert.equal(await page.locator('body').evaluate(e=>getComputedStyle(e).fontSize),'16px');
 assert.equal(await page.locator('body').evaluate(e=>getComputedStyle(e).backgroundColor),'rgb(255, 255, 255)');
 // All exact sources remain downloadable and all detail panes populate for every skill.
 for(const skill of data.skills){
  await page.locator(`.skill-row[data-skill="${skill.id}"]`).click();
  assert.equal(await page.locator('#detail-title').textContent(),skill.title);
  if(skill.guide){
   const overview=await page.locator('#panel-overview').innerText();
   for(const phrase of ['What it does','When to use it','What to give it','What you get','How to start','Built for'])assert(overview.includes(phrase));
   assert(!overview.includes('ESTATE-WRITING'));
   assert(overview.includes(skill.reuse.label));
  }
  await page.locator('#tab-instructions').click();
  assert((await page.locator('#panel-instructions .instructions').innerText()).length>100);
  assert(!(await page.locator('#panel-instructions').innerText()).includes('ESTATE-WRITING:'));
  assert(!(await page.locator('#panel-instructions').innerText()).includes('Before writing:'));
  if(skill.id==='writing-integrity')await page.screenshot({path:path.join(output,'writing-instructions.png')});
  await page.locator('#tab-connections').click();
  const connections=await page.locator('#panel-connections').innerText();
  assert(!connections.includes('ESTATE-WRITING:'));
  assert(!connections.includes('Before writing:'));
  await page.locator('#tab-files').click();
  assert.equal(await page.locator('.raw-source').textContent(),skill.markdown);
  await page.keyboard.press('Escape');assert.equal(await page.locator('#detail').evaluate(e=>e.open),false);
 }
 // Combined query/family/status filtering and empty recovery.
 await page.locator('#search').fill('scope');
 const scopeIds=await page.locator('.skill-row').evaluateAll(es=>es.map(e=>e.dataset.skill));assert(scopeIds.length>0&&scopeIds.length<data.skills.length);
 await page.locator('[data-family="1"]').click();
 const familyIds=await page.locator('.skill-row').evaluateAll(es=>es.map(e=>e.dataset.skill));
 assert(familyIds.every(id=>data.skills.find(s=>s.id===id).family===1));
 await page.locator('#source-filter').selectOption('github');
 const filtered=await page.locator('.skill-row').evaluateAll(es=>es.map(e=>e.dataset.skill));assert(filtered.every(id=>data.skills.find(s=>s.id===id).status==='github'));
 if(preview){
  const pendingDownload=page.waitForEvent('download');await page.locator('#export').click();const dl=await pendingDownload;const zipPath=path.join(output,'selected-packages.zip');await dl.saveAs(zipPath);
  assert.equal(fs.readFileSync(zipPath).subarray(0,4).toString('hex'),'504b0304');
  const {execFileSync}=require('child_process');const checked=JSON.parse(execFileSync('python3',['-c',"import zipfile,json,sys; z=zipfile.ZipFile(sys.argv[1]); assert z.testzip() is None; m=json.loads(z.read('manifest.json')); assert all(z.read('skills/'+v['file']).startswith(b'PK') for v in m['packages'].values()); print(json.dumps({'packages':sorted(m['packages']),'workflows':json.loads(z.read('selected-workflows.json'))['workflows']}))",zipPath],{encoding:'utf8'}));
  const expected=[...new Set(filtered.flatMap(id=>data.skills.find(s=>s.id===id).downloadPackages))].sort();assert.deepEqual(checked.packages,expected);assert.deepEqual(checked.workflows.map(w=>w.workflow).sort(),[...filtered].sort());
 }
 await page.evaluate(()=>document.querySelector('#toast').hidden=true);
 await page.locator('#search').fill('no-such-skill-52948');assert.equal(await page.locator('.skill-row').count(),0);await page.locator('[data-reset]').click();assert.equal(await page.locator('.skill-row').count(),data.skills.length);
 // Keyboard activation, dialog focus trapping, and arrow-key tab navigation.
 await page.locator('.skill-row').first().focus();await page.keyboard.press('Enter');assert(await page.locator('#detail').evaluate(e=>e.open));
 await page.locator('#tab-overview').focus();await page.keyboard.press('ArrowRight');assert.equal(await page.locator('#tab-instructions').getAttribute('aria-selected'),'true');
 for(let i=0;i<25;i++){await page.keyboard.press('Tab');assert(await page.evaluate(()=>document.querySelector('#detail').contains(document.activeElement)))}
 await page.keyboard.press('Escape');
 const chosen=byName('sales-process-mapping')||byName('call-prep');
 function byName(name){return data.skills.find(s=>s.id===name)}
 await page.locator(`.skill-row[data-skill="${chosen.id}"]`).click();await page.screenshot({path:path.join(output,'detail.png')});
 await page.locator('#tab-connections').click();
 if(chosen.mentions.length){await page.locator('#panel-connections [data-skill]').first().click();assert.notEqual(await page.locator('#detail-title').textContent(),chosen.title)}
 await page.keyboard.press('Escape');await page.locator('#routes-view').click();assert.equal(await page.locator('.route').count(),6);await page.screenshot({path:path.join(output,'workflows.png')});
 await page.locator('.route [data-skill]').first().click();assert(await page.locator('#detail').evaluate(e=>e.open));await page.keyboard.press('Escape');await page.locator('#browse-view').click();
 // Full instruction search and status counts.
 await page.locator('#full-search').check();await page.locator('#search').fill('ESTATE-WRITING');assert((await page.locator('.skill-row').count())>0);await page.locator('#reset').click();
 for(const status of ['github','local-revision','local-addition']){await page.locator('#source-filter').selectOption(status);assert.equal(await page.locator('.skill-row').count(),data.counts[status])}
 await page.locator('#reset').click();
 // Intent, required setup, and sharing cleanup remain separate from source parity.
 for(const audience of ['general','megan','review','cleanup','setup']){
  await page.locator('#audience-filter').selectOption(audience);
  const expected=data.skills.filter(s=>audience==='cleanup'?s.reuse.audience==='general'&&s.reuse.cleanup.length:audience==='setup'?s.reuse.audience==='general'&&s.reuse.setup:s.reuse.audience===audience);
  assert.equal(await page.locator('.skill-row').count(),expected.length);
 }
 await page.locator('#reset').click();
 for(const role of ['task','mode','support']){await page.locator('#role-filter').selectOption(role);assert.equal(await page.locator('.skill-row').count(),data.skills.filter(s=>s.catalogRole.kind===role).length)}
 await page.locator('#reset').click();
 // No external requests, mobile overflow, detail layout, and print media.
 await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(output,'mobile.png'),fullPage:false});
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));
 await page.locator(`.skill-row[data-skill="${chosen.id}"]`).click();await page.screenshot({path:path.join(output,'mobile-detail.png')});
 assert(await page.locator('#detail').evaluate(e=>e.scrollWidth<=e.clientWidth));await page.keyboard.press('Escape');
 await page.setViewportSize({width:1440,height:1100});await page.locator('[data-family="0"]').click();await page.emulateMedia({media:'print'});await page.pdf({path:path.join(output,'print.pdf'),format:'Letter',printBackground:true});await page.screenshot({path:path.join(output,'print.png')});
 assert.equal(errors.length,0,errors.join('\n'));assert.equal(requests.length,0,'Offline artifact must not load network resources');
 const report={artifact:input,skills:data.skills.length,counts:data.counts,detailViewsChecked:data.skills.length,checks:['all exact Markdown sources','combined filters','empty/reset','verified complete package ZIP download','keyboard activation','dialog focus','arrow-key tabs','connections','six workflow routes','full instruction search','source filters','390px overflow','print rendering','zero external requests','zero page errors'],errors,requests};
 fs.writeFileSync(path.join(output,'browser-report.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
