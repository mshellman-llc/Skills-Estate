#!/usr/bin/env python3
"""Selftest for charter_check.py.

Runs the gate against the fixtures in scripts/fixtures/ and asserts:
  - the passing charter exits 0 with no FAIL lines
  - each failing fixture exits 1 AND fails the specific check it was built to trip

The em-dash fixture is synthesized into a temp file at runtime (from the passing charter)
so the shipped skill tree itself contains no em dash character.

Exit code 0 when every expectation holds, 1 otherwise. Stdlib only.
"""

import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CHECKER = os.path.join(HERE, "charter_check.py")
FIXTURES = os.path.join(HERE, "fixtures")

# fixture file -> (expected exit code, check id that must appear in a FAIL line, or None)
CASES = [
    ("charter_pass.md", 0, None),
    ("charter_fail_missing_section.md", 1, "required-sections"),
    ("charter_fail_no_stamp.md", 1, "scope-stamp"),
    ("charter_fail_raci_unassigned.md", 1, "raci-filled"),
    ("charter_fail_raci_coverage.md", 1, "raci-coverage"),
    ("charter_fail_placeholder.md", 1, "placeholders"),
    ("charter_fail_em_dash.md", 1, "em-dash"),
]


def synthesize_em_dash_fixture():
    """Build the em-dash failing charter in a temp file from the passing fixture."""
    with open(os.path.join(FIXTURES, "charter_pass.md"), encoding="utf-8") as f:
        text = f.read()
    text = text.replace(
        "measured against.", "measured against " + chr(0x2014) + " always.", 1
    )
    fd, path = tempfile.mkstemp(suffix=".md", prefix="charter_fail_em_dash_")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def main():
    failures = []
    temp_paths = []
    for fname, want_code, want_check in CASES:
        if fname == "charter_fail_em_dash.md":
            path = synthesize_em_dash_fixture()
            temp_paths.append(path)
        else:
            path = os.path.join(FIXTURES, fname)
        if not os.path.exists(path):
            failures.append("%s: fixture missing" % fname)
            continue
        proc = subprocess.run(
            [sys.executable, CHECKER, path],
            capture_output=True,
            text=True,
        )
        out = proc.stdout
        if proc.returncode != want_code:
            failures.append(
                "%s: expected exit %d, got %d\n%s"
                % (fname, want_code, proc.returncode, out)
            )
            continue
        if want_check is None:
            if "FAIL " in out:
                failures.append("%s: expected zero FAIL lines\n%s" % (fname, out))
        else:
            if ("FAIL %s" % want_check) not in out:
                failures.append(
                    "%s: expected a 'FAIL %s' line\n%s" % (fname, want_check, out)
                )
    for p in temp_paths:
        try:
            os.unlink(p)
        except OSError:
            pass
    for f in failures:
        print("SELFTEST FAIL %s" % f)
    print(
        "charter_check_selftest: %d/%d cases passed"
        % (len(CASES) - len(failures), len(CASES))
    )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
