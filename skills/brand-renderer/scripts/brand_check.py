#!/usr/bin/env python3
"""brand_check.py - the visual-layer gate. What prose_check.py is to voice.

prose_check.py stops AI writing patterns shipping. This stops off-brand pixels
shipping. Same shape: tiers, hard failures, review flags, a JSON contract, and
no vocabulary or palette of its own - every color comes from brand/tokens.json,
the single machine-readable brand source.

Usage:
  python3 brand_check.py artifact.html [artifact.pptx ...] [--json out.json]
                                       [--strict]

Inputs: .html .htm .css .pptx .docx .js .py .md  (source files are linted too,
because a renderer that hardcodes a hex will emit it on every future artifact -
catching it in the source is the only fix that holds.)

FAILURES (exit 1). Each traces to BRAND.md via tokens.json `rules`:
  OFF_PALETTE        a hex with no token in the selected brand profile
  BLOCKED_PALETTE    a known off-brand hex with a canonical replacement
  WARM_ACCENT        warm or orange accent; Sand is the only warm surface
  BLACK_BORDER       a black or near-black border
  BORDER_WIDTH       a border that is not 1px
  RADIUS             card radius outside 8-12px, control above 8px, stray 999px
  MARK_AND_LOCKUP    the logo symbol and the full lockup on one surface
  TITLE_UNDERLINE    a decorative underline beneath a title
  CENTERED_BODY      a centered long paragraph

REVIEW (reported, blocks only under --strict):
  TITLE_CASE_HEADING heading that looks title-cased rather than sentence case
  LABEL_TRACKING     an uppercase label with no letter-spacing
  EYEBROW_CONTRAST   the known brand-versus-accessibility tradeoff
  MISSING_FOOTER     a slide with no footer
  FOOTER_LAYOUT      footer logo not left, or page number not right

Brand controls identity: palette, type, assets, hierarchy, accessibility, and
craft. Composition is content-driven, so where a footer sits, and whether a full
bleed cover carries one at all, is the artifact's decision to make and a
reviewer's to read. Footer placement moved from failure to review for that
reason. What identifies a surface, the mark versus the lockup, stays a failure:
that is identity, not layout.

Exit codes:
  0  no failures (review flags may remain)
  1  failures present, or any review flag under --strict
  2  invalid input, missing tokens.json, or runtime failure
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent / "brand"))
from tokens import T, TokensNotFound  # noqa: E402

HEX_RE = re.compile(r"#([0-9a-fA-F]{3})\b|#([0-9a-fA-F]{6})\b|#([0-9a-fA-F]{8})\b")

# A bare 6-hex in quotes is how docx/pptx colors are written in JS ("E0E4EA").
# It is ALSO how OOXML writes coordinates ( x="400000" ), shape ids, and sizes,
# so a bare hex only counts as a color when something on the line says colour.
# Without this guard an EMU offset like 400000 lints as a warm accent.
BARE_HEX_RE = re.compile(r"""["']#?([0-9a-fA-F]{6})["']""")
COLOR_CTX = re.compile(
    r"(?:colou?r|fill|shading|background|bg|stroke|border|accent|palette|hex|"
    r"srgbclr|themecolor|highlight)\s*[:=(]?\s*$"
    r"|[A-Z][A-Z0-9_]{1,15}\s*[:=]\s*$",     # a palette constant: NAVY=, CLAY=
    re.I,
)
# OOXML colors live in specific attributes. Anything else numeric is geometry.
XML_COLOR_RE = re.compile(
    r"<a:(?:srgbClr|sysClr)[^>]*?(?:val|lastClr)=\"([0-9a-fA-F]{6})\""
    r"|w:(?:color|fill|highlight)\s+w:val=\"([0-9a-fA-F]{6})\""
    r"|w:(?:fill|color)=\"([0-9a-fA-F]{6})\"",
    re.I,
)

# Contexts where a hex is not a brand decision and must not be linted.
IGNORE_LINE = re.compile(
    r"retired|replacedBy|do not use|legacy|allowlist|PINNED_TOKENS|"
    r"OFF_PALETTE|off-palette|was:|formerly|#\s*noqa: brand",
    re.I,
)

TEXT_EXT = {".html", ".htm", ".css", ".js", ".py", ".md", ".json", ".txt", ".svg"}


def normalise(h: str) -> str:
    h = h.lower()
    if not h.startswith("#"):
        h = "#" + h
    if len(h) == 4:
        return "#" + "".join(c * 2 for c in h[1:])
    if len(h) == 9:
        return h[:7]
    return h


def hexes_in(line: str, xml: bool = False) -> list[str]:
    """Colors on one line. A '#' prefix is unambiguous; a bare 6-hex needs a
    colour context so OOXML geometry is not linted as a palette."""
    out = []
    for m in HEX_RE.finditer(line):
        out.append(normalise(next(g for g in m.groups() if g)))
    if xml:
        for m in XML_COLOR_RE.finditer(line):
            out.append(normalise(next(g for g in m.groups() if g)))
        return out
    for m in BARE_HEX_RE.finditer(line):
        if COLOR_CTX.search(line[max(0, m.start() - 40):m.start()]):
            out.append(normalise(m.group(1)))
    return out


# --- extraction -------------------------------------------------------------
def pptx_slides(path: Path) -> list[dict[str, Any]]:
    """One record per slide: its XML, its text, and its shape geometry."""
    slides = []
    with zipfile.ZipFile(path) as z:
        names = sorted(
            (n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)),
            key=lambda n: int(re.search(r"(\d+)", n).group(1)),
        )
        for i, n in enumerate(names, 1):
            xml = z.read(n).decode("utf-8", "ignore")
            text = " ".join(re.findall(r"<a:t>([^<]*)</a:t>", xml))
            pics = re.findall(r"<p:pic>.*?</p:pic>", xml, re.S)
            slides.append({"n": i, "xml": xml, "text": text, "pics": pics,
                           "name": f"slide{i}"})
    return slides


PAGE_OPEN = re.compile(r"<(?:div|section|article)\b[^>]*\bclass=\"[^\"]*\bpage\b",
                       re.I)


def split_pages(html: str) -> list[str]:
    """Split a paginated HTML document into its page surfaces.

    Returns [html] when the document has no page containers, so the caller can
    fall back to treating the file as one surface.
    """
    starts = [m.start() for m in PAGE_OPEN.finditer(html)]
    if len(starts) < 2:
        return [html]
    bounds = starts + [len(html)]
    return [html[bounds[i]:bounds[i + 1]] for i in range(len(starts))]


def docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as z:
        parts = [n for n in z.namelist()
                 if re.match(r"word/(document|header\d*|footer\d*)\.xml$", n)]
        return " ".join(z.read(p).decode("utf-8", "ignore") for p in parts)


# --- checks -----------------------------------------------------------------
class Findings:
    def __init__(self) -> None:
        self.fail: list[dict[str, Any]] = []
        self.review: list[dict[str, Any]] = []

    def add(self, bucket: str, code: str, where: str, detail: str) -> None:
        getattr(self, bucket).append({"code": code, "where": where, "detail": detail})


def check_hexes(text: str, label: str, f: Findings,
                per_surface: bool = False, xml: bool = False) -> None:
    """Palette conformance. The core check: a hex with no token is a defect.

    `per_surface` is accepted for caller compatibility and ignored. The old
    per-surface colour budget enforced a cap BRAND.md never stated; the brand
    rule is palette fidelity (every hex is a token), not a count.
    """
    for lineno, line in enumerate(text.splitlines(), 1):
        if IGNORE_LINE.search(line):
            continue
        for h in hexes_in(line, xml=xml):
            where = f"{label}:{lineno}"
            blocked = T.blocked_hexes.get(h)
            if blocked:
                repl = blocked["replacedBy"] or "a canonical token"
                f.add("fail", "BLOCKED_PALETTE", where,
                      f"{h} is off-brand. Use {repl}.")
                continue
            if h not in T.allowed_hexes:
                if T.is_warm(h):
                    f.add("fail", "WARM_ACCENT", where,
                          f"{h} is disallowed by the selected profile warm-accent policy.")
                else:
                    f.add("fail", "OFF_PALETTE", where,
                          f"{h} has no token in the selected brand profile.")
                continue


def check_css_geometry(text: str, label: str, f: Findings) -> None:
    """Borders and radii, from CSS or inline style."""
    for lineno, line in enumerate(text.splitlines(), 1):
        if IGNORE_LINE.search(line):
            continue
        where = f"{label}:{lineno}"
        # border-radius is a separate rule; do not read it as a border width.
        for m in re.finditer(
                r"border(?!-radius)(?:-(?:top|right|bottom|left|color|style|"
                r"width|block|inline)(?:-\w+)?)?\s*:\s*([^;}\n]+)", line, re.I):
            decl = m.group(1)
            if re.search(r"\bnone\b|\b0\b", decl) and "px" not in decl:
                continue
            wm = re.search(r"(\d+(?:\.\d+)?)px", decl)
            if wm and float(wm.group(1)) != T.rules["borderWidthPx"]:
                f.add("fail", "BORDER_WIDTH", where,
                      f"border {wm.group(1)}px; borders are always "
                      f"{T.rules['borderWidthPx']}px.")
            for h in hexes_in(decl):
                r, g, b = T.rgb(h)
                if T.rules.get("borderNeverBlack", False) and max(r, g, b) <= 32:
                    f.add("fail", "BLACK_BORDER", where,
                          f"border {h} is black or near-black; borders are never black.")
            if T.rules.get("borderNeverBlack", False) and re.search(r"\bblack\b", decl, re.I):
                f.add("fail", "BLACK_BORDER", where,
                      "border color 'black'; borders are never black.")
        # Shadows are allowed but restrained: the selected brand profile ships four
        # shadow tokens described as "max 4px offset per brand". Only an
        # oversized offset is a defect.
        shadow = T.rules.get("shadow", {})
        max_off = shadow.get("maxOffsetPx", 4)
        for m in re.finditer(r"box-shadow\s*:\s*([^;}\n]+)", line, re.I):
            decl = m.group(1).strip()
            if re.fullmatch(r"none", decl, re.I) or "inset" in decl.lower():
                continue
            # Offsets are the first two lengths of each shadow; blur and spread
            # are not offsets and the brand does not cap them. Strip colour
            # functions before splitting, or rgba(8, 15, 40, .06) splits into
            # fragments and its blur gets read as an offset. A bare `0` is a
            # length too, so it must be matched with or without the px unit.
            stripped = re.sub(r"\b(?:rgba?|hsla?|color)\([^)]*\)", " ", decl,
                              flags=re.I)
            for part in stripped.split(","):
                lens = [float(m.group(1)) for m in
                        re.finditer(r"(-?\d*\.?\d+)(?:px)?(?=\s|$)", part.strip())]
                if any(abs(v) > max_off for v in lens[:2]):
                    f.add("fail", "SHADOW_OFFSET", where,
                          f"box-shadow '{decl[:44]}' offsets past {max_off}px; "
                          "the brand's shadows are restrained. Use one of the "
                          "--shadow tokens.")
                    break

        rad = T.rules["radius"]
        allowed = set(rad.get("allowedPx", [4, 8]))
        pill = rad.get("pillPx", 999)
        cap = rad.get("capPx", 8)
        for m in re.finditer(r"border-radius\s*:\s*([^;}\n]+)", line, re.I):
            decl = m.group(1)
            for vm in re.finditer(r"(\d+(?:\.\d+)?)px", decl):
                v = float(vm.group(1))
                if v == pill or v == 0:
                    continue
                if v > cap:
                    f.add("fail", "RADIUS", where,
                          f"{v:g}px radius; the brand caps radii at {cap}px for "
                          "cards, buttons, tags, and inputs alike.")
                elif v not in allowed:
                    f.add("review", "RADIUS_OFF_SCALE", where,
                          f"{v:g}px radius is under the {cap}px cap but off the "
                          f"scale ({', '.join(f'{a}px' for a in sorted(allowed))}).")
            if str(pill) in decl and not re.search(
                    r"avatar|dot|puck|status|badge", line, re.I):
                f.add("fail", "RADIUS", where,
                      f"{pill}px full round is for {rad['pillUsage']}.")


def check_html_layout(text: str, label: str, f: Findings) -> None:
    """Title underline and centered body copy."""
    for lineno, line in enumerate(text.splitlines(), 1):
        if IGNORE_LINE.search(line):
            continue
        where = f"{label}:{lineno}"
        if re.search(r"<h[1-3][^>]*style=\"[^\"]*border-bottom", line, re.I) or \
           re.search(r"\bh[1-3]\b[^{]*\{[^}]*border-bottom", line, re.I):
            f.add("fail", "TITLE_UNDERLINE", where,
                  "decorative underline beneath a title; hierarchy comes from "
                  "type and space.")
        if re.search(r"text-align\s*:\s*center", line, re.I) and \
           re.search(r"\bp\b|body|paragraph|\.copy|\.body", line, re.I):
            f.add("fail", "CENTERED_BODY", where,
                  "centered body copy; body copy is left-aligned.")
        for m in re.finditer(r"text-transform\s*:\s*uppercase", line, re.I):
            window = line[max(0, m.start() - 220):m.start() + 220]
            if "letter-spacing" not in window.lower():
                f.add("review", "LABEL_TRACKING", where,
                      f"uppercase label with no letter-spacing; labels track at "
                      f"+{T.rules['labelTrackingEm']}em.")
        if T.rules["eyebrow"]["brandContrastOnWhite"] < T.rules["eyebrow"]["wcagLargeTextMin"] and re.search(r"\.eyebrow\b", line) and T.rules["eyebrow"]["brandHex"].lower() \
                in [h for h in hexes_in(line)]:
            e = T.rules["eyebrow"]
            f.add("review", "EYEBROW_CONTRAST", where,
                  f"eyebrow at {e['brandHex']} is {e['brandContrastOnWhite']}:1 on "
                  f"white, below the {e['wcagLargeTextMin']}:1 WCAG floor. "
                  f"Default is {e['defaultHex']} ({e['defaultContrastOnWhite']}:1).")


SENTENCE_CASE_EXEMPT = {
    "salesforce", "revenue", "cloud", "d365",
    "sow", "ddoc", "rfq", "sku", "phase", "wcag", "ai", "crm", "erp", "roi",
    "q1", "q2", "q3", "q4", "january", "february", "march", "april", "may",
    "june", "july", "august", "september", "october", "november", "december",
}


def looks_title_case(s: str) -> bool:
    words = [w for w in re.findall(r"[A-Za-z][A-Za-z'-]*", s)]
    if len(words) < 3:
        return False
    caps = [w for w in words[1:]
            if w[0].isupper() and w.lower() not in SENTENCE_CASE_EXEMPT
            and not w.isupper()]
    return len(caps) >= max(2, (len(words) - 1) // 2)


def check_headings(headings: list[tuple[str, str]], f: Findings) -> None:
    for where, h in headings:
        if looks_title_case(h):
            f.add("review", "TITLE_CASE_HEADING", where,
                  f"\"{h[:70]}\" looks title-cased; headings are sentence case.")


def check_slide(slide: dict[str, Any], label: str, f: Findings) -> None:
    """Per-slide rules: palette budget, footer, mark-versus-lockup."""
    sl = f"{label}#{slide['n']}"
    check_hexes(slide["xml"], sl, f, per_surface=True, xml=True)

    xml, text = slide["xml"], slide["text"]
    has_pagenum = bool(re.search(r"<a:fld[^>]*type=\"slidenum\"", xml)) or \
        bool(re.search(r"\bslidenum\b", xml))
    names = " ".join(re.findall(r'name="([^"]*)"', xml)).lower()
    # The full lockup and the bare logo symbol are different assets. "wordmark" and
    # "logomark" are single combined assets and must not read as the logo symbol, so
    # the logo symbol pattern needs a word boundary before "mark".
    has_lockup = bool(re.search(
        r"lockup|wordmark|logo-full|full-logo|logo-on-(?:light|dark)", names))
    has_amark = bool(re.search(r"\blogo-symbol\b", names))
    has_logo = has_lockup or has_amark or bool(re.search(r"\blogo\b", names))
    footerish = bool(re.search(r"footer", names)) or (has_logo and has_pagenum)

    if T.rules["footer"].get("convention") and not footerish:
        missing = []
        if not has_logo:
            missing.append("logo")
        if not has_pagenum:
            missing.append("page number")
        f.add("review", "MISSING_FOOTER", sl,
              f"no footer ({' and '.join(missing) or 'nothing'} found). Confirm "
              "this is a cover, divider, or full-bleed slide where the house "
              "convention of logo left and page number right does not apply.")
    elif T.rules["footer"].get("convention"):
        # geometry: logo must sit left of the page number
        def x_of(pattern: str) -> int | None:
            for m in re.finditer(r"<p:(?:pic|sp)>.*?</p:(?:pic|sp)>", xml, re.S):
                blob = m.group(0)
                if re.search(pattern, blob, re.I):
                    off = re.search(r'<a:off x="(-?\d+)"', blob)
                    if off:
                        return int(off.group(1))
            return None
        lx, px = x_of(r"logo|lockup|wordmark"), x_of(r"slidenum")
        if lx is not None and px is not None and lx >= px:
            f.add("review", "FOOTER_LAYOUT", sl,
                  "footer logo is not left of the page number. Confirm the "
                  "arrangement is deliberate for this slide.")

    if has_lockup and has_amark:
        f.add("fail", "MARK_AND_LOCKUP", sl,
              "the logo symbol and the full lockup are on the same surface. One or "
              "the other identifies a surface.")

    # Centered body copy. Measure each centered paragraph's OWN text: a centered
    # digit in a step puck or a centered label is fine, a centered paragraph is
    # not. Measuring the whole slide's word count would flag the puck.
    for m in re.finditer(r"<a:p>(?:(?!</a:p>).)*</a:p>", xml, re.S):
        para = m.group(0)
        if not re.search(r'algn="ctr"', para):
            continue
        own = " ".join(re.findall(r"<a:t>([^<]*)</a:t>", para))
        if len(own.split()) > 12:
            f.add("fail", "CENTERED_BODY", sl,
                  f"centered paragraph of {len(own.split())} words "
                  f"(\"{own[:48]}...\"); body copy is left-aligned.")


# --- driver -----------------------------------------------------------------
def check_path(path: Path) -> Findings:
    f = Findings()
    ext = path.suffix.lower()
    label = path.name

    if ext == ".pptx":
        slides = pptx_slides(path)
        if not slides:
            f.add("fail", "EMPTY_DECK", label, "no slides found.")
        for s in slides:
            check_slide(s, label, f)
        return f

    if ext == ".docx":
        check_hexes(docx_text(path), label, f, xml=True)
        return f

    if ext in TEXT_EXT:
        text = path.read_text(encoding="utf-8", errors="replace")
        if ext in (".html", ".htm"):
            # Per-surface checks treat a page, not the whole file, as the
            # surface for a paginated document. Split on page containers when
            # the document has them; a stylesheet at the top of the file
            # applies to every page, so it is prepended to each.
            pages = split_pages(text)
            if len(pages) > 1:
                head = "\n".join(
                    m.group(0) for m in
                    re.finditer(r"<style[^>]*>.*?</style>", text, re.S | re.I))
                for i, page in enumerate(pages, 1):
                    check_hexes(head + "\n" + page, f"{label} page {i}", f,
                                per_surface=True)
            else:
                check_hexes(text, label, f, per_surface=True)
        else:
            check_hexes(text, label, f)
        check_css_geometry(text, label, f)
        if ext in (".html", ".htm", ".md"):
            check_html_layout(text, label, f)
            heads = []
            for lineno, line in enumerate(text.splitlines(), 1):
                for m in re.finditer(r"<h[1-3][^>]*>(.*?)</h[1-3]>", line, re.I | re.S):
                    heads.append((f"{label}:{lineno}",
                                  re.sub(r"<[^>]+>", "", m.group(1)).strip()))
                m = re.match(r"^\s{0,3}#{1,3}\s+(.*)$", line)
                if m:
                    heads.append((f"{label}:{lineno}", m.group(1).strip()))
            check_headings(heads, f)
        return f

    f.add("fail", "UNSUPPORTED", label, f"cannot lint {ext}")
    return f


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("artifacts", nargs="+", type=Path)
    ap.add_argument("--json", dest="json_path", type=Path)
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 when any review flag remains")
    ap.add_argument("--include-tests", action="store_true",
                    help="also lint *_selftest.py and *_fixtures.py, which hold "
                         "deliberately bad colours")
    ap.add_argument("--require-authoritative", action="store_true",
                    help="fail unless tokens.json has been verified against "
                         "the selected brand profile by sync_tokens.py. Use this in a "
                         "release pipeline: a transcribed token file enforces "
                         "transcribed values, confidently.")
    args = ap.parse_args()

    if args.require_authoritative and not T.is_authoritative:
        print(f"\n  BRAND CHECK   REFUSING TO PASS\n"
              f"  tokens.json is '{T.provenance.get('mode')}', not "
              f"'authoritative'. It has never been read against\n"
              f"  the selected brand profile, so every check below would enforce "
              f"transcribed values.\n  Run scripts/sync_tokens.py "
              f"--css <path> --write first.\n")
        return 2

    results, fails, reviews = [], 0, 0
    # A gate's own fixtures must contain off-palette values or they could not
    # test anything. Skipping them by name, and saying which were skipped: a
    # silent exclusion would read as "everything is clean" when it was not
    # everything.
    skipped = []
    try:
        for p in args.artifacts:
            if not p.exists():
                print(f"  missing: {p}")
                return 2
            if not args.include_tests and re.search(
                    r"(?:_selftest|_fixtures)\.py$", p.name):
                skipped.append(p.name)
                continue
            f = check_path(p)
            fails += len(f.fail)
            reviews += len(f.review)
            results.append({"artifact": str(p), "failures": f.fail,
                            "reviewFlags": f.review})
    except TokensNotFound as exc:
        print(f"  {exc}")
        return 2
    except (OSError, zipfile.BadZipFile, ValueError) as exc:
        print(f"  brand_check failed: {exc}")
        return 2

    report = {
        "gate": "brand",
        "tokens": {"path": str(T.path), "mode": T.provenance.get("mode"),
                   "guidelines": T.provenance.get("guidelines")},
        "artifacts": results,
        "summary": {"failureCount": fails, "reviewFlagCount": reviews,
                    "brandPass": fails == 0},
    }

    print(f"\n  BRAND CHECK   tokens: {T.provenance.get('mode')} "
          f"({T.provenance.get('guidelines')})")
    if skipped:
        print(f"  skipped {len(skipped)} gate fixture file(s), which hold "
              f"deliberately bad colours: {', '.join(sorted(skipped))}")
        print("  (pass --include-tests to lint them anyway)")
    if T.provenance.get("mode") != "authoritative":
        print("  note: tokens.json is not yet verified against "
              "the selected brand profile; run scripts/sync_tokens.py where the org "
              "skill is mounted.")
    for r in results:
        print(f"\n  {Path(r['artifact']).name}")
        if not r["failures"] and not r["reviewFlags"]:
            print("    clean")
        for item in r["failures"]:
            print(f"    FAIL  {item['code']:<18} {item['where']}  {item['detail']}")
        for item in r["reviewFlags"]:
            print(f"    warn  {item['code']:<18} {item['where']}  {item['detail']}")
    print(f"\n  {'FAIL' if fails else 'PASS'}: {fails} failure(s), "
          f"{reviews} review flag(s)\n")

    if args.json_path:
        args.json_path.write_text(json.dumps(report, indent=2) + "\n",
                                  encoding="utf-8")
    code = 1 if fails else 0
    if args.strict and reviews:
        code = 1
    return code


if __name__ == "__main__":
    sys.exit(main())
