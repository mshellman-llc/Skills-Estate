#!/usr/bin/env python3
"""Selftest for render-offering-brief's render_playbook.py. Stdlib only, no network.

PATH TAKEN: test the deterministic pure-python parser (parse_entry) directly.
render_playbook.py imports weasyprint and jinja2 only INSIDE render_pdf(), so the
module imports cleanly with stdlib alone. parse_entry() turns one house-format
entry into the internal/external context dicts the templates consume; it is the
real, deterministic, dependency-free component and is what this test exercises.
No weasyprint render is attempted (the --help fallback is unnecessary here).

Builds a synthetic house-format entry, runs parse_entry(strict=True), and asserts
the returned internal/external dicts have the expected shape and content.

Prints observed vs expected; exits nonzero on mismatch.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import render_playbook as rp  # noqa: E402  (weasyprint/jinja2 are imported lazily inside render_pdf)

ENTRY = """## 01 Signal Review (free)

### Tldr
A fast read on where a client's data hurts most.

### Internal one-pager

**What is it**
A one-hour review of a client's signal data.

**Who is it for**
RevOps leaders at mid-market firms.

**Why should they care**
They stop guessing which pipeline gaps cost the most.

**Why should we care**
It opens the door to a paid scoping engagement.

**What's included**
- A ranked list of data gaps
- A recommended next step

**What's not included**
- No data remediation
- No system build

The paid Signal Build picks up where this stops.

**How do we deliver it**
One remote working session, run by a solutions architect.

### External one-pager

**What is it**
A focused review of your signal data.

**Who is it for**
RevOps leaders who need a clear next step.

**Why should you care**
You leave knowing your top three data gaps. We hand you a prioritized list.

**What's included**
- A ranked list of data gaps
- A recommended next step

**How do we deliver it**
One remote working session with your team.
"""

fail = []


def check(label, got, want):
    print(f"  {label:34} got={got!r:40.40} want={want!r}")
    if got != want:
        fail.append(f"{label}: got {got!r}, want {want!r}")


def check_true(label, got):
    print(f"  {label:34} got={got!r}")
    if not got:
        fail.append(f"{label}: got {got!r}, want truthy")


internal, external = rp.parse_entry(ENTRY, strict=True)

# --- internal shape ---
check("internal.title", internal["title"], "Signal Review")
check("internal.descriptor (tldr)", internal["descriptor"],
      "A fast read on where a client's data hurts most.")
check_true("internal.s1 (what_is_it)", internal["s1"].startswith("A one-hour review"))
check_true("internal.s7 (deliver)", "solutions architect" in internal["s7"])
check("internal.not_included is list", isinstance(internal["not_included"], list), True)
check("internal.not_included count", len(internal["not_included"]), 2)
check_true("internal.boundary carried", "Signal Build" in internal["boundary"])
check_true("internal.footer free tier", "front door" in internal["footer_line"])

# --- external shape ---
check("external.eyebrow", external["eyebrow"], "SIGNAL REVIEW")
check("external.title", external["title"], "Signal Review")
check("external.subtitle (1st sentence)", external["subtitle"],
      "You leave knowing your top three data gaps.")
check("external.what_you_get is list", isinstance(external["what_you_get"], list), True)
check("external.what_you_get count", len(external["what_you_get"]), 2)
check_true("external.how (deliver)", "remote working session" in external["how"])
check("external.columns count", len(external["columns"]), 2)

if fail:
    print("\nSELFTEST FAILED")
    for f in fail:
        print("  -", f)
    sys.exit(1)
print("\nSELFTEST PASSED")
