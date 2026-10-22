#!/usr/bin/env python3
"""
verify_clauses.py — clause-presence gate for Service Provider SOWs.

Asserts that a rendered SOW .docx contains every required contract-class clause,
branching on pricing model (fixed-fee vs T&M). The required clauses and their
anchor phrases are read from references/required-clauses.md so the script and the
template share ONE source of truth. Exits non-zero and prints the missing clauses
if any required anchor is absent.

This is a blocking pre-flight gate, the same pattern as sow-quality's
slop_scan.py. A generated SOW does not pass until this script passes.

Usage:
    python verify_clauses.py SOW.docx
    python verify_clauses.py SOW.docx --model tm
    python verify_clauses.py SOW.docx --clauses ../references/required-clauses.md

Dependency-free: reads the .docx as a zip and extracts text from the document XML,
so it sees body text AND table cells (signature block, deliverables table,
remittance block all live in tables).
"""

import argparse
import os
import re
import sys
import zipfile

# --- text extraction -------------------------------------------------------

def docx_text(path):
    """Return all visible text from a .docx (body + tables + headers/footers)."""
    chunks = []
    with zipfile.ZipFile(path) as z:
        parts = [n for n in z.namelist()
                 if re.match(r"word/(document|header\d*|footer\d*)\.xml$", n)]
        for name in parts:
            xml = z.read(name).decode("utf-8", errors="ignore")
            # paragraph and tab boundaries -> spaces so runs don't fuse
            xml = re.sub(r"</w:p>", " \n ", xml)
            xml = re.sub(r"<w:tab[^>]*/>", " ", xml)
            xml = re.sub(r"<[^>]+>", "", xml)        # strip all tags
            chunks.append(xml)
    return "\n".join(chunks)


def normalize(s):
    """Lowercase, straighten smart quotes, collapse whitespace."""
    s = (s.replace("’", "'").replace("‘", "'")
           .replace("“", '"').replace("”", '"')
           .replace("–", "-").replace("—", "-")
           .replace(" ", " "))
    s = re.sub(r"\s+", " ", s)
    return s.lower().strip()


# --- clause spec parsing ---------------------------------------------------

def parse_clauses(md_path):
    """
    Parse the clause-presence gate table from required-clauses.md.
    Returns list of dicts: {num, name, anchors:[...], fixed:bool, tm:bool}.
    Each row may carry multiple quoted anchor phrases; ALL must be present.
    """
    rows = []
    row_re = re.compile(r"^\|\s*(\d+)\s*\|")
    with open(md_path, encoding="utf-8") as f:
        for line in f:
            if not row_re.match(line):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 5:
                continue
            num, name, anchor_cell, fixed_cell, tm_cell = cells[:5]
            assess_cell = cells[5] if len(cells) > 5 else ""  # Assess column (optional 6th)
            anchors = re.findall(r'"([^"]+)"', anchor_cell)
            if not anchors:
                continue
            rows.append({
                "num": num,
                "name": name,
                "anchors": anchors,
                "fixed": "✓" in fixed_cell,   # check mark
                "tm": "✓" in tm_cell,
                "assess": "✓" in assess_cell,
            })
    if not rows:
        sys.exit(f"ERROR: no clause table rows found in {md_path}")
    return rows


# --- model detection -------------------------------------------------------

def detect_model(text_norm):
    # Assess is fixed-fee too, so check the assessment signal first.
    if "assessment engagement" in text_norm:
        return "assess"
    if "time and materials basis" in text_norm:
        return "tm"
    if "fixed fee" in text_norm:
        return "fixed"
    return None


# --- main ------------------------------------------------------------------

def _default_clauses():
    """Find required-clauses.md relative to this script, whatever the CWD.
    Handles both the repo layout (scripts/ + references/) and the flat
    layout FetchSkillScripts produces."""
    here = os.path.dirname(os.path.abspath(__file__))
    for rel in (os.path.join(here, os.pardir, 'references', 'required-clauses.md'),
                os.path.join(here, 'references', 'required-clauses.md'),
                os.path.join(here, 'required-clauses.md'),
                'references/required-clauses.md'):
        if os.path.exists(rel):
            return os.path.abspath(rel)
    return 'references/required-clauses.md'


def main():
    ap = argparse.ArgumentParser(description="Service Provider SOW clause-presence gate.")
    ap.add_argument("docx", help="path to the generated SOW .docx")
    ap.add_argument("--clauses", default=None,
                    help="path to required-clauses.md (default: references/required-clauses.md)")
    ap.add_argument("--model", choices=["fixed", "tm", "assess"], default=None,
                    help="pricing model / variant; auto-detected if omitted")
    args = ap.parse_args()
    if args.clauses is None:
        args.clauses = _default_clauses()

    raw = docx_text(args.docx)
    text = normalize(raw)
    clauses = parse_clauses(args.clauses)

    model = args.model or detect_model(text)
    if model is None:
        sys.exit("ERROR: could not detect variant (no 'assessment engagement', 'Time and "
                 "Materials basis' or 'fixed fee' found). Re-run with --model fixed|tm|assess.")

    required_flag = model  # 'fixed' | 'tm' | 'assess' — matches the clause-row dict keys
    missing, checked = [], 0
    print(f"Clause-presence gate  |  model: {model.upper()}  |  source: {args.docx}\n")

    for c in clauses:
        if not c[required_flag]:
            continue  # not required for this pricing model
        checked += 1
        absent = [a for a in c["anchors"] if normalize(a) not in text]
        status = "PASS" if not absent else "FAIL"
        print(f"  [{status}] {c['num']:>2}. {c['name']}")
        if absent:
            for a in absent:
                print(f"           missing anchor: \"{a}\"")
            missing.append(c)

    print(f"\n{checked - len(missing)}/{checked} required clauses present.")
    if missing:
        load_bearing = {"12", "15"}
        hard = [c for c in missing if c["num"] in load_bearing]
        print(f"FAIL: {len(missing)} required clause(s) missing.")
        if hard:
            print("HARD STOP — load-bearing protective clause missing: "
                  + ", ".join(f"#{c['num']} {c['name']}" for c in hard))
        sys.exit(1)
    print("PASS: all required clauses present.")
    sys.exit(0)


if __name__ == "__main__":
    main()
