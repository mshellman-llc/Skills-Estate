#!/usr/bin/env python3
"""route_check.py - deterministic routing gate for personal-writing-style-runtime.

Stdlib only. Answers one question: given a request's routing dimensions and a
confirmed profile, should the profile's voice apply? This is a hard gate a
per-person install can call before drafting; it does not draft anything
itself, and it never reads or returns profile voice content, only a bool
and a reason.

Usage:
    python3 route_check.py REQUEST.json PROFILE.json
"""
from __future__ import annotations
import json
import sys


def should_apply(request: dict, profile: dict) -> tuple[bool, str]:
    if profile.get("revoked"):
        return False, "profile is revoked"
    if not profile.get("authorization", {}).get("granted"):
        return False, "profile lacks granted authorization"

    if request.get("authorship") != "profiled_person":
        return False, f"authorship is {request.get('authorship')!r}, not the profiled person"

    if request.get("content_kind") in {"quotation", "verbatim"}:
        return False, "content is a quotation or verbatim excerpt"

    if request.get("governing_voice") in {"legal", "contractual", "regulatory", "organizational"}:
        return False, f"governing voice is {request.get('governing_voice')!r}, overrides personal profile"

    routing = profile.get("routing", {})
    mode = request.get("mode")
    if mode not in routing.get("modes", []):
        return False, f"mode {mode!r} not covered by this profile"

    surface = request.get("surface")
    if surface not in routing.get("surfaces", []):
        return False, f"surface {surface!r} not covered by this profile"

    audience = request.get("audience")
    insufficient = profile.get("base_profile", {}).get(mode, {}).get("insufficient_evidence_for", [])
    if audience in insufficient:
        return False, f"audience {audience!r} has insufficient evidence; fall back to plain drafting"

    return True, "authorship, mode, surface, and audience all resolve to the confirmed profile"


def _main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2
    with open(argv[1], encoding="utf-8") as f:
        request = json.load(f)
    with open(argv[2], encoding="utf-8") as f:
        profile = json.load(f)
    applies, reason = should_apply(request, profile)
    print(json.dumps({"apply_profile": applies, "reason": reason}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv))
