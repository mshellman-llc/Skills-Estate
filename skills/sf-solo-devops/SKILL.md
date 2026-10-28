---
name: sf-solo-devops
description: "Deliver an authorized change to a single-org Salesforce project using its issue, branch, validation, review, deployment, and acceptance process."
---

# Sf solo devops

Read [shared workflow](references/estate/workflow.md). For rendered artifacts, read [brand policy](references/estate/brand.md).

Verify that the project uses a single target organization rather than a deployment pipeline. Read the current project instructions, issue, repository status, and org identity. Preserve dirty work and use isolation when needed.

Implement the scoped change, run relevant static and unit checks, review the diff for behavior and secrets, and validate against the verified org. Use the project's actual review and merge sequence. Do not assume a committed change passed checks merely because a hook exists.

Deploy only the authorized revision and track the deployment job ID. Verify its final result and the affected behavior in the organization. If a merge succeeds but deployment fails, report the divergence and recovery action; never claim an atomic transaction across Git and Salesforce.

Update the issue with the commit, review, validation, deployment, and acceptance evidence. Close it only when its completion criteria are met. Remove temporary worktrees only after preserving needed work. Pipeline-based releases belong to sf-deploy-engine or DevOps Center.

## Working contracts and validation

Read [restored workflow and checks](references/restored-workflow.md) when preparing this artifact or running its deterministic checks. Preserve the current instructions above; the adapter contract states its supported format and limits.
