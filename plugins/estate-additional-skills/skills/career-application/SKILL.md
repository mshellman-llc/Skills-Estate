---
name: career-application
description: "Prepare a role-specific application, supporting materials or interview work from current career authority. Preserve sourced resume figures, ATS methods and submission boundaries."
---

## Choose the requested task

Use the primary workflow below unless the request matches a mode in this table. For a matching mode, read its complete linked workflow and required references, then produce that mode's output. Preserve its calculations, failure handling and acceptance checks. One request does not require every mode.

| Requested mode | Complete workflow |
| --- | --- |
| supporting application materials | [career-materials-and-outreach](_runtime/career-materials-and-outreach/WORKFLOW.md) |
| resume figures and ATS wording | [resume-numbers-and-keywords](_runtime/resume-numbers-and-keywords/WORKFLOW.md) |



# Career application

Run one role at a time from current evidence without relying on conversation history.

## Start here

Use the live source when it is available:

`/Volumes/BeastMode/Career/`

Read `00_Master/Career_Application_Operating_Context.md` first. Then load only:

- the current live posting;
- the current role's `Role_Work_Record.md`, when one exists; and
- the source files named by the operating context for the current mode.

Do not load every prior application or reconstruct the full JobHunt folder unless a cross-surface correction requires it.

This estate package contains workflow instructions and validation code. Private career evidence, submitted applications, and resumes remain in the subject authority. If that source is unavailable, ask for the specific current evidence needed for the request or use an explicitly supplied dated bundle. Do not assume this package includes those private records. Return proposed record changes for the user to save when the live destination is unavailable.

## Invocation modes

Infer the mode from Megan's request. She can also state it directly.

- Codex: `$career-application assess <URL>`
- Claude Code: `/career-application assess <URL>`
- Claude chat or Cowork: enable **Career Application**, then say `Use Career Application to assess <URL>`.

- `$career-application assess <URL>`: verify the live posting, screen the role, and recommend pursue or skip.
- `$career-application find <criteria>`: find current roles, screen them, and return a shortlist. Do not create application folders until Megan chooses a role.
- `$career-application tailor <URL>`: create or update the role work record and a role-specific resume copy. Do not overwrite a master resume.
- `$career-application interview <company or role>`: build a role-specific leadership interview plan from the current posting and evidence-backed story bank.
- `$career-application fill <URL>`: open the form, fill supported factual fields, upload approved materials, and stop at the authorization boundaries below.
- `$career-application status <company or role>`: read the tracker and role work record, then report the verified state and next action.
- `$career-application continue <company or role>`: resume from the saved role work record rather than from prior chat history.

If the request does not specify a mode, use `assess` for a new URL and `continue` for a named existing role.

## Assess

1. Verify the employer's current posting. Treat reposts, aggregators, and old snapshots as secondary.
2. Screen leadership scope, decision authority, reporting shape, compensation, location, technical GTM or transformation relevance, and billable-delivery expectations.
3. Map requirements into four groups: strong evidence, transferable evidence, real gaps, and unsupported or unanswered questions.
4. Give a direct pursue or skip recommendation. Do not tailor materials for a skip.
5. When Megan explicitly chooses pursue or skip, update `03_Tracker/applications.md` in the live source. A skip needs no application folder unless notes would prevent repeated research. In a portable session, create an updated tracker copy for Megan instead of claiming the live tracker changed.

## Tailor and prepare

1. Create `01_Applications/Current/YYYY-MM-DD_Company_Role/` under the live source.
2. Copy `02_Templates/Role_Work_Record_Template.md` into that folder as `Role_Work_Record.md` and fill it from evidence.
3. Read `00_Master/Career_Narrative_Translation_Guide.md`. Map the role's three or four primary mandates to programs in the role record before drafting.
4. When the governed skill estate or Knowledge Hub is selected, read `00_Master/Governed_AI_Skill_Estate_and_Knowledge_Hub_Program_Record.md`. When the estate or an individual skill is selected, also read `00_Master/AI_Skill_Portfolio_Quality_and_Scaling_Record.md`. Keep the estate's reusable-method and distribution story separate from the Hub's bounded-context and persistence story. Select one or two role-relevant skills and preserve the problem, user, mechanism, risk-specific test, pivot or growth path, and verified state. Do not lead with skill or test counts.
5. For solution-engineering, technical-pre-sales, forward-deployed, architecture, value-engineering, Deal Desk, technical-GTM, customer-strategy, transformation, delivery, or recovery roles, read `00_Master/Client_Work_Strategy_and_Leadership_Record.md` and `00_Master/Solution_Engineering_Leadership_Evidence_Map.md`. Use `00_Master/GoGuardian_Program_Record.md` when that assessment-to-remediation sequence is selected. Choose at least one actual client decision and one portfolio, people, or practice mechanism. Keep 43 pursuit teams, 53 deal/project cycles, and 46 authored quotes distinct; the counts do not replace the case.
6. For product, platform, identity, security, or responsible-AI roles, read `00_Master/Linky_Product_Record.md` when Linky is selected. Keep local build and test proof separate from deployment, access, usage, and adoption.
7. For assessment, workforce, enablement, or people-system roles, read `00_Master/Assessment_Strategy_and_Enablement_Program_Record.md`. Preserve source-bank authorship, human-review boundaries, and the difference between built, published privately, shared, run, and adopted.
8. For each selected program, preserve the problem or decision, Megan's ownership, the mechanism, the evidence-backed result, and the real gap or state boundary. Retain the constraint or pivot when it proves leadership or judgment. For governed skills, distinguish original authorship, later estate governance or integration, and later contributor authorship; admission, repair, rename, or consolidation does not establish sole authorship of every package.
9. Select the base resume using the operating-context router. Copy it into the role folder before editing.
10. Before drafting, inventory relevant prior role-specific resumes and historical variants. Read the versions that cover the role mandate and note in the role work record what prior wording or layout to retain, revise, or exclude. Treat them as writing history, never as current claim authority; recheck carried claims against current evidence. A clipped read is incomplete.
11. Tailor only what the posting supports: headline, executive profile, expertise order, selected bullet order or wording, and technology emphasis. Intentional selection is required; do not collapse unrelated programs into one “AI tools” bullet, a platform list, or a playbook count; do not force the entire portfolio into the document.
12. Keep private evidence notes separate from employer-facing materials. Do not place client-sensitive facts, internal identifiers, repositories, or unsupported metrics in application files.
13. Apply Megan's `megan-writing-style` and `writing-integrity` rules. Run `/usr/bin/python3 ~/.agents/humanize/tellscan.py scan <file> --profile megan` as a deterministic gate where it is installed, not as permission to flatten real resume lists.
14. Render and inspect every changed DOCX. Verify accessibility and document integrity. Separately read the finished copy against the role mandate and evidence map; layout review does not prove content quality.
15. Complete the `Resume source review` receipt in the role work record and run `scripts/check_role_resume_readiness.py` against that record before calling a tailored resume prepared locally. The checker verifies a completed receipt and readable files, not the truth or quality of its prose; perform the content review yourself.
16. Update the role work record and tracker with the exact local state. When the source is unavailable, use a supplied role-work-record template or clearly label a new draft record and return it for the user to save.

## Prepare for interviews

1. Verify the current posting and read the role work record. Do not prepare from a remembered title or an expired posting when a live source is available.
2. Read `00_Master/Leadership_Interview_Evidence_Map.md`, `04_Interview/Interview_Preparation.md`, and `05_Reference/Story_Bank/Success_Stories.md`. Add only the program records needed for the role's primary mandates.
3. Translate the posting into five or six likely decision areas: business ownership, technical or solution judgment, executive influence, delivery or recovery, people leadership, and adversity or learning. Do not turn the result into a generic question dump.
4. Select no more than six anchor stories. For each one, prepare a 30-second headline, a two-minute causal answer, likely follow-ups, the difficult decision or conversation, the turnaround mechanism, the result, and the evidence boundary.
5. Use the order: problem or stakes, Megan's mandate, decision, mechanism, resistance or constraint, turning point, evidence-backed result, and learning. Name what changed because of Megan rather than only describing the artifact.
6. Preserve ownership boundaries. Do not claim that Megan performed every delivery task, that forecast value was realized, that UAT equals production, or that an opportunity became a win without evidence.
7. Do not fabricate a direct-report performance case, hiring decision, promotion decision, team-conflict case, or quantified adoption result. If a target role is likely to test one of those areas, mark it as an evidence gap and ask Megan for a real event before drafting the answer.
8. Keep closed corrective-action history out of routine preparation. Use it only if Megan explicitly chooses that material for a specific answer.
9. Save role-specific interview work inside the application folder. Do not overwrite the master interview book for one employer.

## Fill and submit

Filling an application does not authorize submission.

Fill supported factual fields and upload reviewed files. Pause for Megan on:

- salary expectations;
- unconfirmed work authorization or sponsorship answers;
- demographic or self-identification questions;
- legal attestations, signatures, and acknowledgments;
- MFA and CAPTCHA; and
- the final Submit action.

Submit only when Megan explicitly authorizes that specific application. After submission, capture the confirmation or receipt and record it in `Role_Work_Record.md` before marking the tracker `Submitted`.

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
- Do not lower the role target simply because a technically adjacent position is available.
- Do not publish, message recruiters, or submit an application unless Megan asks for that action.
- Do not treat remembered role details as current when the live posting can be checked.
- Treat uploaded bundle files as private personal career material. Do not share or publish the skill or its assets.

## Audience and content review gate

Before drafting, declare the audience, document purpose, intended reader action, author voice, and consequence level. These determine style, density, terminology, and prose-review depth. Internal updates use light review; hiring, public portfolio, client proposals, and consequential work use deep review. Accuracy and privacy are required at every depth. Do not apply a word blacklist or AI-detector scoring.

For a résumé, retrieve the career foundation and relevant prior résumé before selecting examples. Preserve career progression and leadership scope; record audience-specific reasons for other omissions. A portfolio handout is a separate purpose and must not replace a résumé. Choose length after selecting substantive coverage.

The source-review section must include `Content review` pointing to an absolute JSON receipt. The receipt contains `artifact_sha256` for the entire DOCX, `brief`, `review`, and `source_files` with IDs, absolute paths, exact file SHA256 hashes, and snapshot revisions. `review` binds the exact DOCX paragraph text hash, pins all reviewed sources, names the reviewer, supplies exact draft excerpts for required coverage, and separately records accuracy, representation, writing, and layout reviews with concrete notes. The shared `content-review.ts` module supplies the schema, required dimensions, and audience-derived depth. Review the full finished prose; a passing gate checks bindings and attestations, not semantic truth. Changing the draft, source, or brief invalidates the review. Run the readiness checker before replacing or uploading the artifact. Existing prepared artifacts are dated history until rechecked; never rewrite submitted packets.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
