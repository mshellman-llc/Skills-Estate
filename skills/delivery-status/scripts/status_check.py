#!/usr/bin/env python3
"""Deterministic gate for an Aleysian weekly status report.

Checks, in order:
  1. Period stated in the header (Period: YYYY-MM-DD to YYYY-MM-DD).
  2. Every stable ID referenced in the report exists in the referenced log
     files (R-/A-/I-/D- in the RAID log, where D is a dependency; DEC- in the decision log).
  3. A scope-drift section is present and is either "None observed" or
     contains candidate blocks, each with at least one Evidence: line.
  4. An hours-and-burn section is present and names a Source: or a named gap.
  5. No unfilled placeholders remain ({{...}}, TBD, TODO, [FILL...]).

Exit 0 on pass, 1 on failure, 2 on usage or read error. Stdlib only.

Usage:
  python3 status_check.py STATUS.md --raid-log RAID.md --decision-log DECISIONS.md
"""

import argparse
import re
import sys

ID_RE = re.compile(r"\b(DEC|R|A|I|D)-(\d{3})\b")
PERIOD_RE = re.compile(r"^Period:\s*\d{4}-\d{2}-\d{2}\s+to\s+\d{4}-\d{2}-\d{2}\s*$",
                       re.MULTILINE)
PLACEHOLDER_RES = [
    re.compile(r"\{\{[^}]*\}\}"),
    re.compile(r"\bTBD\b"),
    re.compile(r"\bTODO\b"),
    re.compile(r"\[FILL[^\]]*\]"),
]
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
CANDIDATE_RE = re.compile(r"^#{2,6}\s*Candidate\s*:", re.IGNORECASE)
EVIDENCE_RE = re.compile(r"^\s*(?:[-*]\s*)?Evidence:\s*\S")

RAID_PREFIXES = {"R", "A", "I", "D"}


def _sections(text):
    """Yield (level, title_lower, body_lines) for each markdown heading."""
    lines = text.splitlines()
    out = []
    current = None
    for line in lines:
        m = HEADING_RE.match(line)
        if m:
            if current:
                out.append(current)
            current = (len(m.group(1)), m.group(2).strip().lower(), [])
        elif current:
            current[2].append(line)
    if current:
        out.append(current)
    return out


def _find_section(sections, needle):
    """Return the body of the first section whose title contains needle,
    including the bodies of deeper subsections until a heading of the same
    or shallower level."""
    for i, (level, title, body) in enumerate(sections):
        if needle in title:
            merged = list(body)
            for j in range(i + 1, len(sections)):
                sub_level, sub_title, sub_body = sections[j]
                if sub_level <= level:
                    break
                merged.append("#" * sub_level + " " + sub_title)
                merged.extend(sub_body)
            return merged
    return None


def check(report_text, raid_text, decision_text):
    """Return a list of failure strings. Empty list means pass."""
    failures = []
    counts = {"ids_checked": 0, "candidates": 0}

    # 1. Period stated.
    if not PERIOD_RE.search(report_text):
        failures.append(
            "period: no 'Period: YYYY-MM-DD to YYYY-MM-DD' line in the report")

    # 2. Stable ID references resolve against the logs.
    raid_ids = {f"{p}-{n}" for p, n in ID_RE.findall(raid_text or "")
                if p in RAID_PREFIXES}
    decision_ids = {f"{p}-{n}" for p, n in ID_RE.findall(decision_text or "")
                    if p == "DEC"}
    for prefix, num in ID_RE.findall(report_text):
        ref = f"{prefix}-{num}"
        counts["ids_checked"] += 1
        if prefix == "DEC":
            if ref not in decision_ids:
                failures.append(f"id: {ref} referenced but not in decision log")
        else:
            if ref not in raid_ids:
                failures.append(f"id: {ref} referenced but not in RAID log")

    sections = _sections(report_text)

    # 3. Scope-drift section.
    drift = _find_section(sections, "scope drift")
    if drift is None:
        failures.append("scope-drift: section missing (required every period, "
                        "even when the answer is 'None observed')")
    else:
        drift_text = "\n".join(drift)
        candidate_blocks = _split_candidates(drift)
        counts["candidates"] = len(candidate_blocks)
        if candidate_blocks:
            for title, block in candidate_blocks:
                if not any(EVIDENCE_RE.match(line) for line in block):
                    failures.append(
                        f"scope-drift: candidate '{title}' has no Evidence: line")
        elif "none observed" not in drift_text.lower():
            failures.append("scope-drift: section is neither 'None observed' "
                            "nor a set of candidate blocks")

    # 4. Hours and burn carries a source or a named gap.
    burn = _find_section(sections, "hours and burn")
    if burn is None:
        burn = _find_section(sections, "burn")
    if burn is None:
        failures.append("burn: no hours-and-burn section found")
    else:
        burn_text = "\n".join(burn).lower()
        if "source:" not in burn_text and "named gap:" not in burn_text:
            failures.append("burn: section names neither a Source: nor a "
                            "Named gap: (figures may not be estimated silently)")

    # 5. Unfilled placeholders.
    for rx in PLACEHOLDER_RES:
        for m in rx.finditer(report_text):
            failures.append(f"placeholder: unfilled placeholder {m.group(0)!r}")

    return failures, counts


def _split_candidates(section_lines):
    """Split a scope-drift section body into (title, lines) candidate blocks."""
    blocks = []
    current = None
    for line in section_lines:
        if CANDIDATE_RE.match(line):
            if current:
                blocks.append(current)
            title = line.split(":", 1)[1].strip() if ":" in line else line.strip()
            current = (title, [])
        elif current:
            current[1].append(line)
    if current:
        blocks.append(current)
    return blocks


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("report", help="the status report markdown file")
    ap.add_argument("--raid-log", required=True, help="path to the RAID log")
    ap.add_argument("--decision-log", required=True,
                    help="path to the decision log")
    args = ap.parse_args(argv)

    try:
        report_text = open(args.report, encoding="utf-8").read()
        raid_text = open(args.raid_log, encoding="utf-8").read()
        decision_text = open(args.decision_log, encoding="utf-8").read()
    except OSError as exc:
        print(f"status_check: cannot read input: {exc}", file=sys.stderr)
        return 2

    failures, counts = check(report_text, raid_text, decision_text)

    print(f"status_check: {counts['ids_checked']} stable ID references checked, "
          f"{counts['candidates']} scope-drift candidates, "
          f"{len(failures)} failures")
    for f in failures:
        print(f"  FAIL {f}")
    if failures:
        return 1
    print("  PASS all checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
