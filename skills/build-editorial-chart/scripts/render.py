#!/usr/bin/env python3
"""
Render an editorial chart as a standalone HTML page with Observable Plot.

The page follows the container width (375px and up), supports light and dark
themes, draws the hero series in color and the rest in grey, labels series at
their ends, and haloes annotations.

Usage:
    python3 -I render.py spec.json out.html

spec.json:
{
  "headline": "Weekly deaths fell through 2023",          # a sentence stating the finding
  "subtitle": "Deaths per week, all causes, United States, 2020-24",
  "source": "Source: CDC WONDER",
  "chart_type": "line" | "bar" | "area" | "scatter" | "small_multiples" | "range" | "progress",
  "x_axis_label": "",                                    # optional; omit for dates
  "y_axis_label": "Deaths per week",
  "data": [{"date": "2020-01-04", "value": 56000, "series": "U.S."}, ...],
       # line/area/small_multiples: date (or x) + value [+ series] [+ projected: true]
       # bar: label + value [+ target: true | projected: true]
       # range: label + lo + hi [+ either: true, lo_label, hi_label]
       # progress: label + value (done so far) + total (plan)
       # scatter: x + y [+ label]
       # A row marked target or projected draws as a dashed outline (bar) or a dashed
       # continuation of its line, so it never reads as an actual value. Bar charts with
       # such rows keep the input order (actual first); others sort by value.
       # either: true means two discrete outcomes, not a span: two dots joined by a dashed line.
  "hero_series": "U.S.",                                 # line: series to color; bar/range/progress: label to color
  "value_suffix": " h",                                  # optional unit on value labels
  "x_max": 100,                                          # optional; bar only, e.g. 100 for shares of a whole
  "value_label": "Hours used", "total_label": "Hours planned",   # progress key, optional
  "annotations": [{"date": "2020-03-15", "value": 65000, "label": "Lockdowns begin"}],
       # scatter annotations use x + y
  "scheme": "neutral",                                   # optional; the only scheme
  "profile": "default" | "newsroom",                     # typography, default is the system sans stack
  "brand": {"font": "...", "light": {...}, "dark": {...}} # optional; see typography.py
}
"""
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from typography import font_css, font_links  # noqa: E402

D3_URL = "https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"
PLOT_URL = "https://cdn.jsdelivr.net/npm/@observablehq/plot@0.6.16/dist/plot.umd.min.js"

CHART_JS = r"""
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const host = document.getElementById("chart");
const parseX = v => (typeof v === "string" && /^\d{4}-\d{2}(-\d{2})?/.test(v)) ? new Date(v) : v;

function rows() {
  return spec.data.map(d => ({
    ...d,
    x: parseX(d.date ?? d.x),
    value: d.value != null ? +d.value : undefined,
    total: d.total != null ? +d.total : undefined,
    lo: d.lo != null ? +d.lo : undefined,
    hi: d.hi != null ? +d.hi : undefined,
    y: d.y != null ? +d.y : undefined,
  }));
}

function labelWidth(strings, px) {
  return Math.ceil(Math.max(0, ...strings.map(s => String(s).length)) * px);
}

function base(width, extra) {
  return {
    width,
    height: Math.round(Math.min(400, Math.max(260, width * 0.62))),
    marginTop: 28, marginBottom: 32, marginLeft: 48, marginRight: 16,
    style: { background: "transparent", fontFamily: css("--font-sans"), fontSize: "12px", color: css("--ink2"),
             fontVariantNumeric: "tabular-nums", overflow: "visible" },
    ...extra,
  };
}

function annotationMarks(C, xKey, yKey) {
  const ann = (spec.annotations || []).map(a => ({ x: parseX(a.date ?? a.x), y: +(a.value ?? a.y), label: a.label }));
  if (!ann.length) return [];
  return [
    Plot.dot(ann, { x: "x", y: "y", r: 3.5, fill: C.ink, stroke: C.panel, strokeWidth: 1.5 }),
    Plot.text(ann, { x: "x", y: "y", text: "label", dy: -12, lineAnchor: "bottom", fontWeight: 500,
                     fontSize: 12.5, fill: C.ink, stroke: C.panel, strokeWidth: 3, textAnchor: "middle" }),
  ];
}

function lineChart(data, width, C, area) {
  const multi = new Set(data.map(d => d.series)).size > 1;
  const hero = spec.hero_series ?? (multi ? null : data[0]?.series);
  const isHero = d => !multi || d.series === hero;
  const heroAll = data.filter(isHero), ctxAll = data.filter(d => !isHero(d));
  const [heroRows, heroProj] = splitProjected(heroAll), [ctxRows, ctxProj] = splitProjected(ctxAll);
  const names = multi ? [...new Set(data.map(d => d.series))] : [];
  const narrow = width < 520;
  const marks = [];
  if (area) marks.push(Plot.areaY(heroRows, { x: "x", y: "value", fill: C.hero, fillOpacity: 0.12 }));
  if (ctxRows.length) marks.push(Plot.line(ctxRows, { x: "x", y: "value", z: "series", stroke: C.context, strokeWidth: 1.5 }));
  if (ctxProj.length) marks.push(Plot.line(ctxProj, { x: "x", y: "value", z: "series", stroke: C.context, strokeWidth: 1.5, strokeDasharray: "4 3" }));
  marks.push(Plot.line(heroRows, { x: "x", y: "value", z: "series", stroke: C.hero, strokeWidth: 2.5 }));
  if (heroProj.length) marks.push(Plot.line(heroProj, { x: "x", y: "value", z: "series", stroke: C.hero, strokeWidth: 2.5, strokeDasharray: "5 4" }));
  if (multi) {
    if (ctxAll.length) marks.push(Plot.text(ctxAll, Plot.selectLast({ x: "x", y: "value", z: "series", text: "series",
      dx: 6, textAnchor: "start", fill: C.ink2, stroke: C.panel, strokeWidth: 3, fontSize: narrow ? 11 : 12 })));
    marks.push(Plot.text(heroAll, Plot.selectLast({ x: "x", y: "value", z: "series", text: "series",
      dx: 6, textAnchor: "start", fill: C.hero, fontWeight: 700, stroke: C.panel, strokeWidth: 3 })));
  }
  const labelSet = names;
  return base(width, {
    marginRight: multi ? Math.min(narrow ? 76 : 140, labelWidth(labelSet, narrow ? 6.6 : 7.2) + 12) : 16,
    x: { label: spec.x_axis_label || null, ticks: narrow ? 4 : undefined },
    y: { label: spec.y_axis_label || null, labelAnchor: "top", labelArrow: "none", grid: true, nice: true, zero: area, ticks: 5,
         domain: area ? [0, d3.max(data, d => d.value)] : undefined },
    marks: [...marks, ...annotationMarks(C)],
  });
}

// Projected rows continue their series as a dashed line from the last actual point.
function splitProjected(rows) {
  const solid = rows.filter(d => !d.projected), proj = [];
  for (const [, rs] of d3.group(rows, d => d.series)) {
    const sorted = d3.sort(rs, d => d.x), p = sorted.filter(d => d.projected);
    if (!p.length) continue;
    const a = sorted.filter(d => !d.projected);
    if (a.length) proj.push(a[a.length - 1]);
    proj.push(...p);
  }
  return [solid, proj];
}

// Horizontal row charts (bar, range, progress) share a sorted row order, a label
// column that wraps long names onto two lines, and a top value axis.
const fmtN = d3.format(",~r");
const unit = () => spec.value_suffix || "";
const toneOf = (C, hero) => d => hero == null || d.label === hero ? C.hero : C.context;

function rowLayout(width, data, sortKey, rightLabels) {
  const narrow = width < 520;
  // Sort by value, except when rows run from actual to target or projection: keep that order.
  const keep = data.some(d => d.target || d.projected);
  const order = (keep ? data : d3.sort(data, d => -sortKey(d))).map(d => d.label);
  // Phones: labels sit above their bars at full width. Wider: a label column on the left.
  const marginLeft = narrow ? 1 : Math.min(Math.round(width * 0.3), labelWidth(order, 7) + 12);
  const marginRight = Math.min(Math.round(width * 0.3), labelWidth(rightLabels, 6.8) + 14);
  // Height is rows plus the top axis and a small bottom margin, so every row gets rowH.
  // Phones inset the rows below the axis so the first label above its bar clears the tick labels.
  const rowH = narrow ? 58 : 38, padding = narrow ? 0.6 : 0.3, outer = 0.1, n = data.length;
  const inset = narrow ? 24 : 0, bottom = narrow ? 28 : 12;
  const step = rowH * n / (n - padding + 2 * outer), band = step * (1 - padding);
  return { narrow, order, marginLeft, marginRight, padding, outer, band, inset, bottom, height: n * rowH + inset + 28 + bottom,
           lineWidth: Math.max(4, (marginLeft - 12) / 12.5) };
}

function rowAxis(lay, C) {
  const hero = spec.hero_series, fill = d => d === hero ? C.hero : C.ink;
  if (lay.narrow) {
    return Plot.text(lay.order, { y: d => d, text: d => d, frameAnchor: "left", textAnchor: "start",
                                  dy: -Math.round(lay.band / 2) - 9, fontSize: 12.5, fontWeight: 500, fill });
  }
  return Plot.axisY({ tickSize: 0, label: null, lineWidth: lay.lineWidth, fontSize: 12.5, tickPadding: 8, fill });
}

function valueAxis(width, max) {
  // Rule D: the domain reaches the data maximum.
  return { label: null, grid: true, nice: true, domain: [0, max], axis: "top", ticks: width < 520 ? 3 : 6 };
}

function barChart(data, width, C) {
  const hero = spec.hero_series, tone = toneOf(C, hero);
  const outlined = d => d.target || d.projected;
  const text = d => fmtN(d.value) + unit() + (d.target ? " target" : d.projected ? " projected" : "");
  const lay = rowLayout(width, data, d => d.value, data.map(text));
  const max = Math.max(spec.x_max ?? 0, d3.max(data, d => d.value));
  return base(width, {
    height: lay.height, marginLeft: lay.marginLeft, marginRight: lay.marginRight, marginBottom: lay.bottom,
    x: valueAxis(width, max),
    y: { domain: lay.order, axis: null, paddingInner: lay.padding, paddingOuter: lay.outer, insetTop: lay.inset },
    marks: [
      Plot.barX(data.filter(d => !outlined(d)), { x: "value", y: "label", fill: tone }),
      Plot.barX(data.filter(outlined), { x: "value", y: "label", fill: "none", stroke: tone,
                                         strokeWidth: 1.5, strokeDasharray: "4 3" }),
      Plot.ruleX([0], { stroke: C.ink2 }),
      Plot.text(data, { x: "value", y: "label", text, dx: 6, textAnchor: "start",
                        fill: d => d.label === hero ? C.hero : C.ink2 }),
      rowAxis(lay, C),
    ],
  });
}

function rangeChart(data, width, C) {
  const hero = spec.hero_series, tone = toneOf(C, hero);
  const spans = data.filter(d => !d.either), pairs = data.filter(d => d.either);
  const spanText = d => `${fmtN(d.lo)}–${fmtN(d.hi)}${unit()}`;
  const loText = d => d.lo_label ?? fmtN(d.lo) + unit(), hiText = d => d.hi_label ?? fmtN(d.hi) + unit();
  const lay = rowLayout(width, data, d => d.hi, spans.map(spanText));
  const halo = { stroke: C.panel, strokeWidth: 3, fontWeight: 600 };
  return base(width, {
    height: lay.height, marginLeft: lay.marginLeft, marginRight: lay.marginRight, marginBottom: lay.bottom,
    x: valueAxis(width, d3.max(data, d => d.hi)),
    y: { domain: lay.order, axis: null, paddingInner: lay.padding, paddingOuter: lay.outer, insetTop: lay.inset },
    marks: [
      Plot.barX(spans, { x1: "lo", x2: "hi", y: "label", fill: tone, rx: 6, insetTop: 3, insetBottom: 3 }),
      Plot.text(spans, { x: "hi", y: "label", text: spanText, dx: 6, textAnchor: "start", fill: C.ink2 }),
      // Two discrete outcomes: dots joined by a dashed line, labels outside the pair.
      Plot.link(pairs, { x1: "lo", x2: "hi", y1: "label", y2: "label", stroke: tone, strokeWidth: 1.5, strokeDasharray: "3 3" }),
      Plot.dot(pairs, { x: "lo", y: "label", r: 5.5, fill: tone }),
      Plot.dot(pairs, { x: "hi", y: "label", r: 5.5, fill: C.panel, stroke: tone, strokeWidth: 2 }),
      // Wide: each label outside its dot. Phones: one line under the pair, from the left edge.
      ...(lay.narrow
        ? [Plot.text(pairs, { y: "label", text: d => `${loText(d)}  or  ${hiText(d)}`, frameAnchor: "left",
                              textAnchor: "start", dy: 20, fill: tone, ...halo })]
        : [Plot.text(pairs, { x: "lo", y: "label", text: loText, dx: -10, textAnchor: "end", fill: tone, ...halo }),
           Plot.text(pairs, { x: "hi", y: "label", text: hiText, dx: 10, textAnchor: "start", fill: tone, ...halo })]),
      rowAxis(lay, C),
    ],
  });
}

function progressChart(data, width, C) {
  const hero = spec.hero_series, isHero = d => d.label === hero;
  const text = d => `${fmtN(d.value)} of ${fmtN(d.total)}${unit()}`;
  const lay = rowLayout(width, data, d => d.total, data.map(text));
  return base(width, {
    height: lay.height, marginLeft: lay.marginLeft, marginRight: lay.marginRight, marginBottom: lay.bottom,
    x: valueAxis(width, d3.max(data, d => Math.max(d.total, d.value))),
    y: { domain: lay.order, axis: null, paddingInner: lay.padding, paddingOuter: lay.outer, insetTop: lay.inset },
    marks: [
      // Track is the plan; the hero's track is a dashed outline so it shows even at zero.
      Plot.barX(data.filter(d => !isHero(d)), { x: "total", y: "label", fill: C.grid }),
      Plot.barX(data.filter(isHero), { x: "total", y: "label", fill: "none", stroke: C.hero, strokeWidth: 1.5, strokeDasharray: "4 3" }),
      Plot.barX(data, { x: "value", y: "label", fill: d => isHero(d) ? C.hero : C.context }),
      Plot.text(data, { x: "total", y: "label", text, dx: 6, textAnchor: "start",
                        fill: d => isHero(d) ? C.hero : C.ink2, fontWeight: 500 }),
      rowAxis(lay, C),
    ],
  });
}

function progressKey() {
  const p = document.createElement("p");
  p.className = "chart-note";
  p.textContent = `Filled: ${spec.value_label || "done so far"} · Track: ${spec.total_label || "planned"}`;
  return p;
}

function scatterChart(data, width, C) {
  return base(width, {
    x: { label: spec.x_axis_label || null, grid: true, nice: true },
    y: { label: spec.y_axis_label || null, labelAnchor: "top", labelArrow: "none", grid: true, nice: true, ticks: 5 },
    marks: [
      Plot.dot(data, { x: "x", y: "y", r: 4, fill: C.hero, fillOpacity: 0.55 }),
      ...annotationMarks(C),
    ],
  });
}

function smallMultiples(data, width, C) {
  const groups = d3.groups(data, d => d.series);
  const cols = width < 520 ? 2 : 3;
  const w = Math.floor((width - (cols - 1) * 16) / cols);
  // Shared y-domain across panels so they compare honestly; lines need no zero baseline.
  const [yMin, yMax] = d3.extent(data, d => d.value);
  const xDom = d3.extent(data, d => d.x);
  host.style.display = "grid";
  host.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;
  host.style.gap = "16px";
  for (const [name, rowsFor] of groups) {
    const cell = document.createElement("div");
    const title = document.createElement("div");
    title.className = "chart-title";
    title.style.fontSize = "14px";
    title.textContent = name;
    title.style.color = name === spec.hero_series ? C.hero : C.ink;
    cell.append(title);
    cell.append(Plot.plot(base(w, {
      height: Math.round(w * 0.7), marginLeft: 36, marginRight: 8,
      x: { domain: xDom, ticks: 2, label: null },
      y: { domain: [yMin, yMax], nice: true, grid: true, ticks: 3, label: null },
      marks: [Plot.line(rowsFor, { x: "x", y: "value", stroke: name === spec.hero_series || !spec.hero_series ? C.hero : C.context, strokeWidth: 2 })],
    })));
    host.append(cell);
  }
}

function render() {
  const C = { hero: css("--hero"), context: css("--context"), ink: css("--ink"), ink2: css("--ink2"),
              panel: css("--bg"), grid: css("--grid") };
  host.replaceChildren();
  host.removeAttribute("style");
  const width = Math.max(300, host.clientWidth);
  const data = rows();
  const t = spec.chart_type || "line";
  if (t === "small_multiples") return smallMultiples(data, width, C);
  const opts = t === "bar" ? barChart(data, width, C)
    : t === "range" ? rangeChart(data, width, C)
    : t === "progress" ? progressChart(data, width, C)
    : t === "scatter" ? scatterChart(data, width, C)
    : lineChart(data, width, C, t === "area");
  host.append(Plot.plot(opts));
  if (t === "progress") host.append(progressKey());
}

render();
let lastW = host.clientWidth;
new ResizeObserver(() => { if (host.clientWidth !== lastW) { lastW = host.clientWidth; render(); } }).observe(host);
matchMedia("(prefers-color-scheme: dark)").addEventListener("change", render);
"""

EXTRA_CSS = """
#chart{margin:8px 0 0}
#chart svg{max-width:100%;height:auto;display:block}
"""


def _json_for_script(obj):
    return json.dumps(obj).replace("</", "<\\/")


def render_html(spec):
    profile = spec.get("profile", "default")
    scheme = spec.get("scheme", "neutral")
    brand = spec.get("brand")
    e = html.escape
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(spec.get("headline", "Chart"))}</title>
{font_links(profile, brand)}
<style>{font_css(profile, scheme, brand)}{EXTRA_CSS}</style>
<script src="{D3_URL}"></script>
<script src="{PLOT_URL}"></script>
</head>
<body>
<main class="container">
  <h1 class="headline">{e(spec.get("headline", ""))}</h1>
  <p class="subtitle">{e(spec.get("subtitle", ""))}</p>
  <figure id="chart" role="img" aria-label="{e(spec.get("headline", ""))}"></figure>
  <p class="chart-source">{e(spec.get("source", ""))}</p>
</main>
<script type="application/json" id="spec">{_json_for_script(spec)}</script>
<script>
const spec = JSON.parse(document.getElementById("spec").textContent);
{CHART_JS}
</script>
</body>
</html>
"""


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    spec = json.loads(Path(sys.argv[1]).read_text())
    Path(sys.argv[2]).write_text(render_html(spec))
    print(f"Wrote {sys.argv[2]}")
