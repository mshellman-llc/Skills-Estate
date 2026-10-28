#!/usr/bin/env python3
"""Deterministic logic for resolving and updating an engagement AI Knowledge Hub.

This module holds no input and output of its own. It takes Drive search results
that the agent already fetched through the Google Drive MCP connector, and returns
either a decision or a refusal. Keeping it pure is what makes the refusal rules
testable without a network call and without a Drive account.

Three rules drive everything here.

Resolve, never assume. Folder names are matched against search results the caller
supplies. Nothing constructs a path like "Clients/<name>/<name> - Opportunity".
Client and engagement folders can follow different naming patterns, so a
constructed path is a guess.

Refuse on ambiguity. Two plausible clients means stop and ask, never pick the
first or the newest. A hub written into the wrong engagement is worse than no hub.

Never claim a write that was not confirmed. Every write helper returns a planned
call for the agent to make. Persistence is recorded only from the connector's own
response.

Standard library only, Python 3.9 compatible.
"""

from __future__ import annotations

import difflib
import json
import pathlib
import re
from typing import Dict, Iterable, List, Optional, Sequence
from dataclasses import dataclass, field

FOLDER_MIME = "application/vnd.google-apps.folder"
HUB_FOLDER_TITLE = "AI Knowledge Hub"

# Markdown, not a Google Doc. `create_file` converts text/plain into
# application/vnd.google-apps.document unless conversion is switched off, which
# would quietly turn every durable knowledge file into a Doc.
MARKDOWN_MIME = "text/markdown"
JSON_MIME = "application/json"

REGISTRY_PATH = pathlib.Path(__file__).resolve().parent.parent / "references" / "record-registry.json"
with REGISTRY_PATH.open(encoding="utf-8") as _registry_handle:
    RECORD_REGISTRY = json.load(_registry_handle)["records"]

CANONICAL_FILES = (
    "00-hub-index.md",
    "01-client-engagement-profile.md",
    "02-source-register.md",
    "03-evidence-ledger.md",
    "04-decisions-assumptions.md",
    "05-scope-plan-status.md",
    "06-meetings-handoffs.md",
    "07-deliverables-register.md",
)

# Portable capability name mapped to the Drive MCP tool that provides it.
#
# These are names from the legacy adapter, not a live capability inventory.
# Content replacement needs an explicit schema-matched contract and file ID.
CAPABILITY_TOOLS = {
    "search": ("search_files", "list_recent_files"),
    "read": ("read_file_content", "download_file_content"),
    "create": ("create_file",),
    "rename_or_move": ("update_file",),
    "content_update": (),
}

# A managed section is rewritten in place. Anything outside the markers is the
# author's and survives untouched.
SECTION_START = "<!-- HUB-SECTION:{key}:START -->"
SECTION_END = "<!-- HUB-SECTION:{key}:END -->"


class HubError(Exception):
    """Base class so a caller can catch every refusal in one place."""


class CapabilityMissing(HubError):
    def __init__(self, capability: str, available: Sequence[str]):
        self.capability = capability
        self.available = list(available)
        super().__init__(
            "the {} capability is not available; detected tools: {}".format(
                capability, ", ".join(sorted(available)) or "none"
            )
        )


class NotFound(HubError):
    def __init__(self, what: str, searched_in: Optional[str] = None):
        self.what = what
        self.searched_in = searched_in
        where = " under parent {}".format(searched_in) if searched_in else ""
        super().__init__("no match for {}{}".format(what, where))


class ContentUpdateUnsupported(HubError):
    """Raised when a canonical file exists and would have to be edited in place.

    Carries the merged document, so the caller can present exactly what the file
    should become without pretending it was saved.
    """

    def __init__(self, filename, merged, reason):
        self.filename = filename
        self.merged = merged
        self.reason = reason
        super().__init__(
            "{} exists and cannot be updated in place: {}".format(filename, reason)
        )


@dataclass(frozen=True)
class ContentUpdateContract:
    """Argument mapping confirmed from the available tool's actual schema.

    This creates a plan only. The caller executes it, checks the service's
    response, and reads back the same file ID before claiming persistence.
    """
    tool: str
    file_id_argument: str
    content_argument: str
    version_argument: Optional[str] = None
    extra_arguments: Dict = field(default_factory=dict)

    def plan(self, file_id, content, expected_version=None):
        if not file_id:
            raise HubError("content replacement requires the existing canonical file ID")
        names = [self.file_id_argument, self.content_argument]
        if self.version_argument:
            names.append(self.version_argument)
        if not self.tool or not all(names) or len(set(names)) != len(names):
            raise HubError("content update argument mapping is invalid")
        if set(names).intersection(self.extra_arguments):
            raise HubError("extra arguments cannot override identity, content, or version")
        arguments = {**self.extra_arguments, self.file_id_argument: file_id,
                     self.content_argument: content}
        if self.version_argument:
            if expected_version is None:
                raise HubError("this updater requires the observed file version")
            arguments[self.version_argument] = expected_version
        return {"tool": self.tool, "arguments": arguments, "situation": "update",
                "requiresReadback": True}


class Ambiguous(HubError):
    """Raised instead of guessing. Carries the candidates so the agent can ask."""

    def __init__(self, what: str, candidates: Sequence[Dict]):
        self.what = what
        self.candidates = list(candidates)
        listing = "; ".join(
            "{} ({})".format(c.get("title", "?"), c.get("id", "?")) for c in self.candidates
        )
        super().__init__(
            "{} is ambiguous across {} candidates, refusing to choose: {}".format(
                what, len(self.candidates), listing
            )
        )


def detect_capabilities(available_tools: Iterable[str], update_contract=None) -> Dict[str, bool]:
    """Map the connector's tool list onto the four capabilities the hub needs.

    Each is detected independently. A host that can search and read but not
    create still gets a useful answer, and the read-only path is the fallback the
    standard requires rather than an error.
    """
    names = {t.rsplit("__", 1)[-1] for t in available_tools}
    result = {
        capability: any(tool in names for tool in tools)
        for capability, tools in CAPABILITY_TOOLS.items()
    }
    if update_contract is not None:
        result["content_update"] = update_contract.tool.rsplit("__", 1)[-1] in names
    return result


def require(capabilities: Dict[str, bool], capability: str) -> None:
    if not capabilities.get(capability):
        raise CapabilityMissing(
            capability, [name for name, ok in capabilities.items() if ok]
        )


def _normalize(title: str) -> str:
    """Fold case, punctuation and spacing so 'Acme Co.' meets 'acme co'."""
    return re.sub(r"[^a-z0-9]+", " ", (title or "").lower()).strip()


def _folders(results: Sequence[Dict]) -> List[Dict]:
    return [r for r in results if r.get("mimeType") == FOLDER_MIME]


def choose_folder(
    results: Sequence[Dict],
    wanted: str,
    parent_id: Optional[str] = None,
    similarity: float = 0.82,
) -> Dict:
    """Pick the one folder matching `wanted`, or refuse.

    Order of preference: an exact normalized title match, then a single
    close match above `similarity`. More than one candidate at the same
    strength is ambiguous, and ambiguity is a refusal, not a tie-break.
    """
    candidates = _folders(results)
    if parent_id:
        candidates = [c for c in candidates if c.get("parentId") == parent_id]
    if not candidates:
        raise NotFound(repr(wanted), parent_id)

    target = _normalize(wanted)
    exact = [c for c in candidates if _normalize(c.get("title", "")) == target]
    if len(exact) == 1:
        return exact[0]
    if len(exact) > 1:
        raise Ambiguous("client or engagement folder {!r}".format(wanted), exact)

    scored = []
    for candidate in candidates:
        ratio = difflib.SequenceMatcher(
            None, target, _normalize(candidate.get("title", ""))
        ).ratio()
        if ratio >= similarity:
            scored.append((ratio, candidate))
    if not scored:
        raise NotFound(repr(wanted), parent_id)
    best = max(score for score, _ in scored)
    close = [c for score, c in scored if abs(score - best) < 0.02]
    if len(close) > 1:
        raise Ambiguous("client or engagement folder {!r}".format(wanted), close)
    return close[0]


def find_hub(results: Sequence[Dict], parent_id: str) -> Optional[Dict]:
    """Return the AI Knowledge Hub folder inside a confirmed parent, or None.

    None means absent, which is a create decision. It never means "look higher
    up". The lifecycle layout normally passes the confirmed client folder. A
    legacy engagement folder remains supported during discovery.
    """
    hubs = [
        r
        for r in _folders(results)
        if r.get("parentId") == parent_id
        and _normalize(r.get("title", "")) == _normalize(HUB_FOLDER_TITLE)
    ]
    if len(hubs) > 1:
        raise Ambiguous("AI Knowledge Hub inside parent {}".format(parent_id), hubs)
    return hubs[0] if hubs else None


def plan_create_folder(title: str, parent_id: str) -> Dict:
    """The create_file arguments for a folder. Returned, not executed."""
    if not parent_id:
        raise HubError("refusing to create {!r} with no confirmed parent".format(title))
    return {"tool": "create_file", "arguments": {
        "title": title, "parentId": parent_id, "mimeType": FOLDER_MIME}}


def plan_create_markdown(title: str, parent_id: str, text: str) -> Dict:
    """The create_file arguments for a genuine Markdown file.

    `disableConversionToGoogleType` is the load-bearing flag. Without it Drive
    converts the upload into a Google Doc, and a hub of Docs is not the durable
    Markdown the standard specifies.
    """
    if not title.endswith(".md"):
        raise HubError("hub files must end in .md, got {!r}".format(title))
    if not parent_id:
        raise HubError("refusing to create {!r} with no confirmed parent".format(title))
    return {"tool": "create_file", "arguments": {
        "title": title,
        "parentId": parent_id,
        "textContent": text,
        "contentMimeType": MARKDOWN_MIME,
        "disableConversionToGoogleType": True,
    }}


def plan_create_json(title: str, parent_id: str, text: str) -> Dict:
    """Plan a JSON file create without Drive conversion."""
    if not title.endswith(".json"):
        raise HubError("JSON hub files must end in .json, got {!r}".format(title))
    if not parent_id:
        raise HubError("refusing to create {!r} with no confirmed parent".format(title))
    try:
        json.loads(text)
    except json.JSONDecodeError as error:
        raise HubError("invalid JSON for {!r}: {}".format(title, error))
    return {"tool": "create_file", "arguments": {
        "title": title,
        "parentId": parent_id,
        "textContent": text,
        "contentMimeType": JSON_MIME,
        "disableConversionToGoogleType": True,
    }}


def plan_record_write(
    record_id: str,
    target_parent_id: str,
    content: str,
    capabilities: Dict[str, bool],
    existing: Optional[str] = None,
    update_contract: Optional[ContentUpdateContract] = None,
    file_id: Optional[str] = None,
    expected_version=None,
) -> Dict:
    """Plan a complete logical-record write inside its resolved Drive folder."""
    record = RECORD_REGISTRY.get(record_id)
    if record is None:
        raise HubError("unknown logical Hub record {!r}".format(record_id))
    title = pathlib.PurePosixPath(record["path"]).name
    if existing is not None and (not capabilities.get("content_update") or update_contract is None):
        raise ContentUpdateUnsupported(
            record_id, content,
            "the connector cannot replace the existing logical record",
        )
    require(capabilities, "create" if existing is None else "content_update")
    if existing is not None:
        return {**update_contract.plan(file_id, content, expected_version), "record": record_id}
    plan = (
        plan_create_json(title, target_parent_id, content)
        if title.endswith(".json")
        else plan_create_markdown(title, target_parent_id, content)
    )
    plan["record"] = record_id
    plan["situation"] = "create" if existing is None else "update"
    return plan


def plan_canonical_write(
    filename: str,
    parent_id: str,
    section: str,
    body: str,
    capabilities: Dict[str, bool],
    existing: Optional[str] = None,
    timestamp: Optional[str] = None,
    update_contract: Optional[ContentUpdateContract] = None,
    file_id: Optional[str] = None,
    expected_version=None,
) -> Dict:
    """Plan the write for one canonical hub file, or refuse and say why.

    Two different situations, and conflating them is how a skill ends up claiming
    a save that never happened.

    The file does not exist yet. `create_file` handles that, and the returned
    plan is a real call the agent can make.

    The file exists. Updating it requires an explicit schema-matched content
    updater and the canonical file ID. Without them the planner refuses. Creating a second file with the same title would leave
    two copies of the same canonical record in one hub, which the standard rules
    out. An unsupported update raises
    `ContentUpdateUnsupported` carrying the merged document for a patch.
    """
    if filename not in CANONICAL_FILES:
        raise HubError("{!r} is not a canonical hub file".format(filename))
    merged = (
        upsert_section(existing, section, body) if timestamp is None
        else supersede(existing, section, body, timestamp)
    ) if existing is not None else upsert_section("", section, body)

    if existing is None:
        require(capabilities, "create")
        plan = plan_create_markdown(filename, parent_id, merged)
        plan["situation"] = "create"
        plan["merged"] = merged
        return plan

    if not capabilities.get("content_update") or update_contract is None:
        raise ContentUpdateUnsupported(
            filename, merged,
            "no schema-matched content updater is configured; creating another "
            "file would duplicate the canonical record",
        )
    return {**update_contract.plan(file_id, merged, expected_version), "merged": merged}


def upsert_section(document: str, key: str, body: str) -> str:
    """Replace the managed section `key`, or append it when absent.

    Idempotent by construction: running the same skill twice with the same
    finding rewrites one block rather than appending a second dated copy, which
    is the duplication the standard rules out.
    """
    start, end = SECTION_START.format(key=key), SECTION_END.format(key=key)
    block = "{}\n{}\n{}".format(start, body.strip(), end)
    pattern = re.compile(
        re.escape(start) + r".*?" + re.escape(end), re.S
    )
    if pattern.search(document):
        return pattern.sub(lambda _: block, document, count=1)
    separator = "" if document.endswith("\n\n") or not document else "\n"
    return "{}{}\n{}\n".format(document, separator, block)


def supersede(document: str, key: str, body: str, timestamp: str) -> str:
    """Mark the current managed section superseded and add the replacement.

    Prior decisions are preserved rather than overwritten. The old block stays,
    labelled, so the record shows what changed and when.
    """
    start, end = SECTION_START.format(key=key), SECTION_END.format(key=key)
    pattern = re.compile(re.escape(start) + r"(.*?)" + re.escape(end), re.S)
    match = pattern.search(document)
    if not match:
        return upsert_section(document, key, body)
    previous = match.group(1).strip()
    archived = (
        "> Superseded {}. Retained for provenance.\n>\n".format(timestamp)
        + "\n".join("> " + line if line else ">" for line in previous.splitlines())
    )
    replaced = pattern.sub(lambda _: archived, document, count=1)
    return upsert_section(replaced, key, body)


def index_entry(timestamp: str, skill: str, changed: Sequence[str], summary: str) -> str:
    """One legacy update-history row retained for migration compatibility."""
    files = ", ".join(f"`{name}`" for name in changed) if changed else "none"
    return "| {} | `{}` | {} | {} |".format(
        timestamp, skill, files, summary.replace("|", "\\|")
    )


def write_patch(
    targets: Sequence[Dict], reason: str, resolved: Optional[Dict] = None
) -> str:
    """The fallback when read works and write does not.

    Names the exact canonical target for each change so a person can apply it,
    and says plainly that nothing was persisted. A patch presented as a saved
    update is the failure this avoids.
    """
    lines = [
        "# Knowledge Hub patch, not applied",
        "",
        "Persistence did not occur. {}".format(reason),
        "",
    ]
    if resolved:
        lines += [
            "Intended hub: {} (folder id `{}`)".format(
                resolved.get("path", "unresolved"), resolved.get("id", "unknown")
            ),
            "",
        ]
    for target in targets:
        name = target.get("record") or target.get("file", "unknown.md")
        if name not in CANONICAL_FILES and name not in RECORD_REGISTRY:
            raise HubError("{!r} is not a canonical hub target".format(name))
        lines += [
            "## `{}`".format(name),
            "",
            "Section: `{}`".format(target.get("section", "unspecified")),
            "",
            "```markdown",
            (target.get("body") or "").strip(),
            "```",
            "",
        ]
    lines += [
        "## To apply",
        "",
        "1. Open the hub folder named above.",
        "2. For each file, replace the managed section between its markers.",
        "3. Refresh the projection metadata and relevant collection index.",
        "",
    ]
    return "\n".join(lines)
