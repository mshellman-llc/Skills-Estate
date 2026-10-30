import fs from 'node:fs';
import path from 'node:path';
const policyURL = [new URL('../_runtime/brand-renderer/scripts/browser_launch_policy.cjs', import.meta.url),
  new URL('../../brand-renderer/scripts/browser_launch_policy.cjs', import.meta.url)].find(url => fs.existsSync(url));
if (!policyURL) throw new Error('Browser policy is missing. Rebuild with the declared brand runtime.');
const {default: browserPolicy} = await import(policyURL.href);
const { chromium } = await import(process.env.PW_MODULE || 'playwright');
const [url, out] = process.argv.slice(2);
if (!url?.startsWith('file:') || !out) throw new Error('Supply a local file URL and a new output directory');
fs.mkdirSync(out, { recursive: false });
const browser = await chromium.launch(browserPolicy.launchOptions());
const report = {slides:0, views:[], failures:[], remoteRequests:[]};
try {
 const page=await browser.newPage({viewport:{width:1360,height:900}, deviceScaleFactor:1});
 await page.route('**/*',route=>{if(/^https?:/.test(route.request().url())){report.remoteRequests.push(route.request().url());return route.abort();}return route.continue();});
 page.on('pageerror',e=>report.failures.push(e.message));
 await page.goto(url);await page.evaluate(()=>document.fonts.ready);
 const slides=page.locator('.slide');report.slides=await slides.count();
 if(!report.slides)report.failures.push('No slides');
 for(let i=0;i<report.slides;i++){
  const s=slides.nth(i);
  const defects=await s.evaluate(el=>{
   const box=el.getBoundingClientRect(), foot=el.querySelector('footer').getBoundingClientRect();const bad=[];
   for(const node of el.querySelectorAll('h1,h2,h3,p,td,th,li,figcaption,aside,.record-row')){
    if(!node.getClientRects().length)continue;
    const r=node.getBoundingClientRect();
    if(r.right>box.right+1||r.left<box.left-1||r.bottom>foot.top+1||node.scrollWidth>node.clientWidth+1||node.scrollHeight>node.clientHeight+1)bad.push(node.textContent.trim());
   }
   for(const svg of el.querySelectorAll('svg')){
    const bounds=svg.getBoundingClientRect();
    if(bounds.bottom>foot.top+1)bad.push('Diagram crosses the footer');
    for(const label of svg.querySelectorAll('text')){
     const r=label.getBoundingClientRect();
     if(r.left<bounds.left-1||r.right>bounds.right+1||r.top<bounds.top-1||r.bottom>bounds.bottom+1)bad.push('Diagram label outside its viewport: '+label.textContent);
    }
   }
   const overlaps=(a,b)=>a.left<b.right-2&&a.right>b.left+2&&a.top<b.bottom-2&&a.bottom>b.top+2;
   for(const label of el.querySelectorAll('.edge-label')){
    for(const shape of el.querySelectorAll('[data-node]')){
     if(overlaps(label.getBoundingClientRect(),shape.getBoundingClientRect()))bad.push('Edge label overlaps node: '+label.textContent+' / '+shape.dataset.node);
    }
   }
   return bad;
  });
  if(defects.length)report.failures.push({slide:i+1,overflow:defects});
  const filename=`slide-${String(i+1).padStart(2,'0')}.png`;
  await s.screenshot({path:path.join(out,filename)});report.views.push(filename);
 }
 await page.emulateMedia({media:'print'});
 if(await page.locator('table').count() && await page.locator('table').first().evaluate(el=>getComputedStyle(el).display)!=='table')report.failures.push('Print tables lost their column layout');
 await page.pdf({path:path.join(out,'deck.pdf'),preferCSSPageSize:true,printBackground:true});
 await page.emulateMedia({media:'screen'});
 await page.setViewportSize({width:390,height:844});
 if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1))report.failures.push('Narrow page overflows');
 for(let i=0;i<report.slides;i++){
  const filename=`narrow-${String(i+1).padStart(2,'0')}.png`;await slides.nth(i).screenshot({path:path.join(out,filename)});report.views.push(filename);
 }
 if(report.remoteRequests.length)report.failures.push('Output requires remote resources');
} finally {await browser.close();fs.writeFileSync(path.join(out,'browser.json'),JSON.stringify(report,null,2));}
console.log(JSON.stringify(report));process.exit(report.failures.length?1:0);
