#!/usr/bin/env python3
"""Gate for the Estate sales-to-delivery handoff manifest.

Usage:
    python3 check_handoff.py MANIFEST.json

Exit codes:
    0  pass
    1  gate failure (findings printed, one per line)
    2  usage or parse error

What it enforces (structure and traceability, not truth):
- Sections 01 through 12 all present, no extras, none blank. A section passes
  by content (non-empty content list plus sources, each with name and date) or
  by gaps (each with question, owner, resolve_by, gate_blocked).
- At moment "brief" (the default), section 11 must carry at least one session
  with name, owner, attendees, and output, and section 12 at least one
  criterion with a binary test plus a readiness checklist whose items carry a
  status and an owner. Gaps alone never satisfy 11 or 12 at this moment.
- Scope is non-empty and every item is marked "in" or "out".
- Every promise names where it was said; in_sow true requires the clause,
  in_sow false requires an owner.
- Every contract figure's source references the SOW or the quote (money rule).
- Required stamps: client, engagement, as_of, source_snapshot.sow,
  source_snapshot.quote.
- No em dash anywhere in the file.

Stdlib only. Deterministic. A prose checklist can be skipped; this cannot.
"""

import json
import re
import sys

SECTION_KEYS = [f"{i:02d}" for i in range(1, 13)]
VALID_MOMENTS = ("package", "brief")
EM_DASH = "\u2014"
FIGURE_SOURCE_RE = re.compile(r"(sow|quote|q-\d+)", re.IGNORECASE)
GAP_FIELDS = ("question", "owner", "resolve_by", "gate_blocked")
SESSION_FIELDS = ("name", "owner", "attendees", "output")


def filled(value):
    """Non-empty string, or non-empty list of filled values."""
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return len(value) > 0 and all(filled(v) for v in value)
    return False


def valid_gaps(section):
    gaps = section.get("gaps")
    if not isinstance(gaps, list) or not gaps:
        return False, []
    findings = []
    for i, gap in enumerate(gaps):
        if not isinstance(gap, dict):
            findings.append(f"gap {i} is not an object")
            continue
        for field in GAP_FIELDS:
            if not filled(gap.get(field)):
                findings.append(f"gap {i} missing {field}")
    return not findings, findings


def valid_content(section):
    findings = []
    if not filled(section.get("content")):
        findings.append("content empty")
    sources = section.get("sources")
    if not isinstance(sources, list) or not sources:
        findings.append("no sources")
    else:
        for i, src in enumerate(sources):
            if not isinstance(src, dict) or not filled(src.get("name")) or not filled(src.get("date")):
                findings.append(f"source {i} missing name or date")
    return not findings, findings


def check_section(key, section, findings):
    if not isinstance(section, dict):
        findings.append(f"section {key}: not an object")
        return
    content_ok, content_findings = valid_content(section)
    gaps_ok, gap_findings = valid_gaps(section)
    has_gap_attempt = isinstance(section.get("gaps"), list) and section.get("gaps")
    has_content_attempt = section.get("content") or section.get("sources")
    special_fill = bool(section.get("sessions")) or bool(section.get("criteria"))
    if content_ok or gaps_ok or (special_fill and key in ("11", "12")):
        # A partially broken alternate route still fails.
        if has_gap_attempt and not gaps_ok:
            for f in gap_findings:
                findings.append(f"section {key}: {f}")
        if has_content_attempt and not content_ok and not special_fill:
            for f in content_findings:
                findings.append(f"section {key}: {f}")
        return
    if not has_gap_attempt and not has_content_attempt and not special_fill:
        findings.append(
            f"section {key}: blank (no sourced content and no named gap; "
            f"a blank is a gate failure)"
        )
        return
    for f in content_findings + gap_findings:
        findings.append(f"section {key}: {f}")


def check_section_11(section, moment, findings):
    sessions = section.get("sessions")
    if moment == "package":
        if not (isinstance(sessions, list) and sessions) and not valid_gaps(section)[0]:
            findings.append("section 11: package must seed sessions or carry owned gaps")
        # fall through: any provided sessions still validated below
    else:
        if not isinstance(sessions, list) or not sessions:
            findings.append("section 11: brief requires at least one discovery session (gaps alone do not satisfy it)")
            return
    for i, s in enumerate(sessions or []):
        if not isinstance(s, dict):
            findings.append(f"section 11: session {i} is not an object")
            continue
        for field in SESSION_FIELDS:
            if not filled(s.get(field)):
                findings.append(f"section 11: session {i} missing {field}")


def check_section_12(section, moment, findings):
    criteria = section.get("criteria")
    readiness = section.get("readiness")
    if moment == "package":
        if not (isinstance(criteria, list) and criteria) and not valid_gaps(section)[0]:
            findings.append("section 12: package must seed criteria or carry owned gaps")
    else:
        if not isinstance(criteria, list) or not criteria:
            findings.append("section 12: brief requires at least one definition-of-done criterion (gaps alone do not satisfy it)")
        if not isinstance(readiness, list) or not readiness:
            findings.append("section 12: brief requires the readiness checklist")
    for i, c in enumerate(criteria or []):
        if not isinstance(c, dict) or not filled(c.get("criterion")) or not filled(c.get("binary_test")):
            findings.append(f"section 12: criterion {i} missing criterion or binary_test")
    for i, r in enumerate(readiness or []):
        if not isinstance(r, dict):
            findings.append(f"section 12: readiness item {i} is not an object")
            continue
        if not filled(r.get("item")) or not filled(r.get("owner")):
            findings.append(f"section 12: readiness item {i} missing item or owner")
        if r.get("status") not in ("ready", "blocked", "unknown"):
            findings.append(f"section 12: readiness item {i} status must be ready, blocked, or unknown")


def check(manifest, raw_text):
    findings = []

    def count_em_dashes(node):
        if isinstance(node, str):
            return node.count(EM_DASH)
        if isinstance(node, list):
            return sum(count_em_dashes(v) for v in node)
        if isinstance(node, dict):
            return sum(count_em_dashes(k) + count_em_dashes(v) for k, v in node.items())
        return 0

    # Scan both the decoded values and the raw file, so an escaped em dash
    # cannot slip past the raw scan and a raw dash cannot hide from the parse.
    count = max(count_em_dashes(manifest), raw_text.count(EM_DASH))
    if count:
        findings.append(f"em dash found in manifest ({count} occurrence(s)); the shared writing standard requires reviewing it")

    for field in ("client", "engagement", "as_of"):
        if not filled(manifest.get(field)):
            findings.append(f"stamp missing: {field}")
    snapshot = manifest.get("source_snapshot")
    if not isinstance(snapshot, dict) or not filled(snapshot.get("sow")) or not filled(snapshot.get("quote")):
        findings.append("stamp missing: source_snapshot.sow and source_snapshot.quote are both required")

    moment = manifest.get("moment", "brief")
    if moment not in VALID_MOMENTS:
        findings.append(f"moment must be one of {VALID_MOMENTS}, got {moment!r}")
        moment = "brief"

    sections = manifest.get("sections")
    if not isinstance(sections, dict):
        findings.append("sections missing or not an object")
        sections = {}
    for key in SECTION_KEYS:
        if key not in sections:
            findings.append(f"section {key}: missing (sections are never dropped)")
    for key in sorted(sections):
        if key not in SECTION_KEYS:
            findings.append(f"section {key}: not in the 12-section catalog")
    for key in SECTION_KEYS:
        if key in sections:
            check_section(key, sections[key], findings)
    if isinstance(sections.get("11"), dict):
        check_section_11(sections["11"], moment, findings)
    if isinstance(sections.get("12"), dict):
        check_section_12(sections["12"], moment, findings)

    scope = manifest.get("scope")
    if not isinstance(scope, list) or not scope:
        findings.append("scope: empty (every handoff carries the scope list, each item marked in or out)")
    else:
        for i, item in enumerate(scope):
            if not isinstance(item, dict) or not filled(item.get("item")):
                findings.append(f"scope item {i}: missing item text")
                continue
            if item.get("in_or_out") not in ("in", "out"):
                findings.append(f"scope item {i} ({item.get('item')!r}): in_or_out must be 'in' or 'out'")
            if not filled(item.get("source")):
                findings.append(f"scope item {i} ({item.get('item')!r}): missing source")

    promises = manifest.get("promises", [])
    if not isinstance(promises, list):
        findings.append("promises must be a list")
        promises = []
    for i, p in enumerate(promises):
        if not isinstance(p, dict) or not filled(p.get("text")):
            findings.append(f"promise {i}: missing text")
            continue
        if not filled(p.get("said_where")):
            findings.append(f"promise {i}: missing said_where (every promise is sourced to where it was said)")
        if not isinstance(p.get("in_sow"), bool):
            findings.append(f"promise {i}: in_sow must be true or false")
        elif p["in_sow"] and not filled(p.get("sow_clause")):
            findings.append(f"promise {i}: in_sow true requires sow_clause")
        elif not p["in_sow"] and not filled(p.get("owner")):
            findings.append(f"promise {i}: off-contract promise requires an owner (it is a flagged liability)")

    figures = manifest.get("figures", [])
    if not isinstance(figures, list):
        findings.append("figures must be a list")
        figures = []
    for i, f in enumerate(figures):
        if not isinstance(f, dict) or not filled(f.get("label")) or not filled(str(f.get("value", "")).strip()):
            findings.append(f"figure {i}: missing label or value")
            continue
        src = f.get("source", "")
        if not filled(src) or not FIGURE_SOURCE_RE.search(src):
            findings.append(
                f"figure {i} ({f.get('label')!r}): source must reference the executed SOW or the quote (money rule)"
            )

    counts = {
        "sections": sum(1 for k in SECTION_KEYS if k in sections),
        "scope_items": len(scope) if isinstance(scope, list) else 0,
        "promises": len(promises),
        "figures": len(figures),
        "gaps": sum(
            len(s.get("gaps", [])) for s in sections.values() if isinstance(s, dict)
        ),
    }
    return findings, counts, moment


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip().splitlines()[0])
        print("usage: python3 check_handoff.py MANIFEST.json")
        return 2
    try:
        with open(argv[1], encoding="utf-8") as fh:
            raw = fh.read()
        manifest = json.loads(raw)
    except OSError as exc:
        print(f"cannot read manifest: {exc}")
        return 2
    except json.JSONDecodeError as exc:
        print(f"manifest is not valid JSON: {exc}")
        return 2
    if not isinstance(manifest, dict):
        print("manifest root must be a JSON object")
        return 2

    findings, counts, moment = check(manifest, raw)
    summary = (
        f"moment={moment} sections={counts['sections']}/12 "
        f"scope_items={counts['scope_items']} promises={counts['promises']} "
        f"figures={counts['figures']} gaps={counts['gaps']}"
    )
    if findings:
        for f in findings:
            print(f"FAIL: {f}")
        print(f"RESULT: FAIL ({len(findings)} finding(s)) {summary}")
        return 1
    print(f"RESULT: PASS {summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
