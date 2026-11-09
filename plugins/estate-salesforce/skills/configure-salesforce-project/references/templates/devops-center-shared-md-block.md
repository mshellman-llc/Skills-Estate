## Salesforce delivery contract

**Invariant: the shared development org and its integration branch agree at rest.**
`origin/{{DEVOPS_INTEGRATION_BRANCH}}` must equal the latest successful `{{DEVOPS_ENVIRONMENT}}`
GitHub Deployment SHA. `{{TRUNK}}` remains the first DevOps Center pipeline branch. DevOps Center
owns every merge into `{{TRUNK}}` and every promotion beyond it. The integration branch,
`{{TRUNK}}`, and `main` are permanent GitHub branches with deletion disabled.

Does NOT apply to docs-only changes (`docs/`, `*.md`, non-deployable files).

**Two Salesforce targets have different jobs.** Local `sf project` commands use the project-local
target org `{{ORG_ALIAS}}` and never pass `--target-org`. Every `sf devops` command uses
`--target-org {{DEVOPS_ORG_ALIAS}} --json`. DevOps Center project: `{{DEVOPS_PROJECT_ID}}`.

1. **Work item and two branches.** Move the DevOps Center work item to In Progress and preserve
   its generated `WI-######` branch as the pipeline package. Create `dev/WI-######` from the
   verified deployed `origin/{{DEVOPS_INTEGRATION_BRANCH}}` SHA in a separate linked worktree.
   Never merge the integration branch into the packaging branch.

2. **Build against the shared baseline.** Author or retrieve only named components in the
   `dev/WI-######` worktree. Record and review the delta from its integration base. Keep profiles,
   package artifacts, unrelated org noise, and another WI's changes out of the branch.

3. **Validate before integration review.** Commit first, run the staged gates and `/simplify`,
   then run a scoped deployment dry run from the exact development commit. Open its PR to
   `{{DEVOPS_INTEGRATION_BRANCH}}`. A receipt mismatch freezes new branches, rebases, merges,
   validations, and handoffs until the centralized landing coordinator repairs the state.

4. **Centralized landing only.** Local merges and real deploys to the shared org are blocked.
   The coordinator serializes the approved PR merge and exact merge-delta deployment, verifies
   the result, then publishes the successful `{{DEVOPS_ENVIRONMENT}}` deployment SHA. A failed
   deployment leaves the queue frozen for fix-forward or revert.

5. **Package the accepted WI exactly.** In the generated `WI-######` worktree, run
   `estate-devops-package --development-branch dev/WI-######`. It applies only the recorded
   development patch to the `{{TRUNK}}` baseline and writes the scope ledger. Review and commit
   both. Extra, missing, or non-identical files block the DevOps Center review.

6. **Make dependencies explicit.** If the patch does not apply cleanly, or the current deployed
   integration commit changed one of the same files, stop. Promote the predecessor first,
   preserve dependency order, or explicitly combine the WIs. Never copy the accumulated sandbox
   file into a package because Salesforce metadata components are indivisible at this boundary.

7. **Pipeline handoff.** Run quality and validate the packaged commit against the org, push it, and
   create the DevOps Center review to `{{TRUNK}}`. After human review and user approval, move the
   WI to Ready to Promote and use `promote-salesforce-changes`. Its plugin/capability preflight and
   promotion validation are mandatory. For a stale package branch, use the conflict-recovery
   workflow in `references/devops-center.md`. A shared-org deployment is a milestone, not ticket
   completion or evidence of stage promotion.

**Protected branches:** do not manually merge into `{{DEVOPS_INTEGRATION_BRANCH}}`, `{{TRUNK}}`,
or `main`; do not deploy those branches locally. Repository protection and the centralized
coordinator cover browser actions that local hooks cannot observe.

Deep reference in `configure-salesforce-project`: `references/devops-center.md` (the full seam),
`references/hooks/README.md` (deterministic enforcement), and `workflow-steps.md`. Run
`/configure-salesforce-project audit` if the contract, receipt, pipeline, or repo disagree.
