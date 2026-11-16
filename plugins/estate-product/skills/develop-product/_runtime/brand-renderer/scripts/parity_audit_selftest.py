#!/usr/bin/env python3
"""Self-test for parity_audit.py.

Covers positive, hidden, scoped-hidden, strict-warning, structural, and malformed
cases, plus the selector grammar and external-link marking the standard-library
parser now answers for. The external-link pair is here because the earlier suite
had no correctly-marked link in it: `rel` is a token list, reading it as a bare
string turned "noopener noreferrer" into a set of single characters, and every
compliant link raised a safety warning that no test could see.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def codes(script: Path, manifest: Path, artifact: Path) -> set:
    """Every finding code the audit reports, errors and warnings alike."""
    completed = subprocess.run(
        [sys.executable, str(script), str(manifest), str(artifact)],
        capture_output=True, text=True, check=False,
    )
    report = json.loads(completed.stdout)
    return {f["code"] for f in report["errors"] + report["warnings"]}


def run(script: Path, manifest: Path, artifact: Path, strict: bool = False) -> int:
    command = [sys.executable, str(script), str(manifest), str(artifact)]
    if strict:
        command.append("--strict")
    completed = subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return completed.returncode


def main() -> int:
    script = Path(__file__).with_name("parity_audit.py")
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        good_manifest = {
            "manifestVersion": "1.0",
            "requiredPhrases": ["Reject as offered", "Margin below sourced floor"],
            "forbiddenPhrases": ["Approved"],
            "requiredEvidenceReferences": ["M-12"],
            "protectedClaims": [
                {
                    "id": "decision",
                    "text": "Reject as offered",
                    "requiredQualifiers": ["Margin below sourced floor"],
                    "selector": "#decision",
                }
            ],
            "requiredSelectors": ["main", "h1", "#decision"],
            "requiredViews": [],
        }
        manifest = root / "manifest.json"
        manifest.write_text(json.dumps(good_manifest), encoding="utf-8")

        good = root / "good.html"
        good.write_text(
            '<!doctype html><html lang="en"><body><main><h1>Commercial review</h1>'
            '<section id="decision"><p>Reject as offered</p><p>Margin below sourced floor</p><p>M-12</p></section>'
            '</main></body></html>',
            encoding="utf-8",
        )

        hidden = root / "hidden.html"
        hidden.write_text(
            '<!doctype html><html lang="en"><body><main><h1>Commercial review</h1>'
            '<section id="decision" style="display:none"><p>Reject as offered</p>'
            '<p>Margin below sourced floor</p><p>M-12</p></section></main></body></html>',
            encoding="utf-8",
        )

        scoped_only_manifest = {
            "manifestVersion": "1.0",
            "requiredPhrases": [],
            "forbiddenPhrases": [],
            "requiredEvidenceReferences": [],
            "protectedClaims": [
                {
                    "id": "decision",
                    "text": "Reject as offered",
                    "requiredQualifiers": ["Margin below sourced floor"],
                    "selector": "#decision",
                }
            ],
            "requiredSelectors": ["main", "h1", "#decision"],
            "requiredViews": [],
        }
        scoped_manifest = root / "scoped.json"
        scoped_manifest.write_text(json.dumps(scoped_only_manifest), encoding="utf-8")

        ancestor_variants = {
            "hidden_attr": "hidden",
            "aria_hidden": 'aria-hidden="true"',
            "display_none": 'style="display:none"',
            "visibility_hidden": 'style="visibility:hidden"',
            "opacity_zero": 'style="opacity:0"',
        }
        ancestor_files = {}
        for name, attribute in ancestor_variants.items():
            path = root / f"ancestor-{name}.html"
            path.write_text(
                '<!doctype html><html lang="en"><body><main><h1>Commercial review</h1>'
                f'<div {attribute}><section id="decision"><p>Reject as offered</p>'
                '<p>Margin below sourced floor</p><p>M-12</p></section></div>'
                '</main></body></html>',
                encoding="utf-8",
            )
            ancestor_files[name] = path

        broken = root / "broken.html"
        broken.write_text(
            '<!doctype html><html lang="en"><body><main><h1>Commercial review</h1>'
            '<section id="decision" aria-labelledby="missing"><p>Reject as offered</p>'
            '<p>Margin below sourced floor</p><p>M-12</p></section><div id="decision"></div>'
            '</main></body></html>',
            encoding="utf-8",
        )

        malformed = root / "malformed.json"
        malformed.write_text('{"manifestVersion":1,"requiredPhrases":"bad"}', encoding="utf-8")

        invalid_selector = root / "invalid-selector.json"
        invalid_selector.write_text(
            json.dumps({**good_manifest, "requiredSelectors": [{"text": "main"}]}),
            encoding="utf-8",
        )

        # Selector grammar: class, compound, and comma-separated list.
        selector_manifest = root / "selectors.json"
        selector_manifest.write_text(
            json.dumps({
                "manifestVersion": "1.0",
                "requiredSelectors": [
                    "main", "h1", ".panel", "section.panel", "#absent, #decision",
                ],
            }),
            encoding="utf-8",
        )
        selector_html = root / "selectors.html"
        selector_html.write_text(
            '<!doctype html><html lang="en"><body><main><h1>Commercial review</h1>'
            '<section id="decision" class="panel wide"><p>Reject as offered</p></section>'
            '</main></body></html>',
            encoding="utf-8",
        )

        unsupported_selector = root / "unsupported-selector.json"
        unsupported_selector.write_text(
            json.dumps({"manifestVersion": "1.0", "requiredSelectors": ["main p"]}),
            encoding="utf-8",
        )

        # External links: one marked to the rule, one bare.
        link_manifest = root / "links.json"
        link_manifest.write_text(
            json.dumps({"manifestVersion": "1.0", "requiredSelectors": ["main", "h1"]}),
            encoding="utf-8",
        )
        marked_link = root / "link-marked.html"
        marked_link.write_text(
            '<!doctype html><html lang="en"><body><main><h1>Commercial review</h1>'
            '<a href="https://example.com" target="_blank" rel="noopener noreferrer">Source</a>'
            '</main></body></html>',
            encoding="utf-8",
        )
        bare_link = root / "link-bare.html"
        bare_link.write_text(
            '<!doctype html><html lang="en"><body><main><h1>Commercial review</h1>'
            '<a href="https://example.com">Source</a></main></body></html>',
            encoding="utf-8",
        )

        observed = {
            "positive": run(script, manifest, good),
            "selector_grammar": run(script, selector_manifest, selector_html),
            "unsupported_selector": run(script, unsupported_selector, good),
            "external_link_marked": "EXTERNAL_LINK_SAFETY" in codes(script, link_manifest, marked_link),
            "external_link_bare": "EXTERNAL_LINK_SAFETY" in codes(script, link_manifest, bare_link),
            "strict_warning": run(script, manifest, good, strict=True),
            "inline_hidden": run(script, manifest, hidden),
            "scoped_hidden_only": run(script, scoped_manifest, hidden),
            "broken_structure": run(script, manifest, broken),
            "malformed_manifest": run(script, malformed, good),
            "invalid_selector_type": run(script, invalid_selector, good),
        }
        observed.update({f"ancestor_{name}": run(script, scoped_manifest, path) for name, path in ancestor_files.items()})
        expected = {
            "positive": 0,
            "selector_grammar": 0,
            "unsupported_selector": 2,
            "external_link_marked": False,
            "external_link_bare": True,
            "strict_warning": 1,
            "inline_hidden": 1,
            "scoped_hidden_only": 1,
            "broken_structure": 1,
            "malformed_manifest": 2,
            "invalid_selector_type": 2,
        }
        expected.update({f"ancestor_{name}": 1 for name in ancestor_files})
        print(json.dumps({"observed": observed, "expected": expected}, indent=2))
        return 0 if observed == expected else 1


if __name__ == "__main__":
    sys.exit(main())
