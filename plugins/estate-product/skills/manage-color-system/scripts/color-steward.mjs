#!/usr/bin/env node
// color-steward: measure, question and generate UI color systems.
// Commands:
//   audit <tokens.css|tokens.json> [--components file.css ...] [--source tokens.json] [--json out.json]
//   pair <fg> <bg>
//   palette <hex> [--name brand]
//   scheme <hex> [--variant tonal|neutral|fidelity|mono] [--error hex] [--json out.json]
//   cvd <hex> <hex> ...
// Runs on Node 18 or later with nothing to install: Material Color Utilities (Apache-2.0) and culori (MIT) are
// bundled in vendor/deps.mjs with their license notices; lib/apca.mjs implements APCA 0.0.98G-4g.
import fs from 'node:fs';
import { argbFromHex, hexFromArgb, Hct, TonalPalette, MaterialDynamicColors,
  SchemeTonalSpot, SchemeNeutral, SchemeFidelity, SchemeMonochrome, Blend,
  parse, converter, formatHex, differenceEuclidean,
  filterDeficiencyProt, filterDeficiencyDeuter, filterDeficiencyTrit } from './vendor/deps.mjs';
import { APCAcontrast, sRGBtoY } from './lib/apca.mjs';

const toOklch = converter('oklch');
const toRgb = converter('rgb');
const dOk = differenceEuclidean('oklab');

// ---------- color math ----------
export function lum(hex) {
  const c = toRgb(parse(hex));
  const f = v => (v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4);
  return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b);
}
export function wcag(fg, bg) {
  const a = lum(fg), b = lum(bg);
  return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
}
export function apca(fg, bg) {
  const rgb = h => { const c = toRgb(parse(h)); return [c.r, c.g, c.b].map(v => Math.round(v * 255)); };
  return Number(APCAcontrast(sRGBtoY(rgb(fg)), sRGBtoY(rgb(bg))));
}
export function tone(hex) { return Hct.fromInt(argbFromHex(hex)).tone; }
export function hct(hex) { const h = Hct.fromInt(argbFromHex(hex)); return { h: +h.hue.toFixed(1), c: +h.chroma.toFixed(1), t: +h.tone.toFixed(1) }; }
export function oklch(hex) { const o = toOklch(parse(hex)); return { l: +o.l.toFixed(3), c: +o.c.toFixed(3), h: o.h == null ? null : +o.h.toFixed(1) }; }
// composite rgba over a ground
export function over(color, ground) {
  const c = toRgb(parse(color)); const g = toRgb(parse(ground));
  const a = c.alpha ?? 1;
  return formatHex({ mode: 'rgb', r: c.r * a + g.r * (1 - a), g: c.g * a + g.g * (1 - a), b: c.b * a + g.b * (1 - a) });
}
const r2 = n => Math.round(n * 100) / 100;

// Text and graphic thresholds (WCAG 2.2 AA/AAA; APCA bronze guidance)
export const RULES = {
  body: { wcag: 4.5, apca: 75, label: 'body text' },
  large: { wcag: 3, apca: 60, label: 'large text 24px+ or 18.66px bold' },
  ui: { wcag: 3, apca: 45, label: 'control boundary, icon or chart mark' },
  aaa: { wcag: 7, apca: 90, label: 'high-contrast setting' },
};
export function judge(fg, bg) {
  const w = wcag(fg, bg), a = Math.abs(apca(fg, bg));
  const pass = {};
  for (const [k, r] of Object.entries(RULES)) pass[k] = w >= r.wcag;
  return { wcag: r2(w), apcaLc: r2(a), pass };
}

// ---------- token parsing ----------
export function parseTokens(css) {
  const blocks = [];
  const re = /([^{}]+)\{([^{}]*)\}/g; let m;
  while ((m = re.exec(css))) {
    const sel = m[1].replace(/\/\*[\s\S]*?\*\//g, '').trim();
    const body = m[2];
    const decl = /--([\w-]+)\s*:\s*([^;]+);\s*(?:\/\*([\s\S]*?)\*\/)?/g; let d; const vars = {};
    while ((d = decl.exec(body))) vars[d[1]] = { raw: d[2].trim(), note: (d[3] || '').trim() };
    if (Object.keys(vars).length) blocks.push({ sel, vars });
  }
  return blocks;
}
function themeOf(sel) {
  if (/data-contrast/.test(sel)) return 'scoped';
  if (/data-theme="?light"?\]/.test(sel)) return 'light';
  if (/data-theme="?dark"?\]/.test(sel) || /^:root\b/.test(sel)) return 'dark';
  return 'scoped';
}
export function buildThemes(blocks) {
  const themes = { dark: {}, light: {} };
  for (const b of blocks) {
    const t = themeOf(b.sel);
    if (t === 'scoped') continue;
    Object.assign(themes[t], b.vars);
  }
  // light inherits anything it does not redefine from the base block
  for (const [k, v] of Object.entries(themes.dark)) if (!themes.light[k]) themes.light[k] = v;
  return themes;
}
const isColor = s => { try { return !!parse(s); } catch { return false; } };
export function resolve(theme, name, seen = new Set()) {
  const v = theme[name]; if (!v) return null;
  if (seen.has(name)) return null; seen.add(name);
  const m = v.raw.match(/^var\(--([\w-]+)(?:\s*,\s*([^)]+))?\)$/);
  if (m) return resolve(theme, m[1], seen) ?? (m[2] && isColor(m[2]) ? formatHex(parse(m[2])) : null);
  return isColor(v.raw) ? formatHex(parse(v.raw)) : null;
}

// ---------- role map ----------
// The roles a complete UI color system answers for. Aliases map common names onto them.
export const ROLES = [
  { role: 'surface', why: 'page ground', aliases: ['surface', 'background', 'canvas', 'bg', 'page'] },
  { role: 'surface-container', why: 'cards, panels, menus raised off the ground', aliases: ['surface-raised', 'surface-container', 'surface-2', 'card'] },
  { role: 'surface-container-tiers', why: 'nested containers (lowest to highest) without inventing hexes', aliases: ['surface-container-low', 'surface-container-high', 'surface-sunken', 'surface-overlay'] },
  { role: 'on-surface', why: 'headings and body text', aliases: ['ink', 'on-surface', 'text', 'fg', 'foreground'] },
  { role: 'on-surface-variant', why: 'secondary text, labels, icons', aliases: ['ink-muted', 'on-surface-variant', 'text-muted', 'muted'] },
  { role: 'outline', why: 'control boundaries at 3:1', aliases: ['line-strong', 'outline', 'border-strong', 'border-control'] },
  { role: 'outline-variant', why: 'decorative dividers', aliases: ['line', 'outline-variant', 'border', 'divider'] },
  { role: 'primary', why: 'the one high-emphasis action', aliases: ['action', 'primary', 'accent', 'brand'] },
  { role: 'on-primary', why: 'text and icons on the action', aliases: ['on-action', 'on-primary', 'on-accent'] },
  { role: 'secondary', why: 'quieter actions and selected states', aliases: ['action-quiet', 'secondary', 'primary-container'] },
  { role: 'on-secondary', why: 'text on quieter actions', aliases: ['on-action-quiet', 'on-secondary', 'on-primary-container'] },
  { role: 'error', why: 'form errors and destructive actions; must exist even in a no-accent system', aliases: ['error', 'danger', 'negative', 'critical'] },
  { role: 'on-error', why: 'text on error fills', aliases: ['on-error', 'on-danger'] },
  { role: 'inverse-surface', why: 'toasts and snackbars that sit against the page', aliases: ['inverse-surface', 'surface-inverse', 'inverse'] },
  { role: 'focus', why: 'keyboard focus ring at 3:1 against the ground', aliases: ['focus-ring', 'focus'] },
  { role: 'state-layer', why: 'hover, pressed and selected overlays as one rule, not per-component rgba', aliases: ['state-hover', 'state-layer', 'hover', 'state-pressed'] },
  { role: 'disabled', why: 'disabled content and containers with a defined opacity', aliases: ['disabled', 'disabled-content', 'on-surface-disabled'] },
  { role: 'scrim', why: 'dims the page under dialogs', aliases: ['scrim', 'overlay'] },
  { role: 'data-series', why: 'chart series distinguishable without hue', aliases: ['data-1', 'chart-1'] },
];
export function mapRoles(names) {
  const set = new Set(names);
  return ROLES.map(r => ({ ...r, found: r.aliases.filter(a => set.has(a)) }));
}

// ---------- audit ----------
const PRIMITIVE = /^[a-z]+-\d{2,3}$/; // e.g. navy-700, mist-100
// A Design System type tokens.json: { color: { themes:[{id}], tokens:[{name, value:{theme:hex|"{alias}"}, usage}] } }
export function jsonToCss(json) {
  const j = typeof json === 'string' ? JSON.parse(json) : json; const themes = j.color.themes.map(t => t.id);
  const sel = id => id === 'dark' ? ':root, [data-theme="dark"]' : `[data-theme="${id}"]`;
  const order = ['dark', ...themes.filter(t => t !== 'dark')].filter(t => themes.includes(t));
  return order.map(id => `${sel(id)} {\n${j.color.tokens.map(t => {
    const v = typeof t.value === 'string' ? t.value : (t.value[id] ?? t.value[themes[0]]);
    const css = /^\{.+\}$/.test(v) ? `var(--${v.slice(1, -1)})` : v;
    return `  --${t.name}: ${css};${id === order[0] ? ` /* ${(t.usage || '').replace(/\*\//g, '')} */` : ''}`; }).join('\n')}\n}`).join('\n');
}
export function audit(tokensCss, componentCss = [], sourceJson = null) {
  if (/^\s*\{/.test(tokensCss)) tokensCss = jsonToCss(tokensCss);
  const blocks = parseTokens(tokensCss);
  const themes = buildThemes(blocks);
  const names = [...new Set([...Object.keys(themes.dark), ...Object.keys(themes.light)])];
  const colorNames = names.filter(n => resolve(themes.dark, n) || resolve(themes.light, n));
  const values = {};
  for (const t of ['dark', 'light']) { values[t] = {}; for (const n of colorNames) values[t][n] = resolve(themes[t], n); }
  const findings = [];
  const add = (sev, code, title, detail, fix, evidence = {}) => findings.push({ sev, code, title, detail, fix, evidence });

  // 1. pairs the system implies
  const pairs = [];
  for (const n of colorNames) if (n.startsWith('on-') && colorNames.includes(n.slice(3))) pairs.push([n, n.slice(3), 'body']);
  const TEXT = ['ink', 'ink-body', 'ink-muted', 'on-surface', 'on-surface-body', 'on-surface-variant', 'error'];
  const GROUNDS = ['surface', 'surface-raised', 'surface-container-lowest', 'surface-container-low', 'surface-container', 'surface-container-high', 'surface-container-highest', 'surface-dim', 'surface-bright'];
  for (const fg of TEXT) for (const bg of GROUNDS) if (colorNames.includes(fg) && colorNames.includes(bg)) pairs.push([fg, bg, 'body']);
  if (colorNames.includes('inverse-on-surface') && colorNames.includes('inverse-surface')) pairs.push(['inverse-on-surface', 'inverse-surface', 'body']);
  for (const fg of ['line-strong', 'focus-ring', 'outline', 'focus', 'primary']) for (const bg of ['surface', 'surface-container-lowest', 'surface-container']) if (colorNames.includes(fg) && colorNames.includes(bg)) pairs.push([fg, bg, 'ui']);
  for (const fg of colorNames.filter(n => /^data-\d/.test(n))) pairs.push([fg, 'surface', 'ui']);
  const pairResults = [];
  for (const t of ['dark', 'light']) for (const [fg, bg, use] of pairs) {
    const a = values[t][fg], b = values[t][bg]; if (!a || !b) continue;
    const j = judge(a, b); pairResults.push({ theme: t, fg, bg, use, fgHex: a, bgHex: b, ...j });
    if (!j.pass[use]) add(use === 'body' ? 'high' : 'medium', 'PAIR_FAILS', `${fg} on ${bg} fails ${RULES[use].label} in ${t}`,
      `${a} on ${b} measures ${j.wcag}:1 (APCA Lc ${j.apcaLc}); needs ${RULES[use].wcag}:1.`,
      use === 'body' ? `${bg} sits at tone ${Math.round(tone(b))}; set ${fg} at least 50 tones away, at tone ${tone(b) > 50 ? Math.max(0, Math.round(tone(b) - 50)) + ' or darker' : Math.min(100, Math.round(tone(b) + 50)) + ' or lighter'}.` : `Raise ${fg} to 3:1 or add a second cue: a gap, a direct label or a pattern.`, { theme: t, fg, bg, ratio: j.wcag });
  }

  // 1b. passes WCAG 2 but reads weak by APCA (common for light text on dark grounds, and for small labels)
  for (const p of pairResults.filter(p => p.use === 'body' && p.pass.body && p.apcaLc < 60))
    add('medium', 'APCA_WEAK', `${p.fg} on ${p.bg} passes WCAG (${p.wcag}:1) but measures APCA Lc ${p.apcaLc} in ${p.theme}`,
      `WCAG 2 overrates light-on-dark pairs. Lc ${p.apcaLc} suits text 24px and up; 12–14px labels want Lc 75 or more.`,
      `Keep ${p.fg} for large text, or lift it toward the body-text tone for labels under 16px.`, { theme: p.theme, fg: p.fg, bg: p.bg, apcaLc: p.apcaLc });

  // 2. claims written into comments
  // A claim reads "7.5:1 Night", "3:1 or more", "Below 3:1 ... on Day" or "17.6:1 in both themes".
  const THEME_WORD = { night: 'dark', dark: 'dark', day: 'light', light: 'light' };
  const checkClaims = (n, note, scope) => {
    const defPartner = n.startsWith('on-') && colorNames.includes(n.slice(3)) ? n.slice(3) : 'surface';
    const noteThemes = [...new Set([...note.toLowerCase().matchAll(/\b(night|day)\b/g)].map(x => THEME_WORD[x[1]]))];
    for (const m of note.matchAll(/(below\s+)?(\d+(?:\.\d+)?):1(\s+or more)?(?:,\s*Lc\s*\d+)?(?:\s+on\s+([a-z][\w-]*))?(?:\s+(?:(?:on|in)\s+)?(night|day|dark|light)\b)?/gi)) {
      const value = +m[2]; const op = m[1] ? 'max' : m[3] ? 'min' : 'eq';
      const explicit = m[4] && colorNames.includes(m[4]);
      // A note that names other color tokens without tying this ratio to one of them is ambiguous: skip it.
      const others = colorNames.filter(c => c !== n && new RegExp(`(^|[^\\w-])${c}([^\\w-]|$)`).test(note));
      if (!explicit && (others.length || /\bon it\b/i.test(note))) continue;
      const partner = explicit ? m[4] : defPartner;
      if (partner === n) continue;
      const named = scope ? [scope] : m[5] ? [THEME_WORD[m[5].toLowerCase()]] : /both themes/i.test(note) ? ['dark', 'light'] : noteThemes.length === 1 ? noteThemes : ['dark', 'light'];
      const results = named.map(t => { const a = values[t][n], b = values[t][partner]; return a && b ? { t, actual: wcag(a, b) } : null; }).filter(Boolean);
      const ok = r => op === 'min' ? r.actual >= value - 0.05 : op === 'max' ? r.actual <= value + 0.05 : Math.abs(r.actual - value) <= 0.35;
      const strict = scope || m[5] || named.length === 1 || /both themes/i.test(note);
      const holds = strict ? results.every(ok) : results.some(ok);
      if (!holds) add('high', 'CLAIM_WRONG', `${n} note claims ${m[0].trim()}; it measures ${results.map(r => `${r2(r.actual)}:1 ${r.t}`).join(', ')} against ${partner}`,
        `The documentation states a contrast the token does not deliver. People trust the note and ship the failure.`,
        `Compute every ratio in token notes from the values at build time; never type them by hand.`, { token: n, claim: m[0].trim(), partner, measured: results.map(r => ({ theme: r.t, ratio: r2(r.actual) })) });
    }
  };
  for (const n of colorNames) {
    const lightOwn = blocks.filter(b => themeOf(b.sel) === 'light').map(b => b.vars[n]?.note).filter(Boolean).pop();
    const darkOwn = blocks.filter(b => themeOf(b.sel) === 'dark').map(b => b.vars[n]?.note).filter(Boolean).pop();
    if (lightOwn && darkOwn) { checkClaims(n, darkOwn, 'dark'); checkClaims(n, lightOwn, 'light'); }
    else checkClaims(n, darkOwn || lightOwn || '', null);
  }

  // 3. primitives that change per theme
  for (const n of colorNames.filter(x => PRIMITIVE.test(x))) {
    const a = values.dark[n], b = values.light[n];
    if (a && b && a !== b) add('high', 'PRIMITIVE_DRIFT', `Palette step ${n} has two values: ${a} (dark) and ${b} (light)`,
      `A palette step is a fixed color. When it changes per theme, every rule that names it changes meaning silently, and the step number stops describing lightness.`,
      `Keep ${n} at one value in both themes. Let semantic tokens (ink-muted, on-action) pick a different step per theme.`, { token: n, dark: a, light: b });
  }

  // 4. step numbers that lie about lightness (higher number = darker)
  for (const t of ['dark', 'light']) {
    const prims = colorNames.filter(x => PRIMITIVE.test(x)).map(n => ({ n, step: +n.split('-').pop(), t: tone(values[t][n]) }));
    for (const p of prims) {
      const expected = 100 - p.step / 10; // 950 -> ~5, 100 -> ~90
      if (Math.abs(p.t - expected) > 25) add('medium', 'STEP_MISLABELED', `${p.n} is tone ${p.t.toFixed(0)} in ${t}; its name implies about ${expected.toFixed(0)}`,
        `Step numbers are how people pick colors without looking. A 950 that renders as mid-grey sends them to the wrong value.`,
        `Rename the step to match its tone, or set its value to the tone the number promises.`, { token: p.n, theme: t, tone: +p.t.toFixed(1) });
    }
  }

  // 5. role coverage
  const roles = mapRoles(names);
  for (const r of roles.filter(r => !r.found.length)) {
    const sev = ['error', 'on-error', 'state-layer', 'disabled'].includes(r.role) ? 'medium' : 'low';
    add(sev, 'ROLE_MISSING', `No token answers for ${r.role}`, `Needed for ${r.why}. Without it, components invent their own values.`,
      `Add a ${r.role} token (and its on- pair where it holds text).`, { role: r.role });
  }

  // 6. data series separation, including color-vision deficiency
  for (const t of ['dark', 'light']) {
    const series = colorNames.filter(n => /^data-\d/.test(n)).map(n => [n, values[t][n]]);
    const sims = { normal: c => c, protan: filterDeficiencyProt(1), deutan: filterDeficiencyDeuter(1), tritan: filterDeficiencyTrit(1) };
    for (let i = 0; i < series.length; i++) for (let j = i + 1; j < series.length; j++) {
      for (const [k, f] of Object.entries(sims)) {
        const d = dOk(f(parse(series[i][1])), f(parse(series[j][1])));
        if (d < 0.08) add(k === 'normal' ? 'medium' : 'low', 'SERIES_CLOSE', `${series[i][0]} and ${series[j][0]} are ${d.toFixed(3)} apart (OKLab, ${k}) in ${t}`,
          `Below 0.08 in OKLab, adjacent series read as one color at chart sizes.`, `Spread the ramp in lightness or label series directly.`, { theme: t, a: series[i][0], b: series[j][0], vision: k, distance: +d.toFixed(3) });
      }
    }
  }

  // 7. component CSS: literals, shadow token layers, hover that lowers contrast
  const tokenHexes = new Set(Object.values(values.dark).concat(Object.values(values.light)).filter(Boolean));
  for (const { name, css } of componentCss) {
    const lit = [...css.matchAll(/#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)/g)].map(x => x[0]);
    const off = [...new Set(lit.map(x => { try { return formatHex(parse(x)) ? x : null; } catch { return null; } }).filter(Boolean))];
    const unknown = off.filter(x => !tokenHexes.has(formatHex(parse(x))));
    const known = off.filter(x => tokenHexes.has(formatHex(parse(x))));
    if (known.length) add('medium', 'LITERAL_OF_TOKEN', `${known.length} hard-coded values in ${name} duplicate existing tokens`,
      `These will not follow a theme or a palette change: ${known.slice(0, 8).join(', ')}${known.length > 8 ? ' …' : ''}.`, `Replace each with var(--token).`, { file: name, values: known });
    if (unknown.length) add('high', 'LITERAL_OFF_SYSTEM', `${unknown.length} colors in ${name} exist nowhere in the token set`,
      `Off-system values: ${unknown.slice(0, 10).join(', ')}${unknown.length > 10 ? ' …' : ''}. Each is a decision nobody reviewed.`, `Promote the ones that are real roles to tokens; delete the rest.`, { file: name, values: unknown });
    const scoped = parseTokens(css).filter(b => themeOf(b.sel) === 'scoped' || /#root|\.mer-app/.test(b.sel));
    const before = findings.length;
    for (const b of scoped) {
      const clash = Object.keys(b.vars).filter(k => names.includes(k));
      if (clash.length) add('high', 'TOKEN_SHADOWED', `${b.sel.split('\n')[0]} redefines ${clash.length} root tokens (${clash.join(', ')})`,
        `Inside that scope, the same name means a different color. --surface there is the root's surface-raised.`, `Rename the scoped variables or delete the layer and use root tokens directly.`, { selector: b.sel, tokens: clash });
      const misnamed = Object.entries(b.vars).filter(([k, v]) => /amber|green|red|orange|yellow|purple/.test(k) && isColor(v.raw) && (oklch(formatHex(parse(v.raw))).c < 0.04));
      if (misnamed.length) add('medium', 'HUE_NAME_LIES', `${misnamed.map(x => '--' + x[0]).join(', ')} carry a hue name but hold greys`,
        `A token named for a hue that holds a neutral teaches people the wrong mental model.`, `Rename by role (selected, selected-soft) instead of by hue.`, { tokens: misnamed.map(x => x[0]) });
    }
    // one finding per code for a file: merge the per-block ones
    for (const code of ['TOKEN_SHADOWED', 'HUE_NAME_LIES']) {
      const hits = findings.slice(before).filter(f => f.code === code); if (hits.length < 2) continue;
      const keep = hits[0]; const key = code === 'TOKEN_SHADOWED' ? 'tokens' : 'tokens';
      keep.evidence[key] = [...new Set(hits.flatMap(h => h.evidence[key]))];
      keep.evidence.selectors = hits.map(h => h.evidence.selector).filter(Boolean);
      keep.title = code === 'TOKEN_SHADOWED' ? `The product kit redefines ${keep.evidence.tokens.length} root tokens (${keep.evidence.tokens.join(', ')}) in ${hits.length} blocks` : `${keep.evidence.tokens.map(t => '--' + t).join(', ')} carry a hue name but hold greys`;
      for (const h of hits.slice(1)) findings.splice(findings.indexOf(h), 1);
    }
    for (const m of css.matchAll(/([^{}]*:hover[^{}]*)\{[^}]*color:\s*var\(--(ink-muted|ink-3|text-muted)\)/g))
      add('low', 'HOVER_LOWERS_CONTRAST', `Hover drops text to a muted tone: ${m[1].trim()}`, `Hover should raise emphasis. Lowering contrast on hover reads as disabled.`, `Use a state layer on the container and keep the text color.`, { selector: m[1].trim() });
  }
  // 8. the generated stylesheet lags its source
  if (sourceJson) {
    const src = buildThemes(parseTokens(jsonToCss(sourceJson)));
    for (const t of ['dark', 'light']) for (const n of colorNames) {
      const a = values[t][n], b = resolve(src[t], n);
      if (a && b && a !== b) add('high', 'STALE_BUILD', `${n} in ${t} is ${a} in the stylesheet pages load, ${b} in the source`,
        `Pages read the generated stylesheet, so a fix made in the source does not reach them until the stylesheet is rebuilt.`,
        `Rebuild the stylesheet from the source and check it again.`, { token: n, theme: t, built: a, source: b });
    }
  }
  const order = { high: 0, medium: 1, low: 2 };
  findings.sort((a, b) => order[a.sev] - order[b.sev]);
  return { themes: values, pairs: pairResults, roles: roles.map(r => ({ role: r.role, found: r.found, why: r.why })), findings };
}

// ---------- generation ----------
export function palette(hex) {
  const h = Hct.fromInt(argbFromHex(hex));
  const p = TonalPalette.fromHueAndChroma(h.hue, h.chroma);
  const steps = [0, 4, 6, 10, 12, 17, 20, 22, 24, 30, 40, 50, 60, 70, 80, 87, 90, 92, 94, 95, 96, 98, 99, 100];
  return { seed: hex, hct: hct(hex), tones: Object.fromEntries(steps.map(t => [t, hexFromArgb(p.tone(t))])) };
}
const VARIANTS = { tonal: SchemeTonalSpot, neutral: SchemeNeutral, fidelity: SchemeFidelity, mono: SchemeMonochrome };
const ROLE_KEYS = ['primary', 'onPrimary', 'primaryContainer', 'onPrimaryContainer', 'secondary', 'onSecondary', 'secondaryContainer', 'onSecondaryContainer',
  'tertiary', 'onTertiary', 'error', 'onError', 'errorContainer', 'onErrorContainer', 'surface', 'surfaceDim', 'surfaceBright',
  'surfaceContainerLowest', 'surfaceContainerLow', 'surfaceContainer', 'surfaceContainerHigh', 'surfaceContainerHighest',
  'onSurface', 'onSurfaceVariant', 'outline', 'outlineVariant', 'inverseSurface', 'inverseOnSurface', 'inversePrimary', 'scrim'];
export function scheme(hex, { variant = 'tonal', errorHex } = {}) {
  const S = VARIANTS[variant] || SchemeTonalSpot; const src = Hct.fromInt(argbFromHex(hex));
  const out = {};
  for (const dark of [false, true]) for (const level of [0, 0.5, 1]) {
    const s = new S(src, dark, level); const key = `${dark ? 'dark' : 'light'}${level === 0 ? '' : level === 0.5 ? '-medium' : '-high'}`;
    out[key] = Object.fromEntries(ROLE_KEYS.filter(k => MaterialDynamicColors[k]).map(k => [k, hexFromArgb(MaterialDynamicColors[k].getArgb(s))]));
    if (errorHex) { // harmonize a brand error toward the source, then take M3 error tones
      const harm = hexFromArgb(Blend.harmonize(argbFromHex(errorHex), argbFromHex(hex)));
      const ep = TonalPalette.fromInt(argbFromHex(harm)); const tones = dark ? [80, 20, 30, 90] : [40, 100, 90, 10];
      if (level === 1) tones.splice(0, 4, ...(dark ? [90, 10, 80, 0] : [25, 100, 25, 100]));
      [out[key].error, out[key].onError, out[key].errorContainer, out[key].onErrorContainer] = tones.map(t => hexFromArgb(ep.tone(t)));
    }
  }
  return out;
}
// Find the tone in a palette that meets a contrast target against a ground, as close to `prefer` as possible.
// target: { wcag?: number, apca?: number }. Returns { tone, hex, wcag, apcaLc } or null.
export function fitTone(pal, bg, target, prefer) {
  const cands = [];
  for (let t = 0; t <= 100; t += 0.5) {
    const hex = hexFromArgb(pal.tone(t)); const w = wcag(hex, bg); const a = Math.abs(apca(hex, bg));
    if ((target.wcag == null || w >= target.wcag) && (target.apca == null || a >= target.apca)) cands.push({ tone: t, hex, wcag: r2(w), apcaLc: r2(a) });
  }
  cands.sort((x, y) => Math.abs(x.tone - prefer) - Math.abs(y.tone - prefer));
  return cands[0] || null;
}
export function paletteFrom(hue, chroma) { return TonalPalette.fromHueAndChroma(hue, chroma); }
export function harmonize(hex, toward) { return hexFromArgb(Blend.harmonize(argbFromHex(hex), argbFromHex(toward))); }
export function cvd(hexes) {
  const sims = { protan: filterDeficiencyProt(1), deutan: filterDeficiencyDeuter(1), tritan: filterDeficiencyTrit(1) };
  return Object.fromEntries(Object.entries(sims).map(([k, f]) => [k, hexes.map(h => formatHex(f(parse(h))))]));
}

// ---------- CLI ----------
if (import.meta.url === `file://${process.argv[1]}`) {
  const [cmd, ...a] = process.argv.slice(2);
  const flag = (n, d) => { const i = a.indexOf(n); return i >= 0 ? a[i + 1] : d; };
  const flags = n => a.flatMap((x, i) => (x === n ? [a[i + 1]] : []));
  let res;
  if (cmd === 'audit') res = audit(fs.readFileSync(a[0], 'utf8'), flags('--components').map(f => ({ name: f.split('/').pop(), css: fs.readFileSync(f, 'utf8') })), flag('--source') ? fs.readFileSync(flag('--source'), 'utf8') : null);
  else if (cmd === 'pair') res = judge(a[0], a[1]);
  else if (cmd === 'palette') res = palette(a[0]);
  else if (cmd === 'scheme') res = scheme(a[0], { variant: flag('--variant'), errorHex: flag('--error') });
  else if (cmd === 'cvd') res = cvd(a);
  else { console.log('commands: audit | pair | palette | scheme | cvd'); process.exit(1); }
  const out = flag('--json'); const s = JSON.stringify(res, null, 2);
  if (out) fs.writeFileSync(out, s); else console.log(s);
  if (cmd === 'audit') console.error(res.findings.map(f => `[${f.sev}] ${f.code}: ${f.title}`).join('\n'));
}
