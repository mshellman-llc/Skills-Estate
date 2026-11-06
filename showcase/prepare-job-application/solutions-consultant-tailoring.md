---
skill: prepare-job-application
title: Tailoring an application for a senior solutions consultant role
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: f445e838915a95dcf79bcf8a5fe4751ebe44f1201cd4943390c6e010c898b70e
---

## Request

Tailor Jordan Reyes's application for the Northbeam Analytics Senior Solutions Consultant posting: resume bullets and a short cover letter. The candidate record and posting are in ./inputs/. Do not submit anything.

## Inputs

Run of the built `prepare-job-application` task package. All inputs below are invented. The run had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so. Files it also produced, not shown here: `Role_Work_Record.md`.

#### candidate-record.md

#### Candidate record (fictional person, supplied for this task)

Name: Jordan Reyes. Location: Columbus, OH (open to remote).
Target: Senior Solutions Consultant roles at B2B SaaS companies.

Experience (dates and figures confirmed by the candidate):
- Solutions Consultant, Ardent Logistics Software (2021–present). Ran 120+ technical discovery calls and demos per year for a TMS product. Built a demo environment reused by 14 account executives. Supported deals totaling $8.2M in closed-won ACV in 2024. Wrote the RFP response library (240 answers) that cut average RFP turnaround from 9 to 4 business days.
- Implementation Consultant, Ardent Logistics Software (2018–2021). Led 22 customer implementations; average go-live 11 weeks. Trained 300+ end users.
- Operations Analyst, Midstate Freight (2015–2018). Built Excel/SQL reporting for a 40-terminal network.

Skills: SQL, REST APIs, Postman, Salesforce (admin cert 2020), Looker basics, demo storytelling.
Education: B.S. Supply Chain Management, Ohio State University, 2015.
Not true / do not claim: Python, people management, Snowflake.


#### job-posting.md

#### Senior Solutions Consultant — Northbeam Analytics (fictional posting)

Northbeam builds a supply-chain visibility and analytics platform for mid-market shippers and 3PLs.

You will:
- Partner with account executives on discovery, tailored demos and proofs of concept for VP-level buyers in logistics.
- Own technical win for deals from $80K–$400K ARR.
- Respond to RFPs and security questionnaires.
- Feed product with field insights.

You have:
- 5+ years in pre-sales or implementation for B2B SaaS, ideally logistics or supply chain.
- Comfort with APIs, data models and SQL.
- Experience with Snowflake or another cloud data warehouse (nice to have).
- Excellent presentation skills.

## Output

### Jordan Reyes — Northbeam Analytics, Senior Solutions Consultant

Recommendation: pursue. Jordan meets the 5+ years requirement (pre-sales and implementation since 2018) and has logistics, demo and RFP evidence. Two things in the posting have no support in the record, so they stay off the materials (see Gaps).

**Audience and purpose:** Northbeam hiring manager and recruiter. The goal is a screen. Consequence is high, so the review is deep. Accuracy comes first, and every figure is the candidate's stated figure, unrounded.

#### Resume bullets (tailored copy)

**Headline:** Senior Solutions Consultant — logistics and supply chain SaaS (TMS, RFPs, technical discovery and demos)
**Expertise:** Technical discovery · Tailored demos · Proofs of concept · RFP responses · SQL · REST APIs · Postman · Data models · Salesforce · Looker

*Note:* "Proofs of concept" and "Data models" are the posting's own terms, kept in the expertise line for ATS matching. The record does not describe either as work Jordan has done, so Jordan should confirm both or cut them before this goes anywhere.

**Solutions Consultant, Ardent Logistics Software (2021–present)**
- Run 120+ technical discovery calls and demos a year for a TMS product, partnering with account executives; supported deals totaling $8.2M in closed-won ACV in 2024.
- Built a demo environment that 14 account executives reuse.
- Wrote the RFP response library, 240 answers, and cut average RFP turnaround from 9 to 4 business days.

**Implementation Consultant, Ardent Logistics Software (2018–2021)**
- Led 22 customer implementations at an average go-live of 11 weeks.
- Trained 300+ end users.

**Operations Analyst, Midstate Freight (2015–2018)**
- Built Excel/SQL reporting for a 40-terminal network.

**Skills:** SQL, REST APIs, Postman, Salesforce (admin certified 2020), Looker
**Education:** B.S. Supply Chain Management, Ohio State University, 2015

#### Cover letter (about 280 words, four paragraphs)

No salutation line: no hiring manager is named in the posting, and I did not look outside the inputs.

> Northbeam's supply-chain visibility platform for mid-market shippers and 3PLs sits close to the work I have done at Ardent Logistics Software since 2018. As a Solutions Consultant on a TMS product, I run 120+ technical discovery calls and demos a year, and in 2024 I supported deals totaling $8.2M in closed-won ACV. Working with logistics buyers on discovery and demos is what I already do every week.
>
> The posting asks for tailored demos with account executives and RFP responses. I built a demo environment that 14 account executives reuse. I also wrote our RFP response library, 240 answers, and average RFP turnaround fell from 9 to 4 business days. Before pre-sales, I was an Implementation Consultant who led 22 customer implementations, averaged an 11-week go-live and trained 300+ end users. That work shows me what the buyer lives with after the demo, and I scope with that in mind.
>
> On the data side, I started in operations at Midstate Freight, where I built Excel/SQL reporting for a 40-terminal network. Today I work in SQL, REST APIs, Postman and Looker, and I hold a Salesforce admin certification (2020). That is the base I would bring to the data model and API questions that come up in technical evaluations.
>
> I would like to talk first about how Northbeam qualifies deals in the $80K–$400K ARR range, and what the technical win plan and first proof of concept look like when an account executive and a solutions consultant pick up a new opportunity together.
>
> Jordan Reyes
> Columbus, OH (open to remote)

#### Gaps and assumptions

| Posting item | Handling |
| --- | --- |
| Snowflake or another cloud warehouse (nice to have) | No evidence. Left off both documents. Adjacent: SQL, Excel/SQL reporting, Looker. |
| Security questionnaires | No evidence. The RFP library is the closest match, and the letter claims only the RFP work. |
| Owning technical win on $80K–$400K ARR deals | The record shows $8.2M supported ACV but no per-deal size or technical-win ownership. The letter says "supported", as the record does. |
| VP-level buyers, presentation skills | Not in the record. No claim made. |
| Field insights to product | Not in the record. No claim made. |
| Python, people management | Not claimed. |
| Why this move | Jordan's own reason was not supplied and there was no one to ask. The letter ties interest to the work only. Add one sentence in Jordan's words if there is a reason. |

- The 8-year span (2018 to now) is the only calculation. It appears only as "since 2018". Basis is in the work record.
- Jordan's confirmed writing-style profile was not supplied. The drafts follow the skill's writing rules (no filler openers, a number or system in each sentence), and I checked them by reading. No writing scan ran.

#### Process notes
- I could not run scripts. The readiness checker (`check_role_resume_readiness.py`) and the content-review receipt were not produced. The drafts are Markdown, not DOCX, so there was no rendering or ATS layout check. I checked the figures against the candidate record by hand.
- I did not search for a named recipient and I did not fill or submit anything.

#### State
- **Changed now:** four draft files created in `./out/`.
- **Verified:** every figure, title and date matches `candidate-record.md`. No Python, Snowflake or people-management claim appears.
- **Still unchanged:** no master resume, tracker or live record was touched. State is `prepared locally` (drafts). Nothing is filled or submitted.
- **Exact next action:** Jordan confirms whether "Proofs of concept" and "Data models" are real experience (otherwise cut them from the expertise line) and supplies a reason for the move. Then the text goes into the master resume layout as a DOCX, the readiness check runs, and Jordan decides whether to apply.

#### Files
- `out/Jordan_Reyes_Northbeam_Senior_Solutions_Consultant_Resume_Bullets.md`
- `out/Jordan_Reyes_Northbeam_Senior_Solutions_Consultant_Cover_Letter.md`
- `out/Role_Work_Record.md` (draft record with translation table and estimate basis)
- `out/answer.md`

### File: Jordan_Reyes_Northbeam_Senior_Solutions_Consultant_Resume_Bullets.md

**Headline:** Senior Solutions Consultant — logistics and supply chain SaaS (TMS, RFPs, technical discovery and demos)

**Expertise line:** Technical discovery · Tailored demos · Proofs of concept · RFP responses · SQL · REST APIs · Postman · Data models · Salesforce · Looker

**Solutions Consultant, Ardent Logistics Software (2021–present)**
- Run 120+ technical discovery calls and demos a year for a TMS product, partnering with account executives; supported deals totaling $8.2M in closed-won ACV in 2024.
- Built a demo environment that 14 account executives reuse.
- Wrote the RFP response library, 240 answers, and cut average RFP turnaround from 9 to 4 business days.

**Implementation Consultant, Ardent Logistics Software (2018–2021)**
- Led 22 customer implementations at an average go-live of 11 weeks.
- Trained 300+ end users.

**Operations Analyst, Midstate Freight (2015–2018)**
- Built Excel/SQL reporting for a 40-terminal network.

**Skills:** SQL, REST APIs, Postman, Salesforce (admin certified 2020), Looker
**Education:** B.S. Supply Chain Management, Ohio State University, 2015

### File: Jordan_Reyes_Northbeam_Senior_Solutions_Consultant_Cover_Letter.md

Northbeam's supply-chain visibility platform for mid-market shippers and 3PLs sits close to the work I have done at Ardent Logistics Software since 2018. As a Solutions Consultant on a TMS product, I run 120+ technical discovery calls and demos a year, and in 2024 I supported deals totaling $8.2M in closed-won ACV. Working with logistics buyers on discovery and demos is what I already do every week.

The posting asks for tailored demos with account executives and RFP responses. I built a demo environment that 14 account executives reuse. I also wrote our RFP response library, 240 answers, and average RFP turnaround fell from 9 to 4 business days. Before pre-sales, I was an Implementation Consultant who led 22 customer implementations, averaged an 11-week go-live and trained 300+ end users. That work shows me what the buyer lives with after the demo, and I scope with that in mind.

On the data side, I started in operations at Midstate Freight, where I built Excel/SQL reporting for a 40-terminal network. Today I work in SQL, REST APIs, Postman and Looker, and I hold a Salesforce admin certification (2020). That is the base I would bring to the data model and API questions that come up in technical evaluations.

I would like to talk first about how Northbeam qualifies deals in the $80K–$400K ARR range, and what the technical win plan and first proof of concept look like when an account executive and a solutions consultant pick up a new opportunity together.

Jordan Reyes
Columbus, OH (open to remote)
