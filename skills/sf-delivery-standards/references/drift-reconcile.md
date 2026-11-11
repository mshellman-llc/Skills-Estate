# Capturing a reported Setup change

A user changed Salesforce metadata in Setup and told the ticket-owning agent what changed. Start
with that report. `SourceMember` verifies and scopes the named components; it does not operate as
an inbox, a background poller, or proof of who made a change.

This workflow applies to source-tracked development orgs such as Developer, Developer Pro, and
scratch orgs. Building directly in a partial sandbox, full sandbox, or production is outside this
local loop. Pipeline-environment drift belongs to the configured delivery system: either
`sf-deploy-engine` or DevOps Center.

The normal result is a reviewed, ticket-attributed commit that follows the same dry run, merge,
and dev-sandbox deployment path as any authored source change.

## Human-reported fast path

Use this path when the user can name the Setup changes. The agent does the SourceMember and
revision work; the user does not operate a change inbox or reason about revision counters.

### 1. Turn the report into metadata identifiers

Map the user's words to metadata type and full name. Ask only when the identifier is ambiguous.
For example:

> For GH-142, I changed the help text on `Account.Customer_Tier__c` and updated the
> `Renewal_Review` flow in Setup.

The candidate set is:

```text
CustomField:Account.Customer_Tier__c
Flow:Renewal_Review
```

The ticket must already own a worktree. Create one through the normal ticket workflow if it does
not. Never perform this capture in the main or trunk working tree.

### 2. Verify only the reported candidates

Query the exact candidates through the Tooling API. The project-local target org is authoritative,
so do not add `--target-org`.

```bash
sf data query --use-tooling-api \
  --query "SELECT MemberType, MemberName, RevisionCounter, IsNameObsolete FROM SourceMember WHERE (MemberType = 'CustomField' AND MemberName = 'Account.Customer_Tier__c') OR (MemberType = 'Flow' AND MemberName = 'Renewal_Review') ORDER BY RevisionCounter DESC"
```

Keep rows that match the reported identifiers. A missing or ambiguous row is not permission to
retrieve broadly. Confirm the metadata name with the user or use the fallback discovery process
below.

`MemberType` and `MemberName` identify metadata. `RevisionCounter` orders source-tracking changes.
`IsNameObsolete` identifies a deletion. None of those fields proves author, intent, or time. The
user report supplies intent, and the git/deploy cross-check below protects shared orgs.

### 3. Subtract changes already explained by delivery activity

A shared development org receives teammates' deployments as well as Setup edits. `SourceMember`
can report both. Never turn a teammate's legitimate deploy into the current user's drift commit.

Refresh the configured trunk ref and inspect newer source activity for the candidate components:

```bash
TRUNK=$(git config estate.trunk)
git fetch origin "$TRUNK"
git log --name-status HEAD.."origin/$TRUNK" -- force-app/
git log --name-status --since="<when the user made the Setup change>" "origin/$TRUNK" -- force-app/
```

Also inspect the deployment receipts in the clone's common Git directory:

```bash
GIT_COMMON=$(git rev-parse --path-format=absolute --git-common-dir)
test ! -f "$GIT_COMMON/estate/deploy-log" || tail -50 "$GIT_COMMON/estate/deploy-log"
```

Exclude a candidate when a newer trunk commit or a recorded deployment already explains it. If the
user says their Setup edit happened after that deployment, keep the candidate only after comparing
the current org form with the newer source and confirming the remaining difference with them.

The set to capture is:

```text
reported components
intersect SourceMember confirmation
minus newer git and deploy activity that already explains the change
```

For the GH-142 example, suppose both rows appear in `SourceMember`, but a newer trunk deployment
contains `Renewal_Review`. Exclude the flow and tell the user why. Retrieve only the field. If the
user confirms that they edited the flow after that deployment, include it and review its retrieved
diff before committing.

### 4. Handle added, modified, and deleted metadata

For an added or modified component, retrieve only the confirmed component into `tmp-retrieve`
inside the ticket worktree:

```bash
sf project retrieve start \
  --metadata CustomField:Account.Customer_Tier__c \
  --output-dir tmp-retrieve
```

Use one `--metadata` argument per confirmed component when the CLI requires it. Never use a package,
directory-wide retrieve, or the main working tree for this capture.

For `IsNameObsolete = true`, do not attempt a retrieve. The component no longer exists in the org,
so there is nothing retrievable.

1. Confirm with the user that the deletion was intentional.
2. Find the corresponding tracked file or bundle under `force-app/` in the ticket worktree.
3. Check that a newer trunk commit has not already removed it.
4. Delete the exact source file, companion metadata, or bundle deliberately.
5. Review the deletion in `git diff` before staging it.

If the source is already absent, record that finding and make no duplicate deletion. If the
SourceMember row says obsolete but the user did not report a deletion, stop and resolve the
conflict rather than assigning it to them.

### 5. Copy, review, and deliver through the local loop

Copy only the confirmed files from `tmp-retrieve` into their matching `force-app/` paths in the
ticket worktree. Review the full diff. Remove unrelated generated content instead of expanding the
ticket to fit it.

Then follow the ordinary local loop:

1. Commit on the ticket branch.
2. Validate with a dry run from that commit.
3. Merge through the configured review gate.
4. In direct delivery, deploy the same files and tests from trunk to the development sandbox.
   In DevOps Center delivery, push the validated WI branch and create its review to the configured
   first landing stage; do not merge or deploy a stage branch locally.
5. Record the development evidence on the ticket. DevOps Center promotion evidence remains in
   DevOps Center.

Git and the ticket worktree are the handoff into delivery. The configured delivery system begins
after the change is in source, reviewed, and ready for pipeline promotion. It does not poll this
development org or write Setup changes back to source.

## Fallback when the user cannot name the change

Use broad SourceMember discovery only for a report such as, "I changed something in Setup, but I
do not remember exactly what."

```bash
sf data query --use-tooling-api \
  --query "SELECT MemberType, MemberName, RevisionCounter, IsNameObsolete FROM SourceMember ORDER BY RevisionCounter DESC"
```

The agent reads the Salesforce CLI's local source-tracking state under `.sf/orgs/` to establish a
reasonable lower revision bound, then performs the same git/deploy subtraction. Present the small
remainder to the user for confirmation. Do not expose revision bookkeeping as a user-operated
cursor, save a separate cursor store, or keep a standing inbox.

Once the user confirms the components, return to the added, modified, and deleted handling above.
The broad query changes discovery only; it does not relax retrieval scope.

## Why broad retrieval is never the shortcut

A retrieve into the main tree overwrites `force-app/` with org state and can silently revert
deployed work that the local checkout has not pulled. A full retrieve preview is also noisy and
slow for this purpose. It reports org differences outside the user's ticket and metadata the repo
may not track.

The allowed shape is always a named component into `tmp-retrieve`, followed by a reviewed copy in
the ticket worktree.

## Escape hatch

`ALEY_ALLOW_RETRIEVE=1` lets one otherwise blocked retrieve run and records it in the hatch log.
It exists for cases the scratch-directory path cannot express. It is not the normal Setup-change
workflow.
