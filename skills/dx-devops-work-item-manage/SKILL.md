---
name: dx-devops-work-item-manage
description: "Manage Salesforce DevOps Center work items, branches, changes, and review requests through the installed integration. Use for work item lifecycle operations, not promotion."
---

# Dx devops work item manage

Read [shared workflow](references/estate/workflow.md). For a rendered or branded artifact, read [brand policy](references/estate/brand.md) before choosing visual values. These references are generated from the canonical policies when the estate builds.

Inspect the installed DevOps Center capabilities and current project configuration. Verify the Salesforce target and resolve the work item by stable ID. Check branch, working-tree changes, current status, and permissions before mutation.

For creation or updates, use the actual supported fields and preserve unrelated values. For commits, inspect the complete intended diff, exclude secrets and unrelated work, and use the work item's expected branch. Do not treat a successful local commit as a pushed or reviewed change.

For a status transition or review request, verify prerequisites and use the integration's supported operation. Avoid guessed API payloads from an older skill. An unavailable command is a tooling gap, not permission to bypass the process.

Read back the work item, branch, commit, or pull request after each requested change. Report IDs, URLs, and observed state. Route promotion to dx-devops-promote. Do not change status merely to make a blocked work item look ready.
