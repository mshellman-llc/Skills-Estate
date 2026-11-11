#!/usr/bin/env python3
"""record_publish.py - stamp which bundles were uploaded to a cloud tier.

The claude.ai organization tier and Cowork are reachable only through a web UI.
Nothing in this toolchain can read them, so the estate cannot diff them the way
it diffs a local mount. Before this existed, the diff simply omitted them and
printed "all mirrored", which read as "everything is current" when two of three
surfaces were unchecked and could be months behind.

This does not verify an upload. It records a claim: a human uploaded these
bundles, at this content hash, on this date. estate_diff.py then compares the
current bundle hashes against the claim and reports how many are pending. A
known gap that is stated is worth far more than a silent one.

    python3 record_publish.py --surface claude.ai-org
    python3 record_publish.py --surface cowork --only sow
    python3 record_publish.py --status

Run it AFTER the upload, not before. The date comes from the caller, because
scripts here cannot read the clock deterministically; it defaults to today from
the filesystem's own mtime on the newest bundle, which is close enough to be
useful and honest about being derived.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
CONFIG = SKILL / "surfaces.json"
REPO = SKILL.parent.parent
DIST = REPO / "dist"


def load_config() -> dict:
    try:
        return json.loads(CONFIG.read_text())
    except (OSError, json.JSONDecodeError) as e:
        sys.exit(f"error: bad config {CONFIG}: {e}")


def ledger_path(cfg: dict) -> Path:
    return SKILL / cfg.get("ledger", "publish-ledger.json")


def load_ledger(cfg: dict) -> dict:
    p = ledger_path(cfg)
    if not p.exists():
        return {"_comment": "Written by record_publish.py. Each entry is a human's "
                            "claim that these bundle hashes were uploaded to that "
                            "surface. It is not verification.",
                "surfaces": {}}
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError as e:
        sys.exit(f"error: ledger {p} does not parse: {e}")


def bundle_hashes(only: str | None = None) -> dict:
    if not DIST.exists():
        sys.exit(f"error: no dist at {DIST}. Run build_bundles.py first.")
    out = {}
    for b in sorted(DIST.glob("*.skill")):
        name = b.stem
        if only and name != only:
            continue
        out[name] = hashlib.sha1(b.read_bytes()).hexdigest()
    if not out:
        sys.exit(f"error: no bundles matched{' ' + only if only else ''} in {DIST}")
    return out


def pending(cfg: dict, ledger: dict, surface: str) -> tuple:
    """-> (never_recorded, stale, current). Names only."""
    recorded = ledger.get("surfaces", {}).get(surface, {}).get("bundles", {})
    now = bundle_hashes()
    never = sorted(n for n in now if n not in recorded)
    stale = sorted(n for n in now if n in recorded and recorded[n] != now[n])
    current = sorted(n for n in now if recorded.get(n) == now[n])
    return never, stale, current


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--surface", help="cloud surface name from surfaces.json")
    ap.add_argument("--only", help="record a single skill rather than all of dist")
    ap.add_argument("--date", help="upload date, YYYY-MM-DD (default: today)")
    ap.add_argument("--status", action="store_true", help="report pending uploads and exit")
    args = ap.parse_args()

    cfg = load_config()
    ledger = load_ledger(cfg)
    known = [s["name"] for s in cfg.get("cloud_surfaces", [])]

    if args.status or not args.surface:
        print(f"\npublish ledger  ({len(bundle_hashes())} bundles in dist)\n")
        for name in known:
            never, stale, current = pending(cfg, ledger, name)
            when = ledger.get("surfaces", {}).get(name, {}).get("last_recorded", "never")
            print(f"  {name}")
            print(f"    last recorded : {when}")
            print(f"    up to date    : {len(current)}")
            print(f"    changed since : {len(stale)}" + (f"  {', '.join(stale)}" if stale else ""))
            print(f"    never recorded: {len(never)}" + (f"  {', '.join(never)}" if never else ""))
        if not args.surface:
            print("\n  Record an upload with --surface <name> after you have done it.\n")
        return 0

    if args.surface not in known:
        sys.exit(f"error: unknown surface {args.surface!r}. Known: {', '.join(known) or 'none'}")

    date = args.date or time.strftime("%Y-%m-%d")
    entry = ledger.setdefault("surfaces", {}).setdefault(args.surface, {"bundles": {}})
    entry["bundles"].update(bundle_hashes(args.only))
    entry["last_recorded"] = date

    ledger_path(cfg).write_text(json.dumps(ledger, indent=2) + "\n")
    scope = args.only or f"all {len(bundle_hashes())} bundles"
    print(f"recorded {scope} as uploaded to {args.surface} on {date}")
    print(f"  ledger: {ledger_path(cfg)}")
    print("  This records your claim. It does not verify the upload landed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
