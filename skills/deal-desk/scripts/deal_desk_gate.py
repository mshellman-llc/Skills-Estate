#!/usr/bin/env python3
"""Deal Desk packet gate.

Verifies the machine-readable figures block embedded in a Deal Desk packet.
The block is JSON inside either a fenced code block tagged deal-desk-figures
(markdown) or an HTML comment opening with deal-desk-figures (HTML).

Checks, all blocking:
  1. Block present, parses, required keys present.
  2. Arithmetic recomputes: internal cost from role hours x cost rate,
     fee from role hours x bill rate on T&M, margin from fee and cost.
     Stated figures must match recomputed figures within tolerance.
  3. Margin floor present with a dated source, and the stated
     margin_vs_floor verdict matches the arithmetic.
  4. Approval ladder present with a dated source; the stated approval
     route matches the band the recomputed margin lands in. The ladder
     values travel in the block, not in this script, so the script never
     becomes a stale copy of canon.
  5. Delivery cosign status explicitly set to an allowed value. Blank,
     null, assumed, or inferred all fail. Confirmed requires a name
     and date.
  6. Pricing model is exactly one of fixed_fee or t_and_m.
  7. Approval action is a single value from the allowed set.

Exit 0 on pass, 1 on any failure, 2 on unreadable input.
Usage: deal_desk_gate.py <packet.md|packet.html>
"""

import json
import re
import sys

MARGIN_TOLERANCE_PTS = 0.5   # percentage points
MONEY_TOLERANCE = 1.0        # dollars, absorbs rounding

REQUIRED_KEYS = [
    "source_quote", "as_of", "pricing_model", "fee", "roles",
    "internal_cost", "stated_margin_pct", "margin_floor_pct",
    "floor_source", "margin_vs_floor", "approval_ladder",
    "approval_ladder_source", "approval_route", "delivery_cosign",
    "approval_action",
]

COSIGN_STATUSES = {"confirmed", "conditional", "pending", "declined"}
COSIGN_FORBIDDEN = {"", "assumed", "inferred", "tbd", "n/a", "none", "null"}
APPROVAL_ACTIONS = {"approve", "approve_with_conditions", "reject", "not_ready"}
PRICING_MODELS = {"fixed_fee", "t_and_m"}

FENCE_RE = re.compile(r"```deal-desk-figures\s*\n(.*?)```", re.DOTALL)
COMMENT_RE = re.compile(r"<!--\s*deal-desk-figures\s*(.*?)-->", re.DOTALL)
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


def extract_block(text):
    m = FENCE_RE.search(text) or COMMENT_RE.search(text)
    return m.group(1) if m else None


def check(text):
    """Return a list of failure strings. Empty list means pass."""
    fails = []
    raw = extract_block(text)
    if raw is None:
        return ["no deal-desk-figures block found in the packet"]
    try:
        fig = json.loads(raw)
    except json.JSONDecodeError as e:
        return ["figures block is not valid JSON: %s" % e]

    missing = [k for k in REQUIRED_KEYS if k not in fig]
    if missing:
        fails.append("figures block missing keys: %s" % ", ".join(missing))
        return fails  # cannot check arithmetic against absent fields

    # Pricing model: exactly one, never both.
    model = fig["pricing_model"]
    if model not in PRICING_MODELS:
        fails.append("pricing_model must be fixed_fee or t_and_m, got %r" % model)

    # Roles and arithmetic.
    roles = fig["roles"]
    if not isinstance(roles, list) or not roles:
        fails.append("roles must be a non-empty list")
        return fails
    computed_cost = 0.0
    computed_billings = 0.0
    for i, r in enumerate(roles):
        for k in ("role", "hours", "rate", "cost_rate"):
            if k not in r:
                fails.append("role row %d missing %s" % (i, k))
        if any(k not in r for k in ("hours", "rate", "cost_rate")):
            return fails
        try:
            hours = float(r["hours"])
            rate = float(r["rate"])
            cost_rate = float(r["cost_rate"])
        except (TypeError, ValueError):
            fails.append("role row %d has non-numeric hours, rate, or cost_rate" % i)
            return fails
        computed_cost += hours * cost_rate
        computed_billings += hours * rate

    try:
        fee = float(fig["fee"])
        stated_cost = float(fig["internal_cost"])
        stated_margin = float(fig["stated_margin_pct"])
        floor = float(fig["margin_floor_pct"])
    except (TypeError, ValueError):
        fails.append("fee, internal_cost, stated_margin_pct, and margin_floor_pct must be numeric")
        return fails

    if abs(computed_cost - stated_cost) > MONEY_TOLERANCE:
        fails.append(
            "internal_cost mismatch: stated %.2f, recomputed %.2f from role hours x cost_rate"
            % (stated_cost, computed_cost))
    if model == "t_and_m" and abs(computed_billings - fee) > MONEY_TOLERANCE:
        fails.append(
            "fee mismatch on T&M: stated %.2f, recomputed %.2f from role hours x rate"
            % (fee, computed_billings))
    if fee <= 0:
        fails.append("fee must be positive")
        return fails

    real_margin = (fee - computed_cost) / fee * 100.0
    if abs(real_margin - stated_margin) > MARGIN_TOLERANCE_PTS:
        fails.append(
            "stated_margin_pct %.2f does not match recomputed %.2f (fee %.2f, cost %.2f)"
            % (stated_margin, real_margin, fee, computed_cost))

    # Floor comparison: present, sourced with a date, verdict matches arithmetic.
    floor_source = str(fig["floor_source"]).strip()
    if not floor_source:
        fails.append("floor_source is blank; the floor must cite where it was verified")
    elif not DATE_RE.search(floor_source):
        fails.append("floor_source carries no verification date (YYYY-MM-DD)")
    verdict = str(fig["margin_vs_floor"]).strip().lower()
    expected = "above" if real_margin >= floor else "below"
    if verdict not in ("above", "below"):
        fails.append("margin_vs_floor must be 'above' or 'below', got %r" % verdict)
    elif verdict != expected:
        fails.append(
            "margin_vs_floor says %r but recomputed margin %.2f is %s the %.2f floor"
            % (verdict, real_margin, expected, floor))

    # Approval ladder: sourced, and the stated route matches the band.
    ladder = fig["approval_ladder"]
    ladder_source = str(fig["approval_ladder_source"]).strip()
    if not ladder_source:
        fails.append("approval_ladder_source is blank")
    elif not DATE_RE.search(ladder_source):
        fails.append("approval_ladder_source carries no verification date (YYYY-MM-DD)")
    if not isinstance(ladder, list) or not ladder:
        fails.append("approval_ladder must be a non-empty list of bands")
    else:
        band = None
        try:
            for b in sorted(ladder, key=lambda b: float(b["min_margin_pct"]), reverse=True):
                if real_margin >= float(b["min_margin_pct"]):
                    band = b
                    break
            if band is None:
                band = min(ladder, key=lambda b: float(b["min_margin_pct"]))
        except (KeyError, TypeError, ValueError):
            fails.append("each approval_ladder band needs numeric min_margin_pct and an approver")
            band = None
        if band is not None:
            required = str(band.get("approver", "")).strip()
            stated_route = str(fig["approval_route"]).strip()
            if not required:
                fails.append("approval ladder band has no approver")
            elif stated_route.lower() != required.lower():
                fails.append(
                    "approval_route %r does not match ladder: margin %.2f lands in the %r band"
                    % (stated_route, real_margin, required))

    # Delivery cosign: explicit human input, never blank, never inferred.
    cosign = fig["delivery_cosign"]
    if not isinstance(cosign, dict):
        fails.append("delivery_cosign must be an object with status, by, date")
    else:
        status = str(cosign.get("status") or "").strip().lower()
        if status in COSIGN_FORBIDDEN or not status:
            fails.append(
                "delivery_cosign.status is blank or non-committal (%r); it must be one of %s"
                % (status, sorted(COSIGN_STATUSES)))
        elif status not in COSIGN_STATUSES:
            fails.append("delivery_cosign.status %r not in %s" % (status, sorted(COSIGN_STATUSES)))
        if status == "confirmed":
            if not str(cosign.get("by") or "").strip():
                fails.append("delivery_cosign confirmed but no named individual in 'by'")
            if not str(cosign.get("date") or "").strip():
                fails.append("delivery_cosign confirmed but no date")

    # Approval action: exactly one, from the allowed set.
    action = fig["approval_action"]
    if isinstance(action, list):
        fails.append("approval_action must be a single value, not a list")
    elif str(action).strip().lower() not in APPROVAL_ACTIONS:
        fails.append("approval_action %r not in %s" % (action, sorted(APPROVAL_ACTIONS)))

    return fails


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    try:
        with open(argv[1], encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print("FAIL cannot read %s: %s" % (argv[1], e))
        return 2
    fails = check(text)
    if fails:
        for f in fails:
            print("FAIL %s" % f)
        print("%d failure(s). The packet is not ready for Deal Desk." % len(fails))
        return 1
    print("PASS figures block verified: arithmetic recomputes, floor comparison present, cosign explicit.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
