#!/usr/bin/env python3
"""Selftest for check_scope_claims.py. Stdlib only, no network.

Issue 169: a pitch deck that lists what is in and out of scope needs a scope
check of its own, because review-contract-scope ships in another plugin. Each
case builds the fictional "Example bakery pitch deck" and a fictional statement
of work, runs the CLI, and asserts the exit code and the status it reports.

Exit 0 when every case matches, 1 otherwise.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

SCRIPT = Path(__file__).with_name("check_scope_claims.py")

SOW = """# Example bakery statement of work

## In scope
- Wedding cake design and tasting sessions
- Up to 3 revision rounds

## Out of scope
- Delivery of wedding cakes
- Custom sugar flowers

The bakery owner supplies the venue list. Pricing is excluded from this statement of work.
"""

FAILURES: list[str] = []


def run(deck: Path, source: Path, report: Path | None = None) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(SCRIPT), str(deck), "--source", str(source)]
    if report:
        cmd += ["--json", str(report)]
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def expect(name: str, root: Path, deck: Path, source: Path, exit_code: int, statuses: list[str] | None = None) -> None:
    report = root / f"{name}.report.json"
    result = run(deck, source, report)
    if result.returncode != exit_code:
        FAILURES.append(f"{name}: exit {result.returncode}, want {exit_code}\n{result.stdout}{result.stderr}")
        return
    if statuses is not None:
        got = [c["status"] for c in json.loads(report.read_text())["claims"]]
        if got != statuses:
            FAILURES.append(f"{name}: statuses {got}, want {statuses}")


def pptx(path: Path, slides: list[str]) -> None:
    """Minimal deck: only the slide XML carries the text."""
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("[Content_Types].xml", "<Types/>")
        for i, xml in enumerate(slides, 1):
            z.writestr(f"ppt/slides/slide{i}.xml",
                       f"<p:sld><p:cSld><p:spTree>{xml}</p:spTree></p:cSld></p:sld>")


def para(text: str) -> str:
    return f"<p:sp><p:txBody><a:p><a:r><a:t>{text}</a:t></a:r></a:p></p:txBody></p:sp>"


def table(rows: list[list[str]]) -> str:
    body = "".join("<a:tr>" + "".join(f"<a:tc><a:txBody><a:p><a:r><a:t>{c}</a:t></a:r></a:p></a:txBody></a:tc>"
                                      for c in row) + "</a:tr>" for row in rows)
    return f"<p:graphicFrame><a:graphic><a:graphicData><a:tbl>{body}</a:tbl></a:graphicData></a:graphic></p:graphicFrame>"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "sow.md"
        source.write_text(SOW, encoding="utf-8")

        def md(name: str, text: str) -> Path:
            path = root / f"{name}.md"
            path.write_text(text, encoding="utf-8")
            return path

        # The issue's reproduction: the deck says wedding-cake delivery is out of scope.
        expect("issue_169_repro_supported", root,
               md("repro", "# Example bakery pitch deck\n\nDelivery of wedding cakes is out of scope.\n"),
               source, 0, ["supported"])
        expect("same_claim_worded_differently", root,
               md("reworded", "Wedding cake delivery is not included.\n"), source, 0, ["supported"])
        expect("opposite_polarity_is_contradicted", root,
               md("opposite", "Delivery of wedding cakes is in scope.\n"), source, 1, ["contradicted"])
        expect("claim_absent_from_source", root,
               md("absent", "Weekend cake decorating classes are in scope.\n"), source, 1, ["unsupported"])
        expect("number_must_match", root,
               md("number", "Up to 5 revision rounds are included.\n"), source, 1, ["unsupported"])
        expect("number_matches", root,
               md("number_ok", "Up to 3 revision rounds are included.\n"), source, 0, ["supported"])
        expect("one_bad_claim_fails_the_deck", root,
               md("mixed", "Custom sugar flowers are out of scope.\nFree cake delivery is in scope.\n"),
               source, 1, ["supported", "unsupported"])
        expect("no_scope_claims_is_a_pass", root,
               md("none", "Example bakery pitch deck. Our team bakes fresh daily.\n"), source, 0, [])
        expect("source_without_scope_statements_is_an_error", root,
               md("any", "Delivery of wedding cakes is out of scope.\n"),
               md("empty_source", "The bakery opens at six.\n"), 2)
        expect("missing_deck_is_an_error", root, root / "nope.md", source, 2)

        # Heading mode in a .pptx: items under "Out of scope" are exclusions until the slide ends.
        deck = root / "example.pptx"
        pptx(deck, [para("Out of scope") + para("Delivery of wedding cakes") + para("Custom sugar flowers"),
                    para("In scope") + para("Wedding cake design and tasting sessions")])
        expect("pptx_items_under_scope_headings", root, deck, source, 0,
               ["supported", "supported", "supported"])
        bad = root / "example_bad.pptx"
        pptx(bad, [para("In scope") + para("Delivery of wedding cakes")])
        expect("pptx_exclusion_listed_as_in_scope", root, bad, source, 1, ["contradicted"])
        reset = root / "example_reset.pptx"
        pptx(reset, [para("Out of scope") + para("Custom sugar flowers"), para("Our bakers") + para("Rye loaves daily")])
        expect("scope_heading_ends_with_its_slide", root, reset, source, 0, ["supported"])

        # Table columns headed In scope and Out of scope.
        tabled = root / "example_table.pptx"
        pptx(tabled, [table([["In scope", "Out of scope"],
                             ["Wedding cake design and tasting sessions", "Delivery of wedding cakes"],
                             ["Up to 3 revision rounds", "Wedding cake insurance"]])])
        expect("pptx_table_columns", root, tabled, source, 1,
               ["supported", "supported", "supported", "unsupported"])

        # The extract_pptx.py HTML and JSON shapes.
        html = root / "example.extracted.html"
        html.write_text("<html><body><h1>Example bakery pitch deck</h1><main>"
                        '<section class="slide" data-slide="1"><h2>Slide 1</h2>'
                        "<p>Out of scope</p><p>Delivery of wedding cakes</p></section>"
                        '<section class="slide" data-slide="2"><h2>Slide 2</h2>'
                        "<p>Our bakers start at five.</p></section></main></body></html>", encoding="utf-8")
        expect("extract_html_shape", root, html, source, 0, ["supported"])
        extract = root / "example.extracted.json"
        extract.write_text(json.dumps({"title": "Example", "slides": [
            {"slide": 1, "notes": "", "blocks": [{"kind": "p", "text": "Exclusions"},
                                                 {"kind": "p", "text": "Custom sugar flowers"}]}]}), encoding="utf-8")
        expect("extract_json_shape", root, extract, source, 0, ["supported"])

        # Report carries what the quality record cites.
        report = root / "cite.json"
        run(md("cite", "Custom sugar flowers are out of scope.\n"), source, report)
        data = json.loads(report.read_text())
        for key, want in (("control", "check-deck-scope-claims"), ("verdict", "pass")):
            if data.get(key) != want:
                FAILURES.append(f"report {key} is {data.get(key)!r}, want {want!r}")
        if not (data.get("deck_sha256") and data.get("source_sha256")):
            FAILURES.append("report does not bind deck and source by hash")

    if FAILURES:
        for item in FAILURES:
            print("FAIL:", item)
        return 1
    print("PASS: deck scope claims are checked against the named source")
    return 0


if __name__ == "__main__":
    sys.exit(main())
