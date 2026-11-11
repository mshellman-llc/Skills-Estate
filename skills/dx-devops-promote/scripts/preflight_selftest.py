#!/usr/bin/env python3
"""Run the DevOps Center promotion capability and routing regression suite."""

import os
import tempfile
import subprocess
import sys
from pathlib import Path


def main() -> int:
    test = Path(__file__).resolve().parent.parent / "tests" / "preflight.test.sh"
    with tempfile.TemporaryDirectory(prefix="promotion-selftest-") as folder:
        result = subprocess.run(["bash", str(test)], text=True, capture_output=True,
                                env={**os.environ, "ESTATE_TEST_OUTPUT": folder})
        print(result.stdout, end="")
        print(result.stderr, end="", file=sys.stderr)
        return result.returncode


if __name__ == "__main__":
    sys.exit(main())
