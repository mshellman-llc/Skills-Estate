#!/usr/bin/env python3
"""Read-only local health evidence. Prints metadata, never private records or keys."""
import argparse
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

def stamp(s):
    d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if d.tzinfo is None:
        raise ValueError("timezone required")
    return d.astimezone(timezone.utc)

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()

def read_json(path):
    if path.stat().st_size > 2000000:
        raise ValueError("oversized JSON")
    return json.loads(path.read_bytes())

def restore_backup_matches(folders, receipt):
    expected = receipt.get("backupHash")
    gen = receipt.get("generation")
    if not isinstance(expected, str) or len(expected) != 64 or type(gen) is not int:
        return False
    candidates = []
    for folder in folders:
        candidates += [p for p in folder.glob(f"*-{gen}-*.enc") if p.parent.resolve() == folder.resolve()]
        accepted = folder/f"accepted-{gen}.enc"
        if accepted.is_file():
            candidates.append(accepted)
    if len(candidates) > 256:
        return False
    return any(p.is_file() and digest(p) == expected for p in candidates)

def result(area, state, note, source, now, at=None, **extra):
    r = {"area": area, "status": state, "summary": note, "source": source}
    if at:
        r["evidenceAt"] = at
        r["ageHours"] = round((now-stamp(at)).total_seconds()/3600, 2)
    r.update(extra)
    return r

def collect(config, now=None):
    now = now or datetime.now(timezone.utc)
    if config.get("schemaVersion") != 2:
        raise ValueError("unsupported evidence map")
    def configured_path(value, label):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(label + " requires an explicitly configured absolute path")
        path = Path(value).expanduser()
        if not path.is_absolute():
            raise ValueError(label + " requires an explicitly configured absolute path")
        return path
    root = configured_path(config.get("runtimeRoot"), "runtimeRoot")
    if type(config.get("bridgeMaxAgeSeconds")) is not int or config["bridgeMaxAgeSeconds"] <= 0:
        raise ValueError("bridgeMaxAgeSeconds must be a positive configured interval")
    for key in ("skillEntrypoints", "mountRoots", "launchdJobs"):
        if not isinstance(config.get(key, []), list):
            raise ValueError(key + " must be an explicit list")
    entrypoints = [configured_path(value, "skillEntrypoints") for value in config.get("skillEntrypoints", [])]
    mounts = [configured_path(value, "mountRoots") for value in config.get("mountRoots", [])]
    labels = config.get("launchdJobs", [])
    if any(not isinstance(label, str) or not re.fullmatch(r"[A-Za-z0-9._-]+", label) for label in labels):
        raise ValueError("launchdJobs must contain explicit job labels")
    rows = []
    # The explicitly configured off-device destination, when authorized for this check.
    offmac = configured_path(config["offMacBackupDir"], "offMacBackupDir") if config.get("offMacBackupDir") else None
    folders = [root/"backups"] + ([offmac] if offmac else [])
    generation = None
    try:
        generation = read_json(root/"manifest.json")["generation"]
        if type(generation) is not int or generation < 0:
            raise ValueError("invalid generation")
    except (OSError, ValueError, KeyError, TypeError):
        rows.append(result("runtime", "not-rechecked", "Runtime manifest unavailable", str(root/"manifest.json"), now))
    backup = restore = None
    bridge = []
    jobs = []
    dbpath = root/"index.sqlite"
    try:
        db = sqlite3.connect(dbpath.as_uri()+"?mode=ro", uri=True)
        try:
            db.execute("PRAGMA query_only=ON")
            def setting(k):
                v = db.execute("SELECT value FROM settings WHERE key=?", (k,)).fetchone()
                return json.loads(v[0]) if v else None
            backup, restore = setting("last_backup"), setting("last_restore")
            bridge = [json.loads(v) for (v,) in db.execute("SELECT data FROM bridge LIMIT 16")]
            jobs = db.execute("SELECT kind,state,started FROM jobs ORDER BY started DESC LIMIT 30").fetchall()
        finally:
            db.close()
    except (OSError, sqlite3.Error, ValueError, TypeError):
        rows.append(result("evidence-index", "not-rechecked", "Read-only hub index unavailable", str(dbpath), now))
    backup_path = None
    backup_good = False
    if isinstance(backup, dict):
        backup_path = Path(backup.get("destination", ""))
        allowed = (backup_path.is_absolute() and backup_path.suffix == ".enc"
                   and backup_path.parent.resolve() in [f.resolve() for f in folders])
        backup_good = bool(allowed and backup_path.is_file()
                           and digest(backup_path) == backup.get("sha256"))
        current = generation is not None and backup.get("generation") == generation
        state = "verified-now" if backup_good and current else "needs-attention" if not backup_good else "not-rechecked"
        rows.append(result("local-backup", state, "Backup hash and generation match" if state == "verified-now" else "Backup or generation needs review", "settings.last_backup", now, backup.get("at"), generation=backup.get("generation"), hashVerifiedNow=backup_good, coversCurrentGeneration=current))
    else:
        rows.append(result("local-backup", "not-rechecked", "No readable backup pointer", "settings.last_backup", now))
    if isinstance(restore, dict):
        current = generation is not None and restore.get("generation") == generation
        matching = restore_backup_matches(folders, restore)
        later_failed = any(k == "maintenance-cycle" and s == "failed" and stamp(t) > stamp(restore["at"]) for k,s,t in jobs if t)
        state = ("needs-attention" if later_failed or restore.get("state") != "passed" or (current and not matching)
                 else "verified-now" if current and matching else "not-rechecked")
        rows.append(result("restore", state, "Recorded isolated restore passed; backup hash still matches" if state == "verified-now" else "Restore evidence needs review or does not cover current generation", "settings.last_restore", now, restore.get("at"), generation=restore.get("generation"), records=restore.get("records"), backupHashVerifiedNow=matching, coversCurrentGeneration=current, laterMaintenanceFailure=later_failed, caveat="Historical test; this check does not restore"))
    else:
        rows.append(result("restore", "not-rechecked", "No readable restore pointer", "settings.last_restore", now))
    def separate_device(folder):
        try:
            return folder.stat().st_dev != root.stat().st_dev
        except OSError:
            return False
    if isinstance(backup, dict) and offmac and backup.get("offService") is True and backup_path.parent.resolve() == offmac.resolve():
        ok = backup_good and separate_device(offmac)
        rows.append(result("off-mac-copy", "verified-now" if ok else "needs-attention", "Latest backup is on the approved off-Mac volume; hash matches" if ok else "Off-Mac backup is missing, changed, or not on a separate volume", "settings.last_backup", now, backup.get("at"), destination=str(offmac)))
    elif isinstance(backup, dict) and backup.get("offService") is False and offmac:
        # An accepted-change backup is local by design; the off-Mac copy catches up at the next nightly run.
        held = separate_device(offmac) and generation is not None and any(offmac.glob(f"*-{generation}-*.enc"))
        rows.append(result("off-mac-copy", "not-rechecked" if held else "needs-attention", "Latest backup is local; an off-Mac file exists for this generation but its hash has no current receipt" if held else "Latest backup is local; no off-Mac copy of the current generation yet", "settings.last_backup", now, backup.get("at"), destination=str(offmac)))
    elif isinstance(backup, dict) and backup.get("offService") is False:
        rows.append(result("off-mac-copy", "needs-attention", "Latest backup is local; no off-Mac delivery proof", "settings.last_backup", now, backup.get("at")))
    else:
        rows.append(result("off-mac-copy", "not-rechecked", "Separate delivery receipt not verified", "off-Mac receipt", now))
    rows.append(result("key-recovery", "not-rechecked", "Separate key escrow not verified; key material was not opened", "recovery receipt", now))
    links = []
    for p in entrypoints:
        if p.name != "SKILL.md":
            raise ValueError("only skill entrypoints may be checked")
        try:
            resolved = p.resolve(strict=True)
            with p.open("rb") as f:
                f.read(1)
            links.append({"path":str(p), "resolvedPath":str(resolved), "state":"readable"})
        except FileNotFoundError:
            state = "unavailable" if any((p == mount or mount in p.parents) and not os.path.ismount(mount) for mount in mounts) else "missing"
            links.append({"path":str(p), "state":state})
        except OSError:
            links.append({"path":str(p), "state":"unavailable"})
    state = "not-rechecked" if not links else "needs-attention" if any(x["state"] == "missing" for x in links) else "not-rechecked" if any(x["state"] == "unavailable" for x in links) else "verified-now"
    rows.append(result("skill-links", state, "Selected entrypoints on this host" if links else "No entrypoints selected for this check", "live filesystem", now, paths=links))
    if bridge:
        latest = max(bridge, key=lambda v: stamp(v["at"]))
        age = (now-stamp(latest["at"])).total_seconds()
        badroots = [v.get("path") for v in latest.get("roots",[]) if v.get("state") != "mounted"]
        badsources = [v.get("id") for v in latest.get("sources",[]) if v.get("state") in ("failed","offline-or-missing")]
        state = "needs-attention" if badroots or badsources or age > config["bridgeMaxAgeSeconds"] else "verified-now"
        rows.append(result("bridge", state, "Recent bridge heartbeat and mounted roots" if state == "verified-now" else "Bridge heartbeat or sources need attention", "bridge table", now, latest["at"], failedSources=badsources, unmountedRoots=badroots, checkedSources=len(latest.get("sources",[]))))
    else:
        rows.append(result("bridge", "not-rechecked", "No readable bridge heartbeat", "bridge table", now))
    if not labels:
        rows.append(result("launchd", "not-rechecked", "No launchd jobs selected for this check", "explicit configuration", now))
    for label in labels:
        if sys.platform != "darwin":
            rows.append(result("launchd-"+label.rsplit(".",1)[-1], "not-rechecked", "launchd is only available on the Mac", "launchctl", now))
            continue
        try:
            proc = subprocess.run(["launchctl","print",f"gui/{os.getuid()}/{label}"],capture_output=True,text=True,timeout=5)
            if proc.returncode:
                raise OSError("launchctl state unavailable")
            state = "verified-now" if "\tstate = running" in proc.stdout else "needs-attention"
            rows.append(result("launchd-"+label.rsplit(".",1)[-1], state, "Job is running" if state == "verified-now" else "Job is not currently running", "launchctl", now))
        except (OSError, subprocess.TimeoutExpired):
            rows.append(result("launchd-"+label.rsplit(".",1)[-1], "not-rechecked", "launchd state unavailable in this session", "launchctl", now))
    rows.append(result("hosted", "not-rechecked", "This local script did not probe authenticated hosted access", "separate hosted check", now))
    return {"observedAt":now.isoformat(), "mode":"read-only", "runtimeGeneration":generation, "rows":rows,
            "limits":["The hub settings table is the writer-maintained receipt index.",
                      "A historical restore is not a new restore.",
                      "Local evidence does not prove off-Mac recovery or hosted access."]}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, required=True, help="Explicit owner-authorized evidence configuration outside the package")
    args = parser.parse_args()
    try:
        print(json.dumps(collect(read_json(args.index)), indent=2))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)
