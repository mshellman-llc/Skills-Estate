---
name: uat-validation
description: "Prepare and track acceptance testing, requirement traceability, defects, coverage, and the evidence for a go/no-go decision."
---

# Uat validation

Read [shared workflow](references/estate/workflow.md). For rendered artifacts, read [brand policy](references/estate/brand.md).

Read the requirements baseline, test plan, acceptance terms, environment, and actual build status. Identify which requirements are ready to test. Do not count an unbuilt feature as covered by a passing test.

Create test cases with requirement IDs, prerequisites, data, steps, expected results, tester, and actual result. Include important negative, permission, integration, and recovery paths. Separate planned, executed, passed, failed, and blocked tests.

Maintain defects with severity as defined by the project, impact, reproduction evidence, owner, state, workaround, and retest result. Compute coverage using explicit denominators: requirements with test cases and requirements with sufficient passing evidence are different measures.

Prepare readiness and go/no-go evidence against the agreement's actual criteria. Show unresolved defects and decision owners; do not infer acceptance from a percentage or invent signatures. Execution of cutover belongs to cutover-closeout after authorization.
