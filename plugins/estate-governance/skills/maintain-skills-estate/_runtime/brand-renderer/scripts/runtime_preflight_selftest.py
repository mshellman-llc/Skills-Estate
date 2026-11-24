#!/usr/bin/env python3
"""Self-test for the cloud runtime and asset preflight."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import runtime_preflight  # noqa: E402

report = runtime_preflight.resolve()
print("runtime ok={}".format(report["ok"]))
print("asset resolver={}".format(report["asset_resolver"]))
print("prose checker={}".format(report["prose_check"]))
print("brand checker={}".format(report["brand_check"]))
print("release validator={}".format(report["quality_gate"]))
# Issue 186: the preflight names the layout check's browser. Where Playwright is absent the
# preflight reports it missing instead of ok; the other runtime parts still have to resolve.
browser = report["layout_browser"]
print("layout browser={}".format(browser.get("status")))
other_missing = [m for m in report["missing"] if not m.startswith("layout check browser")]
if other_missing:
    print("missing={}".format(", ".join(other_missing)))
    raise SystemExit(1)
if browser.get("status") == "ready":
    if not (browser["playwright"].get("version") and browser.get("chromiumVersion")):
        print("the layout browser is ready but names no version")
        raise SystemExit(1)
    if not report["ok"]:
        print("the browser is ready but the preflight reports not ok")
        raise SystemExit(1)
else:
    if report["ok"] or not any(m.startswith("layout check browser") for m in report["missing"]):
        print("no browser, but the preflight does not report it missing")
        raise SystemExit(1)
print("SELFTEST PASSED")
