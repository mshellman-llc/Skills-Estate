#!/usr/bin/env python3
"""Check the outcome discipline of a now/next/later roadmap plan.

Usage: outcome_check.py PLAN.json [--max-now 3] [--format markdown|json]

Reads every `board` block whose columns include Now. Fails when Now holds more
cards than --max-now, when a Now card has no Outcome field, or when a Now
Outcome names no number to measure against. Warns when a Now Outcome has no
baseline, a Next card has no Outcome, a Later card carries dates or priority
labels, two cards share an Outcome, a Now card has no named owner, or a Now
card cites nothing in a plan not marked as example data.

Exit codes: 0 no failures, 1 at least one failure, 2 input error.
Runs on Python 3.9 with the standard library only.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# A measurable number: a digit not glued to a preceding letter, so SOC2, v2 and Q3 do not count.
NUMBER = re.compile(r"(?<![A-Za-z])\d|\bzero\b", re.I)
MONTH = (r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|"
         r"sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\.?")
BASELINE = re.compile(r"→|->|\bfrom\b.+\bto\b|\bbaseline\b", re.I)
LATER_PRECISION = re.compile(
    r"\bQ[1-4]\s*\d{4}\b|\b\d{4}-\d{2}-\d{2}\b|\bP[0-3]\b|"
    r"\b" + MONTH + r"\s+\d{1,2}\b|"
    r"\b\d{1,2}\s+" + MONTH + r"\b",
    re.I,
)
HORIZONS = ("now", "next", "later")


def horizon(column):
    for value in (column.get("id", ""), column.get("title", "")):
        key = str(value).strip().lower()
        if key in HORIZONS:
            return key
    return None


def outcome_of(card):
    fields = card.get("fields") or {}
    if isinstance(fields, list):
        fields = {str(k): v for k, v in fields}
    for key, value in fields.items():
        if key.strip().lower() == "outcome":
            return str(value).strip()
    return ""


def card_text(card):
    parts = [str(card.get("title", "")), str(card.get("body", ""))]
    fields = card.get("fields") or {}
    items = fields if isinstance(fields, list) else fields.items()
    parts += [f"{k} {v}" for k, v in items]
    return " ".join(parts)


def check(plan, max_now):
    findings = []

    def add(level, card, message):
        findings.append({"level": level, "card": card, "message": message})

    if not isinstance(plan, dict) or not isinstance(plan.get("blocks", []), list):
        raise ValueError("the plan must be a JSON object with a blocks list")
    boards = []
    for block in plan.get("blocks", []):
        if not isinstance(block, dict):
            raise ValueError(f"each block must be an object, got {block!r}")
        if block.get("type") != "board":
            continue
        cols = {c.get("id"): horizon(c) for c in block.get("columns", [])}
        if "now" in cols.values():
            boards.append((block, cols))
    if not boards:
        raise ValueError("no board block with a Now column")

    example = "example" in str(plan.get("meta", {}).get("source", "")).lower()
    seen = {}
    for block, cols in boards:
        cards = block.get("cards", [])
        now = [c for c in cards if cols.get(c.get("col")) == "now"]
        if len(now) > max_now:
            add("fail", None, f"Now holds {len(now)} cards; the cap is {max_now}. Move the rest to Next or show why the team can carry them.")
        for card in cards:
            where = cols.get(card.get("col"))
            cid = card.get("id") or card.get("title", "?")
            outcome = outcome_of(card)
            if outcome:
                key = re.sub(r"\W+", " ", outcome.lower()).strip()
                if key in seen:
                    add("warn", cid, f"Outcome repeats card {seen[key]}; each card needs its own measurable change.")
                else:
                    seen[key] = cid
            if where == "now":
                if not outcome:
                    add("fail", cid, "Now card has no Outcome field.")
                elif not NUMBER.search(outcome):
                    add("fail", cid, f"Now Outcome names no number to measure: \"{outcome}\".")
                elif not BASELINE.search(outcome):
                    add("warn", cid, f"Now Outcome has a target but no baseline: \"{outcome}\".")
                owner = card.get("owner")
                owner = "" if owner is None else str(owner).strip()
                if not owner or owner.upper() == "TBD":
                    add("warn", cid, "Now card has no named owner.")
                if not example and not card.get("cite"):
                    add("warn", cid, "Now card cites no evidence for its problem or outcome.")
            elif where == "next" and not outcome:
                add("warn", cid, "Next card has no Outcome field.")
            elif where == "later":
                hit = LATER_PRECISION.search(card_text(card))
                if hit:
                    add("warn", cid, f"Later card carries precision it cannot support (\"{hit.group(0)}\"). Keep Later to the problem and intent.")
    return findings


def render(findings, path):
    lines = [f"# Outcome check: {path}", ""]
    if not findings:
        lines.append("No findings.")
    for f in findings:
        target = f" [{f['card']}]" if f["card"] else ""
        lines.append(f"- {f['level'].upper()}{target}: {f['message']}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("plan")
    parser.add_argument("--max-now", type=int, default=3)
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()
    try:
        plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
        findings = check(plan, args.max_now)
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps({"plan": args.plan, "findings": findings}, indent=2))
    else:
        print(render(findings, args.plan))
    return 1 if any(f["level"] == "fail" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
