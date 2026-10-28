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

## Recompute traceability and coverage

For CSV-based UAT records, use the restored local checker: `python3 scripts/trace_check.py --requirements requirements.csv --scripts tracker.csv --gaps gaps.csv --gonogo counts.json`. Its module documentation defines supported column names and the JSON count fields. The bundled [tracker](assets/uat-tracker-template.csv), [coverage gaps](assets/coverage-gaps-template.csv), and [defect log](assets/defect-log-template.csv) are starting schemas; adapt them to the user's existing records without inventing test results. [The test-script template](assets/test-script-template.md) separates prerequisites, steps, expected behavior, and observed results.

Every requirement must trace to a test script or an explicitly owned coverage gap. Unknown requirement references and unacknowledged orphan scripts fail the check. Counts must recompute from the actual tracker. Script coverage does not prove test execution, passing behavior, readiness, or acceptance. Continue to evaluate those separately from actual results and the agreement's criteria. Keep descriptive names in reader-facing reports and IDs in traceability tables.

Run `python3 scripts/trace_check_selftest.py` after modifying this adapter. No external account or service is contacted by the checker.
