#!/usr/bin/env python3
"""Record reported bundle publication for an explicitly configured destination.

This is a claim ledger, not an upload, account discovery or destination readback.
Use an authorized workspace configuration with cloud_surfaces and a ledger path.
Relative ledger paths resolve beside that configuration. The CLI requires the
bundle directory explicitly and refuses to write into its reusable skill tree.

    python3 record_publish.py --config /path/to/surfaces.json --dist /path/to/dist --surface selected-destination
    python3 record_publish.py --config /path/to/surfaces.json --dist /path/to/dist --status

Record only after the upload occurred. --date supplies its date; the default is
the current local calendar date, not evidence of when an upload actually occurred.
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


def load_config(path: Path = CONFIG) -> dict:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as e:
        sys.exit(f"error: bad config {path}: {e}")


def ledger_path(cfg: dict, config_dir: Path = SKILL) -> Path:
    value = cfg.get("ledger")
    if not isinstance(value, str) or not value.strip():
        sys.exit("error: configuration must supply an explicit ledger path")
    target = Path(value).expanduser()
    if not target.is_absolute():
        target = config_dir / target
    return target.resolve()


def load_ledger(cfg: dict, config_dir: Path = SKILL) -> dict:
    p = ledger_path(cfg, config_dir)
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
    global DIST
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", type=Path, required=True, help="explicit workspace surface configuration")
    ap.add_argument("--dist", type=Path, required=True, help="explicit directory containing prepared .skill bundles")
    ap.add_argument("--surface", help="cloud surface name from surfaces.json")
    ap.add_argument("--only", help="record a single skill rather than all of dist")
    ap.add_argument("--date", help="upload date, YYYY-MM-DD (default: today)")
    ap.add_argument("--status", action="store_true", help="report pending uploads and exit")
    args = ap.parse_args()

    config_path = args.config.expanduser().resolve()
    DIST = args.dist.expanduser().resolve()
    cfg = load_config(config_path)
    destination = ledger_path(cfg, config_path.parent)
    if destination == SKILL.resolve() or SKILL.resolve() in destination.parents:
        ap.error("ledger must be outside the reusable skill directory")
    if not destination.parent.is_dir():
        ap.error("ledger parent directory must already exist in the authorized workspace")
    ledger = load_ledger(cfg, config_path.parent)
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

    destination.write_text(json.dumps(ledger, indent=2) + "\n")
    scope = args.only or f"all {len(bundle_hashes())} bundles"
    print(f"recorded {scope} as uploaded to {args.surface} on {date}")
    print(f"  ledger: {destination}")
    print("  This records your claim. It does not verify the upload landed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
