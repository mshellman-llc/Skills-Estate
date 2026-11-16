#!/usr/bin/env python3
"""Selftest for layout_check.cjs. Stdlib only, no network.

The visual gate reads layout from the DOM and writes no image files. The static
half asserts that the checker never calls a screenshot API or writes a raster
file. Where Node and Playwright are available (ESTATE_NODE_MODULES or NODE_PATH
naming a node_modules that holds playwright), it renders two synthetic pages at
1280px and 390px: a clean one must pass, and one with sideways scroll, clipped
text, low contrast and a hidden qualifier must fail on each. Without a browser
runtime the live half reports SKIP and the static half still runs.

Prints observed versus expected; exits nonzero on a mismatch.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHECK = HERE / "layout_check.cjs"
fail: list[str] = []


def expect(label, got, want):
    print(f"  {label:44} got={str(got)[:60]:<20} want={want}")
    if got != want:
        fail.append(f"{label}: got {got!r}, want {want!r}")


source = CHECK.read_text(encoding="utf-8")
expect("no screenshot call", bool(re.search(r"\.screenshot\s*\(", source)), False)
expect("no raster file named", bool(re.search(r"\.(png|jpe?g|webp|gif)\b", source, re.I)), False)
expect("uses the launch policy", "launchOptions()" in source, True)

GOOD = """<!doctype html><html><head><meta name="viewport" content="width=device-width">
<style>body{margin:0;font:16px/1.5 sans-serif;color:#1a1a1a;background:#fff}
main{max-width:720px;margin:0 auto;padding:16px}</style></head>
<body><main><h1>Quarterly scope</h1><p>Phase one covers ordering, estimated at 12 weeks.</p></main></body></html>"""

BAD = """<!doctype html><html><head><meta name="viewport" content="width=device-width">
<style>body{margin:0;font:16px/1.5 sans-serif;color:#1a1a1a;background:#fff}
.wide{width:900px}.clip{width:80px;white-space:nowrap;overflow:hidden}
.faint{color:#d0d0d0}.gone{display:none}</style></head>
<body><main><h1>Quarterly scope</h1><p class="wide">This row is wider than a phone.</p>
<p class="clip">A label that cannot fit its box</p><p class="faint">Low contrast note</p>
<p>Estimated at 12 weeks<span class="gone"> if the data export arrives</span>.</p></main></body></html>"""


def playwright_entry() -> Path | None:
    roots = [Path(x) for x in (os.environ.get("ESTATE_NODE_MODULES", "") + os.pathsep +
                               os.environ.get("NODE_PATH", "")).split(os.pathsep) if x]
    roots += [parent / "node_modules" for parent in [HERE, *HERE.parents]]
    for root in roots:
        for name in ("index.mjs", "index.js"):
            if (root / "playwright" / name).is_file():
                return root / "playwright" / name
    return None


node = os.environ.get("ESTATE_NODE") or shutil.which("node")
entry = playwright_entry()
if not node or entry is None:
    print("  SKIP live layout check: Node or Playwright is not available")
else:
    with tempfile.TemporaryDirectory(prefix="layout-check-") as temp:
        folder = Path(temp)
        (folder / "good.html").write_text(GOOD, encoding="utf-8")
        (folder / "bad.html").write_text(BAD, encoding="utf-8")
        (folder / "manifest.json").write_text(json.dumps({
            "manifestVersion": "1", "requiredPhrases": ["Quarterly scope"],
            "protectedClaims": [{"id": "C1", "text": "Estimated at 12 weeks",
                                 "requiredQualifiers": ["if the data export arrives"]}]}))
        env = {**os.environ, "PW_MODULE": entry.resolve().as_uri()}

        def run(name):
            result = subprocess.run([node, str(CHECK), str(folder / name), "--manifest",
                                     str(folder / "manifest.json")],
                                    capture_output=True, text=True, timeout=120, env=env)
            try:
                return result.returncode, json.loads(result.stdout)
            except ValueError:
                return result.returncode, {"failures": [result.stdout + result.stderr]}

        code, report = run("good.html")
        if code == 2:
            print("  SKIP live layout check: " + str(report.get("reason", "browser unavailable")))
        else:
            # The clean page states no qualifier, so only its manifest finding is expected.
            expect("clean page has no layout failure",
                   [f for f in report.get("failures", []) if "qualifier" not in f], [])
            code, report = run("bad.html")
            text = "\n".join(report.get("failures", []))
            expect("defective page fails", code, 1)
            expect("flags sideways scroll at 390px", "390px: page scrolls sideways" in text, True)
            expect("flags clipped text", "clipped text" in text, True)
            expect("flags low contrast", "contrast below the floor" in text, True)
            expect("flags a hidden qualifier", "qualifier for C1 not visible" in text, True)
            images = [p.name for p in folder.rglob("*") if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif"}]
            expect("writes no image files", images, [])

if fail:
    print("\nSELFTEST FAILED")
    for item in fail:
        print("  -", item)
    sys.exit(1)
print("\nSELFTEST PASSED")
