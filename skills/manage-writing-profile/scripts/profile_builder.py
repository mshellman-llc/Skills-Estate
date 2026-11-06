#!/usr/bin/env python3
"""profile_builder.py - mechanical half of the manage-writing-profile workflow.

Stdlib only. Does the deterministic parts a build needs and must not get
wrong by inference: which evidence is eligible, whether a draft or existing
profile matches the schema, and whether two patterns on the same dimension
disagree. Pattern inference from raw evidence text is the agent's job, done
under SKILL.md step 3, not this script's.

Usage:
    python3 profile_builder.py filter EVIDENCE.json      # keep authored-only
    python3 profile_builder.py validate PROFILE.json      # schema check
    python3 profile_builder.py conflicts PATTERNS.json    # find same-dimension disagreement
"""
from __future__ import annotations
import json
import sys

ELIGIBLE_PROVENANCE = {"authored", "templated-edited"}
REQUIRED_TOP_KEYS = {
    "person_id", "authorization", "revoked", "last_confirmed", "history",
    "routing", "base_profile", "channel_overlays", "conflicts",
}
REQUIRED_ROUTING_KEYS = {
    "authorship_trigger", "modes", "surfaces", "audiences", "relationships", "jobs",
}


def filter_authored(evidence: list[dict]) -> list[dict]:
    """Drop every evidence unit whose provenance isn't eligible for the profile."""
    return [e for e in evidence if e.get("provenance") in ELIGIBLE_PROVENANCE]


def validate_profile(profile: dict) -> list[str]:
    """Return schema violations; an empty list means the profile is well-formed.

    This checks shape and eligibility, not voice quality — a well-formed
    profile can still be thin. That judgment stays with the person reviewing
    the draft under SKILL.md step 5.
    """
    errors = []
    missing = REQUIRED_TOP_KEYS - profile.keys()
    if missing:
        errors.append(f"missing top-level keys: {sorted(missing)}")

    if "person_id" in profile and not isinstance(profile["person_id"], str):
        errors.append("person_id must be a string")

    if "authorization" in profile:
        auth = profile["authorization"]
        if not isinstance(auth, dict) or not auth.get("granted"):
            errors.append("authorization.granted must be true; a profile cannot exist without it")

    if "routing" in profile:
        missing_routing = REQUIRED_ROUTING_KEYS - profile["routing"].keys()
        if missing_routing:
            errors.append(f"routing missing keys: {sorted(missing_routing)}")

    for mode in ("written", "spoken"):
        tendencies = profile.get("base_profile", {}).get(mode, {}).get("core_tendencies", [])
        for t in tendencies:
            if t.get("provenance") not in ELIGIBLE_PROVENANCE:
                errors.append(f"{mode} tendency {t.get('pattern')!r} has ineligible provenance {t.get('provenance')!r}")
            if not t.get("sources"):
                errors.append(f"{mode} tendency {t.get('pattern')!r} names no source count")

    return errors


def detect_conflicts(patterns: list[dict]) -> list[dict]:
    """Group patterns by dimension; flag any dimension with more than one distinct reading."""
    by_dimension: dict[str, set[str]] = {}
    for p in patterns:
        by_dimension.setdefault(p["dimension"], set()).add(p["reading"])
    return [
        {"dimension": dim, "readings": sorted(readings), "resolution": "unresolved"}
        for dim, readings in by_dimension.items()
        if len(readings) > 1
    ]


def _main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2
    cmd, path = argv[1], argv[2]
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    if cmd == "filter":
        print(json.dumps(filter_authored(data), indent=2))
        return 0
    if cmd == "validate":
        errors = validate_profile(data)
        if errors:
            for e in errors:
                print(f"FAIL: {e}")
            return 1
        print("OK: profile matches schema")
        return 0
    if cmd == "conflicts":
        print(json.dumps(detect_conflicts(data), indent=2))
        return 0

    print(f"unknown command: {cmd}")
    return 2


if __name__ == "__main__":
    sys.exit(_main(sys.argv))
