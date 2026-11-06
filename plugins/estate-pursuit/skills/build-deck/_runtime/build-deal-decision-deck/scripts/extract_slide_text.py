#!/usr/bin/env python3
"""
extract_slide_text.py — extract slide copy from a PPTX for DDOC quality scanning.

Usage:
  python extract_slide_text.py DECK.pptx                  # plain text output for writing-diagnostics
  python extract_slide_text.py DECK.pptx --json           # structured JSON output
  python extract_slide_text.py DECK.pptx --manifest       # slide manifest format (for review/approval workflow)
  python extract_slide_text.py DECK.pptx --figures        # figures only (for tie-out check)

The plain text output is the format expected by writing-diagnostics.
The manifest format matches the DDOC quality skill's Phase 1 slide manifest.

Requirements: python-pptx (pip install python-pptx)
"""

import sys
import json
import re
import argparse
from pathlib import Path

try:
    from pptx import Presentation
    from pptx.util import Pt
except ImportError:
    sys.exit("python-pptx is required: pip install python-pptx --break-system-packages")


# ---------------------------------------------------------------------------
# Shape classification helpers
# ---------------------------------------------------------------------------

def classify_shape(shape, slide_idx):
    """Return a role label for a shape based on position and size heuristics."""
    if not shape.has_text_frame:
        return None
    text = shape.text_frame.text.strip()
    if not text:
        return None
    # Heuristic: large shapes near the top are likely titles/headers
    try:
        top_pct = shape.top / 6858000  # EMU units; 6858000 = ~96px at standard slide height
        left_pct = shape.left / 9144000
        width_pct = shape.width / 9144000
        is_wide = width_pct > 0.6
        is_top = top_pct < 0.25
    except Exception:
        return "body"

    if is_top and is_wide:
        return "title"
    elif is_top and not is_wide:
        return "subtitle"
    else:
        return "body"


def shape_text_lines(shape):
    """Return list of non-empty paragraph strings from a shape."""
    if not shape.has_text_frame:
        return []
    lines = []
    for para in shape.text_frame.paragraphs:
        text = para.text.strip()
        if text:
            lines.append(text)
    return lines


# ---------------------------------------------------------------------------
# Figure extraction (for --figures / --tie-out)
# ---------------------------------------------------------------------------

FIGURE_RE = re.compile(
    r'(?:'
    r'\$[\d,]+(?:\.\d+)?(?:\s*[KMB])?'   # dollar amounts
    r'|\d+(?:,\d{3})*(?:\.\d+)?\s*(?:hours?|hrs?|days?|weeks?|months?|%|percent)'  # quantities with units
    r'|\d+\s*(?:users?|seats?|sites?|objects?|flows?|integrations?)'  # counts
    r')',
    re.IGNORECASE
)

def extract_figures(text):
    return FIGURE_RE.findall(text)


# ---------------------------------------------------------------------------
# Core extraction
# ---------------------------------------------------------------------------

def extract(pptx_path):
    """Return a list of slide dicts."""
    prs = Presentation(pptx_path)
    slides = []
    for idx, slide in enumerate(prs.slides):
        slide_data = {
            "slide_number": idx + 1,
            "shapes": [],
        }
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            lines = shape_text_lines(shape)
            if not lines:
                continue
            role = classify_shape(shape, idx)
            slide_data["shapes"].append({
                "role": role,
                "lines": lines,
            })
        slides.append(slide_data)
    return slides


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def as_plain_text(slides):
    """Flat text, one line per paragraph, slide-separated for writing-diagnostics."""
    parts = []
    for slide in slides:
        parts.append(f"=== Slide {slide['slide_number']} ===")
        for shape in slide["shapes"]:
            for line in shape["lines"]:
                parts.append(line)
        parts.append("")
    return "\n".join(parts)


def as_manifest(slides):
    """Slide manifest format — matches Phase 1 of the DDOC quality workflow."""
    parts = []
    for slide in slides:
        num = slide["slide_number"]
        titles = []
        bodies = []
        for shape in slide["shapes"]:
            role = shape["role"]
            if role in ("title", "subtitle"):
                titles.extend(shape["lines"])
            else:
                bodies.extend(shape["lines"])

        title_str = " / ".join(titles) if titles else "[no title detected]"
        parts.append(f"SLIDE {num}:")
        parts.append(f"  Title: {title_str}")
        if bodies:
            parts.append("  Body:")
            for line in bodies:
                parts.append(f"    - {line}")
        parts.append("")
    return "\n".join(parts)


def as_figures_only(slides):
    """Figures only — for manual or automated tie-out against the SOW."""
    parts = []
    for slide in slides:
        slide_figures = []
        for shape in slide["shapes"]:
            for line in shape["lines"]:
                figs = extract_figures(line)
                for fig in figs:
                    slide_figures.append((fig, line.strip()))
        if slide_figures:
            parts.append(f"Slide {slide['slide_number']}:")
            for fig, context in slide_figures:
                parts.append(f"  {fig!r:30s}  in: {context[:80]}")
    return "\n".join(parts) if parts else "(no figures found)"


# ---------------------------------------------------------------------------
# Diagnostic summary helpers
# ---------------------------------------------------------------------------

EMDASH_RE = re.compile(r'—|–')
SECTION_SIGN_RE = re.compile(r'§')
COLON_RE = re.compile(r':')
SHORT_SENTENCE_RE = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!)\s+[A-Z][^.!?]{0,25}[.!?]')

def diagnostic_summary(slides):
    """Quick diagnostic counts to surface before Phase 3 review."""
    total_emdash = 0
    total_section_sign = 0
    per_slide_colons = []
    short_sentence_hits = []

    for slide in slides:
        all_text = " ".join(
            line for shape in slide["shapes"] for line in shape["lines"]
        )
        emdash = len(EMDASH_RE.findall(all_text))
        ssign = len(SECTION_SIGN_RE.findall(all_text))
        colons = len(COLON_RE.findall(all_text))
        total_emdash += emdash
        total_section_sign += ssign
        per_slide_colons.append((slide["slide_number"], colons))

        # Short sentence fragments (under ~5 words between punctuation)
        for shape in slide["shapes"]:
            for line in shape["lines"]:
                words = line.split()
                if len(words) <= 5 and line.endswith(('.', '!', '?')) and shape["role"] == "body":
                    short_sentence_hits.append((slide["slide_number"], line))

    lines = []
    lines.append("=== DIAGNOSTIC SUMMARY ===")
    lines.append(f"Em dashes (authored copy must be 0): {total_emdash}")
    lines.append(f"Section signs (must be 0):           {total_section_sign}")
    lines.append("")
    lines.append("Colon density by slide (>2 in body = review):")
    for snum, ccount in per_slide_colons:
        flag = " ← review" if ccount > 2 else ""
        lines.append(f"  Slide {snum:2d}: {ccount} colons{flag}")
    lines.append("")
    if short_sentence_hits:
        lines.append("Short-sentence fragment candidates (body, ≤5 words):")
        for snum, line in short_sentence_hits:
            lines.append(f"  Slide {snum}: {line!r}")
    else:
        lines.append("Short-sentence fragments: none detected")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Extract slide text from a PPTX for DDOC quality review."
    )
    parser.add_argument("pptx", help="Path to the .pptx file")
    parser.add_argument("--json", action="store_true", help="Structured JSON output")
    parser.add_argument("--manifest", action="store_true", help="Slide manifest format (Phase 1)")
    parser.add_argument("--figures", action="store_true", help="Figures only (tie-out)")
    parser.add_argument("--diagnostic", action="store_true", help="Diagnostic summary counts")
    args = parser.parse_args()

    path = Path(args.pptx)
    if not path.exists():
        sys.exit(f"File not found: {path}")
    if path.suffix.lower() != ".pptx":
        sys.exit(f"Expected a .pptx file, got: {path.suffix}")

    slides = extract(path)

    if args.json:
        print(json.dumps(slides, indent=2))
    elif args.manifest:
        print(as_manifest(slides))
    elif args.figures:
        print(as_figures_only(slides))
    elif args.diagnostic:
        print(diagnostic_summary(slides))
    else:
        print(as_plain_text(slides))


if __name__ == "__main__":
    main()
