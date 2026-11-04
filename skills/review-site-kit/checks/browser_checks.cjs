// Browser rules for a rendered review site. Usage: node browser_checks.cjs <dist>
// Prints a JSON list of {rule, status, detail}. Uses Playwright's bundled
// Chromium through the estate launch policy when RS_LAUNCH_POLICY is set.
'use strict';
const path = require('node:path');
const fs = require('node:fs');

async function main() {
  const dist = path.resolve(process.argv[2] || '.');
  let chromium;
  try { ({chromium} = require('playwright')); } catch (e) {
    console.log(JSON.stringify([{rule: 'B0', status: 'pending', detail: 'playwright is not installed'}]));
    return;
  }
  let options = {headless: true};
  if (process.env.RS_LAUNCH_POLICY) options = require(process.env.RS_LAUNCH_POLICY).launchOptions(process.env);
  const browser = await chromium.launch(options);
  const pages = fs.readdirSync(dist).filter(f => f.endsWith('.html'));
  const out = [];
  const add = (rule, problems) => out.push({rule, status: problems.length ? 'failed' : 'passed', detail: problems});
  const results = {err: [], layout: [], type: [], fold: [], dec: [], num: [], color: [], tint: [], status: []};
  for (const width of [1366, 390]) {
    const context = await browser.newContext({viewport: {width, height: 900}});
    for (const file of pages) {
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', e => errors.push(e.message));
      page.on('console', m => { if (m.type() === 'error' && !/favicon/.test(m.text())) errors.push(m.text()); });
      await page.goto('file://' + path.join(dist, file));
      await page.waitForTimeout(250);
      errors.forEach(e => results.err.push(`${file}@${width}: ${e}`));
      const r = await page.evaluate(() => {
        const visible = el => !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
        const own = el => [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
        const res = {};
        res.scroll = document.documentElement.scrollWidth - window.innerWidth;
        res.tables = [...document.querySelectorAll('table')].filter(visible).map((t, i) => {
          const sizes = new Set([...t.querySelectorAll('*')].filter(own).map(e => getComputedStyle(e).fontSize));
          return {i, sizes: [...sizes]};
        }).filter(t => t.sizes.length > 1);
        res.openFolds = [...document.querySelectorAll('details[data-fold]')].filter(d => d.open).map(d => d.id);
        res.decSummary = [...document.querySelectorAll('details.card > summary')].filter(s => s.querySelector('.owner,.answer-box')).length;
        const nums = [...document.querySelectorAll('.num')].filter(visible).map(n => { const b = n.getBoundingClientRect(); return Math.round(b.width) + 'x' + Math.round(b.height); });
        res.nums = [...new Set(nums)];
        const accent = getComputedStyle(document.documentElement).getPropertyValue('--accent').trim();
        const probe = document.createElement('span'); probe.style.color = accent; document.body.appendChild(probe);
        const accentRgb = getComputedStyle(probe).color; probe.remove();
        const allowed = 'a,nav,button,select,label,.tag,.num,.qm,.cls,svg,[aria-current],.seg,.tabs,.btn,.chip';
        res.accentText = [...document.querySelectorAll('#main *')].filter(e => own(e) && visible(e) && getComputedStyle(e).color === accentRgb && !e.closest(allowed))
          .slice(0, 5).map(e => e.tagName.toLowerCase() + (e.className ? '.' + String(e.className).split(' ')[0] : '') + ': ' + e.textContent.trim().slice(0, 40));
        const tiles = [...document.querySelectorAll('.lane:not([hidden]) .tile')].map(t => getComputedStyle(t).backgroundColor);
        res.tiles = tiles;
        res.white = getComputedStyle(document.body).backgroundColor;
        const T = (window.RS_DATA || {}).tickets || {};
        res.status = [...document.querySelectorAll('[data-status-of]')].filter(e => (T[e.dataset.statusOf] || {}).status !== e.textContent.trim()).map(e => e.dataset.statusOf);
        return res;
      });
      if (width === 390 && r.scroll > 1) results.layout.push(`${file}: page scrolls sideways by ${r.scroll}px at 390px`);
      r.tables.forEach(t => results.type.push(`${file}@${width}: table ${t.i} uses ${t.sizes.join(', ')}`));
      if (width === 1366) r.openFolds.forEach(id => results.fold.push(`${file}: ${id} is open on load`));
      if (r.decSummary) results.dec.push(`${file}: ${r.decSummary} closed cards show owner or answer`);
      if (r.nums.length > 1) results.num.push(`${file}@${width}: number circles measure ${r.nums.join(', ')}`);
      r.accentText.forEach(t => results.color.push(`${file}@${width}: accent text outside allowed places: ${t}`));
      if (r.tiles.length > 1 && (r.tiles[0] === r.white || r.tiles[0] === r.tiles[r.tiles.length - 1])) results.tint.push(`${file}: step tiles are not tinted step by step`);
      r.status.forEach(k => results.status.push(`${file}: ${k} shows a status that differs from the data`));
      await page.close();
    }
    await context.close();
  }
  await browser.close();
  add('R-ERR-1', [...new Set(results.err)]);
  add('R-LAYOUT-1', results.layout);
  add('R-TYPE-1', [...new Set(results.type)]);
  add('R-FOLD-1', results.fold);
  add('R-DEC-1', [...new Set(results.dec)]);
  add('R-NUM-1', results.num);
  add('R-COLOR-1', [...new Set(results.color)]);
  add('R-TINT-1', [...new Set(results.tint)]);
  add('R-STATUS-1', [...new Set(results.status)]);
  console.log(JSON.stringify(out));
}
main().catch(e => { console.log(JSON.stringify([{rule: 'B0', status: 'pending', detail: 'browser checks failed to run: ' + e.message}])); });
