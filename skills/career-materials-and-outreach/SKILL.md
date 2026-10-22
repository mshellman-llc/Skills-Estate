---
name: "career-materials-and-outreach"
description: "Draft the pieces around Megan's tailored resume (cover letter, form answers, outreach, LinkedIn sections, reference packets) from the role work record and current evidence, in her voice, as drafts only."
---

<!-- ESTATE-WRITING:BEGIN -->
Before writing, read the [writing standard](references/estate/writing.md). Apply it to every authored sentence. Review instructions and internal records too. Audience labels and file formats do not exempt prose from review.
<!-- ESTATE-WRITING:END -->


# Career materials and outreach

Runs beside `career-application` once a role has a work record with a completed narrative translation table; if the table is empty, run `career-application tailor` first. These pieces select from the same three or four programs the resume uses, so the resume and the letter say the same things.

Before drafting, load `00_Master/Career_Application_Operating_Context.md`, the role's `Role_Work_Record.md` (including its Estimate basis section), the tailored resume copy, the live posting, `00_Master/Professional_Profile.md`. Claim authority is Professional_Profile → program records → `05_Reference/Claim_Governance/Career_Program_Evidence_Ledger.md`; Portfolio case studies are public copies, not a source of figures. LinkedIn work starts from `00_Master/LinkedIn_Profile_Draft.md` and `00_Master/LinkedIn_Profile_Positioning_Brief.md`. Behavioral answers draw on `05_Reference/Story_Bank/Success_Stories.md` and the anchor stories in `04_Interview/Interview_Preparation.md`. References use `02_Templates/References_Template_One_Page.docx`.

Megan is the author. Before drafting, state audience, purpose, reader action and consequence level; hiring material gets deep review. Write under `megan-writing-style` and `writing-integrity`; run `/usr/bin/python3 ~/.agents/humanize/tellscan.py scan <file> --profile megan` on each finished file where installed, fix structure rather than swapping words, and say plainly when no scan ran.

## Rules for every piece

- Open with the point. Each sentence carries a name, number, system, decision or date.
- Posting keywords appear where they describe real work, once or twice a paragraph.
- People leadership is managed people leaders, hired, coached, ran performance reviews; no headcount.
- Figures are locked or stated figures from the sources above, or estimates already in the record's Estimate basis. Years-per-skill for a form field count as an estimate: compute from role dates, record in Estimate basis, then use.
- Employment ended October 1, 2026; nothing implies she is still at her former employer, and a current-employment answer matches the date of the action. Dates are month and year. No defensive narration about the exit or title history.
- Nothing employer-owned: no former-employer branding, client-sensitive facts, internal identifiers or repositories.
- Caveats stay in the ledger. Reader-facing copy states what is true and leaves out what is not; no "not verified", "directional" or "I don't claim" sentences.
- People stories: never invent a hiring, performance, termination or team-conflict case. If a prompt needs one and the sources hold none, mark the gap and ask Megan for a real event.
- Alignment flag in the record's Current decision (Axon's police and weapons business, for example) with Megan choosing to pursue: "why us" copy names the role's mandate and platform problem in her words and ties it to her stated reason for the move. Never a mission or values endorsement she has not said. If her reason line is missing, ask for it before drafting.

## Cover letter

250–350 words, four paragraphs, to a named person when WebSearch finds one, otherwise no salutation line.

1. The specific reason this role fits, tied to one program from the translation table.
2. Two or three posting requirements, each answered with one program, its mechanism and its result.
3. The largest real gap from the record answered with adjacent evidence, or the applied-AI work that distinguishes her in this lane; skipped when the gap is minor.
4. What she would want to discuss first.

No "I am excited to apply", no trait statements, no closing moral. Deliver one letter as a Codex doc; when a file is required, a DOCX beside the resume as `Megan_Shellman_<Company>_<Role>_Cover_Letter.docx`.

## Application-form answers

Answer the question asked, then stop; plain text ready to paste.

- Experience questions: skill, years, one sentence of where she used it; years match the resume.
- "Why this company or role": specific to the company, connected to her real work, under 150 words unless the field allows more; under an alignment flag, the rule above.
- Work samples: the most relevant publish-cleared case studies, one line each with link and one proof point.
- Behavioral prompts: 100–200 words from the anchor stories, ending on the result, under the people-story rule.
- Ratings and dropdowns: the accurate level.
- Pause with no draft: salary expectations, work authorization and sponsorship, demographic and self-identification questions, attestations and signatures.

Present answers as a table of field, answer, character count, field limit. Entering fields and submitting belong to `career-application fill` and its authorization boundaries.

## Outreach to a hiring manager or connection

Subject under eight words, specific to their team or the role. Body under 150 words: one specific about their work, one result of hers that bears on it, one ask (a twenty-minute conversation or a referral path). Link one case study. Cut any sentence that could go to another company. Draft only; a Gmail draft when she asks; sending and recruiter contact are separate approval boundaries.

## LinkedIn sections

Headline under 220 characters in the brief's resolved identity: Solution Engineering and Technical GTM leadership, applied AI as the differentiator. About: first person, three to five short paragraphs, opening with what she led and built, two or three named results, a closing line on what she wants only if she wants open-to-work visible. Experience entries carry the resume's titles, dates and figures exactly and may add context the resume cut. Skills: top three pinned to the lane she is prioritizing. Output is a section-by-section diff against the staged draft. Publication is Megan's action and a separate approval boundary.

## References

Megan names the references. For each: name, current title and company, relationship and the period they saw her work, the lane and claims they can speak to, contact details as she supplies them. Produce a permission request, a briefing note (the role, three things worth emphasizing, the evidence behind each) and a thank-you note, in her voice. The list lives in the role folder on the one-page template and is private.

## Recording

Write each piece's path and state into the role work record under Resume and materials; keep `03_Tracker/applications.md` current. States: `prepared locally` for a file; `filled and awaiting submission` only after `career-application fill`; `submitted` only with employer confirmation. End with changed, verified, unchanged and the exact next action.

Method adapted from the open-source ResumeSkills set (cover-letter-generator, application-form-filler, cold-email-writer, linkedin-profile-optimizer, reference-list-builder), rebuilt against the October 7, 2026 operating context.