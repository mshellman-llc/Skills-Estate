#!/usr/bin/env python3
"""Build an expanded private career bundle and installable .skill artifact."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import shutil
import tempfile
from zipfile import ZIP_DEFLATED, ZipFile


SKILL_ROOT = Path(__file__).resolve().parents[1]
JOBHUNT_ROOT = SKILL_ROOT.parents[1]
AUTHORITATIVE_ROOT = Path("/Volumes/BeastMode/Career")
OUT_DIR = SKILL_ROOT.parent / "dist"
BUNDLE_NAME = "career-application-private"

SOURCE_MAP = {
    SKILL_ROOT / "SKILL.md": Path("SKILL.md"),
    SKILL_ROOT / "scripts" / "content-review.ts": Path("scripts/content-review.ts"),
    SKILL_ROOT / "scripts" / "content-review-cli.ts": Path("scripts/content-review-cli.ts"),
    SKILL_ROOT / "scripts" / "check_role_resume_readiness.py": Path("scripts/check_role_resume_readiness.py"),
    JOBHUNT_ROOT / "00_Master" / "Career_Application_Operating_Context.md": Path("references/career-context.md"),
    JOBHUNT_ROOT / "00_Master" / "Professional_Profile.md": Path("references/professional-profile.md"),
    JOBHUNT_ROOT / "00_Master" / "Career_Program_Portfolio.md": Path("references/career-program-portfolio.md"),
    JOBHUNT_ROOT / "00_Master" / "Productized_Consulting_and_Playbook_Universe_Record.md": Path("references/productized-consulting-and-playbook-universe-record.md"),
    JOBHUNT_ROOT / "00_Master" / "Client_Work_Strategy_and_Leadership_Record.md": Path("references/client-work-strategy-and-leadership-record.md"),
    JOBHUNT_ROOT / "05_Reference" / "Engagements" / "Client_Story_Coverage_Index.md": Path("05_Reference/Engagements/Client_Story_Coverage_Index.md"),
    JOBHUNT_ROOT / "05_Reference" / "Engagements" / "Client_Coverage_Matrix.csv": Path("05_Reference/Engagements/Client_Coverage_Matrix.csv"),
    JOBHUNT_ROOT / "05_Reference" / "Engagements" / "Client_Coverage_Universe.json": Path("05_Reference/Engagements/Client_Coverage_Universe.json"),
    JOBHUNT_ROOT / "05_Reference" / "Engagements" / "Firm_Corpus_Candidates.json": Path("05_Reference/Engagements/Firm_Corpus_Candidates.json"),
    JOBHUNT_ROOT / "06_System" / "migrations" / "2026-10-01_client-story-universe" / "verification.json": Path("06_System/migrations/2026-10-01_client-story-universe/verification.json"),
    JOBHUNT_ROOT / "05_Reference" / "Story_Bank" / "Client_Stories_Development.md": Path("05_Reference/Story_Bank/Client_Stories_Development.md"),
    JOBHUNT_ROOT / "05_Reference" / "Story_Bank" / "Burr_Oak_Tool_Career_Story.md": Path("05_Reference/Story_Bank/Burr_Oak_Tool_Career_Story.md"),
    JOBHUNT_ROOT / "05_Reference" / "Engagements" / "Burr_Oak_Tool" / "Burr_Oak_Tool_Story_Evidence.md": Path("05_Reference/Engagements/Burr_Oak_Tool/Burr_Oak_Tool_Story_Evidence.md"),
    JOBHUNT_ROOT / "05_Reference" / "Engagements" / "Burr_Oak_Tool" / "Burr_Oak_Tool_Story_Evidence.json": Path("05_Reference/Engagements/Burr_Oak_Tool/Burr_Oak_Tool_Story_Evidence.json"),
    JOBHUNT_ROOT / "06_System" / "migrations" / "2026-10-01_burr-oak-story" / "content-review.json": Path("06_System/migrations/2026-10-01_burr-oak-story/content-review.json"),
    JOBHUNT_ROOT / "05_Reference" / "Claim_Governance" / "Client_Story_Development_Ledger.json": Path("05_Reference/Claim_Governance/Client_Story_Development_Ledger.json"),
    JOBHUNT_ROOT / "05_Reference" / "Engagements" / "Older_Client_Participation_Review.csv": Path("05_Reference/Engagements/Older_Client_Participation_Review.csv"),
    JOBHUNT_ROOT / "06_System" / "migrations" / "2026-10-01_client-story-development" / "content-review.json": Path("06_System/migrations/2026-10-01_client-story-development/content-review.json"),
    JOBHUNT_ROOT / "06_System" / "migrations" / "2026-10-01_client-story-development" / "verification.json": Path("06_System/migrations/2026-10-01_client-story-development/verification.json"),
    JOBHUNT_ROOT / "00_Master" / "GoGuardian_Program_Record.md": Path("references/goguardian-program-record.md"),
    JOBHUNT_ROOT / "05_Reference" / "Engagements" / "GoGuardian" / "GoGuardian_Source_Audit.md": Path("references/goguardian-source-audit.md"),
    JOBHUNT_ROOT / "05_Reference" / "Engagements" / "GoGuardian" / "GoGuardian_Deliverables_and_Artifact_Catalog.md": Path("references/goguardian-deliverables-and-artifact-catalog.md"),
    JOBHUNT_ROOT / "05_Reference" / "Engagements" / "GoGuardian" / "GoGuardian_Assessment_Method_and_Scoring.md": Path("references/goguardian-assessment-method-and-scoring.md"),
    JOBHUNT_ROOT / "05_Reference" / "Engagements" / "GoGuardian" / "GoGuardian_Metric_and_Claim_Library.md": Path("references/goguardian-metric-and-claim-library.md"),
    JOBHUNT_ROOT / "00_Master" / "Governed_AI_Skill_Estate_and_Knowledge_Hub_Program_Record.md": Path("references/governed-skill-estate-and-knowledge-hub-program-record.md"),
    JOBHUNT_ROOT / "00_Master" / "AI_Skill_Portfolio_Quality_and_Scaling_Record.md": Path("references/ai-skill-portfolio-quality-and-scaling-record.md"),
    JOBHUNT_ROOT / "00_Master" / "Linky_Product_Record.md": Path("references/linky-product-record.md"),
    JOBHUNT_ROOT / "00_Master" / "Assessment_Strategy_and_Enablement_Program_Record.md": Path("references/assessment-strategy-and-enablement-program-record.md"),
    JOBHUNT_ROOT / "00_Master" / "Solution_Engineering_Leadership_Evidence_Map.md": Path("references/solution-engineering-leadership-evidence-map.md"),
    JOBHUNT_ROOT / "00_Master" / "Leadership_Interview_Evidence_Map.md": Path("references/leadership-interview-evidence-map.md"),
    JOBHUNT_ROOT / "00_Master" / "Career_Narrative_Translation_Guide.md": Path("references/career-narrative-translation-guide.md"),
    JOBHUNT_ROOT / "05_Reference" / "Claim_Governance" / "Career_Program_Evidence_Ledger.md": Path("references/career-program-evidence-ledger.md"),
    JOBHUNT_ROOT / "05_Reference" / "Story_Bank" / "Success_Stories.md": Path("references/success-stories.md"),
    JOBHUNT_ROOT / "04_Interview" / "Interview_Preparation.md": Path("references/interview-preparation.md"),
    JOBHUNT_ROOT / "03_Tracker" / "applications.md": Path("references/applications.md"),
    JOBHUNT_ROOT / "02_Templates" / "Role_Work_Record_Template.md": Path("references/role-work-record-template.md"),
    JOBHUNT_ROOT / "00_Master" / "Resume_Masters" / "Megan_Shellman_Technical_GTM_Solutions_Leadership_Resume.docx": Path("assets/resumes/Megan_Shellman_Technical_GTM_Solutions_Leadership_Resume.docx"),
    JOBHUNT_ROOT / "00_Master" / "Resume_Masters" / "Megan_Shellman_AI_Strategy_Enablement_Resume.docx": Path("assets/resumes/Megan_Shellman_AI_Strategy_Enablement_Resume.docx"),
    JOBHUNT_ROOT / "00_Master" / "Resume_Masters" / "Megan_Shellman_Revenue_Technology_Transformation_Resume.docx": Path("assets/resumes/Megan_Shellman_Revenue_Technology_Transformation_Resume.docx"),
    JOBHUNT_ROOT / "05_Reference" / "Applied_AI_Review_2026-10-01" / "Coverage_Index.md": Path("05_Reference/Applied_AI_Review_2026-10-01/Coverage_Index.md"),
    JOBHUNT_ROOT / "05_Reference" / "Applied_AI_Review_2026-10-01" / "candidate_inventory.json": Path("05_Reference/Applied_AI_Review_2026-10-01/candidate_inventory.json"),
    JOBHUNT_ROOT / "05_Reference" / "Applied_AI_Review_2026-10-01" / "Skill_Evidence_Matrix.md": Path("05_Reference/Applied_AI_Review_2026-10-01/Skill_Evidence_Matrix.md"),
    JOBHUNT_ROOT / "05_Reference" / "Applied_AI_Review_2026-10-01" / "Interview_Story_Bank.md": Path("05_Reference/Applied_AI_Review_2026-10-01/Interview_Story_Bank.md"),
    JOBHUNT_ROOT / "05_Reference" / "Applied_AI_Review_2026-10-01" / "source_manifest.json": Path("05_Reference/Applied_AI_Review_2026-10-01/source_manifest.json"),
    JOBHUNT_ROOT / "05_Reference" / "Applied_AI_Review_2026-10-01" / "Employer/profiles.json": Path("05_Reference/Applied_AI_Review_2026-10-01/Employer/profiles.json"),
    JOBHUNT_ROOT / "05_Reference" / "Applied_AI_Review_2026-10-01" / "Historical/profiles.json": Path("05_Reference/Applied_AI_Review_2026-10-01/Historical/profiles.json"),
    JOBHUNT_ROOT / "05_Reference" / "Applied_AI_Review_2026-10-01" / "Independent/profiles.json": Path("05_Reference/Applied_AI_Review_2026-10-01/Independent/profiles.json"),
}


def file_hash(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_bundle(destination: Path, staged_root: Path) -> None:
    with ZipFile(destination, "w", ZIP_DEFLATED) as archive:
        for path in sorted(staged_root.rglob("*")):
            if path.is_file():
                archive.write(path, Path("career-application") / path.relative_to(staged_root))


def write_manifest(root: Path) -> None:
    manifest = root / "MANIFEST.sha256"
    lines = [
        f"{file_hash(path)}  {path.relative_to(root).as_posix()}"
        for path in sorted(root.rglob("*"))
        if path.is_file() and path != manifest
    ]
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")


def verify_bundle(path: Path) -> None:
    required = {
        "career-application/05_Reference/Applied_AI_Review_2026-10-01/Coverage_Index.md",
        "career-application/05_Reference/Applied_AI_Review_2026-10-01/candidate_inventory.json",
        "career-application/05_Reference/Applied_AI_Review_2026-10-01/Skill_Evidence_Matrix.md",
        "career-application/05_Reference/Applied_AI_Review_2026-10-01/Interview_Story_Bank.md",
        "career-application/05_Reference/Applied_AI_Review_2026-10-01/source_manifest.json",
        "career-application/05_Reference/Applied_AI_Review_2026-10-01/Employer/profiles.json",
        "career-application/05_Reference/Applied_AI_Review_2026-10-01/Historical/profiles.json",
        "career-application/05_Reference/Applied_AI_Review_2026-10-01/Independent/profiles.json",
        "career-application/SKILL.md",
        "career-application/scripts/check_role_resume_readiness.py",
        "career-application/scripts/content-review.ts",
        "career-application/scripts/content-review-cli.ts",
        "career-application/PRIVATE_BUNDLE_NOTICE.md",
        "career-application/bundle-manifest.json",
        "career-application/MANIFEST.sha256",
        "career-application/references/career-context.md",
        "career-application/references/professional-profile.md",
        "career-application/references/career-program-portfolio.md",
        "career-application/references/productized-consulting-and-playbook-universe-record.md",
        "career-application/references/client-work-strategy-and-leadership-record.md",
        "career-application/05_Reference/Engagements/Firm_Corpus_Candidates.json",
        "career-application/05_Reference/Engagements/Client_Coverage_Universe.json",
        "career-application/05_Reference/Engagements/Client_Coverage_Matrix.csv",
        "career-application/05_Reference/Engagements/Client_Story_Coverage_Index.md",
        "career-application/references/goguardian-program-record.md",
        "career-application/references/goguardian-source-audit.md",
        "career-application/references/goguardian-deliverables-and-artifact-catalog.md",
        "career-application/references/goguardian-assessment-method-and-scoring.md",
        "career-application/references/goguardian-metric-and-claim-library.md",
        "career-application/references/governed-skill-estate-and-knowledge-hub-program-record.md",
        "career-application/references/ai-skill-portfolio-quality-and-scaling-record.md",
        "career-application/references/linky-product-record.md",
        "career-application/references/assessment-strategy-and-enablement-program-record.md",
        "career-application/references/solution-engineering-leadership-evidence-map.md",
        "career-application/references/leadership-interview-evidence-map.md",
        "career-application/references/career-narrative-translation-guide.md",
        "career-application/references/career-program-evidence-ledger.md",
        "career-application/references/success-stories.md",
        "career-application/references/interview-preparation.md",
        "career-application/references/applications.md",
        "career-application/references/role-work-record-template.md",
    }
    with ZipFile(path) as archive:
        names = set(archive.namelist())
        missing = required - names
        bad = archive.testzip()
    if missing:
        raise RuntimeError(f"bundle missing required files: {sorted(missing)}")
    if bad:
        raise RuntimeError(f"bundle contains a corrupt member: {bad}")


def verify_expanded(path: Path) -> None:
    required = {
        "05_Reference/Applied_AI_Review_2026-10-01/Coverage_Index.md",
        "05_Reference/Applied_AI_Review_2026-10-01/candidate_inventory.json",
        "05_Reference/Applied_AI_Review_2026-10-01/Skill_Evidence_Matrix.md",
        "05_Reference/Applied_AI_Review_2026-10-01/Interview_Story_Bank.md",
        "05_Reference/Applied_AI_Review_2026-10-01/source_manifest.json",
        "05_Reference/Applied_AI_Review_2026-10-01/Employer/profiles.json",
        "05_Reference/Applied_AI_Review_2026-10-01/Historical/profiles.json",
        "05_Reference/Applied_AI_Review_2026-10-01/Independent/profiles.json",
        "SKILL.md",
        "scripts/check_role_resume_readiness.py",
        "scripts/content-review.ts",
        "scripts/content-review-cli.ts",
        "PRIVATE_BUNDLE_NOTICE.md",
        "bundle-manifest.json",
        "MANIFEST.sha256",
        "references/career-context.md",
        "references/professional-profile.md",
        "references/career-program-portfolio.md",
        "references/productized-consulting-and-playbook-universe-record.md",
        "references/client-work-strategy-and-leadership-record.md",
        "05_Reference/Engagements/Firm_Corpus_Candidates.json",
        "05_Reference/Engagements/Client_Coverage_Universe.json",
        "05_Reference/Engagements/Client_Coverage_Matrix.csv",
        "05_Reference/Engagements/Client_Story_Coverage_Index.md",
        "references/goguardian-program-record.md",
        "references/goguardian-source-audit.md",
        "references/goguardian-deliverables-and-artifact-catalog.md",
        "references/goguardian-assessment-method-and-scoring.md",
        "references/goguardian-metric-and-claim-library.md",
        "references/governed-skill-estate-and-knowledge-hub-program-record.md",
        "references/ai-skill-portfolio-quality-and-scaling-record.md",
        "references/linky-product-record.md",
        "references/assessment-strategy-and-enablement-program-record.md",
        "references/solution-engineering-leadership-evidence-map.md",
        "references/leadership-interview-evidence-map.md",
        "references/career-narrative-translation-guide.md",
        "references/career-program-evidence-ledger.md",
        "references/success-stories.md",
        "references/interview-preparation.md",
        "references/applications.md",
        "references/role-work-record-template.md",
    }
    names = {item.relative_to(path).as_posix() for item in path.rglob("*") if item.is_file()}
    missing = required - names
    if missing:
        raise RuntimeError(f"expanded bundle missing required files: {sorted(missing)}")


def main() -> None:
    canonical = Path("/Volumes/BeastMode/Projects/Knowledge Hub/src")
    for name in ("content-review.ts", "content-review-cli.ts"):
        source = canonical / name
        if not source.is_file():
            raise SystemExit("canonical content validator unavailable; do not build a stale derivative")
        shutil.copy2(source, SKILL_ROOT / "scripts" / name)
    missing = [str(path) for path in SOURCE_MAP if not path.is_file()]
    if missing:
        raise SystemExit("missing source files: " + ", ".join(missing))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="career-application-bundle-") as temp_dir:
        staged_root = Path(temp_dir) / "career-application"
        for source, relative in SOURCE_MAP.items():
            target = staged_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

        notice = staged_root / "PRIVATE_BUNDLE_NOTICE.md"
        notice.write_text(
            "# Private career bundle\n\n"
            "This package contains Megan Shellman's current resume masters, including personal "
            "contact information, private career narratives and evidence boundaries, role-search "
            "preferences, and application history. "
            "Upload it only to Megan's private Claude skill library. Do not share it with an "
            "organization, group, marketplace, or another person.\n\n"
            "The package is a point-in-time snapshot. Rebuild it from BeastMode after a title, "
            "resume, evidence, preference, or application-state change.\n",
            encoding="utf-8",
        )

        manifest = {
            "name": "career-application",
            "built_at": datetime.now(timezone.utc).isoformat(),
            "privacy": "private-personal-career-material",
            "source_root": str(AUTHORITATIVE_ROOT),
            "built_from_root": str(JOBHUNT_ROOT),
            "files": [
                {
                    "bundle_path": str(relative),
                    "source_path": str(AUTHORITATIVE_ROOT / source.relative_to(JOBHUNT_ROOT)),
                    "sha256": file_hash(source),
                }
                for source, relative in sorted(SOURCE_MAP.items(), key=lambda item: str(item[1]))
            ],
        }
        (staged_root / "bundle-manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )
        write_manifest(staged_root)

        expanded_path = OUT_DIR / BUNDLE_NAME
        legacy_zip = OUT_DIR / f"{BUNDLE_NAME}.zip"
        legacy_checksum = OUT_DIR / f"{BUNDLE_NAME}.zip.sha256"
        if legacy_zip.exists() or legacy_checksum.exists():
            raise SystemExit("legacy .zip output remains; run the recorded no-ZIP cleanup first")
        # Directory renames and recursive replacement are unreliable on the mounted SMB
        # volume. The staged source is already verified through its manifest, so update
        # the generated expanded view in place and verify the destination afterward.
        shutil.copytree(staged_root, expanded_path, dirs_exist_ok=True)
        verify_expanded(expanded_path)

        skill_path = OUT_DIR / f"{BUNDLE_NAME}.skill"
        skill_temp = OUT_DIR / f".{BUNDLE_NAME}.skill.tmp"
        write_bundle(skill_temp, staged_root)
        verify_bundle(skill_temp)
        skill_temp.replace(skill_path)

    verify_expanded(expanded_path)
    verify_bundle(skill_path)
    checksum_path = OUT_DIR / f"{BUNDLE_NAME}.skill.sha256"
    checksum_path.write_text(
        f"{file_hash(skill_path)}  {skill_path.name}\n", encoding="utf-8"
    )
    print(f"BUILT {expanded_path}")
    print(f"BUILT {skill_path}")
    print(f"BUILT {checksum_path}")
    print("VERIFIED expanded bundle contents and .skill archive integrity")


if __name__ == "__main__":
    main()
