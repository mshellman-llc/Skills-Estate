---
name: "resume-numbers-and-keywords"
description: "Wording method for Megan's tailored resume copy under career-application tailor: stated and estimated figures, rounding, posting keyword placement, bullet shape, ATS layout."
---

# Resume numbers and keywords

This skill supplies the wording method that `career-application` tailor step 11 leaves open. It does not choose the master, select programs or decide claims; those come from `00_Master/Career_Application_Operating_Context.md` and the role's `Role_Work_Record.md`, whose narrative translation table must be complete. If it is empty, stop and run `career-application tailor` first.

Before writing, load the operating context, the role work record, the master copy in the role folder, the live posting (if it is down, the record's posting snapshot, and say so), and `00_Master/Career_Narrative_Translation_Guide.md`. Claim authority is Professional_Profile → program records → `05_Reference/Claim_Governance/Career_Program_Evidence_Ledger.md`. Portfolio case studies are public copies and never a source for a resume figure.

## Two classes of figure

- Stated: an exact figure in Professional_Profile, a program record, the operating context or the evidence ledger (more than 90% of AMER Revenue Cloud delivery deals, 92 projects, $28.2M, the four $1M-plus deals, the $8.5M pipeline, the $7.6M CRM pursuit value, the $256,751 GoGuardian value). Megan prefers these approximated and rounded the same way as estimates: round to the nearest natural figure and signal it with one word inside the number ($7.6M → "~$7.5M", $256,751 → "about $250K", 92 projects → "90+ projects"). Keep the figure's stated scope, because the scope is what makes it true. No Estimate basis entry is needed, since the source already holds the exact value.
- Estimate: a figure built from inputs Megan has (counts, frequencies, durations, deal sizes, before-and-after timings, totals and her share). Megan wants these on the resume.

## Building an estimate

- Write the inputs and the arithmetic. Shapes: a range ("$1M–$2M deal values"), a bound ("20+ enterprise pursuits"), a share of a stated total ("about half of the $2.19M closed-won work"), frequency times period (5 workshops a month across 2025 → "about 60"), before and after with the baseline ("from about two weeks to half a day").
- Round to the nearest natural figure (nearest 5, 10, half or whole). When the arithmetic lands exactly between, keep the raw figure. Do not shade down for modesty or up for effect.
- Signal the estimate with one word inside the number: about, roughly, ~, +, or a range.
- A ledger qualifier on a figure is handled first by replacement with the verified result (the assessment became two signed SOWs and a paid change order, $256,751) and otherwise as one word inside the number ("a reported ~40%"). Never a clause, parenthetical or second sentence.
- Missing inputs: ask Megan one question for that bullet ("roughly how many pursuits a quarter?") and leave the bullet unnumbered until she answers.
- Record every estimate in the role work record under a new section `## Estimate basis`, placed after `## Resume source review`: bullet, figure, inputs, arithmetic, rounding. The readiness checker parses only the source review section, so the new section does not affect it. A figure reused on a second surface (LinkedIn, letter, interview) is promoted to the evidence ledger in a separate, explicit step; `career-materials-and-outreach` reads estimates from this section and makes none of its own.

## What belongs on the resume

- In: scale and outcome figures — dollars, portfolio size, cycles, attendees, time saved, contract value, deals, pipeline.
- Out, per Megan's October 7 direction: inventory counts — issues found, requirements written, capabilities listed, offers in a catalog, tests passing, skill counts; and every program-specific count the operating context bans (Meridian or agent-fleet adoption totals, department counts, respondent results, realized savings).
- Never headcount. People leadership is managed people leaders, hired, coached, ran performance reviews.
- Two figures per bullet. When a stated set of three or four belongs together, keep scope and result and drop the intermediate ("40+ pursuit teams, about $1.1M closed-won solution work led"; drop $7.6M pursued) rather than inventing a ratio.

## Keywords

Megan wants posting keywords on the resume, placed by judgment: an exact-match search finds each critical term, a hiring reader sees ordinary sentences.

- Extract in four groups: role identity (title nouns, function); platforms and methods (Salesforce Revenue Cloud, CPQ, Billing, quote-to-cash, Agentforce, integration, named AI tooling); outcomes the posting measures (adoption, cycle time, platform roadmap, budget); leadership verbs the posting repeats. A term is critical when it is in the title, the first three responsibilities, or repeated.
- Map each keyword to the evidence line where it is true. No evidence → a gap in the role work record for the letter or interview, and off the resume. Never add a tool, certification or title she does not hold.
- Headline and profile: the role-identity terms and the two or three platforms the role is built on, as sentences about what she led.
- Expertise line: the posting's exact phrasing for things she has done.
- Bullets: the keyword that names the work, in the most recent instance; rewrite around it only when the sentence stays accurate.
- Frequency: critical terms two or three times across the document, others once.
- Synonym precedence: the posting's term in the expertise line, her term once elsewhere, never both in one line. "Managed managers and individual contributors" is permitted where the source says people leaders.
- Internal names (Meridian, Linky, Playbook Universe) appear only with a plain description. Check exact phrases: "revenue recognition" is not matched by "rev rec"; "managing managers" is not matched by "leadership".

## Bullet shape

Each bullet names what Megan decided or owned, the mechanism she built or used, and the result, with plain verbs (led, designed, built, priced, decided, managed, hired, coached). Vary the order. End at the fact; a consequence gets its own sentence. No trailing "resulting in" or "ensuring", no power verbs (spearheaded, orchestrated, championed), no builder constructions, no X-not-Y. Solution and transformation roles keep one concrete client decision and one scaling mechanism, as the operating context requires. Titles and dates exactly as locked, month and year ("Feb 2026–Oct 2026").

## Layout and gate

Keep the master's typography; one or two pages as the router allows. ATS checks: standard section names, contact details in the body, no text boxes, images or content tables, standard fonts. Render to PDF and look at every page.

Apply `megan-writing-style` and the leadership-and-career section of `writing-integrity`. Where installed, run `/usr/bin/python3 ~/.agents/humanize/tellscan.py scan <file> --profile megan` and fix structure rather than swapping words; where not installed, check by reading and say no scan ran. Complete the resume source review receipt, run `06_System/career-application/scripts/check_role_resume_readiness.py`, update `03_Tracker/applications.md`, state `prepared locally`, and end with changed, verified, unchanged and the exact next action.

Method adapted from the open-source ResumeSkills set (resume-quantifier, resume-ats-optimizer, resume-bullet-writer, resume-formatter, executive-resume-writer), rewritten against the October 7, 2026 operating context.