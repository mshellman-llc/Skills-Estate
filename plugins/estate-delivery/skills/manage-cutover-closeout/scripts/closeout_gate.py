#!/usr/bin/env python3
"""Deterministic gate for manage-cutover-closeout artifacts.

Checks three artifact types, auto-detected or forced with --type:

  runbook     Every step row has an owner, a verification, and either a
              rollback point or the literal "No rollback:" with a stated
              reason. Blank, TBD, or reasonless cells fail.
  acceptance  The Go-Live Acceptance tracker carries the go-live date, the
              acceptance period as read from the executed SOW clause, the
              verbatim clause text, and a deemed-acceptance deadline. The
              gate recomputes the deadline from the go-live date and the
              stated period (business days skip weekends and any listed
              holidays) and fails on a mismatch. The computation is printed.
  closeout    The Hypercare Closeout Report's actuals-vs-estimate table has
              a source or a named gap ("GAP: reason") on every row, and
              every hypercare issue row has a stable HC-ID, a severity, and
              a disposition; rows dispositioned Closed must state verified
              resolution.

Exit 0 on pass, 1 on any failure, 2 on usage or unreadable input.
Stdlib only. No network. No em dashes in this file or its output.
"""

import argparse
import datetime
import re
import sys

EMPTYISH = {"", "-", "tbd", "n/a", "na", "none", "unknown", "?", "todo", "pending"}

DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def is_empty(cell: str) -> bool:
    return cell.strip().strip("*_`").lower() in EMPTYISH


def parse_tables(text: str):
    """Yield (heading, rows) for each markdown pipe table, where heading is
    the nearest preceding markdown heading text (lowercased) and rows is a
    list of cell lists (header row first, separator row removed)."""
    heading = ""
    tables = []
    current = None
    for line in text.splitlines():
        h = re.match(r"^#{1,6}\s+(.*)", line)
        if h:
            heading = h.group(1).strip().lower()
            current = None
            continue
        if line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
                continue
            if current is None:
                current = (heading, [])
                tables.append(current)
            current[1].append(cells)
        else:
            current = None
    return tables


def find_table(tables, required_cols):
    """Return (heading, header, body_rows, colmap) for the first table whose
    header contains every name in required_cols (substring match, case
    insensitive), else None."""
    for heading, rows in tables:
        if not rows:
            continue
        header = [c.lower() for c in rows[0]]
        colmap = {}
        for want in required_cols:
            for i, col in enumerate(header):
                if want in col:
                    colmap[want] = i
                    break
        if len(colmap) == len(required_cols):
            return heading, rows[0], rows[1:], colmap
    return None


def check_runbook(text: str, out):
    failures = []
    found = find_table(parse_tables(text), ["step", "owner", "verification", "rollback"])
    if not found:
        return ["runbook: no step table found with Step, Owner, Verification, "
                "and Rollback columns (see references/runbook-format.md)"]
    heading, header, body, colmap = found
    if not body:
        return ["runbook: step table has a header but no step rows"]
    for n, row in enumerate(body, start=1):
        label = f"runbook step row {n}"
        if len(row) <= max(colmap.values()):
            failures.append(f"{label}: row has fewer cells than the header")
            continue
        step = row[colmap["step"]]
        owner = row[colmap["owner"]]
        verify = row[colmap["verification"]]
        rollback = row[colmap["rollback"]]
        if is_empty(step):
            failures.append(f"{label}: step description is empty")
        if is_empty(owner):
            failures.append(f"{label} ({step[:40]}): no owner")
        if is_empty(verify):
            failures.append(f"{label} ({step[:40]}): no verification")
        rb = rollback.strip()
        if is_empty(rb):
            failures.append(f"{label} ({step[:40]}): rollback cell empty; state a "
                            f"rollback point or 'No rollback: <reason>'")
        elif re.match(r"(?i)^no\s+rollback\b", rb):
            reason = re.sub(r"(?i)^no\s+rollback\s*[:,]?\s*", "", rb)
            if is_empty(reason) or len(reason) < 8:
                failures.append(f"{label} ({step[:40]}): 'No rollback' declared "
                                f"without a stated reason")
    out.append(f"runbook: {len(body)} step rows checked in table under "
               f"'{heading or '(no heading)'}'")
    return failures


def add_business_days(start: datetime.date, n: int, holidays) -> datetime.date:
    d = start
    added = 0
    while added < n:
        d += datetime.timedelta(days=1)
        if d.weekday() < 5 and d not in holidays:
            added += 1
    return d


def grab_field(text: str, label_re: str):
    m = re.search(rf"(?im)^\s*[-*]?\s*\*{{0,2}}{label_re}\*{{0,2}}\s*:\s*(.+)$", text)
    return m.group(1).strip() if m else None


def check_acceptance(text: str, out):
    failures = []

    golive_raw = grab_field(text, r"go[- ]live date")
    period_raw = grab_field(text, r"acceptance period")
    deadline_raw = grab_field(text, r"deemed[- ]acceptance deadline")

    if not re.search(r"(?im)^\s*[-*]?\s*\*{0,2}sow clause \(verbatim\)", text):
        failures.append("acceptance: no 'SOW clause (verbatim):' field; the executed "
                        "SOW's deemed-acceptance clause must be quoted, never assumed")
    if not golive_raw:
        failures.append("acceptance: no 'Go-live date:' field")
    if not period_raw:
        failures.append("acceptance: no 'Acceptance period:' field (read it from the "
                        "SOW clause; do not assume 10 days)")
    if not deadline_raw:
        failures.append("acceptance: no 'Deemed-acceptance deadline:' field")
    if failures:
        return failures

    gm = DATE_RE.search(golive_raw)
    dm = DATE_RE.search(deadline_raw)
    pm = re.search(r"(?i)(\d+)\s*(business|calendar)\s*days?", period_raw)
    if not gm:
        failures.append(f"acceptance: go-live date not in YYYY-MM-DD form: '{golive_raw}'")
    if not dm:
        failures.append(f"acceptance: deadline not in YYYY-MM-DD form: '{deadline_raw}'")
    if not pm:
        failures.append("acceptance: period must read '<N> business days' or "
                        f"'<N> calendar days', got '{period_raw}'")
    if failures:
        return failures

    golive = datetime.date.fromisoformat(gm.group(1))
    stated = datetime.date.fromisoformat(dm.group(1))
    n, kind = int(pm.group(1)), pm.group(2).lower()

    holidays = set()
    hol_raw = grab_field(text, r"holidays observed")
    if hol_raw:
        holidays = {datetime.date.fromisoformat(d) for d in DATE_RE.findall(hol_raw)}

    if kind == "business":
        computed = add_business_days(golive, n, holidays)
        skipped = (computed - golive).days - n
        detail = (f"{n} business days from {golive} ({golive.strftime('%a')}), "
                  f"skipping {skipped} weekend/holiday day(s)")
    else:
        computed = golive + datetime.timedelta(days=n)
        detail = f"{n} calendar days from {golive}"
    out.append(f"acceptance: deadline computation: {detail} = {computed} "
               f"({computed.strftime('%a')}); tracker states {stated}")

    if computed != stated:
        failures.append(f"acceptance: stated deadline {stated} does not match "
                        f"computed deadline {computed} ({detail})")
    return failures


def check_closeout(text: str, out):
    failures = []
    tables = parse_tables(text)

    found = find_table(tables, ["estimate", "actual", "source"])
    if not found:
        failures.append("closeout: no actuals-vs-estimate table found with Estimated, "
                        "Actual, and Source columns")
    else:
        heading, header, body, colmap = found
        if not body:
            failures.append("closeout: actuals-vs-estimate table has no rows")
        for n, row in enumerate(body, start=1):
            if len(row) <= max(colmap.values()):
                failures.append(f"closeout actuals row {n}: fewer cells than header")
                continue
            src = row[colmap["source"]].strip()
            if is_empty(src):
                failures.append(f"closeout actuals row {n}: source cell empty; name "
                                f"the source or write 'GAP: <what is missing and who "
                                f"owns getting it>'")
            elif re.match(r"(?i)^gap\b", src):
                reason = re.sub(r"(?i)^gap\s*[:,]?\s*", "", src)
                if is_empty(reason) or len(reason) < 8:
                    failures.append(f"closeout actuals row {n}: 'GAP' declared "
                                    f"without naming what is missing")
        if body:
            out.append(f"closeout: {len(body)} actuals-vs-estimate rows checked")

    hc = find_table(tables, ["id", "severity", "disposition"])
    if not hc:
        failures.append("closeout: no hypercare issue table found with ID, Severity, "
                        "and Disposition columns")
    else:
        heading, header, body, colmap = hc
        if not body:
            failures.append("closeout: hypercare issue table has no rows (if hypercare "
                            "was clean, state that in prose and keep one 'none' row out "
                            "of the table)")
        for n, row in enumerate(body, start=1):
            if len(row) <= max(colmap.values()):
                failures.append(f"closeout hypercare row {n}: fewer cells than header")
                continue
            hcid = row[colmap["id"]].strip()
            sev = row[colmap["severity"]].strip()
            disp = row[colmap["disposition"]].strip()
            if not re.fullmatch(r"HC-\d{3,}", hcid):
                failures.append(f"closeout hypercare row {n}: ID '{hcid}' is not a "
                                f"stable HC-### identifier")
            if not re.search(r"(?i)\bsev\s*[1-4]\b|\b[1-4]\b", sev):
                failures.append(f"closeout hypercare row {n} ({hcid}): severity "
                                f"'{sev}' is not Sev 1..4")
            if is_empty(disp):
                failures.append(f"closeout hypercare row {n} ({hcid}): no disposition")
            elif re.match(r"(?i)^closed\b", disp) and "verif" not in disp.lower():
                failures.append(f"closeout hypercare row {n} ({hcid}): closed without "
                                f"stating verified resolution")
        if body:
            out.append(f"closeout: {len(body)} hypercare issue rows checked")
    return failures


def detect_type(text: str):
    t = text.lower()
    if "deemed-acceptance deadline" in t or "deemed acceptance deadline" in t:
        return "acceptance"
    if "actuals vs estimate" in t or ("hypercare" in t and "closeout" in t):
        return "closeout"
    if "rollback" in t and ("runbook" in t or "cutover" in t):
        return "runbook"
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description="Gate cutover/closeout artifacts")
    ap.add_argument("file", help="markdown artifact to check")
    ap.add_argument("--type", choices=["runbook", "acceptance", "closeout", "auto"],
                    default="auto")
    args = ap.parse_args(argv)

    try:
        with open(args.file, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as e:
        print(f"error: cannot read {args.file}: {e}")
        return 2

    kind = args.type if args.type != "auto" else detect_type(text)
    if kind is None:
        print("error: could not detect artifact type; pass --type "
              "runbook|acceptance|closeout")
        return 2

    if "\u2014" in text:
        print(f"FAIL: {args.file} contains an em dash; house rule is zero em dashes")
        return 1

    out, failures = [], []
    check = {"runbook": check_runbook, "acceptance": check_acceptance,
             "closeout": check_closeout}[kind]
    failures = check(text, out)

    for line in out:
        print(line)
    if failures:
        for f in failures:
            print(f"FAIL: {f}")
        print(f"result: {kind} gate FAILED with {len(failures)} failure(s)")
        return 1
    print(f"result: {kind} gate passed, 0 failures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
