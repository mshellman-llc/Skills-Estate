#!/usr/bin/env python3
"""Build capability map outputs from one capability model JSON file.

    python3 scripts/build_capability_map.py build model.json --output-dir out/
    python3 scripts/build_capability_map.py workshop --stages "Awareness,Acquisition" --title "Workshop" --output-dir ws/
    python3 scripts/build_capability_map.py ingest ws/workshop-capture.xlsx --model ws/model.json --output model.json

`build` validates the model, computes gap, priority score, band and rank, and
writes capability-map.html, capability-assessment.xlsx, capability-readout.md
and model.computed.json. The workbook needs openpyxl; without it the other
outputs are written and the workbook is reported as not produced.

Exit codes: 0 success, 2 invalid model or refused write.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
STARTER = HERE.parent / "assets" / "capability-map.html"

STATES = {"current", "target", "current-and-target"}
STATUSES = {"existing", "partial", "new", "redundant"}
IMPACTS = {"high": 3, "medium": 2, "low": 1}
BASES = {"observed", "reported", "hypothesis"}
RAGS = {"red", "amber", "green", "open"}
DIMENSIONS = ("people", "process", "data", "technology", "organization")
EVIDENCE_TYPES = {"interview", "workshop", "transcript", "document", "system", "catalog", "analysis"}
BANDS = ("Invest now", "Plan", "Monitor", "Hold", "Retire review", "OPEN")
BAND_ORDER = {b: i for i, b in enumerate(BANDS)}
DEFAULT_THRESHOLDS = {"invest_now": 6, "plan": 3, "monitor": 1}
PRIORITIES = ("must", "should", "could", "wont")
DELIVERY_STATUSES = ("done", "in-progress", "not-started", "not-ticketed", "blocked")
IN_SCOPE = ("must", "should")
MATURITY = [
    (0, "Absent", "The organization cannot do this today."),
    (1, "Initial", "Ad hoc and person-dependent; mostly manual; results vary."),
    (2, "Repeatable", "Done the same way in some teams; partial tooling; data often incomplete."),
    (3, "Defined", "A standard process across the business with system support and known owners."),
    (4, "Managed", "Measured against targets, integrated with neighboring capabilities, data trusted."),
    (5, "Optimized", "Automated where useful and improved from its own measures."),
]
DIMENSION_QUESTIONS = {
    "people": "Is the capability adequately staffed and skilled?",
    "process": "Is the process standard, with automation that removes manual steps?",
    "data": "Is the data it depends on complete, current and trusted?",
    "technology": "Will the current tools scale as the business grows?",
    "organization": "Is one accountable owner responsible end to end?",
}
SCORING_HEADERS = ["Capability ID", "Capability", "Domain", "Level", "Parent ID", "Definition", "Status",
                   "Stage IDs", "Goal IDs", "Holders", "Systems", "People", "Process", "Data", "Technology",
                   "Organization", "Current (0-5)", "Target (0-5)", "Impact", "Score reason", "Impact reason",
                   "Votes", "Basis", "Source IDs"]
BOARD_ROWS = ["External activities", "Internal activities", "Goals", "Pains", "Opportunities",
              "Stakeholders", "Systems", "Capabilities today", "Capabilities needed"]


class ModelError(ValueError):
    def __init__(self, errors):
        self.errors = errors
        super().__init__("Model is invalid:\n" + "\n".join("- " + e for e in errors))


# --------------------------------------------------------------------------- validation

def _ids(items, label, errors):
    seen = set()
    for i, item in enumerate(items):
        if not isinstance(item, dict) or not str(item.get("id", "")).strip():
            errors.append(f"{label}[{i}] needs an id")
            continue
        if item["id"] in seen:
            errors.append(f"{label} id {item['id']} is duplicated")
        seen.add(item["id"])
    return seen


def validate(model):
    errors = []
    if not isinstance(model, dict):
        raise ModelError(["The model must be a JSON object"])
    for key in ("meta", "stages", "domains", "goals", "capabilities", "evidence"):
        if key not in model:
            errors.append(f"Missing top-level key: {key}")
    if errors:
        raise ModelError(errors)
    meta = model["meta"]
    for key in ("title", "organization", "scope", "state", "date", "basis_note"):
        if not str(meta.get(key, "")).strip():
            errors.append(f"meta.{key} is required")
    if meta.get("state") and meta["state"] not in STATES:
        errors.append(f"meta.state must be one of {sorted(STATES)}")
    if meta.get("status", "draft") not in {"draft", "validated"}:
        errors.append("meta.status must be draft or validated")
    if meta.get("date") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(meta["date"])):
        errors.append("meta.date must be an ISO date (YYYY-MM-DD)")
    release = meta.get("release")
    if release is not None and (not isinstance(release, dict) or not str(release.get("name", "")).strip()):
        errors.append("meta.release needs a name")
    bands = meta.get("priority_bands")
    if bands is not None:
        if not isinstance(bands, dict) or set(bands) != set(DEFAULT_THRESHOLDS) or not all(isinstance(v, int) for v in bands.values()):
            errors.append("meta.priority_bands needs integer invest_now, plan and monitor")
        elif not bands["invest_now"] > bands["plan"] > bands["monitor"] > 0:
            errors.append("meta.priority_bands must satisfy invest_now > plan > monitor > 0")
    stages = _ids(model["stages"], "stages", errors)
    domains = _ids(model["domains"], "domains", errors)
    goals = _ids(model["goals"], "goals", errors)
    evidence = _ids(model["evidence"], "evidence", errors)
    for item in model["stages"] + model["domains"]:
        if isinstance(item, dict) and not str(item.get("name", "")).strip():
            errors.append(f"{item.get('id')} needs a name")
    for g in model["goals"]:
        if isinstance(g, dict):
            if not str(g.get("statement", "")).strip():
                errors.append(f"goal {g.get('id')} needs a statement")
            for s in g.get("sources", []) or []:
                if s not in evidence:
                    errors.append(f"goal {g.get('id')} cites unknown evidence {s}")
    for e in model["evidence"]:
        if isinstance(e, dict):
            if not str(e.get("label", "")).strip():
                errors.append(f"evidence {e.get('id')} needs a label")
            if e.get("type") not in EVIDENCE_TYPES:
                errors.append(f"evidence {e.get('id')} type must be one of {sorted(EVIDENCE_TYPES)}")
    caps = model["capabilities"]
    cap_ids = _ids(caps, "capabilities", errors)
    by_id = {c["id"]: c for c in caps if isinstance(c, dict) and c.get("id")}
    parents = {c.get("parent") for c in caps if isinstance(c, dict) and c.get("parent")}
    names = {}
    for c in caps:
        if not isinstance(c, dict):
            continue
        cid = c.get("id", "?")
        name = str(c.get("name", "")).strip()
        if not name:
            errors.append(f"{cid} needs a name")
        else:
            key = re.sub(r"\s+", " ", name.lower())
            if key in names:
                errors.append(f"{cid} repeats the name '{name}' used by {names[key]}; keep one occurrence and list performers in holders")
            names[key] = cid
        if not str(c.get("definition", "")).strip():
            errors.append(f"{cid} needs a definition")
        if c.get("domain") not in domains:
            errors.append(f"{cid} names unknown domain {c.get('domain')}")
        if c.get("level") not in (2, 3):
            errors.append(f"{cid} level must be 2 or 3")
        if c.get("level") == 3:
            parent = by_id.get(c.get("parent"))
            if not parent:
                errors.append(f"{cid} is Level 3 and needs a known Level 2 parent")
            elif parent.get("level") != 2:
                errors.append(f"{cid} parent {parent['id']} must be Level 2")
        elif c.get("parent"):
            errors.append(f"{cid} is Level 2 and cannot have a parent")
        if c.get("status") not in STATUSES:
            errors.append(f"{cid} status must be one of {sorted(STATUSES)}")
        for s in c.get("stages", []) or []:
            if s not in stages:
                errors.append(f"{cid} names unknown stage {s}")
        for g in c.get("goals", []) or []:
            if g not in goals:
                errors.append(f"{cid} names unknown goal {g}")
        for s in c.get("sources", []) or []:
            if s not in evidence:
                errors.append(f"{cid} cites unknown evidence {s}")
        stories = c.get("delivered_by")
        if stories is not None:
            if not isinstance(stories, list):
                errors.append(f"{cid} delivered_by must be a list")
            else:
                for n, story in enumerate(stories):
                    if (not isinstance(story, dict) or not str(story.get("name", "")).strip()
                            or story.get("priority") not in PRIORITIES or story.get("status") not in DELIVERY_STATUSES):
                        errors.append(f"{cid} delivered_by[{n}] needs a name, a priority ({', '.join(PRIORITIES)}) "
                                      f"and a status ({', '.join(DELIVERY_STATUSES)})")
        for key in ("functions", "kpis"):
            values = c.get(key)
            if values is not None and (not isinstance(values, list)
                                       or not all(isinstance(v, str) and v.strip() for v in values)):
                errors.append(f"{cid} {key} must be a list of non-empty strings")
        if c.get("basis") not in BASES:
            errors.append(f"{cid} basis must be observed, reported or hypothesis")
        elif c["basis"] != "hypothesis" and not c.get("sources"):
            errors.append(f"{cid} has basis {c['basis']} but cites no sources")
        dims = c.get("dimensions") or {}
        if not isinstance(dims, dict) or set(dims) - set(DIMENSIONS):
            errors.append(f"{cid} dimensions may only use {', '.join(DIMENSIONS)}")
        else:
            for d, v in dims.items():
                if v not in RAGS:
                    errors.append(f"{cid} dimension {d} must be red, amber, green or open")
        if c.get("votes") is not None and (not isinstance(c["votes"], int) or c["votes"] < 0):
            errors.append(f"{cid} votes must be a non-negative integer")
        if cid in parents:
            for key in ("current", "target", "impact", "after_release"):
                if c.get(key) is not None:
                    errors.append(f"{cid} has Level 3 children, so its {key} belongs on the children")
            continue
        for key in ("current", "target", "after_release"):
            v = c.get(key)
            if v is not None and (not isinstance(v, int) or isinstance(v, bool) or not 0 <= v <= 5):
                errors.append(f"{cid} {key} must be an integer from 0 to 5 or null")
        if c.get("after_release") is not None and not meta.get("release"):
            errors.append(f"{cid} has after_release, so meta.release must name the release")
        if c.get("impact") is not None and c["impact"] not in IMPACTS:
            errors.append(f"{cid} impact must be high, medium, low or null")
        if c.get("status") == "new" and c.get("current") not in (0, None):
            errors.append(f"{cid} is new, so current maturity must be 0")
        override = c.get("priority_override")
        if override is not None:
            if not isinstance(override, dict) or override.get("band") not in BANDS[:-1] or not str(override.get("reason", "")).strip():
                errors.append(f"{cid} priority_override needs a band and a reason")
            elif override.get("source") and override["source"] not in evidence:
                errors.append(f"{cid} override cites unknown evidence {override['source']}")
    for item in model.get("open_items", []) or []:
        for ref in item.get("affects", []) or []:
            if ref not in cap_ids and ref not in goals:
                errors.append(f"open item {item.get('id')} affects unknown {ref}")
    if errors:
        raise ModelError(errors)


# --------------------------------------------------------------------------- computation

def rag(current):
    if current is None:
        return "open"
    return "red" if current <= 1 else "amber" if current <= 3 else "green"


def band_for(status, score, thresholds):
    if status == "redundant":
        return "Retire review"
    if score is None:
        return "OPEN"
    if score >= thresholds["invest_now"]:
        return "Invest now"
    if score >= thresholds["plan"]:
        return "Plan"
    if score >= thresholds["monitor"]:
        return "Monitor"
    return "Hold"


def compute(model):
    validate(model)
    out = copy.deepcopy(model)
    thresholds = out["meta"].get("priority_bands") or DEFAULT_THRESHOLDS
    caps = out["capabilities"]
    parents = {c.get("parent") for c in caps if c.get("parent")}
    for c in caps:
        for key in ("rag", "gap", "impact_weight", "priority_score", "band", "final_band", "rank", "scored",
                    "remaining_gap", "remaining_score", "delivery"):
            c.pop(key, None)
        c["scored"] = c["id"] not in parents
        if not c["scored"]:
            continue
        cur, tgt = c.get("current"), c.get("target")
        weight = IMPACTS.get(c.get("impact"))
        gap = tgt - cur if cur is not None and tgt is not None else None
        score = gap * weight if gap is not None and weight is not None else None
        c.update(rag=rag(cur), gap=gap, impact_weight=weight, priority_score=score,
                 band=band_for(c["status"], score, thresholds))
        c["final_band"] = (c.get("priority_override") or {}).get("band", c["band"])
        after = c.get("after_release")
        remaining = tgt - after if after is not None and tgt is not None else None
        c["remaining_gap"] = remaining
        c["remaining_score"] = remaining * weight if remaining is not None and weight is not None else None
        stories = [st for st in c.get("delivered_by") or [] if st["priority"] in IN_SCOPE]
        c["delivery"] = {"in_scope": len(stories), **{k: sum(1 for st in stories if st["status"] == k) for k in DELIVERY_STATUSES}}
    ranked = sorted((c for c in caps if c["scored"]),
                    key=lambda c: (BAND_ORDER[c["final_band"]], -(c["priority_score"] if c["priority_score"] is not None else -99),
                                   -(c.get("votes") or 0), c["id"]))
    rank, previous = 0, None
    for i, c in enumerate(ranked, 1):
        key = (c["final_band"], c["priority_score"], c.get("votes") or 0)
        if key != previous:
            rank, previous = i, key
        c["rank"] = rank
    findings = []
    linked = {g for c in caps for g in c.get("goals", []) or []}
    for g in out["goals"]:
        if g["id"] not in linked:
            findings.append({"kind": "goal-unlinked", "ref": g["id"], "text": f"Goal {g['id']} ({g['statement']}) has no linked capability."})
    for c in ranked:
        if c["final_band"] == "Invest now" and not c.get("goals"):
            findings.append({"kind": "priority-unlinked", "ref": c["id"], "text": f"{c['name']} ranks Invest now but links to no goal."})
        missing = [k for k in ("current", "target", "impact") if c.get(k) is None]
        if missing:
            findings.append({"kind": "open-value", "ref": c["id"], "text": f"{c['name']}: {', '.join(missing)} OPEN."})
        if c.get("priority_override") and c["final_band"] != c["band"]:
            findings.append({"kind": "override", "ref": c["id"],
                             "text": f"{c['name']}: computed {c['band']}, decided {c['final_band']}. " + _sentence(c['priority_override']['reason'])})
    placed = {s for c in caps for s in c.get("stages", []) or []}
    for s in out["stages"]:
        if s["id"] not in placed:
            findings.append({"kind": "stage-empty", "ref": s["id"], "text": f"Stage {s['name']} has no capability."})
    release = (out["meta"].get("release") or {}).get("name")
    if release:
        for c in ranked:
            cur, after = c.get("current"), c.get("after_release")
            if cur is not None and after is not None and after < cur:
                findings.append({"kind": "regression", "ref": c["id"],
                                 "text": f"{c['name']} drops from {cur} to {after} after {release}."})
            d = c["delivery"]
            if d["blocked"] or d["not-ticketed"]:
                parts = [f"{d['blocked']} blocked" if d["blocked"] else "", f"{d['not-ticketed']} not yet ticketed" if d["not-ticketed"] else ""]
                findings.append({"kind": "delivery-risk", "ref": c["id"],
                                 "text": f"{c['name']}: of {d['in_scope']} Must and Should stories, {' and '.join(p for p in parts if p)}."})
        for g in out["goals"]:
            short = [c for c in ranked if g["id"] in (c.get("goals") or []) and c.get("impact") == "high"
                     and (c["remaining_gap"] is None or c["remaining_gap"] > 0)]
            if short:
                names = "; ".join(f"{c['name']}, {_fmt(c.get('after_release'))} against a target of {_fmt(c.get('target'))}" for c in short)
                findings.append({"kind": "expectation-gap", "ref": g["id"],
                                 "text": f"{release[:1].upper() + release[1:]} leaves goal {g['id']} ({g['statement']}) short: {names}."})
    for o in out.get("open_items") or []:
        if not str(o.get("owner") or "").strip():
            findings.append({"kind": "decision-unowned", "ref": o.get("id"), "text": f"{o.get('id')} has no owner: {o.get('question')}"})
    out["findings"] = findings
    out["summary"] = {
        "capabilities": len(caps),
        "scored": len(ranked),
        "bands": {b: sum(1 for c in ranked if c["final_band"] == b) for b in BANDS},
        "open_values": sum(1 for f in findings if f["kind"] == "open-value"),
        "goals_unlinked": sum(1 for f in findings if f["kind"] == "goal-unlinked"),
        "release": release,
        "after_release_gaps": sum(1 for c in ranked if (c.get("remaining_gap") or 0) > 0),
        "regressions": sum(1 for f in findings if f["kind"] == "regression"),
        "expectation_gaps": sum(1 for f in findings if f["kind"] == "expectation-gap"),
        "decisions_unowned": sum(1 for f in findings if f["kind"] == "decision-unowned"),
        "thresholds": thresholds,
    }
    return out


# --------------------------------------------------------------------------- outputs

ICON_NAMES = ("warning", "info", "flag")
# Baseline sections the dashboard uses, with the kit's own palette F tokens. The
# alternate ink theme and components the page does not use are left out.
BASELINE_SECTIONS = ("Tokens", "Base", "Badges", "Radio button group (segmented)", "Data table and tree grid",
                     "Chart series use the bl-cat ramp", "App shell", "Dashboard",
                     "Shell links keep nav ink, not the global link color",
                     "Focus: these come last so component shadows cannot remove the ring")
# Baseline classes the starter uses. Rules that name any other class are left out.
BASELINE_CLASSES = {"bl", "sr-only", "i", "sk", "md", "badge", "warning", "seg", "table-wrap", "table-scroll",
                    "table-tools", "grow", "dt", "num", "wrap-text", "primary", "sub", "table-foot", "page-h",
                    "flat", "page-h-row", "page-h-t", "meta", "dash", "s4", "s8", "s12", "chart-card", "chart-h",
                    "t", "chart-b", "legend", "chart", "grid", "axis", "lbl"}


def _baseline_sections(css):
    parts, title, buf, in_comment = {}, "Tokens", [], False
    for line in css.splitlines():
        if in_comment:
            in_comment = "*/" not in line
            continue
        head = re.match(r"^/\* (.+?)(?: \*/|$)", line)
        if head and not line.startswith("/* Baseline components"):
            parts[title] = "\n".join(buf)
            title, buf = head.group(1).strip().rstrip(".").strip(), []
            in_comment = "*/" not in line
            continue
        buf.append(line)
    parts[title] = "\n".join(buf)
    return parts


def _used_rules(css):
    """Keep at-rules, :root token blocks and the rules whose selectors use only BASELINE_CLASSES."""
    out, depth, start = [], 0, 0
    for i, ch in enumerate(css):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                rule = css[start:i + 1].strip()
                start = i + 1
                selector = re.sub(r"/\*.*?\*/", "", rule.split("{", 1)[0], flags=re.S).strip()
                if selector.startswith("@") or selector == ":root" or \
                        set(re.findall(r"\.([A-Za-z][\w-]*)", selector)) <= BASELINE_CLASSES:
                    out.append(rule)
    return "\n".join(out)


def baseline_assets():
    """Return the Baseline CSS and icons the page uses, from the packaged or source client-brand kit."""
    for path in (HERE.parent / "_runtime/client-brand/baseline", HERE.parent.parent / "client-brand/baseline"):
        if (path / "baseline.css").is_file() and (path / "baseline-icons.json").is_file():
            sections = _baseline_sections((path / "baseline.css").read_text(encoding="utf-8"))
            missing = [t for t in BASELINE_SECTIONS if not any(k.startswith(t) for k in sections)]
            if missing:
                raise RuntimeError("Baseline CSS is missing sections: " + ", ".join(missing))
            kept = [body for key, body in sections.items() if any(key.startswith(t) for t in BASELINE_SECTIONS)]
            css = _used_rules("\n".join(kept))
            icons = json.loads((path / "baseline-icons.json").read_text(encoding="utf-8"))
            absent = [n for n in ICON_NAMES if n not in icons]
            if absent:
                raise RuntimeError("Baseline icons are missing: " + ", ".join(absent))
            return css, {n: icons[n] for n in ICON_NAMES}
    raise RuntimeError("The Baseline kit from client-brand is missing. Rebuild this skill with its declared dependencies.")


def render_html(computed, starter=None):
    html = (starter or STARTER).read_text(encoding="utf-8")
    css, icons = baseline_assets()
    for slot in ("/*__BASELINE_CSS__*/", "/*__ICONS__*/"):
        if html.count(slot) != 1:
            raise ValueError("Starter is missing the slot " + slot)
    html = html.replace("/*__BASELINE_CSS__*/", css.replace("</style", "<\\/style"))
    html = html.replace("const ICONS = {/*__ICONS__*/};", "const ICONS = " + json.dumps(icons).replace("<", "\\u003c") + ";")
    start = html.index("const MODEL = {")
    end = html.index("\n};", start) + 3
    body = json.dumps(computed, ensure_ascii=False, indent=1).replace("<", "\\u003c")
    html = html[:start] + "const MODEL = " + body + ";" + html[end:]
    return html.replace("<title>Capability map</title>", "<title>" + _esc(computed["meta"]["title"]) + "</title>", 1)


def _esc(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _date(iso):
    y, mo, d = (int(x) for x in iso.split("-"))
    return f"{['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][mo - 1]} {d}, {y}"


def _sentence(text):
    text = str(text).strip().rstrip(".")
    return text[:1].upper() + text[1:] + "." if text else ""


def _fmt(v):
    return "OPEN" if v is None else str(v)


def _cell(text):
    return str(text).replace("|", "\\|").replace("\n", " ")


def _ranked(computed):
    return sorted((c for c in computed["capabilities"] if c["scored"]), key=lambda c: (c["rank"], c["id"]))


def _phase2(computed):
    """Capabilities the release leaves short of target, largest remaining score first."""
    rows = [c for c in _ranked(computed) if (c.get("remaining_gap") or 0) > 0]
    return sorted(rows, key=lambda c: (-(c["remaining_score"] or 0), c["rank"], c["id"]))


def _decisions(computed):
    return [{"id": o["id"], "question": o["question"], "owner": o.get("owner") or None, "affects": o.get("affects") or []}
            for o in computed.get("open_items") or []]


def handoffs(computed):
    """Inputs for the skills that take the next steps: sequencing, backlog and the sponsor briefing."""
    release = computed["summary"]["release"]
    goals = {g["id"]: g["statement"] for g in computed["goals"]}
    left = [{"capability": c["name"], "id": c["id"], "after_release": c.get("after_release"), "target": c.get("target"),
             "remaining_score": c["remaining_score"], "goals": [goals[g] for g in c.get("goals") or []],
             "deferred_stories": [st["name"] for st in c.get("delivered_by") or [] if st["priority"] in ("could", "wont")]}
            for c in _phase2(computed)]
    untracked = [{"capability": c["name"], "story": st["name"], "priority": st["priority"]}
                 for c in _ranked(computed) for st in c.get("delivered_by") or []
                 if st["status"] == "not-ticketed" and st["priority"] in IN_SCOPE]
    brief = [f["text"] for f in computed["findings"] if f["kind"] in ("expectation-gap", "regression")]
    return {
        "release": release,
        "roadmap-artifacts": {"purpose": "Sequence the gaps the release leaves open into the next releases.", "items": left},
        "requirements-capture": {"purpose": "Write the Must and Should stories the release needs but has not ticketed.", "items": untracked},
        "deck-builder": {"purpose": "Brief the sponsor on what the release leaves undone and the decisions it needs.",
                         "findings": brief, "decisions": _decisions(computed)},
    }


def _rubric_rows():
    rows = [[f"Maturity {n}", name, text] for n, name, text in MATURITY]
    return rows + [[f"Dimension: {k}", "red / amber / green", q] for k, q in DIMENSION_QUESTIONS.items()]


def render_markdown(computed):
    m, s = computed["meta"], computed["summary"]
    ranked = _ranked(computed)
    lines = [f"# {m['title']}", ""]
    if m.get("status", "draft") == "draft":
        lines += ["The sponsor has not yet accepted these scores.", ""]
    lines += [m["scope"], "", f"{m['organization']}, {m['state'].replace('-', ' ')} state. Scored {_date(m['date'])}.", "",
              m["basis_note"], ""]
    b = s["bands"]
    lines += [f"The assessment covers {s['scored']} capabilities: {b['Invest now']} Invest now, {b['Plan']} Plan, {b['Monitor']} Monitor, "
              f"{b['Hold']} Hold, {b['Retire review']} Retire review and {b['OPEN']} OPEN. "
              f"The dashboard is `capability-map.html` and the tracker is `capability-assessment.xlsx`.", ""]
    release = s.get("release")
    if computed.get("open_items"):
        lines += ["## Decisions needed", ""]
        names = {c["id"]: c["name"] for c in computed["capabilities"]}
        for o in computed["open_items"]:
            owner = f"It is assigned to {o['owner']}." if o.get("owner") else "It has no owner yet."
            affects = [names.get(ref, f"goal {ref}") for ref in o.get("affects") or []]
            lines.append(f"- {o['question']} {owner}" + (f" It affects {', '.join(affects)}." if affects else ""))
        lines.append("")
    if release:
        gaps = sorted((f for f in computed["findings"] if f["kind"] in ("expectation-gap", "regression")),
                      key=lambda f: f["kind"] != "expectation-gap")
        lines += [f"## What {release} leaves undone", ""]
        lines += [f"- {f['text']}" for f in gaps] or ["- Every high-impact capability reaches its target."]
        lines.append("")
        risk = [f for f in computed["findings"] if f["kind"] == "delivery-risk"]
        if risk:
            lines += ["## Delivery risk", ""] + [f"- {f['text']}" for f in risk] + [""]
        left = _phase2(computed)
        if left:
            lines += [f"## After {release}", "", f"These capabilities stay short of target after {release}, largest remaining score first.", "",
                      f"| Capability | Today | After {_cell(release)} | Target | Remaining score |", "| --- | ---: | ---: | ---: | ---: |"]
            lines += [f"| {_cell(c['name'])} | {_fmt(c.get('current'))} | {_fmt(c.get('after_release'))} | {_fmt(c.get('target'))} | "
                      f"{_fmt(c['remaining_score'])} |" for c in left]
            lines.append("")
        lines += ["## Next steps by skill", "",
                  "- `roadmap-artifacts` sequences the capabilities above into the next releases.",
                  "- `requirements-capture` writes the Must and Should stories that are not yet ticketed.",
                  "- `deck-builder` briefs the sponsor on what the release leaves undone and the decisions it needs.",
                  "", "Their inputs are in `handoffs.json`.", ""]
    for band in ("Invest now", "Plan"):
        rows = [c for c in ranked if c["final_band"] == band]
        if not rows:
            continue
        lines += [f"## {band}", "", "| Rank | Capability | Current → target | Impact | Score | Why it matters | Goals |",
                  "| ---: | --- | --- | --- | ---: | --- | --- |"]
        for c in rows:
            lines.append(f"| {c['rank']} | {_cell(c['name'])} | {_fmt(c.get('current'))} → {_fmt(c.get('target'))} | "
                         f"{_fmt(c.get('impact'))} | {_fmt(c['priority_score'])} | {_cell(c.get('impact_reason', ''))} | "
                         f"{', '.join(c.get('goals') or []) or 'none'} |")
        lines.append("")
    retire = [c for c in ranked if c["final_band"] == "Retire review"]
    if retire:
        lines += ["## Retire review", ""] + [f"- {c['name']}: {c.get('definition', '')}" for c in retire] + [""]
    lines += ["## Goal coverage", ""]
    for g in computed["goals"]:
        linked = [c for c in ranked if g["id"] in (c.get("goals") or [])]
        if not linked:
            lines.append(f"- {g['id']} {g['statement']}: no linked capability.")
        else:
            names = ", ".join(f"{c['name']} ({c['final_band']})" for c in linked)
            lines.append(f"- {g['id']} {g['statement']}: {names}.")
    if not computed["goals"]:
        lines.append("- No goals are recorded, so no capability is linked to strategy.")
    lines.append("")
    other = [f for f in computed["findings"] if f["kind"] not in
             ("goal-unlinked", "expectation-gap", "regression", "delivery-risk", "decision-unowned")]
    if other:
        lines += ["## Findings", ""] + [f"- {f['text']}" for f in other] + [""]
    hyp = [c for c in ranked if c.get("basis") == "hypothesis"]
    if hyp:
        lines += ["## Validation questions", "", "These scores are hypotheses. Confirm each with the people who would own the capability.", ""]
        lines += [f"- {c['name']}: current {_fmt(c.get('current'))}, target {_fmt(c.get('target'))}, impact {_fmt(c.get('impact'))}." for c in hyp]
        lines.append("")
    if computed["evidence"]:
        lines += ["## Evidence", ""] + [f"- {e['id']}: {e['label']}" for e in computed["evidence"]] + [""]
    return "\n".join(lines).rstrip() + "\n"


def _xl():
    try:
        import openpyxl
        from openpyxl.styles import Alignment, Font, PatternFill
        from openpyxl.utils import get_column_letter
        from openpyxl.worksheet.datavalidation import DataValidation
    except ImportError:
        return None
    return openpyxl, Alignment, Font, PatternFill, get_column_letter, DataValidation


def _sheet(wb, title, headers, rows, widths=None):
    _, Alignment, Font, PatternFill, letter, _ = _xl()
    ws = wb.create_sheet(title)
    ws.append(headers)
    for row in rows:
        ws.append(row)
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="37437D")
        cell.alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "A2"
    if rows:
        ws.auto_filter.ref = ws.dimensions
    for i, h in enumerate(headers, 1):
        ws.column_dimensions[letter(i)].width = (widths or {}).get(h, max(12, min(40, len(h) + 4)))
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
    return ws


def write_xlsx(computed, path):
    xl = _xl()
    if xl is None:
        return False
    openpyxl = xl[0]
    t = computed["summary"]["thresholds"]
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    domains = {d["id"]: d["name"] for d in computed["domains"]}
    caps = {c["id"]: c for c in computed["capabilities"]}
    ranked = _ranked(computed)
    headers = ["Rank", "ID", "Capability", "Domain", "Parent", "Status", "Current", "Target", "Impact", "Gap",
               "Impact weight", "Score", "Computed band", "Decided band", "Votes", "People", "Process", "Data",
               "Technology", "Organization", "Score reason", "Impact reason", "Goals", "Stages", "Holders",
               "Systems", "Functions", "KPIs", "Basis", "Sources", "After release", "Remaining gap", "Remaining score",
               "Stories in scope", "Done", "In progress", "Not started", "Not ticketed", "Blocked"]
    _, _, _, _, letter, _ = xl
    after_col = letter(headers.index("After release") + 1)
    remaining_col = letter(headers.index("Remaining gap") + 1)
    rows = []
    for r, c in enumerate(ranked, 2):
        d = c.get("dimensions") or {}
        gap = f'=IF(OR(G{r}="",H{r}=""),"OPEN",H{r}-G{r})'
        weight = f'=IF(I{r}="high",3,IF(I{r}="medium",2,IF(I{r}="low",1,"OPEN")))'
        score = f'=IF(OR(J{r}="OPEN",K{r}="OPEN"),"OPEN",J{r}*K{r})'
        band = (f'=IF(F{r}="redundant","Retire review",IF(L{r}="OPEN","OPEN",IF(L{r}>={t["invest_now"]},"Invest now",'
                f'IF(L{r}>={t["plan"]},"Plan",IF(L{r}>={t["monitor"]},"Monitor","Hold")))))')
        decided = (c.get("priority_override") or {}).get("band")
        rows.append([c["rank"], c["id"], c["name"], domains[c["domain"]], (caps.get(c.get("parent")) or {}).get("name", ""),
                     c["status"], c.get("current"), c.get("target"), c.get("impact") or "", gap, weight, score, band,
                     decided if decided else f"=M{r}", c.get("votes"),
                     *[d.get(k, "") for k in DIMENSIONS], c.get("score_reason", ""), c.get("impact_reason", ""),
                     ", ".join(c.get("goals") or []), ", ".join(c.get("stages") or []), ", ".join(c.get("holders") or []),
                     ", ".join(c.get("systems") or []), "; ".join(c.get("functions") or []),
                     "; ".join(c.get("kpis") or []), c["basis"], ", ".join(c.get("sources") or []),
                     c.get("after_release"),
                     f'=IF(OR(H{r}="",{after_col}{r}=""),"",H{r}-{after_col}{r})',
                     f'=IF(OR({remaining_col}{r}="",K{r}="OPEN"),"",{remaining_col}{r}*K{r})',
                     c["delivery"]["in_scope"], *[c["delivery"][k] for k in DELIVERY_STATUSES]])
    _sheet(wb, "Capabilities", headers, rows, {"Capability": 32, "Score reason": 48, "Impact reason": 48, "Computed band": 16, "Decided band": 16})
    stages = computed["stages"]
    life_rows = []
    for c in ranked:
        marks = ["●" if s["id"] in (c.get("stages") or []) else "" for s in stages]
        life_rows.append([c["name"], domains[c["domain"]], *marks, "●" if not c.get("stages") else "", c["final_band"]])
    _sheet(wb, "Lifecycle", ["Capability", "Domain", *[s["name"] for s in stages], "Enabling", "Band"], life_rows, {"Capability": 32})
    trace = []
    for g in computed["goals"]:
        linked = [c for c in ranked if g["id"] in (c.get("goals") or [])]
        best = min((c["final_band"] for c in linked), key=BAND_ORDER.get) if linked else "No linked capability"
        trace.append([g["id"], g["statement"], g.get("measure", ""), g.get("framework", ""),
                      "; ".join(c["name"] for c in linked), best])
    _sheet(wb, "Strategy trace", ["Goal", "Statement", "Measure", "Framework", "Linked capabilities", "Best band"], trace,
           {"Statement": 44, "Measure": 36, "Linked capabilities": 48, "Best band": 20})
    stories = [[c["name"], st["name"], st["priority"], st["status"], st.get("ref", "")]
               for c in ranked for st in c.get("delivered_by") or []]
    if stories:
        _sheet(wb, "Delivery", ["Capability", "Story", "Priority", "Status", "Reference"], stories, {"Capability": 32, "Story": 44})
    rubric = _rubric_rows() + [["Impact weight", k, str(v)] for k, v in IMPACTS.items()]
    rubric += [["Band", "Invest now", f"Score {t['invest_now']} or more"], ["Band", "Plan", f"Score {t['plan']} to {t['invest_now'] - 1}"],
               ["Band", "Monitor", f"Score {t['monitor']} to {t['plan'] - 1}"], ["Band", "Hold", f"Score below {t['monitor']}"],
               ["Band", "Retire review", "Status redundant"], ["Band", "OPEN", "Current, target or impact missing"],
               ["Display", "red / amber / green", "Current 0 to 1 red, 2 to 3 amber, 4 to 5 green"]]
    _sheet(wb, "Rubric", ["Item", "Value", "Meaning"], rubric, {"Item": 24, "Value": 22, "Meaning": 70})
    _sheet(wb, "Evidence", ["ID", "Label", "Type", "Locator"],
           [[e["id"], e["label"], e["type"], e.get("locator", "")] for e in computed["evidence"]], {"Label": 50, "Locator": 50})
    opens = [[o["id"], o["question"], o.get("owner") or "OPEN", ", ".join(o.get("affects") or [])] for o in computed.get("open_items") or []]
    opens += [[f["ref"], f["text"], "OPEN", f["ref"]] for f in computed["findings"] if f["kind"] == "open-value"]
    _sheet(wb, "Open items", ["ID", "Question", "Owner", "Affects"], opens, {"Question": 70})
    wb.properties.title = computed["meta"]["title"]
    wb.properties.creator = ""
    wb.calculation.fullCalcOnLoad = True
    wb.save(path)
    return True


def build(model, output_dir):
    computed = compute(model)
    output_dir.mkdir(parents=True, exist_ok=True)
    names = ["capability-map.html", "capability-assessment.xlsx", "capability-readout.md", "model.computed.json", "handoffs.json"]
    existing = [n for n in names if (output_dir / n).exists()]
    if existing:
        raise FileExistsError("Output exists; choose a new output directory: " + ", ".join(existing))
    (output_dir / names[0]).write_text(render_html(computed), encoding="utf-8")
    workbook = write_xlsx(computed, output_dir / names[1])
    (output_dir / names[2]).write_text(render_markdown(computed), encoding="utf-8")
    (output_dir / names[3]).write_text(json.dumps(computed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / names[4]).write_text(json.dumps(handoffs(computed), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"outputs": [str(output_dir / n) for n in names if (output_dir / n).exists()],
            "workbook": "written" if workbook else "not produced: openpyxl is unavailable",
            "summary": computed["summary"], "findings": len(computed["findings"])}


# --------------------------------------------------------------------------- workshop and ingest

def workshop(stages, title, output_dir, date):
    xl = _xl()
    if xl is None:
        raise RuntimeError("The workshop workbook needs openpyxl")
    openpyxl, _, _, _, letter, DataValidation = xl
    names = [s.strip() for s in stages.split(",") if s.strip()]
    if not names:
        raise ValueError("Give at least one stage name")
    output_dir.mkdir(parents=True, exist_ok=True)
    capture, seed = output_dir / "workshop-capture.xlsx", output_dir / "model.json"
    for p in (capture, seed):
        if p.exists():
            raise FileExistsError(f"Output exists; choose a new output directory: {p.name}")
    stage_list = [{"id": f"S{i}", "name": n} for i, n in enumerate(names, 1)]
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    _sheet(wb, "Lifecycle board", ["Row", *[f"{s['id']} {s['name']}" for s in stage_list]],
           [[r, *[""] * len(stage_list)] for r in BOARD_ROWS], {"Row": 24, **{f"{s['id']} {s['name']}": 30 for s in stage_list}})
    ws = _sheet(wb, "Scoring", SCORING_HEADERS, [], {"Capability": 30, "Definition": 40, "Score reason": 40, "Impact reason": 40})
    lists = {"Status": "existing,partial,new,redundant", "Impact": "high,medium,low", "Basis": "observed,reported,hypothesis",
             **{d.capitalize(): "red,amber,green,open" for d in DIMENSIONS}}
    for i, h in enumerate(SCORING_HEADERS, 1):
        col = letter(i)
        if h in lists:
            dv = DataValidation(type="list", formula1=f'"{lists[h]}"', allow_blank=True)
        elif h in ("Current (0-5)", "Target (0-5)"):
            dv = DataValidation(type="whole", operator="between", formula1="0", formula2="5", allow_blank=True)
        elif h == "Level":
            dv = DataValidation(type="list", formula1='"2,3"', allow_blank=True)
        else:
            continue
        ws.add_data_validation(dv)
        dv.add(f"{col}2:{col}500")
    _sheet(wb, "Rubric", ["Item", "Value", "Meaning"], _rubric_rows(), {"Item": 24, "Value": 22, "Meaning": 70})
    _sheet(wb, "Stages", ["Stage ID", "Stage"], [[s["id"], s["name"]] for s in stage_list])
    wb.properties.title = title
    wb.save(capture)
    model = {"meta": {"title": title, "organization": "OPEN", "scope": "OPEN: business, state and decision.",
                      "state": "current", "date": date, "basis_note": "OPEN: where the scores came from.", "status": "draft"},
             "stages": stage_list, "domains": [], "goals": [], "capabilities": [], "evidence": [], "open_items": []}
    seed.write_text(json.dumps(model, indent=2) + "\n", encoding="utf-8")
    return {"outputs": [str(capture), str(seed)]}


def _split(value):
    return [v.strip() for v in str(value or "").split(",") if v.strip()]


def _int(value, label, errors):
    if value in (None, ""):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        errors.append(f"{label} must be a whole number")
        return None
    if number != int(number):
        errors.append(f"{label} must be a whole number")
        return None
    return int(number)


def ingest(workbook, model):
    xl = _xl()
    if xl is None:
        raise RuntimeError("Reading the workshop workbook needs openpyxl")
    openpyxl = xl[0]
    wb = openpyxl.load_workbook(workbook, data_only=True)
    if "Scoring" not in wb.sheetnames:
        raise ModelError(["The workbook has no Scoring sheet"])
    ws = wb["Scoring"]
    header = [str(c.value or "").strip() for c in ws[1]]
    missing = [h for h in SCORING_HEADERS if h not in header]
    if missing:
        raise ModelError(["Scoring sheet is missing columns: " + ", ".join(missing)])
    col = {h: header.index(h) for h in SCORING_HEADERS}
    out = copy.deepcopy(model)
    domains = {d["name"].lower(): d["id"] for d in out["domains"]}
    errors, existing = [], {c["id"]: c for c in out["capabilities"]}
    for n, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 2):
        get = lambda h: row[col[h]] if col[h] < len(row) else None
        if not any(v not in (None, "") for v in row):
            continue
        cid = str(get("Capability ID") or "").strip()
        if not cid:
            errors.append(f"Scoring row {n} needs a Capability ID")
            continue
        domain = str(get("Domain") or "").strip()
        if domain and domain.lower() not in domains:
            new_id = "D" + str(len(domains) + 1)
            out["domains"].append({"id": new_id, "name": domain})
            domains[domain.lower()] = new_id
        dims = {k: str(get(k.capitalize())).strip().lower() for k in DIMENSIONS if get(k.capitalize()) not in (None, "")}
        cap = {"id": cid, "name": str(get("Capability") or "").strip(), "domain": domains.get(domain.lower()),
               "level": _int(get("Level"), f"row {n} Level", errors) or 2,
               "definition": str(get("Definition") or "").strip(), "status": str(get("Status") or "").strip().lower(),
               "stages": _split(get("Stage IDs")), "goals": _split(get("Goal IDs")), "holders": _split(get("Holders")),
               "systems": _split(get("Systems")), "dimensions": dims,
               "current": _int(get("Current (0-5)"), f"row {n} Current", errors),
               "target": _int(get("Target (0-5)"), f"row {n} Target", errors),
               "impact": (str(get("Impact")).strip().lower() if get("Impact") not in (None, "") else None),
               "score_reason": str(get("Score reason") or "").strip(), "impact_reason": str(get("Impact reason") or "").strip(),
               "votes": _int(get("Votes"), f"row {n} Votes", errors),
               "basis": str(get("Basis") or "").strip().lower(), "sources": _split(get("Source IDs"))}
        if get("Parent ID"):
            cap["parent"] = str(get("Parent ID")).strip()
        cap = {k: v for k, v in cap.items() if v not in (None, "", []) or k in ("current", "target", "impact")}
        if cid in existing:
            existing[cid].update(cap)
        else:
            out["capabilities"].append(cap)
            existing[cid] = cap
    if errors:
        raise ModelError(errors)
    validate(out)
    return out


# --------------------------------------------------------------------------- CLI

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build", help="Validate a model and write every output")
    b.add_argument("model", type=Path)
    b.add_argument("--output-dir", type=Path, required=True)
    v = sub.add_parser("validate", help="Validate a model and print its computed summary")
    v.add_argument("model", type=Path)
    w = sub.add_parser("workshop", help="Write a workshop capture workbook and seeded model")
    w.add_argument("--stages", required=True, help="Comma-separated stage names in lifecycle order")
    w.add_argument("--title", required=True)
    w.add_argument("--date", default=None, help="ISO date for the seeded model; defaults to today")
    w.add_argument("--output-dir", type=Path, required=True)
    i = sub.add_parser("ingest", help="Merge a filled Scoring sheet into a model")
    i.add_argument("workbook", type=Path)
    i.add_argument("--model", type=Path, required=True)
    i.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "build":
            result = build(json.loads(args.model.read_text(encoding="utf-8")), args.output_dir)
        elif args.command == "validate":
            computed = compute(json.loads(args.model.read_text(encoding="utf-8")))
            result = {"valid": True, "summary": computed["summary"], "findings": [f["text"] for f in computed["findings"]]}
        elif args.command == "workshop":
            import datetime as dt
            result = workshop(args.stages, args.title, args.output_dir, args.date or dt.date.today().isoformat())
        else:
            if args.output.exists():
                raise FileExistsError("Output exists; choose a new output path")
            merged = ingest(args.workbook, json.loads(args.model.read_text(encoding="utf-8")))
            args.output.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            result = {"outputs": [str(args.output)], "capabilities": len(merged["capabilities"])}
    except (ModelError, FileExistsError, RuntimeError, ValueError, OSError) as error:
        print(str(error), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
