import fs from 'node:fs';
import path from 'node:path';
const policyURL = [new URL('../_runtime/brand-renderer/scripts/browser_launch_policy.cjs', import.meta.url),
  new URL('../../brand-renderer/scripts/browser_launch_policy.cjs', import.meta.url)].find(url => fs.existsSync(url));
if (!policyURL) throw new Error('Browser policy is missing. Rebuild with the declared brand runtime.');
const {default: browserPolicy} = await import(policyURL.href);
const {chromium}=await import(process.env.PW_MODULE||'playwright');
const [url,out,planPath]=process.argv.slice(2);
if(!url?.startsWith('file:')||!out||!planPath)throw Error('Supply a local HTML URL, new output directory and presentation JSON');
const plan=JSON.parse(fs.readFileSync(planPath,'utf8'));fs.mkdirSync(out,{recursive:false});
const report={failures:[],remoteRequests:[],matrix:[],snapshots:[],views:[]};
const browser=await chromium.launch({...browserPolicy.launchOptions(),args:["--disable-gpu"]});
try{
 const page=await browser.newPage({viewport:{width:1360,height:1000},deviceScaleFactor:1});
 await page.route('**/*',route=>{if(/^https?:/.test(route.request().url())){report.remoteRequests.push(route.request().url());return route.abort();}return route.continue();});
 page.on('pageerror',e=>report.failures.push(e.message));await page.goto(url);await page.evaluate(()=>document.fonts.ready);
 report.matrix=await page.locator('.matrix tr[data-item]').evaluateAll(rows=>rows.map(row=>({id:row.dataset.item,name:row.querySelector('th>span').textContent,description:row.querySelector('th p').textContent,cells:[...row.querySelectorAll('td')].map(td=>({quote:td.dataset.quote,state:td.querySelector('.state').textContent,hours:td.querySelector('.hours')?.textContent??null,range:td.querySelector('.range')?.textContent??null,text:td.innerText}))})));
 const stateNames={in:'Included',available:'Available',optional:'Optional',out:'Not included'};
 if(report.matrix.length!==plan.matrix.length)report.failures.push('Rendered item count differs');
 for(const item of plan.matrix){
  const actual=report.matrix.find(v=>v.id===item.id);
  if(!actual||actual.name!==item.name||actual.description!==item.description){report.failures.push('Missing or changed item '+item.id);continue;}
  for(const [qid,cell] of Object.entries(item.cells)){
   const found=actual.cells.find(v=>v.quote===qid);
   const unestimated=cell.status==='unestimated',range=cell.hours!==null&&typeof cell.hours==='object';
   const hours=unestimated?'Not estimated':cell.hours===null?null:range?Number(cell.hours.expected)+' h expected':Number(cell.hours)+' h';
   if(!found||found.state!==stateNames[cell.state]||found.hours!==hours)report.failures.push('Rendered cell mismatch '+item.id+'/'+qid);
   else if(range&&found.range!=='Range '+Number(cell.hours.low)+' to '+Number(cell.hours.high)+' h')report.failures.push('Rendered range mismatch '+item.id+'/'+qid);
   else if(unestimated&&/\d/.test(found.text))report.failures.push('Unestimated cell shows a figure '+item.id+'/'+qid);
  }
 }
 report.snapshots=await page.locator('tr[data-snapshot]').evaluateAll(rows=>rows.map(row=>({id:row.dataset.snapshot,text:row.innerText})));
 const money=(v,c)=>c+' '+Number(v).toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});
 for(const option of plan.options)for(const s of option.snapshots??[]){
  const row=report.snapshots.find(v=>v.id===s.id);
  if(!row||![s.label,money(s.revenue,s.currency),s.weeks+' weeks',s.hours+' staffing hours'].every(v=>row.text.includes(v)))report.failures.push('Rendered staffing mismatch '+s.id);
 }
 if(plan.options.every(o=>!(o.snapshots??[]).length)){
  // An unpriced comparison names its missing inputs and derives no price, staffing plan or timeline.
  const text=await page.evaluate(()=>document.body.innerText);
  if(await page.locator('.plans').count())report.failures.push('Unpriced page shows a staffing plan');
  if(!await page.locator('.missing-inputs dt').count())report.failures.push('Unpriced page does not name its missing inputs');
  if(/\b[A-Z]{3} [\d,]+\.\d{2}\b|\b\d+ weeks\b|staffing hours/.test(text))report.failures.push('Unpriced page derives a price, duration or staffing figure');
 }
 for(const [name,width] of [['desktop',1360],['narrow',390]]){
  await page.setViewportSize({width,height:1000});
  const problems=await page.evaluate(()=>{
   const bad=[];
   if(document.documentElement.scrollWidth>innerWidth+1)bad.push('Page overflows');
   for(const el of document.querySelectorAll('.option p,.option h2,.plans th,.plans td,.intro,footer,.notes p')){
    const r=el.getBoundingClientRect();if(el.scrollWidth>el.clientWidth+1||r.right>innerWidth+1)bad.push(el.textContent);
   }
   return bad;
  });if(problems.length)report.failures.push({view:name,overflow:problems});
  // Record the rendered text at each width for parity review. No image files are written.
  report.views.push({view:name,width,text:await page.evaluate(()=>document.body.innerText.trim())});
  if(name==='narrow'){
   report.narrowScroll=await page.locator('.table-scroll').evaluate(el=>{el.scrollLeft=el.scrollWidth;return {required:el.scrollWidth>el.clientWidth,position:el.scrollLeft};});
   if(report.narrowScroll.required&&report.narrowScroll.position===0)report.failures.push('Matrix cannot scroll');
  }
 }
 const printPage=await browser.newPage({viewport:{width:1360,height:1000}});
 await printPage.route('**/*',route=>{if(/^https?:/.test(route.request().url())){report.remoteRequests.push(route.request().url());return route.abort();}return route.continue();});
 await printPage.goto(url);await printPage.evaluate(()=>document.fonts.ready);
 await printPage.emulateMedia({media:'print'});
 await printPage.pdf({path:path.join(out,'scope.pdf'),preferCSSPageSize:true,printBackground:true});
 await printPage.close();
 if(report.remoteRequests.length)report.failures.push('Remote dependencies requested');
}finally{await browser.close();fs.writeFileSync(path.join(out,'browser.json'),JSON.stringify(report,null,2));}
console.log(JSON.stringify({failures:report.failures,items:report.matrix.length,snapshots:report.snapshots.length}));process.exit(report.failures.length?1:0);
