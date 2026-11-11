#!/usr/bin/env python3
"""Quote tie-out check for estate-deal-desk.

Reconciles every figure in one or more reviewed artifacts (SOW draft, ROM,
proposal, Deal Desk packet prose) against the source scoping quote, exported
as JSON. The cascade rule made mechanical: every number in a reviewed artifact
traces to the quote or is flagged. The check never changes a number and never
resolves a conflict; it reports, and humans fix the source.

Quote export schema (JSON):
  quote_id        "Q-000181" (required)
  as_of           "YYYY-MM-DD" (required)
  fee             total fee, number (required)
  roles           [{"role", "hours", "rate"}, ...] (required)
  phases          [{"phase", "hours", "fee"}, ...] (optional)
  percentages     [48, 52.84, ...] percent figures verified against the quote
                  or canon; any other percent in an artifact fails (optional)
  extra_amounts   [{"amount", "reason"}, ...] figures sourced and verified
                  outside the quote, each with a stated reason (optional)
  assumptions     ["...", ...] load-bearing assumption lines (optional)
  scope_lines     ["...", ...] scope lines the artifacts must carry (optional)

What it checks:
  FAIL  an artifact currency, hours, or percent figure that traces to nothing
        in the quote export. A wrong figure and a fabricated figure land the
        same way: unmatched, printed with file, line, and the nearest quote
        value so the conflict is visible, never auto-resolved.
  WARN  a quote figure (fee, role hours, role rate, phase fee, phase hours)
        no artifact carries: confirm the omission is intentional.
  WARN  an assumption or scope line from the quote absent from every artifact.

Fenced code blocks are skipped: the deal-desk-figures block is arithmetic
checked by deal_desk_gate.py, and gating the same JSON twice double-reports.

Exit 0 clean or warnings only, 1 on any FAIL, 2 on unreadable input.
Usage: quote_tieout_check.py quote.json artifact.md [artifact2.md ...]
"""

import json
import re
import sys

MONEY_TOL = 1.0
HOURS_TOL = 0.01
PCT_TOL = 0.05

CURRENCY_RE = re.compile(r"\$\s?([0-9][0-9,]*(?:\.[0-9]{1,2})?)")
HOURS_RE = re.compile(r"\b([0-9][0-9,]*(?:\.[0-9]+)?)\s*(?:hours|hrs)\b", re.I)
PERCENT_RE = re.compile(r"\b([0-9][0-9,]*(?:\.[0-9]+)?)\s*%")
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)


def to_num(text):
    return float(text.replace(",", ""))


def norm(text):
    """Normalize a prose line for containment matching."""
    return re.sub(r"\s+", " ", text.strip().lower())


def build_allowed(quote):
    """Return (money, hours, percents) lists of (value, label) from the quote."""
    money = [(float(quote["fee"]), "quote fee")]
    hours = []
    percents = []
    total_hours = 0.0
    for r in quote.get("roles", []):
        h, rate = float(r["hours"]), float(r["rate"])
        label = r.get("role", "role")
        hours.append((h, "%s hours" % label))
        money.append((rate, "%s rate" % label))
        money.append((h * rate, "%s extended billings" % label))
        total_hours += h
    if quote.get("roles"):
        hours.append((total_hours, "total role hours"))
    for p in quote.get("phases", []):
        label = p.get("phase", "phase")
        if "hours" in p:
            hours.append((float(p["hours"]), "%s hours" % label))
        if "fee" in p:
            money.append((float(p["fee"]), "%s fee" % label))
    for pct in quote.get("percentages", []):
        percents.append((float(pct), "verified percentage"))
    for extra in quote.get("extra_amounts", []):
        money.append((float(extra["amount"]),
                      "extra amount: %s" % extra.get("reason", "no reason given")))
    return money, hours, percents


def nearest(value, allowed):
    if not allowed:
        return None
    return min(allowed, key=lambda pair: abs(pair[0] - value))


def match(value, allowed, tol):
    return any(abs(value - candidate) <= tol for candidate, _ in allowed)


def check(quote, artifacts):
    """quote: parsed JSON dict. artifacts: list of (name, text).

    Returns (fails, warns), each a list of strings.
    """
    fails, warns = [], []
    money, hours, percents = build_allowed(quote)
    qid = quote.get("quote_id", "the quote")
    seen_money, seen_hours = set(), set()
    combined_norm = []

    for name, text in artifacts:
        stripped = FENCE_RE.sub("", text)
        combined_norm.append(norm(stripped))
        for lineno, line in enumerate(stripped.splitlines(), 1):
            taken = []
            for m in CURRENCY_RE.finditer(line):
                value = to_num(m.group(1))
                taken.append(m.span(1))
                if match(value, money, MONEY_TOL):
                    seen_money.add(round(value, 2))
                else:
                    near = nearest(value, money)
                    hint = (" (nearest quote value: %.2f, %s)" % near
                            if near else "")
                    fails.append(
                        "%s:%d: $%s does not trace to %s%s"
                        % (name, lineno, m.group(1), qid, hint))
            for m in HOURS_RE.finditer(line):
                if any(a <= m.start(1) < b for a, b in taken):
                    continue
                value = to_num(m.group(1))
                if match(value, hours, HOURS_TOL):
                    seen_hours.add(round(value, 2))
                else:
                    near = nearest(value, hours)
                    hint = (" (nearest quote value: %.2f, %s)" % near
                            if near else "")
                    fails.append(
                        "%s:%d: %s hours does not trace to %s%s"
                        % (name, lineno, m.group(1), qid, hint))
            for m in PERCENT_RE.finditer(line):
                value = to_num(m.group(1))
                if not match(value, percents, PCT_TOL):
                    fails.append(
                        "%s:%d: %s%% is not in the quote export's verified "
                        "percentages; source it or drop it" % (name, lineno, m.group(1)))

    everything = " ".join(combined_norm)
    for value, label in money:
        if round(value, 2) not in seen_money:
            warns.append("quote figure dropped: %s (%.2f) appears in no "
                         "artifact; confirm the omission is intentional" % (label, value))
    for value, label in hours:
        if round(value, 2) not in seen_hours:
            warns.append("quote figure dropped: %s (%.2f) appears in no "
                         "artifact; confirm the omission is intentional" % (label, value))
    for item in quote.get("assumptions", []):
        if norm(item) not in everything:
            warns.append("assumption absent from every artifact: %r" % item)
    for item in quote.get("scope_lines", []):
        if norm(item) not in everything:
            warns.append("scope line absent from every artifact: %r" % item)
    return fails, warns


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    try:
        with open(argv[1], encoding="utf-8") as fh:
            quote = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print("FAIL cannot read quote export %s: %s" % (argv[1], exc))
        return 2
    for key in ("quote_id", "as_of", "fee", "roles"):
        if key not in quote:
            print("FAIL quote export missing required key: %s" % key)
            return 2
    artifacts = []
    for path in argv[2:]:
        try:
            with open(path, encoding="utf-8") as fh:
                artifacts.append((path, fh.read()))
        except OSError as exc:
            print("FAIL cannot read artifact %s: %s" % (path, exc))
            return 2
    fails, warns = check(quote, artifacts)
    for line in fails:
        print("FAIL %s" % line)
    for line in warns:
        print("WARN %s" % line)
    print("%d failure(s), %d warning(s) against %s across %d artifact(s)."
          % (len(fails), len(warns), quote.get("quote_id"), len(artifacts)))
    if fails:
        print("The figures do not tie out. Fix the source artifact or the "
              "quote; this check changes nothing.")
        return 1
    print("PASS every figure traces to the quote.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
