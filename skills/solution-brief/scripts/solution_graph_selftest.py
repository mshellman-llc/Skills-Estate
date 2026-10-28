from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FIXTURES = ROOT / "fixtures"
sys.path.insert(0, str(HERE))
from solution_graph import GraphValidator  # noqa: E402

expectations = {
    "solution-graph-rich.json": (True, set()),
    "solution-graph-readiness.json": (True, set()),
    "solution-graph-invalid-dangling-edge.json": (False, {"DANGLING_EDGE"}),
    "solution-graph-invalid-missing-failure.json": (False, {"INTERFACE_FAILURE_BEHAVIOR"}),
    "solution-graph-invalid-orphan-scope.json": (False, {"ORPHAN_SCOPE_PRICE"}),
    "solution-graph-invalid-bad-allocation.json": (False, {"ALLOCATION_REF"}),
    "solution-graph-invalid-failed-reconciliation.json": (False, {"RECONCILIATION_FAIL"}),
    "solution-graph-invalid-generic-grammar.json": (False, {"GENERIC_CARD_GRAMMAR", "GRAMMAR_DIVERSITY"}),
    "solution-graph-invalid-build-contract-gap.json": (False, {"BUILD_INTERFACE_CONTRACT"}),
    "solution-graph-invalid-sparse-full.json": (False, {"RICH_FAMILY_MISSING", "RELATIONSHIPS_MISSING", "VIEW_REQUIRED"}),
    "solution-graph-field-guide.json": (True, set()),
    "solution-graph-invalid-fg-unearned-section.json": (False, {"SECTION_UNEARNED"}),
    "solution-graph-invalid-fg-unreached-loadbearing.json": (False, {"LOADBEARING_UNREACHED"}),
    "solution-graph-invalid-fg-hidden-blocker.json": (False, {"CONDITIONAL_BLOCKER_HIDDEN"}),
    "solution-graph-invalid-fg-unrecorded-section.json": (False, {"DISPOSITION_UNRECORDED"}),
    "solution-graph-invalid-fg-ledger-disposition.json": (False, {"LEDGER_DISPOSITION"}),
    "solution-graph-invalid-fg-undecided-section.json": (False, {"DISPOSITION_MISSING"}),
}

failed = False
for filename, (expected_pass, expected_codes) in expectations.items():
    graph = json.loads((FIXTURES / filename).read_text(encoding="utf-8"))
    report = GraphValidator(graph).run()
    observed_codes = {item["code"] for item in report["findings"] if item["level"] == "error"}
    passed = report["passed"] == expected_pass and expected_codes.issubset(observed_codes)
    failed = failed or not passed
    print(f"{filename}: pass={passed} validator={report['passed']} codes={sorted(observed_codes)}")
raise SystemExit(1 if failed else 0)
