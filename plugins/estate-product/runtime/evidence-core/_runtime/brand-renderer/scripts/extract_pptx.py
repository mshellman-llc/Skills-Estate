#!/usr/bin/env python3
"""Table-aware PPTX -> HTML text bridge for the artifact parity/prose gates.

Usage:
  python3 extract_pptx.py deck.pptx [--html out.html] [--json out.json] [--title TITLE]

Why this exists:
  The parity audit and prose check read the READABLE TEXT of a rendered
  artifact from HTML. A .pptx is not HTML, and the naive way to pull text from
  a deck (iterating shape.text_frame) silently DROPS every table: table cell
  text lives on graphic-frame shapes, not text-frame shapes. A deck whose
  numbers, scope rows, or staffing hours sit in tables would then pass a parity
  audit while the audited text never contained them. This bridge walks tables,
  grouped shapes, and text frames so the extracted text is complete, then emits
  a minimal semantic HTML document the two gates can consume unchanged.

  Run order for a deck:
    python3 extract_pptx.py deck.pptx --html deck.extracted.html
    python3 parity_audit.py manifest.json deck.extracted.html --strict
    python3 prose_check.py deck.extracted.html --manifest manifest.json

Exit codes:
  0  extraction succeeded
  2  invalid input, missing dependency, or parse/runtime failure

The HTML this emits is a text transcript of the deck for auditing. It is NOT a
rendered deck and never substitutes for visual inspection of the real slides.
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any

try:
    from pptx import Presentation
    from pptx.enum.shapes import MSO_SHAPE_TYPE
except ImportError:
    Presentation = None
    MSO_SHAPE_TYPE = None


def _fail(message: str) -> "NoReturn":  # type: ignore[name-defined]
    print(f"extract_pptx: {message}", file=sys.stderr)
    raise SystemExit(2)


def _paragraph_text(paragraph: Any) -> str:
    return "".join(run.text for run in paragraph.runs) or paragraph.text or ""


def _walk_shape(shape: Any, blocks: list[dict[str, Any]]) -> None:
    """Append readable-text blocks for one shape, recursing into groups/tables."""
    shape_type = getattr(shape, "shape_type", None)

    # Groups: recurse into members so nothing nested is lost.
    if MSO_SHAPE_TYPE is not None and shape_type == MSO_SHAPE_TYPE.GROUP:
        for member in shape.shapes:
            _walk_shape(member, blocks)
        return

    # Tables: the load-bearing fix. Emit a structured table block.
    if getattr(shape, "has_table", False):
        table = shape.table
        rows: list[list[str]] = []
        for row in table.rows:
            rows.append([cell.text.strip() for cell in row.cells])
        if rows:
            blocks.append({"kind": "table", "rows": rows})
        return

    # Text frames: paragraphs in order.
    if getattr(shape, "has_text_frame", False):
        paras = [
            _paragraph_text(p).strip()
            for p in shape.text_frame.paragraphs
            if _paragraph_text(p).strip()
        ]
        for para in paras:
            blocks.append({"kind": "p", "text": para})


def extract(path: Path) -> list[dict[str, Any]]:
    if Presentation is None:
        _fail("python-pptx is not installed (pip install python-pptx)")
    try:
        prs = Presentation(str(path))
    except Exception as exc:  # noqa: BLE001 - surface any pptx parse failure as exit 2
        _fail(f"could not open {path}: {exc}")

    slides: list[dict[str, Any]] = []
    for index, slide in enumerate(prs.slides, start=1):
        blocks: list[dict[str, Any]] = []
        for shape in slide.shapes:
            _walk_shape(shape, blocks)
        notes = ""
        if slide.has_notes_slide:
            notes = (slide.notes_slide.notes_text_frame.text or "").strip()
        slides.append({"slide": index, "blocks": blocks, "notes": notes})
    return slides


def to_html(slides: list[dict[str, Any]], title: str) -> str:
    out: list[str] = [
        "<!DOCTYPE html>",
        '<html lang="en"><head><meta charset="utf-8">',
        f"<title>{html.escape(title)}</title></head><body>",
        f"<h1>{html.escape(title)}</h1>",
    ]
    for slide in slides:
        out.append(f'<section class="slide" data-slide="{slide["slide"]}">')
        out.append(f'<h2>Slide {slide["slide"]}</h2>')
        for block in slide["blocks"]:
            if block["kind"] == "p":
                out.append(f"<p>{html.escape(block['text'])}</p>")
            elif block["kind"] == "table":
                out.append("<table>")
                for r_index, row in enumerate(block["rows"]):
                    cell_tag = "th" if r_index == 0 else "td"
                    out.append("<tr>")
                    for cell in row:
                        out.append(f"<{cell_tag}>{html.escape(cell)}</{cell_tag}>")
                    out.append("</tr>")
                out.append("</table>")
        if slide["notes"]:
            out.append(f'<aside class="notes">{html.escape(slide["notes"])}</aside>')
        out.append("</section>")
    out.append("</body></html>")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Table-aware PPTX -> HTML text bridge.")
    parser.add_argument("pptx", type=Path, help="Path to the .pptx deck.")
    parser.add_argument("--html", type=Path, help="Write extracted HTML transcript here.")
    parser.add_argument("--json", type=Path, help="Write structured slide/block JSON here.")
    parser.add_argument("--title", default=None, help="Title for the HTML transcript.")
    args = parser.parse_args(argv)

    if not args.pptx.is_file():
        _fail(f"no such file: {args.pptx}")

    slides = extract(args.pptx)
    title = args.title or args.pptx.stem

    if args.json:
        args.json.write_text(json.dumps({"title": title, "slides": slides}, indent=2), encoding="utf-8")
    document = to_html(slides, title)
    if args.html:
        args.html.write_text(document, encoding="utf-8")
    if not args.html and not args.json:
        sys.stdout.write(document)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
