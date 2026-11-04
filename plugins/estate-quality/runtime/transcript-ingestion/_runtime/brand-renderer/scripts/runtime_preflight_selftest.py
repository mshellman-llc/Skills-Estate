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
if not report["ok"]:
    print("missing={}".format(", ".join(report["missing"])))
    raise SystemExit(1)
print("SELFTEST PASSED")
