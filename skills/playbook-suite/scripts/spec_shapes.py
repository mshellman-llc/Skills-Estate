"""The SPEC.md per-shape artifact requirements, in one place.

This mirrors the "Per-shape requirements" table in
`skills/_shared/playbook-spec/SPEC.md` (spec 1.1). SPEC.md is the authority; this
module is the machine copy the folder tools (conformance_audit, plan) read so they
score a playbook against the artifacts its shape actually carries, not a flat
all-ten set. The canonical build (`canonical/build-canonical.py`) encodes the same
table for the registry side. Keep the three in step; SPEC.md wins any disagreement.
"""

SPEC_VERSION = "1.1"

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
