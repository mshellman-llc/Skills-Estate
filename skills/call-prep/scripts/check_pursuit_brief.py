#!/usr/bin/env python3
"""Gate for call-prep briefs.

Validates a rolling Pursuit Brief (default) or an Upcoming Call Brief
(--mode call), and verifies human-marker preservation between two versions
of a Pursuit Brief (--before/--after).

Pursuit checks:
  1. Every required section is present as a markdown heading.
  2. Every entry in the assumptions section is a list item labeled as an
     assumption (starts with "Assumption", optionally with an ID).
  3. A last-updated provenance line exists: "Last updated: YYYY-MM-DD ...".
  4. The recommended-calls section names at least one call as a subheading,
     and every call carries Purpose, Desired outcome, and Prerequisites lines.
  5. No unresolved template placeholder: TBD, TKTK, or {{ }}.
  6. No em dash anywhere.

Call checks (--mode call):
  Sections for objective, attendees, run of show, agenda, questions, and
  follow-up, plus an explicit mention of the Pursuit Brief it relates to.
  The placeholder and em dash rules apply here too.

Idempotency check:
  --before OLD --after NEW verifies that every <!-- human --> ... <!-- /human -->
  block in OLD survives byte-identical in NEW, and that markers pair up.

Usage:
  check_pursuit_brief.py brief.md
  check_pursuit_brief.py --mode call call-brief.md
  check_pursuit_brief.py --before old.md --after new.md
  check_pursuit_brief.py --before old.md --after new.md new.md   # both checks

Exit 0 on pass, 1 on any failure, 2 on unusable input.
Stdlib only, by design: the gate must run on any surface.
"""

import argparse
import re
import sys

EM_DASH = "\u2014"  # written as an escape so this gate passes its own scan

HEADING = re.compile(r"^(#{1,6})\s+(.*)$")

# label shown in findings, keywords matched against lowercased heading text
PURSUIT_SECTIONS = (
    ("client and opportunity context", ("context",)),
    ("situation", ("situation",)),
    ("desired business outcomes", ("outcome",)),
    ("confirmed facts", ("confirmed fact", "what we know")),
    ("assumptions", ("assumption",)),
    ("important unknowns", ("unknown",)),
    ("stakeholders", ("stakeholder",)),
    ("risks and warning signs", ("risk",)),
    ("qualification status", ("qualification",)),
    ("recommended calls", ("recommended call", "call plan")),
    ("immediate next steps", ("next step",)),
    ("decisions needed", ("decision",)),
)

CALL_SECTIONS = (
    ("call objective", ("objective",)),
    ("attendees and roles", ("attendee",)),
    ("run of show", ("run of show",)),
    ("agenda", ("agenda",)),
    ("questions", ("question",)),
    ("follow-up plan", ("follow",)),
)

PROVENANCE = re.compile(r"(?im)^[*_\s]*last updated[*_\s]*:.*\d{4}-\d{2}-\d{2}")
PLACEHOLDERS = (
    (re.compile(r"\bTBD\b"), "TBD"),
    (re.compile(r"\bTKTK\b", re.I), "TKTK"),
    (re.compile(r"\{\{.*?\}\}"), "{{ }} slot"),
)
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+(.*)$")
ASSUMPTION_ENTRY = re.compile(r"(?i)^[*_`\s]*assumption\b")
HUMAN_BLOCK = re.compile(r"<!--\s*human\s*-->(.*?)<!--\s*/human\s*-->", re.S)
HUMAN_MARKER = re.compile(r"<!--\s*/?human\s*-->")


def headings(text):
    out = []
    for i, line in enumerate(text.splitlines()):
        m = HEADING.match(line)
        if m:
            out.append((i, len(m.group(1)), m.group(2).strip().lower()))
    return out


def find_section(text, keywords):
    """Return the body lines of the first section whose heading matches."""
    lines = text.splitlines()
    heads = headings(text)
    for idx, (line_no, level, title) in enumerate(heads):
        if any(k in title for k in keywords):
            end = len(lines)
            for next_no, next_level, _ in heads[idx + 1:]:
                if next_level <= level:
                    end = next_no
                    break
            return lines[line_no + 1:end], level
    return None, None


def check_sections(text, sections, problems, kind):
    for label, keywords in sections:
        body, _ = find_section(text, keywords)
        if body is None:
            problems.append(
                "missing section: no heading matches '{}' ({} brief requires it)".format(label, kind)
            )


def check_assumptions(text, problems):
    body, _ = find_section(text, ("assumption",))
    if body is None:
        return  # the missing-section finding already covers it
    entries = [m.group(1) for ln in body if (m := LIST_ITEM.match(ln))]
    if not entries:
        problems.append("assumptions section has no list entries; every assumption is a labeled bullet")
        return
    for entry in entries:
        if not ASSUMPTION_ENTRY.match(entry):
            problems.append(
                "assumptions entry not labeled as an assumption: '{}'".format(entry[:70])
            )


def check_recommended_calls(text, problems):
    body, level = find_section(text, ("recommended call", "call plan"))
    if body is None:
        return
    # Each recommended call is a subheading deeper than the section heading.
    blocks = []
    current = None
    for ln in body:
        m = HEADING.match(ln)
        if m and len(m.group(1)) > level:
            if current is not None:
                blocks.append(current)
            current = [ln]
        elif current is not None:
            current.append(ln)
    if current is not None:
        blocks.append(current)
    if not blocks:
        problems.append(
            "recommended-calls section names no calls; each call is a subheading "
            "with Purpose, Desired outcome, and Prerequisites lines"
        )
        return
    for block in blocks:
        title = HEADING.match(block[0]).group(2).strip()
        flat = re.sub(r"[*_`]", "", "\n".join(block[1:])).lower()
        if not re.search(r"^\s*purpose\s*:", flat, re.M):
            problems.append("recommended call '{}': no Purpose line".format(title[:60]))
        if not re.search(r"^\s*(desired )?outcome\s*:", flat, re.M):
            problems.append("recommended call '{}': no Desired outcome line".format(title[:60]))
        if not re.search(r"^\s*prerequisites?\s*:", flat, re.M):
            problems.append("recommended call '{}': no Prerequisites line".format(title[:60]))


def check_placeholders(text, problems):
    for i, ln in enumerate(text.splitlines(), 1):
        for pattern, name in PLACEHOLDERS:
            if pattern.search(ln):
                problems.append(
                    "unresolved placeholder ({}) on line {}: {}".format(name, i, ln.strip()[:70])
                )


def check_em_dash(text, problems):
    for i, ln in enumerate(text.splitlines(), 1):
        if EM_DASH in ln:
            problems.append("em dash on line {}: {}".format(i, ln.strip()[:70]))


def check_provenance(text, problems):
    if not PROVENANCE.search(text):
        problems.append(
            "no last-updated provenance line; expected 'Last updated: YYYY-MM-DD by <who>, from <sources>'"
        )


def check_pursuit_link(text, problems):
    if "pursuit brief" not in text.lower():
        problems.append(
            "no explicit relationship to the rolling Pursuit Brief; name the pursuit "
            "brief file and which recommended call this one is"
        )


def check_human_markers(before, after, problems):
    for label, text in (("before", before), ("after", after)):
        stripped = HUMAN_BLOCK.sub("", text)
        if HUMAN_MARKER.search(stripped):
            problems.append("{} file has an unpaired human marker".format(label))
    for m in HUMAN_BLOCK.finditer(before):
        block = m.group(0)
        if block not in after:
            snippet = " ".join(m.group(1).split())[:70]
            problems.append(
                "human-authored block was rewritten or dropped: '{}'. Updates must "
                "never touch content between <!-- human --> and <!-- /human -->".format(snippet)
            )


def read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError as exc:
        print("FAIL: cannot read {}: {}".format(path, exc))
        raise SystemExit(2)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Gate for call-prep briefs.")
    ap.add_argument("file", nargs="?", help="brief to validate")
    ap.add_argument("--mode", choices=("pursuit", "call"), default="pursuit")
    ap.add_argument("--before", help="prior version, for the human-marker check")
    ap.add_argument("--after", help="updated version, for the human-marker check")
    a = ap.parse_args(argv)

    if bool(a.before) != bool(a.after):
        print("FAIL: --before and --after must be given together")
        return 2
    if not a.file and not a.before:
        ap.print_usage()
        return 2

    problems = []
    checked = []

    if a.file:
        text = read(a.file)
        if a.mode == "pursuit":
            check_sections(text, PURSUIT_SECTIONS, problems, "pursuit")
            check_assumptions(text, problems)
            check_provenance(text, problems)
            check_recommended_calls(text, problems)
        else:
            check_sections(text, CALL_SECTIONS, problems, "call")
            check_pursuit_link(text, problems)
        check_placeholders(text, problems)
        check_em_dash(text, problems)
        checked.append(a.file)

    if a.before:
        check_human_markers(read(a.before), read(a.after), problems)
        checked.append("{} -> {}".format(a.before, a.after))

    if problems:
        for p in problems:
            print("FAIL: {}".format(p))
        print("{}: {} fail".format("; ".join(checked), len(problems)))
        return 1
    print("{}: 0 fail.".format("; ".join(checked)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
