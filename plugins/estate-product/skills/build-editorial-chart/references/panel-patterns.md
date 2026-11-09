# Panel patterns

Condensed from the World Cup worked example in [sources.md](sources.md). Colors come from the CSS tokens `interactive.py` defines; read them in JS with `getComputedStyle(document.documentElement).getPropertyValue("--hero")` so dark mode works.

## Time-series line

One hero line, dots at each point, two haloed annotations and Voronoi hover.

```js
g.append("path").datum(ed).attr("fill", "none").attr("stroke", HERO).attr("stroke-width", 2.4)
  .attr("d", d3.line().x(d => x(d.year)).y(d => y(d.gpg)).curve(d3.curveMonotoneX));
```

## Small multiples

One `<svg>` per group in a CSS grid, with a shared y-domain across every panel. Mark notable points, such as title years, as filled dots. Set each group's name directly on its panel; there is no legend. At 375px the grid drops to two columns.

## Beeswarm

A force layout per category band in one muted color, with a diamond marking the band average. Run the simulation to rest before drawing.

```js
const sim = d3.forceSimulation(nodes)
  .force("x", d3.forceX(d => x(d.total)).strength(1))
  .force("y", d3.forceY(d => bandY[d.era]).strength(0.07))
  .force("collide", d3.forceCollide(3.2)).stop();
for (let i = 0; i < 180; i++) sim.tick();
```

## Bump chart

`d3.scalePoint` over periods on x and a rank scale on y. Color the top finishers with the hero color and lighter ramp steps, and draw the rest in grey. Label each line directly at its end. Use the single moving highlight ring from Rule C for hover.

## Panel note

Under each panel, one plain sentence names the reference graphic it follows, with a link. Plain text only: no colored tag or pill.
