---
name: assess-career-options
description: "Assess a role, the whole tracker or an offer against the candidate's chosen progression path and gates; prepare salary negotiation; compare offers side by side. The candidate decides."
---


# Assess career options

Use only the candidate identity, career records, thresholds, author profile and destinations explicitly supplied or authorized for this task. Record names below describe a suggested source map; resolve them under the confirmed career root or accept equivalent supplied records. None is a bundled personal default. Missing optional context does not block a bounded draft from supplied facts.

Runs beside `prepare-job-application`. Four jobs: a progression check on one role, a portfolio view across the tracker, negotiation prep once a number is in play, and an offer comparison. The candidate decides; this skill produces facts and drafts.

Before starting, load `00_Master/Career_Application_Operating_Context.md` (target-role screen, current career direction), the role's `Role_Work_Record.md`, `03_Tracker/applications.md`, `05_Reference/Career_Strategy/Career_Paths.md`, and the live posting or written offer. The prepare-job-application assess screen still runs; this adds the level view the operating context asks for.

## Gates

Show each result; a failed gate is never averaged into a score.

- Use the candidate’s supplied minimum and target base compensation, with currency and location. If thresholds or posted base are missing, record an open question; do not invent a default.
- Apply the candidate’s explicit billability preference and threshold, including whether equality passes. Unknown billability remains unresolved; never infer zero from a title, presales work or contract. Internal platform ownership is not necessarily billable delivery.
- Compare actual role responsibilities with the candidate’s chosen leadership or individual-contributor path. An architecture title alone neither passes nor fails that screen.
- Scope: compare actual decision authority with the candidate’s supplied history and target, not title labels. Unknown scope remains unresolved.
- Alignment: record any flag the candidate or the research raised (industry, customers, politics) as a line under the record's Current decision, with the candidate’s stated reason when the candidate chooses to pursue. Recorded, never scored.

## Progression matrix

The destination is the candidate’s confirmed progression goal. Do not assume an executive path. For each criterion selected in the supplied operating context (for example, technical or strategic scope, decision authority, impact, sponsorship and advancement; add budget or people leadership only when relevant) record one of three states: verified (an employer statement in the posting, offer letter or interview), inferred (plausible from role shape, labeled), unknown. A Director title, a VP reporting line or a recruiter's promise is inferred at most; a promotion is verified only in writing.

Score verified 2, inferred 1, unknown 0 per criterion, weighted. Weights are the candidate’s; ask once and record them in the operating context. Equal weights may be shown as an explicitly provisional scenario until confirmed. Report the three column counts beside the score so a high score built on inference is visible. Keep the matrix in the record under Screen and update it after every interview round.

Use the chosen path to interpret role signals. For a people-leadership target, investigate authority over hiring, budget and direct reports; for a senior individual-contributor target, investigate technical decision authority, scope, sponsorship and advancement without management. Hands-on work, an architect title, reporting below VP or having no direct reports is not inherently a red flag. Flag a mismatch with the candidate's confirmed goals, undisclosed delivery obligations or two jobs hidden in one posting. Investigate compensation described only as "competitive" or "DOE", and equity-heavy offers with no stated base.

Choose discovery questions that resolve the candidate's gaps: who held the role and where they went, which decisions it owns, how performance and advancement are evaluated, and any expected billable share. Ask leadership-specific budget, hiring and executive-access questions only for a chosen leadership path.

## Portfolio view

On request, run the gates and the matrix across every nonterminal row in the tracker and add one line per role on lane coherence against the primary identity in `Career_Paths.md` (the candidate’s supplied function, differentiator and domain foundation). Note where an in-house IT seat, a RevOps lens or a consulting title pulls away from that identity. When a role closes, record why in its work record so the next search learns from it.

## Negotiation

- Research with WebSearch at each offer stage: posted bands for comparable roles at the candidate’s target level, function and location; the employer's own ranges; levels data where it exists. Cite source and date. Without search, use the employer's posted range with a dated note.
- The candidate supplies the number. Draft nothing for a salary field or a recruiter's expectations question until the candidate gives a figure. Default, which the candidate can change: do not disclose past pay.
- Counter on base first. Secondary levers in the order that serves the destination: a title appropriate to the chosen path, written scope and decision authority, a dated level review, signing bonus, equity, start date, remote and travel terms, and relevant resources or sponsorship. A verbal promise not in the offer letter stays unknown.
- Deliver a counter email and a call script with answers to "this is our best offer", "the band is fixed" and "we need an answer by Friday", in the candidate's voice. Drafts only; the candidate sends or says it.

## Offer comparison

Ask for these inputs before building:

- base;
- target bonus and realistic attainment;
- equity with valuation assumption, vesting and cliff;
- signing bonus;
- benefits differences;
- relocation;
- travel and office days;
- expected billability;
- reporting line and title;
- anything verified in writing about promotion.

Show base apart from everything else, with a year-one and a four-year view. Lay out the gates per offer, the matrix with its three columns, the weighted score, the strongest case for each offer and the open questions on each. Do not pick. Use the host’s supported spreadsheet output for multiple offers or scenarios and its document output for a single offer. If that tool is unavailable, deliver a complete readable table with its calculations and evidence, and state the unavailable export. Save once under `03_Tracker/` with a pointer from each role folder. Tracker status (`offer`, `closed`) changes only on the candidate's word.

## Reporting

Everything the candidate reads or sends goes through `apply-author-style` with an explicitly supplied confirmed profile and `review-writing`, and the bundled writing diagnostics where installed; otherwise check by reading and say no scan ran. Update the role work record and tracker. End with changed, verified, unchanged and the exact next action.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
