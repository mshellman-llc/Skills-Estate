#!/usr/bin/env python3
"""Static contract test for the scope-reference skill. No network required."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent
text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
checks = {
    "frontmatter name matches folder": "name: scope-reference" in text,
    "live quote is source of truth": "Live quote is the only source of truth" in text,
    "requires 1:1 reconciliation": "Validate 1:1" in text,
    "routes through markdown contract": (
        "_shared/build-card.md" in text and
        (SKILLS / "_shared" / "build-card.md").exists() and
        "output-contract.md" in (SKILLS / "_shared" / "build-card.md").read_text()
    ),
}

failed = [name for name, passed in checks.items() if not passed]
for name, passed in checks.items():
    print(f"  {'PASS' if passed else 'FAIL'} {name}")
if failed:
    print("SELFTEST FAILED:", ", ".join(failed))
    sys.exit(1)
print("SELFTEST PASSED")
