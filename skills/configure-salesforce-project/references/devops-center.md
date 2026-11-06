# DevOps Center local-loop handoff

Use this reference when `git config estate.delivery` is `devops-center`.

## Ownership boundary

| Concern | Owner |
|---|---|
| Work item creation, status, WI branch lookup, review creation | `manage-salesforce-devops` |
| Linked worktree, scoped retrieve, local quality, dry run, development-org feedback | this local loop |
| Merge into `staging`, selective WI promotion, stage deployment | `promote-salesforce-changes` |
| Pipeline, stages, environments, project attachment, activation | `dx-devops-pipeline-manage` |
| Required centralized tests for UI/DX Inspector and other hook-bypassing paths | DevOps Testing and repository checks |

## Choose the development work model

`estate.devops.workmodel=isolated` is the default. It matches Salesforce's intended model: each
developer has an isolated development environment, and the DevOps-generated WI branch is both the
development branch and the pipeline package.

Use `estate.devops.workmodel=shared` only when several developers or agents intentionally share
one persistent development org. Salesforce recommends separate development environments and
documents two shared-org hazards: one person's commit can remove a component from another
person's change list, and a committed file can include someone else's latest changes. Next-
generation back sync also performs a full deployment that can overwrite unpromoted changes.

- [Salesforce guidance for shared development environments](https://help.salesforce.com/s/articleView?id=platform.devops_center_dev_environment_sharing.htm&language=en_US&type=5)
- [Salesforce guidance for next-generation back sync](https://help.salesforce.com/s/articleView?id=platform.devops_center_sync_dev_environment.htm&language=en_US&type=5)

Shared mode is a deliberate compatibility layer for that constraint, not the preferred topology.
It requires GitHub because successful GitHub Deployment records are the centralized, cross-clone
authority. Clone-local files under `.git/estate` cannot serialize several agents. The
integration branch and permanent pipeline branches must also exist on GitHub with deletion
blocked by classic branch protection or an active ruleset.

## Pipeline branch and environment topology

A connected development environment has no dedicated Git branch. DevOps Center compares and
synchronizes it against the first pipeline stage, while each In Progress WI receives a transient
feature branch. Do not create or seed a branch named for the development sandbox.

Pipeline stages form a linked list through `nextStageId`. The landing stage is the unique stage
whose `id` is not referenced by another stage's `nextStageId`; its `branchName` is the source for
new WI branches and the target for their first review. This is the same first-stage algorithm used
by the Salesforce DevOps Center CLI. Resolve it with:

```bash
scripts/resolve-devops-landing.sh \
  --pipeline-id <pipeline-id> \
  --project-id <project-id> \
  --target-org <devops-alias>
```

The configured `estate.trunk` is this landing branch for compatibility with the existing hook
surface. It does not mean the development org equals that branch. Before a pipeline exists, init
may record an explicit provisional value, but it must be rerun with the pipeline id before audit
can report the DevOps Center contract fully armed.

There is no extra local command that associates a commit to a work item. The association is the
DevOps Center-created `WI-######` branch, the same WI token in the commit message, the pushed
branch, and the DevOps Center review. Do not invent another branch and do not manually merge the
review.

That paragraph applies to isolated mode. Shared mode adds one development branch because the
shared org can contain accepted work that has not reached the landing stage. The generated
`WI-######` branch still remains the only DevOps Center package and review branch.

## Shared development-org loop

Shared mode records three additional facts:

```bash
git config estate.devops.workmodel shared
git config estate.devops.integrationbranch integration-dev
git config estate.devops.environment ExampleDevelopment
```

The at-rest invariant is:

```text
origin/<integration branch> == latest successful <environment> GitHub Deployment SHA
```

`estate-devops-shared-status` refreshes the remote ref, reads GitHub Deployments and statuses,
and compares the two SHAs. Missing authentication, an absent successful receipt, an unreachable
remote, and a SHA mismatch are all unverified states. The shared workflow stops because none of
those states proves the org baseline.

The permanent branches must also be protected against deletion. GitHub's automatic
delete-after-merge setting operates outside local hooks. If a stage branch is deleted after it is
used as a pull request head, later DevOps Center transitions can lose the branch they depend on.
Audit and the handoff guard verify the remote branch and its deletion restriction before work is
handed to either landing path.

1. Set the WI status to In Progress so DevOps Center creates `WI-######` from the landing branch.
2. After the centralized receipt is synced, create `dev/WI-######` from
   `origin/<integration branch>` in its own linked worktree.
3. Build and commit the change, execute the repository gates, and validate that exact commit against the shared
   org. Open its PR to the integration branch.
4. A repository-owned coordinator serializes the approved merge and deployment, verifies the org,
   and publishes the successful GitHub Deployment SHA. Local hooks block local merges and real
   deploys because they cannot hold or prove the cross-clone lease.
5. From the generated `WI-######` worktree, run
   `estate-devops-package --development-branch dev/WI-######`. The helper verifies that the
   integration branch is deployed, confirms every owned file still equals the accepted
   development head, applies the exact patch to the pipeline baseline, and writes
   `.estate/work-items/WI-######.json`.
6. Review, commit, and validate the packaged source plus ledger. The handoff guard recomputes the
   file set and blob identities before it permits a DevOps Center review.

The skill does not install a Salesforce deployment workflow. Authentication, test selection,
branch protection, approval policy, and post-deploy verification belong to the repository and
org. Shared mode audits the successful deployment receipt and fails closed until that coordinator
exists. This prevents a generic installer from inventing credentials or a test policy for a live
org.

If another accepted WI changes one of the same files before packaging, the exact-file comparison
blocks. Promotion order, a declared dependency, or an explicit combined WI must resolve the
overlap. Copying the current shared-org file would silently include both WIs.

## Isolated AI or VS Code path

1. Find or create the work item with `manage-salesforce-devops`.
2. Move it to In Progress and read back the exact branch name.
3. Fetch that branch and add it as a linked worktree. Do not create a replacement branch.
4. Author locally, or make a narrow Setup/DX Inspector change in the configured development org.
5. For org-authored work, use source tracking to identify the named component and retrieve only
   that component into the WI worktree. Review the diff before staging.
6. Commit with the same WI token. Run local quality and a scoped dry run from that commit.
7. A real deployment for feedback is allowed only from the clean WI worktree to the project-local
   development org. It is not promotion evidence.
8. Push the WI branch. Create the review through `manage-salesforce-devops`, or use
   `gh pr create --base "$(git config estate.trunk)"` when the DevOps Center review API is
   unavailable.
9. Obtain human review and move the work item to Ready to Promote. Do not merge the PR.
10. Use `promote-salesforce-changes`. Its validate step is mandatory and verifies the associated review
    before DevOps Center merges and deploys the selected work item.

The ordinary VS Code Source Control stage/commit/push interface is compatible with this path.
Git hooks still enforce the WI branch and message when VS Code invokes Git. Actions performed in
Salesforce or GitHub's web UI do not run local hooks, so required organizational checks must also
exist in DevOps Testing or branch protection.

## Human/DX Inspector path

A human can move a WI to In Progress, edit in the development org, select changes in DX Inspector
or DevOps Center, and commit them to the generated WI branch. The same branch and review provide
the handoff. Before Ready to Promote, confirm the centralized tests cover
the quality gates that a web-generated commit did not run locally.

## Two org aliases

The project-local Salesforce target is the branchless development org, such as `sandbox-a`. Local
`sf project retrieve` and `sf project deploy` commands rely on it and never pass `--target-org`.

DevOps Center commands target the control org explicitly:

```bash
sf devops work-item list --project-id <id> --target-org <devops-alias> --json
```

The hook requires the configured `estate.devops.orgalias` and `--json` on `sf devops` commands.
This prevents a project-local development target from silently receiving a DevOps Center API call.

## Promotion capability preflight

Before any promotion workflow, inspect the installed `@salesforce/plugin-devops-center` version
and its command manifest. The promotion skill requires a supported 2.x release and verifies that
promotion validation, work-item preparation, and the promote validation-bypass flag are actually
present. Version text alone is not enough. Stop with an installation or upgrade instruction when
the plugin or a required capability is missing. Do not improvise older command shapes.

The generated project contract keeps this rule high-level. The exact supported version and flags
belong to `promote-salesforce-changes`, where they can change without rewriting every repository contract.

## Stale WI branch conflict recovery

When a stage branch advances after a WI branch was created, repair only the WI branch in its
linked worktree. Never merge locally into a stage branch or `main`.

1. Confirm the worktree is clean, fetch the remote, and resolve the current target-stage tip.
2. Before mutation, inspect the three-way result where possible. For example, use `git merge-tree`
   with the merge base, WI head, and fetched stage tip. Record the expected conflicting files and
   review the stage changes since the WI base.
3. In the linked WI worktree, merge `origin/<target-stage-branch>` into the existing WI branch.
   The direction is stage into WI, never WI into stage.
4. Resolve conflicts by retaining the current stage baseline and folding the WI-specific
   regression or feature into it. Test suites and shared configuration restored by an earlier WI
   remain the baseline. Do not replace them with the stale WI copy. Review both the conflict set
   and the final net WI delta against `MERGE_HEAD`.
5. Run focused checks for the reconciled files and the full repository quality suite. Commit the
   merge, then run the scoped Salesforce deployment dry run from the clean worktree so the evidence
   identifies that exact commit.
6. Push the same WI branch. Do not open a replacement branch or PR. Verify the existing PR reports
   both clean merge state and mergeability against the target stage.
7. Run `sf devops promotion validate` again after the push. Only a successful validation for the
   same work-item set and target stage in this session permits promotion with validation bypassed.

The pre-commit hook detects this stage-sync shape when `MERGE_HEAD` equals a configured protected
stage tip. Formatting, ESLint, PMD, and Jest then use `git diff --cached MERGE_HEAD`, which is the
net WI delta after reconciliation. A chained repository hook receives `ALEY_MERGE_DIFF_BASE`; a
lint-staged-only hook is invoked directly with lint-staged's matching diff option.

If a more complex client hook cannot safely consume that comparison, do not rewrite or lint every
file imported from the stage. The recorded `git commit --no-verify` escape hatch is allowed only
after preserving independent evidence: the `MERGE_HEAD` file list, focused checks, the full
repository suite, and the exact-commit Salesforce dry run. Record the incompatible hook and why it
could not be scoped.

## Environment-specific references

Sandbox refresh is the clean starting point because Salesforce rewrites many sandbox-scoped
references, including usernames, during the copy. A metadata deployment can still fail when a
referenced user does not exist in the target, when more than one rewritten username is plausible,
or when a component stores membership as data rather than metadata. Public-group membership and
similar user assignments should be treated as environment configuration, not normalized into the
metadata baseline.

Keep environment data/configuration in an idempotent configuration runner with explicit stage
inputs. Do not put sandbox usernames into source merely to make one environment deploy.

## Pre- and post-deploy behavior

DevOps Center has no direct equivalent of an engine's arbitrary pre/post anonymous Apex hook with
run-once and freeze semantics. Do not carry a historical scripts folder into the new repository.
Classify each old action instead:

- metadata dependency: include it in the WI source and promotion;
- repeatable environment configuration: use idempotent Apex or a data/configuration job whose
  desired state can be verified;
- one-time migration: run it through a reviewed GitHub Action or migration runner keyed by a
  durable migration ID, after the DevOps Center deployment succeeds;
- historical or already-applied action: archive it outside the active execution path.

A future GitHub Action may call an idempotent migration runner after a confirmed DevOps Center
promotion. It must record target org, promotion/deploy ID, migration ID, result, and retry state.
An Apex callout that asks GitHub to compute inverse metadata is technically possible, but it adds
credentials, asynchronous coordination, API limits, and a second control plane. Treat it as a
later recovery feature. The pilot does not depend on it.

## Recovery seam

First use DevOps Center's work-item and promotion records to understand what moved. A bad promotion
is repaired by a new WI that reverts or fixes the exact source delta, then follows the same review
and promotion path. Do not push an inverse package directly from Apex into a stage org while Git
still says the bad source is current. Any future inverse-delta automation must create reviewed
source first and make the deployment a consequence of that source change.
