#!/usr/bin/env python3
"""Produce a bounded, read-only receipt for Git, file, or generic work."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys
from typing import Dict, List, Optional


PRIVATE_PATTERNS = (
    re.compile(r"/(?:Users|home)/[^/\s]+/"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)(?:api[_-]?key|client[_-]?secret|access[_-]?token)\s*[:=]\s*['\"][^'\"]+"),
)


class ReceiptError(Exception):
    pass


def run_git(path: pathlib.Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(path), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and result.returncode:
        raise ReceiptError(result.stderr.strip() or "git command failed")
    return result.stdout.strip()


def count_findings(text: str) -> int:
    return sum(len(pattern.findall(text)) for pattern in PRIVATE_PATTERNS)


def git_receipt(path: pathlib.Path, base: str, verification: str) -> Dict[str, object]:
    root = pathlib.Path(run_git(path, "rev-parse", "--show-toplevel")).resolve()
    branch = run_git(root, "branch", "--show-current") or "detached"
    commit = run_git(root, "rev-parse", "--short", "HEAD")
    status_lines = [line for line in run_git(root, "status", "--short").splitlines() if line]

    base_exists = run_git(root, "rev-parse", "--verify", "{}^{{commit}}".format(base), check=False)
    ahead: Optional[int] = None
    behind: Optional[int] = None
    changed = set()
    diff_parts: List[str] = []
    if base_exists:
        counts = run_git(root, "rev-list", "--left-right", "--count", "{}...HEAD".format(base)).split()
        behind, ahead = int(counts[0]), int(counts[1])
        changed.update(run_git(root, "diff", "--name-only", "{}...HEAD".format(base)).splitlines())
        diff_parts.append(run_git(root, "diff", "--no-ext-diff", "{}...HEAD".format(base), check=False))
    changed.update(run_git(root, "diff", "--name-only").splitlines())
    changed.update(run_git(root, "diff", "--cached", "--name-only").splitlines())
    changed.update(run_git(root, "ls-files", "--others", "--exclude-standard").splitlines())
    diff_parts.append(run_git(root, "diff", "--no-ext-diff", check=False))
    diff_parts.append(run_git(root, "diff", "--cached", "--no-ext-diff", check=False))

    private_findings = count_findings("\n".join(diff_parts))
    if status_lines:
        state = "built-locally"
    elif ahead:
        state = "committed-locally"
    else:
        state = "unchanged"
    return {
        "kind": "git",
        "state": state,
        "location": str(root),
        "branch": branch,
        "commit": commit,
        "base": base if base_exists else "unresolved: {}".format(base),
        "ahead": ahead if ahead is not None else "unknown",
        "behind": behind if behind is not None else "unknown",
        "changedFiles": len([name for name in changed if name]),
        "workingTree": "clean" if not status_lines else "dirty: {}".format(len(status_lines)),
        "privateFindings": private_findings,
        "verification": verification,
    }


def file_receipt(path: pathlib.Path, verification: str) -> Dict[str, object]:
    resolved = path.expanduser().resolve()
    if not resolved.is_file():
        raise ReceiptError("file does not exist: {}".format(resolved))
    content = resolved.read_bytes()
    return {
        "kind": "file",
        "state": "saved-locally",
        "location": str(resolved),
        "bytes": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
        "verification": verification,
        "cloudChanged": "not-proven",
    }


def generic_receipt(args) -> Dict[str, object]:
    return {
        "kind": "generic",
        "state": args.state or "proposed",
        "location": args.location or str(pathlib.Path(args.path).expanduser().resolve()),
        "authority": args.authority or "not-stated",
        "availability": args.availability or "not-stated",
        "verification": args.verification,
    }


def render(receipt: Dict[str, object]) -> str:
    preferred = (
        "kind", "state", "location", "authority", "availability", "branch",
        "commit", "base", "ahead", "behind", "changedFiles", "workingTree",
        "privateFindings", "bytes", "sha256", "verification", "cloudChanged",
    )
    lines = ["WORK TRUTH"]
    for key in preferred:
        if key in receipt and len(lines) < 12:
            lines.append("{}: {}".format(key, receipt[key]))
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=("auto", "git", "file", "generic"), default="auto")
    parser.add_argument("--path", default=".")
    parser.add_argument("--base", default="origin/main")
    parser.add_argument("--state")
    parser.add_argument("--location")
    parser.add_argument("--authority")
    parser.add_argument("--availability")
    parser.add_argument("--verification", default="not-run")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    path = pathlib.Path(args.path)
    kind = args.kind
    if kind == "auto":
        if run_git(path, "rev-parse", "--is-inside-work-tree", check=False) == "true":
            kind = "git"
        elif path.expanduser().is_file():
            kind = "file"
        else:
            kind = "generic"
    try:
        if kind == "git":
            receipt = git_receipt(path, args.base, args.verification)
        elif kind == "file":
            receipt = file_receipt(path, args.verification)
        else:
            receipt = generic_receipt(args)
    except ReceiptError as error:
        print("WORK TRUTH ERROR: {}".format(error), file=sys.stderr)
        return 2
    print(json.dumps(receipt, indent=2) if args.json else render(receipt))
    return 0


if __name__ == "__main__":
    sys.exit(main())
