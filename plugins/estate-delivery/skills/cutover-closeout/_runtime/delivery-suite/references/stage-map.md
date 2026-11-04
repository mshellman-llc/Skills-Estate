# Delivery stages and routing

The [stage model](stages.json) is the authority for stage IDs and task owners.
It also names the exit gates used by `scripts/plan.py`. Read that model when
routing work. Keep accepted project changes with the executed agreement; this
reference lifecycle does not create contractual obligations.

## Work at each stage

| Stage | Work supported by the estate |
| --- | --- |
| S2D Handoff | Transfer the signed deal and its commitments. Retain the handoff package and receiving team's acceptance. |
| 01 Mobilize | Prepare the charter and kickoff. Establish governance and an initial backlog. Track access and environment setup separately from performing it. |
| 02 Analyze | Capture requirements and map the relevant processes. Preserve integration or migration inventories and known approval owners. On agile engagements, `backlog-refinement` grades stories for the next sprint. |
| 03 Design | Explain the architecture and configuration. Include relevant integration and migration plans; plan acceptance tests against the requirements. |
| 04 Build | Use the project's authorized implementation workflow. Keep build evidence and demonstrations separate from signed acceptance. On agile engagements, `sprint-planning` plans each sprint against capacity. |
| 05 Validate | Prepare and execute the applicable system or user acceptance tests. Track defects and cutover readiness against observed results. |
| 06 Deploy | Use the project's authorized deployment process. Prepare the cutover runbook and record acceptance under the executed agreement. |
| 06b Closeout | Complete the agreed hypercare and support transition. Retain lessons and reusable assets in the project's actual destination. |

Kickoff belongs to `delivery-kickoff`; validation belongs to `acceptance-testing`.
A status report cannot replace either workflow. Scope changes need current
commercial review and an authorized contract change where required. The
contract-review module checks an estimate's assumptions; it does not price it.

## Work across stages

Delivery-status maintains the agreed reporting cadence and records risks.
It also tracks decisions and potential scope changes. Writing-integrity applies
to every authored passage. Use the shared evidence methods for factual claims
and the brand library when rendering a styled artifact.

The signed scope and accepted changes determine committed figures. A proposed
estimate may supply a change candidate, but it does not amend the agreement.
Keep estimates and accepted commitments distinct.

For a request spanning stages, use valid existing artifacts as prerequisites.
Draft later work where the available evidence supports it, with unresolved
dependencies visible. Do not declare an exit gate passed without its actual
acceptance. A change to a previously accepted requirement needs its reason and
effect recorded before changing the baseline.

## Check project capabilities

Inspect the actual comparables library before answering a prior-deal question.
Preserve missing evidence when no such library is accessible. Check whether an
event or automation actually invokes the workflow; a stage transition does not
by itself prove that an agent ran. Use current project records for approval
tracking rather than asserting that an old governance gap still exists.

Pre-signature work belongs to the appropriate scoping or proposal task. This
router supports delivery against an accepted engagement. It neither creates
signature authority nor authorizes a production change.
