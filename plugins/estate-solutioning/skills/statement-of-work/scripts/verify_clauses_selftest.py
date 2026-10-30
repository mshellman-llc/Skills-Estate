#!/usr/bin/env python3
"""Selftest for sow. Stdlib only, no network, no node.

Two halves.

BEHAVIOUR. Builds synthetic .docx files (a zip carrying word/document.xml, which
is all verify_clauses.py reads) from the real required-clauses.md, then runs the
real gate as a subprocess and asserts:

  1. A SOW carrying every fixed-fee anchor PASSES.
  2. Dropping one anchor FAILS, and the gate names the clause it dropped.
  3. Dropping a load-bearing clause (12 or 15) triggers the HARD STOP branch.
  4. The T&M and Assess variants select a different required set, so the gate is
     really branching on model and not checking one fixed list.
  5. Anchor matching survives smart quotes and an em dash, which is what a real
     Word document contains. This is the regression that would let a correct SOW
     fail the gate, or a broken one pass.

A gate that only proves it can fail is a gate nobody trusts to be quiet, so every
case is exercised in both directions.

INTEGRITY. Asserts every file this skill's SKILL.md promises actually exists.

Exit 0 when every case matches, 1 otherwise.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
GATE = HERE / "verify_clauses.py"
CLAUSES = SKILL / "references" / "required-clauses.md"

fail: list[str] = []


def parse_rows(md: Path):
    """Mirror verify_clauses.parse_clauses, independently, so a bug in the real
    parser cannot hide behind the same bug in the test."""
    rows = []
    for line in md.read_text(encoding="utf-8").splitlines():
        if not re.match(r"^\|\s*(\d+)\s*\|", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        anchors = re.findall(r'"([^"]+)"', cells[2])
        if not anchors:
            continue
        rows.append({
            "num": cells[0], "name": cells[1], "anchors": anchors,
            "fixed": "✓" in cells[3], "tm": "✓" in cells[4],
            "assess": "✓" in (cells[5] if len(cells) > 5 else ""),
        })
    return rows


def make_docx(path: Path, body: str) -> Path:
    """Minimal .docx: verify_clauses reads word/document.xml and strips tags."""
    xml = ('<?xml version="1.0"?><w:document '
           'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
           "<w:body>"
           + "".join(f"<w:p><w:r><w:t>{line}</w:t></w:r></w:p>" for line in body.split("\n"))
           + "</w:body></w:document>")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types/>')
        z.writestr("word/document.xml", xml)
    return path


def body_for(rows, model: str, drop: str | None = None, marker: str | None = None) -> str:
    lines = [marker or {"fixed": "This is a fixed fee engagement.",
                        "tm": "Billed on a Time and Materials basis.",
                        "assess": "This is an assessment engagement."}[model]]
    for r in rows:
        if not r[model] or r["num"] == drop:
            continue
        lines.extend(r["anchors"])
    return "\n".join(lines)


def run(docx: Path, model: str | None = None):
    cmd = [sys.executable, str(GATE), str(docx)]
    if model:
        cmd += ["--model", model]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def expect(label: str, got, want):
    ok = got == want
    print(f"  {label:52} got={str(got):<7} want={want}")
    if not ok:
        fail.append(f"{label}: got {got}, want {want}")
    return ok


rows = parse_rows(CLAUSES)
if not rows:
    print(f"  could not parse any clause rows from {CLAUSES}")
    sys.exit(1)
print(f"  parsed {len(rows)} clause rows from required-clauses.md\n")

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)

    # 1. complete fixed-fee SOW passes
    code, out = run(make_docx(tmp / "full.docx", body_for(rows, "fixed")), "fixed")
    expect("complete fixed-fee SOW", code, 0)

    # 2. dropping a non-load-bearing clause fails, and names it
    droppable = [r for r in rows if r["fixed"] and r["num"] not in ("12", "15")]
    victim = droppable[0]
    code, out = run(make_docx(tmp / "gap.docx", body_for(rows, "fixed", drop=victim["num"])), "fixed")
    expect(f"missing clause #{victim['num']} fails", code, 1)
    named = victim["anchors"][0][:30].lower() in out.lower() or victim["name"].lower() in out.lower()
    expect(f"gate names the missing clause", named, True)

    # 3. a load-bearing clause triggers the HARD STOP branch
    load_bearing = [r for r in rows if r["fixed"] and r["num"] in ("12", "15")]
    if load_bearing:
        lb = load_bearing[0]
        code, out = run(make_docx(tmp / "hard.docx", body_for(rows, "fixed", drop=lb["num"])), "fixed")
        expect(f"missing load-bearing #{lb['num']} exits 1", code, 1)
        expect("HARD STOP branch fires", "HARD STOP" in out, True)
    else:
        print("  note: no load-bearing rows (12/15) in the table; HARD STOP not exercised")

    # 4. the model really selects a different required set
    for model in ("tm", "assess"):
        n_req = sum(1 for r in rows if r[model])
        if not n_req:
            continue
        code, out = run(make_docx(tmp / f"{model}.docx", body_for(rows, model)), model)
        expect(f"complete {model.upper()} SOW", code, 0)
        m = re.search(r"(\d+)/(\d+) required clauses present", out)
        expect(f"{model.upper()} checks its own set ({n_req})", int(m.group(2)) if m else -1, n_req)

    # a fixed-fee doc must NOT satisfy a required set it lacks clauses for
    tm_only = [r for r in rows if r["tm"] and not r["fixed"]]
    if tm_only:
        code, _ = run(make_docx(tmp / "wrong.docx", body_for(rows, "fixed")), "tm")
        expect("fixed-fee body judged as T&M fails", code, 1)

    # 5. real Word punctuation must not break anchor matching
    fancy = (body_for(rows, "fixed")
             .replace("'", "’").replace('"', "“").replace(" - ", " — "))
    code, out = run(make_docx(tmp / "fancy.docx", fancy), "fixed")
    expect("smart quotes and em dash still match", code, 0)

    # model auto-detection, with no --model flag
    code, out = run(make_docx(tmp / "auto.docx", body_for(rows, "fixed")))
    expect("auto-detects fixed from the body", code, 0)
    expect("auto-detect reports FIXED", "model: FIXED" in out, True)

    # Auto-detection is load-bearing on two clause anchors that carry the pricing
    # signal in their own text ("you will pay us a fixed fee of", "provided on a
    # Time and Materials basis"). A complete SOW is therefore self-describing.
    # Assert that, then assert the refusal path on a doc carrying no signal at all.
    signals = {"fixed": "fixed fee", "tm": "time and materials basis"}
    for model, sig in signals.items():
        carriers = [r["num"] for r in rows if r[model]
                    and any(sig in a.lower() for a in r["anchors"])]
        expect(f"{model} signal carried by a required anchor", bool(carriers), True)

    quiet = "\n".join(rows[0]["anchors"])  # clause 1, no pricing language
    code, out = run(make_docx(tmp / "nomodel.docx", quiet))
    expect("undetectable variant is refused", code != 0, True)
    expect("refusal explains itself", "could not detect variant" in out.lower(), True)

# INTEGRITY: every file SKILL.md promises exists
print()
text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
promised = set(re.findall(r"`([A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:md|py|js|json|docx|png))`", text))
missing = []
for rel in sorted(promised):
    if rel.startswith("_shared/"):
        continue  # estate_diff resolves those against the skills root
    # A cross-skill citation (a prose register, the build card) is still a real
    # promise, it just does not live under this skill.
    here = [SKILL / c for c in (rel, f"scripts/{rel}", f"references/{rel}", f"assets/{rel}")]
    elsewhere = list(SKILL.parent.glob(f"*/**/{Path(rel).name}"))
    if not any(c.exists() for c in here) and not elsewhere:
        missing.append(rel)
print(f"  SKILL.md promises {len(promised)} files, missing: {missing or 'none'}")
if missing:
    fail.append(f"missing promised files: {missing}")

if fail:
    print("\nSELFTEST FAILED")
    for f in fail:
        print("  -", f)
    sys.exit(1)
print("\nSELFTEST PASSED")
