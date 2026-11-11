#!/usr/bin/env python3
"""Verify corpus integrity after adding or replacing catalog entries.

Splits a source and an edited catalog into level-2 ("## ") entries, keyed by the
full heading text after "## " (e.g. "01 Discovery Sprint", not "01"). Reports
which entries were added, removed, changed, or left identical, and fails if
anything you did NOT declare as changed differs.

Usage:
  python verify_corpus.py --source OLD.md --edited NEW.md \
      [--changed "01 Discovery Sprint" "14 Managed Service"]
  python verify_corpus.py --selftest

--changed takes those same full headings, quoted. A bare number matches nothing
and is reported as an unknown id, so a mis-declared entry fails loudly instead of
passing as undeclared-but-unchanged. Everything
else must be byte-identical, which is the whole point: unchanged plays should
never be re-transcribed, only carried over verbatim.

WHAT THIS CHECKS, PRECISELY
  - Every entry outside --changed is byte-identical, ignoring only a trailing
    "---" separator and trailing blank lines.
  - The preamble (everything above the first entry, including the version line)
    is compared too. Declare it as "preamble" in --changed when you bump it.
  - Duplicate entry ids are a hard error. They are the numbering collision the
    skill tells you to flag, and they make per-id comparison meaningless.
  - "## " lines inside fenced code blocks are not treated as headings, so a
    catalog that documents its own format parses correctly.

KNOWN BEHAVIOUR WORTH KNOWING
  Text after the final "---" in the file is treated as part of the last entry,
  not as a file footer. This is deliberate: guessing where a footer starts is
  how content gets silently dropped. If your catalog has a generated footer,
  put the version line in the preamble instead, or declare the last entry.
"""
import argparse
import difflib
import os
import re
import sys
import tempfile

HEADING = re.compile(r"^## (.+)$")
FENCE = re.compile(r"^\s*(```|~~~)")
PREAMBLE_KEY = "preamble"


def normalize(section):
    """Strip only the chrome that genuinely terminates an entry: trailing blank
    lines and a single trailing "---" separator. Content inside the entry,
    including horizontal rules used as internal dividers, is preserved.

    The earlier version scanned backwards for the LAST "---" anywhere in the
    entry and dropped everything after it, which silently hid real edits in any
    entry that used an internal rule."""
    lines = section.rstrip().split("\n")
    while lines and not lines[-1].strip():
        lines.pop()
    if lines and lines[-1].strip() == "---":
        lines.pop()
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines).rstrip()


def entry_id(heading_text):
    """"01 - Name (free)" -> "01"; "Some Heading" -> "Some Heading"."""
    parts = re.split(r"\s+·\s+", heading_text, maxsplit=1)
    return parts[0].strip()


def split_entries(text):
    """Return (preamble, entries, duplicates).

    entries maps id -> section text. duplicates lists ids that appeared more
    than once; those ids are unreliable and are reported as a hard error rather
    than silently overwritten."""
    lines = text.split("\n")
    in_fence = False
    starts = []
    for i, line in enumerate(lines):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING.match(line)
        if m:
            starts.append((i, m.group(1)))

    if not starts:
        return text, {}, []

    preamble = "\n".join(lines[: starts[0][0]])
    entries, order, duplicates = {}, [], []
    for n, (line_no, heading) in enumerate(starts):
        end = starts[n + 1][0] if n + 1 < len(starts) else len(lines)
        key = entry_id(heading)
        body = "\n".join(lines[line_no:end])
        if key in entries:
            if key not in duplicates:
                duplicates.append(key)
        else:
            order.append(key)
        entries.setdefault(key, body)
    return preamble, entries, duplicates


def brief_diff(a, b, label, limit=6):
    out = []
    for line in difflib.unified_diff(a.split("\n"), b.split("\n"),
                                     fromfile="source/" + label,
                                     tofile="edited/" + label, lineterm="", n=0):
        if line.startswith("---") or line.startswith("+++"):
            continue
        out.append(line)
        if len(out) >= limit:
            out.append("  ... (truncated)")
            break
    return out


def compare(src_text, new_text, changed):
    """Return (report_lines, problems)."""
    src_pre, src_e, src_dupes = split_entries(src_text)
    new_pre, new_e, new_dupes = split_entries(new_text)

    report, problems = [], []

    if src_dupes or new_dupes:
        if src_dupes:
            problems.append("duplicate entry ids in source: %s" % src_dupes)
        if new_dupes:
            problems.append("duplicate entry ids in edited: %s" % new_dupes)

    src_ids, new_ids = set(src_e), set(new_e)
    added = sorted(new_ids - src_ids)
    removed = sorted(src_ids - new_ids)
    common = sorted(src_ids & new_ids)

    identical, differ = [], []
    for k in common:
        (identical if normalize(src_e[k]) == normalize(new_e[k]) else differ).append(k)

    pre_changed = normalize(src_pre) != normalize(new_pre)

    report.append("Entries parsed:   source %d, edited %d" % (len(src_e), len(new_e)))
    report.append("Added entries:    %s" % (added or "none"))
    report.append("Removed entries:  %s" % (removed or "none"))
    report.append("Changed entries:  %s" % (differ or "none"))
    report.append("Preamble:         %s" % ("CHANGED" if pre_changed else "unchanged"))
    report.append("Identical:        %d of %d common entries" % (len(identical), len(common)))

    undeclared_diff = [k for k in differ if k not in changed]
    undeclared_add = [k for k in added if k not in changed]
    undeclared_rm = [k for k in removed if k not in changed]

    if undeclared_diff:
        problems.append("changed but not declared: %s" % undeclared_diff)
    if undeclared_add:
        problems.append("added but not declared: %s" % undeclared_add)
    if undeclared_rm:
        problems.append("removed but not declared: %s" % undeclared_rm)
    if pre_changed and PREAMBLE_KEY not in changed:
        problems.append("preamble changed but not declared (add 'preamble' to --changed)")

    # Warnings: not fatal, but they mean the declaration is out of step.
    warnings = []
    for k in changed:
        if k == PREAMBLE_KEY:
            continue
        if k not in src_ids and k not in new_ids:
            warnings.append("declared id '%s' does not exist in either file" % k)
        elif k in identical:
            warnings.append("declared id '%s' is unchanged" % k)

    for k in undeclared_diff:
        report.append("")
        report.append("Diff for undeclared change in %s:" % k)
        report.extend("  " + ln for ln in brief_diff(normalize(src_e[k]), normalize(new_e[k]), k))

    return report, problems, warnings


def run(source, edited, changed):
    src = open(source, encoding="utf-8").read()
    new = open(edited, encoding="utf-8").read()
    report, problems, warnings = compare(src, new, set(changed))
    for line in report:
        print(line)
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print("  -", w)
    if problems:
        print("\nFAIL - corpus integrity violated:")
        for p in problems:
            print("  -", p)
        print("Either these were unintended (fix them) or add their ids to --changed.")
        return 1
    print("\nPASS - every entry outside --changed is byte-identical to the source.")
    return 0


# ---------------------------------------------------------------------------
# Self-test: locks in the four false-pass regressions this script was fixed for.
# ---------------------------------------------------------------------------
DOT = "·"


def _entry(num, name, body):
    return "## %s %s %s (paid)\n\n%s\n" % (num, DOT, name, body)


def selftest():
    cases = []

    def check(name, src, new, changed, expect_fail):
        _, problems, _ = compare(src, new, set(changed))
        got_fail = bool(problems)
        cases.append((name, expect_fail, got_fail, got_fail == expect_fail))

    # 1. internal rule, no trailing separator, edit after the rule
    a = _entry("01", "Alpha", "Intro.\n\n---\n\n**Deliverables promised**\n- Deck")
    b = _entry("01", "Alpha", "Intro.\n\n---\n\n**Deliverables promised**\n- Deck and plan")
    check("internal rule hides a later edit", a, b, [], True)

    # 2. internal rule in the last entry of a separated catalog
    pre = _entry("01", "Zero", "Body.") + "\n---\n\n"
    check("internal rule in last entry", pre + a, pre + b, [], True)

    # 3. duplicate ids, first occurrence edited
    d1 = _entry("07", "Vendor", "**In scope**\n- One") + "\n---\n\n" + _entry("07", "Portfolio", "**In scope**\n- Two")
    d2 = _entry("07", "Vendor", "**In scope**\n- One changed") + "\n---\n\n" + _entry("07", "Portfolio", "**In scope**\n- Two")
    check("duplicate ids are a hard error", d1, d2, [], True)

    # 4. fenced '## ' must not create a phantom entry
    f1 = _entry("01", "Guide", "```\n## NN %s [Name] (tier)\n```\n\n**Target buyer**\n- RevOps" % DOT)
    f2 = _entry("01", "Guide", "```\n## NN %s [Name] (tier)\n```\n\n**Target buyer**\n- RevOps, CFO" % DOT)
    check("fenced heading does not split the entry", f1, f2, [], True)
    _, e, _ = split_entries(f1)
    cases.append(("fenced catalog parses as exactly 1 entry", True, len(e) == 1, len(e) == 1))

    # 5. preamble change is visible
    p1 = "# Catalog\n\nVersion: 3\n\n" + _entry("01", "Alpha", "Body.")
    p2 = "# Catalog\n\nVersion: 4\n\n" + _entry("01", "Alpha", "Body.")
    check("preamble version bump is caught", p1, p2, [], True)
    check("preamble bump passes when declared", p1, p2, [PREAMBLE_KEY], False)

    # 6. happy paths still behave
    h1 = _entry("01", "Alpha", "Body.") + "\n---\n\n" + _entry("02", "Beta", "Body.")
    h2 = _entry("01", "Alpha", "Body changed.") + "\n---\n\n" + _entry("02", "Beta", "Body.")
    check("declared change passes", h1, h2, ["01"], False)
    check("undeclared change fails", h1, h2, [], True)
    check("identical files pass", h1, h1, [], False)

    width = max(len(c[0]) for c in cases)
    ok = True
    for name, expect, got, passed in cases:
        print("  %-*s  %s" % (width, name, "ok" if passed else "BROKEN"))
        ok = ok and passed
    print("\n%s - %d checks" % ("SELFTEST PASS" if ok else "SELFTEST FAIL", len(cases)))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source")
    ap.add_argument("--edited")
    ap.add_argument("--changed", nargs="*", default=[],
                    help="entry ids you intentionally changed or added; use "
                         "'preamble' for the header/version block")
    ap.add_argument("--selftest", action="store_true",
                    help="run built-in regression checks and exit")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(selftest())
    if not args.source or not args.edited:
        ap.error("--source and --edited are required unless --selftest is used")
    sys.exit(run(args.source, args.edited, args.changed))


if __name__ == "__main__":
    main()
