---
name: prepare-job-application
description: Assess, tailor, prepare interviews, fill, or resume the candidate's applications using current postings and private career evidence. Never submit without explicit authorization.
---


# Prepare job application

Use only the candidate identity, career records, thresholds, author profile and destinations explicitly supplied or authorized for this task. Record names below describe a suggested source map; resolve them under the confirmed career root or accept equivalent supplied records. None is a bundled personal default. Missing optional context does not block a bounded draft from supplied facts.

Run one role at a time from current evidence without relying on conversation history.

## Start here

Resolve the career evidence root from explicit task input or the candidate's confirmed operating context. Do not search a machine-specific default. Paths below are a suggested record layout under that root, not files bundled with this skill. Accept an equivalent source map when the candidate organizes records differently.

Read `00_Master/Career_Application_Operating_Context.md` first. Then load only:

- the current live posting;
- the current role's `Role_Work_Record.md`, when one exists; and
- the source files named by the operating context for the current mode.

Do not load every prior application or reconstruct the full job-search folder unless a cross-surface correction requires it.

This estate package contains workflow instructions and validation code. Private career evidence, submitted applications, and resumes remain in the subject authority. If that source is unavailable, ask for the specific current evidence needed for the request or use an explicitly supplied dated bundle. Do not assume this package includes those private records. Return proposed record changes for the user to save when the live destination is unavailable.

## Invocation modes

Infer the mode from the candidate's request. The candidate can also state it directly.

- Codex: `$prepare-job-application assess <URL>`
- Claude Code: `/prepare-job-application assess <URL>`
- Claude chat or Cowork: enable **Career Application**, then say `Use Career Application to assess <URL>`.

- `$prepare-job-application assess <URL>`: verify the live posting, screen the role, and recommend pursue or skip.
- `$prepare-job-application find <criteria>`: find current roles, screen them, and return a shortlist. Do not create application folders until the candidate chooses a role.
- `$prepare-job-application tailor <URL>`: create or update the role work record and a role-specific resume copy. Do not overwrite a master resume.
- `$prepare-job-application interview <company or role>`: build a role-specific interview plan from the current posting and evidence-backed story bank.
- `$prepare-job-application fill <URL>`: open the form, fill supported factual fields, upload approved materials, and stop at the authorization boundaries below.
- `$prepare-job-application status <company or role>`: read the tracker and role work record, then report the verified state and next action.
- `$prepare-job-application continue <company or role>`: resume from the saved role work record rather than from prior chat history.

If the request does not specify a mode, use `assess` for a new URL and `continue` for a named existing role.

## Assess

1. Verify the employer's current posting. Treat reposts, aggregators, and old snapshots as secondary.
2. Screen the role against the candidate’s confirmed opportunity criteria. Derive the work requirements from the live posting; do not score it against a fixed career identity.
3. Map requirements into four groups: strong evidence, transferable evidence, real gaps, and unsupported or unanswered questions.
4. Give a direct pursue or skip recommendation. Do not tailor materials for a skip.
5. When the candidate explicitly chooses pursue or skip, update `03_Tracker/applications.md` in the live source. A skip needs no application folder unless notes would prevent repeated research. In a portable session, create an updated tracker copy for the candidate instead of claiming the live tracker changed.

## Tailor and prepare

1. Create `01_Applications/Current/YYYY-MM-DD_Company_Role/` under the live source.
2. Copy `02_Templates/Role_Work_Record_Template.md` into that folder as `Role_Work_Record.md` and fill it from evidence.
3. Read `00_Master/Career_Narrative_Translation_Guide.md`. Map the role’s actual requirements to relevant evidence in the role record before drafting. Derive emphasis from the posting and current request rather than a standing career theme.
4. Select program records through the confirmed evidence map for the role's mandates. For a reusable product or governed system, preserve its problem, user, mechanism, risk-specific tests, growth path and verified state. Keep distribution, persistence and adoption claims distinct; do not lead with artifact counts.
5. For client-facing or transformation roles, select the supported decisions and results that demonstrate the posting. Client, portfolio, people and practice examples are available when relevant; no pair is mandatory. Keep pursuit, project, authored-quote and realized-outcome counts distinct. No named historical client or metric is a default input.
6. For product, platform, identity, security or responsible-AI roles, select relevant product evidence from the supplied map. Keep local build and test proof separate from deployment, access, usage and adoption.
7. For assessment, workforce, enablement or people-system roles, preserve source-bank authorship, human-review boundaries, and the difference between built, published privately, shared, run and adopted.
8. For each selected program, preserve the problem or decision, the candidate's ownership, the mechanism, the evidence-backed result, and the real gap or state boundary. Retain the constraint or pivot when it proves leadership or judgment. For governed skills, distinguish original authorship, later estate governance or integration, and later contributor authorship; admission, repair, rename, or consolidation does not establish sole authorship of every package.
9. Select the base resume using the operating-context router. Copy it into the role folder before editing.
10. Before drafting, inventory relevant prior role-specific resumes and historical variants. Read the versions that cover the role mandate and note in the role work record what prior wording or layout to retain, revise, or exclude. Treat them as writing history, never as current claim authority; recheck carried claims against current evidence. A clipped read is incomplete.
11. Tailor only what the posting supports: headline, executive profile, expertise order, selected bullet order or wording, and technology emphasis. Intentional selection is required; do not collapse unrelated programs into one “AI tools” bullet, a platform list, or a playbook count; do not force the entire portfolio into the document.
12. Keep private evidence notes separate from employer-facing materials. Do not place client-sensitive facts, internal identifiers, repositories, or unsupported metrics in application files.
13. Apply the candidate's `apply-author-style` with an explicitly supplied confirmed profile and `review-writing` rules. Run the bundled writing diagnostics as a deterministic gate where it is installed, not as permission to flatten real resume lists.
14. Render and inspect every changed DOCX. Verify accessibility and document integrity. Separately read the finished copy against the role mandate and evidence map; layout review does not prove content quality.
15. Complete the `Resume source review` receipt in the role work record and run `python3 scripts/check_role_resume_readiness.py` against that record before calling a tailored resume prepared locally. The checker verifies a completed receipt and readable files, not the truth or quality of its prose; perform the content review yourself.
16. Update the role work record and tracker with the exact local state. When the source is unavailable, use a supplied role-work-record template or clearly label a new draft record and return it for the user to save.

## Prepare for interviews

1. Verify the current posting and read the role work record. Do not prepare from a remembered title or an expired posting when a live source is available.
2. Read `00_Master/Leadership_Interview_Evidence_Map.md`, `04_Interview/Interview_Preparation.md`, and `05_Reference/Story_Bank/Success_Stories.md`. Add only the program records needed for the role's primary mandates.
3. Derive likely interview areas from the posting and current request. Select relevant evidence rather than requiring a standard set of career themes. Do not turn the result into a generic question dump.
4. Select no more than six anchor stories. For each one, prepare a 30-second headline, a two-minute causal answer, likely follow-ups, the difficult decision or conversation, the turnaround mechanism, the result, and the evidence boundary.
5. Use the order: problem or stakes, the candidate's mandate, decision, mechanism, resistance or constraint, turning point, evidence-backed result, and learning. Name what changed because of the candidate rather than only describing the artifact.
6. Preserve ownership boundaries. Do not claim that the candidate performed every delivery task, that forecast value was realized, that UAT equals production, or that an opportunity became a win without evidence.
7. Do not fabricate a direct-report performance case, hiring decision, promotion decision, team-conflict case, or quantified adoption result. If a target role is likely to test one of those areas, mark it as an evidence gap and ask the candidate for a real event before drafting the answer.
8. Keep closed corrective-action history out of routine preparation. Use it only if the candidate explicitly chooses that material for a specific answer.
9. Save role-specific interview work inside the application folder. Do not overwrite the master interview book for one employer.

## Fill and submit

Filling an application does not authorize submission.

Fill supported factual fields and upload reviewed files. Pause for the candidate on:

- salary expectations;
- unconfirmed work authorization or sponsorship answers;
- demographic or self-identification questions;
- legal attestations, signatures, and acknowledgments;
- MFA and CAPTCHA; and
- the final Submit action.

Submit only when the candidate explicitly authorizes that specific application. After submission, capture the confirmation or receipt and record it in `Role_Work_Record.md` before marking the tracker `Submitted`.

## Preserve execution truth

Use these states precisely: `researching`, `skipped`, `prepared locally`, `filled and awaiting submission`, `submitted`, `screen`, `interview`, `offer`, and `closed`.

A generated file is only `prepared locally`. A populated form is only `filled and awaiting submission`. `Submitted` requires destination-side confirmation or a receipt.

End material work with four facts: **changed now**, **verified**, **still unchanged**, and the **exact next action**.

## Boundaries

- Preserve official titles and dates exactly.
- Do not invent scope, reporting lines, direct-report counts, adoption analytics, production scale, compensation, or realized savings.
- Do not turn a difficult conversation into a fabricated conflict story or remove the evidence boundary to make an answer sound more decisive.
- Do not recast historical titles to match a posting.
- Do not update a downstream claim first. New evidence enters through the evidence ledger and program portfolio, then propagates according to the translation guide.
- Use the candidate’s explicitly confirmed role target; do not substitute another level or career lane without their choice.
- Do not publish, message recruiters, or submit an application unless the candidate asks for that action.
- Do not treat remembered role details as current when the live posting can be checked.
- Treat supplied career records and any explicitly requested evidence bundle as private personal material. The reusable workflow contains no career records; do not attach private evidence to its distributable plugin.

## Audience and content review gate

Before drafting, declare the audience, document purpose, intended reader action, author voice, and consequence level. These determine style, density, terminology, and prose-review depth. Internal updates use light review; hiring, public portfolio, client proposals, and consequential work use deep review. Accuracy and privacy are required at every depth. Do not apply a word blacklist or AI-detector scoring.

For a résumé, retrieve the career foundation and relevant prior résumé before selecting examples. Check roles, dates, responsibilities and ownership for accuracy. Review why the selected evidence fits the role; leadership, client, commercial and product examples are not universally required sections. A portfolio handout is a separate purpose and must not replace a résumé. Choose length after selecting substantive coverage.

The source-review section must include `Content review` pointing to an absolute JSON receipt. The receipt contains `artifact_sha256` for the entire DOCX, `brief`, `review`, and `source_files` with IDs, absolute paths, exact file SHA256 hashes, and snapshot revisions. `review` binds the exact DOCX paragraph text hash, pins all reviewed sources, names the reviewer, supplies exact draft excerpts for required coverage, and separately records accuracy, representation, writing, and layout reviews with concrete notes. The shared `content-review.ts` module supplies the schema, required dimensions, and audience-derived depth. Review the full finished prose; a passing gate checks bindings and attestations, not semantic truth. Changing the draft, source, or brief invalidates the review. Run the readiness checker before replacing or uploading the artifact. Existing prepared artifacts are dated history until rechecked; never rewrite submitted packets.

## Explicit private evidence export

The reusable plugin contains methods and validators, not a candidate's records. If a private evidence snapshot is requested, run `python3 scripts/build_portable_bundle.py --source-map /approved/private/sources.json --output /approved/private/new-export`. Both paths must be explicitly selected; there is no automatic career-folder discovery. The new output must be outside all source skills trees and enclosing plugin packages.

The JSON source map has `format: 1`, an authorized `owner`, and a nonempty `files` array. Each entry supplies an absolute `source`, a safe relative `destination`, and its exact `sha256`; optional `required` lists mandatory destinations. Pin only evidence authorized for this export. A stale hash, missing required source, path escape or existing output blocks it. The resulting `career-evidence.zip` is a private evidence snapshot with workflow copies for provenance; it is not an independently installable skill and requires the separately installed workflow and dependencies. The helper neither installs nor uploads it.
