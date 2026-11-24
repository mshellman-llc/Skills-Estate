#!/usr/bin/env python3
"""Selftest for check_handoff.py.

Runs the gate against the shipped fixtures and a set of generated mutations,
asserting exit codes and expected findings. Exits 0 only if every case behaves.

Usage: python3 s2d_selftest.py
"""

import copy
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CHECKER = os.path.join(HERE, "check_handoff.py")
FIXTURES = os.path.join(HERE, "fixtures")

failures = []
CASES = []


def run(path):
    proc = subprocess.run(
        [sys.executable, CHECKER, path], capture_output=True, text=True
    )
    return proc.returncode, proc.stdout + proc.stderr


def case(name, path, want_code, want_substrings=()):
    CASES.append(name)
    code, out = run(path)
    ok = code == want_code and all(s in out for s in want_substrings)
    if ok:
        print(f"ok   {name} (exit {code})")
    else:
        failures.append(name)
        print(f"FAIL {name}: wanted exit {want_code}, got {code}")
        for s in want_substrings:
            if s not in out:
                print(f"     missing expected finding: {s!r}")
        print("     --- output ---")
        for line in out.strip().splitlines():
            print(f"     {line}")


def mutated(base, mutate, name):
    m = copy.deepcopy(base)
    mutate(m)
    fd, path = tempfile.mkstemp(prefix=f"s2d_{name}_", suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(m, fh)
    return path


def main():
    with open(os.path.join(FIXTURES, "pass_brief.json"), encoding="utf-8") as fh:
        brief = json.load(fh)

    # Issues 176, 177 and 180, on the invented fixture client.
    case("legacy stamp key is refused",
         mutated(brief, lambda m: m["source_snapshot"].update({"write-statement-of-work": m["source_snapshot"].pop("sow")}), "legacy"),
         1, ["source_snapshot.sow and source_snapshot.quote are both required"])
    case("an unsigned working draft is refused",
         mutated(brief, lambda m: m["source_snapshot"].update(sow="unsigned working draft, not for signature"), "draft"),
         1, ["describes a draft or unsigned agreement"])
    case("an executed SOW with no signing record is refused",
         mutated(brief, lambda m: m["source_snapshot"].pop("sow_executed"), "nosign"),
         1, ["source_snapshot.sow_executed needs signed_on"])
    case("one party signing alone is refused",
         mutated(brief, lambda m: m["source_snapshot"]["sow_executed"].update(signers=[{"name": "Fixture Client Signer", "party": "Fixture Client"}]), "oneparty"),
         1, ["signers that name a person for each of at least two parties"])
    case("a signer with no party is refused",
         mutated(brief, lambda m: m["source_snapshot"]["sow_executed"].update(signers=["Fixture Client Signer", "Fixture Provider Signer"]), "noparty"),
         1, ["signers that name a person for each of at least two parties"])
    case("a deck cannot source a contract figure",
         mutated(brief, lambda m: m["figures"][0].update(source="proposal deck slide 4, as quoted in the pitch"), "deck"),
         1, ["money rule"])
    case("a deck beside the SOW id still fails",
         mutated(brief, lambda m: m["figures"][0].update(source="SOW-FIX-001 and the proposal deck"), "deckid"),
         1, ["money rule"])
    case("the quote id alone sources a figure",
         mutated(brief, lambda m: m["figures"][0].update(source="Q-000999 line 3"), "quoteid"), 0, ["RESULT: PASS"])

    # Issue 187: the readiness gap memo has a defined shape.
    memo = os.path.join(FIXTURES, "gap_memo_example.md")
    memo_checker = os.path.join(HERE, "check_gap_memo.py")

    def memo_case(name, path, want_code, want=""):
        proc = subprocess.run([sys.executable, memo_checker, path], capture_output=True, text=True)
        out = proc.stdout + proc.stderr
        if proc.returncode == want_code and want in out:
            print(f"ok   {name} (exit {proc.returncode})")
        else:
            failures.append(name)
            print(f"FAIL {name}: wanted exit {want_code} with {want!r}, got {proc.returncode}: {out.strip()}")
        CASES.append(name)

    memo_case("gap memo example passes", memo, 0, "RESULT: PASS")
    with open(memo, encoding="utf-8") as fh:
        memo_text = fh.read()
    fd, no_next = tempfile.mkstemp(prefix="s2d_memo_", suffix=".md")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(memo_text.split("## Next gate")[0])
    memo_case("gap memo without the next gate fails", no_next, 1, "missing section: Next gate")
    os.unlink(no_next)

    # Shipped fixtures.
    case("pass_brief", os.path.join(FIXTURES, "pass_brief.json"), 0, ["RESULT: PASS"])
    case("pass_package", os.path.join(FIXTURES, "pass_package.json"), 0, ["RESULT: PASS", "moment=package"])
    case(
        "fail_blank_and_unmarked",
        os.path.join(FIXTURES, "fail_blank_and_unmarked.json"),
        1,
        [
            "section 02: blank",
            "section 03: no sources",
            "gap 0 missing owner",
            "section 11: brief requires at least one discovery session",
            "criterion 0 missing criterion or binary_test",
            "section 12: brief requires the readiness checklist",
            "in_or_out must be 'in' or 'out'",
            "missing said_where",
            "off-contract promise requires an owner",
            "money rule",
        ],
    )

    # Generated mutations from the passing brief.
    tmp = []

    def gen(name, mutate, want_code, want_substrings):
        path = mutated(brief, mutate, name)
        tmp.append(path)
        case(name, path, want_code, want_substrings)

    gen(
        "missing_section_05",
        lambda m: m["sections"].pop("05"),
        1,
        ["section 05: missing (sections are never dropped)"],
    )
    gen(
        "extra_section_13",
        lambda m: m["sections"].__setitem__("13", {"content": ["x"], "sources": [{"name": "s", "date": "d"}]}),
        1,
        ["section 13: not in the 12-section catalog"],
    )
    gen(
        "em_dash_in_text",
        lambda m: m["sections"]["01"]["content"].append("A claim \u2014 with an em dash"),
        1,
        ["em dash found"],
    )
    gen(
        "empty_scope",
        lambda m: m.__setitem__("scope", []),
        1,
        ["scope: empty"],
    )
    gen(
        "missing_quote_stamp",
        lambda m: m["source_snapshot"].pop("quote"),
        1,
        ["source_snapshot.sow and source_snapshot.quote"],
    )
    gen(
        "bad_moment",
        lambda m: m.__setitem__("moment", "someday"),
        1,
        ["moment must be one of"],
    )
    gen(
        "session_missing_output",
        lambda m: m["sections"]["11"]["sessions"][0].pop("output"),
        1,
        ["session 0 missing output"],
    )
    gen(
        "in_sow_true_without_clause",
        lambda m: m["promises"][1].pop("sow_clause"),
        1,
        ["in_sow true requires sow_clause"],
    )
    gen(
        "readiness_bad_status",
        lambda m: m["sections"]["12"]["readiness"][0].__setitem__("status", "probably"),
        1,
        ["status must be ready, blocked, or unknown"],
    )

    # Package moment: gaps-only 11 and 12 are allowed.
    def to_package(m):
        m["moment"] = "package"
        m["sections"]["11"] = {"gaps": [{"question": "shape week one", "owner": "Solution Lead", "resolve_by": "2026-08-14", "gate_blocked": "delivery acceptance"}]}
        m["sections"]["12"] = {"gaps": [{"question": "draft readiness and done", "owner": "Program Lead", "resolve_by": "2026-08-14", "gate_blocked": "delivery acceptance"}]}

    gen("package_seeded_11_12", to_package, 0, ["RESULT: PASS", "moment=package"])

    # Parse and usage errors exit 2.
    fd, bad = tempfile.mkstemp(prefix="s2d_notjson_", suffix=".json")
    with os.fdopen(fd, "w") as fh:
        fh.write("{not json")
    tmp.append(bad)
    case("not_json", bad, 2, ["not valid JSON"])

    proc = subprocess.run([sys.executable, CHECKER], capture_output=True, text=True)
    if proc.returncode == 2:
        print("ok   no_args (exit 2)")
    else:
        failures.append("no_args")
        print(f"FAIL no_args: wanted exit 2, got {proc.returncode}")

    for p in tmp:
        os.unlink(p)

    total = len(CASES)
    if failures:
        print(f"SELFTEST: FAIL ({len(failures)}/{total} cases failed: {', '.join(failures)})")
        return 1
    print(f"SELFTEST: PASS ({total}/{total} cases)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
