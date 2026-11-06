#!/usr/bin/env python3
"""Derive combine arguments from a saved successful validation; never execute them."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9]{15}(?:[A-Za-z0-9]{3})?", value):
        raise ValueError("Combine details must contain Salesforce record IDs of 15 or 18 characters.")
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validation", type=Path, required=True)
    args = parser.parse_args()
    try:
        raw = args.validation.read_bytes()
        value = json.loads(raw)
        if not isinstance(value, dict) or type(value.get("status")) is not int or value["status"] != 0:
            raise ValueError("Validation must report numeric status 0.")
        result = value.get("result")
        if not isinstance(result, dict) or result.get("success") is not True:
            raise ValueError("Validation must report result.success true; do not combine after failure.")
        if "combineDetails" not in result:
            raise ValueError("Validation omits combineDetails; cannot determine whether combining is required.")
        details = result["combineDetails"]
        arguments = []
        if details is not None:
            if not isinstance(details, dict):
                raise ValueError("combineDetails must be an object or null.")
            parent = identifier(details.get("parentWorkitemId"))
            children = details.get("childWorkitemsId")
            if not isinstance(children, list) or not children:
                raise ValueError("Combined promotion requires a nonempty childWorkitemsId list.")
            children = [identifier(item) for item in children]
            if len(set(children)) != len(children) or parent in children:
                raise ValueError("Parent and children must be distinct; duplicate child IDs are invalid.")
            arguments = ["--parent-work-item-id", parent]
            for child in children:
                arguments.extend(["--child-work-item-id", child])
        print(json.dumps({"combine": details is not None, "arguments": arguments,
                          "validation_sha256": hashlib.sha256(raw).hexdigest(),
                          "execution_performed": False,
                          "remaining": "Confirm this validation belongs to the current work items, org, target stage and unchanged source before executing."},
                         separators=(",", ":")))
        return 0
    except (OSError, ValueError) as exc:
        print("BLOCKED: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
