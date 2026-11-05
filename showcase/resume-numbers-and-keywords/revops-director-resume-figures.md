---
skill: resume-numbers-and-keywords
title: Resume figures and keywords for a revenue operations director posting
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: bac682d878466ed29e02267f52a0adf61978ceb3b10d68ecd529552388ada4dd
---

## Request

Please rewrite the experience bullets on my tailored resume for the Director of Revenue Operations posting so the numbers are right and the posting's keywords show up where they're true. I'm fine with rounded or estimated figures if the basis holds up; my evidence notes and the posting are attached.

## Inputs

Run of the built `career-application` task package in its "resume figures and ATS wording" mode. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### evidence_notes.md

#### Evidence notes — Dana Whitlock (contact: dana.whitlock@example.com)

##### Locked titles and dates
- Senior Revenue Operations Manager, Harbor Analytics, Mar 2021–Present
- Sales Operations Manager, Brightfield Software, Jun 2017–Feb 2021

##### Ledger (claim authority)
1. Led the CPQ rollout on Salesforce for 140 sellers at Harbor. Quote turnaround went from 3 days to 4 hours. Source: program record, exact.
2. Billing automation at Harbor: forecast saving $1.8M a year (forecast, Jan 2023). Finance sign-off, Feb 2025: $1.3M realized in FY2024.
3. Deal desk at Harbor, which I run: reviewed non-standard quotes at an average of 23 a month through 2025. Set the discount approval matrix.
4. I manage 2 managers and 5 individual contributors in Revenue Operations (disclosure approved).
5. Brightfield: rebuilt the pipeline report used in the weekly forecast call; no figures recorded.
6. Forecast accuracy "improved" under my watch, no baseline or result in any record.

##### Other facts
- The Finance Systems team at Harbor (11 people) runs revenue recognition close. I work with them on handoffs; I don't manage them.
- Agentforce: I attended one vendor webinar. No hands-on work.
- Master resume headline: "Revenue operations leader".

#### posting.md

#### Director, Revenue Operations — Northvale Systems (posting, checked 2026-11-03)

Northvale sells subscription software to mid-market manufacturers. The Director owns revenue operations for a team of managers and individual contributors.

**Responsibilities**
- Own the quote-to-cash process from quote through invoice and revenue recognition handoff.
- Set the roadmap for Salesforce Revenue Cloud, including CPQ and Billing.
- Improve forecast accuracy and pipeline reporting with Sales and Finance.
- Manage managers and individual contributors across sales operations and deal desk.
- Run pricing and discount governance.

**Preferred**
- Hands-on exposure to Agentforce.
- Experience reducing quote cycle time.

## Output

I rewrote the experience bullets for the Northvale Director, Revenue Operations posting. I put in the figures your records support and the posting terms that are true for you. I left out four terms that aren't. The wording is a draft. I haven't produced a resume file or run the readiness check.

#### Bullets

**Headline:** Revenue Operations Leader

**Expertise:** Salesforce CPQ | Billing automation | Deal desk | Pricing and discount governance | Pipeline reporting | Managing managers and individual contributors

**Senior Revenue Operations Manager**, Harbor Analytics, Mar 2021–Present
- Led the Salesforce CPQ rollout for 140 sellers. Quote turnaround fell from 3 days to 4 hours.
- Led billing automation. Finance confirmed $1.3M in realized savings for FY2024.
- Run the deal desk: about 280 non-standard quotes reviewed a year, and I set the discount approval matrix.
- Manage 2 managers and 5 individual contributors in Revenue Operations. Hand closed deals to Finance Systems for revenue recognition.

**Sales Operations Manager**, Brightfield Software, Jun 2017–Feb 2021
- Rebuilt the pipeline report used in the weekly forecast call.

#### Decisions on the figures

- **CPQ (140 sellers, 3 days to 4 hours):** exact ledger figures, with the baseline kept.
- **Billing automation:** the ledger carries a $1.8M annual forecast from January 2023. Your February 2025 Finance sign-off gives $1.3M realized in FY2024. I replaced the forecast with the confirmed result and dropped the forecast.
- **Deal desk (about 280 a year):** this is an estimate. You gave an average of 23 reviews a month through 2025, and 23 × 12 = 276. At an increment of 10, 270 and 280 are 6 and 4 away from 276, so it rounds to 280. The exact figure stays in your notes. This is recorded in the estimate basis table in `out/resume_wording_northvale.md`, for your role work record.
- **Team size:** 2 managers and 5 individual contributors, as disclosed. The Finance Systems team's 11 people stay off the resume because you work with that team and don't manage it.

#### Keywords

Placed because your records show the work: deal desk, CPQ, billing automation, pricing and discount governance (you set the approval matrix), pipeline reporting, revenue recognition handoffs, and "managing managers and individual contributors" in the posting's wording.

Held back:
- **Agentforce:** you attended one webinar and did no hands-on work. It stays off the resume. The cover letter or an interview is the place to say so.
- **Salesforce Revenue Cloud:** your records name CPQ and billing automation, not Revenue Cloud. It stays off until you confirm it.
- **Quote-to-cash:** no record says you owned the whole process. It stays off until you confirm it.
- **Forecast accuracy:** ledger item 6 says it "improved" but has no baseline or result. I wrote no number.

#### Questions for you

1. Did you lead billing automation, or contribute to it? I used "Led" because it's in your own ledger, but the notes don't state your role. I'll soften the verb if you contributed.
2. Roughly what was forecast accuracy before and after your work? With a baseline and a result I can add a bullet. Without them it stays out.
3. Do you own the Revenue Cloud roadmap, or the process from quote through invoice? A yes on either lets me add the posting's exact phrase.

#### Checks and limits

- Titles and dates are as locked, in month-and-year form.
- No bundled scan ran, because I couldn't run scripts. I read the bullets by hand for trailing "resulting in" clauses, power verbs and hedged qualifiers, and found none.
- I couldn't run `check_role_resume_readiness.py`. There is no DOCX or role work record in this session, so the content-review receipt hasn't been done. The tracker is unchanged.

**Changed now:** resume wording and estimate basis drafted, with the status `researching` (not `prepared locally`).
**Verified:** each figure against the ledger; the one estimate's arithmetic and rounding.
**Still unchanged:** your master resume, the tracker, and any DOCX.
**Next action:** answer the three questions, then I update the bullets and you paste them into the role copy of the resume. After that the readiness checker can run.

#### Files

- `out/resume_wording_northvale.md`: the bullets above, the estimate basis table, and the gaps table (Agentforce, Revenue Cloud, quote-to-cash, forecast accuracy, Finance Systems headcount).

### File: resume_wording_northvale.md

#### Resume wording: Director, Revenue Operations (Northvale Systems)

##### Headline and expertise line

Revenue Operations Leader

Expertise: Salesforce CPQ | Billing automation | Deal desk | Pricing and discount governance | Pipeline reporting | Managing managers and individual contributors

##### Experience

**Senior Revenue Operations Manager**, Harbor Analytics, Mar 2021–Present
- Led the Salesforce CPQ rollout for 140 sellers. Quote turnaround fell from 3 days to 4 hours.
- Led billing automation. Finance confirmed $1.3M in realized savings for FY2024.
- Run the deal desk: about 280 non-standard quotes reviewed a year, and I set the discount approval matrix.
- Manage 2 managers and 5 individual contributors in Revenue Operations. Hand closed deals to Finance Systems for revenue recognition.

**Sales Operations Manager**, Brightfield Software, Jun 2017–Feb 2021
- Rebuilt the pipeline report used in the weekly forecast call.

##### Estimate basis

| Bullet | Figure | Inputs | Arithmetic | Rounding |
| --- | --- | --- | --- | --- |
| Harbor deal desk | about 280 a year | Average 23 non-standard quotes reviewed per month through 2025 (ledger 3) | 23 × 12 = 276 | Increment 10: 270 and 280 are 6 and 4 from 276, so 280. Exact source figure kept. |

##### Gaps (not on the resume)

| Posting term | Status |
| --- | --- |
| Agentforce | One vendor webinar, no hands-on work. Off the resume. Cover letter or interview gap. |
| Salesforce Revenue Cloud | Records name Salesforce CPQ and billing automation, not Revenue Cloud. Off until confirmed. |
| Quote-to-cash | No record says the candidate owned the full process. Off until confirmed. |
| Forecast accuracy | Ledger 6 has no baseline or result. Bullet left unnumbered and unclaimed. |
| Finance Systems headcount (11) | Not the candidate's team. Excluded. |
