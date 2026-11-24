// Visual gate, deterministic half: read a rendered HTML artifact's layout from the DOM.
// Usage: node layout_check.cjs artifact.html [--manifest parity.json] [--widths 1280,390] [--json out.json]
//        node layout_check.cjs --probe     (report the Playwright module, its version and the browser build)
// Checks sideways scroll, text past the viewport, clipped text, text contrast from
// computed colors, and text parity across widths and against the parity manifest.
// It writes no image files: the only output is the JSON report.
// Exit 0 pass, 1 failure, 2 browser unavailable or bad input.
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const {launchOptions} = require('./browser_launch_policy.cjs');

function parseArgs(argv) {
  const args = {widths: [1280, 390]};
  for (let i = 0; i < argv.length; i++) {
    const value = argv[i];
    if (value === '--probe') args.probe = true;
    else if (value === '--manifest') args.manifest = argv[++i];
    else if (value === '--json') args.json = argv[++i];
    else if (value === '--widths') args.widths = argv[++i].split(',').map(Number);
    else if (!args.file) args.file = value;
    else throw new Error('Unexpected argument: ' + value);
  }
  if (!args.file && !args.probe) throw new Error('Supply an HTML file');
  if (args.widths.some(width => !Number.isFinite(width) || width < 200)) throw new Error('Widths must be numbers of at least 200');
  return args;
}

// Name the Playwright install this check runs on: the module path, its version and the
// browser build, so a report can be reproduced.
function playwrightInfo() {
  const spec = process.env.PW_MODULE || 'playwright';
  let version = null;
  let moduleFolder = null;
  try {
    let start = null;
    if (spec.startsWith('file:')) start = require('node:url').fileURLToPath(spec);
    else if (path.isAbsolute(spec) || spec.startsWith('.')) start = path.resolve(spec);
    else start = path.dirname(require.resolve(spec + '/package.json'));
    for (let dir = fs.existsSync(start) && fs.statSync(start).isDirectory() ? start : path.dirname(start);
         dir && dir !== path.dirname(dir); dir = path.dirname(dir)) {
      const candidate = path.join(dir, 'package.json');
      if (fs.existsSync(candidate)) {
        const pkg = JSON.parse(fs.readFileSync(candidate, 'utf8'));
        if (/^(playwright|playwright-core)$/.test(pkg.name || '')) { version = pkg.version; moduleFolder = dir; break; }
      }
    }
  } catch (error) { /* the module may resolve only through import; leave the version unknown */ }
  return {module: moduleFolder || spec, version};
}

// Runs inside the page. Returns the layout facts for the current viewport.
function measure() {
  const own = el => [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
  const shown = el => {
    const style = getComputedStyle(el);
    return el.getClientRects().length && style.visibility !== 'hidden' && Number(style.opacity) !== 0;
  };
  const label = el => (el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + ': ' + el.textContent.trim().replace(/\s+/g, ' ')).slice(0, 80);
  const scrolls = el => {
    for (let node = el.parentElement; node; node = node.parentElement) {
      if (['auto', 'scroll'].includes(getComputedStyle(node).overflowX)) return true;
    }
    return false;
  };
  const rgba = value => {
    const parts = (value.match(/[\d.]+/g) || []).map(Number);
    return {r: parts[0] || 0, g: parts[1] || 0, b: parts[2] || 0, a: parts.length > 3 ? parts[3] : 1};
  };
  const background = el => {
    for (let node = el; node; node = node.parentElement) {
      const color = rgba(getComputedStyle(node).backgroundColor);
      if (color.a >= 0.99) return color;
      if (getComputedStyle(node).backgroundImage !== 'none') return null;
    }
    return {r: 255, g: 255, b: 255, a: 1};
  };
  const luminance = c => {
    const channel = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
    return 0.2126 * channel(c.r) + 0.7152 * channel(c.g) + 0.0722 * channel(c.b);
  };
  const ratio = (a, b) => {
    const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
    return (hi + 0.05) / (lo + 0.05);
  };
  const facts = {sidewaysScroll: Math.max(0, document.documentElement.scrollWidth - innerWidth),
    offCanvas: [], clipped: [], lowContrast: [], tokens: {}};
  for (const el of document.body.querySelectorAll('*')) {
    if (!own(el) || !shown(el) || el.closest('script,style,noscript,template')) continue;
    const box = el.getBoundingClientRect();
    if ((box.right > innerWidth + 1 || box.left < -1) && !scrolls(el)) facts.offCanvas.push(label(el));
    const style = getComputedStyle(el);
    const hidesX = ['hidden', 'clip'].includes(style.overflowX) && el.scrollWidth > el.clientWidth + 1;
    const hidesY = ['hidden', 'clip'].includes(style.overflowY) && el.scrollHeight > el.clientHeight + 1;
    if (hidesX || hidesY) facts.clipped.push(label(el));
    const back = background(el);
    if (back) {
      const size = parseFloat(style.fontSize);
      const large = size >= 24 || (size >= 18.66 && Number(style.fontWeight) >= 700);
      const value = ratio(rgba(style.color), back);
      if (value < (large ? 3 : 4.5)) facts.lowContrast.push(label(el) + ' (' + value.toFixed(2) + ':1)');
    }
  }
  const root = getComputedStyle(document.documentElement);
  for (const sheet of document.styleSheets) {
    let rules;
    try { rules = sheet.cssRules; } catch (error) { continue; }
    for (const rule of rules) {
      if (!rule.style) continue;
      for (const name of rule.style) {
        if (name.startsWith('--') && /colou?r|ink|text|bg|background|surface|accent|paper/i.test(name)) {
          const value = root.getPropertyValue(name).trim();
          if (value) facts.tokens[name] = value;
        }
      }
    }
  }
  facts.text = document.body.innerText.replace(/\s+/g, ' ').trim();
  return facts;
}

async function main() {
  let args;
  try { args = parseArgs(process.argv.slice(2)); } catch (error) {
    console.error(error.message);
    process.exit(2);
  }
  const file = args.file ? path.resolve(args.file) : null;
  const manifest = args.manifest ? JSON.parse(fs.readFileSync(args.manifest, 'utf8')) : {};
  let chromium;
  try {
    const pw = await import(process.env.PW_MODULE || 'playwright');
    chromium = pw.chromium ?? pw.default.chromium;
  } catch (error) {
    console.log(JSON.stringify({status: 'pending', reason: 'playwright is not installed', playwright: playwrightInfo()}));
    process.exit(2);
  }
  const options = launchOptions();
  const browser = await chromium.launch(options);
  const browserInfo = {playwright: playwrightInfo(), chromiumExecutable: options.executablePath || 'playwright default', chromiumVersion: browser.version()};
  if (args.probe) {
    await browser.close();
    console.log(JSON.stringify({status: 'ready', ...browserInfo}));
    process.exit(0);
  }
  const report = {artifact: file, writesImages: false, browser: browserInfo, widths: {}, failures: [], warnings: []};
  try {
    for (const width of args.widths) {
      const page = await browser.newPage({viewport: {width, height: 900}});
      await page.route(/^https?:\/\//, route => route.abort());
      await page.goto('file://' + file);
      await page.evaluate(() => document.fonts.ready);
      const facts = await page.evaluate(measure);
      report.widths[width] = facts;
      if (facts.sidewaysScroll > 1) report.failures.push(`${width}px: page scrolls sideways by ${facts.sidewaysScroll}px`);
      facts.offCanvas.forEach(item => report.failures.push(`${width}px: text past the viewport: ${item}`));
      facts.clipped.forEach(item => report.failures.push(`${width}px: clipped text: ${item}`));
      facts.lowContrast.forEach(item => report.failures.push(`${width}px: contrast below the floor: ${item}`));
      for (const phrase of manifest.requiredPhrases || []) {
        if (!facts.text.includes(phrase.replace(/\s+/g, ' ').trim())) report.failures.push(`${width}px: required phrase not visible: ${phrase}`);
      }
      for (const claim of manifest.protectedClaims || []) {
        for (const qualifier of claim.requiredQualifiers || []) {
          if (!facts.text.includes(qualifier)) report.failures.push(`${width}px: qualifier for ${claim.id} not visible: ${qualifier}`);
        }
      }
      await page.close();
    }
  } finally {
    await browser.close();
  }
  const [first, ...rest] = args.widths;
  for (const width of rest) {
    const wide = new Set(report.widths[first].text.split(' '));
    const narrow = new Set(report.widths[width].text.split(' '));
    const missing = [...wide].filter(word => !narrow.has(word));
    if (missing.length) report.warnings.push(`${width}px hides text shown at ${first}px: ${missing.slice(0, 12).join(' ')}`);
  }
  report.status = report.failures.length ? 'failed' : 'passed';
  const text = JSON.stringify(report, null, 2);
  if (args.json) fs.writeFileSync(args.json, text + '\n');
  console.log(text);
  process.exit(report.failures.length ? 1 : 0);
}

main().catch(error => {
  console.log(JSON.stringify({status: 'pending', reason: 'layout check failed to run: ' + error.message}));
  process.exit(2);
});
