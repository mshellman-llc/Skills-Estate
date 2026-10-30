#!/usr/bin/env python3
"""Validate the shared build card and its runtime references.

The build card is maintained once in _shared. Brand values are resolved at run
 time from the selected Markdown profile; they must not be generated into it.
The historical command name and --check flag remain supported for callers.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path


def validate(skills: Path) -> list[str]:
    card = skills / "_shared/build-card.md"
    if not card.is_file():
        return [f"missing shared build card: {card}"]
    text = card.read_text(encoding="utf-8")
    errors = []
    if re.search(r"#[0-9a-fA-F]{6}\b", text):
        errors.append("build card duplicates literal brand colors; use the profile runtime")
    for ref in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
        if "://" not in ref and not (card.parent / ref.split("#", 1)[0]).is_file():
            errors.append(f"missing build-card reference: {ref}")
    for rel in ("brand-renderer/scripts/runtime_preflight.py",
                "brand-renderer/brand/brand_profile.py",
                "prose-pass/scripts/prose_check.py", "quality-gate/scripts/quality_gate.py"):
        if not (skills / rel).is_file():
            errors.append(f"missing build runtime: {rel}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate without rewriting the maintained card")
    parser.add_argument("--skills-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    errors = validate(args.skills_root)
    for error in errors:
        print(f"FAIL: {error}")
    if not errors:
        print("build card: PASS; brand values resolve from the selected profile at runtime")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
