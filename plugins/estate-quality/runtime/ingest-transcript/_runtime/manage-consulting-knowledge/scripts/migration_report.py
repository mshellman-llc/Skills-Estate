#!/usr/bin/env python3
"""Audit legacy local Hub folders without changing them."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import hub_runtime  # noqa: E402




def stable_slug(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def audit(root, bucket_scopes=None):
    # Folder names are workspace configuration, never evidence of lifecycle authority.
    bucket_scopes = {} if bucket_scopes is None else bucket_scopes
    if not isinstance(bucket_scopes, dict) or any(
        not isinstance(key, str) or not key or '/' in key or '\\' in key
        or not isinstance(value, str) or value not in {"opportunity", "engagement", "unclassified"}
        for key, value in bucket_scopes.items()
    ):
        raise ValueError("bucket scopes must map folder names to opportunity, engagement or unclassified")
    root = pathlib.Path(root).expanduser().resolve()
    hubs = []
    for hub in sorted(root.glob("*/*/knowledge-hub")):
        if not hub.is_dir():
            continue
        rows = []
        for path in sorted(
            item for item in hub.iterdir()
            if item.is_file() and not item.name.startswith(".")
        ):
            matches = hub_runtime.legacy_matches(path.name)
            status = "mapped" if len(matches) == 1 else (
                "ambiguous" if len(matches) > 1 else "unmapped")
            rows.append({
                "file": path.name,
                "status": status,
                "candidateRecords": matches,
            })
        bucket = hub.parent.parent.name
        client_slug = stable_slug(hub.parent.name)
        scope = bucket_scopes.get(bucket, "unclassified")
        hubs.append({
            "bucket": bucket,
            "clientFolder": hub.parent.name,
            "proposedClientId": "client-{}".format(client_slug),
            "proposedContextType": scope,
            "proposedContextId": (
                "{}-legacy-{}".format("opp" if scope == "opportunity" else "eng", client_slug)
                if scope in {"opportunity", "engagement"} else None
            ),
            "hubPath": str(hub),
            "files": rows,
            "contentClassificationRequired": scope == "unclassified",
        })
    file_rows = [row for hub in hubs for row in hub["files"]]
    return {
        "mode": "report-only",
        "root": str(root),
        "summary": {
            "hubs": len(hubs),
            "files": len(file_rows),
            "mapped": sum(row["status"] == "mapped" for row in file_rows),
            "ambiguous": sum(row["status"] == "ambiguous" for row in file_rows),
            "unmapped": sum(row["status"] == "unmapped" for row in file_rows),
            "contextProposals": sum(
                hub["proposedContextType"] in {"opportunity", "engagement"}
                for hub in hubs),
            "contentClassificationsRequired": sum(
                hub["contentClassificationRequired"] for hub in hubs),
            "humanApprovalsInferred": 0,
        },
        "hubs": hubs,
    }


def markdown(report):
    summary = report["summary"]
    lines = [
        "# Knowledge Hub migration report",
        "",
        "This report changed no client files.",
        "",
        "| Measure | Count |",
        "|---|---:|",
        "| Legacy Hubs | {} |".format(summary["hubs"]),
        "| Files inspected | {} |".format(summary["files"]),
        "| Files with one mapping | {} |".format(summary["mapped"]),
        "| Files with several possible lifecycle records | {} |".format(summary["ambiguous"]),
        "| Files with no mapping | {} |".format(summary["unmapped"]),
        "| Opportunity or engagement contexts proposed from existing buckets | {} |".format(summary["contextProposals"]),
        "| Intake folders needing content classification | {} |".format(summary["contentClassificationsRequired"]),
        "| Human approvals inferred by this report | {} |".format(summary["humanApprovalsInferred"]),
        "",
        "## Meaning",
        "",
        "A file with one mapping can be proposed for migration. An ambiguous file",
        "mixed several lifecycle domains in the old layout and needs a scoped",
        "decision. AI can classify intake content and propose splits before asking",
        "a person about any material ambiguity. Migration remains a separate write",
        "decision.",
    ]
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("root")
    parser.add_argument("--bucket-scopes", type=pathlib.Path, help="explicit JSON folder-name to lifecycle mapping; otherwise all contexts remain unclassified")
    parser.add_argument("--json-output")
    parser.add_argument("--markdown-output")
    args = parser.parse_args(argv)
    scopes = json.loads(args.bucket_scopes.read_text()) if args.bucket_scopes else None
    report = audit(args.root, scopes)
    if args.json_output:
        pathlib.Path(args.json_output).write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.markdown_output:
        pathlib.Path(args.markdown_output).write_text(markdown(report), encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
