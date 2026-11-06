#!/usr/bin/env python3
"""Deterministic figure gate for the ROM.

Consumes a figures block (a .json file, or the first fenced json block inside a
markdown/HTML build file), recomputes the three-way tie, the fee reconciliation,
the range bracket, and the model card, prints the full reconciliation, and exits
nonzero on any failure.

Usage:
    rom_gate.py <figures.json | build.md>
    rom_gate.py --selftest
"""

import json
import math
import re
import sys

HOURS_TOL = 0.01          # exact tie, rounding room only
FEE_TOL_PCT = 0.5         # percent tolerance on hours x rate vs fee

MODEL_CARDS = {"fixed_fee": "fixed_price", "t_and_m": "tm_envelope"}
REQUIRED = [
    "q_number", "pricing_model", "model_card",
    "quote_total_hours", "blended_rate", "quote_total_fee",
    "range_low", "range_high", "phases", "roles",
]

FENCE_RE = re.compile(r"```json\s*\n(.*?)```", re.DOTALL)


def load_figures(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    if path.endswith(".json"):
        return json.loads(text)
    m = FENCE_RE.search(text)
    if not m:
        raise ValueError("no fenced json figures block found in %s" % path)
    return json.loads(m.group(1))


def _sum(rows):
    return sum(float(r["hours"]) for r in rows)


def check(fig):
    """Return (lines, failures). lines is the printed reconciliation."""
    lines = []
    failures = []

    def flag(msg):
        failures.append(msg)
        lines.append("  FLAG: " + msg)

    if not isinstance(fig, dict):
        flag("figures must be a JSON object")
        return lines, failures
    missing = [k for k in REQUIRED if k not in fig]
    if missing:
        flag("missing required fields: " + ", ".join(missing))
        return lines, failures

    for key in ("q_number", "pricing_model", "model_card"):
        if not isinstance(fig[key], str) or not fig[key].strip():
            flag(key + " must be a nonempty string")

    def number(value, label):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            flag(label + " must be a number")
            return False
        try:
            valid = math.isfinite(value) and value >= 0
        except (OverflowError, ValueError):
            valid = False
        if not valid:
            flag(label + " must be finite and nonnegative")
        return valid

    for key in ("quote_total_hours", "blended_rate", "quote_total_fee", "range_low", "range_high"):
        number(fig[key], key)
    for key in ("phases", "roles", "work_packages"):
        if key not in fig:
            continue
        rows = fig[key]
        if not isinstance(rows, list):
            flag(key + " must be a list")
            continue
        for index, row in enumerate(rows):
            label = "%s[%d].hours" % (key, index)
            if not isinstance(row, dict) or "hours" not in row:
                flag(label + " is required on an object row")
            else:
                number(row["hours"], label)
    if failures:
        return lines, failures
    q = fig["q_number"]
    model = fig["pricing_model"]
    as_of = fig.get("as_of", "unstated")
    lines.insert(0, "ROM figure gate: %s (%s), as of %s" % (q, model, as_of))
    total_hours = float(fig["quote_total_hours"])
    rate = float(fig["blended_rate"])
    fee = float(fig["quote_total_fee"])
    low = float(fig["range_low"])
    high = float(fig["range_high"])
    # Three-way tie (two-way when work_packages absent).
    sums = [("phase hours total", _sum(fig["phases"])),
            ("role hours total", _sum(fig["roles"]))]
    wp = fig.get("work_packages")
    if wp:
        sums.append(("work package hours total", _sum(wp)))
    else:
        lines.append("  work packages: absent in source, tie is two-way")
    sums.append(("quote total hours", total_hours))

    if any(not math.isfinite(value) for _, value in sums):
        flag("summed hours overflow the finite numeric range")
        return lines, failures
    width = max(len(n) for n, _ in sums) + 1
    for name, val in sums:
        lines.append("  %s %.2f" % ((name + ":").ljust(width), val))
    tie_ok = all(abs(val - total_hours) <= HOURS_TOL for _, val in sums)
    tie_label = "three-way tie" if wp else "two-way tie"
    lines.append("  %s: %s" % (tie_label, "PASS" if tie_ok else "FAIL"))
    if not tie_ok:
        for name, val in sums[:-1]:
            delta = val - total_hours
            if abs(delta) > HOURS_TOL:
                flag("%s off quote total hours by %+.2f" % (name, delta))

    if model == "fixed_fee":
        if not isinstance(fig.get("fee_source"), str) or not fig["fee_source"].strip():
            flag("fixed_fee requires fee_source naming the authoritative quote or model")
        if not isinstance(fig.get("fixed_fee_basis"), str) or not fig["fixed_fee_basis"].strip():
            flag("fixed_fee requires fixed_fee_basis; do not infer fee from hours x rate")
        lines.append("  fixed fee: check authoritative fee_source and stated fixed_fee_basis")
    else:
        # Fee reconciliation for time-based fees only.
        computed = total_hours * rate
        delta = computed - fee
        pct = (abs(delta) / fee * 100.0) if fee else float("inf")
        fee_ok = math.isfinite(computed) and pct <= FEE_TOL_PCT
        lines.append(
            "  fee check: %.2f h x %.2f = %.2f vs quote fee %.2f (delta %.2f, %.3f%%): %s"
            % (total_hours, rate, computed, fee, delta, pct, "PASS" if fee_ok else "FAIL"))
        if not fee_ok:
            flag("hours x blended rate does not reconcile to the quote fee "
                 "(delta %.2f, %.3f%%, tolerance %.1f%%)" % (delta, pct, FEE_TOL_PCT))

    # Range brackets the quote total.
    range_ok = (0 < low < high) and (low <= fee <= high)
    lines.append("  range: %.2f to %.2f brackets quote total %.2f: %s"
                 % (low, high, fee, "PASS" if range_ok else "FAIL"))
    if not range_ok:
        flag("range bounds do not bracket the quote total "
             "(low %.2f, total %.2f, high %.2f)" % (low, fee, high))

    # Model card: exactly one, matching the model.
    card = fig["model_card"]
    expected = MODEL_CARDS.get(model)
    card_ok = expected is not None and card == expected
    lines.append("  model card: %s %s %s: %s"
                 % (card, "matches" if card_ok else "does not match", model,
                    "PASS" if card_ok else "FAIL"))
    if expected is None:
        flag("unknown pricing model %r (expected fixed_fee or t_and_m)" % model)
    elif not card_ok:
        flag("model card %r conflicts with pricing model %r; expected %r. "
             "Fixed-price and T&M cards never coexist." % (card, model, expected))

    lines.append("RESULT: %s (%d failure%s)"
                 % ("PASS" if not failures else "FAIL",
                    len(failures), "" if len(failures) == 1 else "s"))
    return lines, failures


def run(path):
    try:
        fig = load_figures(path)
    except (OSError, ValueError, json.JSONDecodeError) as e:
        print("ROM figure gate: cannot read figures block: %s" % e)
        return 1
    lines, failures = check(fig)
    print("\n".join(lines))
    return 1 if failures else 0


def selftest():
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    fixtures = os.path.join(here, "fixtures")
    cases = [("rom_pass.json", 0), ("rom_fail.json", 1)]
    bad = 0
    for name, expected in cases:
        path = os.path.join(fixtures, name)
        print("== selftest fixture: %s (expect exit %d) ==" % (name, expected))
        rc = run(path)
        ok = rc == expected
        print("== %s: exit %d, %s ==\n" % (name, rc, "OK" if ok else "SELFTEST FAIL"))
        if not ok:
            bad += 1
    print("selftest: %d/%d fixtures behaved as expected" % (len(cases) - bad, len(cases)))
    return 1 if bad else 0


def main(argv):
    if len(argv) != 2 or argv[1] in ("-h", "--help"):
        print(__doc__.strip())
        return 2
    if argv[1] == "--selftest":
        return selftest()
    return run(argv[1])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
