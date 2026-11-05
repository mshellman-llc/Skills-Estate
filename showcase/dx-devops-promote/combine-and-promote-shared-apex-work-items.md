---
skill: dx-devops-promote
title: Combine and promote two work items that share an Apex class
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 9a105d47b6a0d13b91d1ab2327554422afb9c638e33fdaa0a84eb4730e1c2d46
---

## Request

Please promote WI-000214 and WI-000219 from the Dev stage to QA in our Lakeside Pipeline project, using the org alias lakeside-release. I've pasted the org status, the plugin inspect output and the validate result from this morning.

## Inputs

**Dry run.** This skill normally works on live systems or its owner's own setup. Here the system state is invented in the inputs below, and nothing was changed anywhere. Run of the built `sf-devops-center` task package in its "promote work items or stages" mode. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### plugin-manifest.json

[{
  "name": "@salesforce/plugin-devops-center",
  "version": "2.3.1",
  "commandIDs": [
    "devops:project:list",
    "devops:work-item:list",
    "devops:work-item:prepare",
    "devops:work-item:combine",
    "devops:promotion:validate",
    "devops:promote",
    "devops:promotion:complete"
  ],
  "commands": [
    {"id": "devops:promote", "flags": {"work-item-id": {}, "stage-id": {}, "target-stage-id": {}, "deploy-all": {}, "test-level": {}, "skip-validation": {}}}
  ]
}]

#### status.txt

Org: lakeside-release (authorized by requester for this promotion)
sf org display --target-org lakeside-release --json -> status 0, connectedStatus Connected, username release.bot@example.com

Project: Lakeside Pipeline
Pipeline stages in order:
  Dev  1QVxx0000000010AAA  (first linked stage)
  QA   1QVxx0000000020AAA
  UAT  1QVxx0000000030AAA

Work items (sf devops work-item list, trimmed)
  WI-000214  id 1fkxx0000000214AAA  "Add late-fee cap to LoanQuoteService"   status Ready to Promote  PipelineStageId 1QVxx0000000010AAA  PR #88 open
  WI-000219  id 1fkxx0000000219AAA  "Round quote totals to 2 decimals"       status Ready to Promote  PipelineStageId 1QVxx0000000010AAA  PR #91 open
  WI-000221  id 1fkxx0000000221AAA  "Update footer label"                     status In Progress       PipelineStageId (none)

Saved validation file: validation.json, written 2026-11-04 09:12 by the requester, run for
WI-000214 + WI-000219, target stage QA, org lakeside-release. No commits to the Dev or QA branches
since 09:12, according to the requester.

#### validation.json

{
  "status": 0,
  "result": {
    "success": true,
    "errorType": null,
    "errorDetails": null,
    "combineDetails": {
      "parentWorkitemId": "1fkxx0000000214AAA",
      "childWorkitemsId": ["1fkxx0000000219AAA"],
      "sharedComponentsList": {
        "1fkxx0000000214AAA": ["LoanQuoteService", "LoanQuoteServiceTest"],
        "1fkxx0000000219AAA": ["LoanQuoteService"]
      }
    },
    "suggestions": [
      "The selected work items share one or more components. Choose one of these approaches:",
      "Option 1 - Combine the work items and promote them as a single unit.",
      "Option 2 - Promote the work items as they are, without combining."
    ]
  },
  "warnings": []
}

## Output

WI-000214 and WI-000219 should be combined and promoted to QA as one unit, with WI-000214 as the parent. I have prepared the plan and the local checks. I have not run any command against `lakeside-release`, so nothing has been promoted yet.

#### Why combine

Your validate result succeeded (`status 0`, `success: true`) and its `combineDetails` names both items as sharing `LoanQuoteService`. WI-000214 also carries `LoanQuoteServiceTest`. The workflow treats that field as the deciding signal, so promoting them separately is not the recommended path. I ran the combine-plan step by hand following the script's rules:

- Parent: `1fkxx0000000214AAA` (WI-000214)
- Child: `1fkxx0000000219AAA` (WI-000219)
- Both are valid 18-character IDs, distinct, with a non-empty child list.
- Arguments: `--parent-work-item-id 1fkxx0000000214AAA --child-work-item-id 1fkxx0000000219AAA`

I could not compute the validation file hash the script normally returns.

#### Checks completed

- **Plugin:** version 2.3.1 is above the 2.0.0 minimum. The manifest lists validate, prepare, combine, promote and complete, and `promote` exposes `skip-validation`. I checked this by reading the manifest, following the preflight script's rules. It describes the file you supplied, not the plugin installed on the machine that will run the commands.
- **Org:** your status shows `lakeside-release` connected. Every command below passes it explicitly.
- **Stage route:** both items already sit in Dev (`1QVxx0000000010AAA`) and the target is QA (`1QVxx0000000020AAA`). The route is `prepare` for each, not `skip`, because they are leaving an existing pipeline stage.
- **Left out:** WI-000221 is In Progress with no pipeline stage and was not part of your request.

#### Commands to run, in order

1. **Revalidate both items.** Your validate output is from 09:12 and I did not produce it in this session. Running it again also makes `--skip-validation` safe to consider later.
   ```
   sf devops promotion validate --work-item-id 1fkxx0000000214AAA --work-item-id 1fkxx0000000219AAA --target-stage-id 1QVxx0000000020AAA --target-org lakeside-release --json
   ```
   Stop on any failure. The combine decision should match the saved result; if `combineDetails` differs, rerun the combine-plan step on the new output.
2. **Prepare each item.**
   ```
   sf devops work-item prepare --work-item-id 1fkxx0000000214AAA --target-stage-id 1QVxx0000000020AAA --target-org lakeside-release --json
   sf devops work-item prepare --work-item-id 1fkxx0000000219AAA --target-stage-id 1QVxx0000000020AAA --target-org lakeside-release --json
   ```
3. **Combine.**
   ```
   sf devops work-item combine --parent-work-item-id 1fkxx0000000214AAA --child-work-item-id 1fkxx0000000219AAA --target-stage-id 1QVxx0000000020AAA --target-org lakeside-release --json
   ```
4. **Promote the parent only.** Children merge into the parent's branch, so WI-000219's ID is not passed.
   ```
   sf devops promote --work-item-id 1fkxx0000000214AAA --target-stage-id 1QVxx0000000020AAA --target-org lakeside-release --json
   ```
   I left out `--skip-validation`. It is allowed only when the exact work-item set passed validation in the same session with no Git or DevOps Center changes since. Your 09:12 result does not meet that, and if step 1 passes you can add the flag, because step 1 would then be that validation. QA is not a production stage, so no `--test-level` is needed.
5. **Capture `.result.promotionId`** from the promote response. The deploy is asynchronous, so poll that ID separately and do not run the next command until it reports success.
6. **Complete the promotion.**
   ```
   sf devops promotion complete --target-stage-id 1QVxx0000000020AAA --target-org lakeside-release --json
   ```

#### Assumptions and gaps

- I treated "no commits to Dev or QA since 09:12" as your statement, not something I confirmed.
- The workflow describes `prepare` as taking one work item. I prepare both before combining; if the combine command rejects an already-prepared child, report the error before retrying.
- If the deploy or the PRs (#88, #91) report a conflict because QA moved, follow the stale-branch recovery steps: merge the fetched QA branch into the WI branch in a linked worktree, push the same branch, keep the existing PR, and revalidate.
- Not verified: live org access, the installed plugin, current PR mergeability, and deployment results.

#### File

- `out/promotion-plan.md`: the checks table above and the ordered command list, with the org and stage IDs filled in.

### File: promotion-plan.md

#### Promotion plan: WI-000214 + WI-000219, Dev to QA

Org: lakeside-release. Target stage: QA (1QVxx0000000020AAA). Nothing below has been run on the org.

##### Checks done locally

| Check | Result |
| --- | --- |
| Plugin `@salesforce/plugin-devops-center` | 2.3.1, meets >=2.0.0 |
| Required commands in manifest | validate, promote, work-item:prepare, promotion:complete, work-item:combine all present |
| `skip-validation` flag on promote | present |
| Saved validation | status 0, `success: true`, `combineDetails` set |
| Combine decision | combine = true; parent 1fkxx0000000214AAA, child 1fkxx0000000219AAA (both 18-character IDs, distinct) |
| Stage route for each work item | `prepare` (current stage Dev 1QVxx0000000010AAA, target QA 1QVxx0000000020AAA, different) |

##### Commands, in order

1. Re-validate both items (the saved result is from 09:12 and was not produced in this session):
   `sf devops promotion validate --work-item-id 1fkxx0000000214AAA --work-item-id 1fkxx0000000219AAA --target-stage-id 1QVxx0000000020AAA --target-org lakeside-release --json`
2. Prepare each item:
   `sf devops work-item prepare --work-item-id 1fkxx0000000214AAA --target-stage-id 1QVxx0000000020AAA --target-org lakeside-release --json`
   `sf devops work-item prepare --work-item-id 1fkxx0000000219AAA --target-stage-id 1QVxx0000000020AAA --target-org lakeside-release --json`
3. Combine:
   `sf devops work-item combine --parent-work-item-id 1fkxx0000000214AAA --child-work-item-id 1fkxx0000000219AAA --target-stage-id 1QVxx0000000020AAA --target-org lakeside-release --json`
4. Promote the parent only, with built-in validation left on (no `--skip-validation`):
   `sf devops promote --work-item-id 1fkxx0000000214AAA --target-stage-id 1QVxx0000000020AAA --target-org lakeside-release --json`
5. Record `.result.promotionId`, poll it separately, then:
   `sf devops promotion complete --target-stage-id 1QVxx0000000020AAA --target-org lakeside-release --json`

Stop if any step returns a non-zero status.
