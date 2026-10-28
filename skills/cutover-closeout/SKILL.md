---
name: cutover-closeout
description: "Prepare a cutover runbook, go-live acceptance record, hypercare plan, and delivery closeout from the approved release and executed scope."
---

# Cutover closeout

Read [shared workflow](references/estate/workflow.md). For a rendered or branded artifact, read [brand policy](references/estate/brand.md) before choosing visual values. These references are generated from the canonical policies when the estate builds.

Read the release plan, test results, actual go/no-go decision, executed scope, acceptance rules, and support ownership. Preparing a runbook is allowed before approval; executing cutover depends on the authorization and target environment.

For each cutover step, specify owner, prerequisites, action, expected result, validation, timing, and rollback or stop condition. Order dependencies explicitly. Identify the last reversible point and who can make the go/no-go decision. Never invent a successful rehearsal or rollback test.

Track go-live acceptance against the agreement's actual criteria. Record open defects and agreed dispositions. Deemed acceptance applies only if the governing agreement contains it and its conditions are evidenced; elapsed time alone is insufficient.

During hypercare, track impact, severity, owner, workaround, resolution, and confirmation. Closeout covers deliverables, acceptance, access and support transition, remaining obligations, operational documentation, and lessons. Distinguish technical deployment, business acceptance, support handover, and project closure in the final record.

## Working contracts and validation

Read [restored workflow and checks](references/restored-workflow.md) when preparing this artifact or running its deterministic checks. Preserve the current instructions above; the adapter contract states its supported format and limits.
