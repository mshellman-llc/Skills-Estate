---
name: draft-application-materials
description: "Draft the pieces around the candidate's tailored resume (cover letter, form answers, outreach, LinkedIn sections, reference packets) from the role work record and current evidence, in the candidate’s voice, as drafts only."
---

Run this module's relative commands from the directory containing this WORKFLOW.md. Resolve that directory to an absolute path first. A command that explicitly names another working directory keeps that requirement. This file is a supporting workflow, not another installed skill entrypoint.



# Draft application materials

Use only the candidate identity, career records, thresholds, author profile and destinations explicitly supplied or authorized for this task. Record names below describe a suggested source map; resolve them under the confirmed career root or accept equivalent supplied records. None is a bundled personal default. Missing optional context does not block a bounded draft from supplied facts.

Runs beside `prepare-job-application` once a role has a work record with a completed narrative translation table; if the table is empty, run `prepare-job-application tailor` first. Select evidence for each piece’s question, audience and purpose. Keep facts consistent across materials without requiring the same examples or repeating the résumé.

Before drafting, load `00_Master/Career_Application_Operating_Context.md`, the role's `Role_Work_Record.md` (including its Estimate basis section), the tailored resume copy, the live posting, `00_Master/Professional_Profile.md`. Claim authority starts with the candidate’s corrections and confirmed facts, then original evidence and the claim ledger, then detailed program records. The professional profile is a summary for navigation; Portfolio case studies are public copies, not a source of figures. LinkedIn work starts from `00_Master/LinkedIn_Profile_Draft.md` and `00_Master/LinkedIn_Profile_Positioning_Brief.md`. Behavioral answers draw on `05_Reference/Story_Bank/Success_Stories.md` and the anchor stories in `04_Interview/Interview_Preparation.md`. References use `02_Templates/References_Template_One_Page.docx`.

the candidate is the author. Before drafting, state audience, purpose, reader action and consequence level; hiring material gets deep review. Write under `apply-author-style` with an explicitly supplied confirmed profile and `review-writing`; run the bundled writing diagnostics on each finished file where installed, fix structure rather than swapping words, and say plainly when no scan ran.

## Bounded drafts from supplied facts

When the user supplies the relevant role facts inline and asks for a short draft, deliver the requested prose using those facts. Keep its provisional state separate from submission readiness. Missing posting details limit role-specific claims; they do not require replacing a requested short letter with a paragraph outline. Omit an unsupported requirement, mechanism or recipient detail rather than filling a placeholder as though it were known. The user's requested length governs that bounded draft; the normal full-letter format applies when a complete application letter is requested.

## Rules for every piece

- Open with the point. Each sentence carries a name, number, system, decision or date.
- Use posting language where it describes real work; do not repeat terms to meet a frequency target.
- Preserve who did what and what was observed. Leading work does not establish personal design or implementation ownership. A named property such as retry-safe does not prove zero failures, a particular mechanism, or a production guarantee. Keep the source's trial, time and outcome qualifiers; an observed reduction does not mean elimination. Omit a missing mechanism rather than inventing one to complete a paragraph.
- State only supported people-leadership responsibilities and counts. Use the candidate’s supplied disclosure preferences; no headcount is implied by a title.
- Figures are locked or stated figures from the sources above, or estimates already in the record's Estimate basis. Years-per-skill for a form field count as an estimate: compute from role dates, record in Estimate basis, then use.
- Determine current employment from the supplied dated record. Preserve exact official dates and titles; do not infer current employment from an old resume. Keep exit history out unless it answers the request.
- Nothing employer-owned: no former-employer branding, client-sensitive facts, internal identifiers or repositories.
- Caveats stay in the ledger. Reader-facing copy states what is true and leaves out what is not; no "not verified", "directional" or "I don't claim" sentences.
- People stories: never invent a hiring, performance, termination or team-conflict case. If a prompt needs one and the sources hold none, mark the gap and ask the candidate for a real event.
- Alignment flag in the record's Current decision (for example, an industry the candidate has identified as a concern) with the candidate choosing to pursue: "why us" copy names the role's mandate and platform problem in the candidate’s words and ties it to the candidate’s stated reason for the move. Never a mission or values endorsement the candidate has not said. If the candidate’s reason line is missing, ask for it before drafting.

## Cover letter

250–350 words, four paragraphs, to a named person when WebSearch finds one, otherwise no salutation line.

1. The specific reason this role fits, tied to one program from the translation table.
2. Two or three posting requirements, each answered with one program, its mechanism and its result.
3. Use another relevant example or address a material question with supported adjacent evidence when that helps the hiring reader. No career category is a default differentiator.
4. What the candidate would want to discuss first.

No "I am excited to apply", no trait statements, no closing moral. Deliver one letter as a Codex doc; when a file is required, a DOCX beside the resume as `Candidate_Name_<Company>_<Role>_Cover_Letter.docx`.

## Application-form answers

Answer the question asked, then stop; plain text ready to paste.

- Experience questions: skill, years, one sentence of where the candidate used it; years match the resume.
- "Why this company or role": specific to the company, connected to the candidate’s real work, under 150 words unless the field allows more; under an alignment flag, the rule above.
- Work samples: the most relevant publish-cleared case studies, one line each with link and one proof point.
- Behavioral prompts: 100–200 words from the anchor stories, ending on the result, under the people-story rule.
- Ratings and dropdowns: the accurate level.
- Pause with no draft: salary expectations, work authorization and sponsorship, demographic and self-identification questions, attestations and signatures.

Present answers as a table of field, answer, character count, field limit. Entering fields and submitting belong to `prepare-job-application fill` and its authorization boundaries.

## Outreach to a hiring manager or connection

Subject under eight words, specific to their team or the role. Body under 150 words: one specific about their work, one result of the candidate’s that bears on it, one ask (a twenty-minute conversation or a referral path). Link one case study. Cut any sentence that could go to another company. Draft only; a Gmail draft when the candidate asks; sending and recruiter contact are separate approval boundaries.

## LinkedIn sections

Headline under 220 characters, selected for the current brief and supported work. A prior headline or positioning correction does not establish a permanent professional identity. About: first person, three to five short paragraphs, opening with what the candidate led and built, two or three named results, a closing line on what the candidate wants only if the candidate wants open-to-work visible. Experience entries carry the resume's titles, dates and figures exactly and may add context the resume cut. Skills: top three pinned to the lane the candidate is prioritizing. Output is a section-by-section diff against the staged draft. Publication is the candidate's action and a separate approval boundary.

## References

the candidate names the references. For each: name, current title and company, relationship and the period they saw the candidate’s work, the lane and claims they can speak to, contact details as the candidate supplies them. Produce a permission request, a briefing note (the role, three things worth emphasizing, the evidence behind each) and a thank-you note, in the candidate’s voice. The list lives in the role folder on the one-page template and is private.

## Recording

Write each piece's path and state into the role work record under Resume and materials; keep `03_Tracker/applications.md` current. States: `prepared locally` for a file; `filled and awaiting submission` only after `prepare-job-application fill`; `submitted` only with employer confirmation. End with changed, verified, unchanged and the exact next action.
