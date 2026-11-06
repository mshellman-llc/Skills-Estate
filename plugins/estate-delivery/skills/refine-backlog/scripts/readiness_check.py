#!/usr/bin/env python3
"""Grade backlog items against INVEST and the team's definition of ready.

Input is the Requirements tab produced by capture-requirements, exported as CSV,
or a JSON list with the same fields. The delivery team adds three columns during
refinement: Estimate Days, Depends On and Refinement Sessions.

Verdicts:
    READY      score >= threshold, estimated and testable
    REFINE     fixable gaps; the report names each failed criterion
    DISCOVERY  score <= 2, or still not ready after three refinement sessions

Exit codes: 0 when every graded item is READY, 1 when any item is not READY,
2 when the input cannot be read or an item has no requirement number.

Usage:
    python3 readiness_check.py requirements.csv
    python3 readiness_check.py requirements.csv --raid-log RAID.md --ids CPE-001,CPE-002
    python3 readiness_check.py requirements.csv --format json --output readiness.json

Standard library only. See ../LICENSE-UPSTREAM and ../UPSTREAM.md for notices.
"""

import argparse
import csv
import io
import json
import re
import sys
from pathlib import Path

FIELDS = {
    "id": ("Requirement Number", "requirement_number", "id"),
    "name": ("Name", "name", "title"),
    "epic": ("Epic", "epic"),
    "as_a": ("As A", "as_a"),
    "i_want_to": ("I Want To", "i_want_to"),
    "so_that": ("So That", "so_that"),
    "acceptance": ("Acceptance Criteria", "acceptance_criteria"),
    "priority": ("Priority", "priority"),
    "status": ("Status", "status"),
    "notes": ("Assumptions & Notes", "assumptions_notes", "notes"),
    "estimate_days": ("Estimate Days", "estimate_days"),
    "depends_on": ("Depends On", "depends_on", "dependencies"),
    "sessions": ("Refinement Sessions", "refinement_sessions"),
}
IMPLEMENTATION_TERMS = re.compile(
    r"\b(api|endpoint|json|database table|db column|react component|apex|lwc|http|"
    r"status code|sql|stored procedure)\b",
    re.IGNORECASE,
)
GENERIC_VALUE = re.compile(r"^(so that )?(i can (use|do|see) (it|this)|it works|we have it|the system works)\.?$", re.IGNORECASE)
RAID_ID = re.compile(r"\bD-\d{3,}\b")


def pick(row, key):
    for name in FIELDS[key]:
        if name in row and row[name] not in (None, ""):
            return row[name]
    return ""


def normalise(row):
    if not isinstance(row, dict):
        raise ValueError(f"each requirement must be an object, got {row!r}")
    item = {key: pick(row, key) for key in FIELDS}
    deps = item["depends_on"]
    if isinstance(deps, str):
        deps = [d.strip() for d in re.split(r"[,;\s]+", deps) if d.strip()]
    elif not isinstance(deps, list):
        deps = [str(deps)]
    item["depends_on"] = [str(d).strip() for d in deps if str(d).strip()]
    for key in ("estimate_days", "sessions"):
        try:
            item[key] = float(item[key]) if item[key] != "" else None
        except (TypeError, ValueError):
            item[key] = None
    for key in FIELDS:
        if key in ("depends_on", "estimate_days", "sessions"):
            continue
        item[key] = str(item[key]).strip()
    return item


def load(path):
    text = Path(path).read_text(encoding="utf-8-sig")
    if path.lower().endswith(".json"):
        data = json.loads(text)
        rows = data.get("requirements") if isinstance(data, dict) else data
        if not isinstance(rows, list):
            raise ValueError("expected a JSON list of requirements, or an object with a requirements list")
    else:
        rows = list(csv.DictReader(io.StringIO(text, newline="")))
    return [normalise(row) for row in rows]


def scenarios(acceptance):
    """Split Gherkin text into scenarios and report which keywords each contains."""
    # Scenario headings separate scenarios; blank lines inside a scenario are valid Gherkin.
    # Text without headings falls back to blank-line separation.
    if re.search(r"^\s*Scenario", acceptance, flags=re.MULTILINE | re.IGNORECASE):
        pattern = r"(?=^\s*Scenario)"
    else:
        pattern = r"\n\s*\n"
    blocks = [b for b in re.split(pattern, acceptance, flags=re.MULTILINE | re.IGNORECASE) if b.strip()]
    result = []
    for block in blocks:
        words = {w.lower() for w in re.findall(r"^\s*(Given|When|Then)\b", block, flags=re.MULTILINE | re.IGNORECASE)}
        result.append({"complete": {"given", "when", "then"} <= words, "text": block.strip()})
    return result


def grade(item, raid_ids, max_days, threshold):
    criteria = {}

    deps = item["depends_on"]
    untracked = [d for d in deps if not (RAID_ID.fullmatch(d) and (raid_ids is None or d in raid_ids))]
    criteria["Independent"] = (
        not untracked,
        "No dependencies." if not deps
        else "Dependencies are tracked in the RAID log: " + ", ".join(deps) + "." if not untracked
        else "Untracked dependencies: " + ", ".join(untracked) + ". Record each in the RAID log or split the item.",
    )

    want = item["i_want_to"]
    impl = IMPLEMENTATION_TERMS.findall(want)
    criteria["Negotiable"] = (
        bool(want) and len(want) <= 400 and not impl,
        "The I Want To statement is missing." if not want
        else f"The I Want To statement has {len(want)} characters and likely prescribes the build." if len(want) > 400
        else "The I Want To statement names implementation terms: " + ", ".join(sorted({t.lower() for t in impl})) + "." if impl
        else "The I Want To statement leaves the build open.",
    )

    value = item["so_that"]
    restates = value and want and value.lower().rstrip(".") == want.lower().rstrip(".")
    criteria["Valuable"] = (
        bool(value) and not restates and not GENERIC_VALUE.match(value) and len(value.split()) >= 4,
        "The So That statement is missing." if not value
        else "The So That statement repeats the I Want To statement." if restates
        else "The So That statement does not say what changes for the user or the business." if GENERIC_VALUE.match(value) or len(value.split()) < 4
        else "The So That statement gives a reason.",
    )

    days = item["estimate_days"]
    estimable = days is not None and days > 0
    criteria["Estimable"] = (
        estimable,
        f"The team estimated {days:g} days." if estimable else "No team estimate. Estimates come from the delivery team during refinement.",
    )
    criteria["Small"] = (
        estimable and days <= max_days,
        "No estimate to compare." if not estimable
        else f"{days:g} days fits the {max_days:g}-day limit." if days <= max_days
        else f"{days:g} days exceeds the {max_days:g}-day limit. Split it with a recipe from references/splitting.md.",
    )

    found = scenarios(item["acceptance"]) if item["acceptance"] else []
    complete = [s for s in found if s["complete"]]
    ac_impl = IMPLEMENTATION_TERMS.findall(item["acceptance"])
    criteria["Testable"] = (
        bool(complete),
        "No acceptance criteria." if not found
        else f"{len(complete)} of {len(found)} scenarios have Given, When and Then." if complete
        else "No scenario has all of Given, When and Then.",
    )

    score = sum(1 for passed, _ in criteria.values() if passed)
    notes = []
    if found and len(complete) < len(found):
        notes.append(f"{len(found) - len(complete)} scenario(s) lack Given, When or Then.")
    if ac_impl:
        notes.append("Acceptance criteria name implementation terms (" + ", ".join(sorted({t.lower() for t in ac_impl})) + "); rewrite them as observable outcomes.")
    if item["status"] and item["status"] not in ("Reviewed", "Approved"):
        notes.append(f"Status is {item['status']}; stakeholders have not reviewed it.")
    sessions = item["sessions"] or 0

    if score <= 2 or (sessions >= 3 and score < threshold):
        verdict = "DISCOVERY"
        if sessions >= 3:
            notes.append(f"Refined {sessions:g} times without becoming ready; route the open question to discovery with an owner.")
    elif score >= threshold and criteria["Estimable"][0] and criteria["Testable"][0]:
        verdict = "READY"
    else:
        verdict = "REFINE"

    return {
        "id": item["id"],
        "name": item["name"],
        "epic": item["epic"],
        "priority": item["priority"],
        "score": score,
        "verdict": verdict,
        "criteria": {name: {"pass": passed, "reason": reason} for name, (passed, reason) in criteria.items()},
        "notes": notes,
    }


def markdown(report):
    s = report["summary"]
    lines = [
        "# Backlog readiness",
        "",
        f"{s['graded']} items graded: {s['READY']} ready, {s['REFINE']} to refine, {s['DISCOVERY']} to discovery. "
        f"Ready means a score of at least {s['threshold']} of 6 with an estimate and a complete Gherkin scenario. "
        f"Small means {s['max_days']:g} days or less.",
        "",
        "| ID | Name | Priority | Score | Verdict | Failed criteria |",
        "|---|---|---|---:|---|---|",
    ]
    for r in report["items"]:
        failed = ", ".join(k for k, v in r["criteria"].items() if not v["pass"]) or "none"
        lines.append(f"| {r['id']} | {r['name']} | {r['priority']} | {r['score']}/6 | {r['verdict']} | {failed} |")
    for r in report["items"]:
        if r["verdict"] == "READY" and not r["notes"]:
            continue
        lines += ["", f"## {r['id']} {r['name']}", ""]
        lines += [f"- {k}: {v['reason']}" for k, v in r["criteria"].items() if not v["pass"]]
        lines += [f"- {n}" for n in r["notes"]]
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Grade backlog items against INVEST and the definition of ready.")
    parser.add_argument("requirements", help="Requirements tab as CSV, or JSON")
    parser.add_argument("--raid-log", help="RAID log Markdown; dependencies must be D-### IDs in it")
    parser.add_argument("--ids", help="Comma-separated requirement numbers to grade (default: all)")
    parser.add_argument("--max-days", type=float, default=5.0)
    parser.add_argument("--threshold", type=int, default=5)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    try:
        items = load(args.requirements)
        raid_ids = set(RAID_ID.findall(Path(args.raid_log).read_text(encoding="utf-8"))) if args.raid_log else None
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    if not items:
        print("error: no requirements to grade", file=sys.stderr)
        return 2
    first = 1 if args.requirements.lower().endswith(".json") else 2
    label = "items" if first == 1 else "rows"
    missing = [i for i, item in enumerate(items, start=first) if not item["id"]]
    if missing:
        print(f"error: {label} without a Requirement Number: " + ", ".join(map(str, missing)), file=sys.stderr)
        return 2
    if args.ids:
        wanted = {i.strip() for i in args.ids.split(",") if i.strip()}
        if not wanted:
            print("error: --ids names no requirement", file=sys.stderr)
            return 2
        unknown = wanted - {item["id"] for item in items}
        if unknown:
            print("error: IDs not in the backlog: " + ", ".join(sorted(unknown)), file=sys.stderr)
            return 2
        items = [item for item in items if item["id"] in wanted]
    graded = [grade(item, raid_ids, args.max_days, args.threshold) for item in items]
    summary = {"graded": len(graded), "threshold": args.threshold, "max_days": args.max_days}
    summary.update({v: sum(1 for g in graded if g["verdict"] == v) for v in ("READY", "REFINE", "DISCOVERY")})
    report = {"summary": summary, "items": graded}
    text = json.dumps(report, indent=2) if args.format == "json" else markdown(report)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0 if summary["READY"] == len(graded) else 1


if __name__ == "__main__":
    sys.exit(main())
