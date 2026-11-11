# Solo Salesforce command workflow

Run local preparation without an org. Continue to org validation and deployment only after the target is confirmed, identity preflight passes, and the requested action is authorized. Replace command placeholders with project values; do not execute them literally.

## 1. Establish the change

Read the existing issue or create one when the requested scope authorizes GitHub updates. Use `github-repository-work` or the authenticated CLI. If GitHub is unavailable, preserve a local change brief with acceptance criteria and keep external issue creation pending.

```bash
gh issue list --search "requested behavior"
```

Write a substantive issue or PR body to a file and use `--body-file`. Keep its source requirements and acceptance criteria explicit. Use `refs #N` while work is pending; do not use a closing keyword to imply deployment completion before it occurs.

## 2. Isolate source changes

Reuse a suitable existing worktree or create one from the confirmed base branch:

```bash
git worktree add ../project-change -b feat/42-description main
```

Use the returned directory for subsequent commands. Preserve uncommitted work. Do not nest a new worktree inside an agent-managed checkout or remove a checkout another task still uses.

The Node helper may link dependencies from the main checkout. It never copies an org alias. Check the installed package manager and tool versions before running project scripts.

## 3. Prepare and check locally

Read the project's package scripts and run the applicable lint, unit-test, formatting, and static-analysis commands. Typical commands are:

```bash
npm run lint
npm test
npm run pmd
```

These examples depend on the project defining those scripts. Use the project's actual commands and retain their output. A commit succeeding does not prove each hook ran.

Review the code for behavior, reuse, maintainability, and Salesforce conventions. Use `code-simplify` when available; a direct review can perform the same work. Fix findings before committing the reviewed files.

Generate permissions from local metadata:

```bash
python3 scripts/gen-permset.py --out /tmp/new-permission-preview.xml
python3 scripts/gen-permset.py --write
python3 scripts/gen-permset.py --fail-on-drift
```

The first command needs a new preview path outside SFDX projects. The second requires a verified linked worktree. Initialize and review the project configuration first if it does not exist. Inspect the grants, exclusions, and skipped fields; the generated XML has not yet passed Salesforce validation.

Stage the intended files explicitly and inspect the staged diff. Commit with the issue reference. Save the exact commit and test outputs.

## 4. Finish a preparation task without an org

Save the source commit, changed component list, generated permission set, local checks, proposed Apex test list, and requested acceptance checks. Identify the missing test org once. Report the output as prepared locally; keep Salesforce validation, deployment, and acceptance testing pending.

Do not call an existing alias to discover whether it is a suitable disposable org. Do not install a default target or fabricate a passing validation receipt.

## 5. Validate with a confirmed org

When the user supplies a target, use `org-preflight` with its exact intended ID and the same connection that will run the operation. Retain that receipt privately. For a development-org dry run:

```bash
sf project deploy start --dry-run --target-org CONFIRMED_ORG --json \
  --source-dir force-app/main/default/classes/ChangedClass.cls \
  --source-dir force-app/main/default/classes/ChangedClassTest.cls \
  --test-level RunSpecifiedTests --tests ChangedClassTest
```

Replace the source and test list with the reviewed package. Inspect related callers, triggers, flows, and acceptance criteria when choosing tests. Use broader test levels when project policy or the target requires them. `NoTestRun` is limited to supported development environments; it is not a general shortcut for production changes. Consult [Salesforce's deployment test-level reference](https://github.com/salesforcecli/plugin-deploy-retrieve/blob/main/messages/deploy.metadata.md).

Production validation and quick deployment have their own supported commands and test requirements. Use that path only for an authorized production release. Preserve the validation job ID and its eligible package; do not treat an unrelated prior validation as proof for a changed commit.

A dry run is an org operation and does not fit the offline path. Commit first, run the validation, and repeat after any relevant change. Record the raw result and exact source SHA. The reference recorder refuses to credit dirty source.

## 6. Review and merge

Create the PR against the project's intended base. Include the problem, resulting behavior, relevant local checks, org validation if it happened, and any remaining acceptance work. Follow branch protections and merge authorization. The solo reference hooks expect a squash merge and a validation record for the PR's head commit.

Do not bypass the validation gate to make an offline task appear deployed. A preparation PR can remain open until a target exists. Keep a deployment issue open until its requested completion criteria are met.

## 7. Deploy the reviewed release

From the clean main checkout, fetch and update to the confirmed merged commit. Verify its identity against the remote branch and preserve the package contents. Repeat org preflight if the connection or target changed.

```bash
sf project deploy start --target-org CONFIRMED_ORG --json \
  --source-dir force-app/main/default/classes/ChangedClass.cls \
  --source-dir force-app/main/default/classes/ChangedClassTest.cls \
  --test-level RunSpecifiedTests --tests ChangedClassTest
```

For an async operation, retain the complete start JSON and extract its job ID using a JSON parser. Query only that job on the same explicit target:

```bash
sf project deploy report --target-org CONFIRMED_ORG --job-id RECORDED_JOB_ID --json
```

Never use `--use-most-recent`. Retain failed, canceled, and incomplete results as well as successes. A `Succeeded` string is insufficient: inspect the complete structured result and distinguish check-only from a real deployment.

If deployment fails, preserve the failure and determine actual org state before choosing a fix or rollback. A Git revert alone does not undo Salesforce changes.

## 8. Verify behavior and close the requested work

Run the acceptance checks against the deployed version and confirmed org. Record each result and any user testing the project requires. Update the issue only when authorized; automated GitHub comments are off by default and require explicit project opt-in.

For deployment work, report the merged commit, deployment job, target, and acceptance evidence. For preparation work, report the local artifacts and exactly which live steps remain. Remove a worktree only after preserving its needed files and confirming it is no longer in use. Git state, a local hook log, and a passing unit test establish different facts; keep them separate.
