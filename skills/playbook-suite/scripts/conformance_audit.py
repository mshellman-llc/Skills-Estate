#!/usr/bin/env python3
"""Audit an existing playbook folder against Aleysian playbook spec 1.1.

    python3 conformance_audit.py PLAYBOOK_DIR [--manifest manifest.json] [--infer] [--json]

Reports what is present, missing, off-format, ungated, and obsolete. It resolves
artifacts through the manifest (STRUCTURE.md: filenames are cosmetic, the machine
binds by drive_file_id), checks the required set per the shape's row in SPEC.md, and
reads the filesystem only to catch obsolete or stale-role filenames and manifest
pointers that miss disk. It never opens a document, so contents conformance stays
with the visual gate and a person.

Exit 0 when the playbook conforms. Exit 1 when it does not. Exit 2 on a usage error.
"""

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spec_shapes

SPEC_VERSION = spec_shapes.SPEC_VERSION
ARTIFACTS = spec_shapes.ARTIFACTS

# Filename fragments that indicate an artifact the spec no longer contains.
OBSOLETE_PATTERNS = [
    (r"pricing[-_ ]?sheet", "Pricing Sheet is obsolete; pricing is the quote in the Pricing System"),
    (r"deal[-_ ]?desk", "Deal Desk document is obsolete; Deal Desk reviews the quote, SOW, and DDOC"),
    (r"discussion[-_ ]?document", "Discussion Document is the superseded name; DDOC is the Deal Decision deck"),
    (r"\bstate\b.*\.md$", "STATE file is retired; the README carries stage, file map, and logs"),
    (r"PB-[A-Z0-9]+-\d{2}", "PB-XX-NN filename is the retired convention; use 'NN Short Name - Artifact' and the code in the manifest"),
]

# Filename fragments that hint at a stale role name.
ROLE_PATTERNS = [(r"accountable[-_ ]?executive", "Accountable Executive was renamed Client Services Executive (CSE)")]

# Approach B filename: "NN Short Name - Artifact[ - Band].ext". The number and
# extension are the load-bearing parts; the rest is human-readable and free.
NAME_RE = re.compile(r"^(\d{2}) .+ - .+\.[a-z0-9]+$")

GATES = ("parity", "visual", "prose")
OK_GATE = ("pass", "dispositioned")
# Manifest artifact status enum (manifest.schema.json). "present" is the only
# conforming state; draft/needs-fix are built-but-not-final; retired is ignored.
STATUS_CONFORMING = "present"
STATUS_UNFINISHED = ("draft", "needs-fix")


def scan(dirpath):
    """Files under the folder, skipping dotfiles and _-prefixed system dirs."""
    files = []
    for root, dirs, names in os.walk(dirpath):
        dirs[:] = [x for x in dirs if not x.startswith("_") and not x.startswith(".")]
        for n in names:
            if n.startswith("."):
                continue
            files.append(os.path.relpath(os.path.join(root, n), dirpath))
    return sorted(files)


def infer_manifest(name, files):
    """Best-effort draft manifest from approach-B filenames. The number leads each
    filename; slug comes from the spec table. Cosmetic filename only; correct by hand."""
    arts = []
    options = []
    for f in files:
        base = os.path.basename(f)
        m = re.match(r"^(\d{2}) ", base)
        if not m:
            continue
        num = int(m.group(1))
        slug = ARTIFACTS.get(num, ("unknown",))[0]
        arts.append({"number": num, "slug": slug, "option": None, "filename": base,
                     "drive_file_id": None, "status": "draft",
                     "gates": {g: "not_run" for g in GATES}})
    return {"code": "C00", "name": name, "short_name": name, "shape": "Assess",
            "stage": 1, "owner": "UNKNOWN", "spec_version": SPEC_VERSION,
            "drive_folder_id": "UNKNOWN", "band_spread": None,
            "options": [], "artifacts": arts}


def rom_required(manifest):
    """ROM (06) is built only when the band spread exceeds 2x (SPEC.md). Absent a
    band_spread it is treated as not required, so a single-band playbook never flags it."""
    spread = manifest.get("band_spread")
    return bool(spread) and spread > 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("playbook_dir")
    ap.add_argument("--manifest", default="manifest.json")
    ap.add_argument("--infer", action="store_true",
                    help="draft a manifest from approach-B filenames when none exists")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    d = args.playbook_dir
    if not os.path.isdir(d):
        print(f"not a directory: {d}")
        return 2

    files = scan(d)
    mpath = args.manifest if os.path.isabs(args.manifest) else os.path.join(d, args.manifest)

    inferred = False
    if os.path.exists(mpath):
        with open(mpath) as fh:
            manifest = json.load(fh)
    elif args.infer:
        manifest = infer_manifest(os.path.basename(os.path.abspath(d)), files)
        inferred = True
    else:
        print(f"no manifest at {mpath}. Re-run with --infer to draft one from filenames.")
        return 2

    shape = manifest.get("shape")
    options = [o.get("name") for o in manifest.get("options", [])]
    rom = rom_required(manifest)
    present = {(a.get("number"), a.get("option")): a for a in manifest.get("artifacts", [])}

    findings = {"missing": [], "misnamed": [], "wrong_format": [], "ungated": [],
                "obsolete": [], "role_language": [], "notes": []}

    if manifest.get("spec_version") != SPEC_VERSION:
        findings["notes"].append(
            f"manifest declares spec_version {manifest.get('spec_version')!r}; auditor is {SPEC_VERSION}")
    if shape not in spec_shapes.SHAPES:
        findings["notes"].append(f"manifest shape {shape!r} is not a canon shape; auditing against the paid suite")
    if inferred:
        findings["notes"].append("manifest was inferred from filenames; correct it by hand before relying on it")

    # Required set per the shape's SPEC.md row. R is required; C is required only
    # when its trigger fires (ROM at band spread > 2); everything else is skipped.
    for num, (slug, fmt, scope) in ARTIFACTS.items():
        req = spec_shapes.requirement(shape, num)
        if req == "C":
            if num == 6 and not rom:
                continue
            if num != 6:
                # Conditional deal-layer artifacts (Front Door 07/09/10): audit if
                # present, never flag as missing.
                pass
        if req is None:
            continue
        targets = options if (scope == "option" and options) else [None]
        for opt in targets:
            entry = present.get((num, opt))
            label = f"{num:02d} {slug}" + (f" [{opt}]" if opt else "")
            status = (entry or {}).get("status")
            if not entry or status == "retired":
                if req == "R":
                    findings["missing"].append(label)
                continue
            if status in STATUS_UNFINISHED:
                findings["notes"].append(f"{label}: status {status!r}, built but not final")
            base = os.path.basename(entry.get("filename") or "")
            if entry.get("filename") and not os.path.exists(os.path.join(d, entry["filename"])) and not entry.get("drive_file_id"):
                findings["notes"].append(f"{label}: manifest points at a file not on disk and has no drive_file_id ({base})")
            if base and not NAME_RE.match(base):
                findings["misnamed"].append(f"{label}: {base} does not match 'NN Short Name - Artifact[ - Band].ext'")
            if base and not base.lower().endswith("." + fmt):
                findings["wrong_format"].append(f"{label}: expected .{fmt}, found {base}")
            gates = entry.get("gates") or {}
            bad = [g for g in GATES if gates.get(g, "not_run") not in OK_GATE]
            if status == STATUS_CONFORMING and bad:
                findings["ungated"].append(f"{label}: {', '.join(bad)}")

    # obsolete and stale-role filenames on disk
    for f in files:
        low = f.lower()
        for pat, msg in OBSOLETE_PATTERNS:
            if re.search(pat, low):
                findings["obsolete"].append(f"{f}: {msg}")
        for pat, msg in ROLE_PATTERNS:
            if re.search(pat, low):
                findings["role_language"].append(f"{f}: {msg}")

    # unreferenced numbered files on disk
    referenced = {os.path.basename(a.get("filename")) for a in manifest.get("artifacts", []) if a.get("filename")}
    for f in files:
        base = os.path.basename(f)
        if base == os.path.basename(mpath):
            continue
        if base not in referenced and NAME_RE.match(base):
            findings["notes"].append(f"{f} is on disk but not referenced in the manifest")

    total = sum(len(v) for k, v in findings.items() if k != "notes")
    result = {"playbook": manifest.get("code"), "shape": shape, "spec_version": SPEC_VERSION,
              "files_scanned": len(files), "blocking_findings": total, "findings": findings}

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n  CONFORMANCE  {result['playbook']}  {shape}  spec {SPEC_VERSION}  "
              f"{len(files)} files scanned\n")
        order = ["missing", "misnamed", "wrong_format", "ungated", "obsolete", "role_language", "notes"]
        for k in order:
            for item in findings[k]:
                tag = "note" if k == "notes" else k.upper()
                print(f"    {tag:<14} {item}")
        n_notes = len(findings["notes"])
        print(f"\n  {total} blocking finding{'' if total == 1 else 's'}, "
              f"{n_notes} note{'' if n_notes == 1 else 's'}")
        print("  Contents conformance is the visual gate and is not checked here.\n")

    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
