#!/usr/bin/env python3
"""Behavior tests for the JSONL ledger event log: check rules and projection.

The projection is judged by the existing validator in evidence_core.py, so the
trial authoring form cannot drift from the schema the finalization gate reads.
"""

import contextlib
import io
import json
import pathlib
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

import ledger_events as le  # noqa: E402
from evidence_core import EvidenceCore  # noqa: E402

passed = 0
failed = 0


def check(label, condition):
    global passed, failed
    if condition:
        passed += 1
        print("  PASS {}".format(label))
    else:
        failed += 1
        print("  FAIL {}".format(label))


def run(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        code = le.main(list(argv))
    return code, out.getvalue()


def codes_of(text):
    findings = le.Findings()
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as handle:
        handle.write(text)
        path = pathlib.Path(handle.name)
    events = le.read_events(path, findings)
    le.validate(events, findings)
    path.unlink()
    return {row["code"] for row in findings.rows}


FIXTURE = ROOT / "fixtures" / "pursuit-ledger.jsonl"
fixture_text = FIXTURE.read_text(encoding="utf-8")
lines = fixture_text.splitlines()

# --- the fixture is clean and projects into a ledger the gate accepts ---------
code, out = run("check", str(FIXTURE))
check("fixture passes check with the low-authority warning", code == 0 and "0 errors" in out and "TAG-AUTHORITY" in out)

with tempfile.TemporaryDirectory() as directory:
    output = pathlib.Path(directory) / "evidence-ledger.json"
    code, out = run("project", str(FIXTURE), "--output", str(output), "--as-of", "2026-09-05T12:00:00Z")
    check("project exits 0", code == 0 and output.exists())
    document = json.loads(output.read_text())
    core = EvidenceCore(ROOT / "reference" / "artifact-registry.json")
    findings = core.validate_ledger(document)
    check("projection has no validator errors: {}".format([f.code for f in findings]),
          not [f for f in findings if f.level == "error"])
    claims = {c["claimId"]: c for c in document["claims"]}
    check("STATED projects to Confirmed", claims["CLM-018"]["status"] == "Confirmed")
    check("OBSERVED from an authority-40 source projects to Inferred, not Confirmed",
          claims["CLM-015"]["status"] == "Inferred")
    check("INFERRED projects to Inferred, then Contested by the open conflict",
          claims["CLM-016"]["status"] == "Contested" and claims["CLM-016"]["owner"] == "deal owner")
    check("ASSUMED projects to Unknown with owner and closure",
          claims["CLM-017"]["status"] == "Unknown" and claims["CLM-017"]["closureCondition"])
    check("supersede projects the old claim as Superseded",
          claims["CLM-014"]["status"] == "Superseded" and "CLM-018" in claims["CLM-014"]["confidenceRationale"])
    check("claim rows carry only schema fields",
          set(claims["CLM-014"]) == set(le.CLAIM_FIELDS))
    check("registers carry decisions and assumptions",
          document["registers"]["decisions"][0]["itemId"] == "DEC-002"
          and document["registers"]["assumptions"][0]["itemId"] == "ASM-007")
    check("asOf honours --as-of", document["asOf"] == "2026-09-05T12:00:00Z")
    check("context is carried from the first event",
          document["context"]["scopeType"] == "opportunity" and document["context"]["contextId"] == "opp-2026-northstar")
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        print("  SKIP jsonschema validation (module not installed)")
    else:
        schema = json.loads((ROOT / "schemas" / "evidence-ledger.schema.json").read_text())
        errors = list(Draft202012Validator(schema).iter_errors(document))
        check("projection validates against evidence-ledger.schema.json: {}".format([e.message for e in errors][:2]),
              not errors)

# --- check rules ------------------------------------------------------------
context = lines[0]
source = lines[2]
good_claim = lines[5]

check("a DECIDED claim is refused",
      "DECIDED-IS-NOT-A-CLAIM" in codes_of("\n".join([context, source, good_claim.replace('"tag":"STATED"', '"tag":"DECIDED"')])))
check("a tag and an explicit contradicting status is refused",
      "TAG-STATUS" in codes_of("\n".join([context, source, good_claim.replace('"tag":"STATED"', '"tag":"STATED","status":"Inferred"')])))
check("an explicit status matching the authority-aware projection is accepted",
      "TAG-STATUS" not in codes_of("\n".join([context, lines[3], good_claim.replace('"sourceIds":["SRC-002"]', '"sourceIds":["SRC-003"]').replace('"tag":"STATED"', '"tag":"STATED","status":"Inferred"')])))
check("an unknown tag is refused",
      "TAG" in codes_of("\n".join([context, source, good_claim.replace('"tag":"STATED"', '"tag":"CONFIRMED"')])))
check("a STATED claim with no source is refused",
      "CLAIM-UNSOURCED" in codes_of("\n".join([context, source, good_claim.replace('"sourceIds":["SRC-002"]', '"sourceIds":[]')])))
check("a claim naming an unknown source is refused",
      "CLAIM-SOURCE" in codes_of("\n".join([context, good_claim])))
check("a load-bearing ASSUMED claim needs owner and closure",
      "ASSUMED-LOAD-BEARING" in codes_of("\n".join([context, source,
          '{"event":"claim","claimId":"CLM-099","statement":"x","tag":"ASSUMED","sourceIds":[],"asOf":"2026-09-04T00:00:00Z","loadBearing":true,"domains":["scope"]}'])))
check("a missing context line is refused",
      "CONTEXT-FIRST" in codes_of("\n".join([source, good_claim])))
check("supersede naming an unknown claim is refused",
      "SUPERSEDE-UNKNOWN" in codes_of("\n".join([context, source, good_claim,
          '{"event":"supersede","claimId":"CLM-014","by":"CLM-500","asOf":"2026-09-05T00:00:00Z"}'])))
check("a two-digit source id is refused",
      "SOURCE-ID" in codes_of("\n".join([context, source.replace("SRC-002", "SRC-02")])))
check("a decision row needs who and when",
      "DECISION-FIELD" in codes_of("\n".join([context, source, good_claim,
          '{"event":"register","register":"decisions","itemId":"DEC-009","claimIds":["CLM-014"]}'])))
check("an assumption row needs if-false and communicate",
      {"ASSUMPTION-IF-FALSE", "ASSUMPTION-COMMUNICATE"} <= codes_of("\n".join([context, source, good_claim,
          '{"event":"register","register":"assumptions","itemId":"ASM-009","claimIds":["CLM-014"]}'])))
check("an open material conflict needs owner and closure",
      "CONFLICT-OPEN" in codes_of("\n".join([context, source, good_claim, lines[6],
          '{"event":"conflict","conflictId":"CNF-002","claimIds":["CLM-014","CLM-015"],"materiality":"material","status":"open","description":"x"}'])))
check("an unknown event kind is refused",
      "EVENT-KIND" in codes_of("\n".join([context, '{"event":"note","text":"hi"}'])))
check("a non-JSON line is refused",
      "JSON" in codes_of("\n".join([context, "not json"])))

with tempfile.TemporaryDirectory() as directory:
    bad = pathlib.Path(directory) / "bad.jsonl"
    bad.write_text("\n".join([context, source, good_claim.replace('"tag":"STATED"', '"tag":"DECIDED"')]) + "\n")
    code, _ = run("check", str(bad))
    check("check exits 1 on errors", code == 1)
    code, _ = run("project", str(bad), "--output", str(pathlib.Path(directory) / "out.json"))
    check("project refuses a ledger with errors", code == 1 and not (pathlib.Path(directory) / "out.json").exists())
    code, _ = run("check", str(pathlib.Path(directory) / "missing.jsonl"))
    check("a missing ledger exits 2", code == 2)

print("{} passed, {} failed".format(passed, failed))
if failed:
    sys.exit(1)
