#!/usr/bin/env python3
"""Selftest for reconcile.py, the Mode B evidence gate.

Each case asserts that a specific failure mode is caught. The failure modes are
drawn from real defects found while building call briefs, which is why they are
the ones worth testing.

Usage: python3 reconcile_selftest.py
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RECONCILE = os.path.join(HERE, "reconcile.py")

MEETING = {"title": "T", "when": "W", "owner": "O"}


def run(payload, args=()):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(payload, f)
        p = f.name
    try:
        r = subprocess.run([sys.executable, RECONCILE, p, "--json", *args],
                           capture_output=True, text=True)
        return json.loads(r.stdout)
    finally:
        os.unlink(p)


CASES = []


def case(name):
    def deco(fn):
        CASES.append((name, fn))
        return fn
    return deco


@case("conflicting values for one quantity are caught")
def _():
    # The real defect: one SOW total in Salesforce and another in the record.
    out = run({"meeting": MEETING, "figures": [
        {"key": "sow002", "label": "SOW002 total", "value": "$197,775",
         "source": "Salesforce closed-won", "meaning": "NTE"},
        {"key": "sow002", "label": "SOW002 total", "value": "$225,800",
         "source": "Engagement record", "meaning": "NTE"},
    ], "landmines": [{"title": "x", "body": "y"}]})
    codes = [e["code"] for e in out["errors"]]
    assert "FIGURE_CONFLICT" in codes, codes
    assert not out["pass"]


@case("matching values across sources do not false-positive")
def _():
    out = run({"meeting": MEETING, "figures": [
        {"key": "credit_memos", "label": "Credit memos", "value": "1,000+",
         "source": "Billing records", "meaning": "per year"},
        {"key": "credit_memos", "label": "Credit memos", "value": "1,000+",
         "source": "Findings Report 10.3", "meaning": "per year"},
    ]})
    assert out["pass"], out["errors"]


@case("a figure with no source fails")
def _():
    out = run({"meeting": MEETING, "figures": [
        {"label": "Recoverable", "value": "$200K-$300K", "meaning": "near term"}]})
    assert "FIGURE_NO_SOURCE" in [e["code"] for e in out["errors"]]


@case("spoken lines without a mined voice fail")
def _():
    out = run({"meeting": MEETING, "voice_inventory": [], "talk_track": [
        {"title": "Open", "say": ["Here is what we found."]}]})
    assert "VOICE_NOT_MINED" in [e["code"] for e in out["errors"]]


@case("spoken lines with a mined voice pass")
def _():
    out = run({"meeting": MEETING,
               "voice_inventory": [{"phrase": "carpet in a bathroom",
                                    "kind": "analogy", "source": "Jun 24 transcript"}],
               "talk_track": [{"title": "Open", "say": ["It is carpet in a bathroom."],
                               "voice_basis": "carpet in a bathroom"}]})
    assert out["pass"], out["errors"]


@case("a Q&A answer with no source fails")
def _():
    out = run({"meeting": MEETING, "qa": [
        {"q": "What is deployed?", "answer": ["Three tickets."]}]})
    assert "QA_NO_SOURCE" in [e["code"] for e in out["errors"]]


@case("a 'never' item placed into content fails")
def _():
    # The real risk: a CFO's assessment of his own staff reaching an artifact.
    out = run({"meeting": MEETING, "claims": [
        {"text": "He questioned two people's suitability", "source": "Jun 24 transcript",
         "sensitivity": "never", "placement": "qa_answer"}]})
    assert "SENSITIVITY_LEAK" in [e["code"] for e in out["errors"]]


@case("an untagged claim fails")
def _():
    out = run({"meeting": MEETING, "claims": [
        {"text": "Work paused pending a change order", "source": "Slack Jul 10"}]})
    assert "CLAIM_NO_SENSITIVITY" in [e["code"] for e in out["errors"]]


@case("a conflict that is not flagged for the reader fails")
def _():
    out = run({"meeting": MEETING, "figures": [
        {"key": "k", "label": "L", "value": "10", "source": "A"},
        {"key": "k", "label": "L", "value": "20", "source": "B"},
    ]})
    codes = [e["code"] for e in out["errors"]]
    assert "CONFLICT_NOT_FLAGGED" in codes, codes


@case("a conflict that is flagged and landmined passes as acknowledged")
def _():
    # Two SOW totals, both shown, disagreement named. The presenter decides.
    out = run({"meeting": MEETING, "figures": [
        {"key": "sow", "label": "SOW", "value": "$197,775", "source": "Salesforce",
         "meaning": "NTE", "flag": True},
        {"key": "sow", "label": "SOW", "value": "$225,800", "source": "Record",
         "meaning": "NTE", "flag": True},
    ], "landmines": [{"title": "Two conflicting SOW totals",
                      "body": "Verify before quoting", "do": "Confirm in writing"}]})
    assert out["pass"], out["errors"]
    assert "FIGURE_CONFLICT_ACKNOWLEDGED" in [w["code"] for w in out["warnings"]]


@case("a stale source warns without failing")
def _():
    out = run({"meeting": MEETING, "figures": [
        {"key": "k", "label": "Old", "value": "5", "source": "Doc",
         "source_date": "2019-01-01", "meaning": "m"}]})
    assert "FIGURE_STALE" in [w["code"] for w in out["warnings"]]
    assert out["pass"]


def main():
    failed = 0
    for name, fn in CASES:
        try:
            fn()
            print("  pass  {}".format(name))
        except AssertionError as e:
            failed += 1
            print("  FAIL  {}\n        {}".format(name, e))
    print("\n  {}/{} passed\n".format(len(CASES) - failed, len(CASES)))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
