/**
 * Deal Decision render layer, v2.
 *
 * Wide canvas (13.333 x 7.5), real type scale, section rail, and the visual devices the
 * decision decks use: navy dividers, big stat blocks, comparison matrices with the
 * recommended column washed, milestone roadmaps on a shared axis, role engagement windows,
 * weighted decision criteria, and assumption rows that name their own consequence.
 */

// Every color and font resolves from the selected canonical brand profile.
const fs = require("fs");
const path = require("path");
const BRAND = require("./brand_runtime");
const C = {
  navy: BRAND.bare.deepNavy, teal: BRAND.bare.teal, tealMid: BRAND.bare.tealMid,
  tealLight: BRAND.bare.tealLight, tealPale: BRAND.bare.tealPale, sand: BRAND.bare.sand,
  darkSand: BRAND.bare.darkSand, steel: BRAND.bare.steelBlue, white: BRAND.bare.white,
  bgAlt: BRAND.bare.offWhite,
  // were F4F6F9 / 4A5260 / 7A7E88, none of them brand colours
  stripe: BRAND.bare.offWhite, fg: BRAND.bare.fg, fg2: BRAND.bare.coolGray,
  muted: BRAND.bare.gray500, border: BRAND.bare.border,
};
const F = BRAND.type.office;
if (!F || F === "Application default") throw new Error("The selected brand profile must name an Office font in type.office.");

const W = 13.333, H = 7.5;
const PAD = 0.82;
const CW = W - PAD * 2;
const TOP = 1.62;
const BOT = 6.72;
const T = { cover: 46, title: 30, lead: 17, body: 12.5, stat: 40, statSm: 26, eyebrow: 9 };
const SEQ = [C.teal, C.navy];

/* ----------------------------------------------------------------- footer */
// Page numbers support navigation. A profile logo is optional and contained
// within the footer box without changing its aspect ratio.
const logoValue = typeof BRAND.logo === "string" ? BRAND.logo : BRAND.logo?.path;
const MARK = logoValue ? path.resolve(path.dirname(BRAND.tokensPath), logoValue) : null;
const MARK_WHITE = MARK;
if (MARK && !fs.existsSync(MARK)) throw new Error(`Selected profile logo is missing: ${MARK}`);

function footer(s, onNavy) {
  const y = 6.98, h = 0.2;
  const mark = onNavy ? MARK_WHITE : MARK;
  if (mark && fs.existsSync(mark)) {
    s.addImage({ path: mark, x: PAD, y, w: 1.4, h,
                 sizing: { type: "contain", w: 1.4, h }, objectName: "footer-logo" });
  }
  s.slideNumber = { x: W - PAD - 0.7, y, w: 0.7, h, fontFace: F, fontSize: 9,
                    color: onNavy ? C.white : C.muted, align: "right" };
}

function newSlide(pres, onNavy) {
  const s = pres.addSlide();
  s.background = { color: C.white };
  footer(s, onNavy === true);
  return s;
}

/* ---------------------------------------------------------------- chrome */

function rail(s, slide) {
  if (slide.section) {
    s.addText(String(slide.section.num || "").padStart(2, "0"), {
      x: PAD, y: 0.5, w: 0.34, h: 0.22, fontFace: F, fontSize: T.eyebrow, bold: true,
      color: C.teal, margin: 0, valign: "middle",
    });
    s.addText(String(slide.section.name || "").toUpperCase(), {
      x: PAD + 0.34, y: 0.5, w: 7, h: 0.22, fontFace: F, fontSize: T.eyebrow,
      color: C.muted, charSpacing: 1.6, margin: 0, valign: "middle",
    });
  } else if (slide.eyebrow) {
    s.addText(String(slide.eyebrow).toUpperCase(), {
      x: PAD, y: 0.5, w: 7, h: 0.22, fontFace: F, fontSize: T.eyebrow, bold: true,
      color: C.teal, charSpacing: 1.8, margin: 0, valign: "middle",
    });
  }
  if (slide.num != null) {
    s.addText(String(slide.num).padStart(2, "0"), {
      x: W - PAD - 1.2, y: 0.5, w: 1.2, h: 0.22, fontFace: F, fontSize: T.eyebrow,
      bold: true, color: C.steel, align: "right", margin: 0, valign: "middle",
    });
  }
}

const isPh = (t) => typeof t === "string" && /^\[.+\]$/.test(t.trim());

function head(s, slide) {
  rail(s, slide);
  s.addText(slide.title, {
    x: PAD, y: 0.82, w: CW, h: 0.56, fontFace: F, fontSize: T.title, bold: true,
    color: isPh(slide.title) ? C.tealMid : C.navy, italic: isPh(slide.title),
    charSpacing: -0.5, margin: 0, valign: "middle",
  });
  if (slide.subtitle) {
    s.addText(slide.subtitle, {
      x: PAD, y: 1.42, w: CW * 0.82, h: 0.44, fontFace: F, fontSize: T.lead,
      color: C.fg2, margin: 0, valign: "top",
    });
  }
  s.addShape("rect", { x: 0, y: H - 0.055, w: W, h: 0.055, fill: { color: C.navy } });
}

const cTop = (slide) => (slide.subtitle ? TOP + 0.34 : TOP - 0.12);

function card(s, x, y, w, h, o) {
  o = o || {};
  s.addShape("roundRect", {
    x, y, w, h, rectRadius: 0.04,
    fill: { color: o.fill || C.bgAlt },
    line: { color: o.line || C.border, width: o.lineW || 0.75 },
  });
  if (o.accent) s.addShape("rect", { x, y, w, h: 0.055, fill: { color: o.accent } });
}

function label(s, text, x, y, w, color) {
  s.addText(String(text).toUpperCase(), {
    x, y, w, h: 0.22, fontFace: F, fontSize: 8.4, bold: true,
    color: color || C.teal, charSpacing: 1.4, margin: 0, valign: "middle",
  });
}

function bullets(s, items, x, y, w, h, o) {
  o = o || {};
  if (!items || !items.length) return;
  const rows = items.map((b, i) => ({
    text: typeof b === "string" ? b : b.text,
    options: { bullet: { code: "2022", indent: 14 }, breakLine: i !== items.length - 1,
      paraSpaceAfter: o.space != null ? o.space : 9 },
  }));
  s.addText(rows, {
    x, y, w, h, fontFace: F, fontSize: o.size || T.body, color: o.color || C.fg2,
    margin: 0, valign: "top", lineSpacingMultiple: 1.18,
  });
}

/* ---------------------------------------------------------------- slides */

function cover(pres, m) {
  const s = newSlide(pres, true);
  s.background = { color: C.navy };
  s.addShape("rect", { x: W - 3.5, y: 0, w: 0.012, h: H, fill: { color: C.tealMid } });
  s.addShape("rect", { x: 0, y: 0, w: 0.1, h: H, fill: { color: C.teal } });
  if (m.template) {
    s.addShape("roundRect", { x: PAD, y: 1.02, w: 2.5, h: 0.32, rectRadius: 0.04,
      fill: { color: C.tealMid } });
    s.addText("PLAYBOOK TEMPLATE", { x: PAD, y: 1.02, w: 2.5, h: 0.32, fontFace: F,
      fontSize: 8, bold: true, color: C.white, align: "center", valign: "middle",
      charSpacing: 1.4, margin: 0 });
  }
  s.addText("DEAL DECISION DOCUMENT", {
    x: PAD, y: 1.5, w: 8, h: 0.26, fontFace: F, fontSize: 10.5, bold: true,
    color: C.tealLight, charSpacing: 3, margin: 0,
  });
  s.addText(m.title, {
    x: PAD, y: 1.95, w: 8.5, h: 2.0, fontFace: F, fontSize: T.cover, bold: true,
    color: C.white, charSpacing: -1.2, margin: 0, valign: "top", lineSpacingMultiple: 0.94,
  });
  s.addShape("rect", { x: PAD, y: 4.16, w: 1.1, h: 0.06, fill: { color: C.teal } });
  if (m.deck_lead) {
    s.addText(m.deck_lead, {
      x: PAD, y: 4.42, w: 8.2, h: 1.2, fontFace: F, fontSize: 14, color: C.white,
      margin: 0, valign: "top", lineSpacingMultiple: 1.3,
    });
  }
  (m.meta || []).slice(0, 4).forEach((it, i) => {
    const x = PAD + i * 2.5;
    s.addText(String(it.k).toUpperCase(), {
      x, y: 6.15, w: 2.35, h: 0.2, fontFace: F, fontSize: 8, bold: true,
      color: C.white, charSpacing: 1.4, margin: 0,
    });
    s.addText(it.v, {
      x, y: 6.37, w: 2.35, h: 0.42, fontFace: F, fontSize: 11.5, color: C.white,
      margin: 0, valign: "top",
    });
  });
  s.addText(m.client, {
    x: W - 3.5, y: 1.5, w: 2.7, h: 0.4, fontFace: F, fontSize: 15, bold: true,
    color: C.white, margin: 0,
  });
  s.addText([m.date, m.quote_number, "Confidential"].filter(Boolean).join("\n"), {
    x: W - 3.5, y: 1.98, w: 2.7, h: 1.3, fontFace: F, fontSize: 10, color: C.white,
    margin: 0, valign: "top", lineSpacingMultiple: 1.55,
  });
  return s;
}

function divider(pres, m, slide) {
  const s = newSlide(pres, true);
  s.background = { color: C.navy };
  s.addShape("rect", { x: 0, y: 0, w: 0.1, h: H, fill: { color: C.teal } });
  s.addText(String(slide.num || "").padStart(2, "0"), {
    x: PAD, y: 2.4, w: 2.4, h: 1.1, fontFace: F, fontSize: 64, bold: true,
    color: C.white, margin: 0, valign: "middle",
  });
  s.addText(slide.title, {
    x: PAD, y: 3.5, w: 9.6, h: 0.8, fontFace: F, fontSize: 34, bold: true,
    color: C.white, margin: 0, valign: "middle",
  });
  if (slide.subtitle) {
    s.addText(slide.subtitle, {
      x: PAD, y: 4.34, w: 8.4, h: 0.9, fontFace: F, fontSize: 14, color: C.white,
      margin: 0, valign: "top", lineSpacingMultiple: 1.3,
    });
  }
  return s;
}

function execSummary(pres, m, slide) {
  const s = newSlide(pres);
  head(s, slide);
  const y = cTop(slide), h = BOT - y, gap = 0.3, w = (CW - gap) / 2;
  card(s, PAD, y, w, h, { fill: C.sand, accent: C.steel });
  label(s, slide.left_label || "Current state", PAD + 0.3, y + 0.3, w - 0.6, C.muted);
  s.addText(slide.left_lead || "", {
    x: PAD + 0.3, y: y + 0.6, w: w - 0.6, h: 0.8, fontFace: F, fontSize: 15, bold: true,
    color: C.navy, margin: 0, valign: "top", lineSpacingMultiple: 1.14,
  });
  bullets(s, slide.left, PAD + 0.3, y + 1.5, w - 0.6, h - 1.8, { size: 11.5 });

  const x2 = PAD + w + gap;
  card(s, x2, y, w, h, { fill: C.tealPale, accent: C.teal });
  label(s, slide.right_label || "Recommended path", x2 + 0.3, y + 0.3, w - 0.6, C.teal);
  s.addText(slide.right_lead || "", {
    x: x2 + 0.3, y: y + 0.6, w: w - 0.6, h: 0.8, fontFace: F, fontSize: 15, bold: true,
    color: C.navy, margin: 0, valign: "top", lineSpacingMultiple: 1.14,
  });
  bullets(s, slide.right, x2 + 0.3, y + 1.5, w - 0.6, h - 1.8, { size: 11.5 });
  return s;
}

function stats(pres, m, slide) {
  const s = newSlide(pres);
  head(s, slide);
  const st = slide.stats || [];
  const y = cTop(slide), gap = 0.26;
  const w = (CW - gap * (st.length - 1)) / Math.max(st.length, 1);
  const h = 2.2;
  st.forEach((it, i) => {
    const x = PAD + i * (w + gap);
    card(s, x, y, w, h, { fill: i === 0 ? C.navy : C.sand });
    s.addText(String(it.value), {
      x: x + 0.26, y: y + 0.32, w: w - 0.52, h: 0.92, fontFace: F,
      fontSize: String(it.value).length > 6 ? T.statSm : T.stat, bold: true,
      color: i === 0 ? C.tealLight : C.teal, charSpacing: -1, margin: 0, valign: "middle",
    });
    s.addText(it.label, {
      x: x + 0.26, y: y + 1.26, w: w - 0.52, h: 0.36, fontFace: F, fontSize: 12,
      bold: true, color: i === 0 ? C.white : C.navy, margin: 0, valign: "top",
    });
    if (it.note) {
      s.addText(it.note, {
        x: x + 0.26, y: y + 1.62, w: w - 0.52, h: 0.44, fontFace: F, fontSize: 9.5,
        color: i === 0 ? C.white : C.muted, margin: 0, valign: "top",
      });
    }
  });
  if (slide.callout) {
    const cy = y + h + 0.4;
    s.addShape("rect", { x: PAD, y: cy, w: 0.05, h: Math.max(BOT - cy, 0.4),
      fill: { color: C.teal } });
    s.addText(slide.callout, {
      x: PAD + 0.3, y: cy, w: CW - 0.3, h: Math.max(BOT - cy, 0.4), fontFace: F,
      fontSize: 13, color: C.fg2, margin: 0, valign: "top", lineSpacingMultiple: 1.25,
    });
  }
  return s;
}

function heard(pres, m, slide) {
  const s = newSlide(pres);
  head(s, slide);
  const items = slide.items || [];
  const y0 = cTop(slide), gap = 0.22;
  const h = Math.min(1.25, (BOT - y0 - gap * (items.length - 1)) / Math.max(items.length, 1));
  items.forEach((it, i) => {
    const y = y0 + i * (h + gap);
    card(s, PAD, y, CW, h, { fill: C.sand });
    s.addShape("rect", { x: PAD, y, w: 0.055, h, fill: { color: C.teal } });
    s.addText(it.text, {
      x: PAD + 0.36, y, w: CW - 0.72, h, fontFace: F, fontSize: 15, color: C.navy,
      valign: "middle", margin: 0, lineSpacingMultiple: 1.16,
    });
  });
  s.addNotes(items.map((i) => `${i.text}  [${i.evidence}] ${i.source}`).join("\n"));
  return s;
}

/* ------------------------------------------- slide minimum type, fit checks */
// Comparison and option-detail text never drops below the selected profile's slide
// minimum. Geometry follows the text; when finite content cannot fit at that size the
// slide refuses with a message instead of shrinking or clipping.
const MIN_PT = (() => {
  const raw = BRAND.type.slide_min_pt;
  if (raw == null) return 18;
  const v = Number(raw);
  if (!Number.isFinite(v) || v <= 0) throw new Error(`type.slide_min_pt must be a positive number of points, got ${raw}`);
  return v;
})();
const TYPE_BOT = 6.88; // text on these two slides may use the band above the page number

const NARROW = new Set(" .,;:'!|iljtfI()[]-/·");
function charEm(ch, bold) {
  let em = NARROW.has(ch) ? 0.28 : /[MW]/.test(ch) ? 0.88 : ch === "m" ? 0.83 : ch === "w" ? 0.72
    : /[A-Z]/.test(ch) ? 0.7 : ch === "—" ? 1 : /[0-9●]/.test(ch) ? 0.58 : 0.53;
  return bold ? em * 1.07 : em;
}
const textEm = (str, bold) => [...str].reduce((a, ch) => a + charEm(ch, bold), 0);

/** Conservative greedy word-wrap estimate: the number of lines `text` needs in `widthIn`. */
function wrapLines(text, size, widthIn, bold) {
  const lineW = widthIn * 72 * 0.96;
  const em = (str) => textEm(str, bold) * size;
  const space = em(" ");
  let lines = 0;
  for (const para of String(text).split("\n")) {
    let cur = 0, n = 1;
    for (const word of para.split(/\s+/).filter(Boolean)) {
      const ww = em(word);
      if (ww > lineW) {
        if (cur > 0) n++;
        n += Math.ceil(ww / lineW) - 1;
        cur = ww % lineW || lineW;
      } else if (cur === 0) cur = ww;
      else if (cur + space + ww <= lineW) cur += space + ww;
      else { n++; cur = ww; }
    }
    lines += n;
  }
  return lines;
}
const textH = (text, size, widthIn, bold, mult) =>
  (wrapLines(text, size, widthIn, bold) * size * 1.2 * (mult || 1)) / 72 + 0.04;
const longestWordIn = (text, size, bold) =>
  Math.max(0, ...String(text).split(/\s+/).map((w) => (textEm(w, bold) * size) / 72));
const lineH = (size) => (size * 1.2) / 72;

function fitError(what, detail) {
  return new Error(`${what} cannot fit at the ${MIN_PT} pt slide minimum without dropping or shrinking text: ${detail}. ` +
    "The selected profile's minimum governs: split the content across slides or obtain an approved copy revision.");
}

const cellText = (v) => (v === true || v === "yes" ? "●" : v === false || v === "no" ? "—" : String(v));

function comparison(pres, m, slide) {
  const s = newSlide(pres);
  head(s, slide);
  const opts = m.options || [], rows = slide.rows || [];
  const sz = MIN_PT, padX = 0.18, padY = 0.08;
  const y0 = cTop(slide);
  const rec = opts.findIndex((o) => o.recommended);
  const subOf = (o) => [o.duration, o.investment].filter(Boolean).join("   ·   ");

  // The label column is as narrow as its longest unbreakable word allows, so option
  // columns get the width. Everything below is measured at the minimum size.
  const labelW = Math.min(4.2, Math.max(1.9,
    Math.max(0, ...rows.map((r) => longestWordIn(r.label, sz, true))) * 1.04 + 0.3));
  const colW = (CW - labelW) / Math.max(opts.length, 1);
  const cellW = colW - 2 * padX, labelTextW = labelW - 0.2;

  const nameH = Math.max(0, ...opts.map((o) => textH(o.name, sz, cellW, true)));
  const subH = Math.max(0, ...opts.map((o) => (subOf(o) ? textH(subOf(o), sz, cellW, true) : 0)));
  const badgeW = (textEm("RECOMMENDED", true) * sz) / 72 + (11 * 0.5) / 72 + 0.3;
  const badgeH = lineH(sz) + 0.14;
  if (rec >= 0 && badgeW > cellW)
    throw fitError(`comparison "${slide.title}"`, `the RECOMMENDED marker needs ${badgeW.toFixed(2)} in but a column offers ${cellW.toFixed(2)} in`);
  const headerH = nameH + subH + (rec >= 0 ? badgeH + 0.08 : 0);
  const ruleY = y0 + headerH + 0.12;
  const rowsTop = ruleY + 0.08;

  const heights = rows.map((r, ri) => {
    const own = [textH(r.label, sz, labelTextW, true)];
    (r.values || []).forEach((v, i) => own.push(textH(cellText(v), sz, cellW, i === rec)));
    return Math.max(0.54, Math.max(...own) + 2 * padY);
  });
  const need = heights.reduce((a, b) => a + b, 0);
  if (rowsTop + need > TYPE_BOT)
    throw fitError(`comparison "${slide.title}"`,
      `${rows.length} rows and ${opts.length} options need ${(rowsTop - y0 + need).toFixed(2)} in of height but ${(TYPE_BOT - y0).toFixed(2)} in is available`);

  if (rec >= 0) {
    s.addShape("rect", { x: PAD + labelW + rec * colW, y: y0 - 0.08, w: colW,
      h: TYPE_BOT - y0 + 0.08, fill: { color: C.tealPale } });
  }
  opts.forEach((o, i) => {
    const x = PAD + labelW + i * colW, isRec = i === rec;
    s.addText(o.name, {
      x: x + padX, y: y0, w: cellW, h: nameH, fontFace: F, fontSize: sz, bold: true,
      color: isRec ? C.teal : C.navy, margin: 0, valign: "top",
    });
    const sub = subOf(o);
    if (sub) {
      s.addText(sub, {
        x: x + padX, y: y0 + nameH, w: cellW, h: subH, fontFace: F, fontSize: sz,
        bold: true, color: isRec ? C.teal : C.muted, margin: 0, valign: "top",
      });
    }
    if (isRec) {
      const by = y0 + nameH + subH + 0.08;
      s.addShape("roundRect", { x: x + padX, y: by, w: badgeW, h: badgeH,
        rectRadius: 0.04, fill: { color: C.teal } });
      s.addText("RECOMMENDED", {
        x: x + padX, y: by, w: badgeW, h: badgeH, fontFace: F, fontSize: sz, bold: true,
        color: C.white, align: "center", valign: "middle", charSpacing: 0.5, margin: 0,
      });
    }
  });
  let y = rowsTop;
  s.addShape("rect", { x: PAD, y: ruleY, w: CW, h: 0.012, fill: { color: C.navy } });
  rows.forEach((r, ri) => {
    const rowH = heights[ri];
    if (ri % 2 === 1) {
      s.addShape("rect", { x: PAD, y, w: CW, h: rowH, fill: { color: C.stripe } });
      if (rec >= 0) s.addShape("rect", { x: PAD + labelW + rec * colW, y, w: colW, h: rowH,
        fill: { color: C.tealPale } });
    }
    s.addText(r.label, {
      x: PAD + 0.1, y, w: labelTextW, h: rowH, fontFace: F, fontSize: sz, bold: true,
      color: C.navy, valign: "middle", margin: 0,
    });
    (r.values || []).forEach((v, i) => {
      const x = PAD + labelW + i * colW, isRec = i === rec;
      const no = v === false || v === "no";
      s.addText(cellText(v), {
        x: x + padX, y, w: cellW, h: rowH, fontFace: F,
        fontSize: sz, bold: isRec,
        color: no ? C.steel : isRec ? C.teal : C.fg2, valign: "middle", margin: 0,
      });
    });
    y += rowH;
  });
  return s;
}

function decisionMatrix(pres, m, slide) {
  const s = newSlide(pres);
  head(s, slide);
  const cols = slide.columns || (m.options || []).map((o) => o.name);
  const crit = slide.criteria || [];
  const rec = slide.recommended_index != null ? slide.recommended_index
    : (m.options || []).findIndex((o) => o.recommended);
  const y0 = cTop(slide), labelW = 4.0, wtW = 0.95;
  const colW = (CW - labelW - wtW) / cols.length;
  if (rec >= 0) {
    s.addShape("rect", { x: PAD + labelW + wtW + rec * colW, y: y0 - 0.08, w: colW,
      h: BOT - y0 + 0.08, fill: { color: C.tealPale } });
  }
  label(s, "Criterion", PAD + 0.1, y0, labelW, C.muted);
  label(s, "Weight", PAD + labelW, y0, wtW, C.muted);
  cols.forEach((c, i) => {
    s.addText(c, {
      x: PAD + labelW + wtW + i * colW + 0.14, y: y0 - 0.06, w: colW - 0.28, h: 0.32,
      fontFace: F, fontSize: 11.5, bold: true, color: i === rec ? C.teal : C.navy,
      valign: "middle", margin: 0,
    });
  });
  let y = y0 + 0.42;
  s.addShape("rect", { x: PAD, y: y - 0.06, w: CW, h: 0.012, fill: { color: C.navy } });
  const rowH = Math.min(0.58, (BOT - 0.8 - y) / Math.max(crit.length, 1));
  crit.forEach((c, ri) => {
    if (ri % 2 === 1) {
      s.addShape("rect", { x: PAD, y, w: CW, h: rowH, fill: { color: C.stripe } });
      if (rec >= 0) s.addShape("rect", { x: PAD + labelW + wtW + rec * colW, y, w: colW,
        h: rowH, fill: { color: C.tealPale } });
    }
    s.addText(c.name, {
      x: PAD + 0.1, y, w: labelW - 0.2, h: rowH, fontFace: F, fontSize: 11, bold: true,
      color: C.navy, valign: "middle", margin: 0,
    });
    s.addText(c.weight, {
      x: PAD + labelW, y, w: wtW, h: rowH, fontFace: F, fontSize: 10.5, color: C.muted,
      valign: "middle", margin: 0,
    });
    const max = Math.max(...(c.scores || [1]));
    (c.scores || []).forEach((v, i) => {
      const x = PAD + labelW + wtW + i * colW;
      const barW = (colW - 0.62) * (Number(v) / (max || 1));
      s.addShape("rect", { x: x + 0.14, y: y + rowH / 2 - 0.07, w: colW - 0.62, h: 0.14,
        fill: { color: C.border } });
      s.addShape("rect", { x: x + 0.14, y: y + rowH / 2 - 0.07, w: Math.max(barW, 0.03),
        h: 0.14, fill: { color: i === rec ? C.teal : C.steel } });
      s.addText(String(v), {
        x: x + colW - 0.46, y, w: 0.4, h: rowH, fontFace: F, fontSize: 10,
        bold: i === rec, color: i === rec ? C.teal : C.fg2, align: "right",
        valign: "middle", margin: 0,
      });
    });
    y += rowH;
  });
  if (slide.totals) {
    s.addShape("rect", { x: PAD, y: y + 0.08, w: CW, h: 0.012, fill: { color: C.navy } });
    s.addText("Weighted score", {
      x: PAD + 0.1, y: y + 0.18, w: labelW + wtW, h: 0.44, fontFace: F, fontSize: 11.5,
      bold: true, color: C.navy, valign: "middle", margin: 0,
    });
    slide.totals.forEach((v, i) => {
      s.addText(String(v), {
        x: PAD + labelW + wtW + i * colW + 0.14, y: y + 0.18, w: colW - 0.28, h: 0.44,
        fontFace: F, fontSize: i === rec ? 21 : 15, bold: true,
        color: i === rec ? C.teal : C.steel, valign: "middle", margin: 0,
      });
    });
  }
  return s;
}

const sectionItems = (v) =>
  (Array.isArray(v) ? v : [v]).map((b) => (typeof b === "string" ? b : String(b.text)));

/**
 * One grid for every option block in the deck, chosen from the largest section set and
 * the longest text across all of them, so the option boundary is the only visible
 * difference. The default grid is tried first, then denser reflows.
 */
function optionGeometry(m, slide) {
  const sz = MIN_PT, gap = 0.26, space = 7;
  const blocks = (m.slides || []).filter((b) => b.kind === "option_block");
  if (!blocks.includes(slide)) blocks.push(slide);
  const y0 = cTop({ subtitle: blocks.some((b) => b.subtitle) });
  const n = Math.max(1, ...blocks.map((b) => Object.keys(b.sections || {}).length));
  const tries = [...new Set([n > 3 ? 2 : n, 2, 1, 3].filter((c) => c >= 1 && c <= n))];
  const tail = 0.26;
  let worst = null;
  for (const cols of tries) {
    const w = (CW - gap * (cols - 1)) / cols, rows = Math.ceil(n / cols);
    const h = (TYPE_BOT - y0 - gap * (rows - 1)) / rows;
    const textW = w - 0.52 - 14 / 72;
    // Every card reserves the same label band, sized for the longest heading in the deck.
    const labelLines = Math.max(1, ...blocks.flatMap((b) =>
      Object.keys(b.sections || {}).map((k) => wrapLines(k.toUpperCase(), sz, w - 0.52, true))));
    const labelH = labelLines * lineH(sz) + 0.04, lead = 0.26 + labelH + 0.14;
    let ok = true;
    for (const b of blocks) for (const [k, v] of Object.entries(b.sections || {})) {
      const items = sectionItems(v);
      const body = items.reduce((a, t) => a + textH(t, sz, textW, false, 1.18), 0)
        + (items.length - 1) * (space / 72);
      const needed = lead + body + tail;
      if (needed > h) { ok = false; worst = { option: b.option || b.title, section: k, needed, h, cols }; }
    }
    if (ok) return { cols, rows, w, h, gap, y0, labelH, lead, space };
  }
  throw fitError(`option detail "${worst.option}"`,
    `section "${worst.section}" needs ${worst.needed.toFixed(2)} in but its card offers ${worst.h.toFixed(2)} in with ${worst.cols} column(s)`);
}

function optionBlock(pres, m, slide) {
  const s = newSlide(pres);
  const opt = (m.options || []).find((o) => o.name === slide.option) || {};
  const g = optionGeometry(m, slide);
  head(s, slide);
  if (opt.recommended) {
    const bw = (textEm("RECOMMENDED", true) * MIN_PT) / 72 + (11 * 0.5) / 72 + 0.3;
    const bh = lineH(MIN_PT) + 0.14;
    if (bh > 0.74 || wrapLines(slide.title, T.title, CW - bw - 0.2, true) > 1)
      throw fitError(`option detail "${slide.option}"`, "the title and the RECOMMENDED marker collide in the header");
    const by = 0.82 + (0.56 - bh) / 2;
    s.addShape("roundRect", { x: W - PAD - bw, y: by, w: bw, h: bh, rectRadius: 0.04,
      fill: { color: C.teal } });
    s.addText("RECOMMENDED", {
      x: W - PAD - bw, y: by, w: bw, h: bh, fontFace: F, fontSize: MIN_PT, bold: true,
      color: C.white, align: "center", valign: "middle", charSpacing: 0.5, margin: 0,
    });
  }
  const sections = slide.sections || {};
  Object.keys(sections).forEach((k, i) => {
    const col = i % g.cols, row = Math.floor(i / g.cols);
    const x = PAD + col * (g.w + g.gap), y = g.y0 + row * (g.h + g.gap);
    card(s, x, y, g.w, g.h, { fill: C.sand });
    s.addText(String(k).toUpperCase(), {
      x: x + 0.26, y: y + 0.26, w: g.w - 0.52, h: g.labelH, fontFace: F,
      fontSize: MIN_PT, bold: true, color: C.teal, charSpacing: 0.6, margin: 0,
      valign: "top",
    });
    bullets(s, sectionItems(sections[k]), x + 0.26, y + g.lead, g.w - 0.52,
      g.h - g.lead - 0.26, { size: MIN_PT, space: g.space });
  });
  return s;
}

function recommendation(pres, m, slide) {
  const s = newSlide(pres);
  head(s, slide);
  const y0 = cTop(slide), heroW = 4.0;
  card(s, PAD, y0, heroW, BOT - y0, { fill: C.navy, line: C.navy });
  s.addText("RECOMMENDATION", {
    x: PAD + 0.34, y: y0 + 0.4, w: heroW - 0.68, h: 0.24, fontFace: F, fontSize: 8.6,
    bold: true, color: C.tealLight, charSpacing: 1.6, margin: 0,
  });
  s.addText(slide.pick || (m.options || []).find(option => option.recommended)?.name || "", {
    x: PAD + 0.34, y: y0 + 0.76, w: heroW - 0.68, h: 1.2, fontFace: F, fontSize: 26,
    bold: true, color: C.white, margin: 0, valign: "top", lineSpacingMultiple: 1.02,
  });
  if (slide.pick_note) {
    s.addText(slide.pick_note, {
      x: PAD + 0.34, y: y0 + 2.06, w: heroW - 0.68, h: 1.8, fontFace: F, fontSize: 12,
      color: C.white, margin: 0, valign: "top", lineSpacingMultiple: 1.28,
    });
  }
  const reasons = slide.reasons || (slide.bullets || []).map(item => ({
    head: typeof item === "string" ? item : item.text, body: "",
  }));
  const x2 = PAD + heroW + 0.32, w2 = CW - heroW - 0.32, gap = 0.2;
  const rh = (BOT - y0 - gap * (reasons.length - 1)) / Math.max(reasons.length, 1);
  reasons.forEach((r, i) => {
    const y = y0 + i * (rh + gap);
    card(s, x2, y, w2, rh, { fill: C.white });
    s.addShape("roundRect", { x: x2 + 0.26, y: y + 0.26, w: 0.3, h: 0.3, rectRadius: 0.05,
      fill: { color: C.teal } });
    s.addText(String(i + 1), {
      x: x2 + 0.26, y: y + 0.26, w: 0.3, h: 0.3, fontFace: F, fontSize: 10.5, bold: true,
      color: C.white, align: "center", valign: "middle", margin: 0,
    });
    s.addText(r.head || "", {
      x: x2 + 0.68, y: y + 0.22, w: w2 - 0.96, h: 0.34, fontFace: F, fontSize: 14,
      bold: true, color: C.navy, margin: 0, valign: "middle",
    });
    s.addText(r.body || "", {
      x: x2 + 0.68, y: y + 0.6, w: w2 - 0.96, h: rh - 0.82, fontFace: F, fontSize: 11.5,
      color: C.fg2, margin: 0, valign: "top", lineSpacingMultiple: 1.2,
    });
  });
  return s;
}

function scopeSplit(pres, m, slide) {
  const s = newSlide(pres);
  head(s, slide);
  const y = cTop(slide), h = BOT - y, gap = 0.5, w = (CW - gap) / 2;
  const ins = slide.in_scope || [], outs = slide.out_scope || [];

  label(s, slide.in_label || "Included", PAD, y, w, C.teal);
  s.addShape("rect", { x: PAD, y: y + 0.3, w, h: 0.02, fill: { color: C.teal } });
  const ih = Math.min(0.5, (h - 0.5) / Math.max(ins.length, 1));
  ins.forEach((t, i) => {
    const iy = y + 0.46 + i * ih;
    s.addShape("rect", { x: PAD + 0.02, y: iy + 0.17, w: 0.1, h: 0.1, fill: { color: C.teal } });
    s.addText(typeof t === "string" ? t : t.text, {
      x: PAD + 0.3, y: iy, w: w - 0.34, h: ih, fontFace: F, fontSize: 12, color: C.navy,
      valign: "top", margin: 0, lineSpacingMultiple: 1.16 });
  });

  const x2 = PAD + w + gap;
  label(s, slide.out_label || "Not included", x2, y, w, C.muted);
  s.addShape("rect", { x: x2, y: y + 0.3, w, h: 0.02, fill: { color: C.darkSand } });
  const oh = Math.min(0.66, (h - 0.5 - (slide.callout ? 0.6 : 0)) / Math.max(outs.length, 1));
  outs.forEach((o, i) => {
    const oy = y + 0.46 + i * oh;
    const txt = typeof o === "string" ? o : o.item;
    const route = typeof o === "string" ? null : o.route;
    s.addText(txt, {
      x: x2, y: oy, w: w, h: 0.3, fontFace: F, fontSize: 12, color: C.fg2,
      valign: "top", margin: 0 });
    if (route) s.addText(route, {
      x: x2, y: oy + 0.26, w: w, h: 0.28, fontFace: F, fontSize: 9.5, bold: true,
      color: C.teal, valign: "top", margin: 0 });
  });
  if (slide.callout) {
    s.addText(slide.callout, {
      x: x2, y: BOT - 0.5, w, h: 0.5, fontFace: F, fontSize: 10.5, italic: true,
      color: C.muted, valign: "middle", margin: 0 });
  }
  return s;
}

const cum = (ph, i) => ph.slice(0, i).reduce((a, p) => a + (p.weeks || 1), 0);

function roadmap(pres, m, slide) {
  const s = newSlide(pres);
  head(s, slide);
  const ph = slide.phases || [];
  const total = ph.reduce((a, p) => a + (p.weeks || 1), 0);
  const y0 = cTop(slide) + 0.55;
  const trackY = y0 + 0.5, trackH = 0.66;
  let x = PAD;
  s.addText(`${total} weeks`, {
    x: PAD, y: y0 - 0.5, w: 3, h: 0.3, fontFace: F, fontSize: 15, bold: true,
    color: C.navy, margin: 0,
  });
  ph.forEach((p, i) => {
    const w = (CW * (p.weeks || 1)) / total;
    s.addShape("rect", { x, y: trackY, w: w - 0.035, h: trackH,
      fill: { color: SEQ[i % SEQ.length] } });
    s.addText(String(i + 1).padStart(2, "0"), {
      x: x + 0.14, y: trackY + 0.07, w: 0.5, h: 0.22, fontFace: F, fontSize: 8,
      bold: true, color: C.white, margin: 0,
    });
    s.addText(p.name, {
      x: x + 0.14, y: trackY + 0.28, w: w - 0.24, h: 0.32, fontFace: F, fontSize: 11.5,
      bold: true, color: C.white, margin: 0, valign: "middle",
    });
    const a = cum(ph, i) + 1, b = cum(ph, i) + (p.weeks || 1);
    s.addText(a === b ? `Wk ${a}` : `Wk ${a}\u2013${b}`, {
      x, y: trackY + trackH + 0.12, w: w - 0.035, h: 0.24, fontFace: F, fontSize: 9,
      color: C.muted, align: "center", margin: 0,
    });
    if (p.detail) {
      s.addText(p.detail, {
        x, y: trackY + trackH + 0.4, w: w - 0.12, h: 0.8, fontFace: F, fontSize: 9.5,
        color: C.fg2, margin: 0, valign: "top", lineSpacingMultiple: 1.15,
      });
    }
    if (p.milestone) {
      s.addShape("diamond", { x: x + w / 2 - 0.1, y: trackY - 0.36, w: 0.2, h: 0.2,
        fill: { color: C.teal } });
      s.addText(p.milestone, {
        x: x + w / 2 - 1.15, y: trackY - 0.7, w: 2.3, h: 0.28, fontFace: F, fontSize: 9,
        bold: true, color: C.teal, align: "center", valign: "bottom", margin: 0,
      });
    }
    x += w;
  });
  return s;
}

function engagement(pres, m, slide) {
  const s = newSlide(pres);
  head(s, slide);
  const roles = slide.roles || [], weeks = slide.weeks || 12;
  const y0 = cTop(slide) + 0.2, nameW = 3.0;
  const trackX = PAD + nameW, trackW = CW - nameW;
  const rowH = Math.min(0.54, (BOT - y0 - 0.5) / Math.max(roles.length, 1));
  const ticks = Math.min(weeks, 8);
  for (let i = 0; i <= ticks; i++) {
    const wx = trackX + (trackW * i) / ticks;
    s.addText(`Wk ${Math.round((weeks * i) / ticks)}`, {
      x: wx - 0.3, y: y0 - 0.32, w: 0.6, h: 0.22, fontFace: F, fontSize: 8,
      color: C.muted, align: "center", margin: 0,
    });
    s.addShape("rect", { x: wx, y: y0, w: 0.006, h: roles.length * rowH,
      fill: { color: C.border } });
  }
  roles.forEach((r, i) => {
    const y = y0 + i * rowH;
    s.addText(r.role, {
      x: PAD, y, w: nameW - 0.2, h: rowH, fontFace: F, fontSize: 11, bold: true,
      color: C.navy, valign: "middle", margin: 0,
    });
    (r.windows || []).forEach((wn) => {
      const x = trackX + (trackW * (wn.from - 1)) / weeks;
      const w = (trackW * (wn.to - wn.from + 1)) / weeks;
      s.addShape("roundRect", { x, y: y + rowH / 2 - 0.11,
        w: Math.max(w - 0.03, 0.06), h: 0.22, rectRadius: 0.03,
        fill: { color: wn.weight === "support" ? C.tealPale : SEQ[i % SEQ.length] } });
    });
  });
  if (slide.legend) {
    s.addText(slide.legend, {
      x: PAD, y: BOT - 0.3, w: CW, h: 0.32, fontFace: F, fontSize: 9.5,
      color: C.muted, margin: 0, valign: "top",
    });
  }
  return s;
}

function investment(pres, m, slide) {
  const s = newSlide(pres);
  head(s, slide);
  const y0 = cTop(slide), heroW = 4.6;
  card(s, PAD, y0, heroW, 2.5, { fill: C.navy, line: C.navy });
  s.addText(slide.amount || "", {
    x: PAD + 0.34, y: y0 + 0.38, w: heroW - 0.68, h: 1.05, fontFace: F, fontSize: 44,
    bold: true, color: C.tealLight, charSpacing: -1.4, margin: 0, valign: "middle",
  });
  if (slide.qualifier) {
    s.addText(slide.qualifier, {
      x: PAD + 0.34, y: y0 + 1.48, w: heroW - 0.68, h: 0.86, fontFace: F, fontSize: 12,
      color: C.white, margin: 0, valign: "top", lineSpacingMultiple: 1.28,
    });
  }
  const terms = slide.terms || [];
  const x2 = PAD + heroW + 0.32, w2 = CW - heroW - 0.32;
  const tw = (w2 - 0.24) / 2;
  terms.forEach((t, i) => {
    const tx = x2 + (i % 2) * (tw + 0.24);
    const ty = y0 + Math.floor(i / 2) * 0.86;
    label(s, t.k, tx, ty, tw, C.muted);
    s.addText(t.v, {
      x: tx, y: ty + 0.26, w: tw, h: 0.48, fontFace: F, fontSize: 15, bold: true,
      color: C.navy, margin: 0, valign: "top",
    });
  });
  const dist = slide.distribution || [];
  if (dist.length) {
    const total = dist.reduce((a, d) => a + d.value, 0) || 1;
    let x = PAD;
    const by = y0 + 2.9;
    label(s, slide.distribution_label || "Where the hours go", PAD, by - 0.34, CW, C.muted);
    dist.forEach((d, i) => {
      const w = (CW * d.value) / total;
      s.addShape("rect", { x, y: by, w: w - 0.025, h: 0.52,
        fill: { color: SEQ[i % SEQ.length] } });
      s.addText(d.name, {
        x, y: by + 0.6, w: w - 0.025, h: 0.24, fontFace: F, fontSize: 9.5, bold: true,
        color: C.navy, align: "center", margin: 0,
      });
      s.addText(String(d.value), {
        x, y: by + 0.82, w: w - 0.025, h: 0.22, fontFace: F, fontSize: 9,
        color: C.muted, align: "center", margin: 0,
      });
      x += w;
    });
  }
  return s;
}

function assumptions(pres, m, slide) {
  const s = newSlide(pres);
  head(s, slide);
  const rows = slide.rows || (slide.bullets || []).map((b) => ({
    text: typeof b === "string" ? b : b.text,
  }));
  const y0 = cTop(slide);
  const rh = Math.min(0.88, (BOT - y0) / Math.max(rows.length, 1));
  const leftW = CW * 0.5;
  rows.forEach((r, i) => {
    const y = y0 + i * rh;
    if (i % 2 === 0) s.addShape("rect", { x: PAD, y, w: CW, h: rh - 0.06,
      fill: { color: C.stripe } });
    s.addShape("rect", { x: PAD + 0.22, y: y + rh / 2 - 0.05, w: 0.1, h: 0.1,
      fill: { color: C.teal } });
    s.addText(r.text, {
      x: PAD + 0.52, y, w: leftW, h: rh - 0.06, fontFace: F, fontSize: 11.5,
      color: C.navy, valign: "middle", margin: 0, lineSpacingMultiple: 1.15,
    });
    if (r.if_false) {
      const rx = PAD + 0.62 + leftW;
      s.addText("IF THIS DOES NOT HOLD", {
        x: rx, y: y + 0.12, w: 2.4, h: 0.22, fontFace: F, fontSize: 7.6, bold: true,
        color: C.muted, charSpacing: 1.2, margin: 0,
      });
      s.addText(r.if_false, {
        x: rx, y: y + 0.34, w: CW - 0.66 - leftW, h: rh - 0.44, fontFace: F,
        fontSize: 10.5, color: C.fg2, valign: "top", margin: 0, lineSpacingMultiple: 1.15,
      });
    }
  });
  return s;
}

function deliverables(pres, m, slide) {
  const s = newSlide(pres);
  head(s, slide);
  const rows = slide.items || [];
  const y0 = cTop(slide);
  const numW = 0.5, fmtW = 1.9, whenW = 2.2;
  const textW = CW - numW - fmtW - whenW;
  label(s, "Deliverable", PAD + numW, y0 - 0.02, textW, C.muted);
  label(s, "Format", PAD + numW + textW, y0 - 0.02, fmtW, C.muted);
  label(s, "When", PAD + numW + textW + fmtW, y0 - 0.02, whenW, C.muted);
  let y = y0 + 0.36;
  s.addShape("rect", { x: PAD, y: y - 0.06, w: CW, h: 0.012, fill: { color: C.navy } });
  const rh = Math.min(0.78, (BOT - y) / Math.max(rows.length, 1));
  rows.forEach((r, i) => {
    if (i % 2 === 1) s.addShape("rect", { x: PAD, y, w: CW, h: rh, fill: { color: C.stripe } });
    s.addText(String(i + 1).padStart(2, "0"), {
      x: PAD, y, w: numW, h: rh, fontFace: F, fontSize: 10, bold: true, color: C.teal,
      valign: "middle", margin: 0 });
    s.addText(r.name, {
      x: PAD + numW, y: y + 0.06, w: textW - 0.2, h: 0.34, fontFace: F, fontSize: 12.5,
      bold: true, color: C.navy, valign: "top", margin: 0 });
    if (r.detail) s.addText(r.detail, {
      x: PAD + numW, y: y + 0.38, w: textW - 0.2, h: rh - 0.42, fontFace: F, fontSize: 10,
      color: C.fg2, valign: "top", margin: 0, lineSpacingMultiple: 1.15 });
    s.addText(r.format || "", {
      x: PAD + numW + textW, y, w: fmtW, h: rh, fontFace: F, fontSize: 10.5,
      color: C.fg2, valign: "middle", margin: 0 });
    s.addText(r.when || "", {
      x: PAD + numW + textW + fmtW, y, w: whenW, h: rh, fontFace: F, fontSize: 10.5,
      bold: true, color: C.teal, valign: "middle", margin: 0 });
    y += rh;
  });
  return s;
}

function nextSteps(pres, m, slide) {
  const s = newSlide(pres);
  head(s, slide);
  const steps = slide.steps || (slide.bullets || []).map((b) => ({
    text: typeof b === "string" ? b : b.text }));
  const y0 = cTop(slide);
  const numW = 0.62, ownerW = 2.6, whenW = 1.9;
  label(s, "Action", PAD + numW, y0 - 0.02, CW - numW - ownerW - whenW, C.muted);
  label(s, "Owner", PAD + CW - ownerW - whenW, y0 - 0.02, ownerW, C.muted);
  label(s, "Target", PAD + CW - whenW, y0 - 0.02, whenW, C.muted);
  let y = y0 + 0.36;
  s.addShape("rect", { x: PAD, y: y - 0.06, w: CW, h: 0.012, fill: { color: C.navy } });
  const rh = Math.min(0.74, (BOT - y) / Math.max(steps.length, 1));
  steps.forEach((st, i) => {
    if (i % 2 === 1) s.addShape("rect", { x: PAD, y, w: CW, h: rh,
      fill: { color: C.stripe } });
    s.addShape("roundRect", { x: PAD + 0.06, y: y + rh / 2 - 0.15, w: 0.3, h: 0.3,
      rectRadius: 0.05, fill: { color: C.teal } });
    s.addText(String(i + 1), {
      x: PAD + 0.06, y: y + rh / 2 - 0.15, w: 0.3, h: 0.3, fontFace: F, fontSize: 10.5,
      bold: true, color: C.white, align: "center", valign: "middle", margin: 0,
    });
    s.addText(st.text, {
      x: PAD + numW, y, w: CW - numW - ownerW - whenW - 0.1, h: rh, fontFace: F,
      fontSize: 12, color: C.navy, valign: "middle", margin: 0,
    });
    s.addText(st.owner || "", {
      x: PAD + CW - ownerW - whenW, y, w: ownerW, h: rh, fontFace: F, fontSize: 11,
      color: C.fg2, valign: "middle", margin: 0,
    });
    s.addText(st.when || "", {
      x: PAD + CW - whenW, y, w: whenW, h: rh, fontFace: F, fontSize: 11, bold: true,
      color: C.teal, valign: "middle", margin: 0,
    });
    y += rh;
  });
  return s;
}

function proof(pres, m, slide) {
  const s = newSlide(pres);
  head(s, slide);
  const cases = slide.cases || [];
  const y = cTop(slide), gap = 0.26;
  const w = (CW - gap * (cases.length - 1)) / Math.max(cases.length, 1);
  const h = BOT - y;
  cases.forEach((c, i) => {
    const x = PAD + i * (w + gap);
    card(s, x, y, w, h, { fill: C.sand, accent: SEQ[i % SEQ.length] });
    label(s, c.sector || "", x + 0.26, y + 0.32, w - 0.52, C.muted);
    s.addText(c.scale || "", {
      x: x + 0.26, y: y + 0.6, w: w - 0.52, h: 0.42, fontFace: F, fontSize: 17, bold: true,
      color: C.navy, margin: 0, valign: "top",
    });
    s.addText(c.what || "", {
      x: x + 0.26, y: y + 1.1, w: w - 0.52, h: h - 2.1, fontFace: F, fontSize: 11,
      color: C.fg2, margin: 0, valign: "top", lineSpacingMultiple: 1.22,
    });
    s.addShape("rect", { x: x + 0.26, y: y + h - 0.98, w: w - 0.52, h: 0.012,
      fill: { color: C.darkSand } });
    s.addText(c.metric || "", {
      x: x + 0.26, y: y + h - 0.86, w: w - 0.52, h: 0.38, fontFace: F, fontSize: 15,
      bold: true, color: C.teal, margin: 0, valign: "middle",
    });
    s.addText(c.metric_label || "", {
      x: x + 0.26, y: y + h - 0.48, w: w - 0.52, h: 0.28, fontFace: F, fontSize: 9.5,
      color: C.muted, margin: 0, valign: "top",
    });
  });
  return s;
}

function closing(pres, m, slide) {
  const s = newSlide(pres, true);
  s.background = { color: C.navy };
  s.addShape("rect", { x: 0, y: 0, w: 0.1, h: H, fill: { color: C.teal } });
  s.addText(slide.title, {
    x: PAD, y: 2.7, w: 10, h: 1.2, fontFace: F, fontSize: 36, bold: true, color: C.white,
    margin: 0, valign: "middle", lineSpacingMultiple: 1.05,
  });
  if (slide.subtitle) {
    s.addText(slide.subtitle, {
      x: PAD, y: 4.05, w: 8.4, h: 0.9, fontFace: F, fontSize: 14, color: C.white,
      margin: 0, valign: "top", lineSpacingMultiple: 1.3,
    });
  }
  s.addText([m.provider, m.client, m.date].filter(Boolean).join("   ·   "), {
    x: PAD, y: H - 1.1, w: 10, h: 0.3, fontFace: F, fontSize: 10, color: C.white, margin: 0,
  });
  return s;
}

function generic(pres, m, slide) {
  const s = newSlide(pres);
  head(s, slide);
  const items = slide.bullets || [];
  const y = cTop(slide);
  const cols = items.length > 4 ? 2 : 1, gap = 0.26;
  const w = (CW - gap * (cols - 1)) / cols;
  const per = Math.ceil(items.length / cols);
  const avail = BOT - y - (slide.callout ? 0.66 : 0);
  const rh = Math.min(0.9, avail / Math.max(per, 1));
  for (let c = 0; c < cols; c++) {
    const chunk = items.slice(c * per, (c + 1) * per);
    const x = PAD + c * (w + gap);
    chunk.forEach((b, i) => {
      const t = typeof b === "string" ? b : b.text;
      const cy = y + i * rh;
      card(s, x, cy, w, rh - 0.1, { fill: C.sand });
      s.addShape("roundRect", { x: x + 0.24, y: cy + 0.24, w: 0.3, h: 0.3,
        rectRadius: 0.05, fill: { color: C.teal } });
      s.addText(String(c * per + i + 1), {
        x: x + 0.24, y: cy + 0.24, w: 0.3, h: 0.3, fontFace: F, fontSize: 10.5,
        bold: true, color: C.white, align: "center", valign: "middle", margin: 0,
      });
      s.addText(t, {
        x: x + 0.66, y: cy, w: w - 0.94, h: rh - 0.1, fontFace: F, fontSize: 12,
        color: C.fg2, valign: "middle", margin: 0, lineSpacingMultiple: 1.18,
      });
    });
  }
  if (slide.callout) {
    s.addShape("rect", { x: PAD, y: BOT - 0.52, w: CW, h: 0.52,
      fill: { color: C.tealPale } });
    s.addText(slide.callout, {
      x: PAD + 0.28, y: BOT - 0.52, w: CW - 0.56, h: 0.52, fontFace: F, fontSize: 11.5,
      bold: true, color: C.teal, valign: "middle", margin: 0,
    });
  }
  return s;
}

const MAP = {
  divider, exec_summary: execSummary, stats, heard, comparison,
  decision_matrix: decisionMatrix, option_block: optionBlock, recommendation,
  scope: scopeSplit, scope_in: scopeSplit, scope_out: scopeSplit,
  deliverables: deliverables,
  timeline: roadmap, engagement, team: engagement, investment, assumptions,
  proof, decision: nextSteps, confirm: nextSteps, need_from_you: nextSteps, closing,
};

const renderSlide = (pres, m, slide) => {
  // Earlier manifests use separate scope slides with bullets. Preserve those
  // statements instead of feeding them to a renderer that reads different keys.
  if (["scope_in", "scope_out"].includes(slide.kind) && slide.bullets)
    return generic(pres, m, slide);
  return (MAP[slide.kind] || generic)(pres, m, slide);
};

module.exports = { C, F, renderSlide, cover };
