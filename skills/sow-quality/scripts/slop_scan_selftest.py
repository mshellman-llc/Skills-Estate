#!/usr/bin/env python3
"""Selftest for sow-quality's slop_scan.py. Stdlib only, no network.

slop_scan.py reads a .docx through the external `extract-text` binary (not
stdlib, not guaranteed on PATH). So this test stubs only that extraction step
(slop_scan.get_text) and exercises the REAL scanning and reporting logic on two
synthetic texts:

  BAD  - repetition-as-thoroughness (a MECHANIC_PHRASE repeated), a
         justification tail, and an em dash. Must produce findings and, under the
         --verify exit contract, return nonzero.
  GOOD - terse, one mechanic phrase used once, no em dash, no section sign, no
         justification tail. Must be clean and return 0 under --verify.

The exit contract matched here is slop_scan.report()'s: in --verify mode it
returns 0 iff section_sign==0 and em_dash==0 and no repeated mechanics, else 1.

Prints observed vs expected; exits nonzero on mismatch.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import slop_scan  # noqa: E402

# A MECHANIC_PHRASE from slop_scan; repeating it is repetition-as-thoroughness.
MECH = slop_scan.MECHANIC_PHRASES[1]  # "bills as the lower actual effort"

BAD_TEXT = (
    "The engagement bills as the lower actual effort. Aleysian tracks scope, so "
    "that the client sees every hour. The engagement bills as the lower actual "
    "effort in a second place too — which the client already knows.\n"
)

GOOD_TEXT = (
    "Aleysian delivers the migration in three sprints. The engagement bills as "
    "the lower actual effort. Weekly demos confirm progress.\n"
)


def prose_of(full):
    # Mirror slop_scan.get_text's prose filtering (drop table rows / blank lines).
    return "\n".join(
        ln for ln in full.splitlines()
        if not ln.lstrip().startswith("|") and ln.strip()
    )


def make_stub(full):
    return lambda path: (full, prose_of(full))


fail = []

# --- BAD text ---
slop_scan.get_text = make_stub(BAD_TEXT)
bad = slop_scan.scan("BAD.docx")
bad_verify = slop_scan.report("BAD.docx", bad, verify=True)

bad_checks = [
    ("BAD repeated_mechanics found", bool(bad["repeated_mechanics"]), True),
    ("BAD mechanic count == 2", bad["repeated_mechanics"].get(MECH), 2),
    ("BAD justification candidates", len(bad["justification_candidates"]) > 0, True),
    ("BAD em_dash counted", bad["em_dash_count"] >= 1, True),
    ("BAD --verify exit nonzero", bad_verify, 1),
]

# --- GOOD text ---
slop_scan.get_text = make_stub(GOOD_TEXT)
good = slop_scan.scan("GOOD.docx")
good_verify = slop_scan.report("GOOD.docx", good, verify=True)

good_checks = [
    ("GOOD no repeated mechanics", bool(good["repeated_mechanics"]), False),
    ("GOOD no em dash", good["em_dash_count"], 0),
    ("GOOD no section sign", good["section_sign_count"], 0),
    ("GOOD --verify exit clean", good_verify, 0),
]

for label, got, want in bad_checks + good_checks:
    print(f"  {label:32} got={got!r:8} want={want!r}")
    if got != want:
        fail.append(f"{label}: got {got!r}, want {want!r}")

if fail:
    print("\nSELFTEST FAILED")
    for f in fail:
        print("  -", f)
    sys.exit(1)
print("\nSELFTEST PASSED")
