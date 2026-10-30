#!/usr/bin/env python3
"""Selftest for extract_pptx.py: proves table cell text survives extraction.

Builds a synthetic 2-slide deck with a text box and a table, then asserts:
  1. The naive text-frame-only walk DROPS the table cell text (the old bug).
  2. extract_pptx.extract() KEEPS it (the fix).
  3. The emitted HTML contains both the paragraph text and the table cells.

All content is synthetic. Exit 0 on pass, 1 on failure.
"""
from __future__ import annotations

import sys
from pathlib import Path

from pptx import Presentation
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

    if failures:
        for f in failures:
            print(f"FAIL: {f}")
        return 1
    print("PASS: table cells and paragraphs survive extraction; naive walk drops tables as expected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
