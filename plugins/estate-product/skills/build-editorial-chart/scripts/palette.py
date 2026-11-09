#!/usr/bin/env python3
"""
Editorial chart palettes built on the Baseline design system.

Rules (from Times graphics practice and ColorBrewer):
1. Never use rainbow or evenly spaced HSV hues. Sequential ramps keep lightness
   monotonic so colorblind readers and greyscale print see the same order.
2. Diverging scales need a midpoint you can name (zero, parity, normal).
3. Series colors are a tonal ramp of one hue. Past five series, use small
   multiples instead of more colors.
4. One hero color per chart. Every other series is one grey.

Default scheme is Baseline palette F (navy). Palette E (ink and amber) is the
alternate. Pass scheme="E" to switch.

Usage:
    python3 -I palette.py sequential [F|E] [n]
    python3 -I palette.py series [F|E] [n]
    python3 -I palette.py hero [F|E] [series_count]
    python3 -I palette.py diverging [name] [n]
    python3 -I palette.py check "#hex,#hex,..."
    python3 -I palette.py css [F|E]
"""
import json
import sys

# Baseline palette tokens. Ramps run dark to light (600 -> 50).
SCHEMES = {
    "F": {
        "name": "navy and pastel",
        "hero": "#37437D",
        "hero_dark": "#B5CAFA",  # hero on dark backgrounds
        "ramp": ["#24265B", "#434D90", "#6577BD", "#8BA1DE", "#B5CAFA", "#E8F0FF", "#F5F8FF"],
    },
    "E": {
        "name": "ink and amber",
        "hero": "#B16F25",
        "hero_dark": "#FBC27B",
        "ramp": ["#362C20", "#6E4C27", "#B16F25", "#E69228", "#FBC27B", "#FDE7C8", "#FFF9F0"],
    },
}

# Baseline neutrals, shared by both schemes.
NEUTRALS = {
    "n0": "#FFFFFF", "n25": "#FAFAFA", "n50": "#F5F5F5", "n100": "#EEEEF0",
    "n200": "#E2E2E3", "n300": "#CBCBCC", "n400": "#B2B3B5", "n500": "#797B7E",
    "n600": "#535559", "n700": "#2E3135", "n900": "#11141A",
}

CONTEXT_GREY = {"light": NEUTRALS["n400"], "dark": NEUTRALS["n600"]}

# Diverging: ColorBrewer, perceptually balanced. Only with a named midpoint.
DIVERGING = {
    "red-blue": ["#67001f", "#b2182b", "#d6604d", "#f4a582", "#fddbc7", "#f7f7f7",
                 "#d1e5f0", "#92c5de", "#4393c3", "#2166ac", "#053061"],
    "brown-teal": ["#543005", "#8c510a", "#bf812d", "#dfc27d", "#f6e8c3", "#f5f5f5",
                   "#c7eae5", "#80cdc1", "#35978f", "#01665e", "#003c30"],
    "purple-green": ["#40004b", "#762a83", "#9970ab", "#c2a5cf", "#e7d4e8", "#f7f7f7",
                     "#d9f0d3", "#a6dba0", "#5aae61", "#1b7837", "#00441b"],
}

MAX_SERIES = 5


def _scheme(scheme):
    s = SCHEMES.get((scheme or "F").upper())
    if s is None:
        raise ValueError(f"Unknown scheme '{scheme}'. Choose from {list(SCHEMES)}.")
    return s


def _sample(ramp, n):
    if n < 1:
        raise ValueError("Need at least one color.")
    if n == 1:
        return [ramp[len(ramp) // 2]]
    step = (len(ramp) - 1) / (n - 1)
    return [ramp[round(i * step)] for i in range(n)]


def relative_luminance(hex_color):
    h = hex_color.lstrip("#")
    if len(h) != 6:
        raise ValueError(f"Expected #RRGGBB, got '{hex_color}'.")
    chans = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        chans.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = chans
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def is_monotonic(colors):
    """True when luminance strictly rises or strictly falls across the list."""
    lum = [relative_luminance(c) for c in colors]
    up = all(a < b for a, b in zip(lum, lum[1:]))
    down = all(a > b for a, b in zip(lum, lum[1:]))
    return up or down


def palette(kind, scheme="F", n=5, name=None):
    """
    kind: 'sequential' | 'series' | 'hero' | 'diverging'
    sequential: n steps of the scheme ramp, dark to light, all 7 steps available.
    series:     n distinct series colors from the first five ramp steps.
    hero:       [hero] + one context grey repeated for the other n-1 series.
    diverging:  odd count from a ColorBrewer diverging ramp (name).
    """
    if kind == "sequential":
        return _sample(_scheme(scheme)["ramp"], n)
    if kind == "series":
        if n > MAX_SERIES:
            raise ValueError(
                f"{n} series is more than {MAX_SERIES}. Use small multiples, one panel per series, "
                "instead of more colors.")
        return _sample(_scheme(scheme)["ramp"][:5], n)
    if kind == "hero":
        if n < 1:
            raise ValueError("Need at least one series.")
        return [_scheme(scheme)["hero"]] + [CONTEXT_GREY["light"]] * (n - 1)
    if kind == "diverging":
        ramp = DIVERGING.get(name or "red-blue")
        if ramp is None:
            raise ValueError(f"Unknown diverging ramp '{name}'. Choose from {list(DIVERGING)}.")
        if n % 2 == 0:
            n += 1  # keep a neutral midpoint
        return _sample(ramp, n)
    raise ValueError(f"Unknown palette kind '{kind}'.")


def css_variables(scheme="F"):
    """Chart tokens for light and dark themes, following the artifact theming contract."""
    s = _scheme(scheme)
    r = s["ramp"]
    light = {
        "--bg": NEUTRALS["n25"], "--panel": NEUTRALS["n0"], "--ink": NEUTRALS["n900"],
        "--ink2": NEUTRALS["n600"], "--ink3": NEUTRALS["n500"], "--rule": NEUTRALS["n200"],
        "--grid": NEUTRALS["n100"], "--hero": s["hero"], "--hero-soft": r[4],
        "--context": CONTEXT_GREY["light"], "--tip-bg": NEUTRALS["n900"], "--tip-ink": NEUTRALS["n0"],
        **{f"--seq-{i}": c for i, c in enumerate(r)},
    }
    dark = {
        "--bg": NEUTRALS["n900"], "--panel": "#171A21", "--ink": NEUTRALS["n50"],
        "--ink2": NEUTRALS["n300"], "--ink3": NEUTRALS["n400"], "--rule": NEUTRALS["n700"],
        "--grid": "#22262D", "--hero": s["hero_dark"], "--hero-soft": r[2],
        "--context": CONTEXT_GREY["dark"], "--tip-bg": NEUTRALS["n50"], "--tip-ink": NEUTRALS["n900"],
        **{f"--seq-{i}": c for i, c in enumerate(reversed(r))},
    }

    def block(d):
        return "\n".join(f"  {k}: {v};" for k, v in d.items())

    return (
        f":root {{\n  color-scheme: light dark;\n{block(light)}\n}}\n"
        f"@media (prefers-color-scheme: dark) {{\n  :root:not([data-theme=\"light\"]) {{\n{block(dark)}\n  }}\n}}\n"
        f":root[data-theme=\"dark\"] {{\n{block(dark)}\n}}\n"
    )


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    kind = args[0]
    if kind == "check":
        cols = [c.strip() for c in args[1].split(",")]
        print(json.dumps({"monotonic": is_monotonic(cols),
                          "luminance": [round(relative_luminance(c), 4) for c in cols]}))
    elif kind == "css":
        print(css_variables(args[1] if len(args) > 1 else "F"))
    elif kind == "diverging":
        print(json.dumps(palette(kind, name=args[1] if len(args) > 1 else None,
                                 n=int(args[2]) if len(args) > 2 else 7)))
    else:
        print(json.dumps(palette(kind, scheme=args[1] if len(args) > 1 else "F",
                                 n=int(args[2]) if len(args) > 2 else 5)))
