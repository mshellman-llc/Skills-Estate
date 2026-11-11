#!/usr/bin/env python3
"""
Chart spec linter. Annotation is the largest difference between a default chart
and an editorial one, so most checks are about words on the chart.

Discipline:
  1. Every chart has a headline that states the finding as a sentence.
  2. The subtitle names the unit and timeframe.
  3. A source line sits under the chart.
  4. Series are labeled at their endpoints, not in a legend.
  5. The hero data point is annotated in place.
  6. Axis labels read as English, not column names.
  7. Gridlines are pale and there is no axis spine.
  8. Known turning points in the data are annotated on the chart.

Spec keys (all optional): headline, subtitle, source, y_axis_label, chart_type,
series_count, colored_series, direct_labels, uses_legend, has_known_inflection,
inflection_annotated, y_min, y_max, data_max, gridlines_dark, axis_spine,
uses_rainbow, dual_axis, has_animated_values, uses_tabular_nums, tested_mobile,
requires_hover_for_critical_info, fonts (list).

Usage:
    python3 -I annotate.py spec.json      # prints score and issues
    python3 -I annotate.py                # demo on a weak spec
"""
import json
import re
import sys

LABEL_WORDS = re.compile(r"^(chart|graph|figure|data|overview|trend|trends)\b", re.I)

REQUIRED = {
    "headline": "A sentence stating the finding: 'Weekly deaths fell through 2023'.",
    "subtitle": "Unit and timeframe: 'Deaths per week, United States, 2020-24'.",
    "source": "A source line: 'Source: CDC WONDER'.",
    "y_axis_label": "The unit on the value axis: 'Deaths per week', 'Share of vote (%)'.",
}


def _headline_is_label(c):
    h = (c.get("headline") or "").strip()
    if not h:
        return False
    words = h.split()
    return len(words) < 4 or bool(LABEL_WORDS.match(h)) or (":" not in h and not re.search(
        r"\b(is|are|was|were|has|have|had|rose|fell|grew|shrank|doubled|halved|leads?|led|"
        r"tops?|topped|beat|lost|gained|climbed|dropped|declined|increased|decreased|stayed|"
        r"remain(s|ed)?|outpaced?|trails?|overtook|peaked|surged|slid)\b", h, re.I))


CHECKS = [
    ("headline_is_a_label", _headline_is_label, "high",
     "The headline reads as a label, not a finding.",
     "Rewrite it as a sentence with a verb that says what to see."),
    ("legend_instead_of_labels",
     lambda c: c.get("series_count", 1) > 1 and (c.get("uses_legend") or not c.get("direct_labels")), "high",
     "Series are identified by a legend rather than direct labels.",
     "Label each series at its endpoint so the eye stays on the data."),
    ("no_hero_series",
     lambda c: c.get("series_count", 1) > 2 and c.get("colored_series", 0) >= c.get("series_count", 1), "high",
     "Every series is colored, so none leads.",
     "Color one series with the hero color and draw the rest in one grey."),
    ("too_many_series",
     lambda c: c.get("series_count", 1) > 5 and c.get("chart_type") != "small_multiples", "high",
     "More than five series on one chart.",
     "Split into small multiples with shared axes."),
    ("inflection_not_annotated",
     lambda c: c.get("has_known_inflection") and not c.get("inflection_annotated"), "high",
     "A known turning point in the data has no annotation.",
     "Label it on the chart: 'March 2020: lockdowns begin'."),
    ("axis_label_is_column_name",
     lambda c: bool(c.get("y_axis_label")) and ("_" in c["y_axis_label"] or c["y_axis_label"].islower()), "medium",
     "The axis label looks like a column name.",
     "Write it in English: 'Unemployment rate (%)', not 'unemployment_rate'."),
    ("bar_not_zero_based",
     lambda c: c.get("chart_type") == "bar" and c.get("y_min", 0) != 0, "high",
     "The bar chart does not start at zero.",
     "Start bars at zero. Use a dot plot if the range must be cropped."),
    ("domain_hides_max",
     lambda c: c.get("data_max") is not None and c.get("y_max") is not None and c["y_max"] < c["data_max"], "critical",
     "The axis maximum is below the data maximum, so marks are off the canvas.",
     "Set the domain from d3.max(data) and add a tick at the maximum (Rule D)."),
    ("dual_axis", lambda c: c.get("dual_axis"), "critical",
     "The chart uses two y-axes.",
     "Use two aligned charts, or index both series to a common base."),
    ("pie", lambda c: c.get("chart_type") in ("pie", "donut"), "high",
     "Pie or donut chart.",
     "Use a stacked or sorted horizontal bar."),
    ("heavy_chrome", lambda c: c.get("gridlines_dark") or c.get("axis_spine"), "medium",
     "Heavy gridlines or an axis spine compete with the data.",
     "Use pale gridlines and drop the spine."),
    ("rainbow", lambda c: c.get("uses_rainbow") or c.get("uses_jet"), "critical",
     "A rainbow or jet color ramp.",
     "Use a one-hue tonal ramp with monotonic lightness (palette.py sequential)."),
    ("monospace", lambda c: any(re.search(r"mono", f, re.I) for f in c.get("fonts", [])), "medium",
     "A monospace font is in use.",
     "Use the sans stack with tabular figures."),
    ("no_tabular_nums",
     lambda c: c.get("has_animated_values") and not c.get("uses_tabular_nums"), "low",
     "Changing numbers without tabular figures will jitter.",
     "Add font-variant-numeric: tabular-nums."),
    ("not_tested_mobile", lambda c: not c.get("tested_mobile"), "high",
     "Not checked at 375px wide.",
     "Check at 375px. Shorten annotations that collide."),
    ("hover_required", lambda c: c.get("requires_hover_for_critical_info"), "critical",
     "Key information appears only on hover or click.",
     "Show it on the chart. Tooltips add depth only."),
]

PENALTY = {"critical": 25, "high": 10, "medium": 4, "low": 1}
ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def audit(spec):
    issues = []
    for field, fix in REQUIRED.items():
        if not spec.get(field):
            issues.append({"severity": "high", "name": f"missing_{field}",
                           "message": f"Missing {field.replace('_', ' ')}.", "fix": fix})
    for name, test, sev, msg, fix in CHECKS:
        if test(spec):
            issues.append({"severity": sev, "name": name, "message": msg, "fix": fix})
    issues.sort(key=lambda i: ORDER[i["severity"]])
    return issues


def score(spec):
    return max(0, 100 - sum(PENALTY[i["severity"]] for i in audit(spec)))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        spec = {"headline": "Unemployment", "chart_type": "line", "series_count": 4, "colored_series": 4,
                "has_known_inflection": True, "y_axis_label": "unemployment_rate"}
    else:
        with open(sys.argv[1]) as f:
            spec = json.load(f)
    print(json.dumps({"score": score(spec), "issues": audit(spec)}, indent=2))
