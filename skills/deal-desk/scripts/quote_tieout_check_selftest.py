#!/usr/bin/env python3
"""Selftest for quote_tieout_check.py.

Runs the checker against the passing and failing tie-out fixtures via
subprocess to verify exit codes, then exercises the check() function directly
on targeted cases: fabricated figures, contradicted figures, dropped quote
figures, dropped assumptions and scope lines, fence skipping, and unsourced
percentages. Exit 0 when every case behaves, 1 otherwise.
"""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CHECK = os.path.join(HERE, "quote_tieout_check.py")
QUOTE = os.path.join(HERE, "fixtures", "tieout_quote.json")
PASSING = os.path.join(HERE, "fixtures", "tieout_pass.md")
FAILING = os.path.join(HERE, "fixtures", "tieout_fail.md")

sys.path.insert(0, HERE)
import quote_tieout_check as tieout  # noqa: E402

results = []


def case(name, ok, detail=""):
    results.append((name, ok, detail))
    print("%s %s%s" % ("ok " if ok else "FAIL", name, (" :: " + detail) if detail else ""))


def load_quote():
    with open(QUOTE, encoding="utf-8") as fh:
        return json.load(fh)


def main():
    # Exit codes through the real CLI.
    p = subprocess.run([sys.executable, CHECK, QUOTE, PASSING],
                       capture_output=True, text=True)
    case("passing fixture exits 0", p.returncode == 0,
         p.stdout.strip().splitlines()[-1] if p.stdout else "")
    case("passing fixture has zero warnings", "WARN" not in p.stdout)
    f = subprocess.run([sys.executable, CHECK, QUOTE, FAILING],
                       capture_output=True, text=True)
    case("failing fixture exits 1", f.returncode == 1)
    case("failing fixture flags the contradicted fee", "$220,000" in f.stdout)
    case("failing fixture names the nearest quote value",
         "nearest quote value: 218000.00" in f.stdout)
    case("failing fixture flags the contradicted hours", "340 hours" in f.stdout)
    case("failing fixture flags the unsourced percentage", "12%" in f.stdout)
    case("failing fixture warns on the dropped assumption",
         "assumption absent" in f.stdout)
    u = subprocess.run([sys.executable, CHECK, QUOTE], capture_output=True, text=True)
    case("missing artifact argument exits 2", u.returncode == 2)

    # Targeted cases through check().
    quote = load_quote()
    body = open(PASSING, encoding="utf-8").read()
    fails, warns = tieout.check(quote, [("pass.md", body)])
    case("clean artifact returns no failures", fails == [], "; ".join(fails))
    case("clean artifact returns no warnings", warns == [], "; ".join(warns))

    fails, _ = tieout.check(quote, [("a.md", body + "\nA travel budget of $7,500 applies.\n")])
    case("fabricated amount fails", any("7,500" in x for x in fails))

    fails, _ = tieout.check(quote, [("a.md", body + "\nAdd 75 hours of enablement.\n")])
    case("fabricated hours fail", any("75 hours" in x for x in fails))

    fails, _ = tieout.check(quote, [("a.md", body + "\nMargin improves to 61%.\n")])
    case("unsourced percentage fails", any("61%" in x for x in fails))

    dropped_body = body.replace("| Solution Architect | 320 hours | $275 |\n", "")
    _, warns = tieout.check(quote, [("a.md", dropped_body)])
    case("dropped role row warns on hours and rate",
         any("SA hours" in x for x in warns) and any("SA rate" in x for x in warns))

    _, warns = tieout.check(quote, [("a.md", body.replace(
        "- Workday integration, outbound only", "- Integration work"))])
    case("dropped scope line warns", any("scope line absent" in x for x in warns))

    fenced = body + "\n```\nA fenced figure of $555,555 must be ignored.\n```\n"
    fails, _ = tieout.check(quote, [("a.md", fenced)])
    case("figures inside code fences are skipped",
         not any("555,555" in x for x in fails))

    fails, _ = tieout.check(quote, [
        ("a.md", body), ("b.md", "Second artifact says the fee is $218,000.\n")])
    case("multiple artifacts reconcile together", fails == [], "; ".join(fails))

    bad = [n for n, ok, _ in results if not ok]
    print("\n%d/%d cases passed." % (len(results) - len(bad), len(results)))
    if bad:
        print("FAILED: %s" % ", ".join(bad))
        return 1
    print("SELFTEST PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
