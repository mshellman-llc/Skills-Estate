from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from evidence_core import EvidenceCore  # noqa: E402

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
