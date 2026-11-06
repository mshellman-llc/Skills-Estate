---
skill: capture-requirements
title: Requirements backlog from a credit union onboarding workshop
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 285e48420fc2c355305c7d5a5a4e628065fa489f69c5589bda1f3fb2c7c784c9
---

## Request

Turn these Cedar & Pine Credit Union onboarding workshop notes into the requirements backlog: epics, capabilities, user stories with Gherkin acceptance criteria. Notes are in ./inputs/. Produce the workbook if your tools allow, and show the backlog content in your answer.

## Inputs

Run of the built `capture-requirements` task package. All inputs below are invented. The run had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so. Files it also produced, not shown here: `epics.csv`, `gap-list.md`, `requirements.csv`.

#### workshop-notes.md

#### Cedar & Pine Credit Union — member onboarding workshop notes (fictional)

Date: (workshop 1 of 2). Attendees: Member Services lead (Aisha Grant), Compliance officer (Rob Lindqvist), Digital banking manager (Kai Nakamura), Branch manager (Sofia Mendes).

Goal: let new members open a membership and a first savings account online in under 10 minutes, instead of the current branch visit.

Discussion:
- Applicant enters personal details, SSN, address; identity verification through the existing KYC vendor ("VeriPass"). Rob: KYC must pass before any account number is issued. Manual review queue for VeriPass "refer" results, worked by Member Services within 1 business day.
- Eligibility: must live or work in one of 6 counties, or be a family member of a current member. Applicant self-attests; Member Services spot-checks 10%.
- Funding: initial $5 share deposit by debit card or ACH from an external account. Kai: ACH micro-deposit verification takes too long; prefer instant account verification through the existing aggregator.
- Disclosures: Truth in Savings disclosure and membership agreement must be presented and accepted before submission; store the version accepted.
- Joint owners: Sofia says 20% of branch openings are joint. Group agreed joint applications are phase two.
- Minors: out of scope; branch only.
- Notifications: email + SMS at submission, approval, and if more information is needed.
- Staff view: Member Services needs a queue of pending applications with KYC result, eligibility basis, and funding status.
- Reporting: Aisha wants daily counts of started, abandoned, submitted, approved, referred.
- Accessibility: must meet WCAG 2.2 AA (board requirement).
- Open question: does the core banking system accept account creation via API, or only batch file? Kai to confirm with vendor.

## Output

### Cedar & Pine Credit Union: online onboarding requirements backlog

The backlog has 9 epics under 3 capabilities and 22 requirements, all in Draft. Eighteen are Must Have, 2 Should Have, 2 Won't Have. Nine open questions are on a separate gap list. The biggest is G8: whether core banking accepts account creation by API or only by batch file.

#### What I could and could not do

- **No .xlsx workbook.** My tools here write text files only, and I could not run a script. I wrote the two tabs as CSV files that import directly into the two-tab layout (Epics, Requirements) from the skill's workbook format. The Epics file holds the live `=COUNTIF(Requirements!C:C, A2)` formulas. Those only calculate once both tabs sit in one workbook, so I did not recalculate anything.
- **Hierarchy review skipped.** The skill has you confirm the hierarchy and prefixes before drafting. No one was available, so the hierarchy and prefixes below are my proposal and are unconfirmed.
- **Checks not run.** I ran no writing checker, brand check or quality gate. I read the text once myself. Styling (default blue/white theme, dropdowns, filters) is not applied, because that happens when the workbook is built.
- **Source column added.** The skill asks for one when a source document exists. Every row cites the notes' bullet by topic, since the notes have no section numbers.
- **Priorities inferred.** Where the notes gave no signal I used the default (Must Have) and said so in the row's notes.

#### Proposed hierarchy

- **Business Need:** Let new members open a membership and a first savings account online in under 10 minutes instead of visiting a branch.

  - **Capability:** Online account opening

    - **Epic:** Online Application Intake [Prefix: **APP**]
      - Capture applicant details
      - Complete application in under 10 minutes
      - Exclude joint applications from this release
      - Exclude minor applicants

    - **Epic:** Membership Eligibility [Prefix: **ELG**]
      - Self-attest eligibility
      - Record eligibility basis
      - Spot-check 10% of self-attested eligibility

    - **Epic:** Identity Verification (KYC) [Prefix: **KYC**]
      - Verify identity through VeriPass
      - Withhold account number until KYC passes
      - Route VeriPass refer results to manual review

    - **Epic:** Initial Share Deposit Funding [Prefix: **FND**]
      - Fund share deposit by debit card
      - Fund share deposit by ACH
      - Verify external account instantly

    - **Epic:** Disclosures and Agreements [Prefix: **DSC**]
      - Require disclosure acceptance before submission
      - Store accepted document versions

    - **Epic:** Accessibility [Prefix: **ACC**]
      - Meet WCAG 2.2 AA

  - **Capability:** Applicant communication

    - **Epic:** Applicant Notifications [Prefix: **NTF**]
      - Notify applicant on submission
      - Notify applicant on approval
      - Notify applicant when more information is needed

  - **Capability:** Onboarding operations and oversight

    - **Epic:** Member Services Application Queue [Prefix: **OPS**]
      - Pending applications queue
      - Work referred applications within one business day

    - **Epic:** Onboarding Reporting [Prefix: **RPT**]
      - Daily onboarding counts

#### Epics tab

| Epic Name | Prefix | Capability | Business Need | Requirement Count |
|---|---|---|---|---|
| Online Application Intake | APP | Online account opening | New members must open a membership and first savings account online in under 10 minutes instead of visiting a branch. | 4 |
| Membership Eligibility | ELG | Online account opening | Only people who live or work in one of the 6 counties, or who are family of a current member, may join. | 3 |
| Identity Verification (KYC) | KYC | Online account opening | No account number may be issued until identity verification through VeriPass passes. | 3 |
| Initial Share Deposit Funding | FND | Online account opening | A new membership needs a $5 share deposit that the applicant can pay online without slow bank verification. | 3 |
| Disclosures and Agreements | DSC | Online account opening | The credit union must show it presented the Truth in Savings disclosure and membership agreement and that the applicant accepted them. | 2 |
| Accessibility | ACC | Online account opening | The board requires the online application to meet WCAG 2.2 AA. | 1 |
| Applicant Notifications | NTF | Applicant communication | Applicants applying without a branch visit need to know when the application is received, approved, or stalled. | 3 |
| Member Services Application Queue | OPS | Onboarding operations and oversight | Member Services must work pending and referred applications within one business day. | 2 |
| Onboarding Reporting | RPT | Onboarding operations and oversight | Member Services leadership needs daily visibility into how many applications start, stall, and complete. | 1 |

#### Requirements tab: summary

| Number | Name | As A | Priority | Source (workshop-notes.md) |
|---|---|---|---|---|
| APP-001 | Capture applicant details | Applicant | Must Have | Discussion: identity bullet |
| APP-002 | Complete application in under 10 minutes | Applicant | Must Have | Goal |
| APP-003 | Exclude joint applications from this release | Member Services lead | Won't Have | Discussion: joint owners bullet |
| APP-004 | Exclude minor applicants | Member Services lead | Won't Have | Discussion: minors bullet |
| ELG-001 | Self-attest eligibility | Applicant | Must Have | Discussion: eligibility bullet |
| ELG-002 | Record eligibility basis | Member Services representative | Must Have | Eligibility and staff view bullets |
| ELG-003 | Spot-check 10% of self-attested eligibility | Member Services representative | Must Have | Discussion: eligibility bullet |
| KYC-001 | Verify identity through VeriPass | Applicant | Must Have | Discussion: identity bullet |
| KYC-002 | Withhold account number until KYC passes | Compliance officer | Must Have | Discussion: identity bullet |
| KYC-003 | Route VeriPass refer results to manual review | Applicant | Must Have | Discussion: identity bullet |
| FND-001 | Fund share deposit by debit card | Applicant | Must Have | Discussion: funding bullet |
| FND-002 | Fund share deposit by ACH | Applicant | Must Have | Discussion: funding bullet |
| FND-003 | Verify external account instantly | Applicant | Should Have | Discussion: funding bullet |
| DSC-001 | Require disclosure acceptance before submission | Applicant | Must Have | Discussion: disclosures bullet |
| DSC-002 | Store accepted document versions | Compliance officer | Must Have | Discussion: disclosures bullet |
| ACC-001 | Meet WCAG 2.2 AA | Applicant using assistive technology | Must Have | Discussion: accessibility bullet |
| NTF-001 | Notify applicant on submission | Applicant | Must Have (default) | Discussion: notifications bullet |
| NTF-002 | Notify applicant on approval | Applicant | Must Have (default) | Discussion: notifications bullet |
| NTF-003 | Notify applicant when more information is needed | Applicant | Must Have (default) | Discussion: notifications bullet |
| OPS-001 | Pending applications queue | Member Services representative | Must Have | Discussion: staff view bullet |
| OPS-002 | Work referred applications within one business day | Member Services lead | Must Have | Discussion: identity bullet |
| RPT-001 | Daily onboarding counts | Member Services lead | Should Have | Discussion: reporting bullet |

Priority reasoning: KYC, disclosures and WCAG are stated as compliance or board requirements, so Must Have. FND-003 is a stated preference ("prefer"), so Should Have. RPT-001 is something Aisha "wants", with no must-language, so Should Have. Joint and minor applications are phase two or out of scope, so Won't Have.

#### Requirements tab: user stories and acceptance criteria

Every row is Status = Draft. "As A" is the persona, then the story reads "I want to … so that …".

##### APP: Online Application Intake

**APP-001 Capture applicant details** (Must Have). As an Applicant, I want to enter my name, SSN and address in the online application, so that I can apply without visiting a branch.

```gherkin
Scenario: Complete details accepted
  Given an applicant on the personal details step with no saved data
  When they enter a legal name, a 9-digit SSN and a residential address and select Continue
  Then the application advances to the eligibility step
  And the entered values are saved to the application record

Scenario: Required field missing
  Given an applicant on the personal details step
  When they leave the SSN blank and select Continue
  Then the application stays on the step
  And an error message names the SSN field

Scenario: Malformed SSN
  Given an applicant on the personal details step
  When they enter 12345 as the SSN and select Continue
  Then the application stays on the step
  And an error message states that the SSN must be 9 digits
```
Note: only "personal details, SSN, address" are named in the notes (G1).

**APP-002 Complete application in under 10 minutes** (Must Have). As an Applicant, I want to finish the membership and first savings account application in under 10 minutes, so that I do not need a branch visit.

```gherkin
Scenario: Application finished within target
  Given an eligible applicant with valid details, a debit card funding source and a VeriPass result of pass
  When they go from starting the application to the submission confirmation page
  Then the elapsed time is under 10 minutes

Scenario: Elapsed time is recorded
  Given an applicant starts an application
  When the application is submitted
  Then the start timestamp and submit timestamp are stored on the application record
```
Note: how the target is measured is undefined (G2). Excluding manual review time is my assumption.

**APP-003 Exclude joint applications from this release** (Won't Have). As the Member Services lead, I want joint applications left out of the first release and recorded for phase two, so that the first release stays limited to single-owner applications.

```gherkin
Scenario: No joint option offered
  Given an applicant on the application start page
  When they view the available application types
  Then no joint-owner option is shown
  And the page states that joint accounts are opened at a branch
```
Note: the group agreed joint is phase two; Sofia Mendes said 20% of branch openings are joint. The branch message is my assumption.

**APP-004 Exclude minor applicants** (Won't Have). As the Member Services lead, I want minor accounts kept out of the online application, so that minors are opened only at a branch.

```gherkin
Scenario: Minor directed to branch
  Given an applicant on the personal details step
  When they enter a date of birth that makes them under 18
  Then the application stops
  And the page states that minor accounts are opened at a branch
```
Note: the notes say "out of scope; branch only". Collecting date of birth and the age of 18 are my assumptions (G1).

##### ELG: Membership Eligibility

**ELG-001 Self-attest eligibility** (Must Have). As an Applicant, I want to state whether I live or work in one of the 6 counties or am a family member of a current member, so that the credit union can confirm I am eligible to join.

```gherkin
Scenario: Applicant attests county residence
  Given an applicant on the eligibility step
  When they select 'I live in one of the 6 counties' and confirm
  Then the application advances to the next step

Scenario: Applicant attests family membership
  Given an applicant on the eligibility step
  When they select 'I am a family member of a current member' and confirm
  Then the application advances to the next step

Scenario: Applicant meets no basis
  Given an applicant on the eligibility step
  When they select 'None of these apply'
  Then the application cannot be submitted
  And the page states that membership is limited to the 6 counties and family of current members
```
Note: the county list and family-relationship detail are missing (G5). The "none" outcome is inferred.

**ELG-002 Record eligibility basis** (Must Have). As a Member Services representative, I want to see which eligibility basis each applicant attested, so that I can review it in the queue and in a spot-check.

```gherkin
Scenario: Basis stored
  Given an applicant attests 'I work in one of the 6 counties'
  When the application is submitted
  Then the application record stores the eligibility basis as 'Works in county'

Scenario: Basis shown in queue
  Given a submitted application with eligibility basis 'Family member'
  When a Member Services representative opens the pending applications queue
  Then the row for that application shows 'Family member'
```

**ELG-003 Spot-check 10% of self-attested eligibility** (Must Have). As a Member Services representative, I want a 10% sample of applications flagged for an eligibility spot-check, so that the credit union can test self-attested eligibility.

```gherkin
Scenario: Sample flagged
  Given 100 applications were submitted with self-attested eligibility during the sampling period
  When the sampling period closes
  Then 10 of those applications are flagged 'Eligibility spot-check' in the queue

Scenario: Spot-check result recorded
  Given an application flagged for spot-check
  When a Member Services representative records the result as 'Confirmed' or 'Not confirmed'
  Then the result and the representative's name are stored on the application record
```
Note: sampling period, selection method and the "Not confirmed" follow-up are not stated (G5).

##### KYC: Identity Verification

**KYC-001 Verify identity through VeriPass** (Must Have). As an Applicant, I want my identity checked through VeriPass when I submit, so that the credit union can open my account in line with KYC rules.

```gherkin
Scenario: Identity data sent for verification
  Given a submitted application with name, SSN and address
  When the application enters identity verification
  Then the details are sent to VeriPass
  And the returned result (pass or refer) is stored on the application record

Scenario: VeriPass unavailable
  Given VeriPass does not respond
  When the application enters identity verification
  Then the application is held with status 'Verification pending'
  And no account number is issued
```
Note: the notes describe only a "refer" result besides a pass (G3). The unavailable scenario is inferred.

**KYC-002 Withhold account number until KYC passes** (Must Have). As the Compliance officer, I want no account number issued before VeriPass returns pass, so that no account exists for an unverified identity.

```gherkin
Scenario: Pass releases account number
  Given an application with a VeriPass result of pass
  When account creation runs
  Then an account number is issued and stored on the application record

Scenario: Refer blocks account number
  Given an application with a VeriPass result of refer
  When account creation runs
  Then no account number is issued

Scenario: Manual review approval releases account number
  Given an application with a VeriPass result of refer that a Member Services representative has approved
  When account creation runs
  Then an account number is issued
```
Note: Rob Lindqvist: "KYC must pass before any account number is issued." Treating a manual approval as a pass is my inference (G3). The core banking interface is unresolved (G8).

**KYC-003 Route VeriPass refer results to manual review** (Must Have). As an Applicant, I want to be told when my identity check needs manual review, so that I know the application has not failed.

```gherkin
Scenario: Refer result queued
  Given an application with a VeriPass result of refer
  When the result is received
  Then the application appears in the Member Services queue with status 'Referred'
  And the applicant sees a message that the application is under review

Scenario: Pass result not queued for review
  Given an application with a VeriPass result of pass
  When the result is received
  Then the application does not appear with status 'Referred'
```

##### FND: Initial Share Deposit Funding

**FND-001 Fund share deposit by debit card** (Must Have). As an Applicant, I want to pay the initial $5 share deposit by debit card, so that my membership is funded when I apply.

```gherkin
Scenario: Debit card accepted
  Given an applicant on the funding step with a valid debit card
  When they choose debit card and confirm the $5 share deposit
  Then a $5.00 charge is authorized
  And the funding status is 'Funded'

Scenario: Debit card declined
  Given an applicant on the funding step
  When the card issuer declines the $5 charge
  Then the funding status stays 'Not funded'
  And the applicant is offered another funding method
```
Note: whether funding comes before or after KYC is not stated (G4).

**FND-002 Fund share deposit by ACH** (Must Have). As an Applicant, I want to pay the initial $5 share deposit by ACH from an account at another institution, so that I can fund without a debit card.

```gherkin
Scenario: ACH funding initiated
  Given an applicant on the funding step with a verified external account
  When they choose ACH and confirm the $5 share deposit
  Then a $5.00 ACH debit is initiated against the external account
  And the funding status is 'Pending ACH'

Scenario: No verified external account
  Given an applicant on the funding step who has not verified an external account
  When they choose ACH
  Then they are taken to account verification before the ACH debit can be confirmed
```
Note: ACH return handling is not stated (G4).

**FND-003 Verify external account instantly** (Should Have). As an Applicant, I want my external account verified instantly through the existing aggregator, so that I do not wait for micro-deposits.

```gherkin
Scenario: Instant verification succeeds
  Given an applicant who chose ACH funding
  When they sign in to their bank through the aggregator and authorize account access
  Then the external account is marked 'Verified' in the same session
  And no micro-deposit is sent

Scenario: Aggregator cannot verify the account
  Given an applicant who chose ACH funding
  When the aggregator returns no verification for the account
  Then the external account is not marked 'Verified'
  And the applicant is offered debit card funding
```
Note: Kai Nakamura prefers this over micro-deposits. Whether micro-deposits stay as a fallback is undecided, so the debit-card fallback is my assumption (G4).

##### DSC: Disclosures and Agreements

**DSC-001 Require disclosure acceptance before submission** (Must Have). As an Applicant, I want to read and accept the Truth in Savings disclosure and membership agreement before I submit, so that I know the terms I am agreeing to.

```gherkin
Scenario: Both documents presented
  Given an applicant on the review step
  When the step loads
  Then the Truth in Savings disclosure and the membership agreement are both displayed

Scenario: Submission blocked until accepted
  Given an applicant who has not accepted both documents
  When they select Submit
  Then the application is not submitted
  And a message states that both documents must be accepted

Scenario: Submission allowed after acceptance
  Given an applicant who accepted both documents
  When they select Submit
  Then the application is submitted
```

**DSC-002 Store accepted document versions** (Must Have). As the Compliance officer, I want the version of each document the applicant accepted stored with the application, so that I can show what each member agreed to.

```gherkin
Scenario: Versions stored
  Given the Truth in Savings disclosure is version 3 and the membership agreement is version 5
  When an applicant accepts both and submits
  Then the application record stores 'Truth in Savings v3' and 'Membership agreement v5'
  And the acceptance date and time

Scenario: Later version does not change earlier record
  Given an application that stored 'Membership agreement v5'
  When version 6 of the membership agreement is published
  Then the stored record still shows 'Membership agreement v5'
```
Note: retention period is not stated (G7).

##### ACC: Accessibility

**ACC-001 Meet WCAG 2.2 AA** (Must Have). As an Applicant using assistive technology, I want to complete the whole application with a keyboard and screen reader, so that I can join without help from a branch.

```gherkin
Scenario: Keyboard-only completion
  Given an applicant using only a keyboard
  When they move through every step from start to confirmation
  Then every control can be reached and operated
  And focus is always visible

Scenario: Conformance audit
  Given the finished application flow
  When it is tested against WCAG 2.2 Level AA success criteria
  Then no failures remain open
```
Note: board requirement. Test method and tools are not stated.

##### NTF: Applicant Notifications

**NTF-001 Notify applicant on submission** (Must Have, default). As an Applicant, I want an email and SMS when I submit, so that I know the credit union received my application.

```gherkin
Scenario: Both messages sent
  Given an applicant with an email address and mobile number on the application
  When the application is submitted
  Then one email and one SMS are sent confirming receipt

Scenario: Send failure recorded
  Given the SMS provider rejects a message
  When the submission notification is sent
  Then the email is still sent
  And the failure is stored on the application record
```
Note: SMS consent is not addressed (G6).

**NTF-002 Notify applicant on approval** (Must Have, default). As an Applicant, I want an email and SMS when my application is approved, so that I know my membership is open.

```gherkin
Scenario: Approval messages sent
  Given an application that has been approved
  When the approval is recorded
  Then one email and one SMS are sent
  And the messages state the account number issued
```
Note: whether the account number may appear in an SMS is a security question (G6).

**NTF-003 Notify applicant when more information is needed** (Must Have, default). As an Applicant, I want an email and SMS if the credit union needs more information from me, so that I can respond and keep my application moving.

```gherkin
Scenario: More-information messages sent
  Given a Member Services representative marks an application 'More information needed'
  When the status is saved
  Then one email and one SMS are sent to the applicant
  And the messages state what is needed
```
Note: how the applicant returns the information is not stated (G3).

##### OPS: Member Services Application Queue

**OPS-001 Pending applications queue** (Must Have). As a Member Services representative, I want a queue of pending applications showing KYC result, eligibility basis and funding status, so that I can see which applications need action.

```gherkin
Scenario: Queue columns
  Given three applications are pending
  When a Member Services representative opens the queue
  Then each row shows the applicant name, KYC result, eligibility basis and funding status

Scenario: Approved applications leave the queue
  Given an application with status 'Approved'
  When a Member Services representative opens the queue
  Then the application is not listed as pending
```
Note: filters, sorting and who may see SSN data are not stated (G7).

**OPS-002 Work referred applications within one business day** (Must Have). As the Member Services lead, I want referred applications reviewed within 1 business day, so that applicants are not left waiting.

```gherkin
Scenario: Due time shown
  Given an application referred on Tuesday at 14:00
  When a Member Services representative views it in the queue
  Then the due time is Wednesday at 14:00

Scenario: Weekend rolls to next business day
  Given an application referred on Friday at 16:00
  When a Member Services representative views it in the queue
  Then the due time is Monday at 16:00

Scenario: Overdue flagged
  Given a referred application past its due time
  When a Member Services representative opens the queue
  Then the row is marked 'Overdue'
```
Note: the same-clock-time rule and the business-day calendar are my assumptions. Review outcomes are not described (G3).

##### RPT: Onboarding Reporting

**RPT-001 Daily onboarding counts** (Should Have). As the Member Services lead, I want daily counts of applications started, abandoned, submitted, approved and referred, so that I can track onboarding volume and drop-off.

```gherkin
Scenario: Daily counts produced
  Given applications with activity on 2026-03-02
  When the Member Services lead opens the daily report for 2026-03-02
  Then the report shows one count each for started, abandoned, submitted, approved and referred

Scenario: Day with no activity
  Given no applications had activity on a date
  When the Member Services lead opens the daily report for that date
  Then all five counts show 0
```
Note: "abandoned" has no definition yet (G2).

#### Gap list

None of these is a requirement row. Each needs an answer and a source before it enters the backlog.

| ID | Category | Question | Who can answer |
|---|---|---|---|
| G1 | Missing scope | Which fields does the application collect beyond name, SSN and address (date of birth, email, mobile number, ID document)? | Aisha Grant, Rob Lindqvist |
| G2 | Missing scope | How is the 10-minute target measured (median, 90th percentile, every application), and where do the clock start and stop? When is an application "abandoned"? | Aisha Grant, Kai Nakamura |
| G3 | Missing scope | What happens on a VeriPass result other than pass or refer? What outcomes can a reviewer choose, and does manual approval of a refer count as KYC passed? How does an applicant return requested information? | Rob Lindqvist, Aisha Grant |
| G4 | Missing scope | Does funding come before or after KYC? What happens on an ACH return? If the aggregator cannot verify an account, do micro-deposits stay as a fallback? Which aggregator? | Kai Nakamura, Rob Lindqvist |
| G5 | Missing scope | Which 6 counties? How is a family relationship described and checked? How is the 10% sample drawn, over what period, and what follows "Not confirmed"? | Rob Lindqvist, Aisha Grant |
| G6 | Unstated security rule | Is SMS opt-in consent needed? May the approval message carry the account number? | Rob Lindqvist |
| G7 | Undefined data ownership | How long are accepted-document versions and application data kept? Who can see SSN and KYC detail in the queue? | Rob Lindqvist |
| G8 | Unresolved integration | Does core banking accept account creation by API or only by batch file? (Open in the notes; Kai Nakamura is to confirm with the vendor.) A batch-only core may prevent issuing an account number during the session, which affects the 10-minute goal and the approval message. | Kai Nakamura |
| G9 | Missing scope | The notes cover workshop 1 of 2 and carry no date. Workshop 2 content is not available. | Aisha Grant |

There are no conflicting statements, since there is one source document.

#### Next step for you

Confirm or change the hierarchy and prefixes, then answer G3, G4 and G8 first. Those three change the most acceptance criteria. When you confirm, I can build the styled .xlsx in an environment that runs scripts, and export the Jira CSV. Per the skill's Jira rules, the export would leave out story points and leave out the gap-list items.

#### Files

- `out/epics.csv`: Epics tab (9 rows, COUNTIF formula in the Requirement Count column)
- `out/requirements.csv`: Requirements tab (22 rows, plus a Source column)
- `out/gap-list.md`: gap list G1 to G9
- `out/answer.md`: this answer
