#!/usr/bin/env python3
"""Gate for discovery-brief ledgers and briefs.

Validates a JSON ledger or a markdown brief against the ledger spec
(references/ledger-spec.md):

  1. Every Column A claim carries a non-empty source.
  2. No Column A confidence is Unknown; every confidence is Confirmed or Inferred.
  3. Column B is non-empty.
  4. Every Column B question has text, a rank of High/Medium/Low, and a
     non-empty scope line it unblocks.
  5. Column B entries appear in rank order (High, then Medium, then Low).
  6. No em dash anywhere in the file.

Usage: check_brief.py <ledger.json | brief.md>
Exit 0 on pass, 1 on any failure, 2 on unusable input.

Stdlib only, by design: the gate must run on any surface.
"""

import json
import re
import sys

RANKS = ("High", "Medium", "Low")
RANK_ORDER = {name: i for i, name in enumerate(RANKS)}
CONFIDENCE = ("Confirmed", "Inferred")
EM_DASH = "\u2014"  # written as an escape so this gate passes its own scan

COL_A_HEADINGS = ("column a", "what we know")
COL_B_HEADINGS = ("column b", "open questions", "ranked unknowns")


def check_known(rows, problems):
    for i, row in enumerate(rows, 1):
        label = (row.get("claim") or "").strip() or "row {}".format(i)
        label = "Column A [{}]".format(label[:60])
        if not (row.get("claim") or "").strip():
            problems.append("{}: empty claim".format(label))
        if not (row.get("source") or "").strip():
            problems.append("{}: no source token; an unsourced claim does not enter Column A".format(label))
        conf = (row.get("confidence") or "").strip()
        if conf == "Unknown":
            problems.append("{}: confidence Unknown; a searched-for fact not found belongs in Column B as a question".format(label))
        elif conf not in CONFIDENCE:
            problems.append("{}: confidence must be Confirmed or Inferred, got '{}'".format(label, conf))


def check_open(rows, problems):
    if not rows:
        problems.append("Column B is empty; a brief with no open questions is a status report, not a discovery brief")
        return
    seen_ranks = []
    for i, row in enumerate(rows, 1):
        label = "Column B [{}]".format((row.get("id") or "row {}".format(i)).strip())
        if not (row.get("question") or "").strip():
            problems.append("{}: empty question".format(label))
        rank = (row.get("rank") or "").strip()
        if rank not in RANKS:
            problems.append("{}: rank must be High, Medium, or Low, got '{}'".format(label, rank))
        else:
            seen_ranks.append((label, rank))
        if not (row.get("unblocks") or "").strip():
            problems.append("{}: no scope line named; a question that unblocks nothing fails the cut test".format(label))
    for (prev_label, prev), (label, cur) in zip(seen_ranks, seen_ranks[1:]):
        if RANK_ORDER[cur] < RANK_ORDER[prev]:
            problems.append("{} ({}) appears after {} ({}); Column B must run in rank order".format(label, cur, prev_label, prev))


def parse_table(lines):
    """Parse a markdown table into a list of dicts keyed by lowercased header."""
    rows = [ln for ln in lines if ln.strip().startswith("|")]
    if len(rows) < 2:
        return []

    def cells(line):
        return [c.strip() for c in line.strip().strip("|").split("|")]

    header = [h.lower() for h in cells(rows[0])]
    out = []
    for line in rows[2:]:  # skip header and separator
        vals = cells(line)
        if all(not v for v in vals):
            continue
        out.append({header[j]: vals[j] for j in range(min(len(header), len(vals)))})
    return out


def find_section_table(text, heading_keys):
    """Return the first table under the first heading matching heading_keys."""
    lines = text.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if re.match(r"\s*#{1,6}\s", ln) and any(k in ln.lower() for k in heading_keys):
            start = i + 1
            break
    if start is None:
        return None
    block = []
    for ln in lines[start:]:
        if re.match(r"\s*#{1,6}\s", ln):
            break
        block.append(ln)
    table = parse_table(block)
    return table if table else None


def field(row, *names):
    for n in names:
        if n in row:
            return row[n]
    return ""


def check_markdown(text, problems):
    table_a = find_section_table(text, COL_A_HEADINGS)
    if table_a is None:
        problems.append("no Column A table found; expected a heading containing 'Column A' or 'what we know' followed by a table")
    else:
        known = [
            {
                "claim": field(r, "claim"),
                "source": field(r, "source", "source(s)", "sources"),
                "confidence": field(r, "confidence"),
            }
            for r in table_a
        ]
        check_known(known, problems)

    table_b = find_section_table(text, COL_B_HEADINGS)
    if table_b is None:
        problems.append("no Column B table found; expected a heading containing 'Column B', 'open questions', or 'ranked unknowns' followed by a table")
    else:
        open_qs = [
            {
                "id": field(r, "id"),
                "question": field(r, "question", "open question"),
                "rank": field(r, "rank", "impact", "scoping impact"),
                "unblocks": field(r, "unblocks", "scope item it unblocks", "scope line"),
            }
            for r in table_b
        ]
        check_open(open_qs, problems)


def check_json(data, problems):
    if not isinstance(data, dict):
        problems.append("JSON ledger must be an object with 'known' and 'open' lists")
        return
    known = data.get("known")
    open_qs = data.get("open")
    if not isinstance(known, list):
        problems.append("missing 'known' list (Column A); use [] for a greenfield deal, never omit it")
    else:
        check_known([r for r in known if isinstance(r, dict)], problems)
        bad = sum(1 for r in known if not isinstance(r, dict))
        if bad:
            problems.append("{} Column A entries are not objects".format(bad))
    if not isinstance(open_qs, list):
        problems.append("missing 'open' list (Column B); the ranked questions are the product")
    else:
        check_open([r for r in open_qs if isinstance(r, dict)], problems)


def check_em_dash(text, problems):
    for i, ln in enumerate(text.splitlines(), 1):
        if EM_DASH in ln:
            problems.append("em dash on line {}: {}".format(i, ln.strip()[:80]))


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    path = argv[1]
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError as exc:
        print("FAIL: cannot read {}: {}".format(path, exc))
        return 2

    problems = []
    if path.endswith(".json"):
        try:
            check_json(json.loads(text), problems)
        except json.JSONDecodeError as exc:
            print("FAIL: invalid JSON: {}".format(exc))
            return 2
    else:
        check_markdown(text, problems)
    check_em_dash(text, problems)

    if problems:
        for p in problems:
            print("FAIL: {}".format(p))
        print("{}: {} fail".format(path, len(problems)))
        return 1
    print("{}: 0 fail. Column A sourced, Column B ranked and tied to scope, no em dashes.".format(path))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
