/* Reference clause structure for synthetic tests. Not an approved contract for any provider.
 * Actual builds require a complete external contract profile with its own source. */
module.exports = {
  LOE_ACCEPTANCE: `On delivery of the work described above, the engagement is complete and the deliverable is accepted. Any factual correction is raised in writing within five (5) business days and Service Provider will correct factual errors.`,

  // ── Assessment variant blocks ──────────────────────────────────────────
  // The build-shaped CLIENT_RESOURCES, PROJECT_MANAGEMENT_*, and one protective
  // assumption reference activities an advisory engagement does not perform
  // (UAT, deployment, cutover, data migration, AppExchange selection). The
  // assess variant renders these instead.
  CLIENT_RESOURCES_ASSESS: [
    {role:"Executive Sponsor", responsibility:"Own the business questions the assessment answers. Approve the in-scope areas, attend the executive readout, and act on the recommendations.", commitment:"2-3 hrs total (kickoff, readout)"},
    {role:"Engagement Coordinator", responsibility:"Client-side point of contact for the Service Provider team. Schedule stakeholder sessions, coordinate access, and confirm attendee availability.", commitment:"2-4 hrs/week"},
    {role:"Business Stakeholders", responsibility:"Participate in discovery and working sessions for the in-scope areas. Provide the context, current-state detail, and priorities the assessment depends on.", commitment:"As scheduled across the engagement"},
    {role:"Technical / Data Contact", responsibility:"Provide read access to the relevant systems and answer technical and data questions. Participate in the technical and data portions of the assessment.", commitment:"As scheduled, higher during the assessment stage"}
  ],
  CLIENT_RESOURCES_NOTE_ASSESS: `A person can hold more than one role. Time commitments are the availability the assessment depends on and are confirmed at kickoff.`,

  // Lean assessment staffing: a small senior team, no separate PM or CSE. The
  // assessment lead owns coordination and presents the readout. The "day-to-day
  // project management and change control" phrase is retained because clause #7
  // of the gate requires it; it names an activity the lead performs, not a role.
  PROJECT_MANAGEMENT_INTRO_ASSESS: `The assessment lead owns coordination and presents the readout. The confirmed role allocation governs staffing. Throughout the engagement the lead will:`,
  PROJECT_MANAGEMENT_BULLETS_ASSESS: [
    `Schedule discovery and working sessions with the appropriate Client personnel`,
    `Coordinate access and information requests`,
    `Provide status updates against the assessment stages`,
    `Maintain a running log of findings, open questions, and information gaps`,
    `Prepare and deliver the executive readout`
  ],

  // Assessment-variant client-resources intro. The build intro opens on "a successful
  // Salesforce implementation", which an advisory engagement does not perform. Same
  // structural purpose, assessment-native wording.
  CLIENT_RESOURCES_INTRO_ASSESS: `Active participation from your team is essential to a high-quality assessment. The commitments below reflect the availability the assessment depends on. Actual effort varies with the number of stakeholders, the systems in scope, and how readily current-state information is available. Consistent availability across the engagement keeps the schedule and the quality of the findings on track.`,


  // #1 — preamble + PSA incorporation by reference. {CLIENT} = client legal name.
  PREAMBLE: `This Statement of Work (“SOW”) is a contract, entered into on the Effective Date of this SOW, by and between {PROVIDER} (“Service Provider”, “we”, “us”, or “our”) and {CLIENT} (“Client”, “you”, or “your”), together with its subsidiaries and affiliates (“{CLIENT}”). This SOW is subject to the terms and conditions stated herein and the terms and conditions set forth in that certain Professional Services Agreement executed by Service Provider and Client effective as of the date stated below (the “Agreement”). The Agreement is hereby incorporated into this SOW by reference as though fully set forth herein. Capitalized terms used in this SOW shall have the meanings defined herein or as used in the Agreement.`,

  // #3 — notice-address column headers (label form the gate checks for)
  NOTICE_SP_LABEL: `Name and Notice Address of Service Provider`,
  NOTICE_CLIENT_LABEL: `Name and Notice Address of Client`,

  // #4 — project scope intro
  PROJECT_SCOPE_INTRO: `Service Provider will provide services subject to the terms of this SOW and the Agreement (the “Services”). The Services are based on the following assumptions, representations and/or information supplied by you.`,

  // #5 — out-of-scope header
  OUT_OF_SCOPE_HEADER: `For the sake of clarity, the following Activities are out of scope:`,

  // #6 — elapsed-period timeline statement. {N} = duration in weeks.
  ELAPSED_PERIOD: `The Services pursuant to this SOW are estimated to be performed over an elapsed period of “{N}” weeks based on the timeline below.`,

  // #7 — project management
  PROJECT_MANAGEMENT_INTRO: `Throughout the project, Service Provider will provide project management and governance services for successful execution of the engagement. These activities are comprised of:`,
  PROJECT_MANAGEMENT_BULLETS: [
    `Ongoing management of the plan as activities move or adjust`,
    `Schedule design and validation workshops with appropriate Client personnel`,
    `Perform day-to-day project management and change control`,
    `Provide weekly status reports and updates to the project team`,
    `Manage the risk and issue log, complete with action items, due dates, and mitigation plan`,
    `Conduct weekly status meetings (30 minutes) to discuss the status report, issues, and risks`,
  ],

  // #9 — client reliance paragraph
  CLIENT_RELIANCE: `You will designate an employee or employees who will make or obtain all management decisions with respect to this engagement on a timely basis. You also agree to ensure that all assumptions set forth below are accurate and to provide us with such further information we may need and which we can rely on to be accurate and complete. You also agree to cause all levels of your employees and contractors to cooperate fully and timely with us. We will be entitled to rely on all of your decisions and approvals made independently and we will not be obligated to evaluate, advise on, confirm, or reject such decisions and approvals.`,

  // Client Resources & Responsibilities — verbatim from the approved template "Project Resources" table.
  // Intro paragraph + the standard role/responsibility/time-commitment set. Renders in §7.1.
  CLIENT_RESOURCES_INTRO: `To deliver a successful Salesforce implementation, active participation from Client resources is essential. Client acknowledges that these resource allocations are essential to ensure a successful outcome. These commitments are based on projects with multiple Salesforce capabilities, several data sources, and a moderate-to-high level of complexity. Actual effort may vary depending on project size, business process scope, and integration needs. Clients are expected to dedicate resources consistently across the engagement to maintain schedule, quality, and adoption success.`,
  CLIENT_RESOURCES: [
    { role: `Executive/Project Owner`, responsibility: `Review and approve key solution requirements. Resolve project issues. Attend Steering Committee meetings and key presentations and demos throughout the project.`, commitment: `2-4 hrs/week (governance, approvals)` },
    { role: `Project Manager`, responsibility: `Work with the Service Provider project manager to achieve overall project direction and success. Coordinate Client-side resources, meetings, facilities, and materials. Coordinate internal project interdependencies. Serve as point of contact for the Service Provider project team.`, commitment: `20-30 hrs/week (may peak near full-time during UAT and deployment)` },
    { role: `Functional SME(s)`, responsibility: `Visible leader for the given business area; provides expert advice and guidance for the specific process area. Participate in workshop preparation and delivery. Ensure key business subject-matter experts are involved throughout the project. Own process KPIs. Collaboratively develop the layout and content of in-scope items. Review and sign off on key deliverables throughout the project. Participate in and support system testing.`, commitment: `15-30 hrs/week (higher during data migration, integration design, and cutover)` },
    { role: `Technical Lead/Data SME`, responsibility: `Participate in solution design including interfaces, data, administration, security, and other key technology components. Participate in workshops and design meetings for technology-related components. Ensure appropriate IT resources are engaged during the design phase. Provide sign-off on deliverables from an IT perspective.`, commitment: `15-30 hrs/week (higher during data migration, integration design, and cutover)` },
    { role: `Salesforce Admin`, responsibility: `Grant Service Provider appropriate access to the Client Salesforce environment and other administrative tasks. Provide input related to system requirements, challenges, and future business needs. Support system reviews, testing, and training.`, commitment: `15-30 hrs/week (may peak near full-time during testing, training, and go-live)` },
  ],
  CLIENT_RESOURCES_NOTE: `A resource can have multiple roles. Actual time commitments are confirmed per engagement and may be adjusted in scoping.`,

  // #10 + #11 — commencement and staffing discretion
  COMMENCEMENT_STAFFING: `The Project shall commence no earlier than thirty (30) calendar days following the date of last signature on this Statement of Work (the “Effective Date”). The specific kickoff date will be confirmed upon resource assignment. Service Provider reserves the right to determine the specific individuals assigned based on availability, skill set, and project requirements.`,

  // Assess commencement (flexible), replaces the 30-day floor for assessments (gate row 30). An assessment
  // is sold on speed, so the fixed 30-day-minimum start is the wrong default. The staffing-discretion
  // sentence (clause #11) is retained verbatim so #11 still passes on the assess variant.
  COMMENCEMENT_STAFFING_ASSESS: `The assessment will commence within a mutually agreed window following the date of last signature on this Statement of Work (the “Effective Date”), and the specific kickoff date will be confirmed upon resource assignment. Service Provider reserves the right to determine the specific individuals assigned based on availability, skill set, and project requirements.`,

  // #14 (+ #13 change-control) — General Project Assumptions protective set (verbatim)
  PROTECTIVE_ASSUMPTIONS: [
    `Timelines, duration of Project and resources, etc. are based on timely execution of this SOW, and as applicable, the Agreement.`,
    `Client will ensure: (i) that executives, management and key application owners (both business & technical), operations, and infrastructure resources of both Client and all third party vendors will be reasonably and timely available as required by Service Provider, for interviews, meetings, and knowledge transfer; (ii) that both Client and all third party vendors will timely provide documentation; (iii) that all third party vendors meaningfully participate as required by Service Provider for the performance of this SOW; and (iv) that qualified individuals from Client and all third party vendors are made reasonably available as required and perform their assigned tasks and responsibilities in a timely manner.`,
    `Client will make timely decisions and obtain required management approvals, all consents, and/or licenses necessary from third parties required for Service Provider to perform its obligations outlined in this document.`,
    `Client will retain responsibility for its compliance with all applicable federal, state/provincial and local laws and regulations.`,
    `Service Provider will be entitled to rely on all Client decisions and approvals made in relation to this SOW. Although nothing in the SOW will require Service Provider to evaluate, advise on, modify, confirm, or reject such decisions and approvals, Service Provider will use its knowledge and expertise to guide client where appropriate.`,
    `Service Provider cannot provide assurance against all possible security vulnerabilities (even where the scope of the engagement involves identifying security vulnerabilities).`,
    `Additional time to conduct workshops required to accurately define business processes and requirements for the capabilities defined in this SOW may require a Change Order to be reviewed and executed by Service Provider and Client.`,
    `If changes to the SOW are identified and/or requested by Client or Service Provider during the course of the Project, a Change Order will be mutually agreed upon and executed by Client and Service Provider detailing the necessary scope modification and, if applicable, revisions to the Service Provider resources, associated fees, and like changes.`,
    `Service Provider will advise on selection of potential 3rd Party AppExchange applications as required to address Client business requirements based on publicly available information regarding application capabilities and functionality. Formal diligence and selection of the applications is outside the scope of this SOW.`,
    `Travel is not expected to be required for this engagement; provided, however, that any required pre-approved travel and out-of-pocket expenses shall be billed in addition to fees and paid by Client in accordance with the Agreement.`,
  ],

  // #15 — catch-all exclusion
  CATCH_ALL_EXCLUSION: `Any services not explicitly set forth in this SOW are deemed out of scope for this SOW, and will be performed pursuant to a separate statement of work or change order executed by the parties.`,

  // #16 — location of services
  LOCATION_OF_SERVICES: `Work pursuant to this SOW will be performed remotely from Service Provider corporate and home offices.`,

  // §10.1 defect handling — standard language carried in the live CPQ-migration SOWs (Tier 1 & Tier 2).
  // Renders as two paragraphs above the severity table.
  DEFECT_SEVERITY_INTRO: `Defects found in SIT or UAT are classified by severity. Service Provider commits to resolving in-scope Severity-1 defects before UAT sign-off; Severity-2 defects are resolved before sign-off where practical, but an open Severity-2 defect does not automatically block go-live; Severity-3 and Severity-4 defects are logged, dispositioned with the Client, and resolved during hypercare or deferred by mutual agreement.`,
  DEFECT_GONOGO: `Whether a defect blocks go-live is a Go/No-Go decision Service Provider and the Client make together, weighing the cost of the open defect against the cost of delaying go-live: the count of open Severity-2 defects, the soundness of any workaround, and the impact if the workaround is not followed. Open Severity-2 defects carried into go-live are documented with their workarounds and resolved during hypercare.`,

  // #12 — deemed-acceptance clause (5 business days)
  DEEMED_ACCEPTANCE: `Client will accept completed Deliverables (as outlined in the sections of this SOW), if they materially conform to the specifications set forth in this SOW and Service Provider has submitted the deliverable for review to the Client according to the Project Plan. Should a completed Deliverable not materially conform to the specifications set forth in this SOW, Client will notify Service Provider of this non-conformance in reasonable detail within five (5) business days of delivery. Service Provider will have a reasonable period of time, based on the severity and complexity of the non-conformance, to correct the non-conformance. If Client fails to promptly notify Service Provider of any material non-conformance within five (5) business days after completed delivery, or unreasonable delays, then the completed Deliverable will be considered accepted by Client no later than the five (5) business days after delivery.`,

  // #18 — Time & Materials close. {TOTAL} = aggregate fee, {UPFRONT} = 25% dollar figure.
  TM_CLOSE: `The Professional Services described in this SOW are provided on a Time and Materials basis. We will bill on an hourly basis based on the actual hours worked in accordance with the hourly rates set forth herein, which may be subject to adjustment from time to time. The aggregate service fees for completion of the entire work set forth in this SOW are {TOTAL}. Any work outside the scope of this SOW shall be set forth in a separate statement of work.`,
  // #19 + upfront
  TM_UPFRONT: `All Fees and expenses will be invoiced and shall be due and payable in accordance with the terms of the Agreement. Upon SOW execution, an upfront invoice of {UPFRONT_PERCENT}% ({UPFRONT}) of the Total Estimated Fees will be submitted and payable in accordance with the terms of the Agreement. This upfront payment will be credited against the corresponding number of billable hours and netted against the final invoice(s).`,

  // #17 — Fixed Fee close. {TOTAL} = fixed fee.
  FIXED_CLOSE: `As compensation for providing the Services hereunder, you will pay us a fixed fee of {TOTAL} plus out of pocket expenses. These fees are based on the assumptions provided under this SOW. Service Provider is not obligated to perform any services related to assumptions unknown at the time of execution of this engagement or deemed to be outside the scope of this engagement. Service Provider will provide the consultants with roles identified in the Service Provider Roles and Responsibilities table above to perform the Services as outlined in this SOW.`,
  FIXED_INVOICES: `All invoices shall be due and payable in accordance with the terms of the Agreement.`,

  // #20 — expenses + sales tax carve-out
  EXPENSES_CARVEOUT: `Actual, reasonable travel and out-of-pocket expenses in accordance with the Customer’s expense policies and state sales tax, if any, are not included in the Fees and will be invoiced separately, in accordance with the Agreement.`,

  // #21 — remittance block
  REMITTANCE_BILLTO_LABEL: `We understand that our bills should be sent to:`,
  REMITTANCE_PAY_LABEL: `Please make payments as follows:`,
  REMITTANCE_CHECK: [`Use the payment instructions supplied with the confirmed contract profile.`],
  REMITTANCE_ELECTRONIC: [`No bank details are included in this synthetic example.`],

  // #26 / #27 / #28 — Miscellaneous Terms
  MISC_TERMS: [
    { title: `Order of Precedence.`, body: `In the event of any conflict, inconsistency, or ambiguity between the terms of this SOW and the terms of the Agreement, this SOW shall control solely as to the specific Services, Deliverables, fees, assumptions, milestones, and schedules described herein, and the Agreement shall control in all other respects, including, without limitation, payment rights, intellectual property, confidentiality, warranties, indemnities, limitations of liability, dispute resolution, and general legal terms.` },
    { title: `Limited Modification.`, body: `Except as expressly set forth in this SOW, this SOW does not amend, waive, or modify the Agreement. All terms of the Agreement not expressly modified by this SOW remain unchanged and in full force and effect.` },
    { title: `Project Assumptions.`, body: `Service Provider’s performance schedule, pricing, staffing, and deliverables under this SOW are based on the assumptions, dependencies, and Client responsibilities described herein. Any material change to such assumptions, scope, timing, or Client responsibilities may require an equitable adjustment to fees, resources, milestones, and delivery dates through a written change order executed by the parties.` },
    { title: `Delays; Rescheduling; Resource Reallocation.`, body: `Any delay caused by Client, including failure to timely provide dependencies, approvals, information, access, feedback, or required resources, shall automatically extend applicable schedules and milestone dates on a day-for-day basis, together with such additional time as reasonably necessary for remobilization and scheduling. If Client delays the project for more than ten (10) business days, Service Provider may reassign reserved personnel to other matters and reschedule Services subject to resource availability. Client-caused delays may result in additional fees, standby charges, rescheduling fees, or rate adjustments at Service Provider’s then-current rates.` },
  ],

  // #22 + #23 — signature preamble (offer-expiry + counterparts). {DATE} = return-by date.
  SIGNATURE_PREAMBLE: `Please indicate your agreement with these terms by signing and returning this SOW on or before {DATE} to enable the Service Provider to manage our resources and business. These terms are not valid if the Service Provider doesn’t receive this signed SOW by such date. This SOW may be executed in one or more counterparts and/or by facsimile or electronic submission, each of which will be deemed an original and all of which signed counterparts, taken together, will constitute one instrument. Service Provider looks forward to working with you on this important project.`,
  // #24 — authority to bind
  AUTHORITY_BIND: `Each person signing this document represents that he/she intends to and has the authority to bind his/her respective Party to this Statement of Work.`,
};

module.exports.LOE_FIXED_CLOSE = "The fixed fee for the services described in this letter is {TOTAL}, plus expenses expressly permitted by this letter and the Agreement. Work outside the stated scope requires a separately agreed change.";
