---
skill: dx-devops-work-item-manage
title: Mark a finished work item Ready to Promote and open its pull request
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: d06e708aef3b2bafb70137e5e457b5f0e0786672a1191c0fd10e50b4c4def260
---

## Request

In our Harborline org (alias harborline-uat, that's the one I'm authorizing), the work item "Fix invoice rounding on partial refunds" is finished and pushed. Mark it Ready to Promote and open the pull request for it.

## Inputs

**Dry run.** This skill normally works on live systems or its owner's own setup. Here the system state is invented in the inputs below, and nothing was changed anywhere. Run of the built `sf-devops-center` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### system-state.md

#### Captured state (read-only export)

##### sf plugins inspect @salesforce/plugin-devops-center --json (trimmed)

```json
{
  "name": "@salesforce/plugin-devops-center",
  "version": "2.3.1",
  "commands": [
    "devops:project:list",
    "devops:work-item:list",
    "devops:work-item:create",
    "devops:work-item:update",
    "devops:review:create",
    "devops:pipeline:promote"
  ]
}
```

##### sf org display --target-org harborline-uat --json (trimmed)

```json
{ "status": 0, "result": { "alias": "harborline-uat", "username": "release.bot@example.com", "connectedStatus": "Connected", "apiVersion": "62.0" } }
```

##### sf devops project list --target-org harborline-uat --json (trimmed)

```json
{ "status": 0, "result": [ { "id": "1Qg000000000701", "name": "Harborline Billing" } ] }
```

##### sf devops work-item list --project-id 1Qg000000000701 --target-org harborline-uat --json (trimmed)

```json
{
  "status": 0,
  "result": [
    { "id": "0Wx000000000311AAA", "name": "WI-000311", "subject": "Fix invoice rounding on partial refunds",
      "branch": "feature/wi-000311-refund-rounding", "environment": "billing-dev-4", "status": "In Progress" },
    { "id": "0Wx000000000312AAA", "name": "WI-000312", "subject": "Fix invoice rounding on partial refunds (docs)",
      "branch": "feature/wi-000312-refund-docs", "environment": "billing-dev-5", "status": "New" },
    { "id": "0Wx000000000298AAA", "name": "WI-000298", "subject": "Add tax region picklist",
      "branch": "feature/wi-000298-tax-region", "environment": "billing-dev-2", "status": "Ready to Promote" }
  ]
}
```

##### git log origin/feature/wi-000311-refund-rounding --oneline -3

```text
a41c9e2 Round partial refund lines half-even before summing
7d03b18 Add RefundRoundingTest cases for 3-way splits
e5f6a10 Create branch for WI-000311
```

##### Notes from the requester's ticket

- Review needs to target the pipeline base branch (set by DevOps Center).
- VCS connection for Harborline Billing: configured last month, per the admin channel.

## Output

WI-000311 is ready to move to Ready to Promote and to get its pull request. I have not run any of it: this session has no connection to the org, so the commands below are the exact sequence to run against `harborline-uat`. The checks I could make against the exported state all passed.

#### What I checked

| Check | Result |
| --- | --- |
| Target org | `harborline-uat`, as you authorized. It is passed with `--target-org` on every command, and no machine default is used or changed. |
| Org connection | `sf org display` shows `Connected`, API 62.0. |
| Plugin | `@salesforce/plugin-devops-center` 2.3.1 (a 2.x release). The manifest lists `devops:work-item:list`, `devops:work-item:update` and `devops:review:create`, which are the three commands this task uses. |
| Project | "Harborline Billing", ID `1Qg000000000701`. It is the only project in the org. |
| Work item | "Fix invoice rounding on partial refunds" resolves to **WI-000311**, status In Progress, branch `feature/wi-000311-refund-rounding`, environment `billing-dev-4`. |
| Commits on the branch | `a41c9e2` and `7d03b18` sit after the branch-creation commit `e5f6a10`. The work is pushed, so DevOps Center's rule that the branch must have commits is met. |

**Name match.** The list also holds WI-000312, "Fix invoice rounding on partial refunds (docs)", status New. Its subject differs from yours, so an exact-subject lookup returns only WI-000311. I did not touch WI-000312. If you meant the docs item as well, say so and I will treat it separately.

#### Commands to run, in this order

The status change comes first, so the review is opened for a work item already marked ready.

1. Move the status:

```bash
sf devops work-item update \
  --work-item-name WI-000311 \
  --status "Ready to Promote" \
  --target-org harborline-uat --json
```

   Accept it only if the exit status is 0 and `.result.status` equals `Ready to Promote`. If the response has no status field, re-run `sf devops work-item list --project-id 1Qg000000000701 --target-org harborline-uat --json` and read the status for WI-000311 there.

2. Open the pull request:

```bash
sf devops review create \
  --work-item-name WI-000311 \
  --target-org harborline-uat --json
```

   Accept it only if the exit status is 0 and the response has a `pullRequestUrl` and a `pullRequestStatus` of `open`. DevOps Center creates the PR from `feature/wi-000311-refund-rounding` to the pipeline's base branch, using the VCS credentials stored in the org, so no local git login is needed.

#### What to expect and how failures are handled

- **Status step fails with `INVALID_STATUS`:** the string must be exactly `Ready to Promote`. Nothing else is changed.
- **PR step returns `VCS_NOT_CONFIGURED`:** the ticket says the connection was set up last month, but the export doesn't prove it. If this error appears, the status is already updated. An admin then needs to check Setup → DevOps Center → VCS Credentials, and the PR command can be re-run without touching the status.
- **PR step returns `PR_ALREADY_EXISTS`:** a PR is already open for WI-000311. Report it and do not create another.
- **Later conflicts:** if the base branch moves and the PR conflicts, the fix goes through the promotion conflict-recovery workflow, with the reconciled commit pushed to the same WI branch.

#### Report once the commands have run

- Status updated: In Progress → Ready to Promote (WI-000311).
- Pull request created: number, status `open`, and URL. I can't give these yet, because they come from the command output.

This request covers the status change and the PR only. I have not promoted anything to a later stage; that would be a separate request.

No files were generated for this task.
