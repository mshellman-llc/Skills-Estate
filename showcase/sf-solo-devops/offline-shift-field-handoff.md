---
skill: sf-solo-devops
title: Prepare a field and permission-set change locally before an org exists
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 7aa22071e02f31275dcdff3bf20170739971f90d31d0563242ef88a520154d73
---

## Request

I've finished the shift pickup-window work for issue #17 in a worktree, but I don't have a sandbox ID to give you yet. Please get it as ready as it can be without an org: generate the permission set, check what the local results say, and give me a handoff I can use when the sandbox is sorted. Details are in the inputs.

## Inputs

**Dry run.** This skill normally works on live systems or its owner's own setup. Here the system state is invented in the inputs below, and nothing was changed anywhere. Run of the built `sf-change-delivery` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so. Other files it produced, not shown here: `new-preview.xml`.

#### issue-17.md

#### Issue #17: Pickup window and remaining slots on volunteer shifts

Coordinators need to see when a food pickup shift starts and how many places are left.

Acceptance criteria
1. Volunteer_Shift__c has a picklist Pickup_Window__c (Early, Midday, Evening).
2. Slots_Remaining__c is a formula (Capacity__c minus booked volunteers) shown on the shift page.
3. Shift_Code__c is an auto-number (SHIFT-{0000}).
4. Coordinator__c looks up the User who runs the shift.
5. ShiftCapacityService.remainingSlots() returns the same number as the formula; ShiftCapacityServiceTest covers full, partial and empty shifts.
6. Volunteer admins can see and edit the new fields. Nobody gets Delete on shifts through this permission set.

Target: Harbourlight sandbox (ID not yet supplied by owner).

#### project-state.md

#### Project state (export from the worktree)

Worktree: ../harbourlight-17, branch feat/17-pickup-window, base main at 4c1e9a0.
Commit on branch: 7be3d52 "feat: pickup window and slots remaining (refs #17)".
Working tree clean. Package directory: force-app (sfdx-project.json).

##### Files changed in 7be3d52 (under force-app/main/default)
objects/Volunteer_Shift__c/fields/Pickup_Window__c.field-meta.xml  (Picklist)
objects/Volunteer_Shift__c/fields/Slots_Remaining__c.field-meta.xml  (Formula, Number)
objects/Volunteer_Shift__c/fields/Shift_Code__c.field-meta.xml  (AutoNumber)
objects/Volunteer_Shift__c/fields/Coordinator__c.field-meta.xml  (Lookup to User)
classes/ShiftCapacityService.cls
classes/ShiftCapacityServiceTest.cls

##### Already in the tree
Volunteer_Shift__c fields: Shift_Date__c (Date), Capacity__c (Number, required=true)
Objects: Volunteer_Shift__c, Volunteer__c
Classes also present: VolunteerImporter, VolunteerImporterTest
Committed permission set: Harbourlight_Admin (grants Volunteer_Shift__c, Volunteer__c; fields Shift_Date__c; no Pickup/Slots/Code/Coordinator)

##### config/permset-gen.json
{"api_name": "Harbourlight_Admin", "label": "Harbourlight Admin",
 "no_delete": ["Volunteer_Shift__c"], "read_only": [],
 "exclude_objects": [], "exclude_fields": [], "exclude_apex_classes": ["VolunteerImporter*"]}

##### Local check output
npm run lint  -> no LWC files changed; 0 problems
npm test      -> "No tests found" (jest has no LWC specs in this project)
npm run pmd   -> sh: pmd: command not found
Apex tests: not run (no org)

##### Org situation
`sf org list` shows one authenticated alias, "hb-scratch", marked default. Owner has not said whether it is the sandbox, and gave no org ID.

## Output

Issue #17 is **prepared locally**. Nothing has been validated or deployed, and nothing in this answer was run against Salesforce.

#### What is ready
- Commit 7be3d52 on feat/17-pickup-window holds four new Volunteer_Shift__c fields and the ShiftCapacityService class with its test class. You made it in a worktree off main (4c1e9a0), so the worktree rule is met.
- A permission-set preview, `out/new-preview.xml`.
- A deployment handoff, `out/deployment-handoff.md`.

#### Gaps you should know about
1. **PMD did not run.** `npm run pmd` reported "command not found". Apex static analysis is skipped, not passed. Install PMD and rerun it before you merge.
2. **Jest found no tests.** The project has no LWC specs and this change touches no LWC, so there was nothing to run. It tells us nothing about the Apex.
3. **Apex tests have not run.** They need an org.
4. **I could not run `gen-permset.py`.** I worked out the preview by hand from the script's documented rules and your `config/permset-gen.json`. Run `python3 scripts/gen-permset.py --out <new path outside the project>`, diff it against my file, and use the script's output if they differ. Then `--write` in the worktree and commit with `refs #17`. The permission-set file is not in 7be3d52, so the handoff needs the new commit SHA.
5. **The org is not confirmed.** `sf org list` shows one alias, hb-scratch, as the default. I did not query or use it. An alias does not tell us which org it points to, and you have not said it is the sandbox. Send the sandbox's Organization ID and I will check it with org-preflight, using one explicit `--target-org` from then on.

#### Permission-set preview: what it grants
| Item | Grant | Reason |
|---|---|---|
| Volunteer_Shift__c.Pickup_Window__c | read, edit | Editable picklist |
| Volunteer_Shift__c.Coordinator__c | read, edit | Editable lookup |
| Volunteer_Shift__c.Slots_Remaining__c | read only | Formula fields are read-only |
| Volunteer_Shift__c.Shift_Code__c | read only | Auto-number fields are read-only |
| Volunteer_Shift__c.Shift_Date__c | read, edit | Existing field, unchanged |
| Volunteer_Shift__c.Capacity__c | not listed | The generator omits universally required fields by design, so this permission set carries no explicit grant for it |
| Volunteer_Shift__c object | create, read, edit; no delete | `no_delete` in your config, which supports criterion 6 |
| Volunteer__c object | full CRUD | Not covered by `no_delete` |
| ShiftCapacityService and its test | enabled | Derived from the classes folder |
| VolunteerImporter, VolunteerImporterTest | not listed | Excluded by `VolunteerImporter*` in config |

`no_delete` only withholds Delete from this permission set. If another permission set or profile grants Delete on shifts, criterion 6 still fails in practice, so the handoff asks you to check that with a real user in the sandbox.

Whether the generator includes the test class in `classAccesses` is my reading of "derives Apex classes"; the script's diff will settle it.

#### Proposed validation once a target exists
Dry run of the seven listed files only (never the whole `force-app`) with `--test-level RunSpecifiedTests --tests ShiftCapacityServiceTest`. Because the permission set must be committed first, validate the final commit, since a dry run counts for one commit only. If you want wider coverage, add VolunteerImporterTest; nothing in this change touches the importer, so I treated that as optional. Then squash-merge to main, deploy from a clean, pushed main, run the six acceptance checks, and close #17 with `fixes #17`. Remove the worktree when the ticket closes.

#### Files
- `out/new-preview.xml` — hand-derived PermissionSet XML for Harbourlight_Admin: five field grants, two object grants (Volunteer_Shift__c with `allowDelete` false) and two class accesses.
- `out/deployment-handoff.md` — commit and file list, the three open items, the dry-run command with a CONFIRMED_ORG placeholder, the org requirement, and the six acceptance checks.

### File: deployment-handoff.md

#### Deployment handoff: issue #17, pickup window and remaining slots

Status: **prepared locally**. No Salesforce validation, deployment or acceptance test has happened.

##### Source
- Branch feat/17-pickup-window in worktree ../harbourlight-17, base main at 4c1e9a0.
- Commit 7be3d52 (refs #17). Working tree was clean when exported.
- Files to deploy (force-app/main/default):
  - objects/Volunteer_Shift__c/fields/Pickup_Window__c.field-meta.xml
  - objects/Volunteer_Shift__c/fields/Slots_Remaining__c.field-meta.xml
  - objects/Volunteer_Shift__c/fields/Shift_Code__c.field-meta.xml
  - objects/Volunteer_Shift__c/fields/Coordinator__c.field-meta.xml
  - classes/ShiftCapacityService.cls
  - classes/ShiftCapacityServiceTest.cls
  - permissionsets/Harbourlight_Admin.permissionset-meta.xml (regenerated, not yet committed)

##### Open before the commit is final
1. Run `python3 scripts/gen-permset.py --out <new path outside the project>` and diff it against out/new-preview.xml (hand-derived). Then, in the worktree, `--write`, commit with `refs #17`, and use that new commit SHA below.
2. Install PMD and run `npm run pmd`. It failed with "command not found", so Apex static analysis is skipped, not passed.
3. Review ShiftCapacityService against the formula behind acceptance criterion 5.

##### Proposed validation (needs a confirmed target)
Tests: ShiftCapacityServiceTest. Add VolunteerImporterTest if the project's release policy wants wider coverage; the permission-set and field changes do not touch the importer, so that is a policy choice.

```bash
sf project deploy start --dry-run --target-org CONFIRMED_ORG --json \
  --source-dir force-app/main/default/objects/Volunteer_Shift__c/fields/Pickup_Window__c.field-meta.xml \
  --source-dir force-app/main/default/objects/Volunteer_Shift__c/fields/Slots_Remaining__c.field-meta.xml \
  --source-dir force-app/main/default/objects/Volunteer_Shift__c/fields/Shift_Code__c.field-meta.xml \
  --source-dir force-app/main/default/objects/Volunteer_Shift__c/fields/Coordinator__c.field-meta.xml \
  --source-dir force-app/main/default/classes/ShiftCapacityService.cls \
  --source-dir force-app/main/default/classes/ShiftCapacityServiceTest.cls \
  --source-dir force-app/main/default/permissionsets/Harbourlight_Admin.permissionset-meta.xml \
  --test-level RunSpecifiedTests --tests ShiftCapacityServiceTest
```

##### Outstanding target requirement
The owner must give the Harbourlight sandbox's Organization ID. Then run org-preflight (`preflight.py --target-org <alias> --expect <ID> --receipt <new path>`) and use that same alias on every later command. The sf CLI currently lists one alias, hb-scratch, as default. It has not been confirmed as the sandbox and was not queried.

##### Acceptance checks after deployment
1. Pickup_Window__c shows Early, Midday, Evening on a shift record.
2. Slots_Remaining__c shows on the shift page and equals capacity minus booked volunteers.
3. A new shift gets a Shift_Code__c in SHIFT-0001 form.
4. Coordinator__c accepts a User.
5. ShiftCapacityServiceTest passes in the org (full, partial, empty shifts).
6. A user with Harbourlight_Admin can edit Pickup_Window__c and Coordinator__c, cannot edit the formula or auto-number, and cannot delete a shift through this permission set (check no other permission set or profile grants Delete).
