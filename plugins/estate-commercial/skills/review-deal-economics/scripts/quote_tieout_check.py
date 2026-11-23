#!/usr/bin/env python3
"""Quote tie-out check for review-deal-economics.

Reconciles every figure in one or more reviewed artifacts (SOW draft, ROM,
proposal, Deal Desk packet prose) against the source scoping quote, exported
as JSON. The cascade rule made mechanical: every number in a reviewed artifact
traces to the quote or is flagged. The check never changes a number and never
resolves a conflict; it reports, and humans fix the source.

Quote export schema (JSON):
  quote_id        "Q-000181" (required)
  as_of           "YYYY-MM-DD" (required)
  fee             total fee, number (required)
  roles           [{"role", "hours", "rate"}, ...] (required). Optional
                  "low", "expected", "high" (hours) state a ranged estimate;
                  each is an allowed hours figure labelled "<role> low
                  hours" and so on. "hours" may be omitted when "expected"
                  is given. Optional "aliases": ["Solution Architect"] names
                  the other words an artifact uses for the role.
  phases          [{"phase", "hours", "fee"}, ...] (optional); the same
                  optional "low", "expected", "high" hours and "aliases".
  low, expected, high
                  optional top-level fee range, numbers; each is an allowed
                  currency figure labelled "quote fee low" and so on.
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
        value so the conflict is visible, never auto-resolved. An hours range
        ("3 to 10 hours", "3-10 hours") is checked at both ends.
  WARN  a currency or hours figure that equals a quote value but sits on a
        line that names none of that value's labels (a role, phase, "fee",
        "total", or the extra amount's reason words). It matches by number
        only, so confirm it means that quote field. A matched figure is not
        counted as carried by the artifact.
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
HOURS_RE = re.compile(
    r"\b(?:([0-9][0-9,]*(?:\.[0-9]+)?)\s*(?:to|-|\u2013|\u2014)\s*)?"
    r"([0-9][0-9,]*(?:\.[0-9]+)?)\s*(?:hours|hrs)\b", re.I)
GENERIC_WORDS = {"hours", "hour", "hrs", "rate", "fee", "quote", "total", "role",
                 "extended", "billings", "extra", "amount", "low", "expected",
                 "high", "the", "and", "of", "for", "from", "by", "in", "a"}
WORD_RE = re.compile(r"[a-z0-9]+")
PERCENT_RE = re.compile(r"\b([0-9][0-9,]*(?:\.[0-9]+)?)\s*%")
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)


def to_num(text):
    return float(text.replace(",", ""))


def norm(text):
    """Normalize a prose line for containment matching."""
    return re.sub(r"\s+", " ", text.strip().lower())


def build_allowed(quote):
    """Return (money, hours, percents) lists of (value, label) from the quote.

    A label may carry aliases after a "|": "SA hours|Solution Architect".
    """
    money = [(float(quote["fee"]), "quote fee")]
    for key in ("low", "expected", "high"):
        if key in quote:
            money.append((float(quote[key]), "quote fee %s" % key))
    hours = []
    percents = []
    total_hours = 0.0

    def aliased(label, entry):
        names = [str(a) for a in entry.get("aliases", [])]
        return label + ("|" + "|".join(names) if names else "")

    def ranged(entry, label):
        for key in ("low", "expected", "high"):
            if key in entry:
                hours.append((float(entry[key]), aliased("%s %s hours" % (label, key), entry)))

    for r in quote.get("roles", []):
        label = r.get("role", "role")
        base = float(r["hours"] if "hours" in r else r["expected"])
        h, rate = base, float(r["rate"])
        hours.append((h, aliased("%s hours" % label, r)))
        ranged(r, label)
        money.append((rate, aliased("%s rate" % label, r)))
        money.append((h * rate, aliased("%s extended billings" % label, r)))
        total_hours += h
    if quote.get("roles"):
        hours.append((total_hours, "total role hours"))
    for p in quote.get("phases", []):
        label = p.get("phase", "phase")
        if "hours" in p:
            hours.append((float(p["hours"]), aliased("%s hours" % label, p)))
        ranged(p, label)
        if "fee" in p:
            money.append((float(p["fee"]), aliased("%s fee" % label, p)))
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


def label_words(label):
    """Distinguishing words of a quote label, split into (words, acronyms)."""
    parts = label.split("|")
    words = set()
    for part in parts:
        words |= {w for w in WORD_RE.findall(part.lower()) if w not in GENERIC_WORDS}
    return words


def line_words(line):
    low = line.lower()
    words = WORD_RE.findall(low)
    acronyms = set()
    for size in (2, 3, 4):
        for i in range(len(words) - size + 1):
            acronyms.add("".join(w[0] for w in words[i:i + size]))
    return words, acronyms


def labelled(value, allowed, tol, line):
    """True when a quote value equal to `value` has a label named on the line.

    A label word matches a line word exactly, as a prefix of three or more
    letters ("dev" for "developer"), or as the initials of consecutive words
    ("SA" for "Solution Architect"). Quote labels with no distinguishing word
    (the fee, a total) match their generic words: "fee", "total", "hours".
    """
    words, acronyms = line_words(line)
    for candidate, label in allowed:
        if abs(value - candidate) > tol:
            continue
        keys = label_words(label)
        generic = {w for w in WORD_RE.findall(label.split("|")[0].lower())
                   if w in ("fee", "total")}
        if generic & set(words):
            return True
        for key in keys:
            if key in words or key in acronyms:
                return True
            if len(key) >= 3 and any(w.startswith(key) or (len(w) >= 4 and key.startswith(w))
                                     for w in words):
                return True
    return False


SENTENCE_END_RE = re.compile(r"(?<=[.!?])\s+")


def contexts(text):
    """Return (lines, para_of): for each line index, its paragraph text and offset.

    A paragraph is a run of consecutive prose lines; a table row or list item
    stands alone. The label for a figure is looked for in its sentence.
    """
    lines = text.splitlines()
    para_of = {}
    i = 0
    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue
        j = i + 1
        solo = lines[i].lstrip().startswith(("|", "-", "*", "#"))
        while (not solo and j < len(lines) and lines[j].strip()
               and not lines[j].lstrip().startswith(("|", "-", "*", "#"))):
            j += 1
        block = "\n".join(lines[i:j])
        offset = 0
        for k in range(i, j):
            para_of[k] = (block, offset)
            offset += len(lines[k]) + 1
        i = j
    return lines, para_of


def sentence_at(block, pos):
    start = 0
    for m in SENTENCE_END_RE.finditer(block):
        if m.end() <= pos:
            start = m.end()
        else:
            return block[start:m.start()]
    return block[start:]


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
        _, para_of = contexts(stripped)
        for lineno, line in enumerate(stripped.splitlines(), 1):
            block, base = para_of.get(lineno - 1, (line, 0))
            taken = []
            for m in CURRENCY_RE.finditer(line):
                value = to_num(m.group(1))
                taken.append(m.span(1))
                if match(value, money, MONEY_TOL):
                    if labelled(value, money, MONEY_TOL,
                                sentence_at(block, base + m.start(1))):
                        seen_money.add(round(value, 2))
                    else:
                        warns.append(
                            "%s:%d: $%s matches a quote value by number only; "
                            "no label on the line ties it to that quote field, "
                            "confirm it means that field" % (name, lineno, m.group(1)))
                else:
                    near = nearest(value, money)
                    hint = (" (nearest quote value: %.2f, %s)"
                            % (near[0], near[1].split("|")[0]) if near else "")
                    fails.append(
                        "%s:%d: $%s does not trace to %s%s"
                        % (name, lineno, m.group(1), qid, hint))
            for m in HOURS_RE.finditer(line):
                ends = []
                if m.group(1) is not None and not any(
                        a <= m.start(1) < b for a, b in taken):
                    ends.append(m.group(1))
                if not any(a <= m.start(2) < b for a, b in taken):
                    ends.append(m.group(2))
                for text_value in ends:
                    value = to_num(text_value)
                    if match(value, hours, HOURS_TOL):
                        if labelled(value, hours, HOURS_TOL,
                                    sentence_at(block, base + m.start())):
                            seen_hours.add(round(value, 2))
                        else:
                            warns.append(
                                "%s:%d: %s hours matches a quote value by number "
                                "only; no label on the line ties it to that quote "
                                "field, confirm it means that field"
                                % (name, lineno, text_value))
                    else:
                        near = nearest(value, hours)
                        hint = (" (nearest quote value: %.2f, %s)"
                                % (near[0], near[1].split("|")[0]) if near else "")
                        fails.append(
                            "%s:%d: %s hours does not trace to %s%s"
                            % (name, lineno, text_value, qid, hint))
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
                         "artifact; confirm the omission is intentional"
                         % (label.split("|")[0], value))
    for value, label in hours:
        if round(value, 2) not in seen_hours:
            warns.append("quote figure dropped: %s (%.2f) appears in no "
                         "artifact; confirm the omission is intentional"
                         % (label.split("|")[0], value))
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
