#!/usr/bin/env python3
"""Compile the browser QA script without importing optional Playwright."""
from pathlib import Path

target = Path(__file__).with_name("qa_field_guide.py")
compile(target.read_text(encoding="utf-8"), str(target), "exec")
print("qa_field_guide.py compiles")
print("SELFTEST PASSED")
