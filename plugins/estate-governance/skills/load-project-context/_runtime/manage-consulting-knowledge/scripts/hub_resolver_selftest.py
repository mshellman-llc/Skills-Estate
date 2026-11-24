#!/usr/bin/env python3
"""Selftest for the Knowledge Hub resolver.

Fixtures are shaped like real Google Drive MCP `search_files` responses, including
synthetic variations in client and engagement folder naming.
Standard library only, Python 3.9 compatible.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import hub_resolver as hub  # noqa: E402

FOLDER = hub.FOLDER_MIME
passed = failed = 0


def check(label, got, want):
    global passed, failed
    if got == want:
        passed += 1
        print("  PASS {}".format(label))
    else:
        failed += 1
        print("  FAIL {}  got={!r} want={!r}".format(label, got, want))


def raises(label, exc, fn, *a, **kw):
    global passed, failed
    try:
        fn(*a, **kw)
    except exc:
        passed += 1
        print("  PASS {}".format(label))
        return
    except Exception as other:
        failed += 1
        print("  FAIL {}  raised {} not {}".format(label, type(other).__name__, exc.__name__))
        return
    failed += 1
    print("  FAIL {}  did not raise {}".format(label, exc.__name__))


def folder(fid, title, parent=None):
    return {"id": fid, "title": title, "mimeType": FOLDER, "parentId": parent}


print("== capability detection ==")
full = hub.detect_capabilities([
    "mcp__drive__search_files", "mcp__drive__read_file_content",
    "mcp__drive__create_file", "mcp__drive__update_file",
])
check("every capability detected", full,
      {"search": True, "read": True, "create": True,
       "rename_or_move": True, "content_update": False})

readonly = hub.detect_capabilities(["mcp__drive__search_files", "mcp__drive__read_file_content"])
check("read-only host detected", readonly,
      {"search": True, "read": True, "create": False,
       "rename_or_move": False, "content_update": False})
check("create is independent of read", readonly["create"], False)

none = hub.detect_capabilities([])
check("no connector at all", none,
      {"search": False, "read": False, "create": False,
       "rename_or_move": False, "content_update": False})
raises("missing capability refuses", hub.CapabilityMissing, hub.require, readonly, "create")
hub.require(readonly, "read")
print("  PASS present capability passes require")
passed += 1

print()
print("== client resolution, never assumed ==")
clients = [
    folder("c1", "Example Materials", "root"),
    folder("c2", "Example Catalog", "root"),
    folder("c3", "Example Parts", "root"),
    {"id": "f9", "title": "Example Catalog", "mimeType": "application/pdf", "parentId": "root"},
]
check("exact match resolves", hub.choose_folder(clients, "Example Catalog")["id"], "c2")
check("case and punctuation folded", hub.choose_folder(clients, "example catalog")["id"], "c2")
check("a file is never chosen as a folder",
      hub.choose_folder(clients, "Example Catalog")["mimeType"], FOLDER)
raises("unknown client is NotFound", hub.NotFound, hub.choose_folder, clients, "Nonexistent Corp")

twins = [folder("d1", "Acme Group", "root"), folder("d2", "Acme  Group", "root")]
raises("two identical clients refuse", hub.Ambiguous, hub.choose_folder, twins, "Acme Group")
try:
    hub.choose_folder(twins, "Acme Group")
except hub.Ambiguous as exc:
    check("refusal carries both candidates", len(exc.candidates), 2)

print()
print("== engagement resolution across varied naming patterns ==")
# Three synthetic variations in engagement-folder naming.
engagements = [
    folder("e1", "Example Catalog - SOW002 - Communities and Knowledge - Opportunity", "c2"),
    folder("e2", "Example Catalog - Knowledge - SOW002 - Delivery", "c2"),
    folder("e3", "Example Materials - Commerce - Opportunity", "c1"),
]
check("exact engagement title resolves",
      hub.choose_folder(engagements, "Example Catalog - Knowledge - SOW002 - Delivery", parent_id="c2")["id"],
      "e2")
check("parent scoping excludes another client's engagement",
      hub.choose_folder(engagements, "Example Materials - Commerce - Opportunity", parent_id="c1")["id"], "e3")
raises("engagement from the wrong parent is NotFound", hub.NotFound,
       hub.choose_folder, engagements, "Example Materials - Commerce - Opportunity", "c2")

print()
print("== hub resolution ==")
check("absent hub returns None, not a guess", hub.find_hub(engagements, "e2"), None)
with_hub = engagements + [folder("h1", "AI Knowledge Hub", "e2")]
check("hub inside the engagement resolves", hub.find_hub(with_hub, "e2")["id"], "h1")
check("a hub in a sibling engagement is not borrowed", hub.find_hub(with_hub, "e1"), None)
client_root_hub = engagements + [folder("h9", "AI Knowledge Hub", "c2")]
check("a hub at the client root is never used for an engagement",
      hub.find_hub(client_root_hub, "e2"), None)
check("the lifecycle hub resolves at the confirmed client root",
      hub.find_hub(client_root_hub, "c2")["id"], "h9")
raises("two hubs in one engagement refuse", hub.Ambiguous, hub.find_hub,
       with_hub + [folder("h2", "ai knowledge hub", "e2")], "e2")

print()
print("== planned writes ==")
plan = hub.plan_create_markdown("00-hub-index.md", "h1", "# Index\n")
check("markdown conversion is disabled",
      plan["arguments"]["disableConversionToGoogleType"], True)
check("content mime type is markdown", plan["arguments"]["contentMimeType"], "text/markdown")
check("text goes in textContent", plan["arguments"]["textContent"], "# Index\n")
check("parent is the hub folder", plan["arguments"]["parentId"], "h1")
raises("a non-markdown hub file is refused", hub.HubError,
       hub.plan_create_markdown, "index.gdoc", "h1", "x")
raises("creating a file with no parent is refused", hub.HubError,
       hub.plan_create_markdown, "00-hub-index.md", "", "x")
raises("creating a folder with no parent is refused", hub.HubError,
       hub.plan_create_folder, hub.HUB_FOLDER_TITLE, "")
check("hub folder plan uses the folder mime type",
      hub.plan_create_folder(hub.HUB_FOLDER_TITLE, "e2")["arguments"]["mimeType"], FOLDER)

logical = hub.plan_record_write(
    "evidence.claims", "evidence-folder", '{"claims": []}\n', full,
    existing=None)
check("logical record disables conversion",
      logical["arguments"]["disableConversionToGoogleType"], True)
check("evidence ledger uses JSON",
      logical["arguments"]["contentMimeType"], "application/json")
check("logical record keeps its record ID", logical["record"], "evidence.claims")
raises("unknown logical record refuses", hub.HubError,
       hub.plan_record_write, "skill.notes", "h1", "x", full)

print()
print("== idempotent section update ==")
doc = "# Evidence ledger\n\nAuthor's own prose stays.\n"
once = hub.upsert_section(doc, "claims", "- ACV is 1.2M, confidence medium")
twice = hub.upsert_section(once, "claims", "- ACV is 1.2M, confidence medium")
check("second identical update changes nothing", twice, once)
check("running twice does not duplicate the block", twice.count("HUB-SECTION:claims:START"), 1)
check("surrounding prose survives", "Author's own prose stays." in twice, True)
updated = hub.upsert_section(once, "claims", "- ACV is 1.4M, confidence high")
check("a changed body replaces in place", updated.count("HUB-SECTION:claims:START"), 1)
check("new value present", "1.4M" in updated, True)
check("old value gone on plain upsert", "1.2M" in updated, False)
check("a second key is added alongside",
      hub.upsert_section(once, "risks", "- none").count("HUB-SECTION:"), 4)

print()
print("== supersession preserves the prior record ==")
superseded = hub.supersede(once, "claims", "- ACV is 1.4M, confidence high",
                           "2026-08-17T00:00:00Z")
check("prior value retained", "1.2M" in superseded, True)
check("new value present", "1.4M" in superseded, True)
check("marked superseded with a timestamp",
      "Superseded 2026-08-17T00:00:00Z" in superseded, True)
check("supersede on a missing key behaves as upsert",
      "1.4M" in hub.supersede(doc, "claims", "- ACV is 1.4M, confidence high", "2026-08-17T00:00:00Z"),
      True)

print()
print("== index history row ==")
row = hub.index_entry("2026-08-17T12:00:00Z", "estimate-project",
                      ["03-evidence-ledger.md"], "Added ROM inputs")
check("row names the skill", "`estimate-project`" in row, True)
check("row names the changed file", "`03-evidence-ledger.md`" in row, True)
check("a pipe in the summary is escaped",
      "\\|" in hub.index_entry("t", "s", [], "a | b"), True)

print()
print("== denied-write fallback ==")
patch = hub.write_patch(
    [{"file": "03-evidence-ledger.md", "section": "claims", "body": "- ACV is 1.2M"}],
    "The connector exposes read but not create or update.",
    {"path": "Clients/Example Catalog/Example Catalog - Knowledge - SOW002 - Delivery/AI Knowledge Hub",
     "id": "h1"},
)
check("patch says persistence did not occur", "Persistence did not occur" in patch, True)
check("patch names the canonical target file", "`03-evidence-ledger.md`" in patch, True)
check("patch names the intended hub", "AI Knowledge Hub" in patch, True)
check("patch names the section", "`claims`" in patch, True)
check("patch carries the body", "- ACV is 1.2M" in patch, True)
raises("a non-canonical target is refused", hub.HubError, hub.write_patch,
       [{"file": "notes.md", "section": "x", "body": "y"}], "read only")

print()
print("== content replacement is not available on this connector ==")
full_caps = hub.detect_capabilities([
    "search_files", "read_file_content", "create_file", "update_file",
])
check("content_update is false even with every tool present",
      full_caps["content_update"], False)
check("rename_or_move is what update_file actually provides",
      full_caps["rename_or_move"], True)

# A canonical file that does not exist yet: a real create plan.
created = hub.plan_canonical_write(
    "03-evidence-ledger.md", "h1", "claims", "- ACV is 1.2M", full_caps, existing=None)
check("absent file plans a create", created["situation"], "create")
check("create plan disables Google conversion",
      created["arguments"]["disableConversionToGoogleType"], True)
check("create plan carries the merged body",
      "- ACV is 1.2M" in created["arguments"]["textContent"], True)

# The same file, now existing: refuse rather than duplicate.
raises("existing file refuses in-place update", hub.ContentUpdateUnsupported,
       hub.plan_canonical_write, "03-evidence-ledger.md", "h1", "claims",
       "- ACV is 1.4M", full_caps, "# Evidence ledger\n")
try:
    hub.plan_canonical_write("03-evidence-ledger.md", "h1", "claims",
                             "- ACV is 1.4M", full_caps, "# Evidence ledger\n")
except hub.ContentUpdateUnsupported as exc:
    check("refusal carries the merged document", "- ACV is 1.4M" in exc.merged, True)
    check("merged document keeps the author's prose",
          "# Evidence ledger" in exc.merged, True)
    check("refusal names the file", exc.filename, "03-evidence-ledger.md")
    check("refusal explains why", "no schema-matched content updater" in exc.reason, True)
    patch = hub.write_patch(
        [{"file": exc.filename, "section": "claims", "body": exc.merged}],
        "The connector cannot replace the content of an existing file.")
    check("the refusal converts into a patch",
          "Persistence did not occur" in patch, True)

raises("a non-canonical target is refused before any planning", hub.HubError,
       hub.plan_canonical_write, "notes.md", "h1", "s", "b", full_caps)

print()
print("== canonical file set matches the standard ==")
legacy_names = {name for record in hub.RECORD_REGISTRY.values() for name in record.get("legacy", [])}
missing = [name for name in hub.CANONICAL_FILES if name not in legacy_names]
check("every legacy canonical file maps through the packaged registry", missing, [])
check("eight legacy canonical files", len(hub.CANONICAL_FILES), 8)

print()
print("{} passed, {} failed".format(passed, failed))
if failed:
    print("SELFTEST FAILED")
    sys.exit(1)
print("SELFTEST PASSED")
