#!/usr/bin/env python3
"""Selftest for playbook-builder. Stdlib only, no network.

verify_corpus.py already carries an internal `--selftest`. It was invisible to the
estate gate, which discovers tests by the `*_selftest.py` filename, so this file
runs it and then adds the cases that matter most for this skill: proving the
corpus guard actually catches an undeclared edit.

That guard is the whole point of the skill. The failure it prevents is a catalog
rewrite that silently re-transcribes plays nobody meant to touch, so the test
drives it from both sides: an undeclared change must fail, and a declared one
must pass, or the guard is either useless or unusable.

Exit 0 when every case matches, 1 otherwise.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
GUARD = HERE / "verify_corpus.py"


def _resolves(rel: str) -> bool:
    """True when a promised file exists, here or in a sibling skill.

    Skills cite files across the estate (a prose register, the shared build
    card). Those are real promises and must be checked, but they do not live
    under this skill, so a same-dir-only lookup reports them missing.
    """
    for cand in (SKILL / rel, SKILL / "scripts" / rel, SKILL / "references" / rel,
                 SKILL.parent / rel):
        if cand.exists():
            return True
    name = Path(rel).name
    return any(SKILL.parent.glob(f"*/**/{name}")) or any(SKILL.parent.glob(f"_shared/**/{name}"))


fail: list[str] = []


def expect(label: str, got, want):
    ok = got == want
    print(f"  {label:52} got={str(got):<7} want={want}")
    if not ok:
        fail.append(f"{label}: got {got}, want {want}")
    return ok


def run(*args):
    p = subprocess.run([sys.executable, str(GUARD), *map(str, args)],
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


CATALOG = """# Play catalog

Version 1.0

## 01 First Play

Scope: the first thing.

---

## 02 Second Play

Scope: the second thing.

---

## 03 Third Play

Scope: the third thing.
"""

# the script's own internal suite
code, out = run("--selftest")
expect("verify_corpus --selftest", code, 0)
m = re.search(r"(\d+) checks", out)
print(f"  internal suite ran {m.group(1) if m else '?'} checks")

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    src = tmp / "old.md"
    src.write_text(CATALOG, encoding="utf-8")

    def edited(text: str) -> Path:
        p = tmp / "new.md"
        p.write_text(text, encoding="utf-8")
        return p

    # identical corpora pass with nothing declared
    code, _ = run("--source", src, "--edited", edited(CATALOG))
    expect("untouched catalog passes", code, 0)

    # an undeclared edit to play 02 must fail. This is the regression that would
    # let a rewrite quietly reword plays nobody asked to change.
    sneaky = CATALOG.replace("Scope: the second thing.", "Scope: something else entirely.")
    code, out = run("--source", src, "--edited", edited(sneaky))
    expect("undeclared edit fails", code != 0, True)
    expect("and it names entry 02", "02" in out, True)

    # The entry key is the FULL heading text ("02 Second Play"), not the leading
    # number. The module docstring says "the token right after ##", which is
    # wrong, so pin the real contract here: a bare number must be rejected with a
    # warning rather than quietly matching nothing and passing.
    code, out = run("--source", src, "--edited", edited(sneaky), "--changed", "02")
    expect("a bare number does not declare an entry", code != 0, True)
    expect("and the script says the id is unknown",
           "does not exist" in out.lower(), True)

    code, _ = run("--source", src, "--edited", edited(sneaky), "--changed", "02 Second Play")
    expect("the same edit declared by heading passes", code, 0)

    # declaring the wrong entry does not launder the change
    code, _ = run("--source", src, "--edited", edited(sneaky), "--changed", "03 Third Play")
    expect("declaring the wrong entry still fails", code != 0, True)

    # a new play is an addition, and must be declared like any other change
    added = CATALOG + "\n---\n\n## 04 Fourth Play\n\nScope: new.\n"
    code, _ = run("--source", src, "--edited", edited(added))
    expect("undeclared addition fails", code != 0, True)
    code, _ = run("--source", src, "--edited", edited(added), "--changed", "04 Fourth Play")
    expect("declared addition passes", code, 0)

    # a dropped play is not silently tolerated
    dropped = CATALOG.split("---")[0] + "---" + CATALOG.split("---")[1]
    code, _ = run("--source", src, "--edited", edited(dropped))
    expect("undeclared removal fails", code != 0, True)

    # duplicate ids are a hard error: per-id comparison is meaningless with them
    dupe = CATALOG + "\n---\n\n## 02 Second Play Again\n\nScope: collision.\n"
    code, out = run("--source", src, "--edited", edited(dupe), "--changed", "02")
    expect("duplicate entry id is a hard error", code != 0, True)

    # a preamble edit is a declarable change like any other
    bumped = CATALOG.replace("Version 1.0", "Version 1.1")
    code, _ = run("--source", src, "--edited", edited(bumped))
    expect("undeclared preamble bump fails", code != 0, True)
    code, _ = run("--source", src, "--edited", edited(bumped), "--changed", "preamble")
    expect("declared preamble bump passes", code, 0)

# integrity: every file SKILL.md promises exists
print()
text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
promised = set(re.findall(r"`([A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:md|py|json))`", text))
INPUTS = {"catalog.json", "registry.json"}
missing = [r for r in sorted(promised)
           if r not in INPUTS and not r.startswith("_shared/")
           and not _resolves(r)]
print(f"  SKILL.md promises {len(promised)} files, missing: {missing or 'none'}")
if missing:
    fail.append(f"missing promised files: {missing}")

if fail:
    print("\nSELFTEST FAILED")
    for f in fail:
        print("  -", f)
    sys.exit(1)
print("\nSELFTEST PASSED")
