#!/usr/bin/env python3
"""Lexical and structural support audit for branded artifact parity.

Usage:
  python3 parity_audit.py manifest.json rendered.html [--json report.json] [--strict]

Exit codes:
  0  lexical/structural checks passed (warnings may remain)
  1  lexical/structural errors, or warnings under --strict
  2  invalid manifest, dependency failure, or parse/runtime failure

This script checks parsed content-text presence, forbidden additions, evidence
references, protected qualifiers, HTML structure, inline-hidden text, image alt
attributes, ID references, external-link safety, and limited source-level CSS
heuristics. It does NOT evaluate computed CSS, pixels, clipping, off-canvas
positioning, responsive visibility, PDF visibility, print visibility, semantic
force, or claim/qualifier association unless a scoped selector is supplied.

HTML parsing and selector resolution run on the standard library. The selector
grammar is tag, `#id`, `.class`, a compound of those, and a comma-separated list.
Anything outside it exits 2 as a configuration error rather than reporting the
element missing from the artifact.

A successful run never authorizes release. Semantic review and rendered
cross-format visual inspection remain mandatory.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from html_dom import Node, SelectorError, parse_html  # noqa: E402

SUPPORTED_MANIFEST_MAJOR = "1"
ALLOWED_KEYS = {"manifestVersion", "artifactId", "decisionJob", "requiredPhrases", "forbiddenPhrases", "requiredEvidenceReferences", "protectedClaims", "requiredSelectors", "requiredViews"}
LIST_KEYS = {"requiredPhrases", "forbiddenPhrases", "requiredEvidenceReferences", "protectedClaims", "requiredSelectors", "requiredViews"}
NON_CONTENT_TAGS = {"script", "style", "template", "noscript"}
ARIA_IDREF_ATTRS = ("aria-labelledby", "aria-describedby", "aria-controls", "aria-owns")
INLINE_HIDDEN = re.compile(r"(?:display\s*:\s*none|visibility\s*:\s*hidden|opacity\s*:\s*0(?:[;\s]|$)|font-size\s*:\s*0(?:px|rem|em|pt|%|[;\s]))", re.I)
PRINT_QUERY = re.compile(r"@media\s*(?:print|[^\{]*\bprint\b)", re.I)
RESPONSIVE_QUERY = re.compile(r"@media\s*[^\{]*(?:max-width|min-width|width\s*[<>]=?)", re.I)


class ManifestError(ValueError):
    pass


def norm(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().casefold()


def phrase(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return str(value.get("text", ""))
    return str(value)


def inline_hidden(tag: Any) -> bool:
    attrs = getattr(tag, "attrs", None) or {}
    return bool("hidden" in attrs or attrs.get("aria-hidden") == "true" or INLINE_HIDDEN.search(str(attrs.get("style", ""))))


def content_text(node: Node, exclude_inline_hidden: bool) -> str:
    """Readable text under a node, in document order.

    Skipping a hidden subtree during the walk replaces the earlier
    remove-the-nodes-then-serialize pass. Same answer, and a scoped claim now
    reads its own container instead of a reparsed serialization of it.
    """
    parts: list[str] = []

    def walk(current: Node) -> None:
        for child in current.children:
            if child.tag == "#text":
                value = child.text.strip()
                if value:
                    parts.append(value)
                continue
            if child.tag in NON_CONTENT_TAGS:
                continue
            if exclude_inline_hidden and inline_hidden(child):
                continue
            walk(child)

    walk(node)
    return " ".join(parts)


def parse_hex(value: str) -> tuple[int, int, int] | None:
    match = re.fullmatch(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})", value.strip())
    if not match:
        return None
    raw = match.group(1)
    if len(raw) == 3:
        raw = "".join(ch * 2 for ch in raw)
    return tuple(int(raw[i : i + 2], 16) for i in (0, 2, 4))


def luminance(rgb: tuple[int, int, int]) -> float:
    def channel(v: int) -> float:
        x = v / 255.0
        return x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    l1, l2 = sorted((luminance(a), luminance(b)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def add(result: dict[str, Any], level: str, code: str, detail: str) -> None:
    result[level].append({"code": code, "detail": detail})


def validate_manifest(manifest: Any) -> dict[str, Any]:
    if not isinstance(manifest, dict):
        raise ManifestError("Manifest root must be an object")
    version = manifest.get("manifestVersion")
    if not isinstance(version, str) or not version:
        raise ManifestError("manifestVersion is required and must be a string")
    if version.split(".", 1)[0] != SUPPORTED_MANIFEST_MAJOR:
        raise ManifestError(f"Unsupported manifestVersion {version!r}; supported major version is {SUPPORTED_MANIFEST_MAJOR}")
    unknown = sorted(set(manifest) - ALLOWED_KEYS)
    if unknown:
        raise ManifestError("Unknown manifest keys: " + ", ".join(unknown))
    for key in ("artifactId", "decisionJob"):
        if key in manifest and not isinstance(manifest[key], str):
            raise ManifestError(f"{key} must be a string")
    for key in LIST_KEYS:
        if key in manifest and not isinstance(manifest[key], list):
            raise ManifestError(f"{key} must be an array")
    for key in ("requiredPhrases", "forbiddenPhrases", "requiredEvidenceReferences"):
        for index, item in enumerate(manifest.get(key, [])):
            if not isinstance(item, (str, dict)):
                raise ManifestError(f"{key}[{index}] must be a string or object with text")
            if isinstance(item, dict):
                if set(item) - {"text"}:
                    raise ManifestError(f"{key}[{index}] has unknown keys")
                if not isinstance(item.get("text"), str) or not item["text"].strip():
                    raise ManifestError(f"{key}[{index}].text must be a nonempty string")
    for key in ("requiredSelectors", "requiredViews"):
        for index, item in enumerate(manifest.get(key, [])):
            if not isinstance(item, str) or not item.strip():
                raise ManifestError(f"{key}[{index}] must be a nonempty string")
    claim_ids: set[str] = set()
    allowed_claim_keys = {"id", "text", "requiredQualifiers", "selector"}
    for index, item in enumerate(manifest.get("protectedClaims", [])):
        if not isinstance(item, dict):
            raise ManifestError(f"protectedClaims[{index}] must be an object")
        unknown_claim_keys = sorted(set(item) - allowed_claim_keys)
        if unknown_claim_keys:
            raise ManifestError(f"protectedClaims[{index}] has unknown keys: {', '.join(unknown_claim_keys)}")
        claim_id = item.get("id")
        if not isinstance(claim_id, str) or not claim_id.strip():
            raise ManifestError(f"protectedClaims[{index}].id is required")
        if claim_id in claim_ids:
            raise ManifestError(f"Duplicate protected claim id: {claim_id}")
        claim_ids.add(claim_id)
        if not isinstance(item.get("text"), str) or not item["text"].strip():
            raise ManifestError(f"protectedClaims[{index}].text is required")
        qualifiers = item.get("requiredQualifiers", [])
        if not isinstance(qualifiers, list) or not all(isinstance(v, str) and v.strip() for v in qualifiers):
            raise ManifestError(f"protectedClaims[{index}].requiredQualifiers must be an array of nonempty strings")
        if "selector" in item and (not isinstance(item["selector"], str) or not item["selector"].strip()):
            raise ManifestError(f"protectedClaims[{index}].selector must be a nonempty string")
    return manifest


def audit(manifest: dict[str, Any], html_path: Path) -> dict[str, Any]:
    html = html_path.read_text(encoding="utf-8", errors="replace")
    soup = parse_html(html)
    all_text = content_text(soup, exclude_inline_hidden=False)
    lexical_text = content_text(soup, exclude_inline_hidden=True)
    nall, nlex = norm(all_text), norm(lexical_text)
    result: dict[str, Any] = {"artifact": str(html_path), "manifestVersion": manifest.get("manifestVersion"), "auditScope": "lexical parsed-content and source-structure support only", "errors": [], "warnings": [], "passedChecks": []}

    for item in manifest.get("requiredPhrases", []):
        value = phrase(item)
        if not value:
            continue
        if norm(value) in nlex:
            result["passedChecks"].append({"code": "REQUIRED_TEXT_LEXICALLY_PRESENT", "detail": value})
        elif norm(value) in nall:
            add(result, "errors", "REQUIRED_TEXT_ONLY_INLINE_HIDDEN", value)
        else:
            add(result, "errors", "REQUIRED_TEXT_MISSING", value)

    for item in manifest.get("forbiddenPhrases", []):
        value = phrase(item)
        if value and norm(value) in nall:
            add(result, "errors", "FORBIDDEN_TEXT_PRESENT", value)

    for item in manifest.get("requiredEvidenceReferences", []):
        value = phrase(item)
        if value and norm(value) not in nlex:
            add(result, "errors", "EVIDENCE_REFERENCE_ONLY_INLINE_HIDDEN" if norm(value) in nall else "EVIDENCE_REFERENCE_MISSING", value)

    for item in manifest.get("protectedClaims", []):
        claim_id, claim_text = str(item["id"]), str(item["text"])
        qualifiers = [str(v) for v in item.get("requiredQualifiers", [])]
        selector = item.get("selector")
        scoped_all = nall
        if selector:
            container = soup.select_one(selector)
            if container is None:
                add(result, "errors", "PROTECTED_CLAIM_SELECTOR_MISSING", f"{claim_id}: {selector}")
                continue
            scoped_all = norm(content_text(container, exclude_inline_hidden=False))
            ancestor_inline_hidden = any(inline_hidden(node) for node in [container, *list(container.ancestors())])
            scoped = "" if ancestor_inline_hidden else norm(content_text(container, exclude_inline_hidden=True))
        else:
            scoped = nlex
            if qualifiers:
                add(result, "warnings", "CLAIM_ASSOCIATION_MANUAL_REVIEW", f"{claim_id}: qualifiers checked globally because no selector was supplied")
        if norm(claim_text) not in scoped:
            code = "PROTECTED_CLAIM_ONLY_INLINE_HIDDEN" if norm(claim_text) in scoped_all else "PROTECTED_CLAIM_MISSING"
            add(result, "errors", code, f"{claim_id}: {claim_text}")
        for qualifier in qualifiers:
            if norm(qualifier) not in scoped:
                code = "CLAIM_QUALIFIER_ONLY_INLINE_HIDDEN" if norm(qualifier) in scoped_all else "CLAIM_QUALIFIER_MISSING"
                add(result, "errors", code, f"{claim_id}: {qualifier}")

    for selector in manifest.get("requiredSelectors", ["main", "h1"]):
        if not soup.select_one(selector):
            add(result, "errors", "REQUIRED_SELECTOR_MISSING", selector)

    html_tag = soup.find_tag("html")
    if html_tag is None or not str(html_tag.get("lang", "")).strip():
        add(result, "errors", "HTML_LANG_MISSING", "html[lang] is required")
    h1s = soup.find_all("h1")
    if len(h1s) != 1 or not h1s[0].get_text(" ", strip=True):
        add(result, "errors", "H1_INVALID", f"Expected one nonempty h1; found {len(h1s)}")
    if soup.find_tag("main") is None:
        add(result, "errors", "MAIN_LANDMARK_MISSING", "A main landmark is required")

    for image in soup.find_all("img"):
        if image.get("alt") is None:
            add(result, "errors", "IMAGE_ALT_MISSING", str(image.get("src", ""))[:120])

    id_values = [str(tag.get("id")) for tag in soup.find_all() if tag.has_attr("id")]
    if any(not v.strip() for v in id_values):
        add(result, "errors", "EMPTY_ID", "One or more empty id attributes found")
    for duplicate, count in Counter(id_values).items():
        if duplicate and count > 1:
            add(result, "errors", "DUPLICATE_ID", duplicate)

    for tag in soup.find_all():
        for attr in ARIA_IDREF_ATTRS:
            if tag.has_attr(attr):
                for target in str(tag.get(attr, "")).split():
                    if soup.find_by_id(target) is None:
                        add(result, "errors", "ARIA_TARGET_MISSING", f"{attr}: {target}")
        style = str(tag.get("style", ""))
        if inline_hidden(tag) and norm(tag.get_text(" ", strip=True)):
            add(result, "warnings", "INLINE_HIDDEN_TEXT", f"<{tag.name}> {tag.get_text(' ', strip=True)[:160]}")
        styles = {key.strip().lower(): value.strip() for key, value in re.findall(r"([\w-]+)\s*:\s*([^;]+)", style)}
        fg = parse_hex(styles.get("color", ""))
        bg = parse_hex(styles.get("background-color", "") or styles.get("background", ""))
        if fg and bg:
            ratio = contrast(fg, bg)
            if ratio < 4.5:
                add(result, "warnings", "INLINE_CONTRAST_HEURISTIC_LOW", f"<{tag.name}> same-element inline hex contrast {ratio:.2f}:1; computed-style review required")

    for link in soup.find_all("a"):
        href = str(link.get("href", ""))
        if href.startswith(("http://", "https://")):
            rel = set(link.attr_list("rel"))
            if link.get("target") != "_blank" or not {"noopener", "noreferrer"}.issubset(rel):
                add(result, "warnings", "EXTERNAL_LINK_SAFETY", href)

    if not PRINT_QUERY.search(html):
        add(result, "warnings", "PRINT_QUERY_ABSENT", "No print media query text found")
    if not RESPONSIVE_QUERY.search(html):
        add(result, "warnings", "RESPONSIVE_QUERY_ABSENT", "No width-based media query text found")
    if manifest.get("requiredViews"):
        add(result, "warnings", "RENDERED_VISUAL_REVIEW_REQUIRED", "Lexical/structural checks cannot prove visibility. Inspect: " + ", ".join(map(str, manifest["requiredViews"])))

    errors, warnings = len(result["errors"]), len(result["warnings"])
    result["summary"] = {"errorCount": errors, "warningCount": warnings, "lexicalStructuralPass": errors == 0, "releasePass": False, "releaseNote": "Release requires semantic association review and rendered cross-format visual evidence. All warnings require disposition in the release note."}
    return result


def failure_report(message: str) -> dict[str, Any]:
    return {"errors": [{"code": "AUDIT_CONFIGURATION_ERROR", "detail": message}], "warnings": [], "passedChecks": [], "summary": {"errorCount": 1, "warningCount": 0, "lexicalStructuralPass": False, "releasePass": False, "releaseNote": "Audit did not run successfully."}}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--json", dest="json_path", type=Path)
    parser.add_argument("--strict", action="store_true", help="Return exit 1 when any warning remains")
    args = parser.parse_args()
    try:
        manifest = validate_manifest(json.loads(args.manifest.read_text(encoding="utf-8")))
        result = audit(manifest, args.artifact)
        exit_code = 0 if result["summary"]["lexicalStructuralPass"] else 1
        if args.strict and result["summary"]["warningCount"]:
            exit_code = 1
    except Exception as exc:
        result, exit_code = failure_report(str(exc)), 2
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    if args.json_path:
        args.json_path.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
