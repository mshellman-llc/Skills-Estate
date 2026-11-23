#!/usr/bin/env python3
"""Scope-claim check for a deck: every in-scope and out-of-scope statement the
deck makes must be found, with the same polarity, in a named source.

A pitch or decision deck often lists what is in and out of scope. Those
statements are contract-scope claims, and review-deliverable's quality gate
fails closed on them until a control backs each one. review-contract-scope, the
statement-of-work control, ships in a different plugin, so a deck built here
needs a check of its own. This is that check. In the quality record it is the
control named `check-deck-scope-claims`, and the gate accepts it as the support
for a deck's `contract_scope` assertions.

Usage:
  python3 check_scope_claims.py DECK --source SOURCE [--json report.json]

  DECK    the deck's text: .pptx, an extract_pptx.py --html or --json file, any
          .html, .md or .txt file.
  SOURCE  the named scope source: a statement of work or scope baseline as .docx,
          .pptx, .html, .md, .txt or .json.

What counts as a scope claim:
  * a sentence carrying a scope phrase: "in scope", "out of scope", "not
    included", "excluded", "outside the scope", "includes", "does not include";
  * an item under a scope heading ("In scope", "Out of scope", "Exclusions",
    "Deliverables", "Services") until the next scope heading or the next slide;
  * a table cell under a column headed that way.
A claim is the subject with the scope phrase removed. It is found when at least
80 percent of its content words appear in one source claim and every number in
it appears there too. A claim found only with the opposite polarity is
contradicted. A claim not found is unsupported. Both fail.

Limits: this is a lexical check. It proves the deck repeats what the source says
and not that the source is right, current or signed. One scope claim per
sentence reads best: "Includes A, excludes B" counts as an exclusion. Words a
deck rewrites (delivery against delivering) can read as unsupported; reword the
deck or add the source's wording, never the reverse. A reviewer still reads the
deck against the source.

Exit codes:
  0  every scope claim in the deck is supported by the source
  1  at least one claim is unsupported or contradicted
  2  unreadable input, or the source holds no scope statements to compare with

Standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

CONTROL = "check-deck-scope-claims"
MATCH_THRESHOLD = 0.8

OUT_INLINE = re.compile(
    r"\b(?:out[\s-]of[\s-]scope|not\s+in\s+scope|outside\s+(?:of\s+)?(?:the\s+)?scope|"
    r"not\s+included|excluded|excludes?|exclusions?|does\s+not\s+include|do\s+not\s+include|"
    r"is\s+not\s+part\s+of)\b", re.I)
IN_INLINE = re.compile(
    r"\b(?:in[\s-]scope|within\s+(?:the\s+)?scope|included|includes?|scope\s+includes)\b", re.I)
OUT_HEADING = re.compile(
    r"^(?:out[\s-]of[\s-]scope|exclusions?|excluded|not\s+included|"
    r"what(?:'s|\s+is)\s+not\s+included|what\s+we\s+will\s+not\s+do)\s*:?$", re.I)
IN_HEADING = re.compile(
    r"^(?:in[\s-]scope|scope\s+of\s+(?:work|services)|services|deliverables|inclusions?|"
    r"included|what(?:'s|\s+is)\s+included|what\s+we\s+will\s+deliver)\s*:?$", re.I)

STOPWORDS = {
    "the", "a", "an", "of", "is", "are", "be", "to", "and", "or", "in", "on", "for",
    "with", "by", "this", "that", "we", "will", "not", "as", "it", "its", "at", "from",
    "all", "any", "our", "your", "us", "part", "within", "outside", "out", "scope",
    "include", "included", "includes", "including", "exclude", "excluded", "excludes",
    "exclusion", "exclusions", "do", "does", "no",
}


class CheckError(Exception):
    """Unreadable input; maps to exit 2."""


# --- reading text into blocks ----------------------------------------------
# A block is {"kind": "p"|"heading"|"table"|"slide", ...}. A "slide" block marks a
# boundary that ends any scope heading's reach.

def _slide(n: int) -> dict[str, Any]:
    return {"kind": "slide", "n": n}


def _para(text: str, heading: bool = False) -> dict[str, Any]:
    return {"kind": "heading" if heading else "p", "text": re.sub(r"\s+", " ", text).strip()}


def blocks_from_pptx(path: Path) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    with zipfile.ZipFile(path) as z:
        names = sorted((n for n in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
                       key=lambda n: int(re.search(r"(\d+)", n).group(1)))
        for index, name in enumerate(names, 1):
            xml = z.read(name).decode("utf-8", "ignore")
            blocks.append(_slide(index))
            # Tables first, replaced by a marker so their cells are not read twice.
            def table(match: "re.Match[str]") -> str:
                rows = []
                for tr in re.findall(r"<a:tr\b.*?</a:tr>", match.group(0), re.S):
                    rows.append([" ".join(_runs(tc)) for tc in re.findall(r"<a:tc\b.*?</a:tc>", tr, re.S)])
                blocks.append({"kind": "table", "rows": rows})
                return ""
            rest = re.sub(r"<a:tbl>.*?</a:tbl>", table, xml, flags=re.S)
            for para in re.findall(r"<a:p\b[^>]*>.*?</a:p>", rest, re.S):
                text = " ".join(_runs(para))
                if text.strip():
                    blocks.append(_para(html.unescape(text)))
    return blocks


def _runs(xml: str) -> list[str]:
    return [html.unescape(t) for t in re.findall(r"<a:t>([^<]*)</a:t>", xml)]


def blocks_from_docx(path: Path) -> list[dict[str, Any]]:
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8", "ignore")
    blocks = []
    for para in re.findall(r"<w:p\b.*?</w:p>", xml, re.S):
        text = "".join(html.unescape(t) for t in re.findall(r"<w:t(?:\s[^>]*)?>([^<]*)</w:t>", para))
        if text.strip():
            heading = bool(re.search(r'<w:pStyle w:val="(?:Heading|Title)', para))
            blocks.append(_para(text, heading))
    return blocks


class _HtmlBlocks(HTMLParser):
    BLOCK = {"p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "div", "figcaption", "blockquote", "aside"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blocks: list[dict[str, Any]] = []
        self._buf: list[str] = []
        self._tag: str | None = None
        self._rows: list[list[str]] | None = None
        self._cell: list[str] | None = None
        self._skip = 0

    def _flush(self) -> None:
        text = "".join(self._buf).strip()
        self._buf = []
        if text and self._cell is None:
            self.blocks.append(_para(text, bool(self._tag and re.fullmatch(r"h[1-6]", self._tag))))
        self._tag = None

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in ("script", "style"):
            self._skip += 1
        elif tag == "table":
            self._flush()
            self._rows = []
        elif tag == "tr" and self._rows is not None:
            self._rows.append([])
        elif tag in ("td", "th") and self._rows is not None:
            self._cell = []
        elif tag == "section" and "slide" in (dict(attrs).get("class") or ""):
            self._flush()
            self.blocks.append(_slide(len([b for b in self.blocks if b["kind"] == "slide"]) + 1))
        elif tag in self.BLOCK or tag == "br":
            self._flush()
            self._tag = tag

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style"):
            self._skip = max(0, self._skip - 1)
        elif tag in ("td", "th") and self._cell is not None and self._rows:
            self._rows[-1].append(re.sub(r"\s+", " ", "".join(self._cell)).strip())
            self._cell = None
        elif tag == "table" and self._rows is not None:
            self.blocks.append({"kind": "table", "rows": [r for r in self._rows if r]})
            self._rows = None
        elif tag in self.BLOCK:
            self._flush()

    def handle_data(self, data: str) -> None:
        if self._skip:
            return
        (self._cell if self._cell is not None else self._buf).append(data)

    def close(self) -> None:
        super().close()
        self._flush()


def blocks_from_html(text: str) -> list[dict[str, Any]]:
    parser = _HtmlBlocks()
    parser.feed(text)
    parser.close()
    return parser.blocks


def blocks_from_text(text: str) -> list[dict[str, Any]]:
    blocks = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        heading = re.match(r"^#{1,6}\s+(.*)$", stripped)
        if heading:
            blocks.append(_para(heading.group(1), True))
            continue
        blocks.append(_para(re.sub(r"^(?:[-*+]|\d+[.)])\s+", "", stripped)))
    return blocks


def blocks_from_json(data: Any) -> list[dict[str, Any]]:
    """extract_pptx.py --json: slides with p and table blocks; any other JSON is
    flattened to its strings."""
    blocks: list[dict[str, Any]] = []
    if isinstance(data, dict) and isinstance(data.get("slides"), list):
        for slide in data["slides"]:
            blocks.append(_slide(slide.get("slide", len(blocks) + 1)))
            for block in slide.get("blocks", []):
                if block.get("kind") == "table":
                    blocks.append({"kind": "table", "rows": block.get("rows", [])})
                elif block.get("text"):
                    blocks.append(_para(block["text"]))
            if slide.get("notes"):
                blocks.append(_para(slide["notes"]))
        return blocks

    def walk(node: Any) -> None:
        if isinstance(node, str):
            blocks.append(_para(node))
        elif isinstance(node, list):
            for item in node:
                walk(item)
        elif isinstance(node, dict):
            for item in node.values():
                walk(item)
    walk(data)
    return blocks


def read_blocks(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    try:
        if suffix == ".pptx":
            return blocks_from_pptx(path)
        if suffix == ".docx":
            return blocks_from_docx(path)
        text = path.read_text(encoding="utf-8", errors="replace")
        if suffix == ".json":
            return blocks_from_json(json.loads(text))
        if suffix in (".html", ".htm"):
            return blocks_from_html(text)
        if suffix in (".md", ".txt", ".markdown", ""):
            return blocks_from_text(text)
    except (OSError, zipfile.BadZipFile, KeyError, ValueError) as exc:
        raise CheckError(f"cannot read {path}: {exc}") from exc
    raise CheckError(f"unsupported file type {suffix!r} for {path}")


# --- scope claims -----------------------------------------------------------
def tokens(text: str) -> set[str]:
    out = set()
    for word in re.findall(r"[a-z0-9]+(?:[.,][0-9]+)*", text.lower()):
        if word in STOPWORDS:
            continue
        if not word[0].isdigit():
            if len(word) > 5 and word.endswith("ing"):
                word = word[:-3]
            elif len(word) > 4 and word.endswith("ied"):
                word = word[:-3] + "y"
            elif len(word) > 4 and word.endswith("ed"):
                word = word[:-2]
            elif len(word) > 3 and word.endswith("ies"):
                word = word[:-3] + "y"
            elif len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
                word = word[:-1]
        out.add(word)
    return out


def heading_polarity(text: str) -> str | None:
    cleaned = text.strip()
    if len(cleaned.split()) > 6:
        return None
    if OUT_HEADING.match(cleaned):
        return "out"
    if IN_HEADING.match(cleaned):
        return "in"
    return None


def _claim(text: str, polarity: str, where: str) -> dict[str, Any] | None:
    subject = OUT_INLINE.sub(" ", text)
    subject = IN_INLINE.sub(" ", subject)
    toks = tokens(subject)
    if not toks:
        return None
    return {"text": text.strip(), "polarity": polarity, "where": where, "tokens": toks}


def claims_from(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    claims: list[dict[str, Any]] = []
    mode: str | None = None
    slide = 0

    def where(extra: str = "") -> str:
        return (f"slide {slide}" if slide else "document") + extra

    def from_text(text: str) -> None:
        for sentence in re.split(r"(?<=[.!?])\s+", text):
            sentence = sentence.strip()
            if not sentence:
                continue
            if OUT_INLINE.search(sentence):
                polarity = "out"
            elif IN_INLINE.search(sentence):
                polarity = "in"
            elif mode:
                polarity = mode
            else:
                continue
            claim = _claim(sentence, polarity, where())
            if claim:
                claims.append(claim)

    for block in blocks:
        kind = block["kind"]
        if kind == "slide":
            slide, mode = block["n"], None
        elif kind in ("p", "heading"):
            polarity = heading_polarity(block["text"])
            if polarity:
                mode = polarity
            elif kind == "heading":
                mode = None
                from_text(block["text"])
            else:
                from_text(block["text"])
        elif kind == "table":
            rows = [[c for c in row] for row in block["rows"]]
            columns = [heading_polarity(c) for c in rows[0]] if rows else []
            if any(columns):
                for row in rows[1:]:
                    for index, cell in enumerate(row):
                        polarity = columns[index] if index < len(columns) else None
                        if polarity and cell.strip():
                            claim = _claim(cell, polarity, where(", table"))
                            if claim:
                                claims.append(claim)
            else:
                for row in rows:
                    for cell in row:
                        from_text(cell)
    return claims


def compare(deck: list[dict[str, Any]], source: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results = []
    for claim in deck:
        numbers = {t for t in claim["tokens"] if t[0].isdigit()}
        best_same = best_other = 0.0
        found_in = None
        for ref in source:
            if not numbers <= ref["tokens"]:
                continue
            ratio = len(claim["tokens"] & ref["tokens"]) / len(claim["tokens"])
            if ratio < MATCH_THRESHOLD:
                continue
            if ref["polarity"] == claim["polarity"]:
                if ratio > best_same:
                    best_same, found_in = ratio, ref
            elif ratio > best_other:
                best_other = ratio
        if found_in:
            status = "supported"
        elif best_other:
            status = "contradicted"
        else:
            status = "unsupported"
        results.append({
            "claim": claim["text"], "polarity": claim["polarity"], "where": claim["where"],
            "status": status,
            "source_text": found_in["text"] if found_in else None,
        })
    return results


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(deck_path: Path, source_path: Path) -> dict[str, Any]:
    source_claims = claims_from(read_blocks(source_path))
    if not source_claims:
        raise CheckError(f"{source_path} holds no scope statements to compare with")
    results = compare(claims_from(read_blocks(deck_path)), source_claims)
    failing = [r for r in results if r["status"] != "supported"]
    return {
        "control": CONTROL,
        "verdict": "fail" if failing else "pass",
        "deck": str(deck_path), "deck_sha256": sha256(deck_path),
        "source": str(source_path), "source_sha256": sha256(source_path),
        "claims_checked": len(results), "claims_not_supported": len(failing),
        "claims": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check a deck's scope claims against a named source.")
    parser.add_argument("deck", type=Path)
    parser.add_argument("--source", type=Path, required=True,
                        help="the statement of work or scope baseline the deck must agree with")
    parser.add_argument("--json", type=Path, help="write the report here; cite this path in the quality record")
    args = parser.parse_args(argv)
    try:
        report = check(args.deck, args.source)
    except CheckError as exc:
        print(f"check_scope_claims: {exc}", file=sys.stderr)
        return 2
    if args.json:
        args.json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    for r in report["claims"]:
        if r["status"] != "supported":
            print(f"{r['status'].upper()}: {r['where']}: {r['claim']!r} ({r['polarity']} of scope)")
    print(f"{report['verdict'].upper()}: {report['claims_checked']} scope claim(s) checked, "
          f"{report['claims_not_supported']} not supported by {args.source.name}")
    return 1 if report["verdict"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
