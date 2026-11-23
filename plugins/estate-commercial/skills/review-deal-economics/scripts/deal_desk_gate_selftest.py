#!/usr/bin/env python3
"""Selftest for deal_desk_gate.py.

Runs the gate against the passing and failing fixtures via subprocess to
verify exit codes, then mutates the passing figures block in memory to
verify each individual check fires on its own. Exit 0 when every case
behaves, 1 otherwise.
"""

import copy
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(HERE, "deal_desk_gate.py")
PASSING = os.path.join(HERE, "fixtures", "passing.md")
FAILING = os.path.join(HERE, "fixtures", "failing.md")
RANGE_HIDDEN = os.path.join(HERE, "fixtures", "range_hidden.md")

sys.path.insert(0, HERE)
import deal_desk_gate as gate  # noqa: E402

results = []


def case(name, ok, detail=""):
    results.append((name, ok, detail))
    print("%s %s%s" % ("ok " if ok else "FAIL", name, (" :: " + detail) if detail else ""))


def wrap(fig):
    return "packet body\n\n```deal-desk-figures\n%s\n```\n" % json.dumps(fig)


def load_passing_fig():
    with open(PASSING, encoding="utf-8") as f:
        text = f.read()
    raw = re.search(r"```deal-desk-figures\s*\n(.*?)```", text, re.DOTALL).group(1)
    return json.loads(raw)


def main():
    # Exit codes through the real CLI.
    p = subprocess.run([sys.executable, GATE, PASSING], capture_output=True, text=True)
    case("passing fixture exits 0", p.returncode == 0, p.stdout.strip().splitlines()[-1] if p.stdout else "")
    f = subprocess.run([sys.executable, GATE, FAILING], capture_output=True, text=True)
    case("failing fixture exits nonzero", f.returncode == 1)
    expected_fails = [
        "internal_cost mismatch", "stated_margin_pct", "verification date",
        "margin_vs_floor", "approval_route", "delivery_cosign.status",
    ]
    for needle in expected_fails:
        case("failing fixture flags: %s" % needle, needle in f.stdout)
    case("no figures block exits nonzero via check()", bool(gate.check("no block here")))

    # Targeted mutations of the clean block. Each must produce failures.
    base = load_passing_fig()
    case("clean block passes check()", gate.check(wrap(base)) == [])

    def mutated(mutate):
        fig = copy.deepcopy(base)
        mutate(fig)
        return gate.check(wrap(fig))

    case("bad stated margin fires",
         any("stated_margin_pct" in x for x in mutated(lambda g: g.update(stated_margin_pct=60))))
    case("bad internal cost fires",
         any("internal_cost mismatch" in x for x in mutated(lambda g: g.update(internal_cost=90000))))
    case("T&M fee drift fires",
         any("fee mismatch" in x for x in mutated(lambda g: g.update(fee=230000))))
    case("blank cosign status fires",
         any("delivery_cosign.status" in x
             for x in mutated(lambda g: g["delivery_cosign"].update(status=""))))
    case("cosign 'assumed' fires",
         any("delivery_cosign.status" in x
             for x in mutated(lambda g: g["delivery_cosign"].update(status="assumed"))))
    case("confirmed cosign without a name fires",
         any("no named individual" in x
             for x in mutated(lambda g: g["delivery_cosign"].update(by=""))))
    case("missing floor key fires",
         any("missing keys" in x for x in mutated(lambda g: g.pop("margin_floor_pct"))))
    case("undated floor source fires",
         any("verification date" in x for x in mutated(lambda g: g.update(floor_source="canon"))))
    case("wrong floor verdict fires",
         any("margin_vs_floor" in x for x in mutated(lambda g: g.update(margin_vs_floor="below"))))
    case("wrong approval route fires",
         any("approval_route" in x for x in mutated(lambda g: g.update(approval_route="ELT"))))
    case("two approval actions fire",
         any("single value" in x
             for x in mutated(lambda g: g.update(approval_action=["approve", "reject"]))))
    case("bad pricing model fires",
         any("pricing_model" in x for x in mutated(lambda g: g.update(pricing_model="both"))))

    def below_floor(g):
        # Push cost up so margin lands between 42 and 45: cost 123000 -> 43.58%.
        g["roles"] = [{"role": "SA", "hours": 1000, "rate": 218, "cost_rate": 123}]
        g["internal_cost"] = 123000
        g["stated_margin_pct"] = 43.58
        g["margin_vs_floor"] = "below"
        g["approval_route"] = "Deal Desk + CEO"
    case("below-floor packet with correct route and verdict passes",
         mutated(below_floor) == [])

    def below_floor_wrong_route(g):
        below_floor(g)
        g["approval_route"] = "AE"
    case("below-floor packet routed to AE fires",
         any("approval_route" in x for x in mutated(below_floor_wrong_route)))

    # Issue 160: an optional margin_range_pct whose low end governs the floor
    # verdict and the approval route.
    r = subprocess.run([sys.executable, GATE, RANGE_HIDDEN], capture_output=True, text=True)
    case("range fixture with point-set verdict and route exits nonzero", r.returncode == 1)
    case("range fixture flags the verdict set from the point figure",
         "margin_vs_floor says 'above'" in r.stdout and "margin_range_pct" in r.stdout)
    case("range fixture flags the route set from the point figure",
         "approval_route 'AE'" in r.stdout and "'ELT' band" in r.stdout)

    def with_range(g, rng, verdict="below", route="ELT"):
        g["margin_range_pct"] = rng
        g["margin_vs_floor"] = verdict
        g["approval_route"] = route

    case("range low below floor with verdict and route from the low end passes",
         mutated(lambda g: with_range(g, {"low": 15, "expected": 52.84})) == [])
    case("range with low, expected and high passes",
         mutated(lambda g: with_range(g, {"low": 43, "expected": 52.84, "high": 60},
                                      route="Deal Desk + CEO")) == [])
    case("range low in a middle band routes by that band",
         any("approval_route" in x for x in mutated(
             lambda g: with_range(g, {"low": 43, "expected": 52.84}, route="ELT"))))
    case("range low above the floor keeps the point-figure result",
         mutated(lambda g: g.update(margin_range_pct={"low": 50, "expected": 52.84, "high": 55})) == [])
    case("range low below floor with verdict 'above' fires",
         any("margin_vs_floor" in x for x in mutated(
             lambda g: with_range(g, {"low": 15, "expected": 52.84}, verdict="above"))))
    case("range low below floor with route from the point figure fires",
         any("approval_route" in x for x in mutated(
             lambda g: with_range(g, {"low": 15, "expected": 52.84}, route="AE"))))
    case("range without a low end fires",
         any("margin_range_pct" in x for x in mutated(
             lambda g: g.update(margin_range_pct={"expected": 52.84}))))
    case("range with a non-numeric low fires",
         any("margin_range_pct" in x for x in mutated(
             lambda g: g.update(margin_range_pct={"low": "n/a"}))))
    case("range out of order fires",
         any("ordered" in x for x in mutated(
             lambda g: with_range(g, {"low": 60, "expected": 52.84}, verdict="above", route="AE"))))
    case("range expected that disagrees with the stated margin fires",
         any("expected" in x for x in mutated(
             lambda g: with_range(g, {"low": 15, "expected": 40}))))
    case("range low above the recomputed margin fires",
         any("above the recomputed margin" in x for x in mutated(
             lambda g: g.update(margin_range_pct={"low": 58}))))

    bad = [n for n, ok, _ in results if not ok]
    print("\n%d/%d cases passed." % (len(results) - len(bad), len(results)))
    if bad:
        print("FAILED: %s" % ", ".join(bad))
        return 1
    print("SELFTEST PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
