from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from evidence_core import SOURCE_AUTHORITY_CAPS, EvidenceCore  # noqa: E402

core = EvidenceCore(ROOT / "reference" / "artifact-registry.json")
cases = [
    ("rich-solution-ledger.json", "solution_brief", "Sufficient", "solution_brief"),
    ("sparse-solution-ledger.json", "solution_brief", "Insufficient", "readiness_gap_memo"),
    ("conflicting-solution-ledger.json", "solution_brief", "Insufficient", "readiness_gap_memo"),
    ("stale-rom-ledger.json", "rom", "Insufficient", "readiness_gap_memo"),
]
failed = False
for filename, artifact_type, status, output in cases:
    ledger = json.loads((ROOT / "fixtures" / filename).read_text(encoding="utf-8"))
    result = core.evaluate(ledger, artifact_type)
    passed = result.status == status and result.outputArtifactType == output
    failed = failed or not passed
    print(f"{filename}: observed={result.status}/{result.outputArtifactType} expected={status}/{output} pass={passed}")

# Discovery synthesis: one interview passes when every claim gives its source
# location and the single-source limit is stated as a gap.
synthesis = json.loads((ROOT / "fixtures" / "discovery-synthesis-ledger.json").read_text(encoding="utf-8"))


def synthesis_case(label: str, ledger: dict, status: str) -> None:
    global failed
    result = core.evaluate(ledger, "discovery_synthesis")
    passed = result.status == status and not result.findings
    failed = failed or not passed
    print(f"discovery-synthesis {label}: observed={result.status} expected={status} pass={passed}")


synthesis_case("single interview, limit stated", synthesis, "Sufficient")

unstated = copy.deepcopy(synthesis)
unstated["claims"] = [c for c in unstated["claims"] if c.get("gapKind") != "single_source"]
synthesis_case("single interview, limit unstated", unstated, "Insufficient")

unlocated = copy.deepcopy(synthesis)
unlocated["claims"][0].pop("sourceLocations")
synthesis_case("finding without source location", unlocated, "Insufficient")

open_gap = copy.deepcopy(synthesis)
open_gap["claims"][4]["closureCondition"] = None
synthesis_case("open question without closure", open_gap, "Insufficient")

corroborated = copy.deepcopy(synthesis)
corroborated["claims"][5].update({
    "statement": "Neither interview covered what the bakery would pay for an ordering tool.",
    "status": "Unknown", "sourceIds": [], "sourceLocations": [], "gapKind": None,
    "closureCondition": "Ask about budget in the next owner interview."})
corroborated["sources"].append({**corroborated["sources"][0], "sourceId": "SRC-002",
                                "title": "Discovery interview with a delivery driver",
                                "locator": "fixture://discovery-synthesis/driver-interview",
                                "interviewees": ["delivery driver"]})
corroborated["claims"][1]["sourceIds"].append("SRC-002")
corroborated["claims"][1]["sourceLocations"].append({"sourceId": "SRC-002", "location": "00:02:10"})
synthesis_case("two interviewees, no limit needed", corroborated, "Sufficient")

# Conditional coverage: a load-bearing Unknown or Contested claim, or a
# load-bearing open conflict, leaves its domains Conditional when it has an
# owner, a closure condition, affected domains and a stop rule. Missing any one
# keeps it a blocker, and the gate routes to the readiness memo.
FOUR = ("owner", "closureCondition", "affectedDomains", "stopRule")


def gate_case(label: str, ledger: dict, artifact_type: str, status: str, output: str, check=None) -> None:
    global failed
    result = core.evaluate(ledger, artifact_type)
    passed = result.status == status and result.outputArtifactType == output and (check is None or check(result))
    failed = failed or not passed
    print(f"{label}: observed={result.status}/{result.outputArtifactType} expected={status}/{output} pass={passed}")


def listed(entries, key: str, item_id: str, missing=None) -> bool:
    return any(entry.get(key) == item_id and (missing is None or missing in entry.get("missingConditions", []))
               for entry in entries)


# The fictional bakery till rollout from issue 140: the unknown till count is
# carried as the install item's high bound, with an owner, a closure condition
# and a stop rule.
bakery = json.loads((ROOT / "fixtures" / "bakery-rom-conditional-ledger.json").read_text(encoding="utf-8"))
gate_case("bakery rom, unknown till count with all four conditions", bakery, "rom", "Conditional", "rom",
          lambda r: not r.blockers and not r.findings and listed(r.openItems, "claimId", "CLM-008")
          and r.domainCoverage["workstream effort"] == "Conditional")

for name in FOUR:
    if name == "affectedDomains":
        continue  # a claim's affected domains are its required `domains`; the conflict cases cover this one
    for blank in (None, "", "  "):
        case = copy.deepcopy(bakery)
        case["claims"][7][name] = blank
        gate_case(f"bakery rom, claim {name}={blank!r}", case, "rom", "Insufficient", "readiness_gap_memo",
                  lambda r, n=name: listed(r.blockers, "claimId", "CLM-008", n) and not r.openItems)

# The issue's reproduction as filed had an owner and a closure condition but no
# stop rule; that remains a blocker, and the blocker says what is missing.
as_filed = copy.deepcopy(bakery)
as_filed["claims"][7].pop("stopRule")
gate_case("bakery rom as filed, no stop rule", as_filed, "rom", "Insufficient", "readiness_gap_memo",
          lambda r: listed(r.blockers, "claimId", "CLM-008", "stopRule"))

# The ledger validator's errors do not change: an open item without an owner
# still raises LOAD_BEARING_OWNER, and one without a closure condition still
# raises LOAD_BEARING_CLOSURE. A missing stop rule adds no validator error.
codes = {}
for name in ("owner", "closureCondition", "stopRule"):
    case = copy.deepcopy(bakery)
    case["claims"][7].pop(name)
    codes[name] = sorted(f.code for f in core.validate_ledger(case))
validator_passed = codes == {"owner": ["LOAD_BEARING_OWNER"], "closureCondition": ["LOAD_BEARING_CLOSURE"], "stopRule": []}
failed = failed or not validator_passed
print(f"validator errors unchanged: observed={codes} pass={validator_passed}")

# A claim that names no domain is a validator error, so it never passes as Conditional.
nameless = copy.deepcopy(bakery)
nameless["claims"][7]["domains"] = []
gate_case("bakery rom, claim with no affected domains", nameless, "rom", "Insufficient", "readiness_gap_memo",
          lambda r: any(f.code == "CLAIM_DOMAIN" for f in r.findings))

conflict = {
    "conflictId": "CNF-001", "claimIds": ["CLM-002", "CLM-006"], "materiality": "load_bearing", "status": "open",
    "description": "The effort model and the operations team disagree on the hours per till.",
    "resolutionClaimId": None, "owner": "ops lead", "closureCondition": "time one install in a pilot store",
    "affectedDomains": ["workstream effort", "range reopeners"],
    "stopRule": "Do not narrow the install range until a pilot install is timed.",
}
conflicted = copy.deepcopy(bakery)
conflicted["conflicts"] = [conflict]
gate_case("bakery rom, open conflict with all four conditions", conflicted, "rom", "Conditional", "rom",
          lambda r: not r.blockers and listed(r.openItems, "conflictId", "CNF-001"))
for name in FOUR:
    for blank in (None, [] if name == "affectedDomains" else "  "):
        case = copy.deepcopy(conflicted)
        case["conflicts"][0][name] = blank
        gate_case(f"bakery rom, conflict {name}={blank!r}", case, "rom", "Insufficient", "readiness_gap_memo",
                  lambda r, n=name: listed(r.blockers, "conflictId", "CNF-001", n))

business_case = json.loads((ROOT / "fixtures" / "business-case-conditional-ledger.json").read_text(encoding="utf-8"))
gate_case("business case, unpriced investment item with all four conditions", business_case, "business_case",
          "Conditional", "business_case",
          lambda r: not r.blockers and listed(r.openItems, "claimId", "CLM-009")
          and r.domainCoverage["investment"] == "Conditional")
unruled = copy.deepcopy(business_case)
unruled["claims"][8]["stopRule"] = None
gate_case("business case, unpriced item without a stop rule", unruled, "business_case",
          "Insufficient", "readiness_gap_memo", lambda r: listed(r.blockers, "claimId", "CLM-009", "stopRule"))


def contract_ledger(artifact_type: str) -> dict:
    """A synthetic ledger that covers every required domain, plus one open item in the first."""
    domains = core.contracts[artifact_type]["requiredDomains"]
    source = {"sourceType": "meeting_transcript", "authority": 70, "observedAt": "2026-11-18T12:00:00Z",
              "effectiveAt": None, "supersedes": [], "notes": None}
    claims = [{"claimId": f"CLM-{index:03d}", "statement": f"Synthetic statement for {domain}.", "status": "Confirmed",
               "sourceIds": ["SRC-001"], "sourceLocations": [{"sourceId": "SRC-001", "location": f"00:0{index % 10}:00"}],
               "asOf": "2026-11-18T12:00:00Z", "loadBearing": True, "domains": [domain],
               "confidenceRationale": None, "closureCondition": None, "owner": None}
              for index, domain in enumerate(domains, start=1)]
    claims.append({"claimId": "CLM-900", "statement": f"One open item in {domains[0]}.", "status": "Unknown",
                   "sourceIds": [], "sourceLocations": [], "asOf": "2026-11-18T12:00:00Z", "loadBearing": True,
                   "domains": [domains[0]], "confidenceRationale": None, "owner": "synthetic owner",
                   "closureCondition": "synthetic closing step", "stopRule": "Hold the dependent work until it closes."})
    return {"ledgerVersion": "0.1.0", "asOf": "2026-11-18T12:00:00Z",
            "context": {"clientId": "client-synthetic", "clientName": "Synthetic client", "scopeType": "opportunity",
                        "contextId": "opp-synthetic"},
            "sources": [{**source, "sourceId": "SRC-001", "title": "First synthetic session", "locator": "fixture://one",
                         "interviewees": ["first person"]},
                        {**source, "sourceId": "SRC-002", "title": "Second synthetic session", "locator": "fixture://two",
                         "interviewees": ["second person"]}],
            "claims": claims, "conflicts": [], "coverage": []}


# Every contract routes the same way: Conditional allows the full artifact with
# the open item listed, and Insufficient produces the readiness memo.
for artifact_type in core.contracts:
    ledger = contract_ledger(artifact_type)
    ledger["claims"][0]["sourceIds"].append("SRC-002")
    ledger["claims"][0]["sourceLocations"].append({"sourceId": "SRC-002", "location": "00:01:00"})
    gate_case(f"{artifact_type} contract, conditional open item", ledger, artifact_type, "Conditional", artifact_type,
              lambda r: listed(r.openItems, "claimId", "CLM-900") and not r.terminal)
    ledger["claims"][-1]["stopRule"] = None
    gate_case(f"{artifact_type} contract, open item without a stop rule", ledger, artifact_type, "Insufficient",
              "readiness_gap_memo", lambda r: r.terminal and r.conclusionForce == "stop")

# Issue 161: a rate card or commercial policy is its own source type, capped at
# 85. The fictional Riverbend Library (synthetic) Deal Desk ledger carries its
# margin floor from a commercial_policy source; a type outside the table or a
# score above the cap still fails.
riverbend = contract_ledger("deal_desk")
riverbend["context"]["clientName"] = "Riverbend Library (synthetic)"
riverbend["sources"][0].update(sourceType="commercial_policy", authority=85, title="Rate card (synthetic)")
policy_ok = core.evaluate(riverbend, "deal_desk")
policy_codes = [item.code for item in core.validate_ledger(riverbend)]
policy_passed = (policy_ok.status == "Conditional" and "SOURCE_TYPE" not in policy_codes
                 and SOURCE_AUTHORITY_CAPS.get("commercial_policy") == 85)
failed = failed or not policy_passed
print(f"commercial_policy source type accepted for deal_desk: observed={policy_ok.status} pass={policy_passed}")
riverbend["sources"][0]["authority"] = 90
capped = [item.code for item in core.validate_ledger(riverbend)]
capped_passed = "SOURCE_AUTHORITY_CAP" in capped
failed = failed or not capped_passed
print(f"commercial_policy authority above 85 is capped: pass={capped_passed}")
schema_types = json.loads((ROOT / "schemas" / "evidence-ledger.schema.json").read_text(encoding="utf-8"))["$defs"]["source"]["properties"]["sourceType"]["enum"]
import ledger_events  # noqa: E402
types_passed = ("commercial_policy" in schema_types and "commercial_policy" in ledger_events.SOURCE_TYPES
                and set(schema_types) == set(SOURCE_AUTHORITY_CAPS) == ledger_events.SOURCE_TYPES)
failed = failed or not types_passed
print(f"source type lists agree across core, schema and ledger_events: pass={types_passed}")

# The command line exits 0 for a Conditional result and 1 for the readiness memo.
import subprocess  # noqa: E402
import tempfile  # noqa: E402

with tempfile.TemporaryDirectory() as directory:
    filed = Path(directory) / "as-filed.json"
    filed.write_text(json.dumps(as_filed), encoding="utf-8")
    exits = [subprocess.run([sys.executable, str(HERE / "evidence_core.py"), str(path), "rom"],
                            capture_output=True, text=True).returncode
             for path in (ROOT / "fixtures" / "bakery-rom-conditional-ledger.json", filed)]
cli_passed = exits == [0, 1]
failed = failed or not cli_passed
print(f"command line exit codes conditional/insufficient: observed={exits} pass={cli_passed}")

opportunity = json.loads((ROOT / "fixtures" / "rich-solution-ledger.json").read_text(encoding="utf-8"))
opportunity.pop("engagement")
opportunity["context"] = {
    "clientId": "client-example",
    "clientName": "Example Manufacturing (synthetic)",
    "scopeType": "opportunity",
    "contextId": "opp-2026-example",
    "opportunityId": "opp-2026-example",
    "engagementId": None,
    "contractId": None,
}
context_findings = core.validate_ledger(opportunity)
context_passed = not [item for item in context_findings if item.code.startswith("CONTEXT") or item.code == "LEDGER_CONTEXT"]
failed = failed or not context_passed
print(f"opportunity-context: pass={context_passed}")
raise SystemExit(1 if failed else 0)
