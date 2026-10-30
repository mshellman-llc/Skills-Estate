import fs from 'node:fs';
import path from 'node:path';
const [url,output]=process.argv.slice(2);
const report={checks:{},failures:[]};
const check=(name,value)=>{report.checks[name]=Boolean(value);if(!value)report.failures.push(name);};
let browser;
try {
  const {chromium}=await import(process.env.PW_MODULE);
  browser=await chromium.launch({headless:true,args:["--disable-gpu"],...(process.env.PW_CHROMIUM?{executablePath:process.env.PW_CHROMIUM}:{})});
  const context=await browser.newContext({viewport:{width:1280,height:1000}});
  const page=await context.newPage();
  page.on('pageerror',e=>report.failures.push(e.message));
  await context.route('**/*',route=>{
    if(/^https?:/.test(route.request().url())){report.failures.push('Unexpected network resource');return route.abort();}
    return route.continue();
  });
  await page.goto(url);await page.evaluate(()=>document.fonts.ready);
  const data=await page.locator('#proposal-data').textContent().then(JSON.parse);
  check('main landmark',await page.locator('main').count()===1);
  for(const v of data.versions){
    await page.getByRole('tab',{name:v.name,exact:true}).click();
    check(v.key+' selected',await page.locator('#version-panel').getAttribute('data-version')===v.key);
    check(v.key+' included count',await page.locator('.item:not(.out)').count()===v._included_ids.length);
    check(v.key+' excluded count',await page.locator('.item.out').count()===data._scope_items.length-v._included_ids.length);
    const metric=await page.locator('#metric').innerText();
    const expected=data.meta.mode==='proposal'?new Intl.NumberFormat('en-US',{style:'currency',currency:data.meta.currency,minimumFractionDigits:2,maximumFractionDigits:20}).format(v.total):String(v.metric);
    check(v.key+' exact metric',metric===expected);
    for(const scope of data._scope_items){
      const card=page.locator('[data-scope-id="'+scope.id+'"]');
      check(v.key+' scope '+scope.id,(await card.innerText()).includes(scope.description));
      check(v.key+' source '+scope.id,(await card.innerText()).includes(data.sources.find(s=>s.id===scope.source).reference));
    }
    for(const id of ['assumptions','boundaries','sources']){
      if(!await page.locator('#'+id).evaluate(e=>e.open))await page.locator('#'+id+' > summary').click();
      check(v.key+' disclosure '+id,await page.locator('#'+id).evaluate(e=>e.open));
    }
    const body=await page.locator('body').innerText();
    for(const assumption of v.assumptions)check(v.key+' assumption '+assumption,body.includes(assumption));
    for(const boundary of v.not_included)check(v.key+' boundary '+boundary.item,body.includes(boundary.route));
    if(data.meta.mode==='explorer'){
      check(v.key+' no currency',!/[€£$¥₹]|\b(?:USD|EUR|GBP|JPY|CAD|AUD|INR)\b/i.test(body));
      check(v.key+' no staffing',!await page.locator('#staffing').isVisible());
    }else{
      for(const person of v.team)check(v.key+' team '+person.role,body.includes(person.role)&&body.includes(person.allocation));
    }
    await page.screenshot({path:path.join(output,'version-'+v.key+'.png'),fullPage:true,animations:'disabled'});
    await page.emulateMedia({media:'print'});
    check(v.key+' print hides option controls',!await page.locator('#tabs').isVisible());
    check(v.key+' print hides excluded cards',await page.locator('.item.out').evaluateAll(nodes=>nodes.every(n=>getComputedStyle(n).display==='none')));
    check(v.key+' print retains included cards',await page.locator('.item:not(.out)').evaluateAll(nodes=>nodes.length>0&&nodes.every(n=>getComputedStyle(n).display!=='none')));
    check(v.key+' print retains metric',await page.locator('#metric').isVisible()&&(await page.locator('#metric').innerText())===expected);
    const printPage=await context.newPage();await printPage.goto(url);
    await printPage.evaluate(()=>document.fonts.ready);
    await printPage.evaluate(key=>{document.getElementById('tab-'+key).click();document.querySelectorAll('details').forEach(d=>d.open=true);window.scrollTo(0,0);},v.key);
    await printPage.emulateMedia({media:'print'});
    await printPage.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
    await printPage.pdf({path:path.join(output,'version-'+v.key+'.pdf'),format:'Letter',printBackground:true});
    await printPage.close();
    await page.emulateMedia({media:'screen'});
  }
  await page.getByRole('tab').first().focus();
  await page.keyboard.press('End');
  check('keyboard End',await page.getByRole('tab').last().getAttribute('aria-selected')==='true');
  await page.keyboard.press('Home');
  check('keyboard Home',await page.getByRole('tab').first().getAttribute('aria-selected')==='true');
  if(data.versions.length>1){await page.keyboard.press('ArrowRight');check('keyboard next',await page.getByRole('tab').nth(1).getAttribute('aria-selected')==='true');}
  await page.setViewportSize({width:390,height:900});
  for(const v of data.versions){
    await page.getByRole('tab',{name:v.name,exact:true}).click();
    check(v.key+' mobile width',await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
    await page.screenshot({path:path.join(output,'mobile-'+v.key+'.png'),fullPage:true,animations:'disabled'});
  }
  check('no missing images',await page.evaluate(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0)));
} catch(error){report.failures.push(error.message);}
finally{if(browser)await browser.close();}
console.log(JSON.stringify(report));
process.exitCode=report.failures.length?2:0;
