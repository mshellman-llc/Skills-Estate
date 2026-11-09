# Interaction rules for hand-built D3

Each rule prevents a bug found and fixed in a real build. `interactive.py` implements A, B and C in `voronoiHover()` and `tipAtNode()`; D and E are your responsibility in each panel.

## Rule A: hit layer in the marks' coordinate space

Append the transparent hover `<rect>` to the same margin-translated `<g>` as the marks. If it sits on the SVG root, `d3.pointer()` returns root coordinates while the marks live in group coordinates, so `delaunay.find()` is off by the left margin and highlights the wrong mark.

```js
// Wrong: overlay on the svg root while marks sit in g(translate(m.left, m.top))
svg.append("rect").attr("x", m.left).attr("y", m.top) /* ... */;
// Right: overlay in the same g as the marks, so pointer space equals mark space
g.append("rect").attr("width", iw).attr("height", ih).attr("fill", "transparent")
  .on("pointermove", function (ev) { const [mx, my] = d3.pointer(ev, this); /* find */ });
```

## Rule B: snap to the nearest mark

Never make the reader hover a 2 to 3px dot. Build a Delaunay triangulation over the marks and snap to the nearest one. Use `pointermove` so touch works too.

```js
const pts = data.map(d => [x(d.k), y(d.v), d]);
const del = d3.Delaunay.from(pts, p => p[0], p => p[1]);
// inside pointermove: const i = del.find(mx, my); const d = pts[i][2];
```

## Rule C: a tooltip that glides from mark to mark

Anchor the tooltip to the hovered mark's on-screen box and transition `left` and `top`, so it slides between marks instead of jumping under the cursor.

```css
.tooltip{position:fixed;opacity:0;transform:translate(-50%,calc(-100% - 12px));
  transition:opacity 140ms ease,left 200ms cubic-bezier(.22,.61,.36,1),top 200ms cubic-bezier(.22,.61,.36,1)}
@media (prefers-reduced-motion:reduce){.tooltip{transition:opacity 140ms ease}}
```

```js
function tipAtNode(node, html) {
  const r = node.getBoundingClientRect();
  tip.innerHTML = html;
  tip.style.left = (r.left + r.width / 2) + "px";
  tip.style.top = r.top + "px";
  tip.style.opacity = 1;
}
```

`interactive.py` also clamps the tooltip inside the viewport so it stays readable at 375px.

Line and bump charts have no node per point. Move one highlight ring to the nearest point and anchor the tooltip to it:

```js
const hl = g.append("circle").attr("r", 5).attr("fill", "none").attr("stroke", "var(--ink)").attr("opacity", 0);
// on hover: hl.attr("cx", p[0]).attr("cy", p[1]).attr("opacity", 1); tipAtNode(hl.node(), html);
```

## Rule D: the domain covers the maximum

A typed round cap pushes outliers off the canvas. In the source build, a goals axis capped at 10 hid the 12-goal match between Switzerland and Austria in 1954, which Austria won 7 to 5.

```js
// Wrong: const x = d3.scaleLinear().domain([0, 10]);
const maxTotal = d3.max(data, d => d.total);
const x = d3.scaleLinear().domain([0, maxTotal]).range([0, iw]);
// Add a tick at maxTotal, and drop any regular tick within about 44px of it,
// or the two labels print on top of each other (1,600 and 1,700 in a 1,700 domain).
const ticks = x.ticks(6).filter(v => x(maxTotal) - x(v) > 44);
ticks.push(maxTotal);
```

## Rule E: annotations stay legible

Give annotation text a halo in the panel background color. Lift labels at troughs and edges clear of the data with a short leader line. Never put a label in the same column as an axis tick.

```css
.anno,.anno-sub{paint-order:stroke fill;stroke:var(--panel);stroke-width:3px;stroke-linejoin:round}
```

```js
// a leader line lifts a trough label clear of the axis and the curve
g.append("line").attr("class", "anno-line")
  .attr("x1", x(yr)).attr("y1", y(v) - 7).attr("x2", x(yr)).attr("y2", y(v) - 42);
g.append("text").attr("class", "anno").attr("x", x(yr)).attr("y", y(v) - 54)
  .attr("text-anchor", "middle").text("1990 · 2.2");
```

## Shared hover helper

```js
function voronoiHover(g, pts, nodes, w, h, onEnter, onLeave) {
  const del = d3.Delaunay.from(pts, p => p[0], p => p[1]);
  g.append("rect").attr("width", w).attr("height", h).attr("fill", "transparent")   // Rule A
    .on("pointermove", function (ev) {
      const [mx, my] = d3.pointer(ev, this);                                        // Rule B
      const i = del.find(mx, my);
      onEnter(pts[i][2], i, nodes ? nodes[i] : null);
    })
    .on("pointerleave", onLeave);
}
```
