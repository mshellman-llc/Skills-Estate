"""Embed a selected brand profile in a standalone HTML artifact."""
import base64
import html
import mimetypes
from pathlib import Path
import re

from brand_profile import compile_tokens, load_profile, resolve_profile


def kebab(value):
    return re.sub(r"([a-z])([0-9])", r"\1-\2", re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", value)).lower()


def data_uri(path):
    mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
    return "data:{};base64,{}".format(mime, base64.b64encode(Path(path).read_bytes()).decode())


def resolve_file(value, profile_path):
    if not isinstance(value, str) or not value:
        raise ValueError("A declared asset needs a local file path")
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = profile_path.parent / path
    if not path.is_file():
        raise ValueError("Selected profile asset is missing: {}".format(path))
    return path


def resources(explicit=None):
    path = resolve_profile(explicit)
    profile = load_profile(path)
    tokens = compile_tokens(profile, path)
    values = {kebab(key): value["hex"] for key, value in tokens["colors"].items()}
    # Existing layouts keep their variable names; values remain profile-owned.
    aliases = {"navy": "deep-navy", "navy2": "lighter-navy", "ltteal": "light-teal",
               "pale": "teal-pale", "teal-lt": "teal-light", "steel": "steel-blue",
               "bluegray": "blue-gray", "coolgray": "cool-gray", "ice": "ice-blue",
               "ink": "fg", "ink2": "fg-secondary", "muted": "fg-muted"}
    for key, source in aliases.items():
        values[key] = values[source]
    font_stack = profile["type"]["body"]
    declarations = [f"--{key}:{value};" for key, value in values.items()]
    declarations += [f"--brand-{key}:{value};" for key, value in profile["colors"].items()]
    declarations += [f"--font-sans:{font_stack};", f"--f:{font_stack};",
                     f"--brand-font-headings:{profile['type']['headings']};",
                     f"--radius:{profile['layout']['radius_px']}px;",
                     f"--radius-sm:{profile['layout']['radius_px']}px;",
                     f"--brand-border-width:{profile['layout']['border_px']}px;",
                     f"--brand-body-min-pt:{profile['type'].get('body_min_pt', 11)}pt;",
                     f"--fs-body:{profile['type'].get('screen_min_px', 16)}px;"]
    palette = ":root{" + "".join(declarations) + "}"
    font_faces = []
    family = font_stack.split(",")[0].strip().strip("'\"")
    weights = {"regular": 400, "medium": 500, "semibold": 600, "bold": 700, "extrabold": 800}
    for style, value in profile["type"].get("files", {}).items():
        if style.lower() not in weights:
            raise ValueError("type.files keys must name a weight: " + ", ".join(weights))
        file = resolve_file(value, path)
        font_faces.append('@font-face{font-family:"' + family + '";src:url("' + data_uri(file) +
                          '");font-weight:' + str(weights[style.lower()]) + ';font-style:normal;font-display:swap;}')
    logo = profile.get("logo")
    if isinstance(logo, dict):
        logo = logo.get("path", "")
    logo_uri = data_uri(resolve_file(logo, path)) if logo is not None else None
    return {"profile": str(path), "name": profile["name"], "palette": palette,
            "fonts": "\n".join(font_faces), "logo": logo_uri, "font_stack": font_stack}


def apply_profile(document, explicit=None):
    resource = resources(explicit)
    # These slots belong to older producer templates, not to authored content.
    document = re.sub(r"@font-face\s*\{[^}]*\{\{FONT_[A-Z_]+\}\}[^}]*\}", "", document)
    document = re.sub(r'url\(["\']?data:image/[^)]*\{\{BG_[A-Z_]+\}\}[^)]*\)', "none", document)
    logo_slots = ("__MARK__", "__LOGO__", "{{LOGO_WHITE}}")
    if resource["logo"] is None:
        for slot in logo_slots:
            document = re.sub(r"<img\b[^>]*" + re.escape(slot) + r"[^>]*>", "", document)
    else:
        document = document.replace("data:image/png;base64,{{LOGO_WHITE}}", resource["logo"])
        for slot in ("__MARK__", "__LOGO__"):
            document = document.replace(slot, resource["logo"])
    document = document.replace("__PALETTE__", resource["palette"])
    document = document.replace("__FONTS__", resource["fonts"])
    if resource["palette"] not in document:
        document = document.replace("</head>", "<style>\n" + resource["fonts"] + "\n" +
                                    resource["palette"] + "\n</style>\n</head>", 1)
    if re.search(r"__(?:PALETTE|FONTS|MARK|LOGO)__|\{\{(?:FONT|LOGO|BG)_[A-Z_]+\}\}", document):
        raise ValueError("Unresolved brand asset slot in HTML")
    return document, resource
