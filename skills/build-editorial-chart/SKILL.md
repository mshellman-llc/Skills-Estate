---
name: build-editorial-chart
description: "Build charts, small dashboards and data stories with newspaper-graphics discipline from New York Times and Upshot practice: one hero color with grey context, direct labels, a headline that states the finding, in-place annotation, 375px-first layout and D3 hover that snaps to the nearest mark. Renders static Observable Plot pages from a JSON spec (line, area, bar, scatter, small multiples, estimate ranges, progress against plan, dashed targets and projections) in the selected brand profile, Baseline by default. Use when a chart, graph or data panel should read as editorial and trustworthy rather than a default library chart. Not for measurement plans or tracking design (design-analytics-plan), explorer sites (build-interactive-explorer) or slide decks (build-deck). Does not publish or share anything."
---

# Build editorial chart

Make each chart answer one question, show the answer without interaction, and state it in the headline. The method follows the graphics desks credited in [sources.md](references/sources.md). Colors and fonts come from the selected brand profile under [the brand policy](references/estate/brand.md). Without a named profile or a project `brand.md`, use the neutral Baseline profile, which these scripts emit by default.

Scripts live in `scripts/`. Run them with `python3 -I scripts/<name>.py`. Every script runs standalone with no network access and no third-party Python packages. The pages they write load pinned D3 and Observable Plot builds from jsDelivr and fonts from Google Fonts.

## When to use

Use for a chart, graph, small dashboard or data story that should read as editorial and trustworthy: a finding stated in the headline, one highlighted series, direct labels and a source line. Typical requests: chart these numbers for a stakeholder page, show progress against plan, compare estimate ranges, show actual against target, or build an interactive panel that snaps to the nearest point.

## When not to use

- A measurement plan, event tracking or metric definitions belong to `design-analytics-plan`.
- A clickable explorer site built from source material belongs to `build-interactive-explorer`.
- A slide deck belongs to `build-deck`; this skill can supply a chart for one of its slides.
- Applying a client identity across a whole document or site belongs to `manage-brand-profile`. This skill takes a resolved profile as its `brand` input.

## Five rules for every chart

1. **Color.** Give the series that matters the hero color. Draw everything else in one grey. Sequential data uses a one-hue tonal ramp with monotonic lightness, never a rainbow. Use a diverging scale only when the midpoint means something you can name. Past five categories, split into small multiples instead of adding colors. `palette.py` holds the Baseline ramps and checks lightness order.
2. **Type.** Use one sans family, with `tabular-nums` on every number so digits stay aligned, and never a monospace face. `typography.py` emits the head block and tokens: Inter for the neutral profile. The `newsroom` profile adds a display serif for headlines; use it only when the user asks for a newspaper look. When a project or client profile governs, map its font and colors into a `brand` dict (a Google Fonts family plus light and dark token overrides) and pass it to `render.py` or `interactive.scaffold()`. `typography.py` documents the format. Read exact values from the profile; do not infer them.
3. **Chart choice.** Use a line first for change over time and a bar second. Never use a pie chart or a second y-axis, and start every bar at zero. Past five series, use small multiples. `chart_selector.py` returns a recommendation, the reason, what to avoid and reference examples. Its patterns cover progress against a plan and comparisons of estimates. They also cover actual values against a target.
4. **Annotation.** The headline is a sentence stating the finding. The subtitle names the unit and timeframe. A source line sits under the chart. Label series directly at their ends; the direct labels act as the legend. Keep a separate legend only when labels cannot fit. Annotate known turning points on the chart. Write axis labels in plain English. `annotate.py` lints a chart spec and scores it.
5. **Visible without interaction.** Anything the reader needs must show without hover or click, and tooltips only add depth. Design at 375px wide first, then widen.

A target or a projection never shares the style of actual values. Draw them as dashed outlines or dashed continuations and say "target" or "projected" in the label.

## Choose the build path

- **Static chart:** write a JSON spec and run `python3 -I scripts/render.py spec.json out.html`. It renders a standalone Observable Plot page with hero and grey series, end labels and haloed annotations. The page supports both themes, and its width follows the container. The chart types are line, area, bar, scatter and small multiples, plus the range and progress row charts. A range row is a low-to-high estimate; a row with `either: true` is two discrete outcomes, drawn as two dots joined by a dashed line. A progress row draws the plan as a track with the work done so far filled in. Rows marked `target` or `projected` draw dashed. On phones, row charts put each label above its bar. The spec format is in the script's docstring.
- **Interactive dashboard:** import `scripts/interactive.py`, write per-panel D3 render functions, and pass them to `scaffold(title, body_html, extra_js, brand=...)`. It supplies the tokens, the gliding tooltip and `voronoiHover()`. Before building, read [interaction-rules.md](references/interaction-rules.md) and [panel-patterns.md](references/panel-patterns.md).

Before building any panel of a dashboard, match it to one reference graphic in [sources.md](references/sources.md) and follow that graphic's discipline.

## Check before delivery

Run `python3 -I scripts/check_html.py out.html`. It parses every inline script with `node --check` (reported as skipped when Node is absent), runs a JSON parse on each embedded JSON block, rejects unpinned CDN URLs, and flags monospace fonts and pie or dual-axis markers. Then check the remaining items:

1. Value domains come from the data maximum, not a typed round number, and an added maximum tick does not collide with its neighbor (Rule D).
2. Every hover rectangle sits in the same translated `<g>` as its marks (Rule A).
3. Hover finds the closest mark through Delaunay (Rule B).
4. The tooltip anchors to the mark and glides (Rule C).
5. Annotations carry a background-colored halo, and edge labels use a leader line (Rule E).
6. A connected scatterplot appears only when both axes move in one direction over time.
7. Open the page in a browser at desktop width and at 375px, in light and dark themes, and confirm every panel draws with no overlapping labels or horizontal scroll. When no browser is available, report the visual check as pending.
8. Cut the editorial text to about half of the first draft: headline, one-line subtitle, source and a short note per panel.

`python3 -I scripts/selftest.py [out_dir]` exercises every script and writes demo pages for each chart type.

## Output

Deliver self-contained HTML. Where the host offers private hosted pages, such as Claude artifacts, publish there; a private page is not permission to share it. Pin every CDN script to an exact version, as `render.py` and `interactive.py` do. Use only numbers from the supplied sources, and name the source on the page.
