import fs from 'node:fs';
const policyURL = [new URL('../_runtime/brand-renderer/scripts/browser_launch_policy.cjs', import.meta.url),
  new URL('../../brand-renderer/scripts/browser_launch_policy.cjs', import.meta.url)].find(url => fs.existsSync(url));
if (!policyURL) throw new Error('Browser policy is missing. Rebuild with the declared brand runtime.');
const {default: browserPolicy} = await import(policyURL.href);
const pw = await import(process.env.PW_MODULE);
const [url, output] = process.argv.slice(2);
const report = { checks: {}, failures: [], widgets: {}, views: [] };
let browser;
function check(name, passed) {
  report.checks[name] = Boolean(passed);
  if (!passed) report.failures.push(name);
}
try {
  browser = await (pw.chromium ?? pw.default.chromium).launch(
    browserPolicy.launchOptions());
  const page = await browser.newPage({viewport:{width:1100,height:1000}});
  page.setDefaultTimeout(5000);
  await page.route(/^https?:\/\//, route => {
    report.failures.push('Unexpected external request: ' + route.request().url());
    return route.abort();
  });
  page.on('pageerror', error => report.failures.push(error.message));
  await page.goto(url);
  await page.evaluate(() => document.fonts.ready);
  check('noUnfilledSlots', !await page.locator('html').evaluate(
    el => /__(?:PALETTE|FONTS|MARK|LOGO)__|\{\{[A-Z_]+\}\}/.test(el.outerHTML)));
  check('substantiveSections', await page.locator('section').count() > 0);
  // Record each checked state as DOM measurements and extracted text. No image files are written.
  async function view(name, locator) {
    const target = locator ?? page.locator('body');
    const state = await target.evaluate(el => {
      const box = el.getBoundingClientRect();
      const clipped = [...el.querySelectorAll('*')].filter(node => node.getClientRects().length &&
        ['hidden', 'clip'].includes(getComputedStyle(node).overflowX) && node.scrollWidth > node.clientWidth + 1)
        .map(node => node.className || node.tagName);
      return {width: Math.round(box.width), right: Math.round(box.right), clipped,
        text: el.innerText.trim()};
    });
    state.name = name;
    state.viewport = page.viewportSize().width;
    if (state.right > state.viewport + 1) report.failures.push(name + ' extends past the viewport');
    if (state.clipped.length) report.failures.push(name + ' clips text in ' + state.clipped.slice(0, 3).join(', '));
    report.views.push(state);
  }
  await view('01-masthead');
  report.widgets.pricing = await page.locator('.pr').count();
  if (report.widgets.pricing) {
    const initial = await page.locator('#prRate').textContent();
    const buttons = page.locator('.pr-tb');
    check('pricingHasTwoTiers', await buttons.count() === 2);
    await buttons.nth(1).click();
    check('tierChangesRate', await page.locator('#prRate').textContent() !== initial);
    await page.locator('.pr-rb').last().click();
    check('roleChangesName', (await page.locator('#prRoleName').textContent()).trim() ===
      (await page.locator('.pr-rb').last().textContent()).trim());
    await page.locator('#prLow').fill('2');
    await page.locator('#prHigh').fill('4');
    const rate = Number((await page.locator('#prRate').textContent()).replace(/[^0-9.]/g,''));
    const totals = (await page.locator('#prCost').textContent()).split('–')
      .map(x => Number(x.replace(/[^0-9.]/g,'')));
    check('rateTimesDays', totals.length === 2 && totals[0] === rate*2 && totals[1] === rate*4);
    await view('02-pricing', page.locator('.pr'));
    await page.locator('#prHigh').fill('1');
    check('reversedRangeRejected', await page.locator('#prHigh').getAttribute('aria-invalid') === 'true');
    await page.locator('#prLow').fill('-1');
    check('negativeDaysRejected', await page.locator('#prLow').getAttribute('aria-invalid') === 'true');
    await page.locator('#prLow').fill('2');
    await page.locator('#prHigh').fill('4');
  }
  report.widgets.flow = await page.locator('.ifl-chip').count();
  if (await page.locator('.ifl-steps').count()) {
    check('flowHasSteps', report.widgets.flow > 0);
    for (let i=0; i<report.widgets.flow; i++) {
      const button = page.locator('.ifl-chip').nth(i);
      const title = await button.locator('.ct').textContent();
      await button.click();
      check('flowStep'+i, (await page.locator('.ifl-detail h4').textContent()).includes(title));
    }
    await view('03-flow', page.locator('.ifl-detail'));
  }
  report.widgets.ledger = await page.locator('.ldf-p').count();
  if (report.widgets.ledger) {
    for (const button of await page.locator('.ldf-p').all()) {
      const filter = await button.getAttribute('data-f');
      await button.click();
      const result = await page.locator('tr[data-disp]').evaluateAll((rows, filter) =>
        rows.every(row => (getComputedStyle(row).display !== 'none') ===
          (filter === 'all' || row.dataset.disp === filter)), filter);
      check('ledgerFilter_'+filter, result);
    }
    await page.locator('.ldf-p[data-f="all"]').click();
    await view('04-ledger', page.locator('.ldf'));
  }
  report.widgets.catalog = await page.locator('.ct-tb').count();
  if (report.widgets.catalog) {
    for (const button of await page.locator('.ct-tb').all()) {
      const view = await button.getAttribute('data-view');
      await button.click();
      check('catalogView_'+view, await page.locator('.ct-view').evaluateAll((views, chosen) =>
        views.every(v => (getComputedStyle(v).display !== 'none') === (v.dataset.view === chosen)), view));
    }
    await view('05-catalog', page.locator('.ctw'));
  }
  await page.evaluate(() => scrollTo(0,0));
  await page.setViewportSize({width:390,height:844});
  check('mobileNoPageOverflow', await page.evaluate(() =>
    document.documentElement.scrollWidth <= innerWidth + 1));
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  await view('06-mobile');
} catch (error) {
  report.failures.push(error.stack || error.message);
} finally {
  if (browser) await browser.close();
}
console.log(JSON.stringify(report));
process.exitCode = report.failures.length ? 2 : 0;
