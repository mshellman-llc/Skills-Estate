#!/usr/bin/env python3
"""Gate for the Estate Project Charter (delivery-kickoff).

Validates a charter markdown document before any human reads or signs it:

  required-sections   every required section heading is present
  scope-stamp         the scope baseline opens with a source stamp (SOW id + as-of date)
  raci-filled         the RACI table exists, every cell is filled, one Accountable per row
  raci-coverage       every role in the team table appears in the RACI
  placeholders        no unfilled template tokens remain ({{...}}, TBD, TODO, ...)
  em-dash             no em dash characters anywhere (writing-integrity owns writing review; this is the
                      one character-level tell cheap enough to block here)

Exit code 0 on pass, 1 on any failure, 2 on usage or read error.
Stdlib only. Usage: python3 charter_check.py CHARTER.md
"""

import re
import sys

REQUIRED_SECTIONS = [
    "Engagement summary",
    "Scope baseline",
    "Delivery model",
    "Team and allocations",
    "RACI",
    "Governance and cadence",
    "Phase plan and milestones",
    "Assumptions and open items",
    "Sign-off",
]

SCOPE_STAMP_RE = re.compile(
    r"^\s*Source:\s*SOW[\s-]*[A-Za-z0-9][A-Za-z0-9._-]*\s*,\s*as of\s+\d{4}-\d{2}-\d{2}",
    re.IGNORECASE | re.MULTILINE,
)

PLACEHOLDER_PATTERNS = [
    (re.compile(r"\{\{[^}]*\}\}"), "unfilled {{token}}"),
    (re.compile(r"\bTBD\b", re.IGNORECASE), "TBD"),
    (re.compile(r"\bTODO\b", re.IGNORECASE), "TODO"),
    (re.compile(r"\bFIXME\b", re.IGNORECASE), "FIXME"),
    (re.compile(r"<\s*fill[^>]*>", re.IGNORECASE), "<fill> tag"),
    (re.compile(r"\[\s*FILL[^\]]*\]", re.IGNORECASE), "[FILL] token"),
    (re.compile(r"\?\?\?"), "??? marker"),
    (re.compile(r"\bLOREM\b", re.IGNORECASE), "lorem filler"),
]

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")


def normalize_heading(text):
    text = re.sub(r"^[\d.]+[.)]?\s+", "", text.strip())
    return re.sub(r"\s+", " ", text).lower().rstrip(":")


def split_sections(text):
    """Return list of (normalized_heading, level, body_text)."""
    lines = text.splitlines()
    sections = []
    current = None
    for line in lines:
        m = HEADING_RE.match(line)
        if m:
            if current:
                sections.append(current)
            current = [normalize_heading(m.group(2)), len(m.group(1)), []]
        elif current:
            current[2].append(line)
    if current:
        sections.append(current)
    return [(h, lvl, "\n".join(body)) for h, lvl, body in sections]


def section_body(sections, name, include_subsections=True):
    """Body of the named section, optionally including deeper subsections."""
    target = name.lower()
    out = []
    capture_level = None
    for heading, level, body in sections:
        if capture_level is not None:
            if level <= capture_level:
                capture_level = None
            elif include_subsections:
                out.append(body)
                continue
        if heading == target:
            capture_level = level
            out.append(body)
    return "\n".join(out) if out else None


def parse_tables(text):
    """Return list of tables; each table is (header_cells, [row_cells])."""
    tables = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("|") and i + 1 < len(lines) and re.match(
            r"^\|[\s:|-]+\|$", lines[i + 1].strip()
        ):
            header = [c.strip() for c in line.strip("|").split("|")]
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                rows.append([c.strip() for c in lines[j].strip().strip("|").split("|")])
                j += 1
            tables.append((header, rows))
            i = j
        else:
            i += 1
    return tables


def check_required_sections(sections, failures):
    found = {h for h, _, _ in sections}
    missing = [s for s in REQUIRED_SECTIONS if s.lower() not in found]
    if missing:
        failures.append(
            "required-sections: missing section(s): " + ", ".join(missing)
        )
        return False
    return True


def check_scope_stamp(sections, failures):
    body = section_body(sections, "Scope baseline")
    if body is None:
        failures.append("scope-stamp: no scope baseline section to stamp")
        return False
    if not SCOPE_STAMP_RE.search(body):
        failures.append(
            "scope-stamp: scope baseline lacks a source stamp line "
            "'Source: SOW <id>, as of YYYY-MM-DD'"
        )
        return False
    return True


BAD_CELL_RE = re.compile(r"^(?:|-|\?+|n/?a)$", re.IGNORECASE)


def find_raci_table(sections):
    body = section_body(sections, "RACI")
    if body is None:
        return None
    for header, rows in parse_tables(body):
        lower = [h.lower() for h in header]
        if all(
            any(col in h for h in lower)
            for col in ("responsible", "accountable", "consulted", "informed")
        ):
            return header, rows
    return None


def check_raci_filled(sections, failures):
    table = find_raci_table(sections)
    if table is None:
        failures.append(
            "raci-filled: no RACI table with Responsible/Accountable/"
            "Consulted/Informed columns found"
        )
        return False
    header, rows = table
    if not rows:
        failures.append("raci-filled: RACI table has no activity rows")
        return False
    lower = [h.lower() for h in header]
    acc_idx = next(i for i, h in enumerate(lower) if "accountable" in h)
    ok = True
    for n, row in enumerate(rows, start=1):
        cells = row + [""] * (len(header) - len(row))
        for i, cell in enumerate(cells[: len(header)]):
            if BAD_CELL_RE.match(cell):
                failures.append(
                    "raci-filled: row %d ('%s') has an unassigned '%s' cell"
                    % (n, cells[0] or "?", header[i])
                )
                ok = False
        acc = cells[acc_idx]
        if acc and (
            "," in acc
            or "/" in acc
            or re.search(r"\band\b|&", acc, re.IGNORECASE)
        ):
            failures.append(
                "raci-filled: row %d ('%s') names more than one Accountable "
                "('%s'); exactly one required" % (n, cells[0] or "?", acc)
            )
            ok = False
    return ok


def check_raci_coverage(sections, failures):
    table = find_raci_table(sections)
    team_body = section_body(sections, "Team and allocations")
    if table is None or team_body is None:
        failures.append(
            "raci-coverage: cannot check role coverage without both the "
            "team table and the RACI table"
        )
        return False
    team_tables = parse_tables(team_body)
    roles = []
    for header, rows in team_tables:
        if header and "role" in header[0].lower():
            for row in rows:
                if row and row[0].strip():
                    roles.append(row[0].strip())
            break  # Estate team table only; client counterparts are consulted, not staffed
    if not roles:
        failures.append(
            "raci-coverage: no roles found in the team and allocations table"
        )
        return False
    _, raci_rows = table
    raci_text = " ".join(" ".join(r) for r in raci_rows).lower()
    ok = True
    for role in roles:
        key = re.sub(r"\s*\(.*\)$", "", role).strip().lower()
        if key and key not in raci_text:
            failures.append(
                "raci-coverage: team role '%s' never appears in the RACI table"
                % role
            )
            ok = False
    return ok


def check_placeholders(text, failures):
    ok = True
    for pattern, label in PLACEHOLDER_PATTERNS:
        hits = pattern.findall(text)
        if hits:
            sample = hits[0] if isinstance(hits[0], str) else str(hits[0])
            failures.append(
                "placeholders: %d instance(s) of %s remain (first: %r)"
                % (len(hits), label, sample[:60])
            )
            ok = False
    return ok


def check_em_dash(text, failures):
    count = text.count("\u2014")
    if count:
        failures.append("em-dash: %d em dash character(s) found" % count)
        return False
    return True


def run_checks(text):
    """Return (passed_names, failures). failures entries start with 'check-id:'."""
    sections = split_sections(text)
    failures = []
    results = [
        ("required-sections", check_required_sections(sections, failures)),
        ("scope-stamp", check_scope_stamp(sections, failures)),
        ("raci-filled", check_raci_filled(sections, failures)),
        ("raci-coverage", check_raci_coverage(sections, failures)),
        ("placeholders", check_placeholders(text, failures)),
        ("em-dash", check_em_dash(text, failures)),
    ]
    passed = [name for name, ok in results if ok]
    return passed, failures


def main(argv):
    if len(argv) != 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 2
    try:
        with open(argv[1], encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print("charter_check: cannot read %s: %s" % (argv[1], e))
        return 2
    passed, failures = run_checks(text)
    for name in passed:
        print("PASS %s" % name)
    for msg in failures:
        print("FAIL %s" % msg)
    print(
        "charter_check: %d passed, %d failed on %s"
        % (len(passed), len(failures), argv[1])
    )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
