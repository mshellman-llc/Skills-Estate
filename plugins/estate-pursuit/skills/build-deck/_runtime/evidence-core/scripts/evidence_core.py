from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SOURCE_AUTHORITY_CAPS = {
    "executed_contract": 100,
    "current_sow": 95,
    "current_quote": 90,
    "approved_design": 85,
    "commercial_policy": 85,
    "crm_record": 80,
    "client_document": 75,
    "meeting_transcript": 70,
    "internal_model": 55,
    "message": 50,
    "other": 40,
    "generated_artifact": 10,
    "worked_example": 0,
}

NON_EVIDENCE_TYPES = {"generated_artifact", "worked_example"}
COVERAGE_STATES = {"Sufficient", "Conditional", "Insufficient", "NotApplicable"}
CLAIM_STATES = {"Confirmed", "Inferred", "Unknown", "Contested", "Superseded"}


@dataclass
class Finding:
    level: str
    code: str
    message: str
    path: str | None = None


@dataclass
class GateResult:
    requestedArtifactType: str
    outputArtifactType: str
    status: str
    terminal: bool
    conclusionForce: str
    domainCoverage: dict[str, str]
    blockers: list[dict[str, Any]] = field(default_factory=list)
    openItems: list[dict[str, Any]] = field(default_factory=list)
    ownershipGaps: list[str] = field(default_factory=list)
    directionToRetain: list[str] = field(default_factory=list)
    nextGate: str = ""
    findings: list[Finding] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["findings"] = [asdict(item) for item in self.findings]
        return payload


class EvidenceCore:
    def __init__(self, registry_path: str | Path):
        registry = json.loads(Path(registry_path).read_text(encoding="utf-8"))
        self.contracts = {item["artifactType"]: item for item in registry["artifacts"]}

    @staticmethod
    def _index(items: Iterable[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
        return {item[key]: item for item in items}

    def validate_ledger(self, ledger: dict[str, Any]) -> list[Finding]:
        findings: list[Finding] = []
        required_top = {"ledgerVersion", "sources", "claims", "conflicts", "coverage", "asOf"}
        for name in sorted(required_top - set(ledger)):
            findings.append(Finding("error", "LEDGER_REQUIRED", f"Missing required field: {name}", name))

        if "context" not in ledger and "engagement" not in ledger:
            findings.append(Finding(
                "error", "LEDGER_CONTEXT",
                "Missing required context; legacy engagement metadata is accepted during migration",
                "context"))
        context = ledger.get("context")
        if context is not None:
            required_context = {"clientId", "clientName", "scopeType", "contextId"}
            for name in sorted(required_context - set(context)):
                findings.append(Finding(
                    "error", "CONTEXT_REQUIRED",
                    f"Missing required context field: {name}", f"context.{name}"))
            if context.get("scopeType") not in {"client", "opportunity", "engagement"}:
                findings.append(Finding(
                    "error", "CONTEXT_SCOPE", "Unknown evidence context scope",
                    "context.scopeType"))

        sources = ledger.get("sources", [])
        claims = ledger.get("claims", [])
        conflicts = ledger.get("conflicts", [])
        source_index = self._index(sources, "sourceId") if sources else {}
        claim_index = self._index(claims, "claimId") if claims else {}

        if len(source_index) != len(sources):
            findings.append(Finding("error", "SOURCE_ID_DUPLICATE", "Source IDs must be unique", "sources"))
        if len(claim_index) != len(claims):
            findings.append(Finding("error", "CLAIM_ID_DUPLICATE", "Claim IDs must be unique", "claims"))

        superseded_source_ids = {old_id for source in sources for old_id in source.get("supersedes", [])}

        for source in sources:
            sid = source.get("sourceId", "<missing>")
            stype = source.get("sourceType")
            authority = source.get("authority")
            if stype not in SOURCE_AUTHORITY_CAPS:
                findings.append(Finding("error", "SOURCE_TYPE", f"Unknown source type: {stype}", f"sources.{sid}.sourceType"))
                continue
            if not isinstance(authority, int) or not 0 <= authority <= 100:
                findings.append(Finding("error", "SOURCE_AUTHORITY", "Authority must be an integer from 0 to 100", f"sources.{sid}.authority"))
            elif authority > SOURCE_AUTHORITY_CAPS[stype]:
                findings.append(Finding("error", "SOURCE_AUTHORITY_CAP", f"{stype} authority cannot exceed {SOURCE_AUTHORITY_CAPS[stype]}", f"sources.{sid}.authority"))
            if stype in NON_EVIDENCE_TYPES and authority != 0:
                findings.append(Finding("error", "NON_EVIDENCE_AUTHORITY", f"{stype} must have authority 0", f"sources.{sid}.authority"))
            if not source.get("locator"):
                findings.append(Finding("error", "SOURCE_LOCATOR", "Every source needs a resolvable locator", f"sources.{sid}.locator"))
            missing_supersedes = [old_id for old_id in source.get("supersedes", []) if old_id not in source_index]
            if missing_supersedes:
                findings.append(Finding("error", "SOURCE_SUPERSEDES_MISSING", f"Source supersedes missing source IDs: {', '.join(missing_supersedes)}", f"sources.{sid}.supersedes"))

        for claim in claims:
            cid = claim.get("claimId", "<missing>")
            status = claim.get("status")
            if status not in CLAIM_STATES:
                findings.append(Finding("error", "CLAIM_STATUS", f"Unknown claim status: {status}", f"claims.{cid}.status"))
            source_ids = claim.get("sourceIds", [])
            missing = [sid for sid in source_ids if sid not in source_index]
            if missing:
                findings.append(Finding("error", "CLAIM_SOURCE_MISSING", f"Claim references missing sources: {', '.join(missing)}", f"claims.{cid}.sourceIds"))
            supporting = [source_index[sid] for sid in source_ids if sid in source_index]
            if status != "Superseded" and any(sid in superseded_source_ids for sid in source_ids):
                findings.append(Finding("error", "CLAIM_USES_SUPERSEDED_SOURCE", "A claim using a superseded source must be marked Superseded or re-sourced", f"claims.{cid}.sourceIds"))
            if status == "Confirmed":
                if not supporting:
                    findings.append(Finding("error", "CONFIRMED_WITHOUT_SOURCE", "Confirmed claims require evidence", f"claims.{cid}"))
                elif not any(src["sourceType"] not in NON_EVIDENCE_TYPES and src.get("authority", 0) >= 70 for src in supporting):
                    findings.append(Finding("error", "CONFIRMED_LOW_AUTHORITY", "Confirmed claims require at least one authoritative source with authority 70 or higher", f"claims.{cid}"))
            if supporting and all(src["sourceType"] in NON_EVIDENCE_TYPES for src in supporting):
                findings.append(Finding("error", "EXAMPLE_AS_EVIDENCE", "Generated artifacts and worked examples cannot support claims", f"claims.{cid}.sourceIds"))
            if claim.get("loadBearing") and status in {"Unknown", "Contested"}:
                if not claim.get("closureCondition"):
                    findings.append(Finding("error", "LOAD_BEARING_CLOSURE", "Load-bearing Unknown or Contested claims need a closure condition", f"claims.{cid}.closureCondition"))
                if not claim.get("owner"):
                    findings.append(Finding("error", "LOAD_BEARING_OWNER", "Load-bearing Unknown or Contested claims need an owner", f"claims.{cid}.owner"))
            if not claim.get("domains"):
                findings.append(Finding("error", "CLAIM_DOMAIN", "Every claim must map to at least one domain", f"claims.{cid}.domains"))
            for entry in claim.get("sourceLocations", []):
                if entry.get("sourceId") not in source_ids:
                    findings.append(Finding("error", "CLAIM_LOCATION_SOURCE", f"Source location names {entry.get('sourceId')}, which the claim does not cite", f"claims.{cid}.sourceLocations"))

        conflict_ids: set[str] = set()
        for conflict in conflicts:
            conflict_id = conflict.get("conflictId", "<missing>")
            if conflict_id in conflict_ids:
                findings.append(Finding("error", "CONFLICT_ID_DUPLICATE", "Conflict IDs must be unique", f"conflicts.{conflict_id}"))
            conflict_ids.add(conflict_id)
            refs = conflict.get("claimIds", [])
            missing = [cid for cid in refs if cid not in claim_index]
            if missing:
                findings.append(Finding("error", "CONFLICT_CLAIM_MISSING", f"Conflict references missing claims: {', '.join(missing)}", f"conflicts.{conflict_id}.claimIds"))
            if len(refs) < 2:
                findings.append(Finding("error", "CONFLICT_CARDINALITY", "A conflict must reference at least two claims", f"conflicts.{conflict_id}.claimIds"))
            if conflict.get("status") == "resolved" and not conflict.get("resolutionClaimId"):
                findings.append(Finding("error", "CONFLICT_RESOLUTION", "Resolved conflicts need a resolution claim", f"conflicts.{conflict_id}.resolutionClaimId"))

        for item in ledger.get("coverage", []):
            if item.get("status") not in COVERAGE_STATES:
                findings.append(Finding("error", "COVERAGE_STATUS", f"Unknown coverage status: {item.get('status')}", f"coverage.{item.get('domain', '<missing>')}"))
            missing = [cid for cid in item.get("requiredClaimIds", []) if cid not in claim_index]
            if missing:
                findings.append(Finding("error", "COVERAGE_CLAIM_MISSING", f"Coverage references missing claims: {', '.join(missing)}", f"coverage.{item.get('domain', '<missing>')}.requiredClaimIds"))

        return findings

    @staticmethod
    def _missing_conditions(item: dict[str, Any], affected_domains: Any) -> list[str]:
        """Name the conditional-coverage conditions an open load-bearing item lacks.

        An open item may leave its domain Conditional only when it has an owner,
        a closure condition, the domains it affects, and a stop rule that holds
        dependent work until it closes.
        """
        def stated(value: Any) -> bool:
            return isinstance(value, str) and bool(value.strip())

        missing = []
        if not stated(item.get("owner")):
            missing.append("owner")
        if not stated(item.get("closureCondition")):
            missing.append("closureCondition")
        if not (isinstance(affected_domains, list) and any(stated(name) for name in affected_domains)):
            missing.append("affectedDomains")
        if not stated(item.get("stopRule")):
            missing.append("stopRule")
        return missing

    @classmethod
    def _open_item(cls, domain: str, key: str, item: dict[str, Any], reason: Any,
                   affected_domains: Any) -> tuple[dict[str, Any], list[str]]:
        entry = {
            "domain": domain,
            key: item[key],
            "reason": reason,
            "owner": item.get("owner"),
            "closureCondition": item.get("closureCondition"),
            "affectedDomains": list(affected_domains) if isinstance(affected_domains, list) else [],
            "stopRule": item.get("stopRule"),
        }
        missing = cls._missing_conditions(item, affected_domains)
        if missing:
            entry["missingConditions"] = missing
        return entry, missing

    def _domain_status(
        self,
        domain: str,
        claims: list[dict[str, Any]],
        conflicts: list[dict[str, Any]],
        contract: dict[str, Any] | None = None,
        sources: dict[str, dict[str, Any]] | None = None,
    ) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
        """Return the domain's coverage, its blockers, and its conditional open items."""
        contract = contract or {}
        sources = sources or {}
        active = [c for c in claims if domain in c.get("domains", []) and c.get("status") != "Superseded"]
        blockers: list[dict[str, Any]] = []
        open_items: list[dict[str, Any]] = []
        if not active:
            return "Insufficient", [{"domain": domain, "reason": "No evidence-backed claim covers this required domain", "owner": None, "closureCondition": "Provide and validate authoritative evidence for this domain"}], []

        if domain in contract.get("executedDomains", []):
            # A hard fail of the contract: a claim that merely sits in this domain, such as
            # "the draft is not signed", is not an executed commitment. The executed flag
            # counts only when a source of type executed_contract stands behind the claim.
            def executed_backing(claim: dict[str, Any]) -> bool:
                return claim.get("status") == "Confirmed" and claim.get("executed") is True and any(
                    sources.get(sid, {}).get("sourceType") == "executed_contract" for sid in claim.get("sourceIds", []))

            if not any(executed_backing(c) for c in active):
                # Carry the owner, closure condition and stop rule the ledger already names.
                named = next((c for c in active if c.get("status") in {"Unknown", "Contested"} and c.get("owner")), None)
                blocker = {"domain": domain,
                           "reason": "No Confirmed claim marks an executed commitment (executed: true, backed by an executed_contract source)",
                           "owner": None,
                           "closureCondition": "Obtain the signed agreement and record it as a Confirmed claim with executed true, backed by an executed_contract source"}
                if named:
                    blocker.update(claimId=named["claimId"], owner=named["owner"],
                                   closureCondition=named.get("closureCondition") or blocker["closureCondition"])
                    if named.get("stopRule"):
                        blocker["stopRule"] = named["stopRule"]
                return "Insufficient", [blocker], []

        if contract.get("sourceLocationRequired"):
            for claim in active:
                located = {entry.get("sourceId") for entry in claim.get("sourceLocations", []) if entry.get("location")}
                unlocated = [sid for sid in claim.get("sourceIds", []) if sid not in located]
                if unlocated:
                    blockers.append({
                        "domain": domain,
                        "claimId": claim["claimId"],
                        "reason": f"{claim['claimId']} cites {', '.join(unlocated)} without a source location",
                        "owner": claim.get("owner"),
                        "closureCondition": "Record the timestamp, line, or section in the source that supports the claim",
                    })

        if domain in contract.get("gapDomains", []):
            # A gap domain is satisfied by named gaps: each open item states what would close it.
            for claim in active:
                if claim.get("status") in {"Unknown", "Contested"} and not claim.get("closureCondition"):
                    blockers.append({
                        "domain": domain,
                        "claimId": claim["claimId"],
                        "reason": f"{claim['claimId']} names a gap without a closure condition",
                        "owner": claim.get("owner"),
                        "closureCondition": "State the follow-up that would answer the open item",
                    })
            if blockers:
                return "Insufficient", blockers, []
            return ("Conditional" if any(c.get("status") == "Inferred" for c in active) else "Sufficient"), [], []

        # A load-bearing Unknown or Contested claim, or a load-bearing open
        # conflict, leaves the domain Conditional when it meets every
        # conditional-coverage condition, and blocks it otherwise. A claim's
        # affected domains are its `domains`; a conflict states `affectedDomains`.
        active_ids = {c["claimId"] for c in active}
        for claim in active:
            if claim.get("loadBearing") and claim.get("status") in {"Unknown", "Contested"}:
                entry, missing = self._open_item(domain, "claimId", claim, claim["statement"], claim.get("domains"))
                (blockers if missing else open_items).append(entry)

        for conflict in conflicts:
            if conflict.get("status") == "open" and conflict.get("materiality") == "load_bearing" and active_ids.intersection(conflict.get("claimIds", [])):
                entry, missing = self._open_item(domain, "conflictId", conflict, conflict.get("description"), conflict.get("affectedDomains"))
                (blockers if missing else open_items).append(entry)

        if blockers:
            return "Insufficient", blockers, open_items
        if open_items:
            return "Conditional", [], open_items
        if any(c.get("status") == "Inferred" for c in active):
            return "Conditional", [], []
        if any(c.get("status") == "Confirmed" for c in active):
            return "Sufficient", [], []
        return "Insufficient", [{"domain": domain, "reason": "Domain has no usable Confirmed or Inferred claim", "owner": None, "closureCondition": "Resolve claim status"}], []

    def evaluate(self, ledger: dict[str, Any], artifact_type: str) -> GateResult:
        if artifact_type not in self.contracts:
            raise ValueError(f"Unknown artifact contract: {artifact_type}")
        contract = self.contracts[artifact_type]
        findings = self.validate_ledger(ledger)
        claims = ledger.get("claims", [])
        conflicts = ledger.get("conflicts", [])
        domain_coverage: dict[str, str] = {}
        blockers: list[dict[str, Any]] = []
        open_items: list[dict[str, Any]] = []

        source_lookup = self._index(ledger.get("sources", []), "sourceId") if ledger.get("sources") else {}
        for domain in contract["requiredDomains"]:
            status, domain_blockers, domain_open_items = self._domain_status(domain, claims, conflicts, contract, source_lookup)
            domain_coverage[domain] = status
            blockers.extend(domain_blockers)
            open_items.extend(domain_open_items)

        limit_rule = contract.get("singleSourceLimit")
        if limit_rule:
            limit_blocker = self._single_source_blocker(ledger, contract, limit_rule)
            if limit_blocker:
                domain_coverage[limit_rule["gapDomain"]] = "Insufficient"
                blockers.append(limit_blocker)

        blockers = self._merge_by_item(blockers)
        open_items = self._merge_by_item(open_items)

        if any(item.level == "error" for item in findings):
            status = "Insufficient"
        elif any(value == "Insufficient" for value in domain_coverage.values()):
            status = "Insufficient"
        elif any(value == "Conditional" for value in domain_coverage.values()):
            status = "Conditional"
        else:
            status = "Sufficient"

        terminal = status == "Insufficient"
        output_type = "readiness_gap_memo" if terminal else artifact_type
        force = "stop" if terminal else "recommend"
        ownership_gaps = sorted({item["domain"] for item in blockers if not item.get("owner") and item.get("domain")})
        source_index = self._index(ledger.get("sources", []), "sourceId") if ledger.get("sources") else {}
        superseded_source_ids = {old_id for source in ledger.get("sources", []) for old_id in source.get("supersedes", [])}
        retained = []
        for claim in claims:
            if claim.get("status") != "Confirmed" or "decisions" not in claim.get("domains", []):
                continue
            supporting = [source_index[sid] for sid in claim.get("sourceIds", []) if sid in source_index and sid not in superseded_source_ids]
            if any(src.get("sourceType") not in NON_EVIDENCE_TYPES and src.get("authority", 0) >= 70 for src in supporting):
                retained.append(claim["statement"])
        if terminal:
            next_gate = "Close all load-bearing blockers and rerun the content-sufficiency gate"
        elif open_items:
            next_gate = ("Approve the artifact content model before rendering, list every open item in the artifact, "
                         "and hold the work each stop rule names until its closure condition is met")
        else:
            next_gate = "Approve the artifact content model before rendering"

        return GateResult(
            requestedArtifactType=artifact_type,
            outputArtifactType=output_type,
            status=status,
            terminal=terminal,
            conclusionForce=force,
            domainCoverage=domain_coverage,
            blockers=blockers,
            openItems=open_items,
            ownershipGaps=ownership_gaps,
            directionToRetain=retained,
            nextGate=next_gate,
            findings=findings,
        )

    @staticmethod
    def _merge_by_item(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Report each claim or conflict once, with every required domain it touches."""
        merged: dict[tuple[str, str], dict[str, Any]] = {}
        for entry in entries:
            if entry.get("conflictId"):
                key = ("conflict", entry["conflictId"])
            elif entry.get("claimId"):
                key = ("claim", entry["claimId"])
            else:
                key = ("reason", entry.get("reason", "Evidence blocker"))
            if key not in merged:
                merged[key] = {**entry, "domains": [entry.get("domain")] if entry.get("domain") else []}
            elif entry.get("domain") and entry.get("domain") not in merged[key]["domains"]:
                merged[key]["domains"].append(entry["domain"])
        result = []
        for entry in merged.values():
            entry["domains"] = sorted(entry.get("domains", []))
            entry["domain"] = ", ".join(entry["domains"])
            result.append(entry)
        return result

    def _single_source_blocker(
        self,
        ledger: dict[str, Any],
        contract: dict[str, Any],
        rule: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Require a stated limit when the evidence rests on one source or one interviewee."""
        domains = set(contract["requiredDomains"])
        source_index = self._index(ledger.get("sources", []), "sourceId") if ledger.get("sources") else {}
        cited: set[str] = set()
        for claim in ledger.get("claims", []):
            if claim.get("status") == "Superseded" or not domains.intersection(claim.get("domains", [])):
                continue
            cited.update(sid for sid in claim.get("sourceIds", [])
                         if sid in source_index and source_index[sid].get("sourceType") not in NON_EVIDENCE_TYPES)
        interviewees = {person for sid in cited for person in source_index[sid].get("interviewees", [])}
        single = len(cited) < rule.get("minIndependentSources", 2) or len(interviewees) == 1
        if not single:
            return None
        stated = any(
            claim.get("gapKind") == rule["gapKind"]
            and rule["gapDomain"] in claim.get("domains", [])
            and claim.get("status") != "Superseded"
            for claim in ledger.get("claims", [])
        )
        if stated:
            return None
        return {
            "domain": rule["gapDomain"],
            "reason": "The evidence rests on a single source or interviewee and the ledger does not state that limit as a gap",
            "owner": None,
            "closureCondition": f"Add a {rule['gapDomain']} claim with gapKind {rule['gapKind']} that states the limit and what further sessions would test it",
        }

    @staticmethod
    def validate_content_model(model: dict[str, Any]) -> list[Finding]:
        findings: list[Finding] = []
        sufficiency = model.get("sufficiency", {})
        conclusion = model.get("conclusion", {})
        if sufficiency.get("status") == "Insufficient":
            if model.get("artifactType") != "readiness_gap_memo":
                findings.append(Finding("error", "TERMINAL_ARTIFACT_TYPE", "Insufficient content must become readiness_gap_memo", "artifactType"))
            if sufficiency.get("terminal") is not True:
                findings.append(Finding("error", "TERMINAL_FLAG", "Insufficient content must be terminal", "sufficiency.terminal"))
            if conclusion.get("force") != "stop":
                findings.append(Finding("error", "TERMINAL_FORCE", "Insufficient content must use stop force", "conclusion.force"))
        if model.get("releaseStatus") in {"content_approved", "rendered", "parity_passed", "released"}:
            protected = {block.get("blockId") for block in model.get("blocks", []) if block.get("protectedMeaning")}
            mapped = {item.get("contentPath", "").split(".")[-1] for item in model.get("evidenceMap", [])}
            missing = protected - mapped
            if missing:
                findings.append(Finding("error", "PROTECTED_EVIDENCE_MAP", f"Protected blocks lack evidence mappings: {', '.join(sorted(missing))}", "evidenceMap"))
        return findings

    @staticmethod
    def validate_parity_manifest(manifest: dict[str, Any]) -> list[Finding]:
        findings: list[Finding] = []
        if manifest.get("releasePass"):
            checks = manifest.get("checks", {})
            for name in ("lexicalStructural", "semantic", "visual"):
                if checks.get(name) != "pass":
                    findings.append(Finding("error", "PARITY_RELEASE", f"releasePass requires {name}=pass", f"checks.{name}"))
        return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate an evidence ledger against an Estate artifact contract")
    parser.add_argument("ledger", type=Path)
    parser.add_argument("artifact_type")
    parser.add_argument("--registry", type=Path, default=Path(__file__).resolve().parents[1] / "reference" / "artifact-registry.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    core = EvidenceCore(args.registry)
    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    result = core.evaluate(ledger, args.artifact_type).to_dict()
    result["evaluatedAt"] = datetime.now(timezone.utc).isoformat()
    text = json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text)
    return 1 if result["terminal"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
