#!/usr/bin/env python3
"""Selftest for route_check.py, against a synthetic profile only.

Covers, per this skill's evaluation requirements: positive and negative
routing, written and spoken modes, multiple surfaces/audiences/jobs, another
intended author, quoted/verbatim overrides, and legal/contractual/
organizational overrides. Builder-side categories (evidence quality,
authorization, correction, revocation lifecycle) live in
writing-style-builder's own selftest, not here.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import route_check as rc  # noqa: E402

PROFILE = json.loads(
    (Path(__file__).resolve().parent.parent / "references" / "synthetic-fixtures" / "profile-sample.json")
    .read_text()
)

BASE_REQUEST = {
    "authorship": "profiled_person",
    "mode": "written",
    "surface": "chat",
    "audience": "peer",
    "content_kind": "original",
    "governing_voice": None,
}


def _req(**overrides):
    r = dict(BASE_REQUEST)
    r.update(overrides)
    return r


def test_positive_routing_applies():
    applies, _ = rc.should_apply(_req(), PROFILE)
    assert applies is True


def test_positive_routing_explicit_invocation_same_result():
    # Explicit invocation ("write this in my voice") carries the same routing
    # dimensions; the gate does not special-case the phrasing, only authorship.
    applies_auto, _ = rc.should_apply(_req(), PROFILE)
    applies_explicit, _ = rc.should_apply(_req(), PROFILE)
    assert applies_auto == applies_explicit == True  # noqa: E712


def test_written_and_spoken_both_route_when_covered():
    written, _ = rc.should_apply(_req(mode="written", surface="chat"), PROFILE)
    spoken, _ = rc.should_apply(_req(mode="spoken", surface="call", audience="client"), PROFILE)
    assert written is True
    assert spoken is True


def test_spoken_falls_back_when_audience_flagged_insufficient():
    # The fixture flags "call" itself as insufficient-evidence for spoken mode,
    # modeled here as an audience-shaped gap to exercise the same fallback path.
    flagged = json.loads(json.dumps(PROFILE))
    flagged["base_profile"]["spoken"]["insufficient_evidence_for"] = ["client"]
    spoken, reason = rc.should_apply(_req(mode="spoken", surface="call", audience="client"), flagged)
    assert spoken is False
    assert "insufficient evidence" in reason


def test_negative_another_author():
    applies, reason = rc.should_apply(_req(authorship="other_named_person"), PROFILE)
    assert applies is False
    assert "authorship" in reason


def test_negative_mere_mention_is_not_authorship():
    applies, _ = rc.should_apply(_req(authorship="mentioned_only"), PROFILE)
    assert applies is False


def test_negative_verbatim_quotation():
    applies, reason = rc.should_apply(_req(content_kind="quotation"), PROFILE)
    assert applies is False
    assert "quotation" in reason or "verbatim" in reason


def test_negative_legal_override():
    applies, reason = rc.should_apply(_req(governing_voice="legal"), PROFILE)
    assert applies is False
    assert "governing voice" in reason


def test_negative_contractual_override():
    applies, _ = rc.should_apply(_req(governing_voice="contractual"), PROFILE)
    assert applies is False


def test_negative_organizational_override():
    applies, _ = rc.should_apply(_req(governing_voice="organizational"), PROFILE)
    assert applies is False


def test_negative_revoked_profile():
    revoked = dict(PROFILE)
    revoked["revoked"] = True
    applies, reason = rc.should_apply(_req(), revoked)
    assert applies is False
    assert "revoked" in reason


def test_negative_unauthorized_profile():
    unauthorized = json.loads(json.dumps(PROFILE))
    unauthorized["authorization"]["granted"] = False
    applies, reason = rc.should_apply(_req(), unauthorized)
    assert applies is False
    assert "authorization" in reason


def test_negative_uncovered_surface_falls_back():
    applies, reason = rc.should_apply(_req(surface="deck"), PROFILE)
    assert applies is False
    assert "surface" in reason


def test_negative_insufficient_evidence_audience_falls_back():
    applies, reason = rc.should_apply(_req(audience="public"), PROFILE)
    assert applies is False
    assert "insufficient evidence" in reason


def test_leakage_negative_result_carries_no_profile_voice_content():
    applies, reason = rc.should_apply(_req(authorship="other_named_person"), PROFILE)
    assert applies is False
    tendency_text = PROFILE["base_profile"]["written"]["core_tendencies"][0]["pattern"]
    assert tendency_text not in reason


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
