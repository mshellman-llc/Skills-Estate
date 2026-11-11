from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

NODE_FAMILIES = {
    "systems": "SYS",
    "interfaces": "IFC",
    "adrs": "ADR",
    "scopeItems": "SCP",
    "risks": "RSK",
    "assumptions": "ASM",
    "dependencies": "DEP",
    "roles": "ROL",
    "allocations": "ALC",
    "phases": "PHS",
    "milestones": "MLS",
    "financialLines": "FIN",
    "reconciliationControls": "REC",
    "dataEntities": "ENT",
    "qaEntries": "QNA",
}

CANONICAL_VIEWS = {
    "technical_judgment",
    "system_boundary",
    "critical_interfaces",
    "architecture_decisions",
    "scope_solution_trace",
    "risk_concentration",
    "staffing_delivery_shape",
    "timeline_decision_gates",
    "financial_reconciliation",
    "conditions_next_action",
    "orientation",
    "end_to_end_flow",
    "data_model",
    "pricing_architecture",
    "stakeholder_qa",
    "sources_evidence",
}

# Outputs that assemble a full graph rather than stopping at the readiness memo.
FULL_OUTPUTS = {"solution_brief", "field_guide"}

# Sections a field guide is expected to consider. Every candidate needs a
# disposition record, so dropping one is a recorded decision rather than a silent
# absence. Staffing and financial reconciliation are absent on purpose: a field
# guide never staffs and never prices.
FIELD_GUIDE_CORE = {
    "orientation",
    "system_boundary",
    "end_to_end_flow",
    "data_model",
    "scope_solution_trace",
    "risk_concentration",
    "technical_judgment",
    "conditions_next_action",
    "sources_evidence",
}
FIELD_GUIDE_CONDITIONAL = {
    "pricing_architecture",
    "critical_interfaces",
    "architecture_decisions",
    "stakeholder_qa",
    "timeline_decision_gates",
}
FIELD_GUIDE_CANDIDATES = FIELD_GUIDE_CORE | FIELD_GUIDE_CONDITIONAL

# Minimum governed claim IDs behind a reader-facing field-guide section. Below the
# floor the section is unearned: omit it and record the reason. Do not lengthen it.
EVIDENCE_FLOOR_DEFAULT = 2
EVIDENCE_FLOOR = {
    "orientation": 1,
    "sources_evidence": 0,
    "stakeholder_qa": 3,
}

REQUIRED_VIEW_WHEN = {
    "technical_judgment": lambda n: True,
    "system_boundary": lambda n: bool(n["systems"] or n["scopeItems"]),
    "critical_interfaces": lambda n: bool(n["interfaces"]),
    "architecture_decisions": lambda n: bool(n["adrs"]),
    "scope_solution_trace": lambda n: bool(n["scopeItems"]),
    "risk_concentration": lambda n: bool(n["risks"] or n["assumptions"] or n["dependencies"]),
    "staffing_delivery_shape": lambda n: bool(n["roles"] or n["allocations"]),
    "timeline_decision_gates": lambda n: bool(n["phases"] or n["milestones"]),
    "financial_reconciliation": lambda n: bool(n["financialLines"] or n["reconciliationControls"]),
    "conditions_next_action": lambda n: True,
}

EDGE_COMPATIBILITY = {
    "owns_process": ({"SYS"}, {"SCP", "PHS"}),
    "owns_data": ({"SYS"}, {"SYS", "IFC", "SCP", "ENT"}),
    "connects_through": ({"SYS", "IFC"}, {"SYS", "IFC"}),
    "implements_scope": ({"SYS", "IFC", "ADR"}, {"SCP"}),
    "depends_on": ({"SYS", "IFC", "ADR", "SCP", "PHS", "ROL", "FIN"}, {"SYS", "IFC", "ADR", "ASM", "DEP", "MLS"}),
    "governs": ({"ADR"}, {"SYS", "IFC", "SCP", "RSK", "ASM", "DEP", "ROL", "PHS", "MLS", "FIN"}),
    "affects": ({"RSK"}, {"SYS", "IFC", "ADR", "SCP", "ROL", "ALC", "PHS", "MLS", "FIN"}),
    "requires_role": ({"SCP", "IFC", "PHS"}, {"ROL"}),
    "allocated_to": ({"ALC"}, {"ROL", "PHS", "SCP"}),
    "delivered_in": ({"SCP"}, {"PHS"}),
    "closes": ({"PHS", "MLS"}, {"ADR", "RSK", "ASM", "DEP"}),
    "blocks": ({"RSK", "ASM", "DEP"}, {"SCP", "PHS", "MLS", "IFC"}),
    "prices": ({"FIN"}, {"SCP", "ROL", "PHS"}),
    "conditions": ({"ASM", "DEP"}, {"SYS", "IFC", "ADR", "SCP", "ROL", "ALC", "PHS", "MLS", "FIN"}),
    "excludes": ({"SCP", "FIN"}, {"SCP", "FIN", "PHS"}),
    "supersedes": ({"ADR", "SCP", "FIN"}, {"ADR", "SCP", "FIN"}),
    "motivates": ({"RSK", "ASM", "DEP", "ADR"}, {"ADR", "SCP", "IFC", "PHS"}),
    "closes_pain": ({"SCP", "SYS", "IFC"}, {"SCP"}),
}


@dataclass
class Finding:
    level: str
    code: str
    message: str
    path: str | None = None


class GraphValidator:
    def __init__(self, graph: dict[str, Any]):
        self.graph = graph
        self.findings: list[Finding] = []
        self.nodes_by_id: dict[str, dict[str, Any]] = {}
        self.family_by_id: dict[str, str] = {}
        self.edges_by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)

    def add(self, level: str, code: str, message: str, path: str | None = None):
        self.findings.append(Finding(level, code, message, path))

    @staticmethod
    def prefix(node_id: str) -> str:
        return node_id.split("-", 1)[0] if "-" in node_id else ""

    def index_nodes(self):
        nodes = self.graph.get("nodes", {})
        for family, prefix in NODE_FAMILIES.items():
            items = nodes.get(family, [])
            if not isinstance(items, list):
                self.add("error", "NODE_FAMILY_TYPE", f"{family} must be an array", f"nodes.{family}")
                continue
            for idx, node in enumerate(items):
                node_id = node.get("id")
                path = f"nodes.{family}[{idx}]"
                if not node_id:
                    self.add("error", "NODE_ID_MISSING", "Node ID is required", path)
                    continue
                if node_id in self.nodes_by_id:
                    self.add("error", "NODE_ID_DUPLICATE", f"Duplicate node ID {node_id}", path)
                    continue
                if self.prefix(node_id) != prefix:
                    self.add("error", "NODE_ID_PREFIX", f"{node_id} must use {prefix}- prefix", f"{path}.id")
                self.nodes_by_id[node_id] = node
                self.family_by_id[node_id] = family

    def validate_top_level(self):
        required = {"graphVersion", "artifactType", "outputType", "mode", "engagement", "sufficiency", "nodes", "edges", "editorialViews", "referencedClaimIds"}
        for name in sorted(required - set(self.graph)):
            self.add("error", "TOP_LEVEL_REQUIRED", f"Missing required field {name}", name)
        if self.graph.get("artifactType") != "solution_brief":
            self.add("error", "ARTIFACT_TYPE", "artifactType must be solution_brief", "artifactType")
        output = self.graph.get("outputType")
        suff = self.graph.get("sufficiency", {})
        if suff.get("status") == "Insufficient":
            if output != "readiness_gap_memo" or self.graph.get("mode") != "readiness" or suff.get("terminal") is not True:
                self.add("error", "INSUFFICIENT_TERMINAL", "Insufficient must route to terminal readiness_gap_memo", "sufficiency")
        if output == "solution_brief":
            if suff.get("status") == "Insufficient" or suff.get("terminal") is not False:
                self.add("error", "FULL_AFTER_INSUFFICIENT", "Full Solution Brief cannot proceed from an Insufficient or terminal gate", "sufficiency")
            if not self.graph.get("technicalJudgment"):
                self.add("error", "TECHNICAL_JUDGMENT_REQUIRED", "Full Solution Brief requires a technical judgment", "technicalJudgment")
        if output == "field_guide":
            if suff.get("status") == "Insufficient" or suff.get("terminal") is not False:
                self.add("error", "FULL_AFTER_INSUFFICIENT", "Field guide cannot proceed from an Insufficient or terminal gate", "sufficiency")
            if self.graph.get("mode") != "field_guide":
                self.add("error", "FIELD_GUIDE_MODE", "Field guide output requires field_guide mode", "mode")
            if not self.graph.get("technicalJudgment"):
                self.add("error", "TECHNICAL_JUDGMENT_REQUIRED", "Field guide requires a technical judgment", "technicalJudgment")
            if self.graph.get("sectionDispositions") is None:
                self.add("error", "SECTION_DISPOSITIONS_REQUIRED", "Field guide requires a confirmed section-disposition record", "sectionDispositions")
        if output == "readiness_gap_memo":
            count = sum(len(self.graph.get("nodes", {}).get(family, [])) for family in NODE_FAMILIES)
            if count or self.graph.get("edges") or self.graph.get("editorialViews"):
                self.add("error", "READINESS_GRAPH_EXPANSION", "Terminal readiness output must stop before assembling the full solution graph", "nodes")

    def validate_claims(self):
        referenced = set(self.graph.get("referencedClaimIds", []))
        for node_id, node in self.nodes_by_id.items():
            claims = node.get("claimIds", [])
            if not claims:
                self.add("error", "NODE_EVIDENCE", f"Node {node_id} has no governed claim IDs", f"nodes.{self.family_by_id[node_id]}.{node_id}.claimIds")
            for claim_id in claims:
                if claim_id not in referenced:
                    self.add("error", "CLAIM_NOT_DECLARED", f"Node {node_id} references undeclared claim {claim_id}", node_id)
        for edge in self.graph.get("edges", []):
            claims = edge.get("claimIds", [])
            if edge.get("derivation") == "evidence" and not claims:
                self.add("error", "EDGE_EVIDENCE", f"Evidence edge {edge.get('edgeId')} needs claim IDs", f"edges.{edge.get('edgeId')}")
            for claim_id in claims:
                if claim_id not in referenced:
                    self.add("error", "CLAIM_NOT_DECLARED", f"Edge {edge.get('edgeId')} references undeclared claim {claim_id}", edge.get("edgeId"))

    def validate_edges(self):
        edge_ids = set()
        for idx, edge in enumerate(self.graph.get("edges", [])):
            edge_id = edge.get("edgeId")
            path = f"edges[{idx}]"
            if not edge_id:
                self.add("error", "EDGE_ID_MISSING", "Edge ID is required", path)
                continue
            if edge_id in edge_ids:
                self.add("error", "EDGE_ID_DUPLICATE", f"Duplicate edge ID {edge_id}", path)
            edge_ids.add(edge_id)
            source, target = edge.get("from"), edge.get("to")
            if source not in self.nodes_by_id:
                self.add("error", "DANGLING_EDGE", f"Edge {edge_id} source {source} does not exist", f"{path}.from")
            if target not in self.nodes_by_id:
                self.add("error", "DANGLING_EDGE", f"Edge {edge_id} target {target} does not exist", f"{path}.to")
            if source in self.nodes_by_id and target in self.nodes_by_id:
                compatibility = EDGE_COMPATIBILITY.get(edge.get("type"))
                if not compatibility:
                    self.add("error", "EDGE_TYPE", f"Unsupported edge type {edge.get('type')}", f"{path}.type")
                else:
                    from_allowed, to_allowed = compatibility
                    if self.prefix(source) not in from_allowed or self.prefix(target) not in to_allowed:
                        self.add("error", "EDGE_SHAPE", f"{edge.get('type')} cannot connect {source} to {target}", path)
            self.edges_by_type[edge.get("type")].append(edge)

    def edges(self, edge_type: str, from_id: str | None = None, to_id: str | None = None) -> list[dict[str, Any]]:
        return [
            edge for edge in self.edges_by_type.get(edge_type, [])
            if (from_id is None or edge.get("from") == from_id) and (to_id is None or edge.get("to") == to_id)
        ]

    def validate_interfaces(self):
        for interface in self.graph.get("nodes", {}).get("interfaces", []):
            iid = interface["id"]
            for field in ("fromSystemId", "toSystemId"):
                ref = interface.get(field)
                if ref not in self.nodes_by_id or self.prefix(ref) != "SYS":
                    self.add("error", "INTERFACE_SYSTEM_REF", f"Interface {iid} has invalid {field} {ref}", f"{iid}.{field}")
            if interface.get("loadBearing") and not interface.get("failurePaths"):
                self.add("error", "INTERFACE_FAILURE_BEHAVIOR", f"Load-bearing interface {iid} has no failure paths", f"{iid}.failurePaths")
            for failure in interface.get("failurePaths", []):
                for required in ("condition", "behavior", "owner", "observability", "claimIds"):
                    if not failure.get(required):
                        self.add("error", "FAILURE_PATH_INCOMPLETE", f"Interface {iid} failure path {failure.get('id')} lacks {required}", f"{iid}.failurePaths")
            if self.graph.get("mode") == "build_reference" and interface.get("loadBearing") and interface.get("contractState") != "approved":
                blocked = any(edge.get("to") == iid for edge in self.edges_by_type.get("blocks", []))
                if not blocked:
                    self.add("error", "BUILD_INTERFACE_CONTRACT", f"Build-reference interface {iid} needs an approved contract or an explicit block", iid)

    def validate_adrs(self):
        for adr in self.graph.get("nodes", {}).get("adrs", []):
            aid = adr["id"]
            if not adr.get("affectedRefs"):
                self.add("error", "ADR_AFFECTED_REFS", f"ADR {aid} has no affected entities", f"{aid}.affectedRefs")
            for ref in adr.get("affectedRefs", []):
                if ref not in self.nodes_by_id:
                    self.add("error", "DANGLING_REF", f"ADR {aid} references missing entity {ref}", f"{aid}.affectedRefs")
            if adr.get("loadBearing") and adr.get("state") in {"open", "proposed"} and not adr.get("decisionPointRef"):
                self.add("error", "ADR_DECISION_POINT", f"Open load-bearing ADR {aid} needs a decision point", f"{aid}.decisionPointRef")

    def validate_scope_trace(self):
        nodes = self.graph.get("nodes", {})
        for scope in nodes.get("scopeItems", []):
            sid = scope["id"]
            implemented = bool(self.edges("implements_scope", to_id=sid))
            delivered = bool(self.edges("delivered_in", from_id=sid))
            roles = bool(self.edges("requires_role", from_id=sid))
            priced = bool(self.edges("prices", to_id=sid))
            if scope.get("inclusionState") in {"included", "conditional"}:
                if not implemented:
                    self.add("error", "ORPHAN_SCOPE_SOLUTION", f"Scope {sid} is not implemented by a system, interface, or ADR", sid)
                if self.graph.get("outputType") == "field_guide":
                    continue
                if not delivered:
                    self.add("error", "ORPHAN_SCOPE_PHASE", f"Scope {sid} is not assigned to a phase", sid)
                if not roles:
                    self.add("error", "ORPHAN_SCOPE_ROLE", f"Scope {sid} has no required role", sid)
                if not priced:
                    self.add("error", "ORPHAN_SCOPE_PRICE", f"Scope {sid} has no financial trace", sid)
            if scope.get("inclusionState") == "excluded":
                for edge in self.edges("prices", to_id=sid):
                    line = self.nodes_by_id[edge["from"]]
                    if line.get("amount") not in (0, None) or line.get("inclusionState") != "excluded":
                        self.add("error", "EXCLUSION_BASELINE", f"Excluded scope {sid} contributes to the priced baseline", sid)

    def validate_risks_and_conditions(self):
        for family in ("risks", "assumptions", "dependencies"):
            for node in self.graph.get("nodes", {}).get(family, []):
                node_id = node["id"]
                for ref in node.get("affectedRefs", []):
                    if ref not in self.nodes_by_id:
                        self.add("error", "DANGLING_REF", f"{node_id} references missing entity {ref}", f"{node_id}.affectedRefs")
                if node.get("loadBearing") and not node.get("owner"):
                    self.add("error", "CONDITION_OWNER", f"Load-bearing {node_id} has no owner", node_id)
                if family == "risks" and not node.get("mitigationActions"):
                    self.add("error", "RISK_MITIGATION", f"Risk {node_id} has no real mitigation", node_id)
                if family in {"assumptions", "dependencies"} and not node.get("closureCondition"):
                    self.add("error", "CONDITION_CLOSURE", f"{node_id} has no closure condition", node_id)

    def validate_staffing(self):
        nodes = self.graph.get("nodes", {})
        for allocation in nodes.get("allocations", []):
            aid = allocation["id"]
            refs = {
                "roleId": (allocation.get("roleId"), "ROL"),
                "phaseId": (allocation.get("phaseId"), "PHS"),
            }
            for field, (ref, prefix) in refs.items():
                if ref not in self.nodes_by_id or self.prefix(ref) != prefix:
                    self.add("error", "ALLOCATION_REF", f"Allocation {aid} has invalid {field} {ref}", f"{aid}.{field}")
            for ref in allocation.get("scopeItemIds", []):
                if ref not in self.nodes_by_id or self.prefix(ref) != "SCP":
                    self.add("error", "ALLOCATION_SCOPE", f"Allocation {aid} references invalid scope {ref}", f"{aid}.scopeItemIds")
            for field in ("startMilestoneId", "endMilestoneId"):
                ref = allocation.get(field)
                if ref and (ref not in self.nodes_by_id or self.prefix(ref) != "MLS"):
                    self.add("error", "ALLOCATION_MILESTONE", f"Allocation {aid} has invalid {field} {ref}", f"{aid}.{field}")

    def validate_timeline(self):
        phases = self.graph.get("nodes", {}).get("phases", [])
        sequence = [phase.get("sequence") for phase in phases]
        if len(sequence) != len(set(sequence)):
            self.add("error", "PHASE_SEQUENCE", "Phase sequence values must be unique", "nodes.phases")
        for phase in phases:
            if not phase.get("exitCriteria"):
                self.add("error", "PHASE_EXIT", f"Phase {phase['id']} needs observable exit criteria", phase["id"])
        for milestone in self.graph.get("nodes", {}).get("milestones", []):
            phase_id = milestone.get("phaseId")
            if phase_id not in self.nodes_by_id or self.prefix(phase_id) != "PHS":
                self.add("error", "MILESTONE_PHASE", f"Milestone {milestone['id']} has invalid phase {phase_id}", milestone["id"])

    def validate_financials(self):
        for control in self.graph.get("nodes", {}).get("reconciliationControls", []):
            cid = control["id"]
            for ref in control.get("leftRefs", []) + control.get("rightRefs", []):
                if ref not in self.nodes_by_id:
                    self.add("error", "RECONCILIATION_REF", f"Control {cid} references missing entity {ref}", cid)
            calculated = control.get("actual", 0) - control.get("expected", 0)
            if abs(calculated - control.get("variance", 0)) > 0.01:
                self.add("error", "RECONCILIATION_MATH", f"Control {cid} variance does not equal actual minus expected", cid)
            should_pass = abs(control.get("variance", 0)) <= control.get("tolerance", 0)
            if control.get("status") == "pass" and not should_pass:
                self.add("error", "RECONCILIATION_STATUS", f"Control {cid} is marked pass outside tolerance", cid)
            if control.get("status") == "fail" or not should_pass:
                self.add("error", "RECONCILIATION_FAIL", f"Control {cid} failed and blocks content approval", cid)

    def validate_judgment(self):
        judgment = self.graph.get("technicalJudgment") or {}
        for ref in judgment.get("conditionRefs", []):
            if ref not in self.nodes_by_id:
                self.add("error", "JUDGMENT_CONDITION_REF", f"Technical judgment references missing condition {ref}", "technicalJudgment.conditionRefs")
        if judgment.get("force") == "approve" and judgment.get("conditionRefs"):
            self.add("error", "JUDGMENT_FORCE", "Unconditional approval cannot carry open condition references", "technicalJudgment.force")

    def validate_views(self):
        views = self.graph.get("editorialViews", [])
        view_ids = set()
        types = Counter()
        grammars = set()
        for idx, view in enumerate(views):
            view_id = view.get("viewId")
            if view_id in view_ids:
                self.add("error", "VIEW_ID_DUPLICATE", f"Duplicate view ID {view_id}", f"editorialViews[{idx}]")
            view_ids.add(view_id)
            view_type = view.get("viewType")
            types[view_type] += 1
            grammar = view.get("preferredGrammar", "")
            grammars.add(grammar)
            if grammar == "generic_claim_card":
                self.add("error", "GENERIC_CARD_GRAMMAR", f"View {view_id} uses rejected generic card grammar", view_id)
            for ref in view.get("entityRefs", []):
                if ref not in self.nodes_by_id:
                    self.add("error", "VIEW_DANGLING_REF", f"View {view_id} references missing entity {ref}", view_id)
            if view_type and view_type not in CANONICAL_VIEWS:
                self.add("error", "VIEW_TYPE", f"View {view_id} uses unsupported view type {view_type}", view_id)
        output = self.graph.get("outputType")
        if output == "solution_brief":
            nodes = self.graph.get("nodes", {})
            for view_type, predicate in REQUIRED_VIEW_WHEN.items():
                if predicate(nodes) and not types[view_type]:
                    self.add("error", "VIEW_REQUIRED", f"Missing required editorial view {view_type}", "editorialViews")
            if len(grammars - {""}) < 5:
                self.add("error", "GRAMMAR_DIVERSITY", "Rich Solution Brief needs at least five distinct semantic renderer grammars", "editorialViews")
        if output == "field_guide" and len(grammars - {""}) < 4:
            self.add("error", "GRAMMAR_DIVERSITY", "Field guide needs at least four distinct semantic renderer grammars", "editorialViews")

    def validate_adequacy(self):
        output = self.graph.get("outputType")
        if output == "field_guide":
            nodes = self.graph.get("nodes", {})
            for family in ("systems", "scopeItems"):
                if not nodes.get(family):
                    self.add("error", "FIELD_GUIDE_FAMILY_MISSING", f"Field guide has no {family}", f"nodes.{family}")
            if not self.graph.get("edges"):
                self.add("error", "RELATIONSHIPS_MISSING", "Field guide has no typed relationships", "edges")
            return
        if output != "solution_brief":
            return
        nodes = self.graph.get("nodes", {})
        required_families = ["systems", "interfaces", "adrs", "scopeItems", "roles", "allocations", "phases", "financialLines", "reconciliationControls"]
        for family in required_families:
            if not nodes.get(family):
                self.add("error", "RICH_FAMILY_MISSING", f"Rich Solution Brief has no {family}", f"nodes.{family}")
        if not self.graph.get("edges"):
            self.add("error", "RELATIONSHIPS_MISSING", "Rich Solution Brief has no typed relationships", "edges")

    def validate_section_dispositions(self):
        records = self.graph.get("sectionDispositions") or []
        seen = set()
        for idx, record in enumerate(records):
            view_type = record.get("viewType")
            path = f"sectionDispositions[{idx}]"
            if view_type in seen:
                self.add("error", "DISPOSITION_DUPLICATE", f"Duplicate section disposition for {view_type}", path)
            seen.add(view_type)
            if view_type and view_type not in CANONICAL_VIEWS:
                self.add("error", "DISPOSITION_VIEW_TYPE", f"Unsupported view type {view_type}", path)
            if not record.get("reason"):
                self.add("error", "DISPOSITION_REASON", f"Section disposition for {view_type} has no reason", path)
            if record.get("confirmedInChat") is not True:
                self.add("error", "DISPOSITION_UNCONFIRMED", f"Section disposition for {view_type} was not confirmed", path)
        built = {view.get("viewType") for view in self.graph.get("editorialViews", [])}
        for record in records:
            view_type, disposition = record.get("viewType"), record.get("disposition")
            if disposition == "omitted" and view_type in built:
                self.add("error", "DISPOSITION_CONTRADICTS", f"{view_type} is recorded as omitted but a view was built", "sectionDispositions")
            if disposition in {"included", "thinned"} and view_type not in built:
                self.add("error", "DISPOSITION_ABSENT", f"{view_type} is recorded as {disposition} but no view exists", "sectionDispositions")
        for view_type in built:
            if view_type not in seen:
                self.add("error", "DISPOSITION_UNRECORDED", f"View {view_type} has no confirmed section disposition", "sectionDispositions")
        for view_type in sorted(FIELD_GUIDE_CANDIDATES - seen):
            self.add(
                "error",
                "DISPOSITION_MISSING",
                f"Candidate section {view_type} has no disposition. Include it, thin it, or omit it with a reason.",
                "sectionDispositions",
            )

    def validate_section_earned(self):
        for view in self.graph.get("editorialViews", []):
            view_type = view.get("viewType")
            floor = EVIDENCE_FLOOR.get(view_type, EVIDENCE_FLOOR_DEFAULT)
            count = len(view.get("claimIds", []))
            if count < floor:
                self.add(
                    "error",
                    "SECTION_UNEARNED",
                    f"View {view.get('viewId')} carries {count} governed claims against a floor of {floor}. "
                    "Omit it and record the reason. Do not lengthen it.",
                    f"editorialViews.{view.get('viewId')}.claimIds",
                )

    def validate_loadbearing_reach(self):
        reached = {
            ref
            for view in self.graph.get("editorialViews", [])
            for ref in view.get("entityRefs", [])
        }
        for node_id, node in self.nodes_by_id.items():
            if node.get("loadBearing") and node_id not in reached:
                self.add("error", "LOADBEARING_UNREACHED", f"Load-bearing {node_id} appears in no included section", node_id)

    def validate_conditional_disclosure(self):
        suff = self.graph.get("sufficiency", {})
        if suff.get("status") != "Conditional":
            return
        register = next(
            (view for view in self.graph.get("editorialViews", []) if view.get("viewType") == "conditions_next_action"),
            None,
        )
        if register is None:
            self.add("error", "CONDITIONAL_NO_REGISTER", "Conditional evidence requires an open-decisions section", "editorialViews")
            return
        disclosed_claims = set(register.get("claimIds", []))
        disclosed_refs = set(register.get("entityRefs", []))
        for idx, blocker in enumerate(suff.get("blockers", [])):
            claims = set(blocker.get("claimIds", []))
            refs = set(blocker.get("affectedRefs", []))
            path = f"sufficiency.blockers[{idx}]"
            if not claims and not refs:
                self.add("error", "BLOCKER_UNTRACEABLE", "Gate blocker declares neither claim IDs nor affected entities", path)
                continue
            if not (claims & disclosed_claims) and not (refs & disclosed_refs):
                self.add("error", "CONDITIONAL_BLOCKER_HIDDEN", f"Gate blocker {idx} is absent from the open-decisions register", path)

    def validate_field_guide_ledger(self):
        for scope in self.graph.get("nodes", {}).get("scopeItems", []):
            if scope.get("inclusionState") in {"included", "conditional"} and not scope.get("buildDisposition"):
                self.add("error", "LEDGER_DISPOSITION", f"Scope {scope['id']} has no build disposition for the ledger", f"{scope['id']}.buildDisposition")

    def validate_qa_entries(self):
        for entry in self.graph.get("nodes", {}).get("qaEntries", []):
            for ref in entry.get("affectedRefs", []):
                if ref not in self.nodes_by_id:
                    self.add("error", "DANGLING_REF", f"{entry['id']} references missing entity {ref}", f"{entry['id']}.affectedRefs")

    def run(self) -> dict[str, Any]:
        self.validate_top_level()
        self.index_nodes()
        self.validate_claims()
        self.validate_edges()
        output = self.graph.get("outputType")
        if output in FULL_OUTPUTS:
            self.validate_interfaces()
            self.validate_adrs()
            self.validate_scope_trace()
            self.validate_risks_and_conditions()
            self.validate_staffing()
            self.validate_timeline()
            self.validate_financials()
            self.validate_judgment()
            self.validate_views()
            self.validate_adequacy()
        if output == "field_guide":
            self.validate_section_dispositions()
            self.validate_section_earned()
            self.validate_loadbearing_reach()
            self.validate_conditional_disclosure()
            self.validate_field_guide_ledger()
            self.validate_qa_entries()
        counts = {family: len(self.graph.get("nodes", {}).get(family, [])) for family in NODE_FAMILIES}
        errors = [finding for finding in self.findings if finding.level == "error"]
        return {
            "validatorVersion": "0.3.0",
            "artifactType": self.graph.get("artifactType"),
            "outputType": self.graph.get("outputType"),
            "mode": self.graph.get("mode"),
            "passed": not errors,
            "nodeCounts": counts,
            "edgeCount": len(self.graph.get("edges", [])),
            "viewCount": len(self.graph.get("editorialViews", [])),
            "grammarCount": len({view.get("preferredGrammar") for view in self.graph.get("editorialViews", []) if view.get("preferredGrammar")}),
            "findings": [asdict(finding) for finding in self.findings],
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an Aleysian Solution Brief relational graph")
    parser.add_argument("graph", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    graph = json.loads(args.graph.read_text(encoding="utf-8"))
    report = GraphValidator(graph).run()
    text = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
