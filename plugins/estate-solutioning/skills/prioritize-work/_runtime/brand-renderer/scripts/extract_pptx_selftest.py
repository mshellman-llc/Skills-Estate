#!/usr/bin/env python3
"""Selftest for extract_pptx.py: proves table cell text survives extraction.

Builds a synthetic 2-slide deck with a text box and a table, then asserts:
  1. The naive text-frame-only walk DROPS the table cell text (the old bug).
  2. extract_pptx.extract() KEEPS it (the fix).
  3. The emitted HTML contains both the paragraph text and the table cells.

It also covers the deck-extract landmark (issue 167): the HTML wraps the slides
in one <main>, so parity_audit.py accepts a deck extract that needs only a phrase
and an h1 instead of raising MAIN_LANDMARK_MISSING.

All content is synthetic. Exit 0 on pass, 1 on failure.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches

import extract_pptx

TABLE_MARKER = "Design co-signed"       # lives ONLY in a table cell
PARA_MARKER = "Batch reconciliation service"  # lives in a text box
HOURS_MARKER = "180"                    # a number that lives only in a table cell


def build_fixture(path: Path) -> None:
    prs = Presentation()
    blank = prs.slide_layouts[6]

    slide1 = prs.slides.add_slide(blank)
    box = slide1.shapes.add_textbox(Inches(1), Inches(1), Inches(6), Inches(1))
    box.text_frame.text = PARA_MARKER

    slide2 = prs.slides.add_slide(blank)
    table = slide2.shapes.add_table(2, 2, Inches(1), Inches(1), Inches(6), Inches(2)).table
    table.cell(0, 0).text = "Gate"
    table.cell(0, 1).text = "Hours"
    table.cell(1, 0).text = TABLE_MARKER
    table.cell(1, 1).text = HOURS_MARKER
    prs.save(str(path))


def naive_text(path: Path) -> str:
    """The old, table-blind approach: text frames only."""
    prs = Presentation(str(path))
    chunks = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                chunks.append(shape.text_frame.text)
    return " ".join(chunks)


def landmark_failures() -> list[str]:
    """Issue 167: one rounded box reading "Example step", extracted, then audited."""
    failures: list[str] = []
    audit = Path(__file__).with_name("parity_audit.py")
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        deck = root / "example.pptx"
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1), Inches(1), Inches(4), Inches(1))
        box.text_frame.text = "Example step"
        prs.save(str(deck))

        html = extract_pptx.to_html(extract_pptx.extract(deck), "Example deck")
        if html.count("<main>") != 1 or html.count("</main>") != 1:
            failures.append("extract HTML does not carry exactly one <main>")
        elif "<h1>" not in html:
            failures.append("h1 missing from extract HTML")
        if "<main>" in html and not (html.index("<main>") < html.index('class="slide"') < html.index("</main>")):
            failures.append("slides sit outside <main>")

        manifest = root / "manifest.json"
        manifest.write_text(json.dumps({
            "manifestVersion": "1.0",
            "requiredPhrases": ["Example step"],
            "requiredSelectors": ["h1"],
        }), encoding="utf-8")
        page = root / "example.extracted.html"
        cli = subprocess.run(
            [sys.executable, str(Path(__file__).with_name("extract_pptx.py")), str(deck), "--html", str(page)],
            capture_output=True, text=True, check=False)
        if cli.returncode != 0:
            failures.append(f"extract_pptx CLI exited {cli.returncode}: {cli.stderr.strip()}")
        else:
            result = subprocess.run([sys.executable, str(audit), str(manifest), str(page)],
                                    capture_output=True, text=True, check=False)
            if result.returncode != 0 or "MAIN_LANDMARK_MISSING" in result.stdout:
                failures.append(f"parity_audit rejected the deck extract (exit {result.returncode}): "
                                f"{result.stdout.strip()[:200]}")
    return failures


def main() -> int:
    fixture = Path("_selftest_deck.pptx")
    build_fixture(fixture)
    failures = []

    naive = naive_text(fixture)
    if TABLE_MARKER in naive or HOURS_MARKER in naive:
        failures.append("naive walk unexpectedly captured table text; fixture invalid")
    if PARA_MARKER not in naive:
        failures.append("naive walk missed the text-box paragraph; fixture invalid")

    slides = extract_pptx.extract(fixture)
    html = extract_pptx.to_html(slides, "selftest")
    for marker in (PARA_MARKER, TABLE_MARKER, HOURS_MARKER, "Gate"):
        if marker not in html:
            failures.append(f"extractor dropped {marker!r}")

    fixture.unlink(missing_ok=True)
    failures.extend(landmark_failures())

    if failures:
        for f in failures:
            print(f"FAIL: {f}")
        return 1
    print("PASS: table cells and paragraphs survive extraction; naive walk drops tables as expected; "
          "deck extract has a main landmark the parity audit accepts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
