#!/usr/bin/env python3
"""Check the explicit source-review receipt before a role resume is called ready."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import json
import hashlib
import subprocess
import shutil
import os
import xml.etree.ElementTree as ET
from zipfile import BadZipFile, ZipFile


FIELDS = (
    "Base master",
    "Prior variants reviewed",
    "Retain",
    "Revise",
    "Exclude",
    "Claim authority checked",
    "Tailored resume",
    "Finished copy check",
    "Content review",
)
FILE_FIELDS = ("Base master", "Claim authority checked", "Tailored resume")
PLACEHOLDERS = {"", "tbd", "todo", "pending", "n/a", "-"}


def section_for(text: str) -> str:
    match = re.search(r"^## Resume source review\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not match:
        raise ValueError("missing 'Resume source review' section")
    return match.group(1)


def field(section: str, label: str) -> str:
    match = re.search(rf"^- {re.escape(label)}:[ \t]*(.*?)[ \t]*$", section, re.M)
    if not match or match.group(1).strip().lower() in PLACEHOLDERS:
        raise ValueError(f"missing review field: {label}")
    return match.group(1).strip()


def paths_in(value: str) -> list[Path]:
    return [Path(name) for name in re.findall(r"`([^`]+)`", value)]


def check(record: Path) -> None:
    if not record.is_file():
        raise ValueError(f"role record missing: {record}")
    section = section_for(record.read_text(encoding="utf-8"))
    values = {label: field(section, label) for label in FIELDS}
    for label in FILE_FIELDS:
        paths = paths_in(values[label])
        if not paths:
            raise ValueError(f"{label} needs an absolute, backticked file path")
        for path in paths:
            if not path.is_absolute() or not path.is_file():
                raise ValueError(f"{label} path is not a readable file: {path}")
    prior = values["Prior variants reviewed"]
    if "none found after inventory" not in prior.lower():
        paths = paths_in(prior)
        if not paths:
            raise ValueError("Prior variants reviewed needs file paths or 'none found after inventory'")
        for path in paths:
            if not path.is_absolute() or not path.is_file():
                raise ValueError(f"prior variant is not a readable file: {path}")
    resume_paths = paths_in(values["Tailored resume"])
    if len(resume_paths) != 1 or resume_paths[0].suffix.lower() != ".docx":
        raise ValueError("Tailored resume must name one DOCX file")
    try:
        with ZipFile(resume_paths[0]) as archive:
            if "word/document.xml" not in archive.namelist() or archive.testzip():
                raise ValueError("tailored DOCX is missing its document or has corrupt members")
            document = ET.fromstring(archive.read("word/document.xml"))
            ns={"w":"http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            body="\n".join("".join(t.text or "" for t in p.findall(".//w:t",ns)) for p in document.findall(".//w:p",ns))
            if not body.strip(): raise ValueError("tailored resume contains no readable document text")
    except (BadZipFile, ET.ParseError) as exc:
        raise ValueError("tailored resume is not a valid DOCX archive") from exc

    reviews=paths_in(values["Content review"])
    if len(reviews)!=1 or not reviews[0].is_absolute() or not reviews[0].is_file():raise ValueError("Content review requires one readable absolute JSON receipt")
    receipt=json.loads(reviews[0].read_text())
    if receipt.get("brief",{}).get("purpose") != "resume" or receipt.get("brief",{}).get("audience") != "hiring":
        raise ValueError("resume readiness requires a hiring resume brief; a handout is a different deliverable")
    if receipt.get("review",{}).get("checks",{}).get("layout",{}).get("result") != "pass":
        raise ValueError("DOCX readiness requires a completed layout review")
    if receipt.get("artifact_sha256") != hashlib.sha256(resume_paths[0].read_bytes()).hexdigest():
        raise ValueError("review does not match the exact DOCX file; recheck content and layout")
    sources={}
    reviewed_paths=set()
    for ref in receipt.get("source_files",[]):
        p=Path(ref["path"])
        if not p.is_absolute() or not p.is_file():raise ValueError("review source must be a readable absolute file")
        current=hashlib.sha256(p.read_bytes()).hexdigest()
        if current!=ref["sha256"]:raise ValueError("review source changed; reread it")
        if ref["id"] in sources:raise ValueError("duplicate source file ID")
        sources[ref["id"]]={"revision":ref["revision"],"hash":current}
        reviewed_paths.add(p.resolve())
    required_paths={p.resolve() for label in ("Base master", "Claim authority checked", "Prior variants reviewed") for p in paths_in(values[label])}
    review_ids={s["id"] for s in receipt.get("review",{}).get("sources",[])}
    if not required_paths.issubset(reviewed_paths) or not set(sources).issubset(review_ids):
        raise ValueError("review foundation must include the master, claim authority, and reviewed prior variants")
    node = os.environ.get("CAREER_REVIEW_NODE") or shutil.which("node")
    if node and (not Path(node).is_absolute() or not Path(node).is_file()):
        raise ValueError("CAREER_REVIEW_NODE must identify an available absolute executable path")
    if not node:raise ValueError("Node 24+ is required for the shared content gate; review is not verified")
    result=subprocess.run([node,str(Path(__file__).with_name("content-review-cli.ts"))],input=json.dumps({"body":body,"brief":receipt.get("brief"),"review":receipt.get("review"),"sources":sources}),text=True,capture_output=True)
    if result.returncode:raise ValueError(result.stderr.strip() or "content review failed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=Path, help="Path to a role's Role_Work_Record.md")
    args = parser.parse_args()
    try:
        check(args.record)
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as exc:
        print(f"FAIL: {exc}")
        return 1
    print("PASS: source and content hashes, readable draft, audience-specific coverage, and separate review attestations checked")
    print("Content truth, editorial quality, and visual layout still require direct review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
