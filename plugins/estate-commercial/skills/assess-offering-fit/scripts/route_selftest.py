#!/usr/bin/env python3
"""Selftest for assess-offering-fit. Stdlib only, no network.

Locks in the crash fix: builds a synthetic qualifier directory (one scorable
qualifier plus one malformed qualifier missing "playbook_code") and a signals
file, then invokes route.py as a subprocess exactly as a caller would:

    python3 route.py --qualifiers DIR --signals FILE

Asserts the run exits 0 (main() completes end to end without crashing), that the
output carries a ROUTE line, and that the malformed qualifier is SKIPPED rather
than crashing the run. Prints observed vs expected; exits nonzero on mismatch.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROUTE = HERE / "route.py"

GOOD_QUALIFIER = {
    "playbook_code": "TEST-01",
    "playbook_name": "T",
    "tags": {"domain": ["crm migration"]},
    "gates": [{"id": "g1", "pass_on": "yes", "question": "CRM?"}],
    "tiers": [{"name": "A", "signals": ["large enterprise"]}],
    "disqualifiers": [],
}

# Missing "playbook_code" on purpose. score_one() must raise QualifierError and
# main() must record it as skipped, not abort the whole run.
BAD_QUALIFIER = {
    "playbook_name": "Malformed",
    "tags": {"domain": ["crm migration"]},
    "gates": [{"id": "g1", "pass_on": "yes", "question": "CRM?"}],
    "tiers": [{"name": "A", "signals": ["large enterprise"]}],
    "disqualifiers": [],
}

SIGNALS = {
    "client": "Acme",
    "signals": [{"text": "crm migration for sales", "source": "notes", "evidence": "confirmed"}],
    "gate_answers": {"g1": {"answer": "yes", "source": "notes", "evidence": "confirmed"}},
}

fail = []

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    qdir = tmp / "qualifiers"
    qdir.mkdir()
    (qdir / "good.json").write_text(json.dumps(GOOD_QUALIFIER))
    (qdir / "bad.json").write_text(json.dumps(BAD_QUALIFIER))
    sig = tmp / "signals.json"
    sig.write_text(json.dumps(SIGNALS))

    proc = subprocess.run(
        [sys.executable, str(ROUTE), "--qualifiers", str(qdir), "--signals", str(sig)],
        capture_output=True, text=True,
    )
    out = proc.stdout + proc.stderr

    checks = [
        ("exit code", proc.returncode, 0),
        ("ROUTE line present", "ROUTE" in out, True),
        ("malformed qualifier SKIPPED", "SKIPPED" in out and "bad.json" in out, True),
        ("scorable qualifier survived", "1 of 2 qualifiers scored" in out, True),
    ]
    for label, got, want in checks:
        print(f"  {label:34} got={got!r:24} want={want!r}")
        if got != want:
            fail.append(f"{label}: got {got!r}, want {want!r}")

    if fail:
        print("\n--- captured output ---")
        print(out)

if fail:
    print("\nSELFTEST FAILED")
    for f in fail:
        print("  -", f)
    sys.exit(1)
print("\nSELFTEST PASSED")
