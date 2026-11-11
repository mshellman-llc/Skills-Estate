#!/usr/bin/env python3
"""Selftest for prose-pass's scan engine and its generated wordlists.

scan.py arrived as a standalone skill. It was folded in here rather than shipped
alongside prose-pass, because two prose gates with two vocabularies is the drift
this repo exists to end. That fold is only safe while the vocabulary really has
one home, so the first and most important case is the drift check: regenerate
the lists from rewrite_scan.py and fail if the files on disk differ.

Then the engine itself, in both directions. A gate that only proves it can fail
is a gate nobody trusts to be quiet, so clean prose must score zero and exit 0.

Exit 0 when every case matches, 1 otherwise.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
SCAN = HERE / "scan.py"
WORDLISTS = SKILL / "wordlists"

fail: list[str] = []


def expect(label: str, got, want):
    ok = got == want
    print(f"  {label:54} got={str(got):<7} want={want}")
    if not ok:
        fail.append(f"{label}: got {got}, want {want}")
    return ok


def run(*args, stdin: str | None = None):
    p = subprocess.run([sys.executable, str(SCAN), *map(str, args)],
                       capture_output=True, text=True, input=stdin)
    return p.returncode, p.stdout + p.stderr


# --- 1. the vocabulary still has exactly one home ----------------------------
code = subprocess.run([sys.executable, str(HERE / "sync_wordlists.py"), "--check"],
                      capture_output=True, text=True)
expect("generated wordlists match rewrite_scan.py", code.returncode, 0)
if code.returncode != 0:
    fail.append(f"run sync_wordlists.py: {code.stdout.strip()}")

for name in ("vocabulary.txt", "flowery-phrases.txt"):
    text = (WORDLISTS / name).read_text(encoding="utf-8")
    expect(f"{name} is marked generated", text.startswith("# GENERATED"), True)
    terms = [l for l in text.splitlines() if l and not l.startswith("#")]
    expect(f"{name} is non-empty", len(terms) > 0, True)

# the weighted lists stay hand-maintained and must still parse
for name in ("marketing-verbs.txt", "soft-phrasing.txt"):
    lines = [l for l in (WORDLISTS / name).read_text(encoding="utf-8").splitlines()
             if l and not l.startswith("#")]
    bad = [l for l in lines if len(l.rsplit(" ", 1)) != 2 or not l.rsplit(" ", 1)[1]
           .replace(".", "", 1).isdigit()]
    expect(f"{name} weights all parse", bad, [])

# --- 2. the engine detects, and points at the right place --------------------
print()
SLOP = ("This is a robust solution. We leverage a tapestry of holistic "
        "capabilities in order to empower teams.\n")
CLEAN = ("The invoice service retries three times, then writes to the dead "
         "letter queue. Ops reads that queue every morning at 09:00.\n")

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    slop = tmp / "slop.md"
    slop.write_text(SLOP, encoding="utf-8")
    clean = tmp / "clean.md"
    clean.write_text(CLEAN, encoding="utf-8")

    code, out = run("audit", slop)
    expect("audit exits non-zero on slop", code != 0, True)
    expect("  and reports file:line:col", ":1:" in out, True)
    for term in ("robust", "leverage", "tapestry"):
        if term not in out:
            fail.append(f"audit missed house term {term!r}")
    print(f"  audit named the house terms it should")

    code, out = run("audit", clean)
    expect("audit exits 0 on clean prose", code, 0)

    # The derived vocabulary is really wired in: terms that exist only in
    # A phrase absent from the stub lists scan.py shipped with must be caught.
    # One sentence per phrase. The flowery detector reports a single phrase per
    # sentence, so two in one sentence would hide the second behind the first.
    only_in_house = tmp / "house.md"
    only_in_house.write_text("The paradigm drove synergy.\n\nIt is a testament to the team.\n",
                             encoding="utf-8")
    code, out = run("audit", only_in_house)
    expect("catches terms sourced from rewrite_scan", code != 0, True)
    expect("  including a generated word", "paradigm" in out.lower(), True)
    expect("  and a generated phrase", "testament to" in out.lower(), True)

    # --- 3. score is informational and machine-readable ----------------------
    code, out = run("score", slop, "--json")
    expect("score --json exits 0", code, 0)
    try:
        data = json.loads(out)
        expect("  and emits parsable json", isinstance(data, dict), True)
    except json.JSONDecodeError as e:
        fail.append(f"score --json did not parse: {e}")

    code, out = run("score", clean)
    expect("score exits 0 on clean prose too", code, 0)

    # score never gates, even on heavy slop
    code, _ = run("score", slop)
    expect("score never gates", code, 0)

    # --- 4. the single-input gate ---------------------------------------------
    code, out = run("--input", str(slop))
    expect("--input gates a single file", code != 0, True)
    expect("  and omits the path prefix", str(slop) not in out, True)

    code, _ = run("--input", str(clean))
    expect("--input passes clean prose", code, 0)

    # --- 5. wordlists are not scanned as prose --------------------------------
    code, out = run("audit", str(WORDLISTS))
    expect("audit skips its own wordlists", code, 0)

if fail:
    print("\nSELFTEST FAILED")
    for f in fail:
        print("  -", f)
    sys.exit(1)
print("\nSELFTEST PASSED")
