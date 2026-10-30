#!/usr/bin/env python3
"""Behavior tests for portable Hub resolution and local writes."""

import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import hub_runtime as hub  # noqa: E402


passed = 0
failed = 0


def check(label, condition):
    global passed, failed
    if condition:
        passed += 1
        print("  PASS {}".format(label))
    else:
        failed += 1
        print("  FAIL {}".format(label))


def raises(label, error, function, *args, **kwargs):
    global passed, failed
    try:
        function(*args, **kwargs)
    except error:
        passed += 1
        print("  PASS {}".format(label))
    except Exception as other:
        failed += 1
        print("  FAIL {} raised {}".format(label, type(other).__name__))
    else:
        failed += 1
        print("  FAIL {} did not raise".format(label))


registry = hub.load_registry()
check("registry has lifecycle records", len(registry["records"]) == 25)
check("normal task routes stay within four records",
      all(len(records) <= 4 for records in registry["routes"].values()))
check("weekly status route is targeted",
      hub.select_context_records(profile="weekly-status") == [
          "engagement.front_door", "engagement.delivery_status", "engagement.control"])
check("a future skill can request records without registration",
      hub.select_context_records(requested=[
          "client.front_door", "engagement.outcomes_closeout"]) == [
          "client.front_door", "engagement.outcomes_closeout"])
raises("unknown requested record refuses", hub.UnknownRecord,
       hub.select_context_records, ["skill-specific-output"])
check("engagement identity resolves a portable path",
      hub.resolve_record_path("engagement.delivery_status", {
          "engagement_id": "eng-2026-example"}) ==
      "engagements/eng-2026-example/delivery-status.md")
check("evidence resolves inside its lifecycle context",
      hub.resolve_record_path("evidence.claims", {
          "context_path": "opportunities/opp-2026-example"}) ==
      "opportunities/opp-2026-example/evidence/evidence-ledger.json")
raises("missing engagement identity refuses", hub.MissingIdentity,
       hub.resolve_record_path, "engagement.delivery_status", {})
raises("unknown record refuses", hub.UnknownRecord,
       hub.resolve_record_path, "skill-specific-notes", {})
check("legacy evidence record maps without choosing one silently",
      hub.legacy_matches("03-evidence-ledger.md") == ["evidence.claims"])
check("ambiguous legacy scope remains visible",
      len(hub.legacy_matches("05-scope-plan-status.md")) == 3)

manifest = {"primaryStore": "local", "mirrors": ["google-drive"]}
check("declared primary wins when available",
      hub.select_store(manifest, ["local", "google-drive"])["primary"] == "local")
raises("missing primary refuses instead of falling through", hub.StoreUnavailable,
       hub.select_store, manifest, ["google-drive"])

with tempfile.TemporaryDirectory() as directory:
    root = pathlib.Path(directory)
    created = hub.write_local_record(root, "00-CLIENT.md", "# Client\n", None)
    check("new local record is written and confirmed",
          created["state"] == "written-and-confirmed")
    check("new local record content is exact",
          (root / "00-CLIENT.md").read_text() == "# Client\n")
    raises("existing file needs a version hash", hub.VersionConflict,
           hub.write_local_record, root, "00-CLIENT.md", "changed", None)
    updated = hub.write_local_record(
        root, "00-CLIENT.md", "# Current client\n", created["afterHash"])
    check("matching hash permits atomic replacement",
          (root / "00-CLIENT.md").read_text() == "# Current client\n")
    raises("stale hash refuses replacement", hub.VersionConflict,
           hub.write_local_record, root, "00-CLIENT.md", "bad", created["afterHash"])
    raises("path escape refuses", hub.UnsafePath,
           hub.write_local_record, root, "../outside.md", "bad", None)
    check("post-write hash is reported", len(updated["afterHash"]) == 64)

with tempfile.TemporaryDirectory() as directory:
    base = pathlib.Path(directory)
    acme_hub = base / "GoogleDrive-owner-a@example.invalid" / "My Drive" / "Clients" / "Acme Corp" / "AI Knowledge Hub"
    acme_hub.mkdir(parents=True)
    (acme_hub / "00-CLIENT.md").write_text("# Acme\n")
    beta_hub = (base / "GoogleDrive-owner-a@example.invalid" / "Shared drives" /
                "Example Shared Drive" / "Clients" / "Beta LLC" / "AI Knowledge Hub")
    beta_hub.mkdir(parents=True)
    # A hub nested one level below the client folder, under an engagement.
    thermal_hub = (base / "GoogleDrive-owner-a@example.invalid" / "Shared drives" /
                "Example Shared Drive" / "Clients" / "Example Thermal" /
                "Example - Pilot" / "AI Knowledge Hub")
    thermal_hub.mkdir(parents=True)
    west_hub = base / "GoogleDrive-owner-b@example.invalid" / "My Drive" / "Clients" / "Acme West" / "AI Knowledge Hub"
    west_hub.mkdir(parents=True)

    check("both Drive accounts are seen, never reduced to one",
          len(hub.synced_drive_mounts(base=base)) == 2)
    check("account filter narrows to one mount",
          len(hub.synced_drive_mounts(base=base, email="owner-a@example.invalid")) == 1)
    check("absent CloudStorage base yields no mounts",
          hub.synced_drive_mounts(base=base / "missing") == [])

    acme = hub.find_synced_hub_roots(client="acme", base=base)
    check("client match returns every account's hub, not the first",
          len(acme) == 2)
    check("My Drive does not imply write authority",
          all(m["writableByDefault"] is False for m in acme if m["area"] == "my-drive"))
    beta = hub.find_synced_hub_roots(client="beta", base=base)
    check("a Shared drive hub is found but not writable by default",
          len(beta) == 1 and beta[0]["writableByDefault"] is False)
    thermal = hub.find_synced_hub_roots(client="thermal", base=base)
    check("a hub nested under an engagement folder is found",
          len(thermal) == 1 and thermal[0]["client"] == "Example Thermal")
    check("no client returns hubs across areas and accounts",
          len(hub.find_synced_hub_roots(base=base)) == 4)
    check("a live mount reads as readable",
          hub._readable_dir(acme_hub) is True)
    check("a missing path is not readable",
          hub._readable_dir(base / "nope") is False)
    check("a file used as a hub root is not readable",
          hub._readable_dir(acme_hub / "00-CLIENT.md") is False)

check("patch is an explicit persistence state",
      hub.persistence_result("patch-returned", "google-drive")["state"] ==
      "patch-returned")
check("held conflict is an explicit persistence state",
      hub.persistence_result("conflict-held", "local")["state"] ==
      "conflict-held")
raises("unknown persistence language refuses", hub.HubRuntimeError,
       hub.persistence_result, "probably-saved", "local")

print("{} passed, {} failed".format(passed, failed))
if failed:
    sys.exit(1)
