#!/usr/bin/env python3
"""Playbook fit router.

    python3 route.py --qualifiers DIR --signals signals.json [--weights weights.json]
                     [--out run.json] [--format text|json] [--top N]

Scores a prospect's extracted signals against every playbook's qualifier.json and returns a
ranked match with the evidence behind it.

Two rules make the output trustworthy, and both are enforced here rather than left to
judgment:

1. **Nothing scores without a citation.** A signal with no source contributes zero.
2. **Evidence class is carried, never upgraded.** A match built on inferred signals is
   reported as inferred. The router never promotes an inference to a client-stated fact.
   This now binds disqualifiers too: an inference cannot issue a terminal rejection.

It does not price, does not pick a tier band, and does not write artifacts.

Three behaviours here are calibration hypotheses, not settled law, and each is tunable:
the component weights, the tag denominator cap, and the negation cue list. None of them
should be treated as authoritative until they are checked against real closed deals.
"""

import argparse
import datetime
import glob
import json
import os
import sys

DEFAULT_WEIGHTS = {
    "tag_match": 0.4,
    "gate_pass": 0.4,
    "tier_signal": 0.2,
    "evidence_multiplier": {
        "client_stated": 1.0,
        "seller_asserted": 0.6,
        "inferred": 0.3,
        "not_evidenced": 0.0,
    },
    "fit_thresholds": {"strong": 0.65, "possible": 0.4},
    # A verbose qualifier must not rank below a sparse one on identical evidence. The tag
    # denominator is capped so breadth of matching saturates instead of diluting.
    "tag_denominator_cap": 8,
}

EVIDENCE_ORDER = ["client_stated", "seller_asserted", "inferred", "not_evidenced"]

# Classes strong enough to issue a terminal rejection. An inferred disqualifier is
# surfaced for a human to check, and it does not kill the match on its own.
DISQUALIFYING_CLASSES = {"client_stated", "seller_asserted"}

NEGATION_BEFORE = ("no ", "not ", "never", "without", "ruled out", "won't", "will not",
                   "wont", "don't", "dont", "cannot", "can't", "excluded", "instead of",
                   "rather than", "no longer", "declined", "deferred")
NEGATION_AFTER = ("out of scope", "not in scope", "is excluded", "ruled out",
                  "not required", "no longer", "was declined")
NEG_WINDOW = 40

REQUIRED_QUALIFIER_KEYS = ("playbook_code", "gates", "tiers")


class QualifierError(Exception):
    """A qualifier file that cannot be scored. Reported, never fatal to the run."""


def load_json(path):
    with open(path) as fh:
        return json.load(fh)


def norm(s):
    return " ".join(str(s).lower().split())


def deep_merge(base, override):
    """Merge nested dicts. A partial override must not delete sibling keys."""
    out = dict(base)
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def validate_weights(w):
    """A weights file that drops a class would silently zero it. Fail loudly instead."""
    problems = []
    for key in ("tag_match", "gate_pass", "tier_signal", "tag_denominator_cap"):
        if key not in w:
            problems.append(f"missing '{key}'")
    for cls in EVIDENCE_ORDER:
        if cls not in w.get("evidence_multiplier", {}):
            problems.append(f"evidence_multiplier missing '{cls}'")
    for band in ("strong", "possible"):
        if band not in w.get("fit_thresholds", {}):
            problems.append(f"fit_thresholds missing '{band}'")
    if int(w.get("tag_denominator_cap", 0)) < 1:
        problems.append("tag_denominator_cap must be at least 1")
    return problems


def is_negated(text_n, tag_n):
    """Flag a tag occurrence that the source ruled out.

    A bounded cue check, not sentence parsing. It is here to stop a ruled-out capability
    from scoring as present. It will miss some negations, so a flagged hit is reported for
    a human rather than silently dropped from the record.
    """
    idx = text_n.find(tag_n)
    if idx < 0:
        return False
    before = text_n[max(0, idx - NEG_WINDOW):idx]
    after = text_n[idx + len(tag_n): idx + len(tag_n) + NEG_WINDOW]
    if any(cue in before for cue in NEGATION_BEFORE):
        return True
    return any(cue in after for cue in NEGATION_AFTER)


def signal_weight(sig, weights):
    """A signal with no source contributes nothing, whatever it claims."""
    if not sig.get("source"):
        return 0.0, None, "no source"
    cls = sig.get("evidence", "not_evidenced")
    return weights["evidence_multiplier"].get(cls, 0.0), cls, None


def score_tags(pb, signals, weights, negation_guard=True):
    tags = pb.get("tags", {}) or {}
    wanted = []
    for group, values in (tags.items() if isinstance(tags, dict) else []):
        for v in values or []:
            wanted.append((group, norm(v)))
    if not wanted:
        return 0.0, [], [], 0

    hits, negated, total = [], [], 0.0
    for group, tag in wanted:
        if not tag:
            continue
        for sig in signals:
            text_n = norm(sig.get("text", ""))
            if tag not in text_n:
                continue
            w, cls, skip = signal_weight(sig, weights)
            if w == 0.0:
                continue
            if negation_guard and is_negated(text_n, tag):
                negated.append({"tag": tag, "group": group, "evidence": cls,
                                "source": sig.get("source"), "quote": sig.get("text"),
                                "note": "source appears to rule this out; excluded from score"})
                break
            total += w
            hits.append({"tag": tag, "group": group, "evidence": cls,
                         "source": sig.get("source"), "quote": sig.get("text")})
            break

    denom = min(len(wanted), int(weights["tag_denominator_cap"]))
    score = min(total / denom, 1.0) if denom else 0.0
    return score, hits, negated, len(wanted)


def score_gates(pb, answers, weights):
    gates = pb.get("gates", []) or []
    if not gates:
        return 0.0, [], []
    passed, unanswered, detail = 0.0, [], []
    for g in gates:
        if not isinstance(g, dict) or "id" not in g or "pass_on" not in g:
            raise QualifierError("a gate entry is missing 'id' or 'pass_on'")
        question = g.get("question", g["id"])
        a = answers.get(g["id"])
        if a is None:
            unanswered.append(question)
            continue
        ans = a.get("answer")
        w, cls, skip = signal_weight(a, weights)
        ok = (ans == g["pass_on"])
        if ok:
            passed += w
        detail.append({"gate": g["id"], "question": question, "answer": ans,
                       "pass": ok, "evidence": cls, "uncited": bool(skip),
                       "source": a.get("source")})
    return (passed / len(gates)), detail, unanswered


def score_tiers(pb, signals, weights):
    best, best_score, evidence = None, 0.0, []
    for tier in pb.get("tiers", []) or []:
        sigs = (tier or {}).get("signals", []) or []
        if not sigs:
            continue
        total, hits = 0.0, []
        for s in sigs:
            for sig in signals:
                if norm(s) in norm(sig.get("text", "")):
                    w, cls, skip = signal_weight(sig, weights)
                    if w == 0.0:
                        continue
                    total += w
                    hits.append({"signal": s, "evidence": cls, "source": sig.get("source")})
                    break
        sc = total / len(sigs)
        if sc > best_score:
            best, best_score, evidence = tier.get("name"), sc, hits
    return best, best_score, evidence


def check_disqualifiers(pb, signals, negation_guard=True):
    """Split by evidence class. Only a witnessed condition can reject a playbook."""
    terminal, flagged = [], []
    for d in pb.get("disqualifiers", []) or []:
        cond = norm((d or {}).get("condition", ""))
        if not cond:
            continue
        for sig in signals:
            text_n = norm(sig.get("text", ""))
            if cond not in text_n or not sig.get("source"):
                continue
            if negation_guard and is_negated(text_n, cond):
                break
            row = {"condition": d["condition"], "route_to": d.get("route_to"),
                   "source": sig.get("source"), "evidence": sig.get("evidence"),
                   "quote": sig.get("text")}
            if sig.get("evidence") in DISQUALIFYING_CLASSES:
                terminal.append(row)
            else:
                row["note"] = ("disqualifier matched on an unverified signal; "
                               "confirm with the client before ruling this playbook out")
                flagged.append(row)
            break
    return terminal, flagged


def evidence_profile(*groups):
    """Counts per class across everything that actually contributed."""
    prof = {c: 0 for c in EVIDENCE_ORDER}
    for g in groups:
        for item in g or []:
            cls = item.get("evidence")
            if cls in prof:
                prof[cls] += 1
    return prof


def weakest_class(profile):
    for cls in reversed(EVIDENCE_ORDER):
        if profile.get(cls):
            return cls
    return "not_evidenced"


def dominant_class(profile, weights):
    """The class carrying the most weight, so one stray inference does not read as the whole match."""
    best, best_w = None, -1.0
    for cls in EVIDENCE_ORDER:
        w = profile.get(cls, 0) * weights["evidence_multiplier"].get(cls, 0.0)
        if w > best_w and profile.get(cls):
            best, best_w = cls, w
    return best or "not_evidenced"


def score_one(pb, signals, answers, weights, negation_guard):
    for key in REQUIRED_QUALIFIER_KEYS:
        if key not in pb:
            raise QualifierError(f"missing required key '{key}'")

    tag_s, tag_hits, negated, tag_total = score_tags(pb, signals, weights, negation_guard)
    gate_s, gate_detail, unanswered = score_gates(pb, answers, weights)
    tier, tier_s, tier_hits = score_tiers(pb, signals, weights)
    dq_terminal, dq_flagged = check_disqualifiers(pb, signals, negation_guard)

    total = (weights["tag_match"] * tag_s
             + weights["gate_pass"] * gate_s
             + weights["tier_signal"] * tier_s)

    th = weights["fit_thresholds"]
    if dq_terminal:
        fit = "disqualified"
    elif total >= th["strong"]:
        fit = "strong"
    elif total >= th["possible"]:
        fit = "possible"
    else:
        fit = "weak"

    prof = evidence_profile(tag_hits, gate_detail, tier_hits, dq_terminal, dq_flagged)
    return {
        "playbook": pb.get("playbook_code"),
        "name": pb.get("playbook_name"),
        "score": round(total, 3),
        "fit": fit,
        "evidence_class": weakest_class(prof),
        "dominant_evidence": dominant_class(prof, weights),
        "evidence_profile": prof,
        "suggested_tier": tier,
        "tier_confidence": round(tier_s, 3),
        "components": {"tags": round(tag_s, 3), "gates": round(gate_s, 3),
                       "tier": round(tier_s, 3)},
        "tag_denominator": {"declared": tag_total,
                            "used": min(tag_total, int(weights["tag_denominator_cap"]))},
        "evidence": {"tags": tag_hits, "gates": gate_detail, "tier": tier_hits},
        "negated_tag_hits": negated,
        "unanswered_gates": unanswered,
        "disqualifiers_hit": dq_terminal,
        "disqualifiers_flagged": dq_flagged,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--qualifiers", required=True, help="directory of qualifier.json files")
    ap.add_argument("--signals", required=True, help="extracted signals JSON")
    ap.add_argument("--weights")
    ap.add_argument("--out", help="write the full run record here; stdout stays a summary")
    ap.add_argument("--top", type=int, default=3)
    ap.add_argument("--format", choices=["json", "text"], default="text")
    ap.add_argument("--no-negation-guard", action="store_true",
                    help="score a tag even where the source appears to rule it out")
    args = ap.parse_args()

    weights = DEFAULT_WEIGHTS
    if args.weights:
        weights = deep_merge(DEFAULT_WEIGHTS, load_json(args.weights))
    problems = validate_weights(weights)
    if problems:
        print(json.dumps({"error": "invalid weights", "problems": problems}, indent=2))
        return 2

    src = load_json(args.signals)
    signals = src.get("signals", [])
    answers = src.get("gate_answers", {})

    files = sorted(glob.glob(os.path.join(args.qualifiers, "*.json")))
    if not files:
        print(json.dumps({"error": f"no qualifier files in {args.qualifiers}"}, indent=2))
        return 2

    results, skipped = [], []
    negation_guard = not args.no_negation_guard
    for f in files:
        pb = load_json(f)
        try:
            results.append(score_one(pb, signals, answers, weights, negation_guard))
        except QualifierError as e:
            skipped.append({"file": os.path.basename(f), "reason": str(e)})

    results.sort(key=lambda r: (r["fit"] == "disqualified", -r["score"]))
    top = results[: args.top]
    viable = [r for r in top if r["fit"] in ("strong", "possible")]

    coverage = {"files_found": len(files), "scored": len(results),
                "skipped": skipped, "complete": not skipped}

    notes = []
    if not viable:
        notes.append("No playbook scored above the possible threshold. Route to paid "
                     "scoping rather than forcing the nearest match.")
    else:
        notes.append("Scores are evidence-weighted. An inferred match is not a confirmed fit.")
    if skipped:
        notes.append(f"{len(skipped)} qualifier file(s) could not be scored and were left "
                     f"out of the ranking. This result is partial.")
    if any(r["negated_tag_hits"] for r in top):
        notes.append("Some tags appeared in the source only where it ruled them out. They "
                     "are listed under negated_tag_hits and did not score.")
    if any(r["disqualifiers_flagged"] for r in top):
        notes.append("A disqualifier matched on an unverified signal. It did not reject the "
                     "playbook. Confirm it with the client.")

    out = {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "inputs": {"qualifiers_dir": os.path.abspath(args.qualifiers),
                   "signals_file": os.path.abspath(args.signals),
                   "weights_file": os.path.abspath(args.weights) if args.weights else None,
                   "client": src.get("client")},
        "weights_used": weights,
        "coverage": coverage,
        "top_matches": top,
        "route": ("paid scoping" if not viable else top[0]["playbook"]),
        "notes": notes,
    }

    if args.out:
        with open(args.out, "w") as fh:
            json.dump(out, fh, indent=2)

    if args.format == "json" and not args.out:
        print(json.dumps(out, indent=2))
    else:
        cov = f"{coverage['scored']} of {coverage['files_found']} qualifiers scored"
        if skipped:
            cov += f", {len(skipped)} skipped"
        print(f"\n  ROUTE  {out['route']}     [{cov}]\n")
        for r in top:
            print(f"    {r['playbook']:<10} {r['fit']:<13} score {r['score']:<6} "
                  f"evidence {r['evidence_class']} (mostly {r['dominant_evidence']})")
            if r["suggested_tier"]:
                print(f"      tier hypothesis: {r['suggested_tier']} ({r['tier_confidence']})")
            for h in r["evidence"]["tags"][:3]:
                print(f"      tag '{h['tag']}' <- {h['source']} [{h['evidence']}]")
            for n in r["negated_tag_hits"]:
                print(f"      NEGATED, not scored: '{n['tag']}' <- {n['source']}")
            for d in r["disqualifiers_hit"]:
                print(f"      DISQUALIFIED: {d['condition']} -> {d['route_to']} [{d['evidence']}]")
            for d in r["disqualifiers_flagged"]:
                print(f"      unverified disqualifier: {d['condition']} [{d['evidence']}], confirm before ruling out")
            for q in r["unanswered_gates"]:
                print(f"      gate unanswered: {q}")
            print()
        for s in skipped:
            print(f"      SKIPPED {s['file']}: {s['reason']}")
        if skipped:
            print()
        for n in out["notes"]:
            print(f"  {n}")
        print()
        if args.out:
            print(f"  full run record written to {args.out}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
