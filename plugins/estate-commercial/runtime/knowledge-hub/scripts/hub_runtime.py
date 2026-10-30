#!/usr/bin/env python3
"""Portable record resolution and guarded local persistence for Knowledge Hub.

The functions are storage-neutral until `write_local_record` is called. Local
writes require an explicit Hub root and an expected hash for every existing file.
The module uses the Python standard library and is compatible with Python 3.9.
"""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import tempfile
import time
from contextlib import contextmanager
from typing import Dict, Iterable, List, Optional


HERE = pathlib.Path(__file__).resolve().parent
REGISTRY_PATH = HERE.parent / "references" / "record-registry.json"
PERSISTENCE_STATES = {
    "written-and-confirmed",
    "written-primary-mirrors-pending",
    "patch-returned",
    "not-written",
    "conflict-held",
}


class HubRuntimeError(Exception):
    """Base class for a portable Hub refusal."""


class UnknownRecord(HubRuntimeError):
    pass


class MissingIdentity(HubRuntimeError):
    pass


class StoreUnavailable(HubRuntimeError):
    pass


class VersionConflict(HubRuntimeError):
    pass


class UnsafePath(HubRuntimeError):
    pass


class RecordBusy(HubRuntimeError):
    pass


def load_registry(path: pathlib.Path = REGISTRY_PATH) -> Dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def resolve_record_path(record_id: str, identities: Dict[str, str], registry=None) -> str:
    registry = registry or load_registry()
    record = registry["records"].get(record_id)
    if record is None:
        raise UnknownRecord(record_id)
    path = record["path"]
    required = []
    if "{opportunity_id}" in path:
        required.append("opportunity_id")
    if "{engagement_id}" in path:
        required.append("engagement_id")
    if "{context_path}" in path:
        required.append("context_path")
    missing = [name for name in required if not identities.get(name)]
    if missing:
        raise MissingIdentity(
            "{} requires {}".format(record_id, ", ".join(missing))
        )
    for name in ("opportunity_id", "engagement_id"):
        value = identities.get(name)
        if value and (value in {".", ".."} or "/" in value or "\\" in value):
            raise MissingIdentity("{} must be a single directory identifier".format(name))
    context_path = identities.get("context_path")
    if context_path:
        candidate = pathlib.PurePosixPath(context_path)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise MissingIdentity("context_path must be relative and cannot traverse")
    return path.format(**identities)


def select_context_records(
    requested: Optional[Iterable[str]] = None,
    profile: Optional[str] = None,
    registry=None,
    limit: int = 4,
) -> List[str]:
    """Select bounded logical records without registering a calling skill.

    A caller may name exact records or use a generic context profile. Profiles
    describe consulting purposes, not approved skill names.
    """
    registry = registry or load_registry()
    if requested is not None and profile is not None:
        raise HubRuntimeError("choose requested records or a context profile, not both")
    if requested is not None:
        records = list(requested)
    elif profile is not None:
        records = registry.get("routes", {}).get(profile)
        if records is None:
            raise UnknownRecord("no context profile for {!r}".format(profile))
    else:
        raise HubRuntimeError("requested records or a context profile is required")
    if len(records) > limit:
        raise HubRuntimeError(
            "context request loads {} records; limit is {}".format(len(records), limit)
        )
    unknown = [name for name in records if name not in registry["records"]]
    if unknown:
        raise UnknownRecord(", ".join(unknown))
    return list(records)


def select_store(manifest: Dict, available: Iterable[str]) -> Dict[str, object]:
    primary = manifest.get("primaryStore")
    if primary not in {"local", "google-drive", "supplied-files"}:
        raise StoreUnavailable("manifest has no supported primary store")
    available_set = set(available)
    if primary not in available_set:
        raise StoreUnavailable(
            "primary store {!r} is unavailable; available: {}".format(
                primary, ", ".join(sorted(available_set)) or "none"
            )
        )
    mirrors = [
        name for name in manifest.get("mirrors", [])
        if name in available_set and name != primary
    ]
    return {"primary": primary, "availableMirrors": mirrors}


# ---------------------------------------------------------------------------
# Synced Drive detection
#
# A Google Drive that streams to a local mount is the access path for a `local`
# store, not a second store competing for authority. When a client Hub is
# reachable on such a mount, this runtime reads and updates it in place with the
# same guarded writes used for any local root. That path can replace an existing
# record's bytes without requiring a cloud connector. Detection stays parameterized
# so it runs without a Drive account, against a fixture tree in tests.
# ---------------------------------------------------------------------------

DEFAULT_SYNCED_DRIVE_BASE = "~/Library/CloudStorage"
HUB_FOLDER_NAME = "AI Knowledge Hub"


def _readable_dir(path) -> bool:
    """True when path lists as a directory and its first regular file reads.

    A streaming mount can list a folder while an offline content fetch fails.
    Listing plus a one-byte read of the first regular file confirms the mount
    is live, not merely present. A path that is not a directory returns False.
    When the folder holds only subdirectories, no read happens and a successful
    listing alone returns True, so `readable` is an advisory hint, not a proof
    that content fetches work.
    """
    try:
        entries = sorted(os.listdir(path))
    except OSError:
        return False
    for name in entries:
        child = os.path.join(path, name)
        if os.path.isfile(child):
            try:
                with open(child, "rb") as handle:
                    handle.read(1)
            except OSError:
                return False
            break
    return True


def synced_drive_mounts(base=None, email=None) -> List[pathlib.Path]:
    """Return Google Drive mount roots present on this host.

    `base` defaults to the macOS CloudStorage location and is a parameter so a
    test can point at a fixture tree. Each result is a directory named
    `GoogleDrive-<account>`. With `email`, only that account is returned. More
    than one account is returned as more than one mount; this never guesses.
    """
    root = pathlib.Path(base or DEFAULT_SYNCED_DRIVE_BASE).expanduser()
    if not root.is_dir():
        return []
    mounts = []
    for entry in sorted(root.iterdir()):
        if not entry.is_dir() or not entry.name.startswith("GoogleDrive-"):
            continue
        if email and entry.name != "GoogleDrive-{}".format(email):
            continue
        mounts.append(entry)
    return mounts


def _clients_dirs(mount: pathlib.Path) -> List[Dict[str, object]]:
    """Return the `Clients` directories on one mount, tagged by area.

    My Drive has one at `My Drive/Clients`. A host can hold several Shared
    drives, each with its own `Clients` folder. A missing folder is skipped.
    """
    found = []
    my_drive = mount / "My Drive" / "Clients"
    if my_drive.is_dir():
        found.append({"area": "my-drive", "dir": my_drive})
    shared = mount / "Shared drives"
    if shared.is_dir():
        try:
            drives = sorted(shared.iterdir())
        except OSError:
            drives = []
        for drive in drives:
            clients = drive / "Clients"
            if clients.is_dir():
                found.append({"area": "shared-drive", "dir": clients})
    return found


def find_synced_hub_roots(client=None, base=None, email=None) -> List[Dict[str, object]]:
    """Locate `AI Knowledge Hub` folders on synced Drive mounts.

    Returns one dict per candidate: `root` (absolute path to the hub folder),
    `area` (`my-drive` or `shared-drive`), `account` (the mount name), `client`
    (the client folder name under `Clients`), `readable` (the mount answered a
    list and a first-byte read), and `writableByDefault` (True for My Drive;
    False for a Shared drive, which an organization commonly controls read only,
    and which a caller holding a write grant can override).

    A hub may sit directly under its client folder or one level down under an
    opportunity or engagement folder; both are found. With `client`, the search
    narrows to client folders whose name contains the string (case insensitive)
    before scanning, so a large Shared drive is not walked in full. All matches
    are returned across every account; the caller disambiguates rather than this
    function choosing one.
    """
    token = (client or "").strip().lower()
    matches = []
    for mount in synced_drive_mounts(base=base, email=email):
        for entry in _clients_dirs(mount):
            clients_dir = entry["dir"]
            try:
                client_folders = sorted(clients_dir.iterdir())
            except OSError:
                continue
            for client_folder in client_folders:
                # The client name filter needs no I/O, so apply it before the
                # is_dir() stat; a narrowed search then stats one folder, not all.
                if token and token not in client_folder.name.lower():
                    continue
                if not client_folder.is_dir():
                    continue
                # The hub sits in the client folder or one level below it.
                candidates = [client_folder / HUB_FOLDER_NAME]
                candidates += sorted(client_folder.glob("*/" + HUB_FOLDER_NAME))
                for hub_path in candidates:
                    if not hub_path.is_dir():
                        continue
                    matches.append({
                        "root": str(hub_path),
                        "area": entry["area"],
                        "account": mount.name,
                        "client": client_folder.name,
                        "readable": _readable_dir(hub_path),
                        "writableByDefault": entry["area"] == "my-drive",
                    })
    return matches


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_file(path: pathlib.Path) -> Optional[str]:
    if not path.exists():
        return None
    return sha256_bytes(path.read_bytes())


def _inside(path: pathlib.Path, root: pathlib.Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def local_target(hub_root, relative_path: str) -> pathlib.Path:
    root = pathlib.Path(hub_root).expanduser().resolve()
    if not root.is_dir():
        raise UnsafePath("configured Hub root does not exist: {}".format(root))
    relative = pathlib.Path(relative_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise UnsafePath("record path must be relative and cannot traverse")
    target = (root / relative).resolve()
    if not _inside(target, root) or target == root:
        raise UnsafePath("target escapes configured Hub root: {}".format(relative_path))
    return target


def read_local_record(hub_root, relative_path: str) -> Dict[str, object]:
    """Read content and its version from the same byte snapshot."""
    target = local_target(hub_root, relative_path)
    payload = target.read_bytes()
    return {"path": str(target), "content": payload.decode("utf-8"),
            "sha256": sha256_bytes(payload)}


@contextmanager
def record_lock(root: pathlib.Path, relative_path: str, timeout: float = 10.0):
    """Serialize cooperating local writers; cloud sync needs separate checks.

    A crashed writer leaves an explicit lock to inspect. Never remove another
    process's lock merely because a timeout elapsed.
    """
    key = sha256_bytes(str(local_target(root, relative_path)).encode("utf-8"))
    lock = root / (".hub-write-lock-" + key)
    deadline = time.monotonic() + timeout
    while True:
        try:
            lock.mkdir()
            break
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise RecordBusy("record lock is held; inspect the writer before recovery: {}".format(lock))
            time.sleep(0.02)
    try:
        yield
    finally:
        lock.rmdir()


def write_local_record(
    hub_root,
    relative_path: str,
    content: str,
    expected_hash: Optional[str],
) -> Dict[str, object]:
    """Atomically create or replace one file inside an explicit Hub root.

    Existing files require their current SHA-256. New files require
    `expected_hash=None`. A changed file refuses before replacement.
    """
    root = pathlib.Path(hub_root).expanduser().resolve()
    local_target(root, relative_path)
    with record_lock(root, relative_path):
        return _write_local_record_locked(root, relative_path, content, expected_hash)


def _write_local_record_locked(root, relative_path, content, expected_hash):
    target = local_target(root, relative_path)

    before = sha256_file(target)
    if target.exists() and expected_hash is None:
        raise VersionConflict("existing files require an expected hash")
    if before != expected_hash:
        raise VersionConflict(
            "expected hash {!r}, found {!r}".format(expected_hash, before)
        )

    target.parent.mkdir(parents=True, exist_ok=True)
    payload = content.encode("utf-8")
    descriptor, temporary = tempfile.mkstemp(prefix=".hub-write-", dir=str(target.parent))
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

    after = sha256_file(target)
    intended = sha256_bytes(payload)
    if after != intended:
        raise HubRuntimeError("post-write verification failed for {}".format(target))
    return {
        "state": "written-and-confirmed",
        "path": str(target),
        "beforeHash": before,
        "afterHash": after,
    }


def legacy_matches(filename: str, registry=None) -> List[str]:
    registry = registry or load_registry()
    return sorted(
        record_id for record_id, record in registry["records"].items()
        if filename in record.get("legacy", [])
    )


def persistence_result(state: str, primary: Optional[str], mirrors=None) -> Dict:
    if state not in PERSISTENCE_STATES:
        raise HubRuntimeError("unsupported persistence state {!r}".format(state))
    return {
        "state": state,
        "primary": primary,
        "mirrors": list(mirrors or []),
    }
