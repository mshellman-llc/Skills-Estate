import fs from 'node:fs';
import {pathToFileURL} from 'node:url';
const [source, destination, expected] = process.argv.slice(2);
const report = {checks:{}, failures:[]};
let browser;
try {
  const {chromium} = await import(process.env.PW_MODULE);
  browser = await chromium.launch({headless:true, ...(process.env.PW_CHROMIUM ? {executablePath:process.env.PW_CHROMIUM} : {})});
  const context = await browser.newContext({viewport:{width:816,height:1056}});
  const page = await context.newPage();
  page.on('pageerror', error=>report.failures.push(error.message));
  await context.route('**/*',route=>{
    if (/^https?:/.test(route.request().url())) {
      report.failures.push('Unexpected remote resource');
      return route.abort();
    }
    return route.continue();
  });
  await page.goto(pathToFileURL(source).href);
  await page.emulateMedia({media:'print'});
  await page.evaluate(()=>document.fonts.ready);
  const layout = await page.evaluate(()=>{
    const problems=[];
    const pages=[...document.querySelectorAll('.page')];
    for(const [i,page] of pages.entries()) {
      const box=page.getBoundingClientRect();
      const footer=page.querySelector('.foot')?.getBoundingClientRect();
      for(const element of page.querySelectorAll('*')) {
        if(element.closest('.foot'))continue;
        const rect=element.getBoundingClientRect();
        if(rect.width===0||rect.height===0)continue;
        if(rect.left<box.left-1||rect.right>box.right+1||rect.bottom>box.bottom+1)
          problems.push(`Page ${i+1}: ${element.className||element.tagName} exceeds page bounds`);
        if(footer&&rect.bottom>footer.top-8)
          problems.push(`Page ${i+1}: ${element.className||element.tagName} collides with footer`);
      }
    }
    for(const image of document.images) if(!image.complete||!image.naturalWidth)problems.push('Unloaded image');
    const rootStyle=getComputedStyle(document.documentElement);
    const normalize=value=>value.replace(/["']/g,'').replace(/\s+/g,' ').trim().toLowerCase();
    const headingStack=normalize(rootStyle.getPropertyValue('--brand-font-headings'));
    const headingFonts=[...document.querySelectorAll('h1,h2,h3')].map(element=>getComputedStyle(element).fontFamily);
    if(!headingStack||!headingFonts.length||headingFonts.some(value=>normalize(value)!==headingStack))
      problems.push('Heading font does not match the selected profile');
    return {pages:pages.length,problems,headingFonts,headingStack};
  });
  report.checks.pageContainers=layout.pages===Number(expected);
  report.checks.noClipping=layout.problems.length===0;
  report.typography={headingFonts:layout.headingFonts,expectedHeadingStack:layout.headingStack};
  report.failures.push(...layout.problems);
  if(!report.checks.pageContainers)report.failures.push('Unexpected page container count');
  const pages=page.locator('.page');
  for(let i=0;i<await pages.count();i++) await pages.nth(i).screenshot({path:destination.replace(/\.pdf$/,`.page-${i+1}.png`),animations:'disabled'});
  await page.pdf({path:destination,printBackground:true,preferCSSPageSize:true,displayHeaderFooter:false});
} catch(error) {
  report.failures.push(error.message);
} finally {
  if(browser) await browser.close();
}
fs.writeFileSync(destination.replace(/\.pdf$/,'.checks.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
process.exitCode=report.failures.length?2:0;
