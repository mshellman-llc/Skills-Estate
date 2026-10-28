---
name: sf-deploy-engine
description: "Operate an existing Salesforce deployment pipeline using its current configuration, documented commands, release state, and authorization controls."
---

# Sf deploy engine

Read [shared workflow](references/estate/workflow.md). For a rendered or branded artifact, read [brand policy](references/estate/brand.md) before choosing visual values. These references are generated from the canonical policies when the estate builds.

Read the project's pipeline configuration and current deployment-engine documentation. Establish which integration and commands actually exist. If no engine is configured, report that fact and prepare a setup proposal instead of inventing an endpoint or running a different deployment path.

Resolve source commit, ticket set, target environment, route, validations, test policy, freeze state, and authorized operation. Use org-preflight to verify the destination identity. Inspect status before promotion, retry, rollback, pause, or recovery.

For a release, verify the selected changes and dependencies, run the required validation, and preserve the exact result associated with the source revision. Execute only the authorized stage. Re-query status until completion or a concrete failure; a queued request is not a completed deployment.

For rollback or freeze recovery, inspect the failure and the engine's supported recovery operation. State affected changes and recovery limits before an action not already authorized. Report commit, environment, operation ID, test result, and final observed state. Do not skip tests or bypass a freeze based on stale instructions.

## Working contracts and validation

Read [restored workflow and checks](references/restored-workflow.md) when preparing this artifact or running its deterministic checks. Preserve the current instructions above; the adapter contract states its supported format and limits.
