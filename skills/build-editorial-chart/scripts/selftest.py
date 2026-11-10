#!/usr/bin/env python3
"""
Self-test for the build-editorial-chart scripts. Writes demo pages to the given
directory (default: a temporary one) and runs check_html.py on each.

Usage:
    python3 -I selftest.py [out_dir]
"""
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import annotate  # noqa: E402
import chart_selector  # noqa: E402
import check_html  # noqa: E402
import interactive  # noqa: E402
import palette  # noqa: E402
import render  # noqa: E402
import typography  # noqa: E402

failures = []


def expect(cond, label):
    if not cond:
        failures.append(label)
    print(("pass  " if cond else "FAIL  ") + label)


# palette
for s in palette.SCHEMES:
    expect(palette.is_monotonic(palette.SCHEMES[s]["ramp"]), f"scheme {s} ramp lightness is monotonic")
    expect(palette.is_monotonic(palette.palette("series", s, 5)), f"scheme {s} series colors are monotonic")
for name, ramp in palette.DIVERGING.items():
    half = len(ramp) // 2
    expect(palette.is_monotonic(ramp[:half + 1]) and palette.is_monotonic(ramp[half:]),
           f"diverging {name} is monotonic on each side")
expect(not palette.is_monotonic(["#ff0000", "#00ff00", "#0000ff", "#ffff00"]), "rainbow fails the check")
try:
    palette.palette("series", "neutral", 6)
    expect(False, "six series raises")
except ValueError:
    expect(True, "six series raises")
expect(palette.palette("hero", "neutral", 3) == ["#37437D", "#B2B3B5", "#B2B3B5"], "hero is one accent plus one grey")
expect(len(palette.palette("diverging", n=6)) == 7, "diverging forces an odd count")

# typography
css = typography.font_css()
expect("Inter" in css and "mono" not in css.lower(), "default profile is Inter, no monospace")
expect("prefers-color-scheme: dark" in css and '[data-theme="dark"]' in css, "dark theme tokens present")
expect("Playfair" not in typography.FONT_LINKS["default"], "serif only in newsroom profile")

# brand override
brand = {"font": "Hanken Grotesk", "light": {"--hero": "#B16F25"}, "dark": {"--hero": "#FBC27B"}}
bcss = typography.font_css(brand=brand)
expect('"Hanken Grotesk"' in bcss and "--hero:#B16F25" in bcss and ":root[data-theme=\"dark\"]{--hero:#FBC27B;}" in bcss,
       "brand overrides font and tokens in light and dark")
expect("family=Hanken+Grotesk" in typography.font_links(brand=brand), "brand font loads from Google Fonts")
for bad in ({"font": "JetBrains Mono"}, {"light": {"--hero": "red;}body{display:none"}}):
    try:
        typography.font_css(brand=bad)
        expect(False, f"bad brand rejected {bad}")
    except ValueError:
        expect(True, f"bad brand rejected {list(bad)[0]}")

# chart selector
cs = chart_selector.select_chart
expect("small multiples" in cs("change_over_time", {"n_series": 7})["recommended"], "7 series -> small multiples")
expect("hero" in cs("change_over_time", {"n_series": 3})["recommended"], "3 series -> hero line")
expect("connected" not in cs("show_correlation_over_time", {})["recommended"], "non-monotonic -> no connected scatter")
expect("pie" not in cs("show_composition", {})["recommended"].lower(), "composition never recommends pie")

# annotate
good = {"headline": "Unemployment fell to a 50-year low in 2019", "subtitle": "Rate, %, monthly, 2000-19",
        "source": "Source: BLS", "y_axis_label": "Unemployment rate (%)", "chart_type": "line",
        "series_count": 1, "tested_mobile": True}
expect(annotate.score(good) == 100, f"good spec scores 100 (got {annotate.score(good)})")
bad = {"headline": "Unemployment", "series_count": 4, "colored_series": 4, "y_axis_label": "unemp_rate",
       "y_max": 10, "data_max": 12, "dual_axis": True}
names = {i["name"] for i in annotate.audit(bad)}
for n in ("headline_is_a_label", "legend_instead_of_labels", "no_hero_series", "axis_label_is_column_name",
          "domain_hides_max", "dual_axis"):
    expect(n in names, f"bad spec flags {n}")

# render + interactive + check_html
out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(tempfile.mkdtemp(prefix="build-editorial-chart-"))
out.mkdir(parents=True, exist_ok=True)
years = range(2015, 2025)
line_spec = {
    "headline": "Rents rose fastest in Austin, then fell back",
    "subtitle": "Median asking rent, dollars per month, 2015-24",
    "source": "Source: illustrative data for the self-test </script> escape check",
    "chart_type": "line", "y_axis_label": "Dollars per month", "hero_series": "Austin",
    "data": [{"date": f"{y}-01-01", "value": v, "series": s}
             for s, base, slope in (("Austin", 1100, 90), ("Denver", 1300, 50), ("Phoenix", 950, 60))
             for y, v in ((y, base + slope * (y - 2015) + (250 if s == "Austin" and y in (2021, 2022) else 0))
                          for y in years)],
    "annotations": [{"date": "2022-01-01", "value": 1100 + 90 * 7 + 250, "label": "2022 peak"}],
}
bar_spec = {"headline": "Austin added the most rental units", "subtitle": "New units, thousands, 2024",
            "source": "Source: illustrative", "chart_type": "bar", "y_axis_label": "Thousand units",
            "hero_series": "Austin",
            "data": [{"label": k, "value": v} for k, v in (("Austin", 32), ("Denver", 18), ("Phoenix", 26),
                                                           ("Dallas", 30), ("Miami", 12))]}
sm_spec = dict(line_spec, chart_type="small_multiples", headline="Each city's rent path differs")
proj_spec = dict(line_spec, headline="Austin rents are projected to keep rising",
                 data=line_spec["data"] + [{"date": "2026-01-01", "value": 2300, "series": "Austin", "projected": True}])
target_spec = {"headline": "Recurring revenue has to more than double", "subtitle": "Share of revenue, %",
               "source": "Source: illustrative", "chart_type": "bar", "x_max": 100, "value_suffix": "%",
               "data": [{"label": "Today", "value": 18}, {"label": "Target", "value": 40, "target": True}]}
range_spec = {"headline": "Only one item moves with the decision", "subtitle": "Effort, hours",
              "source": "Source: illustrative", "chart_type": "range", "hero_series": "Handoff", "value_suffix": " h",
              "data": [{"label": "Renewals", "lo": 1400, "hi": 1700}, {"label": "Contracts", "lo": 800, "hi": 1000},
                       {"label": "Handoff", "lo": 600, "hi": 900, "either": True, "lo_label": "600 · A", "hi_label": "900 · B"}]}
progress_spec = {"headline": "One workstream hasn't started", "subtitle": "Hours used against plan",
                 "source": "Source: illustrative", "chart_type": "progress", "hero_series": "Integration",
                 "value_suffix": " h",
                 "data": [{"label": "Quoting", "value": 380, "total": 700}, {"label": "Integration", "value": 0, "total": 330}]}
for name, spec in (("line", line_spec), ("bar", bar_spec), ("small-multiples", sm_spec), ("projected", proj_spec),
                   ("target", target_spec), ("range", range_spec), ("progress", progress_spec)):
    p = out / f"render-{name}.html"
    p.write_text(render.render_html(spec))
    errs, notes, *_ = check_html.check(p)
    expect(not errs, f"render {name} passes check_html {errs or ''}{notes or ''}")
    expect("<\\/script>" in p.read_text() or name in ("bar", "target", "range", "progress"),
           f"render {name} escapes </script> in spec JSON")
p = out / "interactive-demo.html"
p.write_text(interactive.scaffold("Hover demo", interactive.DEMO_BODY, interactive.DEMO_JS))
errs, notes, *_ = check_html.check(p)
expect(not errs, f"interactive demo passes check_html {errs or ''}{notes or ''}")

bad_page = out / "bad.html"
bad_page.write_text('<script src="https://cdn.jsdelivr.net/npm/d3@7"></script>'
                    '<style>body{font-family:"JetBrains Mono"}</style><script>let x = ;</script>')
errs, *_ = check_html.check(bad_page)
expect(len(errs) >= 2, f"bad page is rejected ({len(errs)} errors)")

print(f"\nDemo pages in {out}")
print("ALL PASS" if not failures else f"{len(failures)} FAILED")
sys.exit(1 if failures else 0)
