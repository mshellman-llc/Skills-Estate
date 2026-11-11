#!/usr/bin/env python3
"""Build a standalone call brief with shared brand settings and inline icons.

Use --profile to select a canonical Markdown profile. The neutral profile needs
no external fonts or logos. --verify exercises the finished page; missing browser
support or a failed interaction returns a failing exit code.
"""

import argparse
import base64
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import shutil
import html as html_module
from brand_runtime import apply_profile

# Lucide paths, inlined so the brief works with no network. Stroke width 1.75 per brand.
ICONS = {
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "flag": '<path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" x2="4" y1="22" y2="15"/>',
    "zap": '<path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "chevron-right": '<path d="m9 18 6-6-6-6"/>',
    "git-branch": '<line x1="6" x2="6" y1="3" y2="15"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M18 9a9 9 0 0 1-9 9"/>',
    "alert-triangle": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    "box": '<path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/>',
    "server": '<rect width="20" height="8" x="2" y="2" rx="2" ry="2"/><rect width="20" height="8" x="2" y="14" rx="2" ry="2"/><path d="M6 6h.01"/><path d="M6 18h.01"/>',
    "layers": '<path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "eye": '<path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"/><circle cx="12" cy="12" r="3"/>',
    "arrow-right": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "trending-up": '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
}

ICON_TAG = re.compile(r'<i data-lucide="([a-z\-]+)"([^>]*)></i>')

ICON_CSS = (
    "\nsvg.ic{display:inline-block;vertical-align:middle;flex:0 0 auto;}"
    "\nsummary svg.ic.chev{margin-left:auto;color:var(--slate-blue);transition:transform .15s ease;}"
    "\ndetails[open] summary svg.ic.chev{transform:rotate(90deg);}"
)


def inline_icons(html: str) -> tuple:
    missing = set()

    def rep(m):
        name, attrs = m.group(1), m.group(2)
        if name not in ICONS:
            missing.add(name)
            return m.group(0)
        w = (re.search(r'width="(\d+)"', attrs) or [None, "16"])[1]
        h = (re.search(r'height="(\d+)"', attrs) or [None, w])[1]
        cls = re.search(r'class="([^"]*)"', attrs)
        cls = f' class="ic {cls.group(1)}"' if cls else ' class="ic"'
        sty = re.search(r'style="([^"]*)"', attrs)
        sty = f' style="{sty.group(1)}"' if sty else ""
        sw = "2.5" if 'stroke-width="2.5"' in attrs else "1.75"
        return (
            f'<svg{cls}{sty} width="{w}" height="{h}" viewBox="0 0 24 24" fill="none" '
            f'stroke="currentColor" stroke-width="{sw}" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>'
        )

    html, n = ICON_TAG.subn(rep, html)
    if n and "svg.ic{display" not in html:
        html = html.replace("</style>", ICON_CSS + "\n</style>", 1)
    # The template has no CDN script, but a hand-edited draft might have reintroduced one.
    html = re.sub(r'\s*<script src="https://unpkg\.com/lucide[^>]*></script>', "", html)
    html = html.replace("lucide.createIcons({attrs:{'stroke-width':1.75}});", "/* icons inlined */")
    html = html.replace("lucide.createIcons();", "/* icons inlined */")
    return html, n, missing


def fill_template(template, data):
    """Fill text slots and the five interaction registries from supplied data."""
    slots = data.get("slots", {})
    text = re.sub(r"<!--.*?-->", "", template, flags=re.S)
    missing = set()
    def replace(match):
        key = match.group(1)
        if key not in slots:
            missing.add(key)
            return match.group(0)
        value = str(slots[key])
        if key == "CALL_TIME_ISO":
            if not re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d(?::\d\d)?(?:Z|[+-]\d\d:\d\d)", value):
                raise ValueError("CALL_TIME_ISO must be an absolute ISO datetime with a timezone")
            return value
        return html_module.escape(value)
    # Brand slots belong to the shared runtime.
    text = re.sub(r"\{\{((?!(?:FONT|LOGO|BG)_)[A-Z_]+)\}\}", replace, text)
    for registry, key, empty in (("FN", "footnotes", "{}"), ("FLOW", "flow", "{}"),
                                 ("QS", "questions", "[]"), ("ASM", "assumptions", "[]"),
                                 ("DRILL", "drill", "[]")):
        value = data.get(key)
        if value is None:
            raise ValueError("Missing interaction registry: " + key)
        encoded = json.dumps(value, ensure_ascii=False).replace("<", "\\u003c")
        text = text.replace("const " + registry + " = " + empty + ";",
                            "const " + registry + " = " + encoded + ";")
    if missing:
        raise ValueError("Missing template text slots: " + ", ".join(sorted(missing)))
    return text


VERIFY_JS = r"""
// NODE_PATH does not apply to ES modules, so the caller passes an absolute module URL.
// Support CommonJS and ES module Playwright packages.
const pw = await import(process.env.PW_MODULE);
const chromium = (pw.chromium ?? pw.default?.chromium);
if (!chromium) { console.error('Could not load chromium from ' + process.env.PW_MODULE); process.exit(2); }
const [file, output] = process.argv.slice(2);
const b = await chromium.launch(process.env.PW_CHROMIUM ? { executablePath: process.env.PW_CHROMIUM } : {});
const p = await b.newPage({ viewport: { width: 1400, height: 1000 } });
p.setDefaultTimeout(5000);
await p.route(/^https?:\/\//, route => route.abort());
const errs = [];
p.on('pageerror', e => errs.push('PAGEERROR: ' + e.message));
p.on('console', m => { if (m.type() === 'error') errs.push('CONSOLE: ' + m.text()); });
await p.goto('file://' + file);
await p.evaluate(() => document.fonts.ready);
const s = await p.evaluate(() => {
  const q = x => document.querySelectorAll(x).length;
  const unresolved = (document.documentElement.innerHTML.match(/\{\{[A-Z_]+\}\}/g) || []);
  return {
    sections: q('section'), footnoteChips: q('.fn'), inlineAssumptions: q('.asm'),
    questions: q('.qitem'), assumptionRows: q('#asmTable tbody tr'), flowNodes: q('.fnode'),
    drillCards: (typeof DRILL !== 'undefined' ? DRILL.length : 0),
    footnoteKeys: (typeof FN !== 'undefined' ? Object.keys(FN).length : 0),
    icons: q('svg.ic'),
    danglingFootnotes: (typeof FN !== 'undefined'
      ? [...document.querySelectorAll('.fn')].map(e => e.dataset.fn).filter(k => !(k in FN)) : []),
    unresolvedSlots: [...new Set(unresolved)],
    fontFamily: getComputedStyle(document.body).fontFamily,
    fontsReady: document.fonts.status === 'loaded',
  };
});
// exercise the interactions
try {
  await p.locator('.fn').first().click();
  await p.waitForTimeout(200);
  s.footnotePopoverWorks = await p.evaluate(() => document.getElementById('fnpop').classList.contains('open'));
  await p.click('#drillBtn');
  await p.waitForTimeout(200);
  s.drillOpens = await p.evaluate(() => document.getElementById('drill').classList.contains('open'));
  await p.click('#drillReveal');
  s.drillAnswerWorks = await p.evaluate(() => document.getElementById('drillA').classList.contains('show') &&
    document.getElementById('drillA').textContent.length > 0);
  const beforeCard = await p.locator('#drillQ').textContent();
  await p.click('#drillNext');
  s.drillNextWorks = s.drillCards < 2 || beforeCard !== await p.locator('#drillQ').textContent();
  await p.click('#drillClose').catch(()=>{});
  await p.click('#asmBtn').catch(()=>{});
  s.assumptionToggleWorks = await p.evaluate(() => document.body.classList.contains('asm-hl'));
  s.flowDetailRenders = true;
  for (const node of await p.$$('.fnode')) {
    await node.click();
    const key = await node.getAttribute('data-flow');
    s.flowDetailRenders &&= await p.evaluate(key => FLOW[key] &&
      document.getElementById('flowdetail').textContent.includes(FLOW[key].t), key);
  }
  s.questionToggleWorks = false;
  if (s.questions) {
    await p.locator('.qitem').first().click();
    s.questionToggleWorks = await p.locator('.qitem').first().evaluate(e => e.classList.contains('done'));
  }
  await p.locator('#q').fill('no-match-synthetic-7f92');
  s.searchFilterWorks = await p.locator('[data-search-scope]:not(.hidden)').count() === 0;
  await p.locator('#q').fill('');
  s.searchResetWorks = await p.locator('[data-search-scope]:not(.hidden)').count() > 0;
} catch (e) { errs.push('INTERACTION: ' + e.message); }
await p.screenshot({ path: output + '/page.png', fullPage: true });
s.errors = errs;
console.log(JSON.stringify(s, null, 1));
await b.close();
process.exit(errs.length ? 2 : 0);
"""


def find_playwright():  # -> pathlib.Path or None; typed loosely so Python 3.9 can run this
    """Locate a node_modules containing playwright, walking up from cwd and from this
    script. Node resolves modules by walking up from the importing file, so a brief
    written to /tmp cannot see a playwright installed under the working directory."""
    configured = os.environ.get("ESTATE_NODE_MODULES") or os.environ.get("NODE_PATH", "")
    for value in configured.split(os.pathsep):
        if value and (pathlib.Path(value) / "playwright").is_dir():
            return pathlib.Path(value)
    seen = set()
    for start in (pathlib.Path.cwd(), pathlib.Path(__file__).resolve().parent, pathlib.Path.home()):
        for d in [start, *start.parents]:
            nm = d / "node_modules"
            if nm in seen:
                continue
            seen.add(nm)
            if (nm / "playwright").exists():
                return nm
    return None


def verify(path: pathlib.Path) -> int:
    """Render headlessly and report. An artifact that fails to render is worth nothing,
    and you cannot tell from reading the source."""
    attempt_root = path.resolve().parent / ".verification"
    attempt_root.mkdir(parents=True, exist_ok=True)
    attempt = pathlib.Path(tempfile.mkdtemp(prefix=path.stem + "-", dir=attempt_root))
    nm = find_playwright()
    node = os.environ.get("ESTATE_NODE") or shutil.which("node")
    if nm is None or not node:
        message = "Verification failed: Node and Playwright are required. Configure ESTATE_NODE and ESTATE_NODE_MODULES, then install Chromium with Playwright."
        (attempt / "console.log").write_text(message + "\n")
        print(message)
        return 2
    script = attempt / "verify.mjs"
    script.write_text(VERIFY_JS)
    entry = nm / "playwright" / "index.js"
    if not entry.exists():
        entry = nm / "playwright" / "index.mjs"
    env = {**os.environ, "PW_MODULE": entry.resolve().as_uri()}
    try:
        result = subprocess.run([node, str(script), str(path.resolve()), str(attempt)],
                                capture_output=True, text=True, timeout=180, env=env)
    except (OSError, subprocess.TimeoutExpired) as exc:
        (attempt / "console.log").write_text(str(exc) + "\n")
        print("Verification failed: " + str(exc))
        return 2
    (attempt / "console.log").write_text(result.stdout + result.stderr)
    try:
        report = json.loads(result.stdout)
    except ValueError:
        print("Verification failed; browser output saved in " + str(attempt))
        return 2
    failures = list(report.get("errors", []))
    for key in ("unresolvedSlots", "danglingFootnotes"):
        if report.get(key):
            failures.append(key + ": " + str(report[key]))
    for key in ("footnotePopoverWorks", "drillOpens", "drillAnswerWorks", "drillNextWorks",
                "assumptionToggleWorks", "flowDetailRenders", "questionToggleWorks",
                "searchFilterWorks", "searchResetWorks", "fontsReady"):
        if report.get(key) is not True:
            failures.append("failed interaction or font readiness: " + key)
    report["failures"] = failures
    report["exitCode"] = result.returncode or (2 if failures else 0)
    (attempt / "result.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    print("Verification outputs: " + str(attempt))
    return 2 if report["exitCode"] else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", nargs="?", help="draft html with content filled in")
    ap.add_argument("-o", "--output", help="output path for the finished brief")
    ap.add_argument("--verify", action="store_true", help="render-test after building")
    ap.add_argument("--verify-only", metavar="FILE", help="verify an existing file, no build")
    ap.add_argument("--profile", help="canonical Markdown brand profile")
    ap.add_argument("--data", type=pathlib.Path, help="JSON text slots and interaction registries for the supplied template")
    a = ap.parse_args()

    if a.verify_only:
        sys.exit(verify(pathlib.Path(a.verify_only)))

    if not a.input or not a.output:
        ap.error("input and --output are required unless using --verify-only")

    src = pathlib.Path(a.input)
    if not src.exists():
        sys.exit(f"No such file: {src}")

    try:
        source = src.read_text()
        if a.data:
            source = fill_template(source, json.loads(a.data.read_text()))
        html, profile = apply_profile(source, a.profile)
    except (ValueError, OSError) as exc:
        sys.exit("Build failed: " + str(exc))
    html, n_icons, missing = inline_icons(html)
    if missing:
        sys.exit(f"Unresolved icons: {sorted(missing)}; add their paths or select supported icons.")
    if re.search(r"\{\{[^{}]+\}\}", re.sub(r"<!--.*?-->", "", html, flags=re.S)):
        sys.exit("Unfilled content slots remain. Supply --data or finish the draft before building.")

    out = pathlib.Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    mb = out.stat().st_size / 1e6
    print(f"Built {out}: {mb:.2f} MB, {n_icons} icons inlined, profile {profile['name']}")
    if mb > 5:
        print("Warning: over 5 MB. Review embedded asset sizes for offline use.")

    sys.exit(verify(out) if a.verify else 0)


if __name__ == "__main__":
    main()
