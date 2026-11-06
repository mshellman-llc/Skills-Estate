---
skill: operate-salesforce-pipeline
title: Recovering a frozen preprod after a deploy fails on a missing field
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 8a638326984a888fd4e4f1ede7405a1e9899ece7f7ffc051022438c23252ad4d
---

## Request

Preprod has been frozen since this morning and my team lead says to just hit retry so the queue moves. I've pasted the status and the recent history; can you tell me what to do and give me the exact commands?

## Inputs

**Dry run.** This skill normally works on live systems or its owner's own setup. Here the system state is invented in the inputs below, and nothing was changed anywhere. Run of the built `operate-salesforce-pipeline` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### history.md

#### preprod activity, 2026-11-03 to 2026-11-04 (from /api/history, newest first)

- 2026-11-04 08:12  deploy FAILED  sha b93d2f6  PR #418 "EXAMPLE-88 Escalate P1 cases by tier"  -> environment FROZEN, tag stays 7e41c09
- 2026-11-04 07:58  PR #418 merged (merge commit b93d2f6) into preprod
- 2026-11-04 07:41  validation PASSED  PR #418 at sha 4fd8e21 (test level RunLocalTests)
- 2026-11-03 17:05  validation PASSED  PR #418 at sha 4fd8e21 -- note: PR head was then rebased/merged from sandbox-a, field metadata not in diff
- 2026-11-03 15:30  deploy SETTLED  sha 7e41c09  PR #409 "GH-377 Quote footer text"

#### PR #418 diff summary
- flows/Case_Escalation.flow-meta.xml (modified; reads Case.Escalation_Tier__c)
- classes/EscalationRouter.cls and EscalationRouterTest.cls (modified)

#### Board notes
- EXAMPLE-91 "Add Escalation_Tier__c to Case" is on the Dev Sandboxes column, carried by sandbox-a. Its PR merged on sandbox-a only; never released to preprod.
- PR #421 (GH-380, footer typo) is queued for validation behind the freeze. It touches one email template.

#### status.json

{
  "paused": false,
  "repo": "northfield-labs/crm-metadata",
  "environments": {
    "preprod": {
      "state": "FROZEN",
      "deployedTag": "7e41c09",
      "inFlightJobId": null,
      "deployUrl": "https://northfield--preprod.example.com/lightning/setup/DeployStatus/page?address=0Af000000000123",
      "freezeReason": "Deploy failed: flows/Case_Escalation.flow-meta.xml: field Case.Escalation_Tier__c does not exist (Component Failures: 1, Tests run: 0)",
      "currentItem": { "type": "deploy", "sha": "b93d2f6", "pr": 418 },
      "queueLength": 1,
      "queue": [ { "type": "validation", "pr": 421, "sha": "5c0aa17" } ]
    },
    "main": {
      "state": "SETTLED",
      "deployedTag": "2d90e5b",
      "inFlightJobId": null,
      "deployUrl": null,
      "freezeReason": null,
      "currentItem": null,
      "queueLength": 0,
      "queue": []
    }
  }
}

## Output

Don't retry yet. A retry would fail again, and it would also cost another test run.

#### What the status says

`preprod` is `FROZEN`, and `main` is `SETTLED` and unaffected. The `freezeReason` is a Salesforce deploy error, not a transient one:

> Deploy failed: flows/Case_Escalation.flow-meta.xml: field Case.Escalation_Tier__c does not exist

The failed item is PR #418 (EXAMPLE-88, merge commit `b93d2f6`). Its flow reads `Case.Escalation_Tier__c`, but the field belongs to EXAMPLE-91, which is only on `sandbox-a` and was never released to preprod. The PR's validation passed because the field was missing from the diff and from the org it checked. That is a gap in how the dependency was released, and it is not an engine fault.

The tag `deployed/preprod` is still `7e41c09`, so git still describes the org correctly. Nothing was half-deployed. Retry re-enqueues a deploy of the same metadata at `b93d2f6`, and the missing field would fail it again.

PR #421 (GH-380, an email template typo) is waiting in the queue behind the freeze. It has no dependency on this problem.

#### Recommended path: fix forward by releasing EXAMPLE-91, then retry

Retry becomes the right command once the field is in preprod's branch, because it deploys branch HEAD, which will then include both changes.

1. Set up auth if you haven't. Open `$ENGINE_URL/auth/login?redirect=cli`, sign in, save the token to a mode-600 file, and export `SFDE_TOKEN_FILE` with its absolute path. A bare curl returns 401 or 503.

   ```bash
   export ENGINE_URL=$(grep '^engine_url:' pipeline.yml | awk '{print $2}')
   scripts/engine.sh status        # re-read freezeReason; confirm still FROZEN
   ```

2. Release the field ticket from its sandbox into preprod:

   ```bash
   scripts/engine.sh release --to preprod --from sandbox-a EXAMPLE-91
   ```

   `--from` is required. Read the response before going further. The release cherry-picks EXAMPLE-91's merge, so it only works because that PR merged on `sandbox-a`. If the engine refuses with "unattributed commits", the merge carries other work too. Read what it names and either add those tickets or use the fallback below.

3. Wait for the release PR's validation to pass, then merge it with a **merge commit**, not a squash. Validation computes the delta from `deployed/preprod` (`7e41c09`), so it covers the flow, the Apex and the new field together.

4. Once the release has merged, retry:

   ```bash
   scripts/engine.sh retry preprod
   ```

   This lifts the freeze and deploys current HEAD. When it finishes, the status should show `SETTLED` with the tag advanced, and PR #421 then validates.

#### Fallback: roll back EXAMPLE-88

Use this if the EXAMPLE-91 release is refused, or if the field turns out to need work in `sandbox-a` first.

```bash
scripts/engine.sh rollback --env preprod --sha b93d2f6
```

I used `--sha` because the failed deploy never completed, and a ticket-based rollback looks up "the deploy that carried it". That lookup may not find one. The default `--mode pr` opens a revert PR so the inverse deployment is validated first; keep it. `--mode direct` is for emergencies only. To re-land afterwards, don't reuse the original branch: create a new branch, run `git revert <revert-sha>`, add the fix, and open a new PR, with EXAMPLE-91 released first.

#### Things I could not confirm from what you pasted

- Whether the engine validates the release PR while preprod is `FROZEN`. PR #421 is sitting in the queue, which suggests validations may wait. The skill documents retry and rollback as the freeze exits, and does not say whether a validation can run during a freeze. If the release PR stays queued, `rollback` is the way to unfreeze first.
- Whether EXAMPLE-91 includes field-level security or a permission set. Check this before step 3. The Apex test run happens on the same deploy, and a missing permission will fail tests, not the field itself.
- I haven't run any of these commands. Everything above is from the status and history you pasted.

#### What not to do

- Don't deploy the field to the preprod org yourself with `sf project deploy`. The engine can't detect a manual deploy, and `deployed/preprod` would then misstate the org. The recovery for that is Pause, then reconcile by hand, then Resume.
- Don't move the `deployed/preprod` tag.
- Don't add `--use-most-recent` to any `sf` command.

#### For your team lead

The quick answer: retry only helps when the failure was transient (auth, network, git). This one is a missing dependency in the metadata, so the order is to land the field first and retry second. If the team wants to confirm quickly, EXAMPLE-91 is the card sitting in the Dev Sandboxes column of the board.
