---
name: dx-devops-promote
description: 'Use this skill to drive the full DevOps Center promotion workflow for work items and pipeline stages — inspect plugin capabilities, validate preconditions, conditionally prepare work items, recover stale WI branches, optionally combine work items that share metadata, promote one or more work items or an entire stage, and complete the promotion. TRIGGER when the user wants to promote a work item, advance changes to the next environment or stage, recover a promotion conflict, combine work items, or move metadata through the release pipeline. The capability and validate steps run before mutation. DO NOT TRIGGER for work item creation or status updates (use dx-devops-work-item-manage), or for polling an existing promotion''s status.'
metadata:
  accessCheck: '[{''type'': ''orgPref'', ''value'': ''ALMDevopsCorePref''}, {''type'': ''userPerm'', ''value'': ''UserHasDevOpsCore''}]'
  cliTools: '[{''tool'': [''python3''], ''semver'': ''>=3.9''}, {''tool'': [''sf''], ''semver'': ''>=2.0.0''}]'
  domains: '[''Developer Experience'']'
  minApiVersion: '58.0'
  relatedSkills: '[''dx-devops-work-item-manage'']'
  version: '1.1'
---


# DevOps Center Promotion

Guides validation, conditional preparation, combination, promotion, and completion in DevOps Center. Retain each structured command response and its operation identifier. A successful command start does not prove deployment completion, and retry safety must be checked for the particular operation.

## Work without an org

The bundled capability inspector and stage router work locally with Python 3. They do not require jq. With a saved plugin manifest, `python3 scripts/preflight.py --manifest plugin.json` makes no Salesforce CLI call; without that flag it only runs local `sf plugins inspect`. Add `--require-combine` when the proposed workflow combines work items. The JSON receipt distinguishes local capabilities from org or promotion verification.

`python3 scripts/promotion-route.py --current-stage-id "" --target-stage-id FIRST --first-stage-id FIRST` exercises the first-stage route without a connection. Use synthetic inputs for practice and retain their outputs as local checks. A missing org stops the live phases below; it does not authorize using a cached alias or changing the machine default. Do not claim deployment acceptance from these local tools.

## Scope

  - **In scope**: Validate plugin capabilities and promotion preconditions, conditionally prepare a work item, recover a stale WI branch, combine work items that share metadata into one promotion, promote one or more work items or an entire source stage to a target stage, and complete the promotion
  - **Out of scope**: Work item creation/status updates (use `dx-devops-work-item-manage`), polling an existing promotion's status, pipeline or project setup (separate skills)

---

## Required Inputs

Gather or infer before proceeding:

- **Promotion target**: one or more specific work items, or all approved work items in a source stage
- **Target stage ID**: `--target-stage-id`, required for validate, combine, promote, complete, and for prepare only when prepare is routed
- **Work item ID(s)** or **source stage ID** — depending on the promotion target. `sf devops promote` takes `--work-item-id` (repeatable) XOR `--stage-id`
- **For combined promotion**: a parent work item ID and one or more child work item IDs that share metadata
- **Target org**: an explicitly authorized `--target-org <alias>` for this operation; never infer it from a machine default or cached alias.

Defaults unless specified:
- Output format: `--json` for headless consumption
- Test level: omit `--test-level` for development-stage deploys (defaults to `NoTestRun`); use `RunLocalTests` for production-stage deploys with Apex

If the user gives a clear request ("promote work item 1fkxx… to stage 1QVxx…", "promote the QA stage to UAT", "combine these work items and promote"), proceed once you have the required IDs.

---

## Workflow

All operations use `sf devops` CLI commands with `--json` output. Capability preflight runs before org access, and promotion validation always runs before mutation. All promotion commands are keyed on **record IDs**, not work item names. Resolve names to IDs first if needed.

### Phase 0 — Plugin and capability preflight

1. **Run the shipped preflight before starting:**
   ```bash
   scripts/preflight.sh
   ```
   - Require `@salesforce/plugin-devops-center >=2.0.0`; inspect the installed version and capabilities before use. The historical examples used 2.2.0; that is not a current deployment-verification claim.
   - Inspect the plugin manifest, not only version text. Require `devops:promotion:validate`, `devops:promote`, `devops:work-item:prepare`, `devops:promotion:complete`, and the promote `skip-validation` flag. Add `--require-combine` to require `devops:work-item:combine` before a combined promotion.
   - If the plugin is missing, obsolete, invalid, or lacks a capability, STOP with the exact failed check and an install/upgrade instruction. Do not substitute older or guessed commands.

### Phase 1 — Authenticate and Validate

2. **Verify org authentication** before any operation:
   ```bash
   sf org display --target-org <confirmed-alias> --json
   ```
   - If it fails, instruct the user to run `sf org login web --alias <confirmed-alias>`
   - Pass the confirmed `--target-org <alias>` on every command. A configured default is not confirmation of the target.

3. **Run the mandatory validate step**. This is non-negotiable and always runs before prepare/combine/promote. `sf devops promotion validate` requires the target stage (`-t/--target-stage-id`) and one or more `-i/--work-item-id`:
   ```bash
   # Capture the output — Phase 2 derives the combine decision from it deterministically.
   VALIDATE_JSON=$(sf devops promotion validate --work-item-id <id> --target-stage-id <target-stage-id> --target-org <alias> --json)
   ```
   - Validates whether the work item(s) can be promoted to the target stage — checks for VCS and object-permission errors (including the associated-PR requirement) before a promotion is attempted
   - Repeat `--work-item-id` to validate multiple work items in one call
   - **Success:** `status == 0` and `.result.success == true` — proceed
   - **If validation fails** (non-zero exit; e.g. `VCS_ERROR: No pull request exists…`, with `.result.errorType`/`.result.errorDetails` set), STOP. Report the error and do not proceed. If it references metadata overlap, resolve the conflict before retrying
   - **Shared components:** when `.result.combineDetails` is non-null, the work items share metadata — validate returns the parent/child grouping and `suggestions`. This is the authoritative signal for the Phase 2 combine decision (see step 6); do not guess whether to combine — the Phase 2 script reads `.result.combineDetails` from `VALIDATE_JSON`

### Phase 2 — Prepare (and optionally Combine)

4. **Route preparation before running it:**
   ```bash
   scripts/promotion-route.sh \
     --current-stage-id "${PIPELINE_STAGE_ID:-}" \
     --target-stage-id <target-stage-id> \
     --first-stage-id <first-linked-stage-id>
   ```
   - If the development WI has no `PipelineStageId` and is entering the first linked pipeline stage, the route is `skip`. Do not call prepare. DevOps Center already owns this normal first-stage path.
   - If the WI already has a pipeline stage and is being promoted one-off to another pipeline stage, the route is `prepare`.
   - If the WI has no stage but the requested target is not the first linked stage, STOP as ambiguous. Do not guess or force preparation.
   - Resolve the first linked stage from pipeline topology and read the WI's `pipelineStageId`/`PipelineStageId` from current DevOps Center data.

5. **Prepare only when the route is `prepare`:**
   ```bash
   sf devops work-item prepare --work-item-id <id> --target-stage-id <target-stage-id> --target-org <alias> --json
   ```
   - This command is for one-off promotion between existing pipeline stages.
   - `--target-stage-id` is required and is the same target stage the work item will be promoted to.
   - Before retrying, inspect the returned status and current work-item state. Do not assume a repeated mutation is harmless.

6. **Derive combination from the saved validation response.** Save the complete Phase 1 JSON as `validation.json`; preserve the command receipt with its explicit org, target stage, work-item set, and source revision. Then run:
   ```bash
   python3 scripts/combine-plan.py --validation validation.json
   ```
   The helper requires numeric status 0 and `result.success: true`. An explicit null `combineDetails` produces `combine: false`. A combine object must have one parent and a nonempty list of distinct child IDs; missing or malformed details fail. It returns a JSON `arguments` array and the validation file hash. It never calls Salesforce or claims the saved response is current.

   If `combine` is true, rerun capability preflight with `--require-combine`. Confirm that the saved validation still belongs to the exact current org, work items, target stage, and unchanged source. Supply the returned argument list to `sf devops work-item combine`, followed by the confirmed `--target-stage-id`, `--target-org`, and `--json` flags. Use a structured process argument list; never shell-evaluate JSON text. Retain the result, and promote the returned parent only after combination succeeds.

   If `combine` is false, skip combination. If the user has identified additional dependencies not represented in validation, resolve and revalidate them before mutation. Older reference examples use jq as an optional shell parser; this bundled helper provides the same decision without that dependency.

### Phase 3 — Promote

7. **Promote to the target stage** — exactly one of `--work-item-id` or `--stage-id` must be provided; `--target-stage-id` is always required. **Pass `--skip-validation` ONLY when the exact work-item set and target stage passed Phase 1 validation in the current session and neither Git nor DevOps Center state changed afterward.** Otherwise, omit the flag and let the CLI run its built-in validation:
   - Promote one or more specific work items (repeat `--work-item-id` per item; use the parent's ID for a combined promotion). Include the `--skip-validation` line ONLY if Phase 1 validate passed this session; otherwise drop that line:
     ```bash
     sf devops promote \
       --work-item-id <id> \
       --target-stage-id <target-stage-id> \
       --skip-validation \
       --target-org <alias> \
       --json
     ```
   - Or promote all approved work items from a source stage (again, include the `--skip-validation` line only if Phase 1 validate passed this session):
     ```bash
     sf devops promote \
       --stage-id <source-stage-id> \
       --target-stage-id <target-stage-id> \
       --skip-validation \
       --target-org <alias> \
       --json
     ```
   - **Why conditional:** `sf devops promote`'s built-in pre-promote validation runs the *same* checks as the Phase 1 `sf devops promotion validate` step (including the associated-PR requirement). When the full workflow ran sequentially this session, that validation already passed, so `--skip-validation` only eliminates a redundant re-run. But if the agent resumed mid-workflow, promotion was invoked without a preceding Phase 1 validate, or Phase 1 was not run for every work item being promoted, DO NOT pass `--skip-validation` — bypassing it there would skip validation entirely with no prior guard
   - Add `--deploy-all` to deploy all metadata in the branch rather than only changes not yet in the target stage
   - Add `--test-level RunLocalTests` (or `RunSpecifiedTests --tests <names>`) for production-stage deploys that include Apex
   - The deploy runs asynchronously — capture the returned promotion/deploy identifier from the JSON `.result`

### Phase 4 — Complete and Report

8. **Complete the promotion** to finalize — advances the work items in the target stage:
   ```bash
   sf devops promotion complete --target-stage-id <target-stage-id> --target-org <alias> --json
   ```
   - Run after the promote deploy succeeds to mark the promotion done in the target stage
   - `--target-stage-id` is required (same target stage the work items were promoted to)

9. **Report the outcome**:
   - Confirm the CLI returned status 0 for each step
   - Report the promotion/deploy identifier and note that async deploy completion is tracked separately
   - Do NOT block or busy-wait inside this skill — surface the identifier and return
   - State the promotion clearly: e.g., "Work item promotion initiated (source stage → target stage). Deploy ID: <id>. Poll this ID to confirm deploy completion, then run promotion complete."

---

## Rules / Constraints

| Constraint | Rationale |
|-----------|-----------|
| Validate ALWAYS runs first | Guarantees preconditions are met before any mutation; skipping it can corrupt pipeline state |
| Plugin version and capabilities are inspected first | A CLI version can be installed yet lack required commands or flags; fail on skew instead of improvising |
| All `sf devops` commands must use `--json` | Structured output is required for headless consumption; human-readable output is unreliable to parse |
| Commands are keyed on record IDs, not names | `--work-item-id`, `--stage-id`, `--target-stage-id`, `--parent/--child-work-item-id` all take IDs; resolve names to IDs first |
| `--target-stage-id` required for validate, combine, promote, complete, and routed prepare | The target stage is mandatory; prepare itself is conditional |
| Exactly one of `--work-item-id` or `--stage-id` on promote | These flags are mutually exclusive; promote either specific items or a whole source stage |
| Pass `--skip-validation` only for the exact validation that passed this session | Work-item set, target stage, branch head, PR state, and DevOps Center state must still match; otherwise revalidate or omit the flag |
| Deploy runs async — capture and report the identifier | The promote deploy does not complete synchronously; completion is tracked separately |
| Do NOT busy-wait for deploy completion in this skill | Polling is a separate concern; blocking here wastes turns and risks timeouts |
| Combine only when work items share metadata/dependencies | Combining is for conflict-prone or dependent items, not a default for every multi-item promotion |
| Prepare is only for one-off movement between existing stages | A development WI entering its first linked stage has no `PipelineStageId`; unconditional prepare is invalid |
| Never use interactive prompts | Skills run headless; all inputs must be CLI flags |
| Pass IDs as CLI flags, never interpolate into shell strings | Prevents prompt/command injection via crafted identifiers |

---

## Gotchas

| Issue | Resolution |
|-------|------------|
| **Validation fails** | STOP — do not prepare/combine/promote. Report the non-zero status / error message; if metadata overlap, resolve the conflict before retrying |
| **Plugin missing, below 2.0.0, or missing required capabilities** | STOP in Phase 0. Install or upgrade `@salesforce/plugin-devops-center`, then rerun preflight. Do not improvise unsupported commands |
| **Development WI has no PipelineStageId** | If the target is the first linked stage, skip prepare. If it is not, stop and verify topology and WI state |
| **No confirmed org target** | Confirm the intended target with the user, then use `sf org display --target-org <confirmed-alias> --json`; login is a separate account-access action. |
| **Passing a work item name instead of an ID** | Promotion commands need record IDs; resolve names from the structured result of `sf devops work-item list --project-id <id> --target-org <confirmed-alias> --json`, and refuse ambiguous matches |
| **Both `--work-item-id` and `--stage-id` supplied** | They are mutually exclusive; pick specific work items OR a source stage, not both |
| **Missing `--target-stage-id`** | Required for validate, combine, promote, complete, and any routed prepare; obtain the target stage ID from the pipeline configuration |
| **Combined promotion promotes the wrong item** | After `work-item combine`, promote the **parent** work item ID — children merge into the parent's branch |
| **Treating the deploy as synchronous** | The promote deploy is async; capture the identifier and confirm completion before running `promotion complete` |
| **Production deploy fails on Apex coverage** | Set `--test-level RunLocalTests` (or `RunSpecifiedTests --tests <names>`) for production-stage promotions with Apex |
| **Deploy fails with conflict or PR is not mergeable** | Read `references/conflict-recovery.md`, merge the fetched target stage into the WI worktree, preserve the stage baseline, push the same WI branch, and revalidate |

---

## Output Expectations

Deliverables vary by operation:

- **Validate**: `.result.success` plus, when work items share metadata, `.result.combineDetails` / `.result.suggestions`. A non-zero exit (with `.result.errorType`/`.result.errorDetails`) means the work item cannot be promoted to the target stage
- **Prepare / combine**: confirmation that the work item(s) are staged (combine returns the parent/child grouping)
- **Promote**: an async deploy identifier and confirmation that the promotion deploy was initiated
- **Promotion complete**: confirmation the work items advanced in the target stage

Outputs are derived from `sf devops work-item`, `sf devops promote`, and `sf devops promotion complete` CLI commands. Async deploy completion is NOT produced by the promote call — poll the returned identifier separately before completing.

---

## Cross-Skill Integration

| When | Action |
|------|--------|
| Work item must be created or moved to a promotable status first | Delegate to `dx-devops-work-item-manage` |
| Validation reports a stale branch or VCS conflict | Follow `references/conflict-recovery.md`, then revalidate before retrying |
| The promote deploy identifier must be polled to confirm completion | Poll the returned identifier separately, then run `sf devops promotion complete` |

---

## Reference File Index

| File | When to read |
|------|-------------|
| `references/cli-commands.md` | When you need detailed CLI flag documentation, JSON output schemas, or error-handling patterns for validate/prepare/combine/promote/complete |
| `references/conflict-recovery.md` | When a WI branch is stale, its PR conflicts, or promotion fails after the target stage advances |
| `examples/promotion-workflows.md` | When the user's request matches a common pattern (single work item promotion, combined promotion, whole-stage promotion, validate-first gate) |
