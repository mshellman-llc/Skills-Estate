#!/usr/bin/env python3
"""Structural and source-integrity checks for the personal career skill."""

from pathlib import Path
import re
import sys


SKILL_ROOT = Path(__file__).resolve().parents[1]
JOBHUNT_ROOT = SKILL_ROOT.parents[1]
SKILL = SKILL_ROOT / "SKILL.md"
CONTEXT = JOBHUNT_ROOT / "00_Master" / "Career_Application_Operating_Context.md"

REQUIRED_SOURCES = [
    CONTEXT,
    JOBHUNT_ROOT / "00_Master" / "Professional_Profile.md",
    JOBHUNT_ROOT / "00_Master" / "Career_Program_Portfolio.md",
    JOBHUNT_ROOT / "00_Master" / "Client_Work_Strategy_and_Leadership_Record.md",
    JOBHUNT_ROOT / "00_Master" / "GoGuardian_Program_Record.md",
    JOBHUNT_ROOT / "05_Reference" / "Engagements" / "GoGuardian" / "GoGuardian_Source_Audit.md",
    JOBHUNT_ROOT / "05_Reference" / "Engagements" / "GoGuardian" / "GoGuardian_Deliverables_and_Artifact_Catalog.md",
    JOBHUNT_ROOT / "05_Reference" / "Engagements" / "GoGuardian" / "GoGuardian_Assessment_Method_and_Scoring.md",
    JOBHUNT_ROOT / "05_Reference" / "Engagements" / "GoGuardian" / "GoGuardian_Metric_and_Claim_Library.md",
    JOBHUNT_ROOT / "00_Master" / "Governed_AI_Skill_Estate_and_Knowledge_Hub_Program_Record.md",
    JOBHUNT_ROOT / "00_Master" / "AI_Skill_Portfolio_Quality_and_Scaling_Record.md",
    JOBHUNT_ROOT / "00_Master" / "Linky_Product_Record.md",
    JOBHUNT_ROOT / "00_Master" / "Assessment_Strategy_and_Enablement_Program_Record.md",
    JOBHUNT_ROOT / "00_Master" / "Solution_Engineering_Leadership_Evidence_Map.md",
    JOBHUNT_ROOT / "00_Master" / "Leadership_Interview_Evidence_Map.md",
    JOBHUNT_ROOT / "00_Master" / "Career_Narrative_Translation_Guide.md",
    JOBHUNT_ROOT / "05_Reference" / "Claim_Governance" / "Career_Program_Evidence_Ledger.md",
    JOBHUNT_ROOT / "05_Reference" / "Story_Bank" / "Success_Stories.md",
    JOBHUNT_ROOT / "04_Interview" / "Interview_Preparation.md",
    JOBHUNT_ROOT / "03_Tracker" / "applications.md",
    JOBHUNT_ROOT / "02_Templates" / "Role_Work_Record_Template.md",
    JOBHUNT_ROOT / "00_Master" / "Resume_Masters" / "Megan_Shellman_Technical_GTM_Solutions_Leadership_Resume.docx",
    JOBHUNT_ROOT / "00_Master" / "Resume_Masters" / "Megan_Shellman_AI_Strategy_Enablement_Resume.docx",
    JOBHUNT_ROOT / "00_Master" / "Resume_Masters" / "Megan_Shellman_Revenue_Technology_Transformation_Resume.docx",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


text = SKILL.read_text(encoding="utf-8")
match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
if not match:
    fail("SKILL.md has no YAML frontmatter")

frontmatter = match.group(1)
name = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
description = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
if not name or name.group(1).strip() != "career-application":
    fail("unexpected skill name")
if not description or len(description.group(1).strip()) > 200:
    fail("description is missing or exceeds Claude's 200-character guidance")

for required in (
    "filled and awaiting submission",
    "explicitly authorizes",
    "references/career-context.md",
    "references/career-narrative-translation-guide.md",
    "references/governed-skill-estate-and-knowledge-hub-program-record.md",
    "references/ai-skill-portfolio-quality-and-scaling-record.md",
    "references/client-work-strategy-and-leadership-record.md",
    "references/goguardian-program-record.md",
    "references/goguardian-source-audit.md",
    "references/goguardian-deliverables-and-artifact-catalog.md",
    "references/goguardian-assessment-method-and-scoring.md",
    "references/goguardian-metric-and-claim-library.md",
    "references/linky-product-record.md",
    "references/assessment-strategy-and-enablement-program-record.md",
    "references/solution-engineering-leadership-evidence-map.md",
    "references/leadership-interview-evidence-map.md",
    "references/success-stories.md",
    "references/interview-preparation.md",
    "$career-application interview",
    "assets/resumes/",
    "Do not share or publish",
    "A clipped read is incomplete",
    "inventory relevant prior role-specific resumes",
    "check_role_resume_readiness.py",
):
    if required.lower() not in text.lower():
        fail(f"missing required instruction: {required}")

missing = [str(path) for path in REQUIRED_SOURCES if not path.is_file()]
if missing:
    fail("missing source files: " + ", ".join(missing))

receipt_template = (JOBHUNT_ROOT / "02_Templates" / "Role_Work_Record_Template.md").read_text(encoding="utf-8")
for required in (
    "## Resume source review",
    "Base master:",
    "Prior variants reviewed:",
    "Retain:",
    "Revise:",
    "Exclude:",
    "Claim authority checked:",
    "Tailored resume:",
    "Finished copy check:",
):
    if required not in receipt_template:
        fail(f"role record template is missing: {required}")

if not (SKILL_ROOT / "scripts" / "check_role_resume_readiness.py").is_file():
    fail("resume readiness checker is missing")

context = CONTEXT.read_text(encoding="utf-8")
for required in (
    "Senior Managing Principal Sales Engineer, Technology Solutions - AI & Revenue Operations",
    "Managing Principal | Jul 2025-Feb 2026",
    "SQMR",
    "$200K",
    "$250K+",
    "43 CRM-attributed pursuit teams",
    "53 broader Book of Business deal/project cycles",
    "46 authored scoping-application quotes",
    "Megan_Shellman_Technical_GTM_Solutions_Leadership_Resume.docx",
    "Megan_Shellman_AI_Strategy_Enablement_Resume.docx",
    "Megan_Shellman_Revenue_Technology_Transformation_Resume.docx",
    "Older resumes are writing and layout history, not current claim authority",
):
    if required not in context:
        fail(f"operating context is missing: {required}")

print("PASS: career-application skill and live sources are consistent")
sys.exit(0)
