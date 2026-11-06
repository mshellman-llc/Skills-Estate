#!/usr/bin/env python3
"""Check field-guide interactions and save screenshots plus a failing/passing report.

Usage: python3 qa_field_guide.py built.html [output-directory]
Requires Node.js, Playwright, and Chromium. ESTATE_NODE, ESTATE_NODE_MODULES,
and PW_CHROMIUM can select existing installations. No downloads occur here.
"""
import argparse
from pathlib import Path
import brand_runtime  # resolves the bundled shared runtime
from browser_check import run_check

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('document', type=Path)
    parser.add_argument('output', nargs='?', type=Path)
    args = parser.parse_args()
    raise SystemExit(run_check(args.document, Path(__file__).with_name('qa_field_guide.mjs'), args.output))
