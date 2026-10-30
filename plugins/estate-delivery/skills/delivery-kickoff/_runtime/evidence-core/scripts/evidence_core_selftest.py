from __future__ import annotations

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
