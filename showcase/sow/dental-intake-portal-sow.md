---
skill: sow
title: Statement of work for a dental group intake portal
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 4e4d47135eda6b0e5bf6fabff30693368ad61984e4761e705d038d935fcf7db3
---

## Request

Draft the statement of work for the Brightwell Dental Partners intake portal from the confirmed scope, quote and contract profile in ./inputs/.

## Inputs

Run of the built `statement-of-work` task package. All inputs below are invented. The run had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### confirmed-scope.md

#### Brightwell Dental Partners — confirmed scope (fictional)

Client: Brightwell Dental Partners, LLC, a group of 11 dental offices in Ohio.
Provider: Harbor Lane Consulting, LLC (fictional consultancy).
Project: Online new-patient intake portal.

In scope:
1. Discovery and design: 2 workshops, intake form design for adult and pediatric patients, accessibility review to WCAG 2.2 AA.
2. Build: web intake form (responsive), insurance card photo upload, e-signature on consent forms, integration that pushes completed intake to the practice-management system "DentaCore" via its import API.
3. Testing: QA, one round of user acceptance testing with 2 pilot offices.
4. Launch: pilot in 2 offices, then rollout to all 11; staff training (2 remote sessions, recorded).
5. Hypercare: 30 days after full rollout.

Out of scope: appointment scheduling, payments, DentaCore configuration changes, translation beyond English and Spanish form text supplied by the client.

Client responsibilities: provide DentaCore API sandbox access by week 2; named product owner (Operations Director, Lena Ortiz); Spanish translations of form text; pilot office availability.

Assumptions: DentaCore import API supports the required fields; no PHI stored outside DentaCore and the HIPAA-eligible hosting the client already licenses.


#### contract-profile.md

#### Contract profile (fictional)

- Governing agreement: Master Services Agreement between the parties dated March 3, 2026 (assume standard MSA terms; this SOW should reference it, not restate it).
- Acceptance: deliverables deemed accepted 10 business days after delivery unless the client gives written notice of a material nonconformance.
- Business Associate Agreement: in place, dated March 3, 2026.


#### quote.md

#### Quote (fictional) — fixed fee by milestone

| Milestone | Amount (USD) |
|---|---|
| M1 Discovery and design accepted | 18,000 |
| M2 Build complete, QA passed | 46,000 |
| M3 UAT accepted, pilot live | 22,000 |
| M4 Full rollout and training complete | 14,000 |
| Total | 100,000 |

Hypercare included. Timeline: 14 weeks from kickoff. Change requests billed at $175/hour on approved change orders.
Payment terms: net 30 from milestone acceptance.

## Output

I've drafted the Brightwell intake portal SOW as a Markdown file with its gaps visible. It is not approved or sent, and I couldn't produce a DOCX or run any checks in this session.

#### Route and limits

- **Document route, not the generator.** The quote is a USD 100,000 fixed fee split by milestone, with no roles, rates or hours. The generator needs per-role hours times rate to equal revenue, so it can't represent this agreement. I wrote the draft by hand from the three inputs and kept the fee as quoted.
- **No scripts or document tool.** I couldn't run `generate_sow.js`, `verify_contract.py`, the slop scan or the release-gate checks. The Markdown file is the editable draft; it still needs conversion to the Word template, a rendered-page check and the writing-integrity, brand and quality gates.
- **Contract wording kept.** The SOW references the MSA dated March 3, 2026 rather than restating it. It uses the deemed-acceptance rule (10 business days unless written notice of a material nonconformance), net 30 from milestone acceptance, and $175/hour on approved change orders.
- **Writing review done by hand.** Each mechanic has one home. Acceptance is in Section 3, change control in Section 8, and the other sections point to them.

#### Figure check (by hand)

| Milestone | Amount (USD) |
|---|---|
| M1 Discovery and design accepted | 18,000 |
| M2 Build complete, QA passed | 46,000 |
| M3 UAT accepted, pilot live | 22,000 |
| M4 Full rollout and training complete | 14,000 |
| Sum | 100,000 (matches quote total) |

#### Open items, left as bracketed fields in the draft

1. **Timeline versus hypercare.** The quote says 14 weeks from kickoff and hypercare is 30 days after full rollout. The two only fit if rollout finishes by about week 10. Per-milestone target weeks were not supplied.
2. **Hypercare.** Its activities and response expectations are undefined. It is included in the fee but has no milestone, so the draft invoices the full fee by M4.
3. **Acceptance criteria.** Only the deemed-acceptance rule was supplied. The UAT pass standard and per-deliverable criteria need a decision.
4. **Late client dependencies.** Nothing says what happens to dates or fees if the DentaCore sandbox (due week 2), the Spanish text or pilot availability is late. I didn't invent a consequence.
5. **Missing party details.** The effective date, kickoff date, client address and notice contact, provider lead, accounts-payable contact, signatories, and MSA precedence wording are all absent.
6. **Contract profile.** It is marked as an assumption ("assume standard MSA terms"), so check the SOW against the actual MSA.

#### Files

- `out/Brightwell Dental Partners - Intake Portal - SOW (DRAFT).md` — the full draft SOW, with 10 sections:
  1. Purpose and agreement
  2. Scope of services
  3. Deliverables and acceptance
  4. Timeline
  5. Client responsibilities
  6. Assumptions
  7. Exclusions
  8. Change control
  9. Fees and payment
  10. Signatures

### File: Brightwell Dental Partners - Intake Portal - SOW (DRAFT).md

#### Statement of Work: New-Patient Intake Portal

**DRAFT. Not approved, not sent, not executed. Bracketed fields are unresolved and need a source.**

| | |
|---|---|
| Client | Brightwell Dental Partners, LLC, 11 dental offices in Ohio |
| Provider | Harbor Lane Consulting, LLC |
| Governing agreement | Master Services Agreement dated March 3, 2026 (the "MSA") |
| Business Associate Agreement | In place, dated March 3, 2026 |
| SOW effective date | [not supplied] |
| Kickoff date | [not supplied] |
| Client address / notice contact | [not supplied] |
| Client product owner | Lena Ortiz, Operations Director |
| Provider lead | [not supplied] |
| Quote basis | Fixed fee by milestone, USD 100,000 |

##### 1. Purpose and agreement

This SOW is issued under the MSA. The MSA governs all terms not stated here, and this SOW does not restate them. If this SOW and the MSA conflict, [precedence rule: take from the MSA; not supplied].

Brightwell's new patients need an online way to complete intake before their visit. Harbor Lane will design, build, test and launch an intake portal that sends completed intake to Brightwell's practice-management system, DentaCore, through its import API.

##### 2. Scope of services

###### 2.1 Discovery and design
- Two workshops with Brightwell.
- Intake form design for adult and pediatric patients.
- Accessibility review of the design against WCAG 2.2 AA.

###### 2.2 Build
- A responsive web intake form.
- Insurance card photo upload.
- E-signature on consent forms.
- An integration that pushes each completed intake to DentaCore through its import API.
- Form text in English and Spanish. Brightwell supplies the Spanish text (Section 5).

###### 2.3 Testing
- QA by Harbor Lane.
- One round of user acceptance testing (UAT) with two pilot offices.

###### 2.4 Launch
- Pilot in two offices, then rollout to all 11 offices.
- Two remote staff training sessions, recorded.

###### 2.5 Hypercare
- 30 days of hypercare after full rollout, included in the fixed fee. [Hypercare activities and response expectations are not defined in the confirmed scope. Confirm before issue.]

##### 3. Deliverables and acceptance

| # | Deliverable | Milestone |
|---|---|---|
| D1 | Workshop outputs, adult and pediatric intake form designs, WCAG 2.2 AA accessibility review | M1 |
| D2 | Built portal: responsive intake form, insurance card upload, e-signature, DentaCore integration; QA results | M2 |
| D3 | UAT with two pilot offices; pilot go-live | M3 |
| D4 | Rollout to all 11 offices; two recorded training sessions | M4 |

Acceptance follows the contract profile. Each deliverable is deemed accepted 10 business days after delivery unless Brightwell gives written notice of a material nonconformance within that period. Notice goes to [Provider notice contact; not supplied]. Brightwell's UAT in D3 is a single round.

Acceptance criteria for each deliverable beyond this rule were not supplied: [confirm whether D1–D4 need written criteria, for example the UAT pass standard].

##### 4. Timeline

The work runs 14 weeks from kickoff. [Per-milestone target weeks were not supplied. Confirm whether the 14 weeks include the 30-day hypercare period; 30 days after full rollout would extend past week 14 unless rollout completes by about week 10.]

##### 5. Client responsibilities and dependencies

Brightwell will:
1. Provide DentaCore API sandbox access by week 2.
2. Name a product owner. Lena Ortiz, Operations Director, is the named product owner.
3. Supply Spanish translations of form text.
4. Make the two pilot offices available for UAT and pilot.

The schedule depends on these items. [Effect of late delivery on dates or fees is not stated in the supplied terms; the MSA or Section 8 change control applies. Confirm.]

##### 6. Assumptions

- The DentaCore import API supports the required fields.
- No PHI is stored outside DentaCore and the HIPAA-eligible hosting Brightwell already licenses. The BAA dated March 3, 2026 applies.

If either assumption proves false, Harbor Lane will raise it with the product owner and handle any change in effort under Section 8.

##### 7. Exclusions

- Appointment scheduling.
- Payments.
- DentaCore configuration changes.
- Translation, except the English and Spanish form text Brightwell supplies.

##### 8. Change control

Work outside Sections 2 and 7, or a failed assumption in Section 6, proceeds only under a written change order approved by both parties. Approved change orders are billed at USD 175 per hour. No change order carries a fee until approved.

##### 9. Fees and payment

Fixed fee: USD 100,000. Hypercare is included.

| Milestone | Trigger | Amount (USD) |
|---|---|---|
| M1 | Discovery and design accepted | 18,000 |
| M2 | Build complete, QA passed | 46,000 |
| M3 | UAT accepted, pilot live | 22,000 |
| M4 | Full rollout and training complete | 14,000 |
| **Total** | | **100,000** |

Each milestone is invoiced on acceptance under Section 3 and is payable net 30 from milestone acceptance. Invoices go to [accounts payable contact; not supplied]. Hypercare has no separate milestone; the full fee is invoiced by M4.

##### 10. Signatures

| Brightwell Dental Partners, LLC | Harbor Lane Consulting, LLC |
|---|---|
| Name: [not supplied] | Name: [not supplied] |
| Title: [not supplied] | Title: [not supplied] |
| Signature / Date: | Signature / Date: |
