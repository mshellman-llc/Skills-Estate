#!/usr/bin/env python3
"""Exercise every option, source disclosure, keyboard control and print view."""
import argparse
from pathlib import Path
from brand_runtime import resources
from browser_check import run_check

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('document',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    raise SystemExit(run_check(args.document,Path(__file__).with_suffix('.mjs'),args.output))
