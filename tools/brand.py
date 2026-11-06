#!/usr/bin/env python3
"""Read the canonical profile and emit CSS or renderer-compatible JSON."""
import argparse
import importlib.util
import json
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "skills/brand-renderer/brand/brand_profile.py"
SPEC = importlib.util.spec_from_file_location("estate_brand_profile", MODULE)
profile_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(profile_module)
load_profile = profile_module.load_profile
css = profile_module.css
compile_tokens = profile_module.compile_tokens

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("profile", type=Path)
    ap.add_argument("--tokens", action="store_true")
    args = ap.parse_args()
    try:
        value = load_profile(args.profile)
        print(json.dumps(compile_tokens(value, args.profile), indent=2) if args.tokens else css(value))
    except (ValueError, KeyError, OSError) as exc:
        ap.exit(2, str(exc) + "\n")
