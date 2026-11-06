#!/usr/bin/env node
/**
 * Deal Decision deck builder.
 *
 *   node build_ddoc.js manifest.json [-o out.pptx]
 *
 * Renders an approved slide manifest into a Deal Decision deck. It renders; it does not
 * author. Copy is approved in the skill workflow before this runs, and this file refuses
 * to invent a slide, a number, or a heading.
 *
 * Two modes, read from manifest.mode: "decision" (client is choosing between options) and
 * "confirmation" (one option, boundary confirmation). The slide skeleton for each is fixed
 * by the spec; this file enforces presence, not wording.
 */

const fs = require("fs");
const path = require("path");
// pptxgenjs and ./render are loaded lazily inside build(), so the preflight gate runs
// in environments that cannot install the renderer. The gate is the quality control;
// the renderer is environment-specific. Never couple them again.

// PptxGenJS expects colors without a leading hash. The shared runtime resolves
// those values from the selected Markdown profile.
const T = require("./brand_runtime");
const C = {
  deepNavy: T.bare.deepNavy,
  navy: T.bare.deepNavy,
  teal: T.bare.teal,
  tealPale: T.bare.tealPale,
  steel: T.bare.steelBlue,
  sand: T.bare.sand,
  ink: T.bare.fg,          // was 1C2433, not a brand colour
  body: T.bare.coolGray,   // was 39424F, not a brand colour
  white: T.bare.white,
};
const FONT = T.type.office;

// Human-readable footer labels. A client never sees a machine identifier.
const LABELS = {
  heard: "What we heard", recommendation: "Recommendation", comparison: "Options",
  option_block: "Option detail", outside_all: "Outside every option",
  need_from_you: "What we need", decision: "Decision", outcomes: "What you get",
  scope_in: "Scope", scope_out: "Scope boundaries", assumptions: "Assumptions",
  timeline: "Timeline", team: "Team", investment: "Investment", confirm: "Next step",
};

// Slide skeletons: the required slides. The builder verifies presence here and order
// against PREFERRED_ORDER below, which is the default narrative order.
const SKELETON_ALIASES = { scope: ["scope_in", "scope_out"], deliverables: ["outcomes"] };
const SKELETON = {
  decision: ["heard", "recommendation", "comparison", "option_block", "outside_all", "need_from_you", "decision"],
  confirmation: ["heard", "recommendation", "scope", "deliverables", "timeline", "team",
                 "investment", "assumptions", "need_from_you", "confirm"],
};
const PREFERRED_ORDER = {
  decision: ["heard", "stats", "exec_summary", "recommendation", "comparison",
             "decision_matrix", "option_block", "outside_all", "scope_out", "timeline", "team",
             "proof", "investment", "assumptions", "need_from_you", "decision"],
  confirmation: ["heard", "stats", "exec_summary", "recommendation", "outcomes",
                 "deliverables", "scope", "scope_in", "scope_out", "timeline", "team", "proof", "investment",
                 "assumptions", "need_from_you", "confirm"],
};

// Line budgets. A support line that overflows on the rendered slide is a build-time
// failure, so it is caught here rather than after the deck is in a client's hands.
const BUDGET = { title: 78, subtitle: 120, bullet: 150, card: 220, maxBullets: 7 };

function die(msg) {
  console.error(`BUILD FAILED: ${msg}`);
  process.exit(1);
}

function readManifest(p) {
  if (!fs.existsSync(p)) die(`manifest not found: ${p}`);
  let m;
  try {
    m = JSON.parse(fs.readFileSync(p, "utf8"));
  } catch (e) {
    die(`manifest is not valid JSON: ${e.message}`);
  }
  return m;
}

/** Collect every authored string, so the checks below see the whole deck. */
function allText(m) {
  const out = [];
  const walk = (v) => {
    if (typeof v === "string") out.push(v);
    else if (Array.isArray(v)) v.forEach(walk);
    else if (v && typeof v === "object") Object.values(v).forEach(walk);
  };
  walk({title: m.title, deck_lead: m.deck_lead, client: m.client, meta: m.meta,
        options: m.options, slides: m.slides || []});
  return out;
}

/**
 * Resolve the profile's declared logo with the rule render.js uses: a string or a
 * {path} object, resolved against the directory of the selected profile file.
 * Returns null when the profile declares no logo.
 */
function declaredLogoPath(brand = T) {
  const value = typeof brand.logo === "string" ? brand.logo : brand.logo?.path;
  return value ? path.resolve(path.dirname(brand.tokensPath), value) : null;
}

/** A declared logo that cannot be read is a hard failure, reported before rendering. */
function logoErrors(brand = T) {
  const file = declaredLogoPath(brand);
  if (!file) return [];
  try {
    if (!fs.statSync(file).isFile()) return [`declared logo is not a file: ${file}`];
    fs.closeSync(fs.openSync(file, "r"));
  } catch (e) {
    const why = e.code === "ENOENT" ? "does not exist" : `cannot be read (${e.code || e.message})`;
    return [`declared logo ${why}: ${file}`];
  }
  return [];
}

function preflight(m) {
  const errs = [...logoErrors()];
  const warns = [];

  if (!m.mode || !SKELETON[m.mode]) errs.push(`mode must be "decision" or "confirmation", got ${m.mode}`);
  if (!m.client) errs.push("manifest.client is required");
  if (!m.title) errs.push("manifest.title is required");
  if (!Array.isArray(m.slides) || !m.slides.length) errs.push("manifest.slides is required");
  if (errs.length) return { errs, warns };

  const options = m.options || [];
  if (m.mode === "decision") {
    if (options.length < 2) errs.push("decision mode needs at least two options; use confirmation mode for one");
    if (options.length > 3) errs.push(`decision mode allows at most three options, got ${options.length}. Four is a catalog`);
    if (!options.some((o) => o.recommended)) errs.push("no option is marked recommended. Lead with a recommendation, never a menu");
    if (options.filter((o) => o.recommended).length > 1) errs.push("more than one option is marked recommended");
  } else if (options.length > 1) {
    errs.push("confirmation mode takes one option");
  }

  // Skeleton presence and order.
  const kinds = m.slides.map((s) => s.kind);
  const want = SKELETON[m.mode];
  for (const k of want) {
    const alternatives = SKELETON_ALIASES[k];
    if (!kinds.includes(k) && !(alternatives && alternatives.every(kind => kinds.includes(kind))))
      errs.push(`missing required slide: ${k}`);
  }
  const pref = PREFERRED_ORDER[m.mode] || want;
  const seq = kinds.filter((k) => pref.includes(k));
  const ranked = seq.map((k) => pref.indexOf(k));
  for (let i = 1; i < ranked.length; i++) {
    if (ranked[i] < ranked[i - 1]) {
      warns.push(`slide order departs from the ${m.mode} reference order at "${seq[i]}". Intentional variants are fine; check it is deliberate`);
      break;
    }
  }

  // Decision mode: one option_block per option, identical geometry.
  if (m.mode === "decision") {
    const blocks = m.slides.filter((s) => s.kind === "option_block");
    if (blocks.length !== options.length) {
      errs.push(`${options.length} options but ${blocks.length} option_block slides. Every option gets the same slides`);
    }
    const optionNames = options.map(o => o.name);
    if (new Set(optionNames).size !== optionNames.length || optionNames.some(n => !n))
      errs.push("each option needs a unique name");
    for (const name of optionNames) {
      if (blocks.filter(b => b.option === name).length !== 1)
        errs.push(`option "${name}" needs exactly one matching option_block`);
    }
    const shape = (b) => Object.keys(b.sections || {}).sort().join(",");
    const shapes = new Set(blocks.map(shape));
    if (shapes.size > 1) {
      errs.push("option_block slides do not share an identical section set. Identical geometry is what makes the boundary the only visible difference");
    }
    // Word-count parity: no option may be visually favored by volume.
    const counts = blocks.map((b) => allText({ slides: [b] }).join(" ").split(/\s+/).length);
    const lo = Math.min(...counts), hi = Math.max(...counts);
    if (lo && hi / lo > 1.4) {
      warns.push(`option_block word counts range ${lo} to ${hi}. A spread past 1.4x reads as effort, not scope`);
    }
  }

  // A comparison slide renders option headers from m.options and its body from rows.
  // Without rows the slide is only a header strip, so rows are required, one cell per option.
  // false and 0 are meaningful cells; only absent, blank, or non-scalar values are rejected.
  m.slides.forEach((s, i) => {
    if (s.kind !== "comparison") return;
    const at = `comparison slide ${i + 1}`;
    if (!Array.isArray(s.rows) || !s.rows.length) {
      errs.push(`${at} has no rows. A comparison with only option names and prices compares nothing`);
      return;
    }
    s.rows.forEach((r, ri) => {
      const row = r && typeof r === "object" ? r : {};
      if (typeof row.label !== "string" || !row.label.trim()) errs.push(`${at} row ${ri + 1} has a blank label`);
      if (!Array.isArray(row.values)) {
        errs.push(`${at} row ${ri + 1} has no values array`);
        return;
      }
      if (row.values.length !== options.length)
        errs.push(`${at} row ${ri + 1} has ${row.values.length} cells for ${options.length} options`);
      row.values.forEach((v, ci) => {
        const ok = typeof v === "boolean" || (typeof v === "number" && Number.isFinite(v))
          || (typeof v === "string" && v.trim() !== "");
        if (!ok) errs.push(`${at} row ${ri + 1} cell ${ci + 1} is blank or not a string, number, or boolean`);
      });
    });
  });

  // Evidence classes on the "what we heard" slide.
  const heard = m.slides.find((s) => s.kind === "heard");
  if (heard) {
    const items = heard.items || [];
    if (!items.length) errs.push("the heard slide has no items");
    items.forEach((it, i) => {
      if (typeof it === "string") {
        errs.push(`heard item ${i + 1} is a bare string. Each needs {text, evidence, source}`);
        return;
      }
      if (!it.evidence) errs.push(`heard item ${i + 1} has no evidence class`);
      if (it.evidence && it.evidence !== "client_stated") {
        errs.push(`heard item ${i + 1} is ${it.evidence}. Only client_stated renders on this slide; move it to need_from_you as a question or drop it`);
      }
      if (!it.source) errs.push(`heard item ${i + 1} has no source. Attribute it to a person and a meeting or document`);
    });
  }

  // Figure tie-out.
  const figures = m.figures || [];
  figures.forEach((f, i) => {
    if (!f.quote_field) errs.push(`figure ${i + 1} (${f.label}) has no quote_field. Every number maps to a named quote field`);
    if (!m.quote_number && f.value != null) errs.push(`figure ${i + 1} carries a value but the manifest has no quote_number`);
    if (f.value != null && f.quote_field) {
      const snapshot = m.quote_snapshot || {};
      if (!Object.prototype.hasOwnProperty.call(snapshot, f.quote_field))
        errs.push(`figure ${i + 1} has no source value in quote_snapshot for ${f.quote_field}`);
      else if (snapshot[f.quote_field] !== f.value)
        errs.push(`figure ${i + 1} does not match quote_snapshot.${f.quote_field}`);
    }
  });

  // House voice, mechanical subset. The full gate is writing-diagnostics.
  const text = allText(m);
  text.forEach((t) => {
    if (t.includes("\u2014")) warns.push(`em dash in authored copy: "${t.slice(0, 50)}"`);
    if (t.includes("\u00A7")) errs.push(`section symbol in authored copy: "${t.slice(0, 60)}"`);
    if (/\bTBD\b|\[FLAG:/.test(t)) errs.push(`unresolved placeholder in authored copy: "${t.slice(0, 60)}"`);
  });

  // Line budgets.
  m.slides.forEach((s, i) => {
    if (!s.title || typeof s.title !== "string")
      errs.push(`slide ${i + 1} needs a title`);
    if (s.title && s.title.length > BUDGET.title) errs.push(`slide ${i + 1} title is ${s.title.length} chars, budget ${BUDGET.title}`);
    if (s.subtitle && s.subtitle.length > BUDGET.subtitle) errs.push(`slide ${i + 1} subtitle is ${s.subtitle.length} chars, budget ${BUDGET.subtitle}`);
    (s.bullets || []).forEach((b, j) => {
      const str = typeof b === "string" ? b : b.text || "";
      if (str.length > BUDGET.bullet) errs.push(`slide ${i + 1} bullet ${j + 1} is ${str.length} chars, budget ${BUDGET.bullet}`);
      if (str && !/[.?]$/.test(str.trim())) warns.push(`slide ${i + 1} bullet ${j + 1} is not a complete sentence: "${str.slice(0, 50)}"`);
    });
    if ((s.bullets || []).length > BUDGET.maxBullets) errs.push(`slide ${i + 1} has ${s.bullets.length} bullets, budget ${BUDGET.maxBullets}`);
  });

  return { errs, warns };
}

// ---------------------------------------------------------------- rendering
// Render layer lives in render.js so preflight and design evolve independently.

function build(m, out) {
  let pptxgen, cover, renderSlide;
  try {
    pptxgen = require("pptxgenjs");
    ({ cover, renderSlide } = require("./render"));
  } catch (e) {
    die(`the renderer is unavailable here (${String(e.message).split("\n")[0]}). The preflight gate still runs: re-run with --check to gate the copy, then build where pptxgenjs is installed.`);
  }
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5 in
  pres.author = m.author || "";
  pres.company = m.provider || "";
  pres.title = `${m.client} deal decision`;

  cover(pres, m);
  for (const slide of m.slides) renderSlide(pres, m, slide);
  return pres.writeFile({ fileName: out });
}

function main() {
  const argv = process.argv.slice(2);
  const checkOnly = argv.includes("--check");
  const args = argv.filter((a) => a !== "--check");
  if (!args.length) die("usage: node build_ddoc.js manifest.json [-o out.pptx] [--check]");
  const mpath = args[0];
  const oi = args.indexOf("-o");
  const m = readManifest(mpath);
  const out = oi >= 0 ? args[oi + 1]
    : path.join(path.dirname(mpath), `${(m.client || "build-deal-decision-deck").replace(/\s+/g, "-")}-DDOC.pptx`);

  const { errs, warns } = preflight(m);
  warns.forEach((w) => console.log(`  warn   ${w}`));
  if (errs.length) {
    errs.forEach((e) => console.error(`  FAIL   ${e}`));
    die(`${errs.length} preflight failures. Copy is approved before the build, so fix the manifest, not the deck.`);
  }

  // Report counts, never an adjective. A reader must see the numbers the gate measured.
  console.log(`  gate   ${errs.length} failures, ${warns.length} warnings across ${m.slides.length} slides`);
  if (checkOnly) {
    console.log("  check  preflight passed. No deck was built (--check).");
    return;
  }

  build(m, out).then(() => {
    console.log(`  mode   ${m.mode}`);
    console.log(`  slides ${m.slides.length + 1}`);
    console.log(`  warn   ${warns.length}`);
    console.log(`  built  ${out}`);
    console.log("  Next: validate.py, then rasterize and run the visual gate. Do not ship on a clean build alone.");
  }).catch((e) => die(e.message));
}

if (require.main === module) main();
module.exports = { preflight, build, allText, declaredLogoPath, logoErrors };
