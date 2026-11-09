## Salesforce delivery contract

**Invariant: DevOps Center owns stage branches and promotion.** `{{ORG_ALIAS}}` is a branchless
development environment for local build and validation. `{{TRUNK}}` is the landing branch derived
from the first linked pipeline stage. DevOps Center owns every merge into it and every promotion
beyond it. `main` and `{{TRUNK}}` are pipeline branches, not local deployment branches.

Does NOT apply to docs-only changes (`docs/`, `*.md`, non-deployable files).

**Two Salesforce targets have different jobs.** Local `sf project` commands use the project-local
target org `{{ORG_ALIAS}}` and never pass `--target-org`. Every `sf devops` command uses
`--target-org {{DEVOPS_ORG_ALIAS}} --json`. DevOps Center project: `{{DEVOPS_PROJECT_ID}}`.

1. **Work item first.** Create or find the DevOps Center work item with
   `manage-salesforce-devops`. Move it to In Progress and use the exact branch DevOps Center
   creates from `{{TRUNK}}`, normally `WI-######`. Do not invent a feature branch, reuse another
   WI, or look for a branch owned by the development environment.

2. **Worktree always.** Fetch the WI branch, then open it as a linked worktree. Never edit
   `force-app/` in the main checkout and never nest worktrees. Human Setup or DX Inspector edits
   are allowed, but retrieve only named components into this WI worktree and review the diff.

3. **Build and capture.** Author locally or in `{{ORG_ALIAS}}`. Use scoped source tracking or a
   named-component retrieve. Never retrieve the whole org over the repo. Keep package artifacts,
   profiles, and unrelated environment noise out of the change.

4. **Quality and validation.** Commit first. Run the staged quality gates and `/simplify`, then
   validate the exact WI commit with `sf project deploy start --dry-run`, explicit source paths,
   and the narrowest correct test level. A real deploy is allowed only from this WI worktree to
   `{{ORG_ALIAS}}`, never from `{{TRUNK}}` or `main`.

5. **Push, then create review.** Push the WI branch and use `manage-salesforce-devops` to create
   the DevOps Center review. Do not run `gh pr merge`: the open PR is a promotion prerequisite,
   and DevOps Center owns the merge. Keep one WI per branch and use squash semantics.

6. **Handoff.** After review and local evidence are green, move the WI to Ready to Promote.
   From this point use `promote-salesforce-changes`; its plugin/capability preflight and validate step are
   mandatory. DevOps Center decides which ready WIs move to `{{TRUNK}}` and later `main`, deploys
   them, and records the result. For a stale WI branch, follow the conflict-recovery workflow in
   `references/devops-center.md` and change only the WI branch.

7. **Done locally = all five:** WI branch pushed + review open + quality and dry run green +
   acceptance criteria checked in `{{ORG_ALIAS}}` + user green light. Promotion and production
   completion are separate DevOps Center states. Never claim them from local Git evidence.

**Protected branches:** do not manually merge into `{{TRUNK}}` or `main`, do not deploy either
branch with `sf project deploy`, and do not repair pipeline state with ad hoc Git. Use the DevOps
Center work-item and promotion skills so associated PR and promotion records stay intact.

**Escape hatches remain recorded**, but none authorizes a manual stage merge or stage deploy.
If a guard blocks a legitimate WI action, read its message and repair the configuration.

Deep reference in `configure-salesforce-project`: `references/devops-center.md` (the full seam),
`workflow-steps.md`, `seeding-guide.md`, `drift-reconcile.md`, and `host-adapters.md`. Run
`/configure-salesforce-project audit` if this contract and the repo disagree.
