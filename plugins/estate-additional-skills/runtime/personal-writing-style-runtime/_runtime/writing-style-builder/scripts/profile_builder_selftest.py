#!/usr/bin/env python3
"""Selftest for profile_builder.py. Synthetic fixtures only; never a real profile."""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import profile_builder as pb  # noqa: E402

FIXTURES = Path(__file__).resolve().parent.parent / "references" / "synthetic-fixtures"


def test_filter_authored_drops_ineligible_provenance():
    evidence = json.loads((FIXTURES / "evidence-sample.json").read_text())
    kept = pb.filter_authored(evidence)
    kept_ids = {e["id"] for e in kept}
    assert kept_ids == {"e1", "e2", "e6"}, f"unexpected eligible set: {kept_ids}"
    assert "e3" not in kept_ids  # quoted
    assert "e4" not in kept_ids  # third-party
    assert "e5" not in kept_ids  # ai-generated


def test_validate_profile_accepts_wellformed_fixture():
    profile = json.loads((FIXTURES / "profile-sample.json").read_text())
    errors = pb.validate_profile(profile)
    assert errors == [], f"expected no errors, got: {errors}"


def test_validate_profile_rejects_unauthorized():
    profile = json.loads((FIXTURES / "profile-sample.json").read_text())
    profile["authorization"]["granted"] = False
    errors = pb.validate_profile(profile)
    assert any("authorization.granted" in e for e in errors)


def test_validate_profile_rejects_ineligible_tendency_provenance():
    profile = json.loads((FIXTURES / "profile-sample.json").read_text())
    profile["base_profile"]["written"]["core_tendencies"].append(
        {"pattern": "leaked from a quoted email", "confidence": "low", "provenance": "quoted", "sources": 1}
    )
    errors = pb.validate_profile(profile)
    assert any("ineligible provenance" in e for e in errors)


def test_validate_profile_rejects_missing_source_count():
    profile = json.loads((FIXTURES / "profile-sample.json").read_text())
    profile["base_profile"]["written"]["core_tendencies"].append(
        {"pattern": "no source count given", "confidence": "low", "provenance": "authored", "sources": 0}
    )
    errors = pb.validate_profile(profile)
    assert any("names no source count" in e for e in errors)


def test_detect_conflicts_flags_disagreeing_readings():
    patterns = [
        {"dimension": "directness", "reading": "always leads with the ask"},
        {"dimension": "directness", "reading": "often opens with context first"},
        {"dimension": "length", "reading": "short by default"},
    ]
    conflicts = pb.detect_conflicts(patterns)
    dims = {c["dimension"] for c in conflicts}
    assert dims == {"directness"}, f"expected only 'directness' to conflict, got {dims}"


def _run():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failures = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as e:
            failures += 1
            print(f"FAIL {t.__name__}: {e}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(_run())
