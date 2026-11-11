#!/usr/bin/env python3
"""Run the DevOps Center promotion capability and routing regression suite."""

import subprocess
import sys
from pathlib import Path


def main() -> int:
    test = Path(__file__).resolve().parent.parent / "tests" / "preflight.test.sh"
    result = subprocess.run(["bash", str(test)], text=True)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
