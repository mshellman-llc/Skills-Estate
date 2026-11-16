#!/usr/bin/env python3
"""Self-test for brand_check.py.

Every rule is exercised in both directions: a violating fixture that must fail
with the expected code, and a conforming fixture that must pass. A linter that
only proves it can fail is a linter nobody can trust to be quiet.

Exit 0 when every case matches.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

SCRIPT = Path(__file__).with_name("brand_check.py")

# (name, filename, content, expect_exit, expect_code | None)
CASES = [
    # ---- palette -----------------------------------------------------------
    ("off_palette", "a.css", ".x{color:#123456}", 1, "OFF_PALETTE"),
    ("off_brand_navy", "b.css", ".x{color:#1f2a44}", 1, "OFF_PALETTE"),
    ("neutral_text_allowed", "c.css", ".x{color:#111111}", 0, None),
    # a warm hex that is not on the blocked list, so this proves the warm rule
    ("warm_accent", "d.css", ".x{background:#C2410C}", 1, "OFF_PALETTE"),
    ("blocked_warm_reports_blocked_first", "d2.css", ".x{background:#B23A48}", 1,
     "OFF_PALETTE"),
    ("warm_amber_box", "e.css", ".alert{background:#FBF6E7}", 1, "OFF_PALETTE"),
    ("canonical_palette_ok", "f.css",
     ".x{color:#111111;background:#F5F5F5;border:1px solid #DDDDDD}", 0, None),
    ("sand_is_warm_but_allowed", "g.css",
     ".x{background:#F5F5F5;border:1px solid #DDDDDD}", 0, None),
    ("bare_hex_in_js", "h.js", 'const NAVY="123456";', 1, "OFF_PALETTE"),
    ("bare_canonical_in_js", "i.js", 'const NAVY="111111";', 0, None),

    # ---- borders and radii -------------------------------------------------
    ("border_width", "j.css", ".x{border:2px solid #DDDDDD}", 1, "BORDER_WIDTH"),
    ("profile_text_border", "k.css", ".x{border:1px solid #111111}", 0, None),
    # colors_and_type.css caps radii at 8px for cards, buttons, tags, and inputs
    # alike, with 4px as --radius-sm. An earlier 8-to-12px card band was wrong.
    ("radius_small_ok", "l.css", ".card{border-radius:4px}", 0, None),
    ("radius_over_cap", "m.css", ".card{border-radius:20px}", 1, "RADIUS"),
    ("radius_12_over_cap", "n.css", ".card{border-radius:12px}", 1, "RADIUS"),
    ("radius_default_ok", "p.css", ".btn{border-radius:4px}", 0, None),
    ("radius_off_scale_review", "p2.css", ".card{border-radius:2px}", 0, None),
    ("pill_on_dot_ok", "q.css", ".status-dot{border-radius:999px}", 0, None),
    ("pill_stray", "r.css", ".panel{border-radius:999px}", 1, "RADIUS"),

    # ---- layout ------------------------------------------------------------
    ("title_underline", "s.html",
     "<style>h2{border-bottom:1px solid #DDDDDD}</style><h2>Scope of work</h2>",
     1, "TITLE_UNDERLINE"),
    ("centered_body", "t.html",
     "<style>p{text-align:center}</style><p>Body copy here.</p>", 1,
     "CENTERED_BODY"),
    ("left_body_ok", "u.html",
     "<style>p{text-align:left}</style><p>Body copy here.</p>", 0, None),
    # four brand tokens as literals on one HTML surface: legal. BRAND.md caps
    # nothing at a count; the palette rule is that every hex is a token.
    ("html_four_brand_ok", "z1.html",
     "<style>.a{color:#111111}.b{color:#111111}.c{color:#FFFFFF}"
     ".d{background:#F5F5F5}</style><p>x</p>", 0, None),
    # the same palette reached through var(): equally legal, and no advisory
    # flag is emitted about an uncountable budget, because there is no budget
    ("html_var_palette_ok", "z2.html",
     "<style>:root{--navy:#111111;--teal:#111111;--tl:#FFFFFF;--sand:#F5F5F5}"
     ".a{color:var(--navy)}.b{color:var(--teal)}</style><p>x</p>", 0, None),
    # Shadows are allowed but restrained: the CSS ships four shadow tokens
    # described as "max 4px offset per brand". Only oversized offsets fail.
    ("shadow_restrained_ok", "y1.css",
     ".card{box-shadow:0 2px 18px rgba(0,0,0,.06)}", 1, "SHADOW_OFFSET"),
    ("shadow_offset_too_big", "y1b.css",
     ".card{box-shadow:0 12px 18px rgba(8,15,40,.06)}", 1, "SHADOW_OFFSET"),
    ("shadow_none_ok", "y2.css", ".card{box-shadow:none}", 0, None),
    ("inset_ring_ok", "y3.css", ".card{box-shadow:inset 0 0 0 1px #DDDDDD}", 0, None),

    # ---- review tier (passes non-strict) -----------------------------------
    ("title_case_heading_review", "v.html", "<h1>Scope Of Work And Timeline</h1>",
     0, None),
    ("sentence_case_ok", "w.html", "<h1>Scope of work and timeline</h1>", 0, None),
    ("label_tracking_review", "x.html",
     "<style>.eyebrow{text-transform:uppercase}</style><p>x</p>", 0, None),
]

# Review-tier cases asserted to produce the flag, and to block under --strict.
REVIEW_CASES = [
    ("title_case_heading_review", "TITLE_CASE_HEADING"),
    ("label_tracking_review", "LABEL_TRACKING"),
    ("radius_off_scale_review", "RADIUS_OFF_SCALE"),
]


def run(paths, strict=False):
    cmd = [sys.executable, str(SCRIPT)] + [str(p) for p in paths]
    if strict:
        cmd.append("--strict")
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def report_for(path):
    with tempfile.NamedTemporaryFile("r", suffix=".json", delete=False) as tf:
        out = Path(tf.name)
    cmd = [sys.executable, str(SCRIPT), str(path), "--json", str(out)]
    subprocess.run(cmd, capture_output=True, text=True, check=False)
    return json.loads(out.read_text())


def codes(path):
    r = report_for(path)
    a = r["artifacts"][0]
    return ([i["code"] for i in a["failures"]],
            [i["code"] for i in a["reviewFlags"]])


def make_pptx(path: Path, slides: list[str]) -> None:
    """Minimal PPTX skeleton: only the slide XML matters to the linter."""
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("[Content_Types].xml", "<Types/>")
        for i, xml in enumerate(slides, 1):
            z.writestr(f"ppt/slides/slide{i}.xml", xml)


GOOD_SLIDE = (
    '<p:sld><p:cSld><p:spTree>'
    '<p:pic><p:nvPicPr><p:cNvPr id="2" name="footer-logo-lockup"/></p:nvPicPr>'
    '<p:spPr><a:xfrm><a:off x="400000" y="6500000"/></a:xfrm></p:spPr></p:pic>'
    '<p:sp><p:nvSpPr><p:cNvPr id="3" name="footer-slidenum"/></p:nvSpPr>'
    '<p:spPr><a:xfrm><a:off x="8500000" y="6500000"/></a:xfrm></p:spPr>'
    '<p:txBody><a:p><a:fld type="slidenum"><a:t>1</a:t></a:fld></a:p></p:txBody>'
    '</p:sp>'
    '<p:sp><p:txBody><a:p><a:t>Quoting speed is capped by response time.</a:t>'
    '</a:p></p:txBody></p:sp>'
    '</p:spTree></p:cSld></p:sld>'
)
NO_FOOTER_SLIDE = (
    '<p:sld><p:cSld><p:spTree><p:sp><p:txBody><a:p><a:t>Scope</a:t></a:p>'
    '</p:txBody></p:sp></p:spTree></p:cSld></p:sld>'
)
SWAPPED_FOOTER_SLIDE = GOOD_SLIDE.replace('x="400000"', 'x="9000000"')
MARK_AND_LOCKUP_SLIDE = GOOD_SLIDE.replace(
    'name="footer-slidenum"', 'name="logo-symbol"', 1).replace(
    '<a:fld type="slidenum"><a:t>1</a:t></a:fld>',
    '<a:fld type="slidenum"><a:t>1</a:t></a:fld>')
# navy + teal + tealLight + sand = four brand groups on one slide. Legal:
# BRAND.md states no per-surface count, only palette fidelity. Neutrals too.
FOUR_BRAND_SLIDE = GOOD_SLIDE.replace(
    '<a:t>Quoting speed is capped by response time.</a:t>',
    '<a:srgbClr val="111111"/><a:srgbClr val="111111"/>'
    '<a:srgbClr val="FFFFFF"/><a:srgbClr val="F5F5F5"/>'
    '<a:srgbClr val="F5F5F5"/><a:srgbClr val="111111"/>'
    '<a:t>Four brand colors on one slide.</a:t>')
# navy + teal + sand plus every neutral: on-palette throughout, must pass.
THREE_BRAND_SLIDE = GOOD_SLIDE.replace(
    '<a:t>Quoting speed is capped by response time.</a:t>',
    '<a:srgbClr val="111111"/><a:srgbClr val="111111"/>'
    '<a:srgbClr val="F5F5F5"/><a:srgbClr val="DDDDDD"/>'
    '<a:srgbClr val="F5F5F5"/><a:srgbClr val="111111"/>'
    '<a:srgbClr val="DDDDDD"/><a:srgbClr val="FFFFFF"/>'
    '<a:t>Three brand colors and every neutral.</a:t>')


def main() -> int:
    observed, expected, wrong_reason = {}, {}, []
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)

        for name, fname, content, want, want_code in CASES:
            p = root / fname
            p.write_text(content, encoding="utf-8")
            observed[name] = run([p]).returncode
            expected[name] = want
            if want_code:
                fails, _ = codes(p)
                if want_code not in fails:
                    wrong_reason.append((name, want_code, fails))

        for name, want_code in REVIEW_CASES:
            fname = next(f for n, f, *_ in CASES if n == name)
            p = root / fname
            _, revs = codes(p)
            if want_code not in revs:
                wrong_reason.append((name + ":review", want_code, revs))
            observed[name + "_strict"] = run([p], strict=True).returncode
            expected[name + "_strict"] = 1

        # ---- known off-brand colors remain blocked ------------------------
        rp = root / "legacy.css"
        rp.write_text(".x{color:#1f2a44}", encoding="utf-8")
        observed["off_brand_blocked_by_default"] = run([rp]).returncode
        expected["off_brand_blocked_by_default"] = 1
        rp2 = root / "legacy2.css"
        rp2.write_text(".x{color:#111111}", encoding="utf-8")
        observed["second_off_brand_color_blocked"] = run([rp2]).returncode
        expected["second_off_brand_color_blocked"] = 0

        # ---- lint-context exemptions ---------------------------------------
        # a hex named in a `replacedBy` record is not a brand decision
        rec = root / "record.md"
        rec.write_text("#1f2a44 replacedBy #111111.",
                       encoding="utf-8")
        observed["replacement_record_not_flagged"] = run([rec]).returncode
        expected["replacement_record_not_flagged"] = 0

        # ---- decks ---------------------------------------------------------
        good = root / "good.pptx"
        make_pptx(good, [GOOD_SLIDE])
        observed["deck_ok"] = run([good]).returncode
        expected["deck_ok"] = 0

        # Footer placement is composition, not identity. A cover or full-bleed
        # slide legitimately carries no footer, so the gate raises it for a
        # reader instead of failing the deck. It still has to raise it: silence
        # here would drop the check rather than move it.
        nofoot = root / "nofoot.pptx"
        make_pptx(nofoot, [NO_FOOTER_SLIDE])
        observed["deck_missing_footer"] = run([nofoot]).returncode
        expected["deck_missing_footer"] = 0
        observed["deck_missing_footer_strict"] = run([nofoot], strict=True).returncode
        expected["deck_missing_footer_strict"] = 0
        _, r = codes(nofoot)
        if "MISSING_FOOTER" in r:
            wrong_reason.append(("deck_missing_footer", "MISSING_FOOTER review", r))

        swapped = root / "swapped.pptx"
        make_pptx(swapped, [SWAPPED_FOOTER_SLIDE])
        observed["deck_footer_layout"] = run([swapped]).returncode
        expected["deck_footer_layout"] = 0
        observed["deck_footer_layout_strict"] = run([swapped], strict=True).returncode
        expected["deck_footer_layout_strict"] = 0
        _, r = codes(swapped)
        if "FOOTER_LAYOUT" in r:
            wrong_reason.append(("deck_footer_layout", "FOOTER_LAYOUT review", r))

        marked = root / "marked.pptx"
        make_pptx(marked, [MARK_AND_LOCKUP_SLIDE])
        f, _ = codes(marked)
        observed["deck_mark_and_lockup"] = 1 if "MARK_AND_LOCKUP" in f else 0
        expected["deck_mark_and_lockup"] = 1

        four = root / "four.pptx"
        make_pptx(four, [FOUR_BRAND_SLIDE])
        f, _ = codes(four)
        # Regression for the removed invented rule: four on-palette brand
        # colours on one slide must not fail on a count.
        observed["deck_four_brand_ok"] = 1 if "TOO_MANY_BRAND" in f else 0
        expected["deck_four_brand_ok"] = 0

        # exactly at the cap, with every neutral present, must pass: proves
        # neutrals are free and the cap is not off by one
        three = root / "three.pptx"
        make_pptx(three, [THREE_BRAND_SLIDE])
        observed["deck_three_brand_ok"] = run([three]).returncode
        expected["deck_three_brand_ok"] = 0

        # ---- release guard -------------------------------------------------
        # --require-authoritative must refuse while tokens.json is a
        # transcription, and must not affect the ordinary path.
        clean_css = root / "f.css"
        tokens_mode = "authoritative"  # read directly from a confirmed Markdown policy
        r = subprocess.run(
            [sys.executable, str(SCRIPT), str(clean_css),
             "--require-authoritative"],
            capture_output=True, text=True, check=False)
        observed["require_authoritative"] = r.returncode
        expected["require_authoritative"] = 0 if tokens_mode == "authoritative" else 2

        # ---- bad input -----------------------------------------------------
        observed["missing_file"] = run([root / "nope.css"]).returncode
        expected["missing_file"] = 2

    mismatches = {k: (observed[k], expected[k]) for k in expected
                  if observed.get(k) != expected[k]}
    print(json.dumps({"observed": observed, "expected": expected}, indent=2))
    if mismatches:
        print("\nEXIT-CODE MISMATCHES (observed, expected):")
        for k, v in mismatches.items():
            print(f"  {k}: {v}")
    if wrong_reason:
        print("\nFAILED FOR THE WRONG REASON:")
        for n, c, got in wrong_reason:
            print(f"  {n}: wanted {c}, fired {got}")
    total = len(expected)
    print(f"\n{total - len(mismatches)}/{total} exit codes correct, "
          f"{len(CASES) + len(REVIEW_CASES) + 4 - len(wrong_reason)} rule "
          "assertions fired as expected")
    return 1 if (mismatches or wrong_reason) else 0


if __name__ == "__main__":
    sys.exit(main())
