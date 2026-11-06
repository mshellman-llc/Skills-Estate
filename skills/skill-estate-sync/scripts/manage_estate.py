#!/usr/bin/env python3
"""Run the selected canonical checkout's estate CLI from an installed skill.

This bridge never downloads tooling or guesses a repository from the working
directory. Select --repo, or use the repository pointer written by installation.
"""
import argparse
from pathlib import Path
import subprocess
import sys


def repository(explicit, home):
    pointer = home / ".config/skills-estate/repository"
    selected = explicit if explicit is not None else pointer
    if explicit is None and not pointer.is_symlink():
        raise ValueError("No registered estate. Pass --repo /absolute/path/to/Skills-Estate.")
    root = selected.expanduser().resolve(strict=True)
    required = ("tools/estate.py", "tools/portable.py", "policies/skill-standard.md")
    missing = [name for name in required if not (root / name).is_file()]
    if missing or not (root / "skills").is_dir():
        raise ValueError("Selected checkout lacks the canonical estate tooling: " + str(root))
    return root


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, help="Explicit canonical checkout")
    parser.add_argument("--home", type=Path, default=Path.home(), help="Installation home; use an isolated home for tests")
    parser.add_argument("command", choices=[
        "validate", "build", "bundle", "install", "adopt", "sync", "status",
        "restore", "record-publication", "pin-installed", "rollback", "update", "test-local",
    ])
    parser.add_argument("arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    try:
        root = repository(args.repo, args.home.expanduser().resolve())
        command = [sys.executable, str(root / "tools/estate.py"),
                   "--home", str(args.home.expanduser().resolve()), args.command, *args.arguments]
        return subprocess.run(command, cwd=root, check=False).returncode
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
