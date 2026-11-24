#!/usr/bin/env python3
"""Pursuit and delivery workspace lifecycle for a local Knowledge Hub.

Workspace commands:

  init    create or repair a hub root and, optionally, one opportunity workspace.
          Idempotent: a second run adds what is missing and overwrites nothing.
  audit   read-only health report: manifest, index files, Drive conflict copies,
          git integrity (dangling commits from a sync race), dormancy.
  doctor  audit, then the safe repairs: reattach dangling commits under
          refs/heads/recovered/, restore missing pointer files. Says so per fix.
  check   gate work product: frontmatter, claim-tag vocabulary, assumptions
          sections, relative dates, ledger append-only against the committed
          copy, CLM and SRC references resolving to ledger events.

Exit codes: 0 clean or warnings only, 1 blocking findings, 2 the tool could not
run. Standard library only. Python 3.9.

The hub manifest `hub.yaml` is written as JSON, which is valid YAML, so this
runtime can read it without PyYAML. A hand-edited YAML manifest is read through
PyYAML when that module is present, and refused with exit 2 when it is not.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
from typing import Dict, List, Optional, Tuple

HERE = pathlib.Path(__file__).resolve().parent
SKILL = HERE.parent
TEMPLATES = SKILL / "templates"
REFERENCES = SKILL / "references"

MANIFEST = "hub.yaml"
LEDGER_NAME = "evidence-ledger.jsonl"
WORKING_AREAS = ("inputs", "research", "synthesis")
CONTEXT_ROOTS = ("opportunities", "engagements")
DORMANT_DAYS = 60

CONFLICT_COPY = re.compile(r" \(\d+\)(\.[^.]+)?$")
LOCK_FILE = re.compile(r"^\.~lock\..*#$")
KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
CLAIM_TAG = re.compile(r"\[(STATED|OBSERVED|INFERRED|DECIDED|ASSUMED)(?:,[^\]]*)?\]")
FOREIGN_TAG = re.compile(
    r"\[(CONFIRMED|INFERENCE|ASSUMPTION|DECISION|OBSERVATION|STATEMENT|UNKNOWN|CONTESTED)\]")
CLM_REF = re.compile(r"\bCLM-\d{3,}\b")
SRC_REF = re.compile(r"\bSRC-\d{3,}\b")
RELATIVE_DATE = re.compile(
    r"\b(yesterday|tomorrow|recently|last (?:week|month|year)|next (?:week|month|year))\b",
    re.IGNORECASE)
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---", re.S)
REQUIRED_FRONTMATTER = ("title", "status", "owner", "updated", "sources")
STATUS_VALUES = {"draft", "in-review", "final", "live"}
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class ToolError(Exception):
    """The tool could not run. Exit 2."""


# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------

class Report:
    def __init__(self, verb: str, hub: pathlib.Path):
        self.verb = verb
        self.hub = str(hub)
        self.findings: List[Dict[str, str]] = []
        self.actions: List[Dict[str, str]] = []

    def block(self, code: str, message: str, path: str = "") -> None:
        self.findings.append({"level": "blocking", "code": code, "message": message, "path": path})

    def warn(self, code: str, message: str, path: str = "") -> None:
        self.findings.append({"level": "warning", "code": code, "message": message, "path": path})

    def act(self, kind: str, message: str, path: str = "") -> None:
        self.actions.append({"kind": kind, "message": message, "path": path})

    @property
    def blocking(self) -> int:
        return sum(1 for item in self.findings if item["level"] == "blocking")

    @property
    def warnings(self) -> int:
        return sum(1 for item in self.findings if item["level"] == "warning")

    def exit_code(self) -> int:
        return 1 if self.blocking else 0

    def to_dict(self) -> Dict[str, object]:
        return {
            "verb": self.verb,
            "hub": self.hub,
            "blocking": self.blocking,
            "warnings": self.warnings,
            "findings": self.findings,
            "actions": self.actions,
            "exitCode": self.exit_code(),
        }

    def render(self) -> str:
        lines = ["{} {}".format(self.verb, self.hub)]
        for item in self.actions:
            lines.append("  {:<8} {} {}".format(item["kind"].upper(), item["path"], item["message"]).rstrip())
        for item in self.findings:
            lines.append("  {:<8} {} {} {}".format(
                item["level"].upper(), item["code"], item["path"], item["message"]).rstrip())
        lines.append("  {} blocking, {} warnings, exit {}".format(
            self.blocking, self.warnings, self.exit_code()))
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------

def today() -> str:
    return _dt.date.today().isoformat()


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def load_manifest(hub: pathlib.Path) -> Optional[Dict]:
    path = hub / MANIFEST
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    try:
        loaded = json.loads(text)
    except ValueError:
        try:
            import yaml  # type: ignore
        except ImportError:
            raise ToolError(
                "{} is not JSON and PyYAML is not installed; cannot read the manifest".format(path))
        loaded = yaml.safe_load(text)
    if not isinstance(loaded, dict):
        raise ToolError("{} is not a mapping".format(path))
    return loaded


def write_manifest(hub: pathlib.Path, manifest: Dict) -> None:
    (hub / MANIFEST).write_text(json.dumps(manifest, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def new_manifest(client: str, client_id: str, aliases: List[str], git: bool) -> Dict:
    return {
        "schemaVersion": "1.0",
        "client": {"clientId": client_id, "canonicalName": client, "aliases": aliases},
        "opportunities": [],
        "engagements": [],
        "primaryStore": "local",
        "mirrors": [],
        "stores": {"local": {"root": ".", "gitRepository": git, "syncedFilesystem": False}},
        "persistence": {"conflictPolicy": "stop-and-report", "lastVerified": None},
    }


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def git_available() -> bool:
    return shutil.which("git") is not None


def git(hub: pathlib.Path, *args: str, check: bool = False) -> Tuple[int, str]:
    completed = subprocess.run(
        ["git", "-C", str(hub)] + list(args),
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if check and completed.returncode != 0:
        raise ToolError("git {} failed: {}".format(" ".join(args), completed.stdout.strip()))
    return completed.returncode, completed.stdout


def is_git_repo(hub: pathlib.Path) -> bool:
    return (hub / ".git").is_dir()


def dangling_commits(hub: pathlib.Path) -> Tuple[List[str], List[str]]:
    """Return (dangling commit shas, other fsck problems).

    `--no-reflogs` matters: a synced `.git/logs` may or may not carry the losing
    machine's entry, and a commit that only the reflog reaches is exactly the
    case a Drive race produces. Without the flag fsck would call it reachable.
    """
    code, out = git(hub, "fsck", "--no-reflogs", "--no-progress")
    dangling = []
    problems = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("dangling commit "):
            dangling.append(line.split()[-1])
        elif line.startswith("dangling "):
            continue  # blobs and trees left by an aborted write are noise
        elif code != 0 or line.startswith(("error", "missing", "broken")):
            problems.append(line)
    return dangling, problems


def last_commit_age_days(hub: pathlib.Path) -> Optional[int]:
    code, out = git(hub, "log", "-1", "--format=%ct")
    if code != 0 or not out.strip():
        return None
    then = _dt.datetime.fromtimestamp(int(out.strip()), tz=_dt.timezone.utc)
    return (_dt.datetime.now(tz=_dt.timezone.utc) - then).days


def recovered_refs(hub: pathlib.Path) -> List[str]:
    code, out = git(hub, "for-each-ref", "--format=%(refname:short)", "refs/heads/recovered/")
    if code != 0:
        return []
    return [line for line in out.splitlines() if line.strip()]


def committed_text(hub: pathlib.Path, relative: str) -> Optional[bytes]:
    code, _ = git(hub, "cat-file", "-e", "HEAD:{}".format(relative))
    if code != 0:
        return None
    completed = subprocess.run(
        ["git", "-C", str(hub), "show", "HEAD:{}".format(relative)], stdout=subprocess.PIPE)
    return completed.stdout if completed.returncode == 0 else None


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

def render_template(name: str, values: Dict[str, str]) -> str:
    text = (TEMPLATES / name).read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def ensure_file(report: Report, path: pathlib.Path, content: str) -> bool:
    safe_workspace_path(path, pathlib.Path(report.hub))
    if path.exists():
        report.act("kept", "exists, left as is", str(path.relative_to(report.hub)))
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    report.act("created", "", str(path.relative_to(report.hub)))
    return True


def ensure_dir(report: Report, path: pathlib.Path) -> None:
    safe_workspace_path(path, pathlib.Path(report.hub))
    if not path.is_dir():
        path.mkdir(parents=True, exist_ok=True)
        report.act("created", "directory", str(path.relative_to(report.hub)) + "/")


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------

def safe_workspace_path(path: pathlib.Path, hub: pathlib.Path) -> None:
    try:
        path.resolve().relative_to(hub.resolve())
    except ValueError:
        raise ToolError("workspace path escapes hub: {}".format(path))


def validate_identifier(value: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", value) or value in {".", ".."}:
        raise ToolError("context id must be a single directory identifier: {}".format(value))


def cmd_init(args: argparse.Namespace) -> Report:
    hub = pathlib.Path(args.hub).expanduser().resolve()
    for value in (args.opportunity, args.engagement):
        if value:
            validate_identifier(value)
    dirty_before = False
    if is_git_repo(hub) and git_available():
        code, status = git(hub, "status", "--porcelain")
        if code:
            raise ToolError("cannot inspect existing repository before initialization")
        dirty_before = bool(status.strip())
    hub.mkdir(parents=True, exist_ok=True)
    report = Report("init", hub)
    use_git = not args.no_git
    if use_git and not git_available():
        report.warn("GIT-MISSING", "git is not installed; the hub is created without version control")
        use_git = False

    manifest = load_manifest(hub)
    if manifest is None:
        if not args.client:
            raise ToolError("--client is required when the hub has no manifest")
        client_id = args.client_id or "client-{}".format(slug(args.client))
        manifest = new_manifest(args.client, client_id, list(args.alias or []), use_git)
        manifest["stores"]["local"]["syncedFilesystem"] = args.synced_filesystem
        write_manifest(hub, manifest)
        report.act("created", "manifest", MANIFEST)
    else:
        report.act("kept", "manifest exists", MANIFEST)
    if manifest.get("primaryStore") != "local":
        raise ToolError("workspace init requires the declared local primary store")
    local_root = pathlib.Path(manifest.get("stores", {}).get("local", {}).get("root", "."))
    if (hub / local_root).resolve() != hub:
        raise ToolError("run workspace init at the declared local root")
    client = manifest["client"]["canonicalName"]
    client_id = manifest["client"]["clientId"]
    values = {"client": client, "client_id": client_id, "today": today()}

    ensure_file(report, hub / "AGENTS.md", render_template("AGENTS.md", values))
    ensure_file(report, hub / "CLAUDE.md", render_template("CLAUDE.md", values))
    ensure_file(report, hub / "TODO.md", render_template("TODO.md", values))
    ensure_file(report, hub / "00-CLIENT.md", render_template("00-CLIENT.md", values))
    ensure_file(report, hub / "STANDARDS.md",
                (REFERENCES / "workspace-standards.md").read_text(encoding="utf-8"))
    ensure_file(report, hub / "METHODOLOGY.md",
                (REFERENCES / "pursuit-methodology.md").read_text(encoding="utf-8"))
    ensure_file(report, hub / ".gitignore",
                ".DS_Store\n.~lock.*\n*.tmp\n.hub-write-*\n")

    if args.opportunity:
        opp_id = args.opportunity
        name = args.opportunity_name or opp_id
        existing = [item for item in manifest.get("opportunities", []) if item["opportunityId"] == opp_id]
        if not existing:
            manifest.setdefault("opportunities", []).append(
                {"opportunityId": opp_id, "name": name, "status": "active"})
            write_manifest(hub, manifest)
            report.act("updated", "registered opportunity {}".format(opp_id), MANIFEST)
        context = hub / "opportunities" / opp_id
        values.update({"opportunity_id": opp_id, "opportunity_name": name})
        ensure_file(report, context / "00-OPPORTUNITY.md", render_template("00-OPPORTUNITY.md", values))
        for folder in ("inputs", "inputs/transcripts", "research", "synthesis", "evidence", "deliverables"):
            ensure_dir(report, context / folder)

    if args.engagement:
        engagement_id = args.engagement
        name = args.engagement_name or engagement_id
        existing = [item for item in manifest.get("engagements", []) if item["engagementId"] == engagement_id]
        if not existing:
            manifest.setdefault("engagements", []).append(
                {"engagementId": engagement_id, "name": name, "status": "active"})
            write_manifest(hub, manifest)
            report.act("updated", "registered engagement {}".format(engagement_id), MANIFEST)
        context = hub / "engagements" / engagement_id
        values.update({"engagement_id": engagement_id, "engagement_name": name})
        ensure_file(report, context / "00-ENGAGEMENT.md", render_template("00-ENGAGEMENT.md", values))
        for folder in ("inputs", "inputs/transcripts", "research", "synthesis", "evidence", "deliverables"):
            ensure_dir(report, context / folder)

    if use_git:
        if not is_git_repo(hub):
            git(hub, "init", "-q", check=True)
            report.act("created", "git repository", ".git/")
        if dirty_before:
            report.warn("GIT-DIRTY", "existing changes preserved; review and commit workspace changes explicitly")
            return report
        own_files = sorted({item["path"] for item in report.actions
                            if item["kind"] in {"created", "updated"} and item["path"]
                            and not item["path"].endswith("/")})
        if own_files:
            git(hub, "add", "--", *own_files, check=True)
        code, status = git(hub, "status", "--porcelain")
        if status.strip():
            message = "init: hub skeleton" if not args.opportunity else "init: workspace for {}".format(args.opportunity)
            code, out = git(hub, "commit", "-q", "-m", message)
            if code == 0:
                report.act("committed", message, "")
            else:
                report.warn("GIT-COMMIT", "skeleton staged but not committed: {}".format(out.strip().splitlines()[-1] if out.strip() else "unknown"))
        else:
            report.act("kept", "nothing to commit", ".git/")
    return report


# ---------------------------------------------------------------------------
# audit
# ---------------------------------------------------------------------------

def walk_all(hub: pathlib.Path):
    for root, dirs, files in os.walk(hub):
        for name in files:
            yield pathlib.Path(root) / name


def run_audit(hub: pathlib.Path, report: Report) -> Dict[str, List[str]]:
    facts: Dict[str, List[str]] = {"dangling": [], "gitConflictCopies": [], "missing": []}
    if not hub.is_dir():
        raise ToolError("hub root does not exist: {}".format(hub))

    manifest = load_manifest(hub)
    if manifest is None:
        report.block("MANIFEST-MISSING", "no {} at the hub root; run init".format(MANIFEST), MANIFEST)
    else:
        if manifest.get("primaryStore") not in {"local", "google-drive", "supplied-files"}:
            report.block("MANIFEST-STORE", "primaryStore is not a supported store", MANIFEST)
        if not (manifest.get("client") or {}).get("clientId"):
            report.block("MANIFEST-CLIENT", "client.clientId is missing", MANIFEST)

    for name in ("AGENTS.md", "CLAUDE.md"):
        if not (hub / name).exists():
            report.warn("INDEX-MISSING", "{} is missing; doctor restores it".format(name), name)
            facts["missing"].append(name)
    claude = hub / "CLAUDE.md"
    if claude.exists() and "@AGENTS.md" not in claude.read_text(encoding="utf-8"):
        report.warn("INDEX-POINTER", "CLAUDE.md does not point at AGENTS.md", "CLAUDE.md")

    for path in walk_all(hub):
        rel = str(path.relative_to(hub))
        if CONFLICT_COPY.search(path.name):
            if rel.startswith(".git" + os.sep):
                report.block("SYNC-CONFLICT-GIT", "Drive conflict copy inside .git; doctor removes it when identical", rel)
                facts["gitConflictCopies"].append(rel)
            else:
                report.warn("SYNC-CONFLICT", "Drive conflict copy; reconcile and delete", rel)
        elif LOCK_FILE.match(path.name):
            report.warn("LOCK-FILE", "office lock file left behind", rel)
    if (hub / ".git" / "index.lock").exists():
        report.warn("GIT-INDEX-LOCK", "index.lock present; another process, or a crashed one", ".git/index.lock")

    if is_git_repo(hub):
        if not git_available():
            report.warn("GIT-MISSING", "hub has .git but git is not installed; integrity not checked", ".git/")
        else:
            dangling, problems = dangling_commits(hub)
            for sha in dangling:
                report.block("GIT-DANGLING",
                             "commit {} is not on any branch (sync race); doctor reattaches it".format(sha[:7]), ".git/")
            facts["dangling"] = dangling
            for line in problems:
                report.block("GIT-FSCK", line, ".git/")
            for ref in recovered_refs(hub):
                report.warn("GIT-RECOVERED", "recovered branch {} awaits review and merge".format(ref), ".git/")
            age = last_commit_age_days(hub)
            if age is None:
                report.warn("GIT-EMPTY", "repository has no commits yet", ".git/")
            elif age > DORMANT_DAYS:
                agents = hub / "AGENTS.md"
                text = agents.read_text(encoding="utf-8") if agents.exists() else ""
                if not re.search(r"^## Dormancy\s*\n+(?!\S*A hub untouched)", text, re.M) or "outcome:" not in text.lower():
                    report.warn("DORMANT", "last commit {} days ago; record the outcome under Dormancy in AGENTS.md".format(age), "AGENTS.md")
    elif manifest and (manifest.get("stores", {}).get("local", {}).get("gitRepository")):
        report.block("GIT-DECLARED-MISSING", "manifest declares gitRepository but .git is absent", ".git/")
    return facts


def cmd_audit(args: argparse.Namespace) -> Report:
    hub = pathlib.Path(args.hub).expanduser().resolve()
    report = Report("audit", hub)
    run_audit(hub, report)
    return report


# ---------------------------------------------------------------------------
# doctor
# ---------------------------------------------------------------------------

def cmd_doctor(args: argparse.Namespace) -> Report:
    hub = pathlib.Path(args.hub).expanduser().resolve()
    first = Report("doctor", hub)
    facts = run_audit(hub, first)
    report = Report("doctor", hub)

    if facts["dangling"] and git_available():
        stamp = _dt.datetime.now(tz=_dt.timezone.utc).strftime("%Y%m%d")
        for sha in facts["dangling"]:
            ref = "refs/heads/recovered/{}-{}".format(stamp, sha[:7])
            code, out = git(hub, "update-ref", ref, sha)
            if code == 0:
                report.act("repaired", "dangling commit {} reattached as {}".format(sha[:7], ref[len("refs/heads/"):]), ".git/")
            else:
                report.block("GIT-RECOVER-FAILED", out.strip(), ".git/")

    for rel in facts["gitConflictCopies"]:
        copy = hub / rel
        original = copy.with_name(CONFLICT_COPY.sub(lambda m: m.group(1) or "", copy.name))
        if original.exists() and original.read_bytes() == copy.read_bytes():
            copy.unlink()
            report.act("repaired", "removed conflict copy identical to {}".format(original.name), rel)
        else:
            report.warn("SYNC-CONFLICT-GIT-KEPT", "conflict copy differs from original; resolve by hand", rel)

    manifest = load_manifest(hub)
    if manifest is not None:
        values = {"client": manifest["client"]["canonicalName"],
                  "client_id": manifest["client"]["clientId"], "today": today()}
        for name in facts["missing"]:
            (hub / name).write_text(render_template(name, values), encoding="utf-8")
            report.act("repaired", "restored from template", name)

    # Report the state after repair; the exit code is the post-repair truth.
    run_audit(hub, report)
    return report


# ---------------------------------------------------------------------------
# check
# ---------------------------------------------------------------------------

def parse_frontmatter(text: str) -> Optional[Dict[str, str]]:
    match = FRONTMATTER.match(text)
    if not match:
        return None
    fields: Dict[str, str] = {}
    for line in match.group(1).splitlines():
        if line.startswith((" ", "\t", "-")):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields


def working_area_files(hub: pathlib.Path) -> List[pathlib.Path]:
    found = []
    for root_name in CONTEXT_ROOTS:
        root = hub / root_name
        if not root.is_dir():
            continue
        for context in sorted(root.iterdir()):
            if not context.is_dir():
                continue
            for area in WORKING_AREAS:
                folder = context / area
                if folder.is_dir():
                    found.extend(sorted(p for p in folder.rglob("*.md") if p.is_file()))
    return found


def context_of(hub: pathlib.Path, path: pathlib.Path) -> Optional[pathlib.Path]:
    rel = path.relative_to(hub).parts
    if len(rel) >= 2 and rel[0] in CONTEXT_ROOTS:
        return hub / rel[0] / rel[1]
    return None


def read_ledger_lines(path: pathlib.Path, report: Report, rel: str) -> List[Dict]:
    events: List[Dict] = []
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            event = json.loads(raw)
        except ValueError:
            report.block("LEDGER-JSON", "line {} is not a JSON object".format(number), rel)
            continue
        if not isinstance(event, dict) or "event" not in event:
            report.block("LEDGER-EVENT", "line {} has no event field".format(number), rel)
            continue
        events.append(event)
    return events


def check_ledger(hub: pathlib.Path, ledger: pathlib.Path, report: Report) -> Tuple[set, set]:
    rel = str(ledger.relative_to(hub))
    events = read_ledger_lines(ledger, report, rel)
    claims = {e.get("claimId") for e in events if e.get("event") == "claim"}
    sources = {e.get("sourceId") for e in events if e.get("event") == "source"}
    if is_git_repo(hub) and git_available():
        before = committed_text(hub, rel)
        if before is not None:
            now = ledger.read_bytes()
            if not now.startswith(before):
                report.block("LEDGER-APPEND-ONLY",
                             "committed ledger lines were modified or removed; append a supersede line instead", rel)
    return claims, sources


def check_markdown(hub: pathlib.Path, path: pathlib.Path, report: Report,
                   claims: set, sources: set) -> None:
    rel = str(path.relative_to(hub))
    text = path.read_text(encoding="utf-8")
    if CONFLICT_COPY.search(path.name):
        report.block("SYNC-CONFLICT", "Drive conflict copy in a working area", rel)
    elif not KEBAB.match(path.name):
        report.block("FILENAME", "working-area filenames are kebab-case .md", rel)

    fields = parse_frontmatter(text)
    if fields is None:
        report.block("FRONTMATTER-MISSING", "no frontmatter block", rel)
    else:
        for key in REQUIRED_FRONTMATTER:
            if key not in fields:
                report.block("FRONTMATTER-FIELD", "frontmatter lacks {}".format(key), rel)
        if fields.get("status") and fields["status"] not in STATUS_VALUES:
            report.block("FRONTMATTER-STATUS", "status must be draft, in-review, or final", rel)
        if fields.get("updated") and not ISO_DATE.match(fields["updated"]):
            report.block("FRONTMATTER-DATE", "updated must be YYYY-MM-DD", rel)

    if FOREIGN_TAG.search(text):
        report.block("TAG-VOCABULARY",
                     "bracketed tag outside STATED, OBSERVED, INFERRED, DECIDED, ASSUMED", rel)
    if "[ASSUMED" in text and "## Assumptions to validate" not in text:
        report.block("ASSUMPTIONS-SECTION", "[ASSUMED] claims without an Assumptions to validate section", rel)
    for match in RELATIVE_DATE.finditer(text):
        report.warn("RELATIVE-DATE", "relative date {!r}; use an absolute date".format(match.group(0)), rel)
        break
    for ref in sorted(set(CLM_REF.findall(text))):
        if ref not in claims:
            report.block("CLM-UNRESOLVED", "{} has no claim event in the context ledger".format(ref), rel)
    for ref in sorted(set(SRC_REF.findall(text))):
        if ref not in sources:
            report.warn("SRC-UNRESOLVED", "{} has no source event in the context ledger".format(ref), rel)


def cmd_check(args: argparse.Namespace) -> Report:
    hub = pathlib.Path(args.hub).expanduser().resolve()
    report = Report("check", hub)
    if not hub.is_dir():
        raise ToolError("hub root does not exist: {}".format(hub))

    ledgers: Dict[pathlib.Path, Tuple[set, set]] = {}
    for root_name in CONTEXT_ROOTS:
        root = hub / root_name
        if not root.is_dir():
            continue
        for context in sorted(p for p in root.iterdir() if p.is_dir()):
            ledger = context / "evidence" / LEDGER_NAME
            if ledger.exists():
                ledgers[context] = check_ledger(hub, ledger, report)
            else:
                register = context / "evidence" / "source-register.md"
                ids = set(SRC_REF.findall(register.read_text(encoding="utf-8"))) if register.exists() else set()
                ledgers[context] = (set(), ids)

    if args.paths:
        targets = [pathlib.Path(p).expanduser().resolve() for p in args.paths]
        for target in targets:
            if not target.exists():
                raise ToolError("path does not exist: {}".format(target))
        files = []
        for target in targets:
            files.extend(sorted(target.rglob("*.md")) if target.is_dir() else [target])
        files = [f for f in files if f.suffix == ".md" and context_of(hub, f) is not None
                 and len(f.relative_to(hub).parts) > 3 and f.relative_to(hub).parts[2] in WORKING_AREAS]
    else:
        files = working_area_files(hub)

    for path in files:
        context = context_of(hub, path)
        claims, sources = ledgers.get(context, (set(), set()))
        check_markdown(hub, path, report, claims, sources)
    report.act("checked", "{} working-area files, {} ledgers".format(len(files), len(ledgers)), "")
    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="emit the report as JSON")
    sub = parser.add_subparsers(dest="verb", required=True)

    init = sub.add_parser("init", help="create or repair a hub and an optional opportunity workspace")
    init.add_argument("--hub", required=True, help="hub root, the AI Knowledge Hub folder")
    init.add_argument("--client", help="canonical client name (required for a new hub)")
    init.add_argument("--client-id", help="stable id, default client-<slug>")
    init.add_argument("--alias", action="append", help="client alias; repeatable")
    init.add_argument("--opportunity", help="opportunity id to create a pursuit workspace for")
    init.add_argument("--opportunity-name", help="display name for the opportunity")
    init.add_argument("--engagement", help="engagement id to create a delivery workspace for")
    init.add_argument("--engagement-name", help="display name for the engagement")
    init.add_argument("--synced-filesystem", action="store_true",
                      help="declare a newly created hub to be on a configured sync mount")
    init.add_argument("--no-git", action="store_true", help="do not initialize or commit a git repository")

    for verb in ("audit", "doctor"):
        p = sub.add_parser(verb)
        p.add_argument("--hub", required=True)

    check = sub.add_parser("check", help="gate working-area files and ledgers")
    check.add_argument("--hub", required=True)
    check.add_argument("paths", nargs="*", help="files or folders inside the hub; default is every working area")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handlers = {"init": cmd_init, "audit": cmd_audit, "doctor": cmd_doctor, "check": cmd_check}
    try:
        report = handlers[args.verb](args)
    except ToolError as exc:
        sys.stderr.write("error: {}\n".format(exc))
        return 2
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(report.render())
    return report.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())
