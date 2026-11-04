#!/usr/bin/env python3
"""Rank candidates with one prioritization framework and check the evidence behind each score.

Frameworks:
    rice         (reach x impact x confidence) / effort
    ice          impact x confidence x ease
    opportunity  importance x (1 - satisfaction)                   (Olsen; importance 0-10, satisfaction 0-1)
    odi          importance + max(importance - satisfaction, 0)   (Ulwick; both 0-10, customer ratings)
    wsjf         (business_value + time_criticality + risk_reduction) / job_size
    weighted     sum(weight x criterion score); criteria and weights in the input file

Evidence rules:
    - A confidence above 0.5 needs a named source in sources.confidence; otherwise it is capped at 0.5.
    - Effort or job size without sources.effort is flagged: an engineer has not sized it.
    - Opportunity and ODI scores without sources.importance are internal estimates and are labelled as hypotheses.
    - When more than 30% of items share the maximum impact, the impact scale ranks nothing.

The ranking is a proposal for the people who own the decision. It does not change the
MoSCoW priority recorded by requirements-capture.

Exit codes: 0 when every item scored, 1 when an item is missing a required field or
an ID repeats, 2 when the input cannot be read.

Usage:
    python3 priority_score.py candidates.json --framework rice
    python3 priority_score.py candidates.json --framework wsjf --format json

Standard library only. Framework formulas follow prioritization_scorer.py in the
Claude Skills Library (MIT + Commons Clause); see ../UPSTREAM.md.
"""

import argparse
import json
import sys
from pathlib import Path

REQUIRED = {
    "rice": ("reach", "impact", "confidence", "effort"),
    "ice": ("impact", "confidence", "ease"),
    "opportunity": ("importance", "satisfaction"),
    "odi": ("importance", "satisfaction"),
    "wsjf": ("business_value", "time_criticality", "risk_reduction", "job_size"),
    "weighted": (),
}
RICE_IMPACT = (0.25, 0.5, 1, 2, 3)


def as_fraction(value):
    value = float(value)
    return value / 100 if value > 1 else value


def is_number(value):
    if isinstance(value, bool):
        return False
    try:
        float(value)
    except (TypeError, ValueError):
        return False
    return True


def score_item(item, framework, criteria):
    sources = item.get("sources") or {}
    flags = []
    v = {k: item.get(k) for k in REQUIRED[framework]}
    missing = [k for k, val in v.items() if val is None]
    if framework == "weighted":
        scores = item.get("scores") or {}
        missing = [c["name"] for c in criteria if c["name"] not in scores]
    if missing:
        return None, ["Missing " + ", ".join(missing) + "."]
    values = dict(v)
    if framework == "weighted":
        values.update({c["name"]: scores[c["name"]] for c in criteria})
    bad = [f"{k}={val!r}" for k, val in values.items() if not is_number(val)]
    if bad:
        return None, ["Not a number: " + ", ".join(bad) + "."]

    if framework in ("rice", "ice"):
        confidence = as_fraction(v["confidence"])
        if confidence > 0.5 and not sources.get("confidence"):
            flags.append(f"Confidence {confidence:.0%} has no source; capped at 50%.")
            confidence = 0.5
    if framework in ("rice", "wsjf") and not sources.get("effort"):
        flags.append("Effort has no engineering source; do not publish this score until an engineer sizes it.")

    if framework == "rice":
        impact = float(v["impact"])
        if impact not in RICE_IMPACT:
            flags.append(f"Impact {impact:g} is off the RICE scale (0.25, 0.5, 1, 2, 3).")
        effort = float(v["effort"])
        if effort <= 0:
            return None, ["Effort must be greater than zero."]
        score = float(v["reach"]) * impact * confidence / effort
        formula = f"({float(v['reach']):g} x {impact:g} x {confidence:g}) / {effort:g}"
    elif framework == "ice":
        score = float(v["impact"]) * confidence * float(v["ease"])
        formula = f"{float(v['impact']):g} x {confidence:g} x {float(v['ease']):g}"
    elif framework == "opportunity":
        imp, sat = float(v["importance"]), float(v["satisfaction"])
        if sat > 1:
            flags.append(f"Satisfaction {sat:g} read as a 0-10 rating and converted to {sat / 10:g}.")
            sat = sat / 10
        score = imp * (1 - sat)
        formula = f"{imp:g} x (1 - {sat:g})"
    elif framework == "odi":
        imp, sat = float(v["importance"]), float(v["satisfaction"])
        score = imp + max(imp - sat, 0)
        formula = f"{imp:g} + max({imp:g} - {sat:g}, 0)"
    elif framework == "wsjf":
        size = float(v["job_size"])
        if size <= 0:
            return None, ["Job size must be greater than zero."]
        cost_of_delay = float(v["business_value"]) + float(v["time_criticality"]) + float(v["risk_reduction"])
        score = cost_of_delay / size
        formula = f"({float(v['business_value']):g} + {float(v['time_criticality']):g} + {float(v['risk_reduction']):g}) / {size:g}"
    else:
        scores = item["scores"]
        parts = [(c["name"], float(c["weight"]), float(scores[c["name"]])) for c in criteria]
        score = sum(w * s for _, w, s in parts)
        formula = " + ".join(f"{w:g} x {s:g}" for _, w, s in parts)

    if framework in ("opportunity", "odi") and not sources.get("importance"):
        flags.append("Importance and satisfaction are internal estimates, not customer ratings; treat the rank as a hypothesis.")
    if not item.get("job") and not item.get("problem"):
        flags.append("No job or problem is named; rank the problem before the solution (see jtbd-framing).")
    return {"score": round(score, 2), "formula": formula}, flags


def run(data, framework):
    items = data.get("items") if isinstance(data, dict) else data
    if not isinstance(items, list):
        raise ValueError("expected a JSON list of items, or an object with an items list")
    criteria = data.get("criteria", []) if isinstance(data, dict) else []
    errors, notes = [], []
    if framework == "weighted":
        if not criteria:
            return None, ["Weighted scoring needs a criteria list with name and weight."], []
        if any(not isinstance(c, dict) or "name" not in c or not is_number(c.get("weight")) for c in criteria):
            return None, ["Each criterion needs a name and a numeric weight."], []
        total = sum(float(c["weight"]) for c in criteria)
        if total <= 0:
            return None, ["Criterion weights must sum to more than zero."], []
        if abs(total - 1) > 0.01:
            notes.append(f"Criterion weights sum to {total:g}; they were normalised to 1.")
            criteria = [{**c, "weight": float(c["weight"]) / total} for c in criteria]
    seen, rows, impacts = set(), [], []
    for item in items:
        if not isinstance(item, dict):
            errors.append(f"An item is not an object: {item!r}.")
            continue
        iid = item.get("id")
        if not iid:
            errors.append(f"An item has no ID: {item.get('title', '(untitled)')}.")
            continue
        if iid in seen:
            errors.append(f"ID {iid} appears more than once.")
            continue
        seen.add(iid)
        result, flags = score_item(item, framework, criteria)
        if result is None:
            errors.append(f"{iid}: " + " ".join(flags))
            continue
        if framework in ("rice", "ice"):
            impacts.append(float(item["impact"]))
        rows.append({"id": iid, "title": item.get("title", ""), "job": item.get("job") or item.get("problem") or "", **result, "flags": flags})
    if framework in ("rice", "ice") and rows:
        top = max(impacts)
        share = impacts.count(top) / len(rows)
        if share > 0.3 and len(rows) >= 4:
            notes.append(f"{share:.0%} of items share the highest impact ({top:g}). Recalibrate: keep the top value only where there is behavioural or revenue evidence.")
    rows.sort(key=lambda r: r["score"], reverse=True)
    for rank, row in enumerate(rows, start=1):
        row["rank"] = rank
    ties = sorted({r["score"] for r in rows if sum(1 for x in rows if x["score"] == r["score"]) > 1})
    if ties:
        notes.append("Tied scores: " + ", ".join(f"{t:g}" for t in ties) + ". Break ties in the decision meeting, not in the formula.")
    return rows, errors, notes


def markdown(framework, rows, errors, notes):
    lines = [f"# Prioritization: {framework.upper()}", "", "This ranking is a proposal. The decision owner sets the order; requirements-capture keeps its MoSCoW values.", ""]
    if rows:
        lines += ["| Rank | ID | Title | Score | Formula | Flags |", "|---:|---|---|---:|---|---|"]
        for r in rows:
            lines.append(f"| {r['rank']} | {r['id']} | {r['title']} | {r['score']:g} | {r['formula']} | {' '.join(r['flags']) or 'none'} |")
    if notes:
        lines += ["", "Notes:"] + [f"- {n}" for n in notes]
    if errors:
        lines += ["", "Not scored:"] + [f"- {e}" for e in errors]
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Rank candidates and check the evidence behind each score.")
    parser.add_argument("candidates", help="JSON list of items, or an object with items and criteria")
    parser.add_argument("--framework", required=True, choices=sorted(REQUIRED))
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    try:
        data = json.loads(Path(args.candidates).read_text(encoding="utf-8"))
        rows, errors, notes = run(data, args.framework)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    if rows is None:
        print("error: " + " ".join(errors), file=sys.stderr)
        return 2
    text = (json.dumps({"framework": args.framework, "ranking": rows, "errors": errors, "notes": notes}, indent=2)
            if args.format == "json" else markdown(args.framework, rows, errors, notes))
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
