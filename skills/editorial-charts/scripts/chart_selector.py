#!/usr/bin/env python3
"""
Chart-type selector following Times graphics desk practice.

Given the question and the shape of the data, return a recommended chart, the
reason, the anti-pattern to avoid and Times examples. Sources: Gregor Aisch's
portfolio retrospective (line, choropleth, small multiples, bar, scatter in
that order of frequency), Amanda Cox's talks, Archie Tse's interaction rules
and the published Upshot catalog.

data_shape (dict, all optional):
  n_rows: int
  n_series: int               distinct lines or categories
  x_type: "time" | "ordinal" | "quantitative" | "geo"
  both_axes_monotonic: bool   for connected scatterplots

question_type, one of:
  change_over_time, compare_categories, show_distribution, show_correlation,
  show_correlation_over_time, show_composition, rank_items, rank_over_time,
  where_is_it, how_likely

Defaults: line for time series; small multiples past five series; never pie;
horizontal bars sorted by value for rankings; a locator map before a
choropleth; scatterplots with named outliers; diverging color only with a
nameable zero.

Usage:
    python3 -I chart_selector.py <question_type> ['{"n_series": 7}']
"""
import json
import sys

MAX_SERIES = 5

PATTERNS = {
    "change_over_time": {
        "single_series": {
            "recommended": "line chart",
            "why": "One line in the hero color with a label at its end. The most common Times chart.",
            "avoid": "An area chart, unless filled magnitude is the point. Areas exaggerate.",
            "examples": ["Daily COVID-19 cases tracker (2020-23)", "U.S. unemployment rate"],
        },
        "few_series": {
            "recommended": "line chart: one hero series in color, the rest in grey",
            "why": "Color the line the story is about. Demote the rest to context.",
            "avoid": "Coloring every line. Readers can follow one or two at once.",
            "examples": ["Excess mortality by country", "Inflation: U.S. vs. peers"],
        },
        "many_series": {
            "recommended": "small multiples: one panel per series with shared axes",
            "why": "Past five lines a single chart turns to spaghetti.",
            "avoid": "Twelve lines on one axis, or a twelve-color legend.",
            "examples": ["State-by-state COVID-19 waves", "Country GDP growth paths"],
        },
    },
    "compare_categories": {
        "few": {
            "recommended": "horizontal bar chart sorted by value",
            "why": "Labels fit horizontally and bar lengths compare at a glance.",
            "avoid": "Vertical bars that force rotated labels.",
            "examples": ["Most-watched shows", "Highest-grossing films"],
        },
        "many": {
            "recommended": "dot plot or short bar chart with the head and tail named",
            "why": "Annotate the extremes and leave the middle as context.",
            "avoid": "Fifty tiny bars when six matter.",
            "examples": ["State teacher pay rankings"],
        },
    },
    "show_distribution": {
        "default": {
            "recommended": "beeswarm, strip plot or histogram",
            "why": "Dots show the actual records. A density curve hides them.",
            "avoid": "Box plots. General readers do not read them.",
            "examples": ["COVID-19 vaccination tracker beeswarm", "How rich is your school district?"],
        },
    },
    "show_correlation": {
        "default": {
            "recommended": "scatterplot with three to five named points and a reference line",
            "why": "An unlabeled cloud tells the reader nothing.",
            "avoid": "A regression line without saying what it means.",
            "examples": ["Income vs. life expectancy by country", "2016 hottest year scatter"],
        },
    },
    "show_correlation_over_time": {
        "monotonic": {
            "recommended": "connected scatterplot",
            "why": "Both axes move one way, so the path reads as a trajectory.",
            "avoid": "Leaving the start and end years unlabeled.",
            "examples": ["Driving Shifts Into Reverse (2010)"],
        },
        "non_monotonic": {
            "recommended": "two aligned line charts sharing the time axis",
            "why": "A connected scatterplot tangles when either axis doubles back.",
            "avoid": "A connected scatterplot here. Readers lose the time order.",
            "examples": [],
        },
    },
    "show_composition": {
        "default": {
            "recommended": "stacked bar, one bar per category or period",
            "why": "Stacks read fast. Pies fail past four slices.",
            "avoid": "Pie, 3D pie, or a donut unless the hole shows the total.",
            "examples": ["Federal budget composition"],
        },
        "over_time": {
            "recommended": "stacked area with the most-changing part on top",
            "why": "Put the volatile category on the upper edge, where the eye lands.",
            "avoid": "Streamgraphs. They look good and cannot be read for values.",
            "examples": ["Sources of U.S. electricity generation"],
        },
    },
    "rank_items": {
        "default": {
            "recommended": "horizontal bar chart sorted descending",
            "why": "Sort by the value being compared. Length is the value.",
            "avoid": "Alphabetical order, or lollipops for ranks.",
            "examples": ["Highest-paid CEOs"],
        },
    },
    "rank_over_time": {
        "default": {
            "recommended": "bump chart: leader in the hero color, the rest in grey",
            "why": "Rank changes read as crossings, and the hero line carries the story.",
            "avoid": "A legend. Label each line at its end.",
            "examples": ["All-time points table (World Cup worked example)"],
        },
    },
    "progress_against_plan": {
        "default": {
            "recommended": "progress bars: plan as a light track, done so far filled (render.py chart_type progress)",
            "why": "Each row shows how much is done and how much is planned at the same scale.",
            "avoid": "Percent-complete alone, which hides how big each item is; colored status labels.",
            "examples": ["Hours used against plan by workstream"],
        },
    },
    "compare_estimates": {
        "default": {
            "recommended": "range bars from low to high estimate (render.py chart_type range)",
            "why": "A span shows uncertainty honestly; a single midpoint invents precision.",
            "avoid": "Error bars on a bar chart, or a midpoint bar without its range.",
            "examples": ["Draft effort by scope item"],
        },
        "two_outcomes": {
            "recommended": "two dots joined by a dashed line, each labeled with its condition (range row with either: true)",
            "why": "A decision gives one value or the other, not anything in between, so a filled span misleads.",
            "avoid": "Drawing the two outcomes as a continuous range.",
            "examples": ["600 h if one system issues invoices, 900 h if the other does"],
        },
    },
    "actual_vs_target": {
        "default": {
            "recommended": "bars or lines where targets and projections are dashed outlines or dashed continuations",
            "why": "A target drawn like an actual value reads as something already achieved.",
            "avoid": "Solid target bars, or a projection in the same stroke as history.",
            "examples": ["Recurring revenue share today against a stated target"],
        },
    },
    "where_is_it": {
        "single_point": {
            "recommended": "locator map with nearby cities or landmarks labeled",
            "why": "The question is where it sits relative to places readers know.",
            "avoid": "A point on a world map with no reference.",
            "examples": ["Breaking-news locator maps"],
        },
        "many_values": {
            "recommended": "choropleth with a sequential ramp, or a hex-binned dot map",
            "why": "Choropleth when values vary by place and matter. Hex bins when raw density matters.",
            "avoid": "A choropleth for absolute counts in dense areas. Size circles by value instead.",
            "examples": ["County-level election maps", "Extreme heat days map"],
        },
    },
    "how_likely": {
        "default": {
            "recommended": "probability bar, gauge or 100-icon array",
            "why": "Shows uncertainty visually. The election needle animated it.",
            "avoid": "A single point estimate with no range.",
            "examples": ["The election needle (2016, 2020, 2024)", "Senate forecast gauges"],
        },
    },
}

QUESTION_TYPES = list(PATTERNS)


def select_chart(question_type, data_shape=None):
    shape = data_shape or {}
    rules = PATTERNS.get(question_type)
    if not rules:
        return {
            "recommended": "line chart (default)",
            "why": "When unsure, start with a line on a time axis.",
            "avoid": "Sankey, chord or radial charts before line and bar have failed.",
            "examples": [],
            "known_question_types": QUESTION_TYPES,
        }
    n_series = shape.get("n_series", 1)
    if question_type == "change_over_time":
        if n_series <= 1:
            return rules["single_series"]
        return rules["few_series"] if n_series <= MAX_SERIES else rules["many_series"]
    if question_type == "compare_categories":
        return rules["few"] if shape.get("n_rows", 0) < 15 else rules["many"]
    if question_type == "show_correlation_over_time":
        return rules["monotonic"] if shape.get("both_axes_monotonic") else rules["non_monotonic"]
    if question_type == "show_composition":
        return rules["over_time"] if shape.get("x_type") == "time" else rules["default"]
    if question_type == "where_is_it":
        return rules["many_values"] if shape.get("n_rows", 1) > 1 else rules["single_point"]
    return rules["default"]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    q = sys.argv[1]
    s = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    print(json.dumps(select_chart(q, s), indent=2))
