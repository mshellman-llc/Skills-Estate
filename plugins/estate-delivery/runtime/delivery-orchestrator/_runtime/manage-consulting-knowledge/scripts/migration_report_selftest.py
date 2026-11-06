#!/usr/bin/env python3
"""Selftest for non-mutating legacy Hub audit."""

import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import migration_report  # noqa: E402


with tempfile.TemporaryDirectory() as directory:
    root = pathlib.Path(directory)
    hub = root / "Synthetic Sales" / "example" / "knowledge-hub"
    hub.mkdir(parents=True)
    (hub / "01-company-profile.md").write_text("profile")
    (hub / "05-scope-plan-status.md").write_text("mixed")
    (hub / "custom.md").write_text("unknown")
    before = {path: path.read_bytes() for path in hub.iterdir()}
    report = migration_report.audit(root, {"Synthetic Sales": "opportunity"})
    unspecified = migration_report.audit(root)
    summary = report["summary"]
    checks = {
        "unconfigured folder does not imply lifecycle": unspecified["summary"]["contextProposals"] == 0 and unspecified["hubs"][0]["proposedContextType"] == "unclassified",
        "one Hub found": summary["hubs"] == 1,
        "three files inspected": summary["files"] == 3,
        "one direct mapping": summary["mapped"] == 1,
        "one ambiguity retained": summary["ambiguous"] == 1,
        "one unmapped file retained": summary["unmapped"] == 1,
        "opportunity context proposed": summary["contextProposals"] == 1,
        "no human approval invented": summary["humanApprovalsInferred"] == 0,
        "source bytes unchanged": before == {path: path.read_bytes() for path in hub.iterdir()},
    }
    failed = [name for name, ok in checks.items() if not ok]
    for name, ok in checks.items():
        print("  {} {}".format("PASS" if ok else "FAIL", name))
    if failed:
        sys.exit(1)
