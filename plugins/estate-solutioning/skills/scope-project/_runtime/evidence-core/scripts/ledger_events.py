#!/usr/bin/env python3
"""Check and project an append-only evidence ledger event log.

The event log is JSONL at `evidence/evidence-ledger.jsonl`: one JSON object per
line, never edited, only appended. It is the append-only authoring form supported by
the workspace standard. `project` turns it into the schema-valid document that
`evidence_core.py` evaluates, so the finalization gate is unchanged.

  check    LEDGER.jsonl                 validate every event; exit 1 on errors
  project  LEDGER.jsonl --output FILE   write the projected evidence-ledger.json

Exit codes: 0 clean or warnings, 1 blocking findings, 2 the tool could not run.
Standard library only. Python 3.9.

Event types and the inline tag mapping:

  context    first line; clientId, clientName, scopeType, contextId
  source     SRC-###: sourceType, title, authority, observedAt, locator
  claim      CLM-###: statement, tag, sourceIds, asOf, loadBearing, domains
             tag STATED or OBSERVED -> Confirmed when a supporting source has
             authority 70 or higher, otherwise Inferred (the authority model
             in evidence_core.py decides, not the tag); INFERRED -> Inferred;
             ASSUMED -> Unknown. DECIDED is not a claim; see register.
  supersede  claimId, by: the old claim projects as Superseded
  conflict   CNF-###: claimIds, materiality, status, description; open
             conflicts project their claims as Contested
  register   register (scope, estimate, decisions, risks, assumptions,
             stakeholders, timeline), itemId, claimIds, free fields
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import pathlib
import re
import sys
from typing import Dict, List, Optional, Tuple

TAG_STATUS = {"STATED": "Confirmed", "OBSERVED": "Confirmed", "INFERRED": "Inferred", "ASSUMED": "Unknown"}
CONFIRMED_AUTHORITY = 70
NON_EVIDENCE_TYPES = {"generated_artifact", "worked_example"}


def projected_status(tag: str, source_ids, sources: Dict[str, Dict]) -> str:
    """The status a tagged claim projects to, given its supporting sources.

    A STATED or OBSERVED claim is Confirmed only when at least one supporting
    source is evidence (not a generated artifact or worked example) with
    authority 70 or higher. Below that it is Inferred: the tag records how the
    claim was authored, the authority model decides what it can bear.
    """
    status = TAG_STATUS.get(tag, "Unknown")
    if status != "Confirmed":
        return status
    for sid in source_ids or []:
        source = sources.get(sid)
        if source and source.get("sourceType") not in NON_EVIDENCE_TYPES \
                and isinstance(source.get("authority"), int) and source["authority"] >= CONFIRMED_AUTHORITY:
            return "Confirmed"
    return "Inferred"
SOURCE_TYPES = {"executed_contract", "current_sow", "current_quote", "crm_record", "approved_design",
                "meeting_transcript", "client_document", "internal_model", "message",
                "generated_artifact", "worked_example", "other"}
REGISTERS = {"scope", "estimate", "decisions", "risks", "assumptions", "stakeholders", "timeline"}
MATERIALITY = {"load_bearing", "material", "minor"}
CONFLICT_STATUS = {"open", "resolved", "accepted_exception"}
SCOPE_TYPES = {"client", "opportunity", "engagement"}
SRC_ID = re.compile(r"^SRC-\d{3,}$")
CLM_ID = re.compile(r"^CLM-\d{3,}$")
CNF_ID = re.compile(r"^CNF-\d{3,}$")
CLIENT_ID = re.compile(r"^client-[a-z0-9][a-z0-9-]*$")
CLAIM_FIELDS = ("claimId", "statement", "status", "sourceIds", "asOf", "loadBearing", "domains",
                "confidenceRationale", "closureCondition", "owner")
SOURCE_FIELDS = ("sourceId", "sourceType", "title", "authority", "observedAt", "effectiveAt",
                 "supersedes", "locator", "notes")
CONFLICT_FIELDS = ("conflictId", "claimIds", "materiality", "status", "description",
                   "resolutionClaimId", "owner", "closureCondition")


class ToolError(Exception):
    pass


class Findings:
    def __init__(self) -> None:
        self.rows: List[Dict[str, object]] = []

    def error(self, code: str, message: str, line: int) -> None:
        self.rows.append({"level": "error", "code": code, "message": message, "line": line})

    def warn(self, code: str, message: str, line: int) -> None:
        self.rows.append({"level": "warning", "code": code, "message": message, "line": line})

    @property
    def errors(self) -> int:
        return sum(1 for r in self.rows if r["level"] == "error")


def read_events(path: pathlib.Path, findings: Findings) -> List[Tuple[int, Dict]]:
    if not path.exists():
        raise ToolError("ledger does not exist: {}".format(path))
    events: List[Tuple[int, Dict]] = []
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            event = json.loads(raw)
        except ValueError:
            findings.error("JSON", "line is not a JSON object", number)
            continue
        if not isinstance(event, dict) or not isinstance(event.get("event"), str):
            findings.error("EVENT", "line has no event field", number)
            continue
        events.append((number, event))
    return events


def _require(event: Dict, keys, findings: Findings, line: int, kind: str) -> bool:
    missing = [k for k in keys if k not in event]
    if missing:
        findings.error("REQUIRED", "{} event lacks {}".format(kind, ", ".join(missing)), line)
        return False
    return True


def validate(events: List[Tuple[int, Dict]], findings: Findings) -> None:
    claim_ids = {e.get("claimId") for _, e in events if e.get("event") == "claim"}
    source_rows = {e.get("sourceId"): e for _, e in events if e.get("event") == "source"}
    source_ids = set(source_rows)
    if not events or events[0][1].get("event") != "context":
        findings.error("CONTEXT-FIRST", "the first line must be a context event", events[0][0] if events else 0)
    for line, event in events:
        kind = event["event"]
        if kind == "context":
            if _require(event, ("clientId", "clientName", "scopeType", "contextId"), findings, line, kind):
                if not CLIENT_ID.match(str(event["clientId"])):
                    findings.error("CONTEXT-CLIENT", "clientId must look like client-<slug>", line)
                if event["scopeType"] not in SCOPE_TYPES:
                    findings.error("CONTEXT-SCOPE", "scopeType must be client, opportunity, or engagement", line)
        elif kind == "source":
            if _require(event, ("sourceId", "sourceType", "title", "authority", "observedAt", "locator"), findings, line, kind):
                if not SRC_ID.match(str(event["sourceId"])):
                    findings.error("SOURCE-ID", "sourceId must be SRC-### with three or more digits", line)
                if event["sourceType"] not in SOURCE_TYPES:
                    findings.error("SOURCE-TYPE", "unknown sourceType {!r}".format(event["sourceType"]), line)
                if not isinstance(event["authority"], int) or not 0 <= event["authority"] <= 100:
                    findings.error("SOURCE-AUTHORITY", "authority must be an integer from 0 to 100", line)
                for old in event.get("supersedes", []):
                    if old not in source_ids:
                        findings.error("SOURCE-SUPERSEDES", "supersedes unknown source {}".format(old), line)
        elif kind == "claim":
            if _require(event, ("claimId", "statement", "tag", "sourceIds", "asOf", "loadBearing", "domains"), findings, line, kind):
                if not CLM_ID.match(str(event["claimId"])):
                    findings.error("CLAIM-ID", "claimId must be CLM-### with three or more digits", line)
                tag = event["tag"]
                if tag == "DECIDED":
                    findings.error("DECIDED-IS-NOT-A-CLAIM",
                                   "a decision is a register event in decisions; tagging it as a claim launders judgment into evidence", line)
                elif tag not in TAG_STATUS:
                    findings.error("TAG", "unknown tag {!r}; use STATED, OBSERVED, INFERRED, or ASSUMED".format(tag), line)
                else:
                    expected = projected_status(tag, event["sourceIds"], source_rows)
                    if "status" in event and event["status"] != expected:
                        findings.error("TAG-STATUS", "tag {} projects to {}, not {}".format(tag, expected, event["status"]), line)
                    if expected == "Inferred" and TAG_STATUS[tag] == "Confirmed":
                        findings.warn("TAG-AUTHORITY",
                                      "{} claim has no supporting source with authority {} or higher; it projects to Inferred".format(
                                          tag, CONFIRMED_AUTHORITY), line)
                    if tag != "ASSUMED" and not event["sourceIds"]:
                        findings.error("CLAIM-UNSOURCED", "a {} claim names at least one source".format(tag), line)
                    if tag == "ASSUMED" and event["loadBearing"]:
                        for key in ("owner", "closureCondition"):
                            if not event.get(key):
                                findings.error("ASSUMED-LOAD-BEARING", "a load-bearing ASSUMED claim needs {}".format(key), line)
                for sid in event["sourceIds"]:
                    if sid not in source_ids:
                        findings.error("CLAIM-SOURCE", "unknown source {}".format(sid), line)
                if not isinstance(event["domains"], list) or not event["domains"]:
                    findings.error("CLAIM-DOMAIN", "domains must be a non-empty list", line)
                if not isinstance(event["loadBearing"], bool):
                    findings.error("CLAIM-LOAD-BEARING", "loadBearing must be true or false", line)
        elif kind == "supersede":
            if _require(event, ("claimId", "by", "asOf"), findings, line, kind):
                for key in ("claimId", "by"):
                    if event[key] not in claim_ids:
                        findings.error("SUPERSEDE-UNKNOWN", "{} names unknown claim {}".format(key, event[key]), line)
                if event.get("claimId") == event.get("by"):
                    findings.error("SUPERSEDE-SELF", "a claim cannot supersede itself", line)
        elif kind == "conflict":
            if _require(event, ("conflictId", "claimIds", "materiality", "status", "description"), findings, line, kind):
                if not CNF_ID.match(str(event["conflictId"])):
                    findings.error("CONFLICT-ID", "conflictId must be CNF-###", line)
                if len(event["claimIds"]) < 2:
                    findings.error("CONFLICT-CARDINALITY", "a conflict names at least two claims", line)
                for cid in event["claimIds"]:
                    if cid not in claim_ids:
                        findings.error("CONFLICT-CLAIM", "unknown claim {}".format(cid), line)
                if event["materiality"] not in MATERIALITY:
                    findings.error("CONFLICT-MATERIALITY", "materiality must be load_bearing, material, or minor", line)
                if event["status"] not in CONFLICT_STATUS:
                    findings.error("CONFLICT-STATUS", "status must be open, resolved, or accepted_exception", line)
                if event["status"] == "resolved" and not event.get("resolutionClaimId"):
                    findings.error("CONFLICT-RESOLUTION", "a resolved conflict names its resolution claim", line)
                if event["status"] == "open" and event["materiality"] != "minor":
                    for key in ("owner", "closureCondition"):
                        if not event.get(key):
                            findings.error("CONFLICT-OPEN", "an open {} conflict needs {}".format(event["materiality"], key), line)
        elif kind == "register":
            if _require(event, ("register", "itemId", "claimIds"), findings, line, kind):
                if event["register"] not in REGISTERS:
                    findings.error("REGISTER", "unknown register {!r}".format(event["register"]), line)
                for cid in event["claimIds"]:
                    if cid not in claim_ids:
                        findings.error("REGISTER-CLAIM", "unknown claim {}".format(cid), line)
                if event["register"] == "decisions":
                    for key in ("decidedBy", "decidedOn"):
                        if not event.get(key):
                            findings.error("DECISION-FIELD", "a decision row needs {}".format(key), line)
                if event["register"] == "assumptions":
                    if not event.get("ifFalse"):
                        findings.error("ASSUMPTION-IF-FALSE", "an assumption row states what breaks if it is false", line)
                    if not isinstance(event.get("communicate"), bool):
                        findings.error("ASSUMPTION-COMMUNICATE", "an assumption row says communicate true or false", line)
        else:
            findings.error("EVENT-KIND", "unknown event kind {!r}".format(kind), line)


def _latest(iterable):
    return _dt.datetime.max if not iterable else max(iterable)


def project(events: List[Tuple[int, Dict]], as_of: Optional[str] = None) -> Dict:
    context = None
    sources: Dict[str, Dict] = {}
    claims: Dict[str, Dict] = {}
    conflicts: Dict[str, Dict] = {}
    registers: Dict[str, Dict[str, Dict]] = {}
    superseded: Dict[str, Dict] = {}
    stamps: List[str] = []
    for _, event in events:
        kind = event["event"]
        for key in ("asOf", "observedAt", "recordedAt"):
            if isinstance(event.get(key), str):
                stamps.append(event[key])
        if kind == "context":
            context = {
                "clientId": event["clientId"], "clientName": event["clientName"],
                "scopeType": event["scopeType"], "contextId": event["contextId"],
                "opportunityId": event.get("opportunityId"),
                "engagementId": event.get("engagementId"),
                "contractId": event.get("contractId"),
            }
        elif kind == "source":
            row = {k: event.get(k) for k in SOURCE_FIELDS if k in event or k in ("effectiveAt", "supersedes", "notes")}
            row["supersedes"] = list(event.get("supersedes", []))
            sources[event["sourceId"]] = row
        elif kind == "claim":
            row = {k: event.get(k) for k in CLAIM_FIELDS}
            row["status"] = projected_status(event.get("tag"), event.get("sourceIds"), sources)
            claims[event["claimId"]] = row
        elif kind == "supersede":
            superseded[event["claimId"]] = event
        elif kind == "conflict":
            conflicts[event["conflictId"]] = {k: event.get(k) for k in CONFLICT_FIELDS}
        elif kind == "register":
            item = {k: v for k, v in event.items() if k not in ("event", "register")}
            registers.setdefault(event["register"], {})[event["itemId"]] = item

    for claim_id, event in superseded.items():
        if claim_id in claims:
            claims[claim_id]["status"] = "Superseded"
            note = "Superseded by {} on {}".format(event["by"], event["asOf"])
            claims[claim_id]["confidenceRationale"] = (
                "{}. {}".format(claims[claim_id]["confidenceRationale"], note)
                if claims[claim_id].get("confidenceRationale") else note)
    for conflict in conflicts.values():
        if conflict["status"] != "open":
            continue
        for claim_id in conflict["claimIds"]:
            claim = claims.get(claim_id)
            if claim and claim["status"] != "Superseded":
                claim["status"] = "Contested"
                claim["owner"] = claim.get("owner") or conflict.get("owner")
                claim["closureCondition"] = claim.get("closureCondition") or conflict.get("closureCondition")

    document = {
        "ledgerVersion": "2.0",
        "asOf": as_of or (max(stamps) if stamps else _dt.datetime.now(tz=_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")),
        "context": context,
        "sources": [sources[k] for k in sorted(sources)],
        "claims": [claims[k] for k in sorted(claims)],
        "conflicts": [conflicts[k] for k in sorted(conflicts)],
        "coverage": [],
    }
    if registers:
        document["registers"] = {name: [items[k] for k in sorted(items)] for name, items in sorted(registers.items())}
    return document


def render(findings: Findings, path: pathlib.Path) -> str:
    lines = ["ledger check {}".format(path)]
    for row in findings.rows:
        lines.append("  {:<8} line {:<4} {} {}".format(row["level"].upper(), row["line"], row["code"], row["message"]))
    lines.append("  {} errors, {} warnings".format(findings.errors, len(findings.rows) - findings.errors))
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true")
    sub = parser.add_subparsers(dest="verb", required=True)
    check = sub.add_parser("check")
    check.add_argument("ledger", type=pathlib.Path)
    proj = sub.add_parser("project")
    proj.add_argument("ledger", type=pathlib.Path)
    proj.add_argument("--output", type=pathlib.Path, required=True)
    proj.add_argument("--as-of", help="ISO 8601 timestamp for the projected document")
    args = parser.parse_args(argv)

    findings = Findings()
    try:
        events = read_events(args.ledger, findings)
    except ToolError as exc:
        sys.stderr.write("error: {}\n".format(exc))
        return 2
    validate(events, findings)
    if args.verb == "check":
        if args.json:
            print(json.dumps({"ledger": str(args.ledger), "errors": findings.errors, "findings": findings.rows}, indent=2))
        else:
            print(render(findings, args.ledger))
        return 1 if findings.errors else 0
    if findings.errors:
        print(render(findings, args.ledger))
        sys.stderr.write("error: refusing to project a ledger with errors\n")
        return 1
    document = project(events, args.as_of)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print("projected {} events to {}".format(len(events), args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
