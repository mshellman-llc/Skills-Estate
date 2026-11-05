---
skill: sow-quality
title: Reviewing a draft helpdesk migration SOW against its quote
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: f13a0cc56620104bd57e6b8f76a4586488f7d2fdd9fe7ad5424117a6a0fd9ec1
---

## Request

Can you review the attached draft SOW for our helpdesk migration against the quote summary before it goes to the client's procurement team? I want to know what's inconsistent, what's duplicated, and what needs a decision from someone else, without you changing any pricing.

## Inputs

Run of the built `statement-of-work` task package in its "contract scope and obligation review" mode. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### quote-summary.txt

QUOTE Q-2291 rev 3 (confirmed by pricing owner)
Pricing model: fixed fee. Total $91,400. 480 hours. 12 weeks from 2027-01-18.

Resources:
- Engagement Manager: 60 h x $200 = $12,000
- Solution Architect: 140 h x $220 = $30,800
- Senior Consultant: 220 h x $180 = $39,600
- Data Analyst: 60 h x $150 = $9,000

Scope items:
1. Case history migration. Volume estimate 38,000 cases (estimate from client export of 2026-10-12, not a cap).
2. Email templates: up to 40.
3. Automation rules: up to 12.
4. Cutover support and go-live readout.

Milestones: kickoff 25%, data load complete 45%, go-live 30%.
Exclusions: third-party integrations (including billing); custom reporting.
Acceptance: 10 business days per deliverable; final acceptance on go-live readout.
Client roles: Executive Sponsor, Data Owner (named by client), Engagement Manager approves deliverables for client.
Client dependency: admin access to the existing platform by 2027-01-18.

#### sow-draft.md

#### Statement of Work: Helpdesk Migration (DRAFT v2)
Provider: Tallow & Reed Consulting. Client: Harbourline Logistics. Quote ref: Q-2291 rev 3.

##### 1. Overview
Tallow & Reed will migrate Harbourline's support operation to the new helpdesk platform. Changes to scope follow the Change Order process in Section 7.

##### 2. Scope
The provider will migrate the full configuration of the existing platform, with functional parity on launch. The engagement runs 10 weeks from 18 January 2027.

##### 3. Deliverables and limits
3.1 Migration of case history (about 38,000 cases, a hard cap; any additional cases require a Change Order under Section 7).
3.2 Migration of up to 40 email templates and up to 12 automation rules.
3.3 Billing system sync for invoice-related cases.
3.4 Exclusions: integrations with third-party systems, including billing, are out of scope. Any change to scope requires a Change Order.

##### 4. Responsibilities
The provider will ensure Harbourline's administrator access is in place by 18 January 2027. The Client Lead approves each deliverable. Harbourline will supply a named data owner, so that data questions have a single point of contact.

##### 5. Fees
Fixed fee of $91,400. Overage is billed at the rates in the quote on a time-and-materials basis. Milestones: kickoff 25% ($22,850); data load complete 45% ($41,130); go-live 25% ($22,850).

##### 6. Acceptance
Harbourline has 5 business days to accept or reject each deliverable in writing. Silence is not acceptance. Final acceptance follows the go-live readout described in Section 9.

##### 7. Change control
Any change to scope, volume or timeline requires a written Change Order signed by both parties before work proceeds. A Change Order states the change, its fee and its schedule effect.

## Output

### Review of draft SOW v2 against quote Q-2291 rev 3

I read the full draft against the confirmed quote summary. I changed no figures and edited no text. Eight items need a decision from the pricing owner, the contract owner or you. Three are editorial and can be fixed once the decisions are made.

**Method note.** I could not run `slop_scan.py`, so I did its checks by hand: repeated mechanics, justification tails, verb piles and cross-reference checks. The counts below are my manual counts. The draft stays unapproved until its authorised owner signs off. This review is not legal approval.

#### 1. Decisions needed before it goes to procurement

| # | Location | Finding | Source | Who decides |
|---|---|---|---|---|
| 1 | Section 5, milestones | The three milestones total 95%, or $86,830. The fixed fee is $91,400, so $4,570 is unbilled. The quote's go-live milestone is **30%** ($27,420). The draft says 25% ($22,850). | Quote milestones: 25/45/30 | Pricing owner confirms the split. I have not corrected it. |
| 2 | Section 5, "Overage is billed … time-and-materials" | This contradicts "Fixed fee". The quote is fixed fee and gives no T&M overage right. The sentence adds a billing model the quote does not contain. | Quote pricing model | Pricing owner and contract owner. Delete it, or confirm it is an agreed term. |
| 3 | Section 2, "10 weeks" | The quote says 12 weeks from 2027-01-18. | Quote header | Pricing owner. The date and the duration must match the quote. |
| 4 | Section 3.1, "a hard cap" | The quote calls 38,000 cases a volume **estimate** from the client's 2026-10-12 export, "not a cap". The draft turns an estimate into a cap, and Section 3.1 then sends extra cases to a Change Order. | Quote scope item 1 | Contract owner. Decide whether the number is an estimate or a cap, then say so once. If it is a cap, the quote needs a revision first. |
| 5 | Section 2, "full configuration … functional parity" against Section 3.2 | The parity promise conflicts with the caps of 40 templates and 12 rules. I have kept both until an authorised owner resolves it. As written, a client could claim parity for a 41st template. | Quote items 2 and 3 | Contract owner. Likely fix: tie scope to the Section 3 list and drop "full" and "parity". |
| 6 | Section 3.3 against Section 3.4 | 3.3 delivers a billing system sync. 3.4 excludes billing integrations. The quote excludes third-party integrations "including billing" and has no sync item. | Quote exclusions | Pricing owner. Either 3.3 is not in scope and should be removed, or the quote is missing an item. |
| 7 | Section 6, "5 business days" | The quote gives 10 business days per deliverable. | Quote acceptance | Contract owner. The shorter period favours the provider and departs from the quote. |
| 8 | Section 4, approver | The draft names "Client Lead" as approver. The quote's role is the Engagement Manager, who approves deliverables for the client. The quote lists no Client Lead. The quote lists an Executive Sponsor and a Data Owner. | Quote client roles | Engagement owner. I kept the quote's role names and did not substitute one for the other. |

#### 2. Obligation and dependency check

- **Admin access (Section 4).** The draft says the provider "will ensure" Harbourline's administrator access is in place by 18 January 2027. The quote lists this as a **client dependency**, not a provider promise. As written, the provider owns a client task. Reword to make Harbourline the owner. This is an owner correction, so I list it here for confirmation. It also needs a stated consequence if the date slips, and the quote gives none. That is an open gap.
- **Data owner (Section 4).** Harbourline supplies a named data owner. The name is not in the sources, so it needs a placeholder in the draft.
- **Final acceptance (Section 6).** It points to "Section 9", but the draft ends at Section 7. The quote ties final acceptance to the go-live readout. The reference is broken, and the readout is not described anywhere in the draft. Add the readout to the scope list, or point to the deliverable that holds it. The quote's scope item 4 (cutover support and go-live readout) has no matching deliverable in Section 3 either.
- **Custom reporting.** The quote excludes it. The draft's exclusions list leaves it out. Add it to Section 3.4 only if the contract owner agrees, since that is a scope-boundary decision.

#### 3. Quantities (Basis of Estimate)

| Quantity | Source | Status in quote | Status in draft | Owning section | Verification | Open decision |
|---|---|---|---|---|---|---|
| ~38,000 cases | Client export, 2026-10-12 | Estimate | "Hard cap" | 3.1 | Mismatch | Finding 4 |
| 40 email templates | Quote item 2 | "Up to" limit | Same | 3.2 | Matches | Finding 5 (parity conflict) |
| 12 automation rules | Quote item 3 | "Up to" limit | Same | 3.2 | Matches | Finding 5 |
| 12 weeks | Quote header | Duration | 10 weeks | 2 | Mismatch | Finding 3 |
| 480 hours / $91,400 | Quote | Fixed fee | $91,400 (hours not shown) | 5 | Fee matches | Finding 2 |

The quote reconciles internally. The role hours sum to 60 + 140 + 220 + 60 = 480. The revenue sums to $12,000 + $30,800 + $39,600 + $9,000 = $91,400. Each role's hours times rate equals its stated revenue. The draft's $91,400 fee agrees with the quote. Only the milestone split fails.

The draft does not say when the case estimate is checked against actual inventory, or who accepts the result. That is an unresolved gate. I did not invent one.

#### 4. Structural de-slop (editorial, safe after the decisions above)

**Repeated change mechanic: five statements.** I found the change-order rule in Section 1, Section 3.1, Section 3.4, Section 5 (overage) and Section 7. Section 7 should own it. This follows the ownership map: the change process, trigger, approval and fee-and-schedule statement sit in one place.
- Section 1 already points to Section 7, so keep it.
- Section 3.1: replace the parenthetical with "Case volume changes follow Section 7", once Finding 4 is decided.
- Section 3.4: delete the last sentence ("Any change to scope requires a Change Order"). It restates Section 7.
- Section 5: the overage sentence is removed or confirmed under Finding 2.
- The Section 7 text stays complete. Note that it treats volume, scope and timeline alike. If the contract distinguishes volume changes from new workstreams, that is a contract-owner call. I have not invented a soft/hard split.

**Justification tails.** One candidate: Section 4, "so that data questions have a single point of contact." It repeats the purpose of naming a data owner and defends no exception. It may be cut, subject to the contract owner's approval of any change to an obligation. I would keep Section 6's "Silence is not acceptance". It is a stricter-than-default term, not a tail.

**Verb piles and commentary.** None found. "Functional parity" is a scope claim, not commentary, and is handled in Finding 5.

**Cross-references.** Sections 1, 3.1 and 3.4 point to Section 7, which exists and holds the rule. The Section 6 reference to Section 9 is broken (above).

Counts, by hand: repeated mechanic 1 (five locations), justification tails 1 candidate, broken references 1, meta-commentary 0. I have not re-scanned a revised document, because there is no revised document yet.

#### 5. Suggested next steps

1. Send Findings 1–3 and 6 to the pricing owner. They need a revised or reconfirmed quote.
2. Send Findings 4, 5 and 7 to the contract owner. Findings 4 and 5 together decide whether the scope is capped or estimated.
3. Confirm Finding 8 and the admin-access owner with the engagement owner.
4. After those decisions, I can apply the Section 4 edits as tracked changes and re-run the checks.

#### Gaps and assumptions

- I had only the SOW draft and the quote summary. There is no master agreement, template or approved decision deck, so clauses that would normally come from the agreement could not be checked. I did not assume them.
- The draft lacks signature, notice and miscellaneous terms. I treated it as a partial draft and did not judge that absence.
- No receipts from prose, brand or quality-gate tooling exist. These checks need scripts I cannot run, and the document is not final.
- No `.docx` was produced, so nothing needed a visual or brand check.

#### Files

- `out/answer.md` (this review). Its key content is the eight findings above.
