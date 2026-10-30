#!/usr/bin/env python3
"""Embed roadmap components in single-file estate pages.

Estate pages carry their data, styles and scripts inline and load nothing from
the network. Their colors, fonts, radius and border width come from the
selected brand profile through brand-renderer's palette (`--brand-*`,
`--font-sans`, `--radius`, `--brand-border-width`). This module turns the kit
stylesheet into that form: no web font import, no hex values, every color a
profile role, every corner the profile radius and every border the profile
width.

    python3 scripts/rk_embed.py page plan.json --output roadmap.html [--profile brand.md]
    python3 scripts/rk_embed.py css > rk-estate.css

Host builders call `assets()` and place the CSS and JS in their own template.
"""
import argparse
import functools
import hashlib
import html
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"

# Status tones come from the profile's status roles. The text tone is mixed
# with the text color so it reads at body contrast; the ground is a light tint.
# A profile without a status role shows that tone in text and surface colors,
# and the tag's label still carries the meaning.
TONES = (
    "--good: color-mix(in srgb, var(--brand-status-good, var(--brand-text)) 50%, var(--brand-text));"
    " --good-t: color-mix(in srgb, var(--brand-status-good, var(--brand-surface)) 14%, var(--brand-background));"
    " --warn: color-mix(in srgb, var(--brand-status-warning, var(--brand-text)) 50%, var(--brand-text));"
    " --warn-t: color-mix(in srgb, var(--brand-status-warning, var(--brand-surface)) 18%, var(--brand-background));"
    " --crit: color-mix(in srgb, var(--brand-status-critical, var(--brand-text)) 70%, var(--brand-text));"
    " --crit-t: color-mix(in srgb, var(--brand-status-critical, var(--brand-surface)) 12%, var(--brand-background));"
    " --info: var(--brand-accent); --info-t: color-mix(in srgb, var(--brand-accent) 10%, var(--brand-background));"
)

# Kit settings an estate profile may not record, and the profile role each falls back to.
FALLBACKS = {
    "on-accent": "var(--rk-on-accent)",
    "highlight": "var(--brand-chart-2, var(--brand-accent))",
    "dark": "var(--brand-text)",
    "on-dark": "var(--brand-background)",
    "on-dark-muted": "var(--brand-border)",
    "border-strong": "var(--brand-muted)",
    "subtle": "var(--brand-muted)",
    "surface-2": "var(--brand-surface)",
}
# Roles every confirmed profile records (brand_profile.load_profile) or the palette always emits.
CORE = {"background", "text", "muted", "border", "surface", "accent", "border-width"}
for n in range(1, 7):
    FALLBACKS["chart-%d" % n] = "var(--brand-accent)"
    FALLBACKS["chart-%d-on" % n] = "var(--rk-chart-%d-on)" % n

STATUS_ROLES = ("status-good", "status-warning", "status-critical")


def adapter(colors=None):
    """Settings that map the kit onto estate palette variables."""
    colors = colors or {}

    def on(role):
        # Text on a filled role: the profile's text or background color, whichever contrasts more.
        value = colors.get(role)
        if not value or "text" not in colors or "background" not in colors:
            return "var(--brand-background)" if role in ("accent", "dark") else "var(--brand-text)"
        contrast = brand_runtime()[1].contrast
        return ("var(--brand-text)" if contrast(value, colors["text"]) >= contrast(value, colors["background"])
                else "var(--brand-background)")

    settings = ["--brand-font-body: var(--font-sans)", "--brand-radius: var(--radius)",
                "--rk-on-accent: " + on("accent")]
    settings += ["--rk-chart-%d-on: %s" % (n, on("chart-%d" % n)) for n in range(1, 7)]
    relaxed = []
    for n in range(1, 7):
        # Relaxed fills cards with a light tint of each group color, so any brand palette keeps its calm look.
        relaxed.append("--c%d: color-mix(in srgb, var(--brand-chart-%d, var(--brand-accent)) 26%%, var(--brand-background)); "
                       "--c%do: var(--brand-text); --c%di: var(--brand-text)" % (n, n, n, n))
    return ("\n.rk { " + "; ".join(settings) + "; }\n"
            ".rk, .rk[data-rk-mode] { --r-sm: var(--radius); --r: var(--radius); --r-lg: var(--radius); }\n"
            '.rk[data-rk-mode="relaxed"] { ' + "; ".join(relaxed) + "; }\n")


def estate_css(colors=None, css=None):
    """Return the kit stylesheet in the estate's profile-only form.

    colors is the selected profile's color map. It decides text-on-color pairs;
    without it the stylesheet assumes a light background and dark text.
    """
    css = css if css is not None else (ASSETS / "rk.css").read_text(encoding="utf-8")
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"@import\s+url\([^)]*\)[^;]*;\s*", "", css)
    status = re.search(r"--good:[^}]*?--info-t:\s*#[0-9a-fA-F]{6};", css)
    if not status:
        raise ValueError("Kit stylesheet has no status tone line")
    css = css[:status.start()] + TONES + css[status.end():]
    previous = None
    while previous != css:
        previous = css
        css = re.sub(r",\s*#[0-9a-fA-F]{3,8}\s*\)", ")", css)
    for role, fallback in FALLBACKS.items():
        css = css.replace("var(--brand-%s)" % role, "var(--brand-%s, %s)" % (role, fallback))
    css = re.sub(r"border-radius:\s*[12]px", "border-radius: 0", css)
    css = re.sub(r"(border(?:-top|-left|-right|-bottom)?:\s*)2px\b", r"\1var(--brand-border-width)", css)
    # Kit sizes become a minimum the host can raise with --rk-min-text.
    css = re.sub(r"font-size:\s*(\d+(?:\.\d+)?)px", r"font-size: max(\1px, var(--rk-min-text, 0px))", css)
    css = re.sub(r"\n\s*\n+", "\n", css).strip() + "\n" + adapter(colors)
    bare = set(re.findall(r"var\(--brand-([a-z0-9-]+)\)", css)) - CORE
    if bare:
        raise ValueError("Optional brand settings need a fallback: " + ", ".join(sorted(bare)))
    leftover = re.findall(r"#[0-9a-fA-F]{3,8}\b", css)
    if leftover:
        raise ValueError("Estate stylesheet still has fixed colors: " + ", ".join(sorted(set(leftover))))
    if re.search(r"https?:|@import|url\(", css):
        raise ValueError("Estate stylesheet must not load remote resources")
    return css


def assets(colors=None):
    """CSS and JS for an inline host page. Live connector code is not included."""
    js = (ASSETS / "rk.js").read_text(encoding="utf-8")
    if "</script" in js.lower():
        raise ValueError("Kit script cannot be inlined")
    return {"css": estate_css(colors), "js": js}


def script_json(value):
    """JSON that cannot close its script element."""
    return (json.dumps(value, ensure_ascii=False)
            .replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026"))


def status_report(profile_colors):
    missing = [role for role in STATUS_ROLES if role not in profile_colors]
    return ["Status tone {} is not in the profile; that tone uses text and surface colors.".format(r)
            for r in missing]


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
*{box-sizing:border-box}body{margin:0;background:var(--brand-background);color:var(--brand-text);font:var(--fs-body)/1.5 var(--font-sans)}
main{max-width:1280px;margin:0 auto;padding:24px 16px 48px}
__RK_CSS__
</style></head><body>
<main><div class="rk rk-embed" id="roadmap"></div></main>
<script type="application/json" id="rk-plan">__PLAN__</script>
<script>__RK_JS__</script>
<script>RoadmapKit.mount(JSON.parse(document.getElementById("rk-plan").textContent), document.getElementById("roadmap"), {embed: true, live: false});</script>
</body></html>
"""


@functools.lru_cache(maxsize=None)
def brand_runtime():
    for path in (HERE.parent / "_runtime/brand-renderer/brand", HERE.parent.parent / "brand-renderer/brand"):
        if (path / "html_profile.py").is_file():
            sys.path.insert(0, str(path))
            import html_profile
            import brand_profile
            return html_profile, brand_profile
    raise RuntimeError("Brand runtime is missing. Rebuild this skill with its declared dependencies.")


def build_page(plan, profile=None):
    sys.path.insert(0, str(HERE))
    from build import check, cited
    problems = check(plan)
    if problems:
        raise ValueError("Plan check failed:\n- " + "\n- ".join(problems))
    if cited(plan) and not any(b.get("type") == "evidence" for b in plan.get("blocks", [])):
        raise ValueError("A standalone page with cite numbers needs an evidence block for them to point to")
    if plan.get("live"):
        raise ValueError("A single-file estate page cannot hold live bindings; build a snapshot")
    html_profile, brand_profile = brand_runtime()
    colors = brand_profile.load_profile(brand_profile.resolve_profile(str(profile) if profile else None))["colors"]
    kit = assets(colors)
    title = html.escape(str(plan.get("meta", {}).get("title", "Roadmap")), quote=False)
    document = (PAGE.replace("__TITLE__", title).replace("__RK_CSS__", kit["css"])
                .replace("__PLAN__", script_json(plan)).replace("__RK_JS__", kit["js"]))
    document, resource = html_profile.apply_profile(document, str(profile) if profile else None)
    return document, resource, status_report(colors)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("css", help="print the estate stylesheet")
    page = sub.add_parser("page", help="build a single-file branded roadmap page")
    page.add_argument("plan", type=Path)
    page.add_argument("--output", type=Path, required=True)
    page.add_argument("--profile", type=Path)
    args = parser.parse_args()
    if args.command == "css":
        sys.stdout.write(estate_css())
        return
    if args.output.exists():
        parser.error("Output exists; choose a new attempt")
    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
        document, resource, notes = build_page(plan, args.profile)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(document, encoding="utf-8")
    except (ValueError, OSError, RuntimeError) as error:
        parser.exit(2, str(error) + "\n")
    print(json.dumps({"state": "built; browser and brand review required", "profile": resource["name"],
                      "planSha256": hashlib.sha256(args.plan.read_bytes()).hexdigest(),
                      "artifactSha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
                      "notes": notes}, indent=2))


if __name__ == "__main__":
    main()
