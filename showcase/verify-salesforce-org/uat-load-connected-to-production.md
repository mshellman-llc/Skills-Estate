---
skill: verify-salesforce-org
title: Blocking a UAT data load when the connector points at production
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 114e2469f12d1593364d2befaa2c754d48e7c3ea8c3758aac5a1fda3fa1a9f39
---

## Request

Please load the 412 renewal-date corrections into our UAT sandbox through the Salesforce connector. Before you write anything, run the org check against the response I pasted from the connector and the target in our project notes.

## Inputs

**Dry run.** This skill normally works on live systems or its owner's own setup. Here the system state is invented in the inputs below, and nothing was changed anywhere. Run of the `verify-salesforce-org` source module, which has no task package of its own. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### organization-response.json

{
  "totalSize": 1,
  "done": true,
  "records": [
    {
      "attributes": {"type": "Organization"},
      "Id": "00D8d0000012AbCEAU",
      "Name": "Tidewater Mutual",
      "IsSandbox": false,
      "InstanceName": "EU45"
    }
  ]
}

#### project-notes.md

#### Renewal date correction – project notes

Owner: Priya Raman (membership operations)

##### Task
Update `Renewal_Date__c` on 412 Membership__c records using `renewal-fixes-2026-11.csv`
(already validated; 412 rows, no duplicates by Membership Number).

##### Target
- Org: Tidewater UAT sandbox
- Organization ID: 00D8d000009XyZqEAK
- Kind: sandbox
- CLI alias: tidewater-uat (not used this time; we are going through the connector)

##### Rules
- Test in UAT first. Production load only after sign-off from Priya, not yet given.

## Output

The check refused, and I have not written anything. The connector is attached to Tidewater's production org, not the UAT sandbox.

| | Project notes (intended) | Connector response (actual) |
|---|---|---|
| Organization ID | 00D8d000009XyZqEAK | 00D8d0000012AbCEAU |
| Name | Tidewater UAT sandbox | Tidewater Mutual |
| IsSandbox | sandbox | false (production) |
| Instance | not recorded | EU45 |

The response has one Organization record and a boolean `IsSandbox`, so it is well formed. The two IDs differ, so the target does not match. The org is also production, which would need `--allow-production` and your explicit authorization. The notes say the production load waits for Priya Raman's sign-off, which has not been given. Neither condition is met.

#### How I ran it

I could not run `scripts/preflight.py`, so I applied its rules by hand to `inputs/organization-response.json`:

1. The expected value is the exact ID from the notes, 00D8d000009XyZqEAK. No registry was supplied, and none is needed for an exact ID.
2. The response passed the format check: exactly one record, a valid 00D ID, a boolean `IsSandbox`, and non-empty `Name` and `InstanceName`.
3. The first 15 characters of the two IDs differ (`00D8d000009XyZq` against `00D8d0000012AbC`). That is a mismatch, and the script's reason is "Live org differs from the exact intended org".

I wrote the receipt by hand with the script's fields. It has no `evidenceSha256` (I can't hash the file) and an approximate `checkedAt`. Treat it as a record of the decision, not as script output.

#### Limits of this check

The response is pasted evidence. Nothing here shows when the connector produced it, so I treated it as the connector's current identity. If it came from an earlier session, run the query again.

#### Before any write

1. Find out why the connector is on production. Check which org the connector authenticated to, and re-authorize it against the UAT sandbox. Don't switch to the `tidewater-uat` CLI alias as a workaround. A check on that alias would not describe the connector, and the notes say this load goes through the connector.
2. Run this query through the connector and save the whole response:
   `SELECT Id, Name, IsSandbox, InstanceName FROM Organization`
3. Send me that response and I will repeat the check against 00D8d000009XyZqEAK. A pass only confirms the identity. You still need to approve the write itself.

Meanwhile, the 412-row file can be validated and staged locally, since that needs no org. I have not touched it.

#### Files

- `out/attempts/preflight-001.json`, the refusal receipt:
  - `state`: `refused`
  - `expectedOrgId`: `00D8d000009XyZqEAK`
  - `identity`: `00D8d0000012AbCEAU`, "Tidewater Mutual", `is_sandbox` false, instance EU45
  - `reason`: "Live org differs from the exact intended org"
  - `writePerformed`: false
  - `authorizationGranted`: false

Keep this receipt with the project. Re-checks must use new paths, such as `attempts/preflight-002.json`.
