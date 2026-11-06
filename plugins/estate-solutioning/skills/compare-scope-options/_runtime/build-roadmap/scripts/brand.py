#!/usr/bin/env python3
"""Compile an org brand profile into a Roadmap Kit theme (theme.css).

Usage:
  python3 brand.py brand.md   -o theme.css   # manage-brand-profile table profile, or an estate profile (JSON block)
  python3 brand.py brand.json -o theme.css   # kit brand JSON (themes/*.json)
  add --allow-draft to compile a profile whose status is not confirmed (only when the user said so)

The theme sets --brand-* custom properties on :root. rk.css reads them in all three modes (Work, Pastel,
Present). A role the profile does not record is left unset, so that mode keeps its own default for it,
and the report says so. The names --brand-background/-text/-muted/-border/-surface/-accent/-font-body/
-font-headings match the estate brand-renderer, so the same profile themes both.

Rules: recorded values only. No color is generated, lightened, darkened or blended. Text-on-color pairs
the profile does not record are picked from recorded colors or white/black by contrast, and reported.
Contrast is checked and reported; it is never fixed by changing a brand color.
"""
import argparse
import base64
import json
import mimetypes
import pathlib
import re
import sys

WHITE, BLACK = "#ffffff", "#0b0b0b"
COLOR_ROLES = ["background", "surface", "border", "text", "muted", "subtle", "accent", "on_accent", "highlight", "dark", "on_dark"]
MD_ROLE = {
    "page ground": "background", "background": "background", "ground": "background",
    "alternate surface": "surface", "surface": "surface", "card": "surface",
    "border": "border", "border and divider": "border", "divider": "border",
    "text": "text", "body text": "text", "muted text": "muted", "secondary text": "muted", "muted": "muted",
    "subtle text": "subtle", "primary": "accent", "single accent": "accent", "text on primary": "on_accent",
    "on primary": "on_accent", "accent": "highlight", "secondary": "highlight", "highlight": "highlight",
    "dark": "dark", "dark ground": "dark", "dark surface": "dark", "text on dark": "on_dark",
}
HEX = re.compile(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b")


def lum(hexv):
    h = hexv.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


def best_on(color, candidates):
    return max([c for c in candidates if c], key=lambda c: contrast(c, color))


# ---------- readers: every format becomes one dict ----------
def empty():
    return {"colors": {}, "chart": [], "fonts": {}, "sources": {}}


def from_kit_json(d):
    b = empty()
    for k in ("name", "status", "source", "confirmed_by", "google_fonts", "font_files", "radius", "logo"):
        if k in d:
            b[k] = d[k]
    lt = d.get("light") or {}
    for src, dst in (("ground", "background"), ("surface", "surface"), ("border", "border"), ("text", "text"),
                     ("muted", "muted"), ("subtle", "subtle"), ("accent", "accent"), ("on_accent", "on_accent"),
                     ("highlight", "highlight"), ("dark", "dark")):
        if lt.get(src):
            b["colors"][dst] = lt[src].lower()
    b["chart"] = [c.lower() for c in (d.get("categorical") or {}).get("light", [])][:6]
    b["fonts"] = d.get("fonts") or {}
    return b


def from_estate_json(d):
    b = empty()
    for k in ("name", "status", "source", "logo"):
        if k in d:
            b[k] = d[k]
    for role, v in (d.get("colors") or {}).items():
        if role in COLOR_ROLES and isinstance(v, str):
            b["colors"][role] = v.lower()
    chart = (d.get("colors") or {}).get("chart") or d.get("chart") or []
    b["chart"] = [c.lower() for c in chart][:6]
    t = d.get("type") or {}
    if t.get("body"):
        b["fonts"]["body"] = {"family": "", "stack": t["body"]}
    if t.get("headings"):
        b["fonts"]["display"] = {"family": "", "stack": t["headings"]}
    rp = (d.get("layout") or {}).get("radius_px")
    if rp is not None:
        b["radius"] = f"{rp}px"
    return b


def from_client_brand_md(text):
    b = empty()
    m = re.search(r"^#\s+(.+?)\s+brand profile", text, re.M | re.I)
    b["name"] = m.group(1).strip() if m else "Unnamed brand"
    for key in ("status", "confirmed_by", "source", "usage_rights"):
        m = re.search(rf"^{key}:\s*(.+)$", text, re.M | re.I)
        if m:
            b[key] = m.group(1).strip()
    section = None
    for line in text.splitlines():
        h = re.match(r"^##\s+(.+)", line)
        if h:
            section = h.group(1).strip().lower()
            continue
        if section and section.startswith("color") and line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 2 or not HEX.search(cells[1] or ""):
                continue
            role, hexv = cells[0].lower(), HEX.search(cells[1]).group(0).lower()
            src = cells[3] if len(cells) > 3 else ""
            cm = re.match(r"(chart|data|series|categorical)\s*(\d)", role)
            if cm:
                idx = int(cm.group(2)) - 1
                while len(b["chart"]) <= idx:
                    b["chart"].append(None)
                b["chart"][idx] = hexv
                b["sources"][f"chart {idx + 1}"] = src
                continue
            r = MD_ROLE.get(role)
            if r and r not in b["colors"]:
                b["colors"][r] = hexv
                b["sources"][r] = src
        if section == "type":
            m = re.match(r"^\s*(headings|display|body)\s*:\s*([^,\n]+?)(?:,|\s{2,}|$)(.*)", line, re.I)
            if m:
                role = "body" if m.group(1).lower() == "body" else "display"
                fam = m.group(2).strip()
                stack = re.search(r"fallback stack:\s*(.+)$", line, re.I)
                b["fonts"][role] = {"family": fam, "stack": stack.group(1).strip() if stack else ""}
                if re.search(r"google", line, re.I):
                    weights = sorted(set(re.findall(r"\b([1-9]00)\b", m.group(3)))) or ["400"]
                    if role == "body":
                        weights = sorted(set(weights + ["500", "600"]))
                    spec = "family=" + fam.replace(" ", "+") + ":wght@" + ";".join(weights)
                    b["google_fonts"] = "&".join(x for x in (b.get("google_fonts"), spec) if x)
        if section == "logo":
            m = re.match(r"^\s*files?:\s*(.+)$", line, re.I)
            if m:
                b["logo"] = {"file": m.group(1).split(",")[0].strip(), "alt": b["name"]}
        if section == "layout":
            m = re.search(r"radius[^0-9]*(\d+(?:\.\d+)?px|none)", line, re.I)
            if m:
                b["radius"] = "0px" if m.group(1).lower() == "none" else m.group(1)
    b["chart"] = [c for c in b["chart"] if c][:6]
    return b


def read_profile(path):
    text = path.read_text()
    if path.suffix == ".json":
        d = json.loads(text)
        return from_estate_json(d) if "colors" in d else from_kit_json(d)
    block = re.search(r"```json\s*(\{.*?\})\s*```", text, re.S)
    if block and '"colors"' in block.group(1):
        return from_estate_json(json.loads(block.group(1)))
    return from_client_brand_md(text)


# ---------- resolve, check, emit ----------
def resolve(b):
    col, rep = dict(b["colors"]), {"default": [], "picked": [], "warnings": []}
    defaults = {"background": "page", "surface": "surfaces", "border": "rules and borders", "text": "text",
                "muted": "secondary text", "accent": "accent (buttons, focus, Present big numbers)"}
    for role, what in defaults.items():
        if not col.get(role):
            rep["default"].append(f"{role}: each mode keeps its own {what}")
    if col.get("accent") and not col.get("on_accent"):
        col["on_accent"] = best_on(col["accent"], [col.get("background"), col.get("text"), WHITE, BLACK])
        rep["picked"].append(f"on_accent {col['on_accent']} (best contrast on accent)")
    if not col.get("highlight"):
        if len(b["chart"]) > 1:
            col["highlight"] = b["chart"][1]
            rep["picked"].append(f"highlight uses chart 2 {col['highlight']} (Present corner shape, Work column dot)")
        else:
            rep["default"].append("highlight: each mode keeps its own second accent")
    if not col.get("dark"):
        if col.get("text"):
            col["dark"] = col["text"]
            rep["picked"].append(f"dark uses text {col['dark']} (Present timeline band)")
        else:
            rep["default"].append("dark: Present keeps its own timeline band")
    if col.get("dark") and not col.get("on_dark"):
        col["on_dark"] = best_on(col["dark"], [col.get("background"), WHITE])
        rep["picked"].append(f"on_dark {col['on_dark']} (text on the Present band)")
    chart = list(b["chart"])
    if len(chart) < 6:
        rep["default"].append(f"chart slots {len(chart) + 1} to 6: each mode keeps its own colors" if chart else "chart colors: each mode keeps its own palette (profile records none)")
    ons = [best_on(c, [col.get("text"), col.get("background"), WHITE, BLACK]) for c in chart]
    return col, chart, ons, rep


def check(col, chart, ons, rep):
    pairs = []

    def need(label, fg, bg, floor):
        if fg and bg:
            r = contrast(fg, bg)
            pairs.append((label, r, floor))
            if r < floor:
                rep["warnings"].append(f"{label}: {r:.2f}:1 is under {floor}:1")

    need("text on background", col.get("text"), col.get("background"), 4.5)
    need("text on surface", col.get("text"), col.get("surface"), 4.5)
    need("muted text on background", col.get("muted"), col.get("background"), 4.5)
    need("label on accent", col.get("on_accent"), col.get("accent"), 4.5)
    need("text on dark band", col.get("on_dark"), col.get("dark"), 4.5)
    for i, (c, o) in enumerate(zip(chart, ons), 1):
        need(f"label on chart {i}", o, c, 4.5)
    return pairs


def font_rules(b, base):
    imports, faces, vars_ = [], [], []
    for f in b.get("font_files") or []:
        p = (base / f["file"]).resolve()
        mime = mimetypes.guess_type(p.name)[0] or "font/woff2"
        data = base64.b64encode(p.read_bytes()).decode()
        faces.append(f'@font-face {{ font-family: "{f["family"]}"; src: url(data:{mime};base64,{data}); '
                     f'font-weight: {f.get("weight", "400")}; font-style: {f.get("style", "normal")}; font-display: swap; }}')
    if b.get("google_fonts"):
        imports.append(f'@import url("https://fonts.googleapis.com/css2?{b["google_fonts"]}&display=swap");')
    fonts = b.get("fonts") or {}

    def value(f):
        if not f:
            return None
        fam, stack = (f.get("family") or "").strip(), (f.get("stack") or "").strip()
        if fam:
            return f'"{fam}", {stack or "system-ui, sans-serif"}'
        return stack or None

    body, display = value(fonts.get("body")), value(fonts.get("display"))
    if body:
        vars_.append(f"  --brand-font-body: {body};")
    if display:
        vars_.append(f"  --brand-font-headings: {display};")
    return imports, faces, vars_


def emit(b, col, chart, ons, base):
    imports, faces, fvars = font_rules(b, base)
    lines = [f"  --brand-{r.replace('_', '-')}: {col[r]};" for r in COLOR_ROLES if col.get(r)]
    for i, (c, o) in enumerate(zip(chart, ons), 1):
        lines.append(f"  --brand-chart-{i}: {c}; --brand-chart-{i}-on: {o};")
    if b.get("radius"):
        lines.append(f"  --brand-radius: {b['radius']}; --brand-radius-lg: {b['radius']};")
    head = f"/* Roadmap Kit theme: {b.get('name')} ({b.get('status', 'unknown')}). Built by scripts/brand.py; do not edit by hand. */"
    return "\n".join(imports + [head] + faces) + "\n:root {\n" + "\n".join(lines + fvars) + "\n}\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("profile")
    ap.add_argument("-o", "--out")
    ap.add_argument("--allow-draft", action="store_true")
    a = ap.parse_args()
    path = pathlib.Path(a.profile)
    b = read_profile(path)
    status = (b.get("status") or "").lower()
    if status != "confirmed" and not a.allow_draft:
        sys.exit(f"brand '{b.get('name')}' is {status or 'unmarked'}, not confirmed. Show the values to the user; "
                 "re-run with --allow-draft only if they say to proceed on the draft.")
    col, chart, ons, rep = resolve(b)
    pairs = check(col, chart, ons, rep)
    css = emit(b, col, chart, ons, path.parent)
    if a.out:
        pathlib.Path(a.out).write_text(css)
    print(f"Theme: {b.get('name')} · status {status or 'unmarked'}" + (f" · confirmed by {b['confirmed_by']}" if b.get("confirmed_by") else ""))
    print(f"Recorded: {', '.join(r for r in COLOR_ROLES if b['colors'].get(r)) or 'no colors'}; {len(chart)} chart colors; "
          f"fonts: {', '.join(k for k in (b.get('fonts') or {})) or 'none'}")
    for k, label in (("picked", "Picked from recorded colors"), ("default", "Not in the profile (mode defaults apply)"), ("warnings", "Contrast warnings")):
        if rep[k]:
            print(f"{label}:")
            for x in rep[k]:
                print("  -", x)
    if pairs:
        worst = min(pairs, key=lambda p: p[1] / p[2])
        print(f"Contrast: {len(pairs)} pairs checked; tightest is {worst[0]} at {worst[1]:.2f}:1 (floor {worst[2]}:1).")
    if a.out:
        print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
