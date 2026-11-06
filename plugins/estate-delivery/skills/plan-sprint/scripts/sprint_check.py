#!/usr/bin/env python3
"""Check a sprint plan before the team commits to it.

The check computes capacity from per-person inputs, compares committed and
stretch hours with the team's targets, and confirms that every committed item
is ready according to the refine-backlog report. Dependencies must cite a
RAID dependency ID that exists in the RAID log when one is supplied.

Exit codes: 0 when no fail finding exists, 1 when at least one fail finding
exists, 2 when the input cannot be read.

Usage:
    python3 sprint_check.py PLAN.json
    python3 sprint_check.py PLAN.json --readiness READINESS.json --raid-log RAID.md
    python3 sprint_check.py PLAN.json --format json

Standard library only. See ../LICENSE-UPSTREAM and ../UPSTREAM.md for notices.
"""

import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_COMMIT_PCT = 80.0
DEFAULT_STRETCH_PCT = 15.0
DEFAULT_FOCUS = 0.7
RAID_DEP_ID = re.compile(r"\bD-\d{3,}\b")


def number(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def field(record, key, default=0.0):
    """Read a numeric field. Absent or null means the default; anything else must be a number."""
    value = record.get(key)
    if value is None:
        return float(default)
    if isinstance(value, bool):
        raise ValueError(f"{key} must be a number, got {value!r}")
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{key} must be a number, got {value!r}") from None


def member_hours(member, sprint_days, hours_per_day, default_focus):
    """Return (effective hours, explanation). Supplied hours win over a calculation."""
    if member.get("available_hours") is not None:
        return field(member, "available_hours"), "supplied"
    days = field(member, "working_days", sprint_days) - field(member, "pto_days")
    per_day = field(member, "hours_per_day", hours_per_day)
    raw = max(days, 0) * per_day
    overhead = sum(field(member, key) for key in ("meeting_hours", "on_call_hours", "interrupt_hours"))
    focus = field(member, "focus_factor", default_focus)
    hours = max(raw - overhead, 0) * focus
    return hours, f"({days:g} d x {per_day:g} h - {overhead:g} h) x {focus:g}"


def load_readiness(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = data.get("items", data) if isinstance(data, dict) else data
    return {row["id"]: row for row in rows if isinstance(row, dict) and row.get("id")}


def load_raid_ids(path):
    return set(RAID_DEP_ID.findall(Path(path).read_text(encoding="utf-8")))


def check(plan, readiness=None, raid_ids=None):
    if not isinstance(plan, dict):
        raise ValueError("the sprint plan must be a JSON object")
    findings = []

    def add(severity, item, message):
        findings.append({"severity": severity, "item": item, "message": message})

    goal = (plan.get("goal") or "").strip()
    if not goal:
        add("fail", "sprint", "No sprint goal. Write one sentence that states the outcome the sprint exists for.")
    elif len(goal) > 200:
        add("warn", "sprint", f"The sprint goal has {len(goal)} characters. Reduce it to one sentence.")

    cap = plan.get("capacity") or {}
    sprint_days = field(cap, "sprint_days", 10)
    hours_per_day = field(cap, "hours_per_day", 8)
    focus = field(cap, "focus_factor", DEFAULT_FOCUS)
    members = cap.get("team_members") or []
    member_rows = []
    for member in members:
        hours, basis = member_hours(member, sprint_days, hours_per_day, focus)
        member_rows.append({"name": member.get("name", "(unnamed)"), "hours": round(hours, 1), "basis": basis})
    capacity = sum(row["hours"] for row in member_rows)
    if not members and cap.get("total_available_hours") is not None:
        capacity = field(cap, "total_available_hours")
        add("warn", "capacity", "Capacity is a team total with no per-person rows, so PTO and on-call time cannot be checked.")
    if capacity <= 0:
        add("fail", "capacity", "Capacity is zero or missing. Supply per-person hours or the inputs to calculate them.")

    commit_pct = field(cap, "commit_target_pct", DEFAULT_COMMIT_PCT)
    stretch_pct = field(cap, "stretch_pct", DEFAULT_STRETCH_PCT)
    if commit_pct > 90:
        add("warn", "capacity", f"The commit target is {commit_pct:g}% of capacity. Teams that commit above 90% usually miss.")
    if commit_pct + stretch_pct > 100:
        add("warn", "capacity", f"Commit and stretch targets total {commit_pct + stretch_pct:g}%, leaving no reserve.")

    items = plan.get("items") or []
    if not items:
        add("fail", "items", "The plan has no items.")
    dod = [entry.strip().lower() for entry in plan.get("definition_of_done") or [] if entry.strip()]
    if not dod:
        add("warn", "sprint", "No team definition of done is recorded, so item completion criteria cannot be checked.")

    commit_hours = stretch_hours = commit_points = 0.0
    for item in items:
        iid = item.get("id") or "(no id)"
        kind = (item.get("type") or "").lower()
        hours = number(item.get("estimated_hours"))
        if kind == "commit":
            commit_hours += hours
            commit_points += number(item.get("estimated_points"))
        elif kind == "stretch":
            stretch_hours += hours
        else:
            add("fail", iid, "Type must be commit or stretch.")
        if not item.get("id"):
            add("fail", iid, "Every item needs the requirement or story ID from the backlog.")
        if hours <= 0:
            add("warn", iid, "No hour estimate, so the item is excluded from the capacity totals.")
        if not item.get("assignee"):
            add("warn", iid, "No assignee.")

        if readiness is not None and item.get("id"):
            row = readiness.get(item["id"])
            if row is None:
                add("fail" if kind == "commit" else "warn", iid, "Not found in the refine-backlog report. Refine it before planning.")
            elif row.get("verdict") != "READY":
                add("fail" if kind == "commit" else "warn", iid, f"Refinement verdict is {row.get('verdict')}; only READY items can be committed.")
        elif readiness is None and kind == "commit" and not item.get("refined"):
            add("warn", iid, "No refinement report was supplied and the item is not marked refined.")

        for dep in item.get("dependencies") or []:
            if isinstance(dep, str):
                dep = {"raid_id": dep} if RAID_DEP_ID.fullmatch(dep.strip()) else {"description": dep}
            elif not isinstance(dep, dict):
                raise ValueError(f"{iid}: each dependency must be an object or a D-### ID, got {dep!r}")
            label = dep.get("raid_id") or (dep.get("description") or "")[:40] or "(unnamed dependency)"
            severity = "fail" if kind == "commit" else "warn"
            if not dep.get("owner"):
                add(severity, iid, f"Dependency {label} has no owner.")
            if not dep.get("needed_by"):
                add("warn", iid, f"Dependency {label} has no needed-by date.")
            if not dep.get("confirmed"):
                add("warn", iid, f"Dependency {label} is not confirmed by its owner.")
            if not dep.get("raid_id"):
                add("warn", iid, f"Dependency {label} has no RAID ID; record it in the RAID log through track-delivery.")
            elif raid_ids is not None and dep["raid_id"] not in raid_ids:
                add("fail", iid, f"Dependency {dep['raid_id']} is not in the RAID log.")

        if kind == "commit" and not item.get("risks"):
            add("info", iid, "No risks recorded for a committed item.")
        if dod:
            item_dod = {entry.strip().lower() for entry in item.get("dod_items") or []}
            missing = [entry for entry in dod if entry not in item_dod]
            if missing:
                add("info", iid, "Definition-of-done items not planned: " + ", ".join(missing) + ".")

    commit_target = capacity * commit_pct / 100
    stretch_target = capacity * stretch_pct / 100
    if capacity > 0:
        if commit_hours > capacity:
            add("fail", "commits", f"Committed work is {commit_hours:g} h against {capacity:g} h of capacity.")
        elif commit_hours > commit_target * 1.1:
            add("warn", "commits", f"Committed work is {commit_hours:g} h against a {commit_target:.0f} h target.")
        elif commit_hours < capacity * 0.7:
            add("info", "commits", f"Committed work uses {100 * commit_hours / capacity:.0f}% of capacity. Check whether READY items are missing from the backlog.")
        if stretch_hours > stretch_target * 1.5:
            add("info", "stretch", f"Stretch work is {stretch_hours:g} h against a {stretch_target:.0f} h target.")

    velocity = [number(v) for v in plan.get("velocity_history_points") or []]
    average_velocity = sum(velocity) / len(velocity) if velocity else None
    if average_velocity and commit_points > average_velocity * 1.05:
        add("warn", "velocity", f"Committed points ({commit_points:g}) exceed the recent average velocity ({average_velocity:.1f}).")

    counts = {level: sum(1 for f in findings if f["severity"] == level) for level in ("fail", "warn", "info")}
    return {
        "sprint": plan.get("sprint_name", ""),
        "dates": plan.get("dates", ""),
        "goal": goal,
        "capacity_hours": round(capacity, 1),
        "members": member_rows,
        "commit_target_hours": round(commit_target, 1),
        "commit_hours": commit_hours,
        "commit_utilization_pct": round(100 * commit_hours / capacity, 1) if capacity else None,
        "stretch_hours": stretch_hours,
        "commit_points": commit_points,
        "average_velocity": round(average_velocity, 1) if average_velocity else None,
        "readiness_checked": readiness is not None,
        "raid_checked": raid_ids is not None,
        "counts": counts,
        "findings": findings,
    }


def markdown(report):
    order = {"fail": 0, "warn": 1, "info": 2}
    lines = [f"# Sprint plan check: {report['sprint']}", ""]
    if report["dates"]:
        lines.append(f"Dates: {report['dates']}")
    lines.append(f"Goal: {report['goal'] or '(none)'}")
    lines.append("")
    utilization = report["commit_utilization_pct"]
    lines.append(
        f"Capacity is {report['capacity_hours']:g} h. Committed work is {report['commit_hours']:g} h"
        + (f" ({utilization:g}% of capacity)" if utilization is not None else "")
        + f" against a {report['commit_target_hours']:g} h target. Stretch work is {report['stretch_hours']:g} h."
    )
    if report["average_velocity"] is not None:
        lines.append(f"Committed points: {report['commit_points']:g}; recent average velocity: {report['average_velocity']:g}.")
    lines.append(
        "Readiness was checked against the refinement report." if report["readiness_checked"]
        else "No refinement report was supplied; readiness relies on the plan's own flags."
    )
    lines.append("RAID IDs were checked against the RAID log." if report["raid_checked"] else "No RAID log was supplied.")
    if report["members"]:
        lines += ["", "| Person | Hours | Basis |", "|---|---:|---|"]
        lines += [f"| {m['name']} | {m['hours']:g} | {m['basis']} |" for m in report["members"]]
    c = report["counts"]
    lines += ["", f"Findings: {c['fail']} fail, {c['warn']} warn, {c['info']} info.", ""]
    if report["findings"]:
        lines += ["| Severity | Item | Finding |", "|---|---|---|"]
        for f in sorted(report["findings"], key=lambda f: order[f["severity"]]):
            lines.append(f"| {f['severity']} | {f['item']} | {f['message']} |")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check a sprint plan before commitment.")
    parser.add_argument("plan", help="Sprint plan JSON")
    parser.add_argument("--readiness", help="JSON report from refine-backlog readiness_check.py")
    parser.add_argument("--raid-log", help="RAID log Markdown maintained by track-delivery")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", help="Write the report to this file")
    args = parser.parse_args(argv)
    try:
        plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
        readiness = load_readiness(args.readiness) if args.readiness else None
        raid_ids = load_raid_ids(args.raid_log) if args.raid_log else None
    except (OSError, ValueError, KeyError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    try:
        report = check(plan, readiness, raid_ids)
    except (ValueError, KeyError, TypeError, AttributeError) as error:
        print(f"error: invalid plan: {error}", file=sys.stderr)
        return 2
    text = json.dumps(report, indent=2) if args.format == "json" else markdown(report)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 1 if report["counts"]["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
