#!/usr/bin/env python3
"""
slop_scan.py - structural slop scanner for Estate client-facing SOWs.

Finds candidates; the human judges them. It does not edit.
Reports: repeated mechanics (repetition-as-thoroughness), justification-tail
candidates, rule-of-three verb piles, meta-commentary candidates, and the
two hard house-style checks (section-sign symbol, em dashes).

Usage:
    python slop_scan.py SOW.docx
    python slop_scan.py SOW.docx --verify   # terse pass/fail summary

Uses the Python standard library for DOCX text extraction. --text prints the
complete extracted text for review; drawing/embedded-object content still needs
rendered inspection.
"""
import sys
import re
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter

# Distinctive FULL-CLAUSE phrases that only the owning section should contain.
# These must be long and specific enough that legitimate term-recurrence does
# NOT match. A short fragment like "Change Order before" or "75% aggregate"
# recurs legitimately (defined terms, distinct rules) and is NOT a mechanic
# repeat; do not put fragments here. See references/structural-deslop.md for
# the term-recurrence-is-fine rule. Extend per tier with full clauses only.
MECHANIC_PHRASES = [
    "re-baselines the estimate and timeline through a Change Order before Build proceeds",
    "bills as the lower actual effort",
    "exit criteria that gate progression",
    "is enabling and non-billable",
    "no separate senior-architect line in the price",
    "consumes the envelope faster than the hour total",
    "footprint materially exceeds the Basis of Estimate, Estate re-baselines",
]

# Justification-tail connectors: a rule followed by one of these often explains
# why the rule exists. Candidates only; the exception (defends a deviation) is
# a human call.
JUSTIFICATION_MARKERS = [
    r",\s*so (?:that )?the\b",
    r",\s*because\b",
    r"\bso that it can be\b",
    r"\bin order to\b",
    r"\bwhich ensures\b",
    r"\bto ensure that\b",
]

# Meta-commentary: sentences about Estate's own pricing/staffing logic that a
# client did not ask about.
META_MARKERS = [
    r"non-billable",
    r"no separate .{0,30} line in the price",
    r"consumes the envelope faster",
    r"enabling and",
    r"is fixed oversight",
    r"reflects the delivery plan",
]

# Rule-of-three verb piles: "X, Y, or Z" / "X, Y, and Z" with three verbs.
RULE_OF_THREE = re.compile(
    r"\b(\w+),\s+(\w+),\s+(?:or|and)\s+(\w+)\b"
)


def get_text(path):
    """Read Word text without invoking an external executable.

    Tables belong in the complete text and figure scan. The prose-only view
    excludes table paragraphs but retains literal pipe-prefixed prose. Word
    text runs are joined before counting a phrase split across formatting.
    """
    ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    full, prose = [], []

    def walk(node, in_table=False):
        in_table = in_table or node.tag == ns + "tbl"
        if node.tag == ns + "p":
            pieces = []
            for part in node.iter():
                if part.tag == ns + "t":
                    pieces.append(part.text or "")
                elif part.tag == ns + "tab":
                    pieces.append("\t")
                elif part.tag in (ns + "br", ns + "cr"):
                    pieces.append("\n")
                elif part.tag == ns + "noBreakHyphen":
                    pieces.append("\u2011")
                elif part.tag == ns + "softHyphen":
                    pieces.append("\u00ad")
                elif part.tag == ns + "sym":
                    # Legacy symbol fonts use font-specific/private mappings.
                    # Never silently erase them or guess a contractual symbol.
                    font = part.get(ns + "font", "").casefold()
                    raw = part.get(ns + "char", "")
                    text_fonts = {"arial", "times new roman", "calibri", "aptos",
                                  "cambria", "courier new", "helvetica"}
                    try:
                        code = int(raw, 16)
                        supported = font in text_fonts and 0x20 <= code < 0xD800
                        supported &= not 0x7F <= code <= 0x9F
                        if not supported:
                            raise ValueError()
                        pieces.append(chr(code))
                    except ValueError:
                        raise ValueError(f"unmappable Word symbol font={font!r} char={raw!r}; inspect the rendered document")
            text = "".join(pieces)
            if text.strip():
                full.append(text)
                if not in_table:
                    prose.append(text)
            return
        for child in node:
            walk(child, in_table)

    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            if "word/document.xml" not in names:
                raise ValueError("DOCX has no word/document.xml")
            parts = ["word/document.xml"] + sorted(
                n for n in names if re.fullmatch(
                    r"word/(?:header\d+|footer\d+|footnotes|endnotes)\.xml", n))
            for name in parts:
                walk(ET.fromstring(archive.read(name)))
    except (OSError, ValueError, zipfile.BadZipFile, ET.ParseError) as e:
        sys.exit(f"Could not extract text from {path}: {e}")
    if not full:
        sys.exit(f"Could not extract text from {path}: no readable Word text; inspect the rendered document")
    return "\n".join(full), "\n".join(prose)


def sentences(prose):
    # crude sentence split good enough for scanning
    return [s.strip() for s in re.split(r"(?<=[.])\s+", prose) if s.strip()]


def scan(path, verify=False):
    full, prose = get_text(path)
    # Discretionary hyphens are layout hints. Keep them in --text/source, but
    # do not let formatting conceal a repeated mechanic from the diagnostics.
    full, prose = full.replace("\u00ad", ""), prose.replace("\u00ad", "")
    findings = {}

    # 1. repeated mechanics
    repeats = {}
    for phrase in MECHANIC_PHRASES:
        n = full.count(phrase)
        if n > 1:
            repeats[phrase] = n
    findings["repeated_mechanics"] = repeats

    # 2. justification-tail candidates
    jt = []
    for s in sentences(prose):
        for pat in JUSTIFICATION_MARKERS:
            if re.search(pat, s):
                jt.append(s)
                break
    findings["justification_candidates"] = jt

    # 3. meta-commentary candidates
    meta = []
    for s in sentences(prose):
        for pat in META_MARKERS:
            if re.search(pat, s, re.I):
                meta.append(s)
                break
    findings["meta_candidates"] = meta

    # 4. rule-of-three (verb piles); report sentences with the pattern
    r3 = []
    for s in sentences(prose):
        if RULE_OF_THREE.search(s):
            r3.append(s)
    findings["rule_of_three"] = r3

    # 5. hard house-style checks
    findings["section_sign_count"] = full.count("\u00a7")
    findings["em_dash_count"] = full.count("\u2014")

    return findings


def report(path, f, verify):
    sign = f["section_sign_count"]
    em = f["em_dash_count"]
    reps = f["repeated_mechanics"]

    if verify:
        ok = (sign == 0 and em == 0 and not reps)
        print(f"{'PASS' if ok else 'FAIL'}  {path}")
        print(f"  section-sign: {sign} (must be 0)")
        print(f"  em-dash: {em} (must be 0)")
        if reps:
            print("  repeated mechanics still present:")
            for p, n in reps.items():
                print(f"    {n}x  {p}")
        else:
            print("  repeated mechanics: none")
        return 0 if ok else 1

    print(f"=== slop scan: {path} ===\n")

    print("REPEATED MECHANICS (repetition-as-thoroughness)")
    if reps:
        print("  Each should appear once, in its owning section. Cut others to a pointer.")
        for p, n in sorted(reps.items(), key=lambda kv: -kv[1]):
            print(f"    {n}x  \"{p}\"")
    else:
        print("  none over threshold")
    print()

    print(f"JUSTIFICATION-TAIL CANDIDATES ({len(f['justification_candidates'])})")
    print("  Cut the why UNLESS it defends an exception or a stricter-than-default term.")
    for s in f["justification_candidates"]:
        print(f"    - {s[:160]}")
    print()

    print(f"META-COMMENTARY CANDIDATES ({len(f['meta_candidates'])})")
    print("  Sentences about internal pricing/staffing logic. Usually cut.")
    for s in f["meta_candidates"]:
        print(f"    - {s[:160]}")
    print()

    print(f"RULE-OF-THREE / VERB PILES ({len(f['rule_of_three'])})")
    print("  Review for verb piles that restate a boundary owned elsewhere.")
    for s in f["rule_of_three"][:25]:
        print(f"    - {s[:160]}")
    if len(f["rule_of_three"]) > 25:
        print(f"    ... and {len(f['rule_of_three']) - 25} more")
    print()

    print("HOUSE STYLE (hard)")
    print(f"    section-sign symbol: {sign}  (must be 0)")
    print(f"    em dash: {em}  (must be 0)")
    print()
    print("Note: candidates are not verdicts. Judge each against references/structural-deslop.md.")
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]
    if not args:
        sys.exit("usage: python slop_scan.py SOW.docx [--verify|--text]")
    if "--text" in flags:
        print(get_text(args[0])[0])
        sys.exit(0)
    findings = scan(args[0], verify="--verify" in flags)
    sys.exit(report(args[0], findings, "--verify" in flags))
