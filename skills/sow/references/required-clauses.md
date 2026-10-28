# Required clauses, the language a generated SOW must never be missing

This file lists the contract-class clauses that must appear in the reference SOW example. The clause-presence gate in pre-flight checks for them; `scripts/approved_clauses.js` supplies the verbatim language. Organized by clause, not by section number, so it holds across both the numbered "Tier 1 CPQ Lift & Shift" structure and the standard named-section structure.

**Reference status.** This is the neutral example clause table retained for anchor-checker regression tests. Actual builds use the explicitly selected contract profile and `verify_contract.py`. The example terms do not carry approval for a real engagement.

**Scope.** Only the SOW-resident soft contractual layer: preamble, acceptance, change control, payment, protective assumptions, and execution. Limitation of liability, IP, confidentiality, warranties, and termination stay in the PSA and must never be restated here.

**Format.** Brackets `[ ]` mark deterministic fill from the quote; `[[ ]]` marks reasoned fill per the placeholder convention.

---

## The clause-presence gate (add to pre-flight)

A generated SOW fails pre-flight if any clause below is absent. Check by string-matching the anchor phrase, not by section number.

The **Assess** column is the required set for an assessment SOW (see "Assess variant" below). A blank means the clause is not required for that variant.

| # | Clause | Anchor phrase to match | Fixed-fee | T&M | Assess |
|---|--------|------------------------|:--:|:--:|:--:|
| 1 | Contract preamble + PSA incorporation | "is a contract, entered into on the Effective Date" | ✓ | ✓ | ✓ |
| 2 | PSA Effective Date line | "Professional Services Agreement Effective Date:" | ✓ | ✓ | ✓ |
| 3 | Notice addresses (both parties, with Attn) | "Name and Notice Address of" | ✓ | ✓ | ✓ |
| 4 | Project Scope intro | "based on the following assumptions, representations and/or information supplied by you" | ✓ | ✓ | ✓ |
| 5 | Out-of-scope header | "For the sake of clarity, the following Activities are out of scope" | ✓ | ✓ | ✓ |
| 6 | Elapsed-period timeline statement | "estimated to be performed over an elapsed period of" | ✓ | ✓ | ✓ |
| 7 | Project Management section | "day-to-day project management and change control" | ✓ | ✓ |  |
| 8 | Deliverables table (Deliverable / Description / Format) | "Deliverable" + "Format" header row | ✓ | ✓ | ✓ |
| 9 | Client reliance paragraph | "We will be entitled to rely on all of your decisions and approvals" | ✓ | ✓ | ✓ |
| 10 | 30-day commencement clause | "commence no earlier than thirty (30) calendar days following the date of last signature" | ✓ | ✓ |  |
| 11 | Service Provider staffing-discretion clause | "reserves the right to determine the specific individuals assigned" | ✓ | ✓ | ✓ |
| 12 | **Deemed-acceptance clause** | "will be considered accepted by Client no later than the five (5) business days after delivery" | ✓ | ✓ | ✓ |
| 13 | Change-Order-on-changes clause | "a Change Order will be mutually agreed upon and executed" | ✓ | ✓ | ✓ |
| 14 | Security-vulnerability disclaimer | "cannot provide assurance against all possible security vulnerabilities" | ✓ | ✓ | ✓ |
| 15 | **Catch-all exclusion** | "Any services not explicitly set forth in this SOW are deemed out of scope" | ✓ | ✓ | ✓ |
| 16 | Location of Services | "performed remotely from Service Provider corporate and home offices" | ✓ | ✓ | ✓ |
| 17 | Payment-model close (fixed fee) | "you will pay us a fixed fee of" + billing schedule table | ✓ |, | ✓ |
| 18 | Payment-model close (T&M) | "provided on a Time and Materials basis" + "upfront invoice of 25%" |, | ✓ |  |
| 19 | Invoices-per-Agreement line | "due and payable in accordance with the terms of the Agreement" | ✓ | ✓ | ✓ |
| 20 | Expenses + sales tax carve-out | "are not included in the Fees and will be invoiced separately" | ✓ | ✓ | ✓ |
| 21 | Remittance block (bill-to + pay-to + bank) | "Please make payments as follows" | ✓ | ✓ | ✓ |
| 22 | Return-by-date / offer-expiry | "These terms are not valid if the Service Provider doesn't receive this signed SOW by such date" | ✓ | ✓ | ✓ |
| 23 | Counterparts clause | "may be executed in one or more counterparts" | ✓ | ✓ | ✓ |
| 24 | Authority-to-bind clause | "has the authority to bind his/her respective Party" | ✓ | ✓ | ✓ |
| 25 | Dual signature block (By / Name / Title / Date) | "Acceptance and signatures" + client name header row | ✓ | ✓ | ✓ |
| 26 | Order of Precedence (Miscellaneous Terms) | "this SOW shall control solely as to the specific Services" | ✓ | ✓ | ✓ |
| 27 | Limited Modification (Miscellaneous Terms) | "does not amend, waive, or modify the Agreement" | ✓ | ✓ | ✓ |
| 28 | Delays / Rescheduling / Resource Reallocation | "extend applicable schedules and milestone dates on a day-for-day basis" | ✓ | ✓ | ✓ |
| 29 | Assess coordination (lean, replaces #7) | "the assessment lead owns coordination" |  |  | ✓ |
| 30 | Assess commencement (flexible, replaces #10) | "commence within a mutually agreed window following the date of last signature" |  |  | ✓ |

Clauses 12 (deemed acceptance) and 15 (catch-all exclusion) are the two most load-bearing protections and the easiest to lose in a regenerate. Treat their absence as a hard stop, not a warning. Clauses 26–28 are the Miscellaneous Terms block added by the reference clause library; they did not appear in older signed SOWs and are the most likely to be absent from a generator that predates the reference clause library.

**Assess variant.** The Assess column is the required set for an assessment SOW (advisory, fixed fee). It is the fixed-fee set with two swaps: clause 7 (project management and governance) becomes clause 29 (lean assessment-lead coordination), and clause 10 (the 30-day commencement floor) becomes clause 30 (a flexible commencement window). Both originals misfit a fast, lean assessment: #7 mandates PM/governance an assessment does not staff, and #10 bars a start for 30 days against the speed an assessment is sold on. The load-bearing pair (12, 15) and every other protection stay required. This set is an example. Its presence in the skill does not authorize it for an engagement.

---

## Clause library (verbatim)

### 1. Contract preamble + PSA incorporation
> This Statement of Work ("SOW") is a contract, entered into on the Effective Date of this SOW, by and between **Service Provider** ("Service Provider", "we", "us", or "our") and [Client legal name] ("Client", "you", or "your"), together with its subsidiaries and affiliates ("[Client short name]"). This SOW is subject to the terms and conditions stated below and the terms and conditions stated in the Professional Services Agreement document executed by Service Provider and Client are effective as of the date stated below. Capitalized terms used in this SOW shall have the meanings defined herein or as used in the Professional Services Agreement.

### 2. PSA Effective Date line
> **Professional Services Agreement Effective Date:** [[date, leave blank only if this is the first SOW under no executed PSA; otherwise fill from the governing PSA]]

### 3. Notice addresses
> **Name and Notice Address of Service Provider:** [Provider legal name], [confirmed notice address], Attn: [confirmed contact]
> **Name and Notice Address of Client:** [Client legal name] ("Client"), [Client address], Attn: [Client contact]

### 4. Project Scope intro
> Service Provider will provide services subject to the terms of this SOW and the Agreement. The Services are based on the following assumptions, representations and/or information supplied by you.

### 5. Out-of-scope header
> **For the sake of clarity, the following Activities are out of scope:**

### 6. Elapsed-period timeline statement
> The Services pursuant to this SOW are estimated to be performed over an elapsed period of "[N]" weeks based on the timeline below.

### 7. Project Management
> Throughout the project, Service Provider will provide project management and governance services for successful execution of the engagement. These activities are comprised of: ongoing management of the plan as activities move or adjust; schedule design and validation workshops with appropriate customer personnel; perform day-to-day project management and change control; provide weekly status reports and updates to project team; manage the risk and issue log, complete with action items, due dates and mitigation plan; conduct weekly status meetings (30 minutes) to discuss status report, issues/risks.

### 8. Deliverables table
> Table with columns **Deliverable | Deliverable Description | Format**. Standard rows: Requirements Doc, Solution Design Doc, Training Doc, [Platform] Configuration. (Format = Excel/Word/PPT/Salesforce as applicable.) Never one deliverable per scope item.

### 9. Client reliance paragraph
> You will designate an employee or employees who will make or obtain all management decisions with respect to this engagement on a timely basis. You also agree to ensure that all assumptions set forth below are accurate and to provide us with such further information we may need and which we can rely on to be accurate and complete. You also agree to cause all levels of your employees and contractors to cooperate fully and timely with us. We will be entitled to rely on all of your decisions and approvals made independently and we will not be obligated to evaluate, advise on, confirm, or reject such decisions and approvals.

### 10–11. Commencement + staffing discretion
> The Project shall commence no earlier than thirty (30) calendar days following the date of last signature on this Statement of Work (the "Effective Date"). The specific kickoff date will be confirmed upon resource assignment. Service Provider reserves the right to determine the specific individuals assigned based on availability, skill set, and project requirements.

### 12. Deemed-acceptance clause (load-bearing)
> Client will accept completed Deliverables (as outlined in the sections of this SOW), if they materially conform to the specifications set forth in this SOW and Service Provider has submitted the deliverable for review to the Client according to the Project Plan. Should a completed Deliverable not materially conform to the specifications set forth in this SOW, Client will notify Service Provider of this non-conformance in reasonable detail within five (5) business days of delivery. Service Provider will have a reasonable period of time, based on the severity and complexity of the non-conformance, to correct the non-conformance. If Client fails to promptly notify Service Provider of any material non-conformance within five (5) business days after completed delivery, or unreasonable delays, then the completed Deliverable will be considered accepted by Client no later than the five (5) business days after delivery.

### 13. Change control
> Additional time to conduct workshops required to accurately define business processes and requirements for the capabilities defined in this SOW may require a Change Order to be reviewed and executed by Service Provider and Client. If changes to the SOW are identified and/or requested by Client or Service Provider during the course of the Project, a Change Order will be mutually agreed upon and executed by Client and Service Provider detailing the necessary scope modification and, if applicable, revisions to the Service Provider resources, associated fees, and like changes.

### 14. Standard protective assumptions (the General Project Assumptions set)
> - Timelines, duration of Project and resources, etc. are based on timely execution of this SOW, and as applicable, the Agreement.
> - Client will ensure: (i) that executives, management and key application owners (both business & technical), operations, and infrastructure resources of both Client and all third party vendors will be reasonably and timely available as required by Service Provider, for interviews, meetings, and knowledge transfer; (ii) that both Client and all third party vendors will timely provide documentation; (iii) that all third party vendors meaningfully participate as required by Service Provider for the performance of this SOW; and (iv) that qualified individuals from Client and all third party vendors are made reasonably available as required and perform their assigned tasks and responsibilities in a timely manner.
> - Client will make timely decisions and obtain required management approvals, all consents, and/or licenses necessary from third parties required for Service Provider to perform its obligations outlined in this document.
> - Client will retain responsibility for its compliance with all applicable federal, state/provincial and local laws and regulations.
> - Service Provider will be entitled to rely on all Client decisions and approvals made in relation to this SOW. Although nothing in the SOW will require Service Provider to evaluate, advise on, modify, confirm, or reject such decisions and approvals, Service Provider will use its knowledge and expertise to guide client where appropriate.
> - Service Provider cannot provide assurance against all possible security vulnerabilities (even where the scope of the engagement involves identifying security vulnerabilities).
> - Service Provider will advise on selection of potential 3rd Party AppExchange applications as required to address Client business requirements based on publicly available information regarding application capabilities and functionality. Formal diligence and selection of the applications is outside the scope of this SOW.

### 15. Catch-all exclusion (load-bearing)
> Any services not explicitly set forth in this SOW are deemed out of scope for this SOW, and will be performed pursuant to a separate statement of work or change order executed by the parties.

### 16. Location of Services
> Work pursuant to this SOW will be performed remotely from Service Provider corporate and home offices. Any Service Provider resource travel will be mutually agreed upon by both parties. Service Provider Travel & Expenses will be billed at cost.

### 17. Professional Arrangements, fixed-fee variant
> As compensation for providing the services hereunder, you will pay us a fixed fee of $[amount] plus out of pocket expenses. These fees are based on the assumptions provided under this SOW. Service Provider is not obligated to perform any services related to assumptions unknown at the time of execution of this engagement or deemed to be outside the scope of this engagement. Service Provider will provide the consultants with roles identified in the Service Provider Roles and Responsibilities table above to perform the Services as outlined in this agreement.
>
> Followed by a billing schedule table, **Billing Description | Fees to be Billed | Billing Date**, with milestone rows (e.g. SOW Execution, Project Kick-off, mid-project start, Project Completion).

### 18. Professional Arrangements, T&M variant
> The Professional Services described in this SOW are provided on a Time and Materials basis. We will bill on an hourly basis based on the actual hours worked in accordance with the hourly rates set forth herein, which may be subject to adjustment from time to time. The aggregate service fees for completion of the entire work set forth in this SOW are $[amount] USD. Any work outside the scope of this SOW shall be set forth in a separate statement of work.
>
> Followed by an estimated-total line, then: Upon SOW execution, an upfront invoice of [25]% ($[amount]) of the Total Estimated Fees will be submitted and payable in accordance with the terms of the Professional Services Agreement. This upfront payment will be credited against the corresponding number of billable hours and netted against the final invoice(s).

### 19–20. Invoices per PSA + expenses carve-out
> All invoices shall be due and payable in accordance with the terms of the Professional Services Agreement. Actual, reasonable travel and out-of-pocket expenses in accordance with the Customer's expense policies and state sales tax, if any, are not included in the Fees and will be invoiced separately, in accordance with the Agreement.

### 21. Remittance block
> We understand that our bills should be sent to: [Client AP name / address / email]
> Please make payments as follows:
> **Payment by Check:** [Confirmed payment instructions from the selected private contract profile]
> **All Electronic Payments:** [Confirmed payment instructions from the selected private contract profile]

### 22–24. Signature preamble
> Please indicate your agreement with these terms by signing and returning this SOW on or before [date] to enable the Service Provider to manage our resources and business. These terms are not valid if the Service Provider doesn't receive this signed SOW by such date. This SOW may be executed in one or more counterparts and/or by facsimile or electronic submission, each of which will be deemed an original and all of which signed counterparts, taken together, will constitute one instrument. Service Provider looks forward to working with you on this important project.
>
> **Each person signing this document represents that he/she intends to and has the authority to bind his/her respective Party to this Statement of Work.**

### 25. Dual signature block
> Two-column block, **Service Provider** | **[clientLegalName]**, each with By / Name / Title / Date.

### 26. Order of Precedence (Miscellaneous Terms)
> **Order of Precedence.** In the event of any conflict, inconsistency, or ambiguity between the terms of this SOW and the terms of the Agreement, this SOW shall control solely as to the specific Services, Deliverables, fees, assumptions, milestones, and schedules described herein, and the Agreement shall control in all other respects, including, without limitation, payment rights, intellectual property, confidentiality, warranties, indemnities, limitations of liability, dispute resolution, and general legal terms.

### 27. Limited Modification (Miscellaneous Terms)
> **Limited Modification.** Except as expressly set forth in this SOW, this SOW does not amend, waive, or modify the Agreement. All terms of the Agreement not expressly modified by this SOW remain unchanged and in full force and effect.

### 28. Delays; Rescheduling; Resource Reallocation
> **Delays; Rescheduling; Resource Reallocation.** Any delay caused by Client, including failure to timely provide dependencies, approvals, information, access, feedback, or required resources, shall automatically extend applicable schedules and milestone dates on a day-for-day basis, together with such additional time as reasonably necessary for remobilization and scheduling. If Client delays the project for more than ten (10) business days, Service Provider may reassign reserved personnel to other matters and reschedule Services subject to resource availability. Client-caused delays may result in additional fees, standby charges, rescheduling fees, or rate adjustments at Service Provider's then-current rates.

### 29. Assess coordination (assess variant, replaces #7)
> The assessment runs with a small senior team. Service Provider does not staff a separate project manager or client services executive on an engagement of this size; the assessment lead owns coordination and presents the readout. Anchor: "the assessment lead owns coordination".

### 30. Assess commencement (assess variant, replaces #10)
> The assessment will commence within a mutually agreed window following the date of last signature on this Statement of Work (the "Effective Date"), and the specific kickoff date will be confirmed upon resource assignment. Service Provider reserves the right to determine the specific individuals assigned based on availability, skill set, and project requirements. Anchor: "commence within a mutually agreed window following the date of last signature".

> Note: the reference clause library also carries a **Project Assumptions** Miscellaneous-Terms clause (equitable adjustment via written change order) and restates **Counterparts; Electronic Signatures** and **Authority** in the Misc Terms block. Those are covered by clauses 13/23/24; keep them, but they are not separately gated to avoid double-counting.

---

## Example values

- **Upfront percentage: 25%**, the example T&M value (clause 18). Real engagements use the selected profile's upfront percentage.
- **Acceptance window: five (5) business days** (clause 12). Real engagements use the selected profile's acceptance language.
- **Payment instructions:** selected private contract profile only; no bank details are packaged here.
- **Service Provider lead role** in the reference clause library is **Engagement Manager** (not "Accountable Executive"/"AE", not "CSE"). Reconcile against the skill's role-naming rule before generating.
