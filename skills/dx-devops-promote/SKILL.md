---
name: dx-devops-promote
description: "Promote authorized Salesforce DevOps Center work items or pipeline stages after capability, target, dependency, and validation checks."
---

# Dx devops promote

Read [shared workflow](references/estate/workflow.md). For a rendered or branded artifact, read [brand policy](references/estate/brand.md) before choosing visual values. These references are generated from the canonical policies when the estate builds.

Inspect the installed plugin's capabilities and the current pipeline. Resolve work items, source and destination stages, branches, metadata overlap, and permissions. Use org-preflight to verify the target organization.

Validate preconditions before preparing or promoting. If branches are stale, inspect the divergence and preserve work before using the supported recovery path. Combine work items only when the user authorizes the combined release and the metadata dependencies justify it.

Prepare the exact work-item set and run the required validation. Review test results and conflicts. Execute the authorized promotion using the supported integration; do not substitute a direct production deploy for a failed DevOps Center operation.

Track the promotion's operation ID and re-query its final status. Complete follow-up transitions only when their prerequisites are observed. Report the work items, target, validation, final promotion result, and remaining action. Starting a promotion does not establish completion.
