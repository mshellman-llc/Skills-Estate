#!/usr/bin/env python3
"""Render a playbook into an internal brief and external one-page PDF: internal brief + external one-pager.

Input modes:
  --md CORPUS.md --entry 01        parse one house-format entry and render
  --md CORPUS.md --all             render every entry in a house-format corpus
  --json SPEC.json                 render from an explicit spec (qualifiers,
                                   talking tracks, steps, callouts)

Missing declared assets, unrecognized source labels, empty required slots, and
page overflow fail the run. Every generated HTML, PDF, screenshot and check result
is retained. A neutral profile needs no logo or custom font.

Requires: jinja2, pypdf, Node.js, Playwright and Chromium
"""
import argparse, hashlib, json, re, sys, datetime
from pathlib import Path

# ---------- layout resolution ----------
# Works whether the skill is laid out as scripts/ + templates/ + assets/, or
# flat (which is what FetchSkillScripts produces).
def resolve_root():
    here = Path(__file__).resolve().parent
    for cand in (here.parent, here):
        if (cand / "templates").is_dir() and (cand / "assets").is_dir():
            return cand
    for cand in (here, here.parent):
        if (cand / "internal_brief.html").is_file():
            return cand
    return here.parent


ROOT = resolve_root()
FLAT = (ROOT / "internal_brief.html").is_file()
TPL = ROOT if FLAT else ROOT / "templates"
ASSETS = ROOT if FLAT else ROOT / "assets"

EXPECTED_PAGES = {"internal_brief.html": 2, "external_onepager.html": 1}

WARNINGS = []


def warn(msg):
    WARNINGS.append(msg)
    print("  WARN  " + msg, file=sys.stderr)


def die(msg, code=2):
    print("ERROR: " + msg, file=sys.stderr)
    sys.exit(code)


# ---------- preflight ----------
def preflight(profile=None):
    from brand_runtime import resources
    for file in (TPL / "internal_brief.html", TPL / "external_onepager.html", ASSETS / "brand.css"):
        if not file.is_file():
            die("Missing renderer file: " + str(file))
    resource = resources(profile)
    return {"profile": resource["profile"], "profile_sha256": hashlib.sha256(Path(resource["profile"]).read_bytes()).hexdigest(),
            "layout_sha256": hashlib.sha256((ASSETS / "brand.css").read_bytes()).hexdigest()}


def render_pdf(template_name, ctx, out_path, strict):
    from jinja2 import Environment, FileSystemLoader
    from brand_runtime import apply_profile
    from pdf_runtime import render_and_check, safe_fields, validate_spec
    validate_spec(template_name, ctx)
    env = Environment(loader=FileSystemLoader(str(TPL)), autoescape=True)
    html = env.get_template(template_name).render(**safe_fields(ctx))
    html = html.replace('<link rel="stylesheet" href="brand.css">', '<style>' + (ASSETS / 'brand.css').read_text() + '</style>')
    html, resource = apply_profile(html, PROFILE)
    if out_path.exists() or out_path.with_suffix('.html').exists():
        die('Output already exists; choose a new attempt directory: ' + str(out_path))
    out_path.with_suffix('.html').write_text(html)
    pages = render_and_check(out_path.with_suffix('.html'), out_path, EXPECTED_PAGES[template_name])
    print(f"  wrote {out_path.name} ({pages}p)")
    return pages


# ---------- house-format parsing ----------
# Sources drift. Accept the known spellings, and warn on any bold label we do
# not recognise so a renamed heading surfaces instead of emptying a slot.
LABEL_ALIASES = {
    "what is it": "what_is_it",
    "what it is": "what_is_it",
    "who is it for": "who_for",
    "who it is for": "who_for",
    "who it's for": "who_for",
    "why should they care": "they_care",
    "why should you care": "you_care",
    "why should we care": "we_care",
    "what's included": "included",
    "whats included": "included",
    "what is included": "included",
    "what's not included": "not_included",
    "whats not included": "not_included",
    "what is not included": "not_included",
    "how do we deliver it": "deliver",
    "how we deliver it": "deliver",
    "how is it delivered": "deliver",
}

REQUIRED_INTERNAL = ["what_is_it", "who_for", "they_care", "we_care", "included", "not_included", "deliver"]
REQUIRED_EXTERNAL = ["what_is_it", "included", "deliver"]


def _blocks(text, where, strict=True):
    out, cur, buf = {}, None, []
    for line in text.splitlines():
        m = re.match(r"^\*\*(.+?)\*\*\s*:?\s*$", line.strip())
        if m:
            if cur is not None:
                out[cur] = "\n".join(buf).strip()
            raw = m.group(1).strip().lower().rstrip("?:")
            key = LABEL_ALIASES.get(raw)
            if key is None:
                (die if strict else warn)(f"{where}: unrecognised label \"{m.group(1).strip()}\" was ignored. "
                     "Its content will not appear in the PDF.")
                key = "__ignored__" + raw
            cur, buf = key, []
        elif cur is not None:
            buf.append(line)
    if cur is not None:
        out[cur] = "\n".join(buf).strip()
    return out


def _bullets(s):
    return [re.sub(r"^[-*]\s+", "", ln).strip() for ln in s.splitlines()
            if ln.strip().startswith(("- ", "* "))]


def _prose(s):
    keep = [ln for ln in s.splitlines() if not ln.strip().startswith(("- ", "* "))]
    return " ".join(" ".join(keep).split())


def _list_or_prose(s):
    b = _bullets(s)
    return (b, None) if b else (None, _prose(s))


def _require(fields, needed, where, strict):
    gaps = [k for k in needed if not (fields.get(k) or "").strip()]
    if gaps:
        human = {v: k for k, v in LABEL_ALIASES.items()}
        msg = (f"{where} is missing required content: "
               + ", ".join(f'"{human.get(g, g)}"' for g in gaps)
               + ". The PDF would render those panels empty.")
        if strict:
            die(msg, code=5)
        warn(msg)


def parse_entry(entry_md, strict):
    head = re.match(r"^##\s+(.+)$", entry_md.splitlines()[0]).group(1)
    # Tolerate any separator between the number and the name: 01 · X, 01 - X,
    # 01 – X, 01: X, 01. X, or plain "01 X".
    name = re.sub(r"^\s*[A-Za-z]{0,3}[-]?\d+[A-Za-z]?\s*(?:[·–—:.)\-]\s*)?", "", head).strip()
    if not name:
        name = head.strip()
    tier = "free" if re.search(r"\(\s*free\s*\)", head, re.I) else "paid"
    name = re.sub(r"\s*\(\s*(free|paid)\s*\)\s*$", "", name, flags=re.I).strip()

    def section(title):
        m = re.search(r"^###\s+" + re.escape(title) + r"\s*$(.*?)(?=^###\s|\Z)",
                      entry_md, re.M | re.S)
        return m.group(1).strip() if m else ""

    tldr = re.sub(r"\s+", " ", section("Tldr")).strip()
    infields = _blocks(section("Internal one-pager"), f"[{name}] internal one-pager", strict)
    exfields = _blocks(section("External one-pager"), f"[{name}] external one-pager", strict)
    if not infields and not exfields:
        die(f"[{name}] has neither an \"### Internal one-pager\" nor an "
            "\"### External one-pager\" section. Nothing to render.", code=5)
    _require(infields, REQUIRED_INTERNAL, f"[{name}] internal one-pager", strict)
    _require(exfields, REQUIRED_EXTERNAL, f"[{name}] external one-pager", strict)

    ni_raw = infields.get("not_included", "")
    inc_list, s5 = _list_or_prose(infields.get("included", ""))
    internal = {
        "title": name, "descriptor": tldr,
        "s1": _prose(infields.get("what_is_it", "")),
        "s2": _prose(infields.get("who_for", "")),
        "s3": _prose(infields.get("they_care", "")),
        "s4": _prose(infields.get("we_care", "")),
        "included_list": inc_list, "s5": s5,
        "not_included": _bullets(ni_raw),
        "boundary": _prose(ni_raw),
        "s7": _prose(infields.get("deliver", "")),
        "footer_line": ('The free front door to our <span class="hl">practice</span>.'
                        if tier == "free" else
                        'Offering details for the sales team.'),
    }

    # The subtitle is the opening sentence of "why should you care". Print the
    # remainder in the column so the same sentence does not appear twice on one page.
    ex_care = _prose(exfields.get("you_care", ""))
    parts = re.split(r"(?<=[.!?])\s+", ex_care, 1) if ex_care else [""]
    subtitle = parts[0]
    care_rest = parts[1].strip() if len(parts) > 1 and parts[1].strip() else ex_care

    if tier == "free":
        foot_line = 'What it costs: nothing. <span class="hl">It is how we start.</span>'
        foot_note = "Contact the offering owner to begin."
    else:
        foot_line = 'Ready when you are. <span class="hl">Let\'s scope it.</span>'
        foot_note = "Contact the offering owner to discuss scope."

    external = {
        "eyebrow": name.upper(), "title": name, "subtitle": subtitle,
        "intro": _prose(exfields.get("what_is_it", "")),
        "what_you_get": _bullets(exfields.get("included", "")) or [_prose(exfields.get("included", ""))],
        "columns": [
            {"k": "Who it's for", "v": _prose(exfields.get("who_for", ""))},
            {"k": "Why it matters", "v": care_rest},
        ],
        "columns_heading": "Who it's for and why it matters",
        "how": _prose(exfields.get("deliver", "")),
        "footer_line": foot_line, "footer_note": foot_note,
    }
    return internal, external


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def render_spec(spec, outdir, base, strict):
    made = {}
    if spec.get("internal"):
        p = outdir / f"{base}-internal-brief.pdf"
        made[p.name] = render_pdf("internal_brief.html", spec["internal"], p, strict)
    if spec.get("external"):
        p = outdir / f"{base}-external-onepager.pdf"
        made[p.name] = render_pdf("external_onepager.html", spec["external"], p, strict)
    return made


def write_manifest(outdir, source, fingerprint, artifacts):
    """Provenance for a batch: which source, which asset bytes, when, how many
    pages each. Without this a folder of PDFs cannot be traced back to a revision."""
    m = {
        "generated": datetime.datetime.now(datetime.timezone.utc)
                     .replace(microsecond=0).isoformat(),
        "source": str(source),
        "source_sha256": hashlib.sha256(Path(source).read_bytes()).hexdigest() if Path(source).is_file() else None,
        "brand_assets": fingerprint,
        "artifacts": [{"file": k, "pages": v, "sha256": hashlib.sha256((outdir / k).read_bytes()).hexdigest()} for k, v in sorted(artifacts.items())],
        "warnings": WARNINGS,
    }
    (outdir / "render-manifest.json").write_text(json.dumps(m, indent=2) + "\n")
    print(f"  wrote render-manifest.json ({len(artifacts)} artifacts, {len(WARNINGS)} warnings)")


PROFILE = None

def main():
    global PROFILE
    ap = argparse.ArgumentParser()
    ap.add_argument("--md"); ap.add_argument("--entry"); ap.add_argument("--all", action="store_true")
    ap.add_argument("--json"); ap.add_argument("--out", default="."); ap.add_argument("--prefix", default="")
    ap.add_argument("--profile", help="Confirmed brand Markdown; otherwise project brand.md or the neutral estate profile")
    ap.add_argument("--no-strict", dest="strict", action="store_false", default=True,
                    help="downgrade blocking errors to warnings")
    a = ap.parse_args()
    if a.prefix and not re.fullmatch(r"[A-Za-z0-9_-]+", a.prefix):
        ap.error("--prefix accepts letters, digits, hyphens and underscores only")
    outdir = Path(a.out); outdir.mkdir(parents=True, exist_ok=True)
    if any(outdir.iterdir()):
        ap.error("Output directory must be empty; keep previous attempts in their own directory")
    PROFILE = a.profile
    fingerprint = preflight(PROFILE)

    if a.json:
        spec = json.loads(Path(a.json).read_text())
        if not spec.get("internal") and not spec.get("external"):
            die("spec has neither an \"internal\" nor an \"external\" object.", code=5)
        title = (spec.get("internal") or spec.get("external")).get("title", "playbook")
        made = render_spec(spec, outdir, a.prefix + slug(title), a.strict)
        write_manifest(outdir, a.json, fingerprint, made)
        return

    if not a.md:
        ap.error("provide --json or --md")
    if not a.entry and not a.all:
        ap.error("provide --entry NN or --all")
    text = Path(a.md).read_text(encoding="utf-8")
    entries = [e for e in re.split(r"(?=^##\s+\S*\d)", text, flags=re.M)
               if re.match(r"^##\s+\S*\d", e)]
    if not entries:
        die(f"no house-format entries found in {a.md}. Entries must start with "
            "a level-two heading whose first token carries the number, e.g. "
            "\"## 01 · Signal Review (free)\".", code=5)

    made = {}
    matched = 0
    for e in entries:
        head = re.match(r"^##\s+(.+)$", e.splitlines()[0]).group(1)
        num = head.split()[0].strip(".:-·")
        if a.entry and num != a.entry.strip():
            continue
        matched += 1
        internal, external = parse_entry(e, a.strict)
        print(f"[{num}] {internal['title']}")
        made.update(render_spec({"internal": internal, "external": external},
                                outdir, a.prefix + f"{num}-" + slug(internal["title"]), a.strict))
    if a.entry and matched == 0:
        avail = ", ".join(sorted({re.match(r"^##\s+(\S+)", e).group(1).strip(".:-·")
                                  for e in entries}))
        die(f"entry \"{a.entry}\" not found in {a.md}. Available: {avail}", code=5)
    write_manifest(outdir, a.md, fingerprint, made)
    if WARNINGS:
        print(f"\n{len(WARNINGS)} warning(s). Review before shipping.", file=sys.stderr)


if __name__ == "__main__":
    main()
