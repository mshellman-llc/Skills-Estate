#!/usr/bin/env python3
"""Read, route, and update logical Hub records using the declared local store.

All output is JSON. Reads include the SHA-256 required for an existing-record
write. Creating a record requires --create; replacement requires --expected-hash.
The manifest controls authority. An unavailable primary never silently fails
over to a different store.
"""
import argparse
import json
from pathlib import Path
import sys

import hub_runtime as runtime
from hub_workspace import load_manifest, ToolError


def configured_root(hub):
    hub = Path(hub).expanduser().resolve()
    manifest = load_manifest(hub)
    if manifest is None:
        raise ToolError("hub.yaml is missing; initialize or supply the confirmed hub")
    runtime.select_store(manifest, ["local"])
    value = manifest.get("stores", {}).get("local", {}).get("root")
    if not value:
        raise ToolError("stores.local.root is required")
    root = Path(value).expanduser()
    if not root.is_absolute():
        root = hub / root
    return root.resolve(), manifest


def identities(args, manifest):
    result = {}
    for arg, collection, field in (
        ("opportunity", "opportunities", "opportunityId"),
        ("engagement", "engagements", "engagementId"),
    ):
        value = getattr(args, arg)
        if value:
            if value not in {item.get(field) for item in manifest.get(collection, [])}:
                raise runtime.MissingIdentity("{} is not registered: {}".format(arg, value))
            result[arg + "_id"] = value
            result["context_path"] = collection + "/" + value
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hub", required=True)
    context = parser.add_mutually_exclusive_group()
    context.add_argument("--opportunity")
    context.add_argument("--engagement")
    sub = parser.add_subparsers(dest="verb", required=True)
    sub.add_parser("routes", help="list available task routes and logical records")
    read = sub.add_parser("read")
    read.add_argument("record")
    route = sub.add_parser("context")
    route.add_argument("profile", help="task route, for example proposal or weekly-status")
    write = sub.add_parser("write")
    write.add_argument("record")
    write.add_argument("--input", required=True, type=Path)
    version = write.add_mutually_exclusive_group(required=True)
    version.add_argument("--expected-hash")
    version.add_argument("--create", action="store_true")
    args = parser.parse_args(argv)
    try:
        root, manifest = configured_root(args.hub)
        identity = identities(args, manifest)
        registry = runtime.load_registry()
        if args.verb == "routes":
            result = registry
        elif args.verb == "context":
            names = runtime.select_context_records(profile=args.profile, registry=registry)
            records = []
            for name in names:
                relative = runtime.resolve_record_path(name, identity, registry)
                try:
                    value = runtime.read_local_record(root, relative)
                    records.append({"record": name, **value})
                except FileNotFoundError:
                    records.append({"record": name, "relativePath": relative, "state": "missing"})
            result = {"profile": args.profile, "records": records}
        else:
            relative = runtime.resolve_record_path(args.record, identity, registry)
            if args.verb == "read":
                result = {"record": args.record, **runtime.read_local_record(root, relative)}
            else:
                text = args.input.read_text(encoding="utf-8")
                result = {"record": args.record, **runtime.write_local_record(
                    root, relative, text, None if args.create else args.expected_hash)}
                if manifest.get("mirrors"):
                    result["state"] = "written-primary-mirrors-pending"
                    result["pendingMirrors"] = manifest["mirrors"]
        print(json.dumps(result, indent=2))
        return 0
    except (runtime.HubRuntimeError, ToolError, OSError, ValueError) as exc:
        state = "conflict-held" if isinstance(exc, (runtime.VersionConflict, runtime.RecordBusy)) else "not-written"
        print(json.dumps({"state": state, "error": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
