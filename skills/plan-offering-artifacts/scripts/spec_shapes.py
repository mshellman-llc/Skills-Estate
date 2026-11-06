"""Preserved version 1.1 artifact model for compatibility checks.

The authoritative specification is a caller input and is not bundled. This model
preserves the existing shapes and artifact requirements; it cannot establish that
they match the caller's current rules. See references/spec-inputs.md before using
these checks to support a release decision.
"""

SPEC_VERSION = "1.1"


def authority_status():
    """The local scripts do not validate an authoritative external specification."""
    return {"status": "unverified", "checked_rules_version": SPEC_VERSION,
            "release_ready": False,
            "required_inputs": ["approved_specification", "manifest_schema",
                                "qualifier_schema", "stage_gate_workbook"]}


SHAPES = ["Front Door", "Assess", "Implement", "Migrate", "Enhance", "Operate"]

# artifact number -> (slug, format, scope). scope "option" = one per option.
ARTIFACTS = {
    1:  ("readme", "md", "playbook"),
    2:  ("overview", "docx", "playbook"),
    3:  ("one-pager", "pdf", "playbook"),
    4:  ("talk-track", "docx", "playbook"),
    5:  ("qualifier", "docx", "playbook"),
    6:  ("rom", "pptx", "option"),
    7:  ("ddoc", "pptx", "playbook"),
    8:  ("proposal", "pptx", "option"),
    9:  ("stage-gate", "xlsx", "playbook"),
    10: ("sow", "docx", "option"),
}

# Per-shape required/conditional matrix. R required, C conditional. Every paid
# shape carries the full suite with ROM conditional; Front Door drops the deal
# layer (07 DDOC, 09 Stage Gate, 10 contract) to conditional and keeps 01-05 + 08.
_PAID = {1: "R", 2: "R", 3: "R", 4: "R", 5: "R", 6: "C", 7: "R", 8: "R", 9: "R", 10: "R"}
SHAPE_REQ = {
    "Front Door": {1: "R", 2: "R", 3: "R", 4: "R", 5: "R", 6: "C", 7: "C", 8: "R", 9: "C", 10: "C"},
    "Assess": _PAID,
    "Implement": _PAID,
    "Migrate": _PAID,
    "Enhance": _PAID,
    "Operate": _PAID,
}


def requirement(shape, number):
    """'R', 'C', or None for an artifact number under a shape. Unknown shape
    falls back to the paid suite so a missing shape never silently drops the gate."""
    return SHAPE_REQ.get(shape, _PAID).get(number)
