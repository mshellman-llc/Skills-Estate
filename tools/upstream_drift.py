#!/usr/bin/env python3
"""Report upstream files that changed since an estate skill adapted them.

Each adapted skill lists its upstream files in UPSTREAM.md as table rows of
`| <sha256 at adoption> | <path in the upstream repository> |`. This tool
compares those hashes with an upstream checkout. It reads files only.

Rows may carry extra columns, an uppercase hash or a backticked path. A table
row that starts with a hash-like value of the wrong length, or an UPSTREAM.md
with no rows at all, is reported as malformed so no skill drops out silently.

Exit codes: 0 when nothing changed, 1 when a file changed, disappeared or a
row is malformed, 2 when the upstream path is missing or no skill declares an
upstream.

Usage:
    python3 tools/upstream_drift.py --upstream /path/to/Claude-Skills
    python3 tools/upstream_drift.py --upstream /path/to/Claude-Skills --json
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HASH = re.compile(r"[0-9a-fA-F]{64}")
HASHLIKE = re.compile(r"[0-9a-fA-F]{32,}")


def declared(root=ROOT):
    rows = []
    for path in sorted((root / "skills").glob("*/UPSTREAM.md")):
        skill, found = path.parent.name, 0
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            first = cells[0] if cells else ""
            if HASH.fullmatch(first) and len(cells) >= 2 and cells[1].strip("`").strip():
                rows.append({"skill": skill, "path": cells[1].strip("`").strip(), "adopted_sha256": first.lower()})
                found += 1
            elif HASHLIKE.fullmatch(first) or HASH.fullmatch(first):
                rows.append({"skill": skill, "path": f"UPSTREAM.md line {number}", "state": "malformed"})
        if not found:
            rows.append({"skill": skill, "path": "UPSTREAM.md", "state": "malformed"})
    return rows


def compare(rows, upstream):
    for row in rows:
        if row.get("state") == "malformed":
            continue
        file = upstream / row["path"]
        if not file.is_file():
            row["state"] = "missing"
        else:
            row["current_sha256"] = hashlib.sha256(file.read_bytes()).hexdigest()
            row["state"] = "unchanged" if row["current_sha256"] == row["adopted_sha256"] else "changed"
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--upstream", required=True, help="Local checkout of the upstream repository")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    upstream = Path(args.upstream).expanduser()
    rows = declared()
    if not upstream.is_dir() or not rows:
        print("error: " + ("upstream checkout not found" if not upstream.is_dir() else "no skill declares an upstream"), file=sys.stderr)
        return 2
    rows = compare(rows, upstream)
    drift = [r for r in rows if r["state"] != "unchanged"]
    if args.json:
        print(json.dumps({"checked": len(rows), "drift": drift}, indent=2))
    else:
        print(f"{len(rows)} upstream files checked; {len(drift)} changed or missing.")
        for r in drift:
            print(f"- {r['skill']}: {r['path']} is {r['state']}")
    return 1 if drift else 0


if __name__ == "__main__":
    sys.exit(main())
