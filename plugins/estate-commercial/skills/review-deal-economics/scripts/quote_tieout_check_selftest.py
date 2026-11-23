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
DEMO_QUOTE = os.path.join(HERE, "fixtures", "tieout_demo_quote.json")

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

    # Issue 159: hours ranges are checked at both ends, the export carries
    # optional low, expected and high fields, and a figure that matches only by
    # number is a warning to confirm. The fictional quote Q-DEMO-1 has a
    # 10-hour Build phase and a Consultant range of 8 to 12 hours.
    with open(DEMO_QUOTE, encoding="utf-8") as fh:
        demo = json.load(fh)

    def demo_check(line):
        return tieout.check(demo, [("demo.md", line + "\n")])

    fails, _ = demo_check("The build takes 99 to 10 hours.")
    case("range with a wrong low end fails", any("99 hours" in x for x in fails), "; ".join(fails))
    fails, _ = demo_check("The build takes 10 to 99 hours.")
    case("range with a wrong high end fails", any("99 hours" in x for x in fails))
    fails, _ = demo_check("The build takes 99-10 hours.")
    case("hyphen range with a wrong low end fails", any("99 hours" in x for x in fails))
    fails, _ = demo_check("The build takes 99 hours.")
    case("single wrong hours figure still fails", any("99 hours" in x for x in fails))
    fails, _ = demo_check("The Consultant range is 8 to 12 hours.")
    case("range inside the low and high fields passes", fails == [], "; ".join(fails))
    fails, _ = demo_check("The Consultant range is 8-12 hours.")
    case("hyphen range inside the low and high fields passes", fails == [], "; ".join(fails))
    fails, _ = demo_check("The Consultant expects 10 hours at $200 each, 2,000 in total.")
    case("expected hours figure passes", fails == [], "; ".join(fails))
    fails, _ = demo_check("Consultant effort runs 8 to 13 hours.")
    case("range with a wrong high end against the high field fails",
         any("13 hours" in x for x in fails))

    fails, warns = demo_check("Headroom covers 10 hours of unbilled work.")
    case("value-only match does not fail", fails == [], "; ".join(fails))
    case("value-only match warns to confirm",
         any("matches a quote value by number only" in x and "10 hours" in x for x in warns),
         "; ".join(warns))
    fails, warns = demo_check("The Build phase takes 10 hours.")
    case("labelled match raises no value-only warning",
         fails == [] and not any("by number only" in x for x in warns), "; ".join(warns))
    fails, warns = demo_check("Delivery needs a $2,000 reserve for contingency.")
    case("value-only currency match warns to confirm",
         fails == [] and any("$2,000 matches a quote value by number only" in x for x in warns),
         "; ".join(warns))

    q = subprocess.run([sys.executable, CHECK, DEMO_QUOTE, os.path.join(HERE, "fixtures", "tieout_pass.md")],
                       capture_output=True, text=True)
    case("demo quote against an unrelated artifact exits 1", q.returncode == 1)

    bad = [n for n, ok, _ in results if not ok]
    print("\n%d/%d cases passed." % (len(results) - len(bad), len(results)))
    if bad:
        print("FAILED: %s" % ", ".join(bad))
        return 1
    print("SELFTEST PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
