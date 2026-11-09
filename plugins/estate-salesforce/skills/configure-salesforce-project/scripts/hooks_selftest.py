#!/usr/bin/env python3
"""Run the hook regression suites and fail loudly if any case fails.

The suites themselves are bash, because the things under test are bash functions
sourced by git and Claude Code hooks, and reimplementing their quoting semantics
in another language would test the reimplementation. This wrapper exists so they
run under the house `verify.sh`, which collects `scripts/*_selftest.py`.

Every case here was a bug that shipped. They share a shape worth naming: each one
FAILED OPEN or recorded the wrong answer, rather than breaking visibly. A guard
that stops guarding reports nothing, so none of these were found by using the
stack -- only by instrumenting it. That is the argument for keeping them.
"""

import subprocess
import sys
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent.parent / "references" / "hooks" / "tests"


def main() -> int:
    suites = sorted(TESTS_DIR.glob("*.test.sh"))
    if not suites:
        print(f"FAIL: no test suites found under {TESTS_DIR}")
        return 1

    failed = []
    for suite in suites:
        print(f"== {suite.name} ==")
        result = subprocess.run(
            ["bash", str(suite)],
            capture_output=True,
            text=True,
        )
        sys.stdout.write(result.stdout)
        if result.stderr.strip():
            sys.stdout.write(result.stderr)
        if result.returncode != 0:
            failed.append(suite.name)
        print()

    if failed:
        print(f"FAILED: {', '.join(failed)}")
        return 1

    print(f"PASSED {len(suites)} hook suite(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
