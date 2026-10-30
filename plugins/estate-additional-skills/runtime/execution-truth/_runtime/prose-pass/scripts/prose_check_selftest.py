#!/usr/bin/env python3
"""Selftest for prose-pass. No third-party dependencies, no network.

All fixture narratives and figures are synthetic and describe no real project.
Runs the checker over an inline bad fixture and an inline clean fixture with the
Estate house config, and asserts the expected findings and exit behavior.
Prints observed versus expected and exits nonzero on any mismatch.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import prose_check  # noqa: E402

HOUSE = json.loads((HERE.parent / "house.json").read_text(encoding="utf-8"))
CFG = {k: v for k, v in HOUSE.items() if not k.startswith("_")}
CFG = {**prose_check.DEFAULT_CONFIG, **CFG}

BAD = """\
We leverage best-in-class synergy to deliver a seamless, robust, holistic platform.

It's worth noting that per your request, we built the two panels you asked to see.

The sample import is ready, and the test operator can run it. Two fields need labels, and the reviewer must confirm them. The nightly job stays idle, and the deadline moves again.

We designed a new pipeline, which enables teams to move faster. See Section §4.

The parser serves as the entry point and stands as the core of the release. Let us dig into the logs. It appears to hold and seems to pass. That check is load-bearing, and the honest answer is that we shipped it regardless.

The rollout was fast, clean, and simple.
"""

GOOD = """\
The synthetic parser accepted 12 rows from the sample file.

The test operator checked each header. The missing timestamp caused an error. That result matches the fixture specification.

We added a label to the preview so the reviewer can identify the input. The export retains its original columns.
"""

WARNING_ONLY = """\
The parser serves as the entry point. The router stands as the final gate.
"""

# Categories the bad fixture must trip. Each exercises a different layer.
EXPECT_BAD = {
    "house-banned-term",    # layer 1: vocabulary
    "house-hedge-opener",   # layer 1: hedge openers
    "house-banned-char",    # layer 1: section sign
    "justification-tail",   # layer 1: benefit tail
    "C1-balanced-clause",   # layer 3: the , and epidemic (relocation trap)
    "C7-triad",             # layer 3: three adjectives said for rhythm
    "C10-deference",        # layer 2: deference signalling
    "C18-copula-avoidance", # serves as / stands as
    "C19-gravity-marker",   # load-bearing / the honest answer
    "C20-dig-dive",         # dig into / dive into
    "C21-hedge-verb",       # appears to / seems to
    "C23-trailing-hedge-adverb",  # ...regardless.
}

failures = []


def rules(text):
    findings, _ = prose_check.check(text, CFG)
    return {f.rule for f in findings}, findings


bad_rules, bad_findings = rules(BAD)
missing = EXPECT_BAD - bad_rules
if missing:
    failures.append(f"bad fixture did not trip: {sorted(missing)}")
if not any(f.severity == "FAIL" for f in bad_findings):
    failures.append("bad fixture produced no FAIL")

good_rules, good_findings = rules(GOOD)
good_fails = [f.rule for f in good_findings if f.severity == "FAIL"]
if good_fails:
    failures.append(f"clean fixture produced FAILs: {good_fails}")
if good_findings:
    failures.append(f"clean fixture produced findings: {sorted(good_rules)}")

warning_rules, warning_findings = rules(WARNING_ONLY)
if not warning_findings or any(f.severity == "FAIL" for f in warning_findings):
    failures.append("warning fixture did not produce WARN-only findings")

with tempfile.TemporaryDirectory() as tmp:
    warning_file = Path(tmp) / "warning.md"
    warning_file.write_text(WARNING_ONLY, encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(HERE / "prose_check.py"), "--config",
         str(HERE.parent / "house.json"), str(warning_file)],
        capture_output=True, text=True)
    if proc.returncode != 1:
        failures.append(
            f"warning-only CLI run returned {proc.returncode}, expected 1")

one_dash_rules, _ = rules("The finding is narrow — one owner can fix it.")
if "em-dash" in one_dash_rules:
    failures.append("one em dash exceeded the house allowance")
two_dash_rules, _ = rules(
    "The finding is narrow — one owner can fix it. The next step is clear — deploy Friday.")
if "em-dash" not in two_dash_rules:
    failures.append("two em dashes did not exceed the house allowance")

list_rules, _ = rules("- Alpha owner\n- Beta owner\n- Friday deadline\n")
if "C6-fragment-stacking" in list_rules:
    failures.append("legitimate Markdown list triggered fragment stacking")

imperative_rules, _ = rules("Use the source file. Run the checker. Fix each finding.")
if "C6-fragment-stacking" in imperative_rules:
    failures.append("imperative instructions triggered fragment stacking")

wrapped_rules, _ = rules("The checker reads the first\nline as part of one sentence.")
if "C6-fragment-stacking" in wrapped_rules:
    failures.append("a wrapped Markdown sentence triggered fragment stacking")

protected_rules, _ = rules(prose_check.strip_quoted(
    "Use [`leverage`](terms.md) only as a quoted example."))
if "house-banned-term" in protected_rules or "C6-fragment-stacking" in protected_rules:
    failures.append("protected Markdown link created a lexical or fragment finding")

print("bad fixture rules :", sorted(bad_rules))
print("expected (subset) :", sorted(EXPECT_BAD))
print("good fixture FAILs:", good_fails, "(expected none)")
print("warning fixture  :", sorted(warning_rules), "(must exit 1)")

if failures:
    print("\nSELFTEST FAILED")
    for f in failures:
        print("  -", f)
    sys.exit(1)

print("\nSELFTEST PASSED")
