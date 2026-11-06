#!/usr/bin/env python3
"""Self-test for html_dom.py, the standard-library tree behind the parity gate.

Each case is a behavior parity_audit.py depends on. Prints observed versus
expected and exits nonzero on a mismatch.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from html_dom import SelectorError, parse_html  # noqa: E402

DOC = (
    '<!doctype html><html lang="en"><head><style>.x{color:#000}</style></head>'
    '<body><main><h1>Commercial review</h1>'
    '<section id="decision" class="panel wide" aria-labelledby="lbl">'
    '<p>Reject as offered</p><span style="display:none">Hidden note</span>'
    '</section>'
    '<div hidden><p>Ancestor hidden</p></div>'
    '<img src="chart.png" alt="Margin chart">'
    '<a href="https://example.com" target="_blank" rel="noopener noreferrer">Source</a>'
    '<script>var forbidden = "script text";</script>'
    '</main></body></html>'
)


def main() -> int:
    doc = parse_html(DOC)
    text = doc.get_text()
    section = doc.select_one("#decision")

    def unsupported(selector: str) -> bool:
        try:
            doc.select_one(selector)
        except SelectorError:
            return True
        return False

    observed = {
        "tag_selector": doc.select_one("h1").tag,
        "id_selector": section.tag,
        "class_selector": doc.select_one(".panel").get("id"),
        "compound_selector": doc.select_one("section.panel.wide").get("id"),
        # A comma list returns the first match in document order, not the first
        # match of the first compound that happens to hit.
        "comma_document_order": doc.select_one("#decision, h1").tag,
        "comma_miss_then_hit": doc.select_one("#absent, #decision").get("id"),
        "select_all_count": len(doc.select("p")),
        "descendant_combinator_rejected": unsupported("main p"),
        "attribute_selector_rejected": unsupported("a[href]"),
        "pseudo_class_rejected": unsupported("p:first-child"),
        "lang_attribute": doc.find_tag("html").get("lang"),
        "find_by_id": doc.find_by_id("decision").tag,
        "find_by_id_absent": doc.find_by_id("nope"),
        "h1_count": len(doc.find_all("h1")),
        "all_elements_include_void": "img" in [n.tag for n in doc.find_all()],
        "img_alt": doc.find_tag("img").get("alt"),
        "void_element_not_nested": len(doc.find_tag("img").children),
        "rel_is_token_list": doc.find_tag("a").attr_list("rel"),
        "class_is_token_list": section.attr_list("class"),
        "absent_attr_list_empty": section.attr_list("rel"),
        "has_attr_true": section.has_attr("aria-labelledby"),
        "has_attr_false": section.has_attr("aria-controls"),
        # get_text is the raw walk. Filtering script and style belongs to the
        # caller's content policy, which parity_audit.py owns as NON_CONTENT_TAGS.
        "get_text_is_unfiltered": "forbidden" in text,
        "ancestors_reach_root": "main" in [n.tag for n in section.ancestors()],
        "scoped_text": section.get_text(),
    }
    expected = {
        "tag_selector": "h1",
        "id_selector": "section",
        "class_selector": "decision",
        "compound_selector": "decision",
        "comma_document_order": "h1",
        "comma_miss_then_hit": "decision",
        "select_all_count": 2,
        "descendant_combinator_rejected": True,
        "attribute_selector_rejected": True,
        "pseudo_class_rejected": True,
        "lang_attribute": "en",
        "find_by_id": "section",
        "find_by_id_absent": None,
        "h1_count": 1,
        "all_elements_include_void": True,
        "img_alt": "Margin chart",
        "void_element_not_nested": 0,
        "rel_is_token_list": ["noopener", "noreferrer"],
        "class_is_token_list": ["panel", "wide"],
        "absent_attr_list_empty": [],
        "has_attr_true": True,
        "has_attr_false": False,
        "get_text_is_unfiltered": True,
        "ancestors_reach_root": True,
        "scoped_text": "Reject as offered Hidden note",
    }
    print(json.dumps({"observed": observed, "expected": expected}, indent=2))
    return 0 if observed == expected else 1


if __name__ == "__main__":
    sys.exit(main())
