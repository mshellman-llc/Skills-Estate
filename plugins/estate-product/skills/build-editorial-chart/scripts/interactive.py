#!/usr/bin/env python3
"""
Chrome and interaction primitives for hand-built interactive D3 dashboards.

render.py covers static Observable Plot charts. This module covers multi-panel
interactive dashboards in raw D3, where most craft failures happen.

It provides:
  INTERACTIVE_CSS   panel, annotation halo, gliding tooltip and panel-note styles,
                    layered on the typography.py tokens (light and dark).
  HELPER_JS         tipAtNode() (Rule C), voronoiHover() (Rules A and B) and color().
  scaffold()        a complete page: head, pinned d3, CSS, tooltip node, helpers.
  PREPUBLISH_CHECKLIST

Interaction rules (each prevents an observed bug; details in
references/interaction-rules.md):
  A. The hover <rect> goes in the same translated <g> as the marks.
  B. Hit-test with d3.Delaunay, never bare dot targets.
  C. Anchor the tooltip to the mark's bounding box and transition left/top.
  D. Value domains come from d3.max(data); add the max tick.
  E. Annotation text gets a background-colored halo; edge labels get a leader line.

Usage:
    from interactive import scaffold
    html = scaffold("Title", body_html, extra_js)
    python3 -I interactive.py out.html     # writes a demo page and prints the checklist
"""
import html as _html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from typography import font_css, font_links  # noqa: E402

D3_URL = "https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"

INTERACTIVE_CSS = """
.wrap{max-width:1180px;margin:0 auto;padding:32px 16px 64px}
h1{font-family:var(--font-display);font-weight:700;font-size:clamp(30px,6vw,56px);line-height:1.04;
  letter-spacing:-.02em;margin:0 0 12px;text-wrap:balance}
h2{font-family:var(--font-display);font-weight:700;font-size:clamp(21px,3.2vw,30px);line-height:1.15;
  margin:0 0 6px;max-width:760px;text-wrap:balance}
h2 em{font-style:normal;color:var(--hero)}
.dek,.panel-dek{color:var(--ink2);line-height:1.55;max-width:620px;margin:0 0 16px}
.panel{margin:48px 0 0}
.chartcard{background:var(--panel);border:1px solid var(--rule);border-radius:8px;padding:16px}
@media (min-width:640px){.chartcard{padding:20px 24px 16px}}
svg{display:block;max-width:100%;height:auto;overflow:visible}
.axis text{font-size:11.5px;fill:var(--ink2)}
.axis-title{font-size:11.5px;fill:var(--ink3);font-weight:500}
/* Rule E: halo so labels never fight the data */
.anno,.anno-sub{paint-order:stroke fill;stroke:var(--panel);stroke-width:3px;stroke-linejoin:round}
.anno{font-size:11.5px;fill:var(--ink);font-weight:600}
.anno-sub{font-size:10.5px;fill:var(--ink2);font-weight:400}
.anno-line{stroke:var(--ink3);stroke-width:.8}
/* Rule C: gliding tooltip anchored to the mark */
.tooltip{position:fixed;pointer-events:none;z-index:999;left:0;top:0;background:var(--tip-bg);color:var(--tip-ink);
  padding:8px 11px;font-family:var(--font-sans);font-size:12px;line-height:1.45;border-radius:6px;
  font-variant-numeric:tabular-nums;transform:translate(-50%,calc(-100% - 12px));opacity:0;max-width:260px;
  transition:opacity 140ms ease,left 200ms cubic-bezier(.22,.61,.36,1),top 200ms cubic-bezier(.22,.61,.36,1)}
@media (prefers-reduced-motion:reduce){.tooltip{transition:opacity 140ms ease}}
.tooltip .t-hd{font-weight:700;margin-bottom:1px}
.panel-note{margin-top:12px;padding-top:10px;border-top:1px solid var(--rule);font-family:var(--font-sans);
  font-size:12px;line-height:1.55;color:var(--ink2);max-width:760px}
.panel-note a{color:var(--ink);text-underline-offset:2px}
.source{font-family:var(--font-sans);font-size:12px;color:var(--ink3);margin-top:40px}
"""

HELPER_JS = r"""
// Read a theme token. Re-read after a theme change; tokens differ in dark mode.
const color = name => getComputedStyle(document.documentElement).getPropertyValue(name).trim();

// Rule C: gliding tooltip anchored to a mark, clamped inside the viewport.
const tip = document.getElementById("tooltip");
function tipAtNode(node, html) {
  const r = node.getBoundingClientRect();
  tip.innerHTML = html;
  const half = Math.min(tip.offsetWidth, 260) / 2 + 8;
  const cx = Math.max(half, Math.min(innerWidth - half, r.left + r.width / 2));
  tip.style.left = cx + "px";
  tip.style.top = Math.max(tip.offsetHeight + 16, r.top) + "px";
  tip.style.opacity = 1;
}
function hideTip() { tip.style.opacity = 0; }
addEventListener("scroll", hideTip, { passive: true });

// Rules A and B: proximity hover.
// g      the margin-translated <g> that also holds the marks
// pts    [[x, y, datum], ...] in g coordinates
// nodes  on-screen mark nodes in the same order as pts, or null
// w, h   inner width and height of the plot area
function voronoiHover(g, pts, nodes, w, h, onEnter, onLeave) {
  const del = d3.Delaunay.from(pts, p => p[0], p => p[1]);
  g.append("rect")                                   // Rule A: child of g
    .attr("width", w).attr("height", h).attr("fill", "transparent")
    .style("touch-action", "pan-y")
    .on("pointermove pointerdown", function (ev) {
      const [mx, my] = d3.pointer(ev, this);         // same space as pts
      const i = del.find(mx, my);
      onEnter(pts[i][2], i, nodes ? nodes[i] : null);
    })
    .on("pointerleave", onLeave);
}
"""

PREPUBLISH_CHECKLIST = [
    "Run check_html.py: inline scripts pass node --check, JSON blocks parse, CDN URLs are pinned.",
    "Value-scale domains come from d3.max(data), not a typed round number (Rule D).",
    "Every hover <rect> is appended to its marks' translated <g> (Rule A).",
    "Hover uses d3.Delaunay proximity, not bare dot targets (Rule B).",
    "The tooltip anchors to the mark through getBoundingClientRect() and glides (Rule C).",
    "Annotation text has a halo; trough and edge labels use a leader line (Rule E).",
    "Connected scatterplot only when both axes move in one direction; otherwise a line.",
    "Screenshot at desktop width and at 375px, in light and dark, and confirm every panel draws.",
    "Editorial text is about half the first draft: headline, one-line dek, source, short panel notes.",
]


def scaffold(title, body_html, extra_js="", profile="default", scheme="neutral", brand=None):
    """Return a complete, self-contained dashboard page.

    body_html: the <div class="wrap"> ... </div> markup (header and panels).
    extra_js:  per-panel render functions; runs after d3 and HELPER_JS load.
    brand:     optional font and token overrides; see typography.py.
    """
    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_html.escape(title)}</title>
{font_links(profile, brand)}
<script src="{D3_URL}"></script>
<style>{font_css(profile, scheme, brand)}{INTERACTIVE_CSS}</style>
</head><body>
<div id="tooltip" class="tooltip" role="status" aria-live="polite"></div>
{body_html}
<script>
{HELPER_JS}
{extra_js}
</script>
</body></html>"""


DEMO_BODY = """<div class="wrap">
<h1>Demo: hover snaps to the nearest point</h1>
<p class="dek">Replace this body and pass per-panel render code through extra_js.</p>
<section class="panel"><div class="chartcard"><div id="c-demo"></div></div>
<p class="panel-note">Hover anywhere in the plot; the tooltip glides to the closest point.</p></section>
</div>"""

DEMO_JS = r"""
function drawDemo() {
  const host = document.getElementById("c-demo");
  host.replaceChildren();
  const HERO = color("--hero"), PANEL = color("--panel");
  const W = host.clientWidth || 340, H = Math.max(220, Math.min(320, W * 0.6));
  const m = { top: 20, right: 16, bottom: 28, left: 36 }, iw = W - m.left - m.right, ih = H - m.top - m.bottom;
  const data = d3.range(20).map(i => ({ x: i, y: Math.sin(i / 3) * 10 + 20 }));
  const svg = d3.select(host).append("svg").attr("viewBox", `0 0 ${W} ${H}`);
  const g = svg.append("g").attr("transform", `translate(${m.left},${m.top})`);
  const x = d3.scaleLinear().domain(d3.extent(data, d => d.x)).range([0, iw]);
  const y = d3.scaleLinear().domain([0, d3.max(data, d => d.y)]).nice().range([ih, 0]);   // Rule D
  g.append("g").attr("class", "grid").call(d3.axisLeft(y).ticks(4).tickSize(-iw).tickFormat(""));
  g.append("g").attr("class", "axis").call(d3.axisLeft(y).ticks(4).tickSize(0)).call(s => s.select(".domain").remove());
  g.append("path").datum(data).attr("fill", "none").attr("stroke", HERO).attr("stroke-width", 2.4)
    .attr("d", d3.line().x(d => x(d.x)).y(d => y(d.y)).curve(d3.curveMonotoneX));
  const dots = g.selectAll("circle").data(data).join("circle").attr("cx", d => x(d.x)).attr("cy", d => y(d.y))
    .attr("r", 3).attr("fill", PANEL).attr("stroke", HERO);
  const pts = data.map(d => [x(d.x), y(d.y), d]);
  voronoiHover(g, pts, dots.nodes(), iw, ih,
    (d, i, node) => { dots.attr("r", 3).attr("fill", PANEL); d3.select(node).attr("r", 6).attr("fill", HERO);
      tipAtNode(node, `<div class="t-hd">Point ${d.x}</div>${d.y.toFixed(1)}`); },
    () => { dots.attr("r", 3).attr("fill", PANEL); hideTip(); });
}
drawDemo();
matchMedia("(prefers-color-scheme: dark)").addEventListener("change", drawDemo);
let lastW = 0;
new ResizeObserver(e => { const w = e[0].contentRect.width; if (w !== lastW) { lastW = w; drawDemo(); } })
  .observe(document.getElementById("c-demo"));
"""


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "interactive-demo.html")
    out.write_text(scaffold("Hover demo", DEMO_BODY, DEMO_JS))
    print(f"Wrote {out}")
    print("Pre-publish checklist:")
    for n, item in enumerate(PREPUBLISH_CHECKLIST, 1):
        print(f"  {n}. {item}")
