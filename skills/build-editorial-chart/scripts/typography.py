#!/usr/bin/env python3
"""
Editorial chart typography.

Default profile: Inter for everything (Baseline). Numbers use tabular figures so
digits stay aligned in tables, axes and transitions. No monospace.

Optional `newsroom` profile, only when the newspaper look is requested: a display
serif for headlines (Playfair Display, standing in for the Times' Cheltenham) and a
text serif for long body copy (Source Serif 4, standing in for Imperial). Chart
labels, axes and annotations stay in Inter in both profiles.

Scale:
  headline       700, clamp(26px, 5vw, 44px), states the finding as a sentence
  subtitle       400, 16px, --ink2, names unit and timeframe
  chart title    600, 17px
  axis + labels  400, 12px, --ink2, tabular
  annotation     500, 12.5px, --ink, haloed
  source line    400, 12px, --ink3

Brand override: when the chart belongs to a product or client with its own
design system, pass a `brand` dict instead of relying on Inter and Baseline:
    {"font": "Hanken Grotesk",                    # one Google Fonts sans family
     "light": {"--bg": "#F7F9FB", "--hero": ...},  # any chart token to replace
     "dark":  {"--bg": "#131316", ...}}
Token names are the ones palette.css_variables() emits. Tokens the brand leaves
out keep the scheme's values. Monospace families are rejected.

Usage:
    python3 -I typography.py [default|newsroom] [scheme]
"""
import html
import re
import sys
from urllib.parse import quote_plus
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from palette import css_variables  # noqa: E402

FONT_LINKS = {
    "default": (
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" '
        'rel="stylesheet">'
    ),
    "newsroom": (
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&'
        'family=Playfair+Display:ital,wght@0,700;0,900;1,700&'
        'family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap" rel="stylesheet">'
    ),
}

FONT_VARS = {
    "default": (
        '  --font-sans: "Inter", system-ui, -apple-system, "Segoe UI", sans-serif;\n'
        "  --font-display: var(--font-sans);\n"
        "  --font-body: var(--font-sans);\n"
    ),
    "newsroom": (
        '  --font-sans: "Inter", system-ui, -apple-system, "Segoe UI", sans-serif;\n'
        '  --font-display: "Playfair Display", Georgia, serif;\n'
        '  --font-body: "Source Serif 4", Georgia, serif;\n'
    ),
}

BASE_CSS = """
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--font-body);
  font-size:17px;line-height:1.55;-webkit-font-smoothing:antialiased}
.container{max-width:720px;margin:0 auto;padding:32px 16px 48px}
h1.headline{font-family:var(--font-display);font-weight:700;font-size:clamp(26px,5vw,44px);
  line-height:1.1;letter-spacing:-.01em;margin:0 0 10px;text-wrap:balance}
.subtitle{font-family:var(--font-sans);font-size:16px;color:var(--ink2);line-height:1.45;margin:0 0 20px}
.chart-title{font-family:var(--font-sans);font-weight:600;font-size:17px;line-height:1.25;margin:0 0 4px}
.chart-source,.chart-note{font-family:var(--font-sans);font-size:12px;color:var(--ink3);margin-top:8px}
svg text{font-family:var(--font-sans)}
.axis text,.chart-label{font-size:12px;fill:var(--ink2)}
.anno,.chart-annotation{font-size:12.5px;font-weight:500;fill:var(--ink);
  paint-order:stroke fill;stroke:var(--panel);stroke-width:3px;stroke-linejoin:round}
.tabular,.value-label,.axis text,svg text,td.num{font-variant-numeric:tabular-nums}
.axis line,.axis path{stroke:var(--rule);shape-rendering:crispEdges}
.axis .domain{display:none}
.gridline,.grid line{stroke:var(--grid);shape-rendering:crispEdges}
.grid .domain{display:none}
"""


MONO = re.compile(r"mono|courier|consolas|menlo|code", re.I)
TOKEN = re.compile(r"^--[a-z0-9-]+$")
VALUE = re.compile(r"^[#(),.%\w\s-]+$")


def _check_brand(brand):
    font = brand.get("font")
    if font is not None and (not re.fullmatch(r"[A-Za-z0-9 ]+", font) or MONO.search(font)):
        raise ValueError(f"Brand font '{font}' must be one non-monospace Google Fonts family name.")
    for side in ("light", "dark"):
        for k, v in (brand.get(side) or {}).items():
            if not TOKEN.match(k) or not VALUE.match(str(v)):
                raise ValueError(f"Brand token {k}: {v} is not a plain CSS custom property value.")


def font_links(profile="default", brand=None):
    """<link> tags for the profile, or for the brand's font when one is given."""
    if brand and brand.get("font"):
        _check_brand(brand)
        fam = quote_plus(brand["font"])
        return ('<link rel="preconnect" href="https://fonts.googleapis.com">'
                '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
                f'<link href="https://fonts.googleapis.com/css2?family={fam}:wght@400;500;600;700&display=swap" '
                'rel="stylesheet">')
    return FONT_LINKS[profile]


def brand_css(brand):
    """Token overrides layered after the scheme, in light and both dark selectors."""
    _check_brand(brand)
    css = ""
    if brand.get("font"):
        f = brand["font"]
        css += (f':root{{--font-sans:"{f}",system-ui,-apple-system,"Segoe UI",sans-serif;'
                "--font-display:var(--font-sans);--font-body:var(--font-sans)}\n")

    def block(d):
        return "".join(f"{k}:{v};" for k, v in d.items())

    if brand.get("light"):
        css += f":root{{{block(brand['light'])}}}\n"
    if brand.get("dark"):
        d = block(brand["dark"])
        css += (f'@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{{d}}}}}\n'
                f':root[data-theme="dark"]{{{d}}}\n')
    return css


def font_css(profile="default", scheme="F", brand=None):
    if profile not in FONT_LINKS:
        raise ValueError(f"Unknown profile '{profile}'. Choose default or newsroom.")
    css = css_variables(scheme) + ":root{\n" + FONT_VARS[profile] + "}\n"
    if brand:
        css += brand_css(brand)
    return css + BASE_CSS


def emit_head(title="Chart", profile="default", scheme="F", extra_css="", brand=None):
    """Return a complete <head> block."""
    return (
        "<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{html.escape(title)}</title>\n{font_links(profile, brand)}\n"
        f"<style>{font_css(profile, scheme, brand)}{extra_css}</style>\n</head>"
    )


if __name__ == "__main__":
    prof = sys.argv[1] if len(sys.argv) > 1 else "default"
    sch = sys.argv[2] if len(sys.argv) > 2 else "F"
    print(emit_head("Chart", prof, sch))
