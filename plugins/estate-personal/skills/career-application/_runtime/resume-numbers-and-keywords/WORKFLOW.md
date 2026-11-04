---
name: "resume-numbers-and-keywords"
description: "Wording method for the candidate's tailored resume copy under career-application tailor: stated and estimated figures, rounding, posting keyword placement, bullet shape, ATS layout."
---

Run this module's relative commands from the directory containing this WORKFLOW.md. Resolve that directory to an absolute path first. A command that explicitly names another working directory keeps that requirement. This file is a supporting workflow, not another installed skill entrypoint.



# Resume numbers and keywords

Use only the candidate identity, career records, thresholds, author profile and destinations explicitly supplied or authorized for this task. Record names below describe a suggested source map; resolve them under the confirmed career root or accept equivalent supplied records. None is a bundled personal default. Missing optional context does not block a bounded draft from supplied facts.

This skill supplies the wording method that `career-application` tailor step 11 leaves open. It does not choose the master, select programs or decide claims; those come from `00_Master/Career_Application_Operating_Context.md` and the role's `Role_Work_Record.md`, whose narrative translation table must be complete. If it is empty, stop and run `career-application tailor` first.

Before writing, load the operating context, the role work record, the master copy in the role folder, the live posting (if it is down, the record's posting snapshot, and say so), and `00_Master/Career_Narrative_Translation_Guide.md`. Claim authority is Professional_Profile → program records → `05_Reference/Claim_Governance/Career_Program_Evidence_Ledger.md`. Portfolio case studies are public copies and never a source for a resume figure.

Before combining facts in a bullet, verify that the source explicitly connects the actor, work, figure and period. Separate records for a team activity and a candidate's platform experience do not establish that the candidate led that activity or that it used that platform. An unnamed team's count stays off the candidate's bullet until ownership is supported.

Paths such as `00_Master/`, `03_Tracker/` and `06_System/` name records under the user's confirmed Career root; they are not relative to the installed skill directory. Resolve needed records to absolute paths from that confirmed root. The packaged checker is a separate executable resource, linked in the final step below.

## Two classes of figure

- Stated: an exact figure in the supplied professional profile, program record or evidence ledger. Preserve its unit, scope, period and precision. If the candidate requests rounding, document the convention and keep the exact source figure. Synthetic illustration: 78 completed test cases may be written as “about 80” only when that level of precision fits the claim.
- Estimate: a figure calculated from supplied inputs such as counts, frequencies, durations, deal sizes, before-and-after timings, totals and attributable share. Use an estimate only when the candidate wants it and the basis is defensible.

## Building an estimate

- Write the inputs and the arithmetic. Shapes: a range ("$1M–$2M deal values"), a bound ("20+ enterprise pursuits"), a share of a stated total ("about half of the synthetic $120K total"), frequency times period (5 workshops a month across 2025 → "about 60"), before and after with the baseline ("from about two weeks to half a day").
- Round to the nearest natural figure (nearest 5, 10, half or whole). When the arithmetic lands exactly between, keep the raw figure. Do not shade down for modesty or up for effect. For the chosen increment, calculate the adjacent lower and upper values and compare their distances from the raw figure. A supported 23 rounds to about 25 at an increment of five: distances are 3 and 2; the midpoint is 22.5. Keep the original unit and period. This changes presentation, not the source figure, and is not a new estimate.
- Signal the estimate with one word inside the number: about, roughly, ~, +, or a range.
- A ledger qualifier on a figure is handled first by replacement with the verified result (for example, replacing a forecast with the supplied confirmed result) and otherwise as one word inside the number ("a reported ~40%"). Never a clause, parenthetical or second sentence.
- Missing inputs: ask the candidate one question for that bullet ("roughly how many pursuits a quarter?") and leave the bullet unnumbered until the candidate answers.
- Record every estimate in the role work record under a new section `## Estimate basis`, placed after `## Resume source review`: bullet, figure, inputs, arithmetic, rounding. The readiness checker parses only the source review section, so the new section does not affect it. A figure reused on a second surface (LinkedIn, letter, interview) is promoted to the evidence ledger in a separate, explicit step; `career-materials-and-outreach` reads estimates from this section and makes none of its own.

## What belongs on the resume

- In: scale and outcome figures — dollars, portfolio size, cycles, attendees, time saved, contract value, deals, pipeline.
- Exclude counts the candidate or rights ledger prohibits. Inventory counts can describe scale when they matter to the role, but must not stand in for a supported outcome.
- State people-leadership responsibilities and headcount only when evidence and disclosure authority support them.
- Prefer the figures that explain scope and outcome. Do not invent a ratio merely to compress several unrelated counts.

## Keywords

the candidate wants posting keywords on the resume, placed by judgment: an exact-match search finds each critical term, a hiring reader sees ordinary sentences.

- Extract in four groups: role identity (title nouns, function); platforms and methods (Salesforce Revenue Cloud, CPQ, Billing, quote-to-cash, Agentforce, integration, named AI tooling); outcomes the posting measures (adoption, cycle time, platform roadmap, budget); leadership verbs the posting repeats. A term is critical when it is in the title, the first three responsibilities, or repeated.
- Map each keyword to the evidence line where it is true. No evidence → a gap in the role work record for the letter or interview, and off the resume. Never add a tool, certification or title the candidate does not hold.
- Headline and profile: the role-identity terms and the two or three platforms the role is built on, as sentences about what the candidate led.
- Expertise line: the posting's exact phrasing for things the candidate has done.
- Bullets: the keyword that names the work, in the most recent instance; rewrite around it only when the sentence stays accurate.
- Frequency: critical terms two or three times across the document, other once.
- Synonym precedence: the posting's term in the expertise line, the candidate’s term once elsewhere, never both in one line. "Managed managers and individual contributors" is permitted where the source says people leaders.
- Internal project names appear only with a plain description. Check exact phrases: "revenue recognition" is not matched by "rev rec"; "managing managers" is not matched by "leadership".

## Bullet shape

A bullet format cannot supply missing evidence. If the source establishes experience with API design but no ownership or leadership, retain that level of claim; do not add led, designed, built or managed. Record missing ownership, mechanism and outcome as gaps instead of presenting an invented achievement with placeholders.

When supported by evidence, a bullet names what the candidate decided or owned, the mechanism the candidate built or used, and the result. When those elements are absent, keep a bounded activity or experience statement and record the missing evidence separately. Use plain verbs (led, designed, built, priced, decided, managed, hired, coached). Vary the order. End at the fact; a consequence gets its own sentence. No trailing "resulting in" or "ensuring", no power verbs (spearheaded, orchestrated, championed), no builder constructions, no X-not-Y. Solution and transformation roles keep one concrete client decision and one scaling mechanism, as the operating context requires. Titles and dates exactly as locked, month and year (for example, the synthetic span “Mar 2023–Jun 2024”).

## Layout and gate

Keep the master's typography; one or two pages as the router allows. ATS checks: standard section names, contact details in the body, no text boxes, images or content tables, standard fonts. Render to PDF and look at every page.

Apply `author-writing-style` with an explicitly supplied confirmed profile and the leadership-and-career section of `writing-integrity`. Where installed, run the bundled writing diagnostics and fix structure rather than swapping words; where not installed, check by reading and say no scan ran. Complete the resume source review receipt, resolve the [packaged readiness checker](../../scripts/check_role_resume_readiness.py) from this workflow's location and run it with Python, passing the absolute path to `Role_Work_Record.md` as its single positional argument, update `03_Tracker/applications.md`, state `prepared locally`, and end with changed, verified, unchanged and the exact next action.

Method adapted from the open-source ResumeSkills set (resume-quantifier, resume-ats-optimizer, resume-bullet-writer, resume-formatter, executive-resume-writer), rewritten against the candidate’s confirmed operating context.