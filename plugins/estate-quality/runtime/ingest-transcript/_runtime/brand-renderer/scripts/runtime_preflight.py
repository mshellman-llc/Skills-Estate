#!/usr/bin/env python3
"""Resolve brand assets, writing diagnostics and the release validator.

brand-renderer is the entry point for every branded surface, so it is the skill
that has to prove the runtime before anything is drafted. It resolves writing-diagnostics
for diagnostics under Writing Integrity and review-deliverable for the release decision. The direction is one way:
neither of those resolves brand-renderer, which is what keeps a bundle from
carrying a second copy of the skill that carried it.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def first_file(candidates: list[Path]) -> Path | None:
    for candidate in candidates:
        try:
            if candidate.is_file():
                return candidate.resolve()
        except OSError:
            continue
    return None


def resolve() -> dict:
    asset_resolver = first_file([ROOT / "scripts" / "resolve_assets.py"])
    prose_root_candidates = [
        ROOT / "_runtime" / "writing-diagnostics",
        ROOT.parent / "writing-diagnostics",
        ROOT.parent / "_runtime" / "writing-diagnostics",
    ]
    quality_root_candidates = [
        ROOT / "_runtime" / "review-deliverable",
        ROOT.parent / "review-deliverable",
        ROOT.parent / "_runtime" / "review-deliverable",
    ]
    for key, candidates in (("ESTATE_PROSE_RUNTIME", prose_root_candidates),
                            ("ESTATE_QUALITY_RUNTIME", quality_root_candidates)):
        if os.environ.get(key):
            path = Path(os.environ[key]).expanduser()
            if not path.is_absolute():
                raise ValueError(key + " must name an explicitly selected absolute runtime directory")
            candidates[:] = [path]
    prose_check = first_file([p / "scripts" / "writing_check.py"
                              for p in prose_root_candidates])
    prose_receipt = first_file([p / "scripts" / "prose_receipt.py"
                                for p in prose_root_candidates])
    quality_gate = first_file([p / "scripts" / "quality_gate.py"
                               for p in quality_root_candidates])
    brand_check = first_file([ROOT / "scripts" / "brand_check.py"])
    report = {
        "ok": all((asset_resolver, prose_check, prose_receipt, quality_gate,
                   brand_check)),
        "brand_renderer_root": str(ROOT.resolve()),
        "asset_resolver": str(asset_resolver) if asset_resolver else None,
        "brand_check": str(brand_check) if brand_check else None,
        "prose_check": str(prose_check) if prose_check else None,
        "prose_receipt": str(prose_receipt) if prose_receipt else None,
        "quality_gate": str(quality_gate) if quality_gate else None,
        "missing": [],
    }
    for name in ("asset_resolver", "brand_check", "prose_check", "prose_receipt",
                 "quality_gate"):
        if not report[name]:
            report["missing"].append(name)
    if asset_resolver:
        proc = subprocess.run(
            [sys.executable, str(asset_resolver), "--json"],
            capture_output=True, text=True)
        try:
            report["assets"] = json.loads(proc.stdout)
        except json.JSONDecodeError:
            report["assets"] = {"ok": False, "output": proc.stdout.strip()}
        if proc.returncode != 0:
            report["ok"] = False
            report["missing"].append("brand assets")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        report = resolve()
    except ValueError as exc:
        report = {"ok": False, "missing": [str(exc)]}
    if args.json:
        print(json.dumps(report, indent=2))
    elif report["ok"]:
        print("release runtime: PASS")
        print("assets: {}".format(report["assets"]["brand_root"]))
        print("prose: {}".format(report["prose_check"]))
        print("brand: {}".format(report["brand_check"]))
        print("release: {}".format(report["quality_gate"]))
    else:
        print("release runtime: FAIL")
        for item in report["missing"]:
            print("missing: {}".format(item))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
