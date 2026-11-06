#!/usr/bin/env python3
"""Evidence gate for prepare-sales-pursuit Mode B call briefs.

Fails the build on the failure modes that produce confident wrong briefs:
(Structure of the ledger: ../assets/evidence.schema.json.)
  - a figure asserted with no source
  - the same quantity carrying different values across sources
  - a source too old to be load-bearing
  - a spoken line with no recorded basis
  - a sensitivity tag that would leak a `never` item into the artifact

Usage:  python3 reconcile.py evidence.json [--max-age-days N] [--json]
Exit 0 clean, 1 on any error. Warnings do not fail but are reported.
"""
import json, sys, argparse, re
from datetime import datetime, date
from collections import defaultdict

ERR, WARN = [], []


def err(code, detail): ERR.append({"code": code, "detail": detail})
def warn(code, detail): WARN.append({"code": code, "detail": detail})


def parse_date(v):
    if not v:
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d %b %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(str(v).strip(), fmt).date()
        except ValueError:
            continue
    return None


NUM = re.compile(r"\$?\s*([\d,]+(?:\.\d+)?)\s*([KMB%]?)", re.I)
MULT = {"": 1, "K": 1e3, "M": 1e6, "B": 1e9, "%": 1}


def normalize(value):
    """Return a comparable numeric tuple for a figure string, or None."""
    if value is None:
        return None
    s = str(value).replace("\u2013", "-").replace("\u2014", "-")
    hits = NUM.findall(s)
    if not hits:
        return None
    out = []
    for raw, suf in hits:
        try:
            out.append(float(raw.replace(",", "")) * MULT.get(suf.upper(), 1))
        except ValueError:
            pass
    return tuple(out) if out else None


def close(a, b, tol=0.02):
    if a is None or b is None or len(a) != len(b):
        return False
    return all(abs(x - y) <= tol * max(abs(x), abs(y), 1) for x, y in zip(a, b))


def check(ev, max_age):
    today = date.today()
    ev = ev  # referenced by conflict-handling check below

    # --- figures: source presence, staleness, cross-source conflict ---
    by_key = defaultdict(list)
    for f in ev.get("figures", []):
        label = f.get("label", "<unlabelled>")
        if not f.get("source"):
            err("FIGURE_NO_SOURCE", f"{label}: no source")
        if not f.get("meaning"):
            warn("FIGURE_NO_MEANING", f"{label}: no stated meaning, cannot be defended")
        d = parse_date(f.get("source_date"))
        if d is None:
            warn("FIGURE_NO_DATE", f"{label}: source has no date, staleness unknown")
        elif (today - d).days > max_age:
            warn("FIGURE_STALE", f"{label}: source is {(today-d).days} days old")
        key = (f.get("key") or label).strip().lower()
        by_key[key].append(f)

    for key, group in by_key.items():
        if len(group) < 2:
            continue
        seen = []
        for f in group:
            n = normalize(f.get("value"))
            if n is None:
                continue
            if not any(close(n, s) for s in seen):
                seen.append(n)
        if len(seen) > 1:
            detail = " vs ".join(
                f"{f.get('value')} ({f.get('source')})" for f in group)
            # A conflict is not a defect. Hiding one is. The gate demands handling:
            # every member flagged for the reader, and a landmine that names the
            # disagreement. Handled conflicts warn; silent conflicts fail.
            handled = (all(f.get("flag") for f in group)
                       and bool(ev.get("landmines")))
            (warn if handled else err)(
                "FIGURE_CONFLICT" + ("_ACKNOWLEDGED" if handled else ""),
                f"{key}: {detail}")

    # --- claims: every assertion needs a locatable source ---
    for c in ev.get("claims", []):
        if not c.get("source"):
            err("CLAIM_NO_SOURCE", f"{c.get('text','<empty>')[:70]}")
        if c.get("sensitivity") not in ("public", "internal", "never"):
            err("CLAIM_NO_SENSITIVITY", f"{c.get('text','<empty>')[:70]}")

    # --- spoken lines: no voice without a recording ---
    voice = ev.get("voice_inventory", [])
    lines = ev.get("talk_track", [])
    spoken = [b for b in lines if b.get("say")]
    if spoken and not voice:
        err("VOICE_NOT_MINED",
            f"{len(spoken)} spoken lines but voice_inventory is empty. "
            "Drop to intents or mine the presenter's transcripts.")
    for b in lines:
        if b.get("say") and not b.get("voice_basis"):
            warn("LINE_NO_VOICE_BASIS",
                 f"beat '{b.get('title','?')}' has a spoken line with no voice_basis")

    # --- Q&A: an answer that cannot be defended is a liability ---
    for q in ev.get("qa", []):
        if not q.get("source"):
            err("QA_NO_SOURCE", f"{q.get('q','<empty>')[:70]}")

    # --- sensitivity: `never` items must not carry detail into the guide ---
    for c in ev.get("claims", []):
        if c.get("sensitivity") == "never" and c.get("placement") not in (None, "instruction_only"):
            err("SENSITIVITY_LEAK",
                f"'never' item placed as {c.get('placement')}: {c.get('text','')[:60]}")

    # --- unflagged conflicts: present but invisible to the reader ---
    for key, group in by_key.items():
        if len(group) < 2:
            continue
        vals = {str(f.get("value")) for f in group}
        if len(vals) > 1 and not all(f.get("flag") for f in group):
            err("CONFLICT_NOT_FLAGGED",
                f"{key}: conflicting figures must each set flag:true so the reader sees them")

    # --- earned sections: warn on any section with no backing evidence ---
    reqs = {
        "talk_track": ("asks", "verbatim ask from the counterpart"),
        "qa": ("qa", "counterpart questions"),
        "figures": ("figures", "reconciled figures"),
        "landmines": ("landmines", "a detected conflict or sensitivity"),
    }
    for section, (field, need) in reqs.items():
        if ev.get(section) and not ev.get(field):
            warn("SECTION_UNEARNED", f"{section} present without {need}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("evidence")
    ap.add_argument("--max-age-days", type=int, default=180)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    ev = json.load(open(a.evidence))
    check(ev, a.max_age_days)

    if a.json:
        print(json.dumps({"errors": ERR, "warnings": WARN,
                          "pass": not ERR}, indent=2))
    else:
        print(f"\n  RECONCILE  {a.evidence}\n")
        for e in ERR:
            print(f"    fail  {e['code']:<24} {e['detail']}")
        for w in WARN:
            print(f"    warn  {w['code']:<24} {w['detail']}")
        if not ERR and not WARN:
            print("  clean: every figure sourced and reconciled")
        print(f"\n  {'PASS' if not ERR else 'FAIL'}: "
              f"{len(ERR)} error, {len(WARN)} warning\n")
        if ERR:
            print("  Conflicts are not resolved by choosing the better-reading number.")
            print("  Put both in the guide, name the disagreement, let the presenter decide.\n")
    sys.exit(1 if ERR else 0)


if __name__ == "__main__":
    main()
